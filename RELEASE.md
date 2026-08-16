# Release & Update Workflow

This document explains how updates are shipped so the app can update itself
like any normal Windows application (download a setup, install over the old
one — no manual unzip/reinstall).

## How the in-app updater works

1. On startup (and via the **Check for Updates** button) the app calls the
   GitHub Releases API for `hasali2603/KWIEKLLCREFACTOR`.
2. It compares the latest release `tag_name` (e.g. `v1.2.5`) with the bundled
   `CURRENT_VERSION` in `app.py`.
3. If a newer release exists, the Updates view shows the version, release
   notes, and an **Install Update** button.
4. Clicking it downloads the **setup installer** asset from the release and
   runs it silently (`/SILENT`). Inno Setup detects the same `AppId` and
   upgrades the existing install in place, then the app relaunches.

> The updater expects the release asset to be the **Inno Setup installer**
> (`OperationsToolkit_Setup.exe`), NOT the raw `OperationsToolkit_Webview.exe`.

## Building a new release (step by step)

### 1. Bump the version
- Edit `CURRENT_VERSION` in `app.py` (e.g. `"v1.2.5"`).
- Edit `MyAppVersion` in `installer.iss` to match (without the `v`).
- Edit `currentVersion` in `gui_web/app.js` (the Updates view badge) to match.
- (Optional) Edit the `FileVersion`/`ProductVersion` strings in the repo-root
  `version.txt` — that file is the PyInstaller **version resource** that
  embeds Windows file properties into the exe, not the app version string.

### 2. Build the app
```
build_shared.bat
```
This produces the onedir bundle `dist\OperationsToolkit_Webview\`
(PyInstaller onedir, no UPX — see BUILD.md for why).

### 3. Build the installer
Install [Inno Setup](https://jrsoftware.org/isdl.php) (free), then compile
`installer.iss` with ISCC:
```
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```
This produces `Output\OperationsToolkit_Setup.exe` (bundles the onedir folder).

### 4. Publish the GitHub release
- Create a new release tagged `v1.2.5` on GitHub.
- Upload `Output\OperationsToolkit_Setup.exe` as a release asset.
- Write the changelog in the release body (it shows in the app's notes modal).

That's it — the next time any user opens the app, the badge appears and they
can update with one click.

## First-time install for new users
New users just download `OperationsToolkit_Setup.exe` from the latest GitHub
release and run it. It installs to `Program Files`, adds Start Menu / Desktop
shortcuts, and registers an uninstaller.
