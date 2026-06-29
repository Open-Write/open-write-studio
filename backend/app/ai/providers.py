"""
providers.py — multi-provider model resolution.

Open-Write supports several OpenAI-compatible chat-completions providers
side by side: OpenRouter (the default), GLM (Zhipu), and MiMo, plus any custom
provider the writer adds in Settings. Each provider carries its own base_url,
API key, and model list.

Model identity
--------------
A model is referenced by a *qualified* id of the form ``"<provider>/<model>"``:

  - ``"glm/glm-4.6"``                -> GLM provider, model "glm-4.6"
  - ``"mimo/mimo-7b-instruct"``      -> MiMo provider
  - ``"openrouter/openai/gpt-4o-mini"`` -> OpenRouter (explicit)

Backward compatibility
----------------------
Unqualified ids that predate multi-provider support (e.g. ``"openai/gpt-4o-mini"``,
``"anthropic/claude-3.5-sonnet"``) are treated as OpenRouter models, since their
first segment is not a known provider id. This keeps existing settings working
without migration.

The resolved object exposes the three things an OpenAI-compatible client needs:
``base_url``, ``api_key``, and ``model_name`` (the bare model id to send to the
provider).
"""

from __future__ import annotations

from dataclasses import dataclass

from app.settings_store import get_providers


@dataclass(frozen=True)
class ResolvedProvider:
    provider_id: str
    label: str
    base_url: str
    api_key: str
    model_name: str        # bare model id (no provider prefix)

    @property
    def is_configured(self) -> bool:
        """True if this provider has both a base_url and an api_key."""
        return bool(self.base_url) and bool(self.api_key)


def _provider_index(providers: list[dict] | None = None) -> dict[str, dict]:
    src = providers if providers is not None else get_providers()
    return {p["id"]: p for p in src}


def resolve(model_id: str, providers: list[dict] | None = None) -> ResolvedProvider:
    """
    Resolve a (possibly qualified) model id to a provider + bare model name.

    Resolution order:
      1. If the id starts with a known provider id followed by '/', that
         provider is used and the remainder is the model name.
      2. Otherwise the whole id is treated as an OpenRouter model name
         (backward compatibility for legacy unqualified ids).

    ``providers`` is normally loaded from settings; tests may pass an explicit
    list. Raises ValueError if no provider can be chosen.
    """
    index = _provider_index(providers)
    model_id = (model_id or "").strip()

    provider = None
    model_name = model_id
    if "/" in model_id:
        head, rest = model_id.split("/", 1)
        if head in index:
            provider = index[head]
            model_name = rest

    if provider is None:
        provider = index.get("openrouter")
        if provider is None:
            raise ValueError(
                "No providers configured. Add a provider in Settings."
            )
        # Legacy unqualified id -> OpenRouter model.
        model_name = model_id

    return ResolvedProvider(
        provider_id=provider["id"],
        label=provider.get("label", provider["id"]),
        base_url=provider.get("base_url", ""),
        api_key=provider.get("api_key", ""),
        model_name=model_name,
    )


def all_models() -> list[dict]:
    """
    Return every selectable model across all providers, for the model picker.

    Each entry: ``{"id": "<provider>/<model>", "label": "...", "provider": ...}``.
    OpenRouter contributes its (possibly scraped) model list; the other
    providers contribute their curated lists. OpenRouter's scraped models are
    loaded lazily by the settings/routes layer, so here we emit only the
    curated (non-OpenRouter) provider models plus an explicit entry per
    OpenRouter model already known to settings.
    """
    out: list[dict] = []
    for p in get_providers():
        for m in p.get("models", []):
            out.append({
                "id": f"{p['id']}/{m}",
                "label": f"{p.get('label', p['id'])} — {m}",
                "provider": p["id"],
                "model": m,
            })
    return out
