# Sidecar binaries

This folder holds the **bundled Python backend** that Tauri ships inside the
Open-Write installer in release builds. The file produced here is a frozen
(frozen-by-PyInstaller) copy of the FastAPI backend, named with the platform
suffix Tauri's sidecar mechanism expects:

- `open-write-backend-x86_64-pc-windows-msvc.exe` -- Windows x64
- `open-write-backend-aarch64-apple-darwin`       -- macOS arm64
- `open-write-backend-x86_64-unknown-linux-gnu`   -- Linux x64

## The binary is NOT committed to the repo

No sidecar `.exe` is checked into git. The `tauri.conf.json` `externalBin`
entry is `binaries/open-write-backend`, and the real binary for each target
is built from source at release time and placed in this folder. The folder
is gitignored (`open-write-backend-*`, see `.gitignore` in this directory and
the backstop rule in the repo-root `.gitignore`) so a built binary can never
be committed accidentally.

## Where the file comes from

The binary is produced fresh on every release:

- **In CI (the source of truth for releases):** `.github/workflows/build-windows.yml`
  runs `uv run pyinstaller backend.spec` to compile the backend, copies the
  resulting `backend/dist/open-write-backend.exe` into this folder, then runs
  `npx tauri build`. Before the PyInstaller step the workflow deletes any
  sidecar already present in this folder, and after the copy it verifies the
  file exists -- so the installer always bundles a sidecar built during that
  same run, never a leftover from a previous build.

- **Locally:** run the PyInstaller step yourself from the repo root:

  ```powershell
  .\scripts\build-backend.ps1
  ```

  This calls PyInstaller against `backend/backend.spec` and copies the output
  into this folder. Re-run it whenever you change the FastAPI backend code and
  want to test the release build flow locally.

## Note for local dev mode

`cargo check` / `npm run tauri dev` require that the `externalBin` path exists.
Because no binary is committed, a fresh clone has no file here, so dev mode
needs a sidecar produced first -- run `scripts/build-backend.ps1` (or the
PyInstaller step manually) before starting `npm run tauri dev`. The sidecar
spawn itself is gated by `#[cfg(not(debug_assertions))]` in `lib.rs`, so the
committed-vs-built distinction only affects whether the Tauri shell compiles,
not whether a dev process is launched at runtime.
