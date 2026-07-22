# ai/model_catalog.py -- Curated Model Catalog for Quick-Pick UI
# ===============================================================
# A static catalog of recommended models for creative writing, grouped
# by provider. The frontend uses this to show a "Recommended Models"
# section that works even before the writer has configured any provider
# keys. Models here are a subset of what each provider offers, chosen
# for prose quality, cost-effectiveness, and reliability.
#
# The catalog is provider-agnostic: each entry carries its provider id
# so the frontend can show which provider the model comes from and
# whether that provider is configured yet.

from __future__ import annotations

# ── Curated model entries ─────────────────────────────────────────────────────
# Each entry:
#   id:          qualified "<provider>/<model>" id
#   name:        human-readable display name
#   provider:    provider id (matches PROVIDER_SEEDS)
#   note:        short description for the picker UI
#   tier:        "free" | "budget" | "standard" | "premium"
#   strengths:   list of tags (e.g. ["prose", "reasoning", "fast"])

CATALOG: list[dict] = [
    # ── OpenRouter (aggregator — many providers behind one key) ───────────
    {
        "id": "openrouter/anthropic/claude-sonnet-4",
        "name": "Claude Sonnet 4 (via OpenRouter)",
        "provider": "openrouter",
        "note": "Excellent prose quality, strong at fiction",
        "tier": "standard",
        "strengths": ["prose", "reasoning", "instruction-following"],
    },
    {
        "id": "openrouter/anthropic/claude-3.5-haiku",
        "name": "Claude 3.5 Haiku (via OpenRouter)",
        "provider": "openrouter",
        "note": "Fast, affordable, surprisingly good prose",
        "tier": "budget",
        "strengths": ["fast", "prose", "affordable"],
    },
    {
        "id": "openrouter/openai/gpt-4o",
        "name": "GPT-4o (via OpenRouter)",
        "provider": "openrouter",
        "note": "Strong all-around model",
        "tier": "standard",
        "strengths": ["prose", "reasoning", "versatile"],
    },
    {
        "id": "openrouter/openai/gpt-4o-mini",
        "name": "GPT-4o Mini (via OpenRouter)",
        "provider": "openrouter",
        "note": "Fast, capable, low cost",
        "tier": "budget",
        "strengths": ["fast", "affordable", "versatile"],
    },
    {
        "id": "openrouter/deepseek/deepseek-chat",
        "name": "DeepSeek Chat (via OpenRouter)",
        "provider": "openrouter",
        "note": "Best budget option for long-context writing",
        "tier": "budget",
        "strengths": ["prose", "long-context", "affordable"],
    },
    {
        "id": "openrouter/google/gemini-2.5-flash",
        "name": "Gemini 2.5 Flash (via OpenRouter)",
        "provider": "openrouter",
        "note": "Fast, large context window, good for editing",
        "tier": "budget",
        "strengths": ["fast", "long-context", "affordable"],
    },
    {
        "id": "openrouter/meta-llama/llama-3.3-70b-instruct",
        "name": "Llama 3.3 70B (via OpenRouter)",
        "provider": "openrouter",
        "note": "Strong open-source model, good for drafting",
        "tier": "budget",
        "strengths": ["prose", "open-source", "affordable"],
    },
    {
        "id": "openrouter/mistralai/mistral-large-latest",
        "name": "Mistral Large (via OpenRouter)",
        "provider": "openrouter",
        "note": "Strong reasoning, good for complex plots",
        "tier": "standard",
        "strengths": ["reasoning", "prose", "instruction-following"],
    },
    # ── Direct OpenAI ────────────────────────────────────────────────────
    {
        "id": "openai/gpt-4o",
        "name": "GPT-4o",
        "provider": "openai",
        "note": "OpenAI's flagship, strong all-around",
        "tier": "standard",
        "strengths": ["prose", "reasoning", "versatile"],
    },
    {
        "id": "openai/gpt-4o-mini",
        "name": "GPT-4o Mini",
        "provider": "openai",
        "note": "Fast and affordable for everyday writing",
        "tier": "budget",
        "strengths": ["fast", "affordable", "versatile"],
    },
    {
        "id": "openai/gpt-4.1",
        "name": "GPT-4.1",
        "provider": "openai",
        "note": "Latest generation, improved instruction following",
        "tier": "standard",
        "strengths": ["prose", "reasoning", "instruction-following"],
    },
    # ── Direct Anthropic ─────────────────────────────────────────────────
    {
        "id": "anthropic/claude-sonnet-4-20250514",
        "name": "Claude Sonnet 4",
        "provider": "anthropic",
        "note": "Best for prose quality and creative fiction",
        "tier": "standard",
        "strengths": ["prose", "reasoning", "instruction-following"],
    },
    {
        "id": "anthropic/claude-3-5-haiku-20241022",
        "name": "Claude 3.5 Haiku",
        "provider": "anthropic",
        "note": "Fast, quality, affordable",
        "tier": "budget",
        "strengths": ["fast", "prose", "affordable"],
    },
    {
        "id": "anthropic/claude-3-opus-20240229",
        "name": "Claude 3 Opus",
        "provider": "anthropic",
        "note": "Deep reasoning, nuanced prose",
        "tier": "premium",
        "strengths": ["prose", "reasoning", "nuanced"],
    },
    # ── Direct Google ────────────────────────────────────────────────────
    {
        "id": "google/gemini-2.5-pro",
        "name": "Gemini 2.5 Pro",
        "provider": "google",
        "note": "Strong reasoning, very large context",
        "tier": "standard",
        "strengths": ["reasoning", "long-context", "versatile"],
    },
    {
        "id": "google/gemini-2.5-flash",
        "name": "Gemini 2.5 Flash",
        "provider": "google",
        "note": "Fast and affordable with large context",
        "tier": "budget",
        "strengths": ["fast", "long-context", "affordable"],
    },
    # ── DeepSeek (direct) ────────────────────────────────────────────────
    {
        "id": "deepseek/deepseek-chat",
        "name": "DeepSeek V3",
        "provider": "deepseek",
        "note": "Excellent value, strong for long-form writing",
        "tier": "budget",
        "strengths": ["prose", "long-context", "affordable"],
    },
    {
        "id": "deepseek/deepseek-reasoner",
        "name": "DeepSeek R1",
        "provider": "deepseek",
        "note": "Deep reasoning for complex plot structures",
        "tier": "budget",
        "strengths": ["reasoning", "long-context", "affordable"],
    },
    # ── GLM (Zhipu, direct) ──────────────────────────────────────────────
    {
        "id": "glm/glm-4-plus",
        "name": "GLM-4 Plus",
        "provider": "glm",
        "note": "Zhipu's flagship, good Chinese and English prose",
        "tier": "standard",
        "strengths": ["prose", "bilingual", "reasoning"],
    },
    {
        "id": "glm/glm-4-flash",
        "name": "GLM-4 Flash",
        "provider": "glm",
        "note": "Fast and affordable from Zhipu",
        "tier": "budget",
        "strengths": ["fast", "affordable", "bilingual"],
    },
    # ── Qwen (Alibaba, direct) ──────────────────────────────────────────
    {
        "id": "qwen/qwen-max",
        "name": "Qwen Max",
        "provider": "qwen",
        "note": "Alibaba's flagship, strong bilingual writing",
        "tier": "standard",
        "strengths": ["prose", "bilingual", "reasoning"],
    },
    {
        "id": "qwen/qwen-plus",
        "name": "Qwen Plus",
        "provider": "qwen",
        "note": "Good balance of quality and cost",
        "tier": "budget",
        "strengths": ["prose", "bilingual", "affordable"],
    },
    # ── Mistral (direct) ─────────────────────────────────────────────────
    {
        "id": "mistral/mistral-large-latest",
        "name": "Mistral Large",
        "provider": "mistral",
        "note": "Strong European model, good for complex fiction",
        "tier": "standard",
        "strengths": ["reasoning", "prose", "instruction-following"],
    },
    # ── Groq (fast inference) ────────────────────────────────────────────
    {
        "id": "groq/llama-3.3-70b-versatile",
        "name": "Llama 3.3 70B (via Groq)",
        "provider": "groq",
        "note": "Ultra-fast inference, great for quick drafts",
        "tier": "budget",
        "strengths": ["fast", "affordable", "prose"],
    },
    # ── xAI ──────────────────────────────────────────────────────────────
    {
        "id": "xai/grok-3",
        "name": "Grok 3",
        "provider": "xai",
        "note": "xAI's flagship, unfiltered creative writing",
        "tier": "standard",
        "strengths": ["prose", "reasoning", "unfiltered"],
    },
    # ── Moonshot (Kimi, direct) ──────────────────────────────────────────
    {
        "id": "moonshot/moonshot-v1-128k",
        "name": "Kimi 128K",
        "provider": "moonshot",
        "note": "Very long context, good for full-novel editing",
        "tier": "standard",
        "strengths": ["long-context", "bilingual", "prose"],
    },
    # ── LM Studio (local — free, runs on your hardware) ──────────────────
    # Models below are popular GGUF quantizations people run in LM Studio.
    # The exact model name depends on which file you downloaded; these are
    # suggested starting points. LM Studio auto-detects loaded models.
    {
        "id": "lmstudio/llama-3.3-70b-instruct",
        "name": "Llama 3.3 70B (local)",
        "provider": "lmstudio",
        "note": "Strong open-source model, runs locally on 24+ GB VRAM",
        "tier": "free",
        "strengths": ["prose", "reasoning", "open-source"],
    },
    {
        "id": "lmstudio/qwen2.5-72b-instruct",
        "name": "Qwen 2.5 72B (local)",
        "provider": "lmstudio",
        "note": "Excellent bilingual model, large context, 48+ GB VRAM",
        "tier": "free",
        "strengths": ["prose", "bilingual", "long-context"],
    },
    {
        "id": "lmstudio/mistral-nemo-12b-instruct",
        "name": "Mistral Nemo 12B (local)",
        "provider": "lmstudio",
        "note": "Compact, fast, good prose quality for its size",
        "tier": "free",
        "strengths": ["fast", "prose", "open-source"],
    },
    {
        "id": "lmstudio/phi-4-14b",
        "name": "Phi-4 14B (local)",
        "provider": "lmstudio",
        "note": "Microsoft's small-but-strong model, runs on 8+ GB VRAM",
        "tier": "free",
        "strengths": ["fast", "reasoning", "open-source"],
    },
    {
        "id": "lmstudio/deepseek-r1-distill-llama-70b",
        "name": "DeepSeek R1 Distill 70B (local)",
        "provider": "lmstudio",
        "note": "Reasoning-focused distilled model, good for plot planning",
        "tier": "free",
        "strengths": ["reasoning", "open-source", "prose"],
    },
    {
        "id": "lmstudio/gemma-2-9b-instruct",
        "name": "Gemma 2 9B (local)",
        "provider": "lmstudio",
        "note": "Google's compact model, fast on modest hardware",
        "tier": "free",
        "strengths": ["fast", "affordable", "open-source"],
    },
    # ── Ollama (local — free, runs on your hardware) ─────────────────────
    # Ollama model names use the format "model:tag". Run `ollama pull <name>`
    # to download. Ollama auto-detects installed models.
    {
        "id": "ollama/llama3.3:70b",
        "name": "Llama 3.3 70B (Ollama)",
        "provider": "ollama",
        "note": "Strong open-source model, 24+ GB VRAM",
        "tier": "free",
        "strengths": ["prose", "reasoning", "open-source"],
    },
    {
        "id": "ollama/qwen2.5:72b",
        "name": "Qwen 2.5 72B (Ollama)",
        "provider": "ollama",
        "note": "Excellent bilingual model, 48+ GB VRAM",
        "tier": "free",
        "strengths": ["prose", "bilingual", "long-context"],
    },
    {
        "id": "ollama/mistral-nemo:12b",
        "name": "Mistral Nemo 12B (Ollama)",
        "provider": "ollama",
        "note": "Compact, fast, good prose for its size",
        "tier": "free",
        "strengths": ["fast", "prose", "open-source"],
    },
    {
        "id": "ollama/phi4:14b",
        "name": "Phi-4 14B (Ollama)",
        "provider": "ollama",
        "note": "Microsoft's small-but-strong, 8+ GB VRAM",
        "tier": "free",
        "strengths": ["fast", "reasoning", "open-source"],
    },
    {
        "id": "ollama/deepseek-r1:70b",
        "name": "DeepSeek R1 70B (Ollama)",
        "provider": "ollama",
        "note": "Reasoning-focused, good for plot planning",
        "tier": "free",
        "strengths": ["reasoning", "open-source", "prose"],
    },
    {
        "id": "ollama/gemma2:9b",
        "name": "Gemma 2 9B (Ollama)",
        "provider": "ollama",
        "note": "Google's compact model, fast on modest hardware",
        "tier": "free",
        "strengths": ["fast", "affordable", "open-source"],
    },
]


def get_catalog() -> list[dict]:
    """Return the full curated model catalog."""
    return list(CATALOG)


def get_catalog_by_provider(provider_id: str) -> list[dict]:
    """Return catalog entries for a specific provider."""
    return [m for m in CATALOG if m["provider"] == provider_id]
