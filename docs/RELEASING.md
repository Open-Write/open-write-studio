# Releasing Open-Write

This is the runbook for cutting a new release. Most steps are automated by
`scripts\release.ps1`; the manual ones are flagged inline.

> **Current state:** The Tauri auto-updater is **disabled** in this build
> (no release feed or signing key is configured; see `tauri.conf.json` and
> `app/src/hooks/useAppUpdate.ts`). Releases are distributed as a plain
> `.msi` for manual download. The "One-time setup" steps for the updater
> and signing are deferred until Open-Write has its own release feed and a
> fresh minisign keypair. Until then, ignore the updater/signing sections.

---

## One-time setup (DEFERRED -- updater is currently disabled)

These steps are required only when re-enabling the auto-updater. Skip them
until a release feed and signing key exist.

### 1. Generate the updater signing keypair

The Tauri auto-updater verifies every downloaded bundle against a public
key embedded in the app. The matching private key signs each release.

> **Critical:** The public key bakes into the first signed binary. You
> can't change it later without making existing users manually reinstall.
> Generate it ONCE, store the private key safely, and reuse it for every
> release.

From the `app/` folder:

```powershell
npm run tauri signer generate -- -w "$HOME\.tauri\open-write.key"
```

This creates two files:
- `$HOME\.tauri\open-write.key`     -- the private key (KEEP SAFE)
- `$HOME\.tauri\open-write.key.pub` -- the public key

### 2. Embed the public key and re-enable the updater

- Add a `plugins.updater` block to `app/src-tauri/tauri.conf.json` with
  the public key and the Open-Write `latest.json` endpoint.
- Set `"createUpdaterArtifacts": true` in the `bundle` block.
- Restore the production check path in `app/src/hooks/useAppUpdate.ts`.

Commit the public key; keep the private key secret.

### 3. Stash the private key safely

Store the private key in a password manager. Verify you can read it back
before deleting the local file.

---

## Per release

Every release follows the same steps.

### 1. Update CHANGELOG.md

Move entries from `## [Unreleased]` into a new `## [X.Y.Z] - YYYY-MM-DD`
section just below it. Leave the `## [Unreleased]` heading in place with
empty subsections for the next round of work.

### 2. (Updater only) Export your signing key

Only needed while the auto-updater is enabled. In a new PowerShell session:

```powershell
$env:TAURI_SIGNING_PRIVATE_KEY = "<paste the contents of your .key file here>"
$env:TAURI_SIGNING_PRIVATE_KEY_PASSWORD = "<your password if you set one>"
```

> Don't paste these into a committed script file.

### 3. Run the release script

From the repo root:

```powershell
.\scripts\release.ps1 -Version X.Y.Z
```

This:
- Bumps the version in `package.json`, `tauri.conf.json`, `Cargo.toml`
- Builds the backend exe via PyInstaller
- Builds the Tauri bundle
- Generates `release-artifacts/latest.json` (when the updater is enabled)
- Copies the installer (+ `.sig` when signing) next to the manifest

### 4. Commit and push

```powershell
git add CHANGELOG.md app/package.json app/src-tauri/tauri.conf.json app/src-tauri/Cargo.toml
git commit -m "Release vX.Y.Z"
git tag vX.Y.Z
git push origin main --tags
```

### 5. Create the GitHub Release

Either via the website (paste the release notes, drag the installer from
`release-artifacts/` onto the upload zone) or via the `gh` CLI:

```powershell
gh release create vX.Y.Z `
  --title "Open-Write vX.Y.Z" `
  --notes-file CHANGELOG.md `
  release-artifacts/Open-Write*.msi `
  release-artifacts/latest.json
```

The exact installer filename varies; the script prints it at the end.

### 6. (Updater only) Verify the update flow

Only while the auto-updater is enabled: install the previous version on a
Windows machine and confirm the update banner appears and installs cleanly.

---

## Troubleshooting

### "PyInstaller fails with hidden import error"

The frozen exe is missing a transitive dependency. Open
`backend/backend.spec` and add the missing module to the `hiddenimports`
list, then rerun.

### "SmartScreen warning is back stronger"

Microsoft's SmartScreen ranks executables by reputation. New releases
start near zero and gain trust as more users install them. Workarounds:
- Get a code-signing certificate ($100-300/year)
- Submit your installer to Microsoft for analysis at
  https://www.microsoft.com/en-us/wdsi/filesubmission once per release

### "The auto-update banner never appears" (updater only)

Applies only while the updater is enabled. Checks:
1. Is the running version actually older than `latest.json` reports?
2. Is the running version a release build (`tauri build`), not dev?
3. Did the GitHub Release tag match the version in `latest.json`?
4. Does the public key in `tauri.conf.json` match the key that signed it?
