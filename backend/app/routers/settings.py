# routers/settings.py -- App Settings API
# ==========================================
# Exposes endpoints to read and write global app settings
# (API key, default model, content mode, cost tier).
#
# Settings are stored in ~/.open-write/settings.json via settings_store.py.
#
# Routes:
#   GET  /api/settings        -- return current settings (API key is masked)
#   PUT  /api/settings        -- update one or more settings fields
#   POST /api/settings/test-connection  -- verify the OpenRouter API key works

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.settings_store import (
    load_settings, save_settings, get_vault_root, get_providers, _normalize_providers,
)
from app.ai.openrouter import test_connection
from app.ai.model_catalog import get_catalog, get_catalog_by_provider

router = APIRouter(prefix="/api/settings", tags=["settings"])


# ── Pydantic Models ───────────────────────────────────────────────────────────

class SettingsResponse(BaseModel):
    """What we return to the frontend. API key is partially masked for display."""
    openrouter_api_key:     str        # Masked: "sk-or-...abc" or "" if not set
    openrouter_api_key_set: bool       # True if a key has been saved
    default_model:          str
    content_mode:           str
    cost_tier:              str
    text_only_filter:       bool
    starred_models:         list[str]
    model_allowlist:        list[str]
    model_blocklist:        list[str]
    model_content_modes:    dict[str, list[str]]
    # Multi-provider config. Each provider's api_key is masked for display.
    providers:              list[dict]
    # Per-role pipeline models (qualified "<provider>/<model>"). Empty = default.
    writer_model:           str
    critic_model:           str
    # Orchestration-layer Planner model (The Architect harness). Empty = default.
    planner_model:          str
    # Parent folder where new projects and series are placed. Defaults to
    # ~/Documents/Open-Write. Returned to the frontend so the Settings screen
    # can show the current path (and change it).
    vault_root:             str
    # UI theme: "dark" or "light". Drives the runtime color palette.
    theme:                  str
    # UI font scale for chrome (menus, chat, settings, About, profile labels).
    # One of "default" | "larger" | "larger_plus" | "largest". Drives the
    # root <html> font-size at runtime so every Tailwind text-* rem-based
    # utility scales proportionally. The editor uses its own pixel-sized
    # font so it is unaffected by this setting (writers control editor
    # font via the existing font picker in the editor toolbar).
    ui_scale:               str
    # Writing Progress: writer's chosen skill level. Drives the daily
    # word + task targets in the Writing Progress tracker.
    writing_skill_level:    str
    # Writing Progress: hour at which "today" rolls over. 0 = midnight
    # (default), 4 = Night Owl. See progress_store.local_date_for().
    day_rollover_hour:      int


class UpdateSettingsRequest(BaseModel):
    """Fields the frontend can update. All optional -- only provided fields are changed."""
    openrouter_api_key:  str | None                   = None
    default_model:       str | None                   = None
    content_mode:        str | None                   = None
    cost_tier:           str | None                   = None
    text_only_filter:    bool | None                  = None
    starred_models:      list[str] | None             = None
    model_allowlist:     list[str] | None             = None
    model_blocklist:     list[str] | None             = None
    model_content_modes: dict[str, list[str]] | None  = None
    # Multi-provider list. Each entry: {id, label, base_url, api_key, models}.
    # An api_key of "" or a masked value ("...") preserves the stored key.
    providers:          list[dict] | None             = None
    writer_model:       str | None                    = None
    critic_model:       str | None                    = None
    planner_model:      str | None                    = None
    # Empty string resets to the default location (~/Documents/Open-Write).
    # Any non-empty value is taken as-is. The directory is created on next
    # use; we don't validate it exists at save time so writers can set a
    # not-yet-created folder if they want.
    vault_root:          str | None                   = None
    # "dark" or "light". Anything else is ignored.
    theme:               str | None                   = None
    # One of "default" | "larger" | "larger_plus" | "largest". Anything else
    # is ignored. Forward-compatible if more steps are added later.
    ui_scale:            str | None                   = None
    # One of the seven skill levels. Anything else is silently coerced to
    # "novice" (the default) when written.
    writing_skill_level: str | None                   = None
    # Only 0 or 4 are accepted. Anything else is clamped to 0 at write time.
    day_rollover_hour:   int | None                   = None


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("", response_model=SettingsResponse)
async def get_settings():
    """
    Return the current settings. The full API key is never sent to the frontend --
    only a masked preview ("sk-or-...xyz") is shown in the UI. This prevents the
    key from appearing in browser dev tools or network logs.
    """
    settings = load_settings()
    key = settings.get("openrouter_api_key", "")

    return SettingsResponse(
        openrouter_api_key     = _mask_key(key),
        openrouter_api_key_set = bool(key),
        default_model          = settings.get("default_model", ""),
        content_mode           = settings.get("content_mode", "general"),
        cost_tier              = settings.get("cost_tier", "standard"),
        text_only_filter       = settings.get("text_only_filter", True),
        starred_models         = settings.get("starred_models", []),
        model_allowlist        = settings.get("model_allowlist", []),
        model_blocklist        = settings.get("model_blocklist", []),
        model_content_modes    = settings.get("model_content_modes", {}),
        providers              = _masked_providers(get_providers()),
        writer_model           = settings.get("writer_model", ""),
        critic_model           = settings.get("critic_model", ""),
        planner_model          = settings.get("planner_model", ""),
        # get_vault_root() resolves blanks to the default and ensures the
        # directory exists -- frontend always sees a real path.
        vault_root             = get_vault_root(),
        theme                  = settings.get("theme", "dark"),
        ui_scale               = settings.get("ui_scale", "default"),
        writing_skill_level    = settings.get("writing_skill_level", "novice"),
        day_rollover_hour      = int(settings.get("day_rollover_hour", 0) or 0),
    )


@router.put("", response_model=SettingsResponse)
async def update_settings(request: UpdateSettingsRequest):
    """
    Update one or more settings fields. Only provided fields are changed.
    If openrouter_api_key is provided and non-empty, it replaces the stored key.
    If it's an empty string, it clears the stored key.
    """
    settings = load_settings()

    if request.openrouter_api_key is not None:
        settings["openrouter_api_key"] = request.openrouter_api_key.strip()
    if request.default_model is not None:
        settings["default_model"] = request.default_model
    if request.content_mode is not None:
        settings["content_mode"] = request.content_mode
    if request.cost_tier is not None:
        settings["cost_tier"] = request.cost_tier
    if request.text_only_filter is not None:
        settings["text_only_filter"] = request.text_only_filter
    if request.starred_models is not None:
        settings["starred_models"] = request.starred_models
    if request.model_allowlist is not None:
        settings["model_allowlist"] = request.model_allowlist
    if request.model_blocklist is not None:
        settings["model_blocklist"] = request.model_blocklist
    if request.model_content_modes is not None:
        settings["model_content_modes"] = request.model_content_modes
    if request.providers is not None:
        merged = _merge_providers(settings.get("providers", []), request.providers)
        settings["providers"] = merged
        # Keep the legacy openrouter_api_key mirror in sync for backward compat.
        for p in merged:
            if p.get("id") == "openrouter":
                settings["openrouter_api_key"] = p.get("api_key", "")
    if request.writer_model is not None:
        settings["writer_model"] = request.writer_model
    if request.critic_model is not None:
        settings["critic_model"] = request.critic_model
    if request.planner_model is not None:
        settings["planner_model"] = request.planner_model
    if request.vault_root is not None:
        # Empty string is a sentinel for "reset to default" -- store as ""
        # and let get_vault_root() substitute the default at read time.
        settings["vault_root"] = request.vault_root.strip()
    if request.theme is not None and request.theme in ("dark", "light"):
        # Silently ignore unknown values rather than 400 -- forward-compatible
        # in case future themes are added in newer clients.
        settings["theme"] = request.theme
    if request.ui_scale is not None and request.ui_scale in ("default", "larger", "larger_plus", "largest"):
        # Same silent-ignore pattern as theme. Lets us add more steps later
        # without older clients breaking on the new values.
        settings["ui_scale"] = request.ui_scale
    if request.writing_skill_level is not None:
        # Coerce unknown levels to "novice" (the documented default) rather
        # than 400'ing -- forward-compatible if more steps are added later.
        valid_levels = ("newbie", "beginner", "novice", "amateur",
                        "experienced", "fulltime", "professional")
        settings["writing_skill_level"] = (
            request.writing_skill_level
            if request.writing_skill_level in valid_levels
            else "novice"
        )
    if request.day_rollover_hour is not None:
        # Only midnight (0) and Night Owl (4) are valid. Anything else clamps
        # to 0 so a stray value doesn't shift the gauge unexpectedly.
        settings["day_rollover_hour"] = (
            request.day_rollover_hour
            if request.day_rollover_hour in (0, 4)
            else 0
        )

    save_settings(settings)

    key = settings.get("openrouter_api_key", "")
    return SettingsResponse(
        openrouter_api_key     = _mask_key(key),
        openrouter_api_key_set = bool(key),
        default_model          = settings.get("default_model", ""),
        content_mode           = settings.get("content_mode", "general"),
        cost_tier              = settings.get("cost_tier", "standard"),
        text_only_filter       = settings.get("text_only_filter", True),
        starred_models         = settings.get("starred_models", []),
        model_allowlist        = settings.get("model_allowlist", []),
        model_blocklist        = settings.get("model_blocklist", []),
        model_content_modes    = settings.get("model_content_modes", {}),
        providers              = _masked_providers(get_providers()),
        writer_model           = settings.get("writer_model", ""),
        critic_model           = settings.get("critic_model", ""),
        planner_model          = settings.get("planner_model", ""),
        vault_root             = get_vault_root(),
        theme                  = settings.get("theme", "dark"),
        ui_scale               = settings.get("ui_scale", "default"),
        writing_skill_level    = settings.get("writing_skill_level", "novice"),
        day_rollover_hour      = int(settings.get("day_rollover_hour", 0) or 0),
    )


@router.post("/test-connection")
async def test_openrouter_connection():
    """
    Test whether the stored OpenRouter API key is valid.
    Calls the OpenRouter models endpoint and reports success or failure.
    The frontend calls this when the user clicks 'Test Connection' in Settings.
    """
    api_key = load_settings().get("openrouter_api_key", "")

    if not api_key:
        return {"ok": False, "error": "No API key saved. Enter your OpenRouter key in Settings first."}

    result = await test_connection(api_key)
    return result


class TestProviderRequest(BaseModel):
    """Test a specific provider's key against its base_url."""
    provider_id: str


@router.post("/test-provider")
async def test_provider_connection(req: TestProviderRequest):
    """Test a configured provider by fetching its /models endpoint."""
    provider = None
    for p in get_providers():
        if p.get("id") == req.provider_id:
            provider = p
            break
    if provider is None:
        raise HTTPException(status_code=404, detail=f"Unknown provider: {req.provider_id}")
    if not provider.get("api_key"):
        return {"ok": False, "error": "No API key set for this provider."}
    if not provider.get("base_url"):
        return {"ok": False, "error": "No base URL set for this provider."}
    return await test_connection(provider["api_key"], base_url=provider["base_url"])


@router.get("/providers/catalog")
async def model_catalog():
    """Return the curated model catalog for the quick-pick UI.

    Each entry includes the qualified model id, display name, provider id,
    a short note, cost tier, and strength tags. The frontend uses this to
    populate the "Recommended Models" section that works even before the
    writer has configured any provider keys.
    """
    return get_catalog()


@router.get("/providers/catalog/{provider_id}")
async def provider_catalog(provider_id: str):
    """Return catalog entries for a specific provider."""
    entries = get_catalog_by_provider(provider_id)
    if not entries:
        raise HTTPException(status_code=404, detail=f"No catalog entries for provider: {provider_id}")
    return entries


# ── Helpers ───────────────────────────────────────────────────────────────────

def _mask_key(key: str) -> str:
    """
    Partially mask an API key for safe display in the UI.
    "sk-or-v1-abcdefghijklmnop" -> "sk-or-...mnop"
    Returns "" if the key is empty.
    """
    if not key:
        return ""
    if len(key) <= 8:
        return "***"
    return key[:6] + "..." + key[-4:]


def _masked_providers(providers: list[dict]) -> list[dict]:
    """Return a copy of the providers list with each api_key masked for display."""
    out = []
    for p in providers:
        q = dict(p)
        q["api_key"] = _mask_key(q.get("api_key", ""))
        q["api_key_set"] = bool(p.get("api_key"))
        out.append(q)
    return out


def _merge_providers(stored: list[dict], incoming: list[dict]) -> list[dict]:
    """Merge an incoming provider list onto the stored one.

    Keys are preserved when the incoming value is blank or looks masked, so a
    round-trip through the masked GET response never wipes a saved key. New or
    edited base_urls/models/labels take effect.
    """
    stored_by_id = {p["id"]: dict(p) for p in _normalize_providers(stored)}
    result_order: list[str] = []
    for inc in incoming or []:
        pid = inc.get("id")
        if not pid:
            continue
        base = stored_by_id.get(pid, {"id": pid})
        merged = {
            "id": pid,
            "label": inc.get("label") or base.get("label", pid),
            "base_url": inc.get("base_url", base.get("base_url", "")),
            "models": inc.get("models", base.get("models", [])),
        }
        inc_key = (inc.get("api_key") or "").strip()
        if inc_key and "..." not in inc_key:
            merged["api_key"] = inc_key
        else:
            merged["api_key"] = base.get("api_key", "")
        stored_by_id[pid] = merged
        if pid not in result_order:
            result_order.append(pid)
    # Keep any stored providers not present in the incoming list.
    for pid, p in stored_by_id.items():
        if pid not in result_order:
            result_order.append(pid)
    return [stored_by_id[pid] for pid in result_order]
