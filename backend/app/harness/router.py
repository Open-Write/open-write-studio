"""
harness/router.py — resolve a (domain, role) to a dispatch target.

This is the Open-Write-Studio adaptation of The Architect's Router. Routing is
data-driven via domains.yaml. A ``ResolvedTarget`` carries the role's default
model (a qualified "<provider>/<model>" id resolved through the multi-provider
system), the skills the executor must read first, the proprietary guard, and the
domain's default verifier.

The workspace (the open-write project being worked on) is supplied by the run,
not the registry, so a single registry serves any project.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from app.settings_store import get_default_model, get_writer_model, get_critic_model, get_planner_model
from . import loader


class RoutingError(ValueError):
    """Raised when a (domain, role) cannot be routed."""


@dataclass(frozen=True)
class ResolvedTarget:
    domain: str
    role: str
    model: str                       # qualified provider/model id
    skills: tuple[str, ...]
    proprietary: bool
    proprietary_terms: tuple[str, ...]
    default_verifier: Optional[dict]
    role_job: str


# Role → settings resolver for the default model. Empty/blank in the registry or
# settings falls through to the global default model.
def _role_default_model(role: str, registry_model: Optional[str]) -> str:
    if registry_model and registry_model.strip():
        return registry_model.strip()
    # Domain-aware settings fallbacks so writing roles pick up the A/B config.
    if role in ("writer", "architect", "systems-architect"):
        return get_writer_model()
    if role in ("critic", "editorial", "adversarial-reader"):
        return get_critic_model()
    if role == "planner":
        return get_planner_model()
    return get_default_model()


def resolve(domain: str, role: str) -> ResolvedTarget:
    """Resolve a (domain, role) pair to a dispatch target."""
    domains = loader.domains()
    d = domains.get(domain)
    if d is None:
        raise RoutingError(f"Unknown domain '{domain}'. Known: {loader.known_domains()}")

    roles = loader.roles()
    r = roles.get(role)
    if r is None:
        raise RoutingError(f"Unknown role '{role}'. Known: {loader.known_roles()}")

    registry_model = r.get("model") if isinstance(r, dict) else None
    return ResolvedTarget(
        domain=domain,
        role=role,
        model=_role_default_model(role, registry_model),
        skills=tuple(d.get("skills", []) or []),
        proprietary=bool(d.get("proprietary", False)),
        proprietary_terms=tuple(d.get("proprietary_terms", []) or []),
        default_verifier=d.get("verifier"),
        role_job=(r.get("job", "") if isinstance(r, dict) else ""),
    )


def resolve_task(task) -> ResolvedTarget:
    """Convenience: resolve from a Task-like object."""
    model = getattr(task, "model", None)
    target = resolve(task.domain, task.role)
    if model and model.strip():
        return ResolvedTarget(
            domain=target.domain, role=target.role, model=model.strip(),
            skills=target.skills, proprietary=target.proprietary,
            proprietary_terms=target.proprietary_terms,
            default_verifier=target.default_verifier, role_job=target.role_job,
        )
    return target


def registry_summary() -> dict[str, Any]:
    """Compact view for the planner's system-prompt injection."""
    return {
        "domains": {
            name: {
                "description": d.get("description", ""),
                "default_role": d.get("default_role", ""),
                "proprietary": bool(d.get("proprietary", False)),
            }
            for name, d in loader.domains().items()
        },
        "roles": {
            name: r.get("job", "")
            for name, r in loader.roles().items()
        },
    }
