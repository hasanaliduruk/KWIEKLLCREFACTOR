# Build & Sign

## Quick build (webview version)

```
build_shared.bat
```

This produces an **onedir** bundle `dist\OperationsToolkit_Webview\`
(exe + `_internal` folder, no UPX packing). The Inno Setup installer
(`installer.iss`) then bundles that whole folder into
`Output\OperationsToolkit_Setup.exe`.

### Why no UPX?
- **Windows Defender:** UPX-packed executables are a classic false-positive
  trigger, so we disable UPX (`upx=False` in the spec). The remaining Defender
  risk comes from the exe being **unsigned** — see signing below.

## Code signing (stops Defender warnings)

An unsigned exe built by PyInstaller is frequently flagged by SmartScreen /
Defender on other people's machines. The only real fix is a code-signing
certificate:

1. Get a **Authenticode** code-signing cert (e.g. Sectigo/Comodo, or a
   cheaper EV cert). For an individual, a standard OV cert works; EV gives
   instant SmartScreen reputation.
2. Sign the built exe:

   ```
   signtool sign /fd SHA256 /td SHA256 ^
     /tr http://timestamp.digicert.com ^
     /f your_cert.pfx /p YOUR_PFX_PASSWORD ^
     dist\OperationsToolkit_Webview.exe
   ```

3. Sign the installer too (Inno Setup can do this automatically — add a
   `SignTool` entry in `installer.iss`):

   ```
   [Setup]
   SignTool=innosetup_sign /fd sha256 /tr http://timestamp.digicert.com /td sha256 /f "your_cert.pfx" /p YOUR_PFX_PASSWORD $f
   ```

   Then run ISCC with `/Sinnosetup_sign="path\to\signtool.exe" ...`.

`build_shared.bat` will sign automatically if you set these environment
variables before running it:

```
set SIGN_CERT_PFX=C:\path\to\cert.pfx
set SIGN_CERT_PASSWORD=your_password
build_shared.bat
```

## Version

The app version is the `CURRENT_VERSION` constant in `app.py` (e.g. `v1.2.4`).
The repo-root `version.txt` is a **PyInstaller version resource file** — it
embeds Windows file properties (company name, description, file version) into
the built exe via the `version='../version.txt'` line in `build_webview.spec`.
It is NOT a plain version string; do not edit it as one. `installer.iss` has
its own `MyAppVersion` that must be bumped in lockstep. See `RELEASE.md`.
