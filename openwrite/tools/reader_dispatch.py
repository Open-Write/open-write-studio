#!/usr/bin/env python3
"""
reader_dispatch.py — Direct-call adversarial reader dispatch.

Owns the API call to the provider, bypassing any intermediate routing layer.
Returns provider-supplied provenance (model, request ID, token usage) in the
output header — ground truth from the API response, not a self-report.

Usage:
    python tools/reader_dispatch.py \
        --manuscript manuscript/novel.md \
        --rules-file .kilo/rules-adversarial-reader.md \
        --model zai-coding-plan/glm-4.7 \
        --output coverage_reports/adversarial_reader_B.md

    python tools/reader_dispatch.py \
        --manuscript manuscript/novel.md \
        --rules-file .kilo/rules-adversarial-reader-quantitative.md \
        --model xiaomi-token-plan-sgp/mimo-v2.5-pro \
        --output coverage_reports/quantitative_coverage.md \
        --temperature 0.3

Provider resolution order:
    1. --api-key / --base-url CLI args
    2. Provider auth from Kilo auth.json
    3. Provider endpoint from Kilo models-snapshot.json or kilo.jsonc

No external dependencies — stdlib only.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path


# ── Config resolution ──────────────────────────────────────────────────────

KILO_CONFIG_DIRS = [
    Path.home() / ".config" / "kilo",
    Path.home() / ".kilo",
    Path.home() / ".kilocode",
]

AUTH_FILE_LOCATIONS = [
    Path.home() / ".local" / "share" / "kilo" / "auth.json",
    Path.home() / ".config" / "kilo" / "auth.json",
]

MODELS_SNAPSHOT_LOCATIONS = [
    # VS Code extension bundled snapshot (version-pinned)
    *sorted(
        (Path.home() / ".vscode" / "extensions").glob("kilocode.kilo-code-*/bin/models-snapshot.json"),
        reverse=True,
    ),
    Path.home() / ".cache" / "kilo" / "models.json",
]


def load_auth(provider_name: str) -> str | None:
    """Load API key for a provider from Kilo auth.json."""
    for auth_path in AUTH_FILE_LOCATIONS:
        if auth_path.exists():
            try:
                auth = json.loads(auth_path.read_text(encoding="utf-8"))
                entry = auth.get(provider_name, {})
                if entry.get("key"):
                    return entry["key"]
            except (json.JSONDecodeError, KeyError):
                continue
    return None


def load_provider_endpoint(provider_name: str) -> str | None:
    """Load base URL for a provider from models-snapshot.json or kilo.jsonc."""
    # Try models-snapshot first (has built-in provider definitions)
    for snap_path in MODELS_SNAPSHOT_LOCATIONS:
        if snap_path.exists():
            try:
                snapshot = json.loads(snap_path.read_text(encoding="utf-8"))
                provider = snapshot.get(provider_name, {})
                if provider.get("api"):
                    return provider["api"]
            except (json.JSONDecodeError, KeyError):
                continue

    # Try kilo.jsonc provider config
    for config_dir in KILO_CONFIG_DIRS:
        for name in ["kilo.jsonc", "kilo.json"]:
            config_path = config_dir / name
            if config_path.exists():
                try:
                    cfg = json.loads(config_path.read_text(encoding="utf-8"))
                    provider = cfg.get("provider", {}).get(provider_name, {})
                    options = provider.get("options", {})
                    if options.get("baseURL"):
                        return options["baseURL"]
                except (json.JSONDecodeError, KeyError):
                    continue

    return None


def resolve_model(model_string: str) -> tuple[str, str]:
    """Split 'provider/model' into (provider_name, model_id)."""
    if "/" not in model_string:
        print(f"Error: model must be in 'provider/model' format, got: {model_string}", file=sys.stderr)
        sys.exit(1)
    provider_name, model_id = model_string.split("/", 1)
    return provider_name, model_id


# ── API call ───────────────────────────────────────────────────────────────

def call_provider(base_url: str, api_key: str, model_id: str,
                  system_prompt: str, user_content: str,
                  temperature: float, max_tokens: int) -> dict:
    """Make a direct OpenAI-compatible API call. Returns the full response dict."""
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = json.dumps({
        "model": model_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

    dispatch_utc = datetime.now(timezone.utc).isoformat()

    try:
        with urllib.request.urlopen(req, timeout=600) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {
            "error": f"HTTP {e.code}",
            "error_body": body,
            "dispatch_utc": dispatch_utc,
            "return_utc": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "error": str(e),
            "dispatch_utc": dispatch_utc,
            "return_utc": datetime.now(timezone.utc).isoformat(),
        }

    return_utc = datetime.now(timezone.utc).isoformat()

    # Extract provenance from provider response
    provenance = {
        "dispatch_utc": dispatch_utc,
        "return_utc": return_utc,
        "provider_response_id": raw.get("id", "N/A"),
        "provider_response_model": raw.get("model", "N/A"),
        "usage": raw.get("usage", {}),
    }

    # Extract content
    choices = raw.get("choices", [])
    content = choices[0]["message"]["content"] if choices else ""

    return {
        "provenance": provenance,
        "content": content,
    }


# ── Output assembly ────────────────────────────────────────────────────────

def compute_manuscript_hash(path: Path) -> str:
    """SHA-256 of the manuscript file."""
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def build_provenance_header(provenance: dict, manuscript_path: str,
                            manuscript_hash: str, reader_type: str,
                            provider_name: str) -> str:
    """Build the provenance header from provider-supplied data."""
    usage = provenance.get("usage", {})
    return f"""<!-- DISPATCH PROVENANCE
provider: {provider_name}
model: {provenance.get('provider_response_model', 'N/A')}
request_id: {provenance.get('provider_response_id', 'N/A')}
prompt_tokens: {usage.get('prompt_tokens', 'N/A')}
completion_tokens: {usage.get('completion_tokens', 'N/A')}
total_tokens: {usage.get('total_tokens', 'N/A')}
dispatch_utc: {provenance.get('dispatch_utc', 'N/A')}
return_utc: {provenance.get('return_utc', 'N/A')}
manuscript: {manuscript_path}
manuscript_hash: {manuscript_hash}
reader_type: {reader_type}
-->"""


def build_error_header(error_result: dict, manuscript_path: str,
                       manuscript_hash: str, reader_type: str) -> str:
    """Build a DEGRADED header when dispatch fails."""
    return f"""<!-- DISPATCH PROVENANCE
status: DEGRADED — dispatch failed
error: {error_result.get('error', 'unknown')}
error_body: {error_result.get('error_body', '')[:500]}
dispatch_utc: {error_result.get('dispatch_utc', 'N/A')}
return_utc: {error_result.get('return_utc', 'N/A')}
manuscript: {manuscript_path}
manuscript_hash: {manuscript_hash}
reader_type: {reader_type}
-->

**DEGRADED: Dispatch failed at the provider level.**
Error: {error_result.get('error', 'unknown')}
This is NOT a coverage report. The provider rejected or could not fulfill the request.
"""


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Direct-call adversarial reader dispatch with provider-supplied provenance."
    )
    parser.add_argument("--manuscript", required=True, help="Path to assembled manuscript")
    parser.add_argument("--rules-file", required=True, help="Path to rubric/rules file (system prompt)")
    parser.add_argument("--model", required=True, help="Provider/model string, e.g. zai-coding-plan/glm-4.7")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument("--reader-type", default="qualitative", choices=["qualitative", "quantitative"])
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-tokens", type=int, default=16384)
    parser.add_argument("--api-key", help="Override API key (bypasses auth.json)")
    parser.add_argument("--base-url", help="Override provider base URL (bypasses models-snapshot)")
    parser.add_argument("--dry-run", action="store_true", help="Print config and exit without calling")

    args = parser.parse_args()

    # Resolve model
    provider_name, model_id = resolve_model(args.model)

    # Resolve API key
    api_key = args.api_key or os.environ.get(f"{provider_name.upper().replace('-', '_')}_API_KEY") or load_auth(provider_name)
    if not api_key:
        print(f"Error: no API key found for provider '{provider_name}'. "
              f"Use --api-key, set {provider_name.upper().replace('-', '_')}_API_KEY, "
              f"or add to Kilo auth.json.", file=sys.stderr)
        sys.exit(1)

    # Resolve base URL
    base_url = args.base_url or load_provider_endpoint(provider_name)
    if not base_url:
        print(f"Error: no endpoint found for provider '{provider_name}'. "
              f"Use --base-url or check models-snapshot.json.", file=sys.stderr)
        sys.exit(1)

    # Load manuscript
    manuscript_path = Path(args.manuscript)
    if not manuscript_path.exists():
        print(f"Error: manuscript not found: {manuscript_path}", file=sys.stderr)
        sys.exit(1)
    manuscript_text = manuscript_path.read_text(encoding="utf-8")
    manuscript_hash = compute_manuscript_hash(manuscript_path)

    # Load rules/rubric
    rules_path = Path(args.rules_file)
    if not rules_path.exists():
        print(f"Error: rules file not found: {rules_path}", file=sys.stderr)
        sys.exit(1)
    system_prompt = rules_path.read_text(encoding="utf-8")

    # Dry run
    if args.dry_run:
        print(f"Provider:     {provider_name}")
        print(f"Model:        {model_id}")
        print(f"Base URL:     {base_url}")
        print(f"API key:      {api_key[:8]}...{api_key[-4:]}")
        print(f"Manuscript:   {manuscript_path} ({len(manuscript_text)} chars)")
        print(f"Rules:        {rules_path}")
        print(f"Temperature:  {args.temperature}")
        print(f"Max tokens:   {args.max_tokens}")
        print(f"Output:       {args.output}")
        print(f"Reader type:  {args.reader_type}")
        print(f"\nDRY RUN — no API call made.")
        return

    # Dispatch
    print(f"Dispatching {model_id} via {provider_name} ({base_url})...")
    print(f"  Manuscript: {manuscript_path} ({len(manuscript_text)} chars)")
    print(f"  Rules: {rules_path}")

    result = call_provider(
        base_url=base_url,
        api_key=api_key,
        model_id=model_id,
        system_prompt=system_prompt,
        user_content=manuscript_text,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    # Assemble output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if "error" in result:
        header = build_error_header(result, str(manuscript_path), manuscript_hash, args.reader_type)
        output_path.write_text(header, encoding="utf-8")
        print(f"FAILED: {result['error']}", file=sys.stderr)
        print(f"  Error details written to {output_path}", file=sys.stderr)
        sys.exit(1)

    provenance = result["provenance"]
    header = build_provenance_header(provenance, str(manuscript_path), manuscript_hash, args.reader_type, provider_name)

    # Print provenance to stdout for orchestrator capture
    print(f"\n  Provider response model: {provenance['provider_response_model']}")
    print(f"  Request ID:              {provenance['provider_response_id']}")
    usage = provenance.get("usage", {})
    print(f"  Tokens:                  {usage.get('prompt_tokens', '?')} prompt / {usage.get('completion_tokens', '?')} completion / {usage.get('total_tokens', '?')} total")
    print(f"  Dispatch:                {provenance['dispatch_utc']}")
    print(f"  Return:                  {provenance['return_utc']}")

    # Write output
    full_output = header + "\n\n" + result["content"]
    output_path.write_text(full_output, encoding="utf-8")
    print(f"\n  Output: {output_path} ({len(full_output)} chars)")


if __name__ == "__main__":
    main()
