# Open-Write

A local-first Markdown writing app for fiction and worldbuilding, with structured, context-aware AI review tools. Open-Write combines a distraction-free editor with an AI that reviews, critiques, and brainstorms on demand.

> Open-Write runs entirely on your machine. Your manuscript, profiles, and notes are plain Markdown files in a folder you control. Nothing is uploaded anywhere except the AI requests you explicitly trigger, and those go directly from your computer to your chosen AI provider.

## What it does

- **Markdown editor** with focused, distraction-free writing in a serif typeface (Tauri + CodeMirror 6)
- **Profile system** for characters, relationships, locations, and lore, with structured trait blocks and importance levels
- **Smart Advisor** runs Readability, Structure, and Context passes directly over your chapter; findings appear as colored inline highlights anchored to the exact passages, with accept / ignore / re-cast controls
- **Writing Companion** chat panel for conversational help (brainstorming, voice work, ad-hoc questions)
- **Series support** for multi-book projects with shared canonical profiles and per-book character arcs
- **Export** to a full manuscript, dated snapshots, and optional inclusion of summaries, notes, and profiles
- **Light + dark themes**

## Requirements

- Windows 10 or 11
- An OpenRouter API key for AI features
- ~60 MB free disk space for the installer

## Install

Download the latest installer from the Releases page and run the `.msi` file.

> Open-Write is not yet code-signed. When you run the installer, Windows SmartScreen may show a "Windows protected your PC" warning. Click **More info**, then **Run anyway** to proceed.

## First run

1. Launch Open-Write
2. Open Settings (gear icon) and paste your OpenRouter API key
3. Pick a default model (start with something inexpensive and upgrade if you want richer prose)
4. Click **New Project** on the home screen and choose a folder

Your project is just a folder. You can back it up, sync it to a private cloud drive, or commit it to a personal git repo. Open-Write won't touch any of that.

## Updates

Automatic updates are not configured for this build. Check for new versions manually from the Releases page.

## License

Apache License 2.0. See [LICENSE](LICENSE) for the full text.

## Project documentation

- [`docs/product-scope.md`](docs/product-scope.md) -- core goals, writing philosophy, locked product rules
- [`docs/architecture.md`](docs/architecture.md) -- three-layer architecture, dual storage model, folder layout, API surface
- [`docs/features.md`](docs/features.md) -- what the product does today, in detail
- [`docs/roadmap.md`](docs/roadmap.md) -- Scheduled, Proposed, and Nice-to-Have features
- [`CHANGELOG.md`](CHANGELOG.md) -- shipped changes per version

## Contributing

Issues and pull requests are welcome. The codebase is heavily commented and written for a learning audience. For larger changes, please open an issue first to discuss direction.

## Acknowledgements

Built with [Tauri](https://tauri.app/), [React](https://react.dev/), [CodeMirror](https://codemirror.net/), [FastAPI](https://fastapi.tiangolo.com/), and [OpenRouter](https://openrouter.ai/).

## About

Open-Write is a local-first Markdown writing application for fiction and worldbuilding with context- and content-aware AI review tools.
