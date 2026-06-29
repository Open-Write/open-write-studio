#!/usr/bin/env python3
"""
Multi-Model Critic Runner
Runs critic passes across multiple OpenAI-compatible API models and takes the union of findings.

Models are configured via a models.env file or environment variables.
Each model needs: base_url, api_key, and model_id.

Usage:
    python tools/critic_runner.py --scene 1 --critic show --models model1,model2
    python tools/critic_runner.py --scene 1 --critic voice --character character_name --models model1
    python tools/critic_runner.py --list-models
    python tools/critic_runner.py --check-models
"""

import json
import sys
import os
import argparse
import re
from pathlib import Path


def load_models_config():
    """Load model configuration from models.env or environment variables.
    
    models.env format (KEY=VALUE per line):
        MODEL_KEY_NAME=My Model Name
        MODEL_KEY_BASE_URL=https://api.example.com/v1
        MODEL_KEY_API_KEY=sk-...
        MODEL_KEY_MODEL_ID=model-name
        
    Multiple models use different KEY prefixes:
        OPENAI_NAME=OpenAI GPT-4
        OPENAI_BASE_URL=https://api.openai.com/v1
        OPENAI_API_KEY=sk-...
        OPENAI_MODEL_ID=gpt-4
        
        LOCAL_NAME=Local Llama
        LOCAL_BASE_URL=http://localhost:1234/v1
        LOCAL_API_KEY=not-needed
        LOCAL_MODEL_ID=llama-3.3-70b
    """
    models = {}
    
    env_path = Path(__file__).parent.parent / "models.env"
    env = {}
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").strip().split("\n"):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, value = line.partition('=')
                env[key.strip()] = value.strip().strip('"').strip("'")
    
    all_env = {**os.environ, **env}
    
    prefixes = set()
    for key in all_env:
        if key.endswith('_NAME'):
            prefix = key[:-5]
            prefixes.add(prefix)
    
    for prefix in prefixes:
        model_key = prefix.lower()
        models[model_key] = {
            "name": all_env.get(f"{prefix}_NAME", model_key),
            "base_url": all_env.get(f"{prefix}_BASE_URL", ""),
            "api_key": all_env.get(f"{prefix}_API_KEY", ""),
            "model_id": all_env.get(f"{prefix}_MODEL_ID", model_key),
        }
    
    return models


MODELS = load_models_config()

CRITICS = {
    "show": {
        "name": "Show-Don't-Tell Critic",
        "rules_file": ".kilo/rules-critic-show.md",
        "output_pattern": "critic_outputs/scene_{scene:02d}_show_dont_tell_{model}.md"
    },
    "palette": {
        "name": "Palette Critic",
        "rules_file": ".kilo/rules-critic-palette.md",
        "output_pattern": "critic_outputs/scene_{scene:02d}_palette_{model}.md"
    },
    "continuity": {
        "name": "Continuity Critic",
        "rules_file": ".kilo/rules-critic-continuity.md",
        "output_pattern": "critic_outputs/scene_{scene:02d}_continuity_{model}.md"
    },
    "voice": {
        "name": "Voice Critic",
        "rules_file": ".kilo/rules-critic-voice.md",
        "output_pattern": "critic_outputs/scene_{scene:02d}_voice_{character}_{model}.md"
    },
    "naturalism": {
        "name": "Naturalism Critic",
        "rules_file": ".kilo/rules-critic-naturalism.md",
        "output_pattern": "critic_outputs/scene_{scene:02d}_naturalism_{model}.md"
    }
}


def get_model_config(model_key):
    """Get model configuration."""
    if model_key not in MODELS:
        print(f"Error: Unknown model '{model_key}'. Available: {', '.join(MODELS.keys())}")
        return None
    return MODELS[model_key]


def build_critic_prompt(critic_type, scene_num, character=None):
    """Build the full prompt for a critic pass."""
    base_dir = Path(__file__).parent.parent
    
    critic_config = CRITICS[critic_type]
    rules_path = base_dir / critic_config["rules_file"]
    rules = rules_path.read_text(encoding="utf-8") if rules_path.exists() else ""
    
    scene_files = sorted((base_dir / "script" / "scenes").glob(f"{scene_num:02d}_*.fountain"))
    if not scene_files:
        print(f"Error: No scene file found for scene {scene_num}")
        return None
    scene_content = scene_files[0].read_text(encoding="utf-8")
    scene_name = scene_files[0].stem
    
    format_rules_path = base_dir / "bible" / "07_format_rules.md"
    format_rules = format_rules_path.read_text(encoding="utf-8") if format_rules_path.exists() else ""
    
    prompt_parts = [
        f"# Critic Task: {critic_config['name']} for Scene {scene_num}",
        "",
        "## Your Rules",
        rules,
        "",
        "## Format Rules Reference",
        format_rules,
        "",
        "## Scene to Review",
        f"File: {scene_name}.fountain",
        "",
        scene_content,
        ""
    ]
    
    if critic_type == "voice" and character:
        char_path = base_dir / "bible" / "03_characters" / f"{character}.md"
        if char_path.exists():
            char_profile = char_path.read_text(encoding="utf-8")
            prompt_parts.extend([
                f"## Character Profile: {character}",
                char_profile,
                ""
            ])
    
    if critic_type == "palette":
        outline_path = base_dir / "bible" / "04_outline.md"
        if outline_path.exists():
            outline = outline_path.read_text(encoding="utf-8")
            scene_pattern = rf'\*\*{scene_num}\..*?(?=\*\*{scene_num+1}\.|$)'
            match = re.search(scene_pattern, outline, re.DOTALL)
            if match:
                prompt_parts.extend([
                    "## Scene Outline Entry (for palette reference)",
                    match.group(0),
                    ""
                ])
    
    if critic_type == "continuity":
        for state_file in ["project_state.json", "callback_ledger.json", "timeline.json", "audience_state.json"]:
            state_path = base_dir / "state" / state_file
            if state_path.exists():
                state_data = state_path.read_text(encoding="utf-8")
                prompt_parts.extend([
                    f"## State File: {state_file}",
                    f"```json\n{state_data}\n```",
                    ""
                ])
    
    prompt_parts.extend([
        "---",
        "",
        f"Write your review as a {critic_config['name']} report. Be specific, quote line numbers, and provide actionable fixes."
    ])
    
    return "\n".join(prompt_parts)


def call_openai_compatible(base_url, api_key, model_id, prompt, temperature=0.7):
    """Call an OpenAI-compatible API endpoint."""
    import urllib.request
    import urllib.error
    
    url = f"{base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json"
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    data = json.dumps({
        "model": model_id,
        "messages": [
            {"role": "system", "content": "You are a professional screenplay critic. Be specific, mechanical, and unflinching. Quote line numbers. Provide actionable fixes."},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": 4096
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return f"Error: HTTP {e.code} — {body}"
    except Exception as e:
        return f"Error: {e}"


def run_critic(critic_type, scene_num, model_key, character=None):
    """Run a single critic pass."""
    config = get_model_config(model_key)
    if not config:
        return None
    
    prompt = build_critic_prompt(critic_type, scene_num, character)
    if not prompt:
        return None
    
    print(f"  Running {CRITICS[critic_type]['name']} on {config['name']}...")
    
    result = call_openai_compatible(
        config["base_url"],
        config["api_key"],
        config["model_id"],
        prompt
    )
    
    base_dir = Path(__file__).parent.parent
    output_name = CRITICS[critic_type]["output_pattern"].format(
        scene=scene_num,
        model=model_key,
        character=character or "unknown"
    )
    output_path = base_dir / output_name
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result, encoding="utf-8")
    
    print(f"  Saved to {output_name}")
    return result


def run_multi_model(critic_type, scene_num, models, character=None):
    """Run a critic across multiple models and report."""
    results = {}
    
    for model_key in models:
        result = run_critic(critic_type, scene_num, model_key, character)
        if result and not result.startswith("Error:"):
            results[model_key] = result
    
    if len(results) > 1:
        print(f"\n  Ran {CRITICS[critic_type]['name']} on {len(results)} models.")
        print(f"  Individual reports saved with model suffix.")
        print(f"  Take the UNION of flagged issues across all models for maximum coverage.")
    
    return results


def main():
    MODELS = load_models_config()
    
    parser = argparse.ArgumentParser(description="Multi-Model Critic Runner")
    parser.add_argument("--scene", type=int, help="Scene number to review")
    parser.add_argument("--critic", choices=list(CRITICS.keys()), help="Critic type to run")
    parser.add_argument("--character", type=str, help="Character name (for voice critic)")
    parser.add_argument("--models", type=str, default=",".join(MODELS.keys()) if MODELS else "default", help="Comma-separated model keys")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    parser.add_argument("--list-critics", action="store_true", help="List available critics")
    parser.add_argument("--check-models", action="store_true", help="Check which models are configured")
    
    args = parser.parse_args()
    
    if args.list_models:
        if not MODELS:
            print("No models configured. Create a models.env file with your model configurations.")
            print("Format: PREFIX_NAME=Name, PREFIX_BASE_URL=url, PREFIX_API_KEY=key, PREFIX_MODEL_ID=id")
        else:
            print("Available models:")
            for key, config in MODELS.items():
                print(f"  {key:15} — {config['name']}")
        return
    
    if args.list_critics:
        print("Available critics:")
        for key, config in CRITICS.items():
            print(f"  {key:15} — {config['name']}")
        return
    
    if args.check_models:
        if not MODELS:
            print("No models configured. Create a models.env file.")
        else:
            print("Model configuration status:")
            for key, config in MODELS.items():
                has_key = bool(config.get("api_key"))
                print(f"  {key:15} — {config['name']:25} — API key: {'configured' if has_key else 'MISSING'} — URL: {config.get('base_url', 'N/A')}")
        return
    
    if not args.scene or not args.critic:
        parser.print_help()
        return
    
    models = [m.strip() for m in args.models.split(",")]
    
    print(f"Running {CRITICS[args.critic]['name']} on scene {args.scene}")
    print(f"Models: {', '.join(models)}")
    if args.character:
        print(f"Character: {args.character}")
    print()
    
    run_multi_model(args.critic, args.scene, models, args.character)


if __name__ == "__main__":
    main()
