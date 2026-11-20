# COSC 3796 Assignment 2 consent based demonstration

A disclosed educational adaptation of Assignment 2. A visible companion shares the primary screen with a Python receiver every 30 seconds after the user ticks consent and clicks Start. The Mario launcher explains the companion before starting the original game. Closing Mario does not close the independently started companion. Stop or close the companion to end sharing. No startup registration, hidden tasks, automatic consent, or covert capture.

**Assignment differences:** the PDF asks for a Trojan inserted into the game and public screenshot access. This project uses a disclosure-first launcher, a separately started companion, and an authenticated gallery. The game itself does not upload screenshots. It demonstrates the data flow and continued sharing safely, but those differences may affect the rubric. Confirm the adaptation with the instructor. Do not claim full compliance or fabricate demonstration results.

## Windows setup

Install Python 3 with Tkinter and Git. Open PowerShell in this project folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

This creates a local virtual environment and downloads the upstream game at revision `f34087e4cc47f6cc70b46ced758b1070e64c4dc2`. Dependencies: Pillow, pygame-ce, PyInstaller. The upstream README targets older Python/pygame; this project uses pygame-ce. If Python is not found, install Python and reopen PowerShell. `-ExecutionPolicy Bypass` applies to this script invocation only.

## Run from source

Use three PowerShell terminals in this folder, in order:

```powershell
.\.venv\Scripts\python.exe receiver.py
```

Open http://127.0.0.1:8765 in a browser. Username is `demo`; password is the generated token printed by the receiver and stored in `.demo-token`. Do not record or commit it.

```powershell
.\.venv\Scripts\python.exe client.py
```

Close private windows. Read the disclosure, tick consent, click Start sharing. First capture is immediate, then every 30 seconds plus capture/upload time. Errors are visible and retried after 30 seconds. The receiver keeps only the latest 20 JPEGs in `captures/`, re-encodes incoming images, and limits request size. It listens only on loopback. It is a small demonstration server, not a production service.

```powershell
.\.venv\Scripts\python.exe launch_mario.py
```

Dismiss the disclosure. Controls: arrow keys move, A jumps, S runs/shoots. Stop sharing prevents future uploads; one upload already in progress can finish within the five-second network timeout. Close the companion to exit. Ctrl+C stops the receiver.

## Rehearse with generated images

`simulate_sharing.py` is an optional, separate exercise. It draws numbered JPEGs with a **GENERATED TEST IMAGE** label and an embedded UTC timestamp. The visible window sends them to the authenticated local gallery. This mode is useful when you want to demonstrate the flow using only synthetic data. The game can close while the simulation remains open.

1. Keep the screen sharing companion off. Start the receiver used in the recording at `video-dist/ScreenshotReceiver/ScreenshotReceiver.exe` if it is closed. Open the authenticated gallery at `http://127.0.0.1:8765/`.
2. Run this in PowerShell from the project folder. If you started `receiver.py` from source, replace `recorded` with `source`. If you started the receiver from `dist/`, use `built`.

   ```powershell
   .\.venv\Scripts\python.exe .\simulate_sharing.py --receiver recorded
   ```

3. Tick the consent box and click **Start simulation**. The first image is sent immediately. Refresh the gallery to see sample 001, then close Mario while the simulator stays visibly ON.
4. Wait 35 seconds and refresh for a later sample number and timestamp. Click **Stop simulation**. Once the window shows OFF, wait at least 35 seconds and refresh again. The newest timestamp should stay the same.

Run the simulator using Python. The recorded Windows build covers the original consent-based companion. The supplemental video segment replays the actual generated images from an isolated loopback verification run with condensed timing.

## Build Windows executables

Build on Windows, using the same environment as setup:

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

Keep `dist/MarioConsentDemo`, `dist/SharingCompanion`, and `dist/ScreenshotReceiver` as sibling folders. Do not move just the exe; each app needs its `_internal` folder. Run `dist/ScreenshotReceiver/ScreenshotReceiver.exe`, then `dist/SharingCompanion/SharingCompanion.exe`, then `dist/MarioConsentDemo/MarioConsentDemo.exe`. Receiver and companion share `dist/demo-data/.demo-token`; screenshots go in `dist/demo-data/captures`. Source mode uses the project folder instead, so use either all source apps or all built apps in a session. Console windows remain visible.

The video uses `build-video.ps1`, which builds the same three programs into `video-dist/`. When following that recording, start the three executables from `video-dist/` and keep its app folders together.

## Public gallery through ngrok

Only do this with non-sensitive demo content and explicit consent to making the gallery reachable through the tunnel provider. Install/sign in to ngrok using its official quickstart: https://ngrok.com/docs/gateway/endpoints/agent-cli-quickstart . Configure your own ngrok account token privately, then run:

```powershell
ngrok http 8765
```

Open the printed HTTPS forwarding URL, pass any ngrok interstitial, and log in using `demo` plus the receiver token. The gallery refreshes every 30 seconds. The companion still sends to the local receiver; ngrok exposes the gallery remotely. Authentication is intentional: the public link alone cannot disclose screenshots. Anyone with the password can view and upload, so keep it private and give the instructor temporary access separately if needed. Stop ngrok after the demo. Do not show tokens, browser password dialogs, or personal content in the video. Ngrok account setup and public publication are not automated by these scripts.

## Record the required demonstration

Use Windows Snipping Tool screen recording (Win+Shift+R if available) or OBS. Select the whole demo area so the game, companion, server timestamps and gallery can be seen. Use a clean desktop or test Windows account.

1. Show `launch_mario.py` disclosure, `client.py` consent gate and `share` function, and `receiver.py` upload/gallery routes. Explain the consent-based adaptation.
2. Start recording **before** running `build.ps1`. Record the actual build and successful output, not an old binary.
3. Start the built receiver, then ngrok. Authenticate to the public HTTPS gallery without exposing credentials. Start the built companion, explicitly consent, and click Start.
4. Run the newly built Mario executable. Show gameplay and a new gallery image with its UTC timestamp. Allow 30 seconds for capture and another 30 seconds for the gallery refresh; manually refresh if necessary and explain the timing.
5. Close Mario only. Keep the companion visible and ON. Change a harmless desktop item, wait at least 65 seconds, and show a later image timestamp and receiver POST log proving continued sharing.
6. Click STOP SHARING, wait at least 35 seconds, refresh, and show that no newer capture arrived. Close companion, stop ngrok and receiver.
7. Review recording for secrets. Upload it to YouTube as unlisted/public and check playback while signed out. Publish your own source repository, excluding ignored files. Submit GitHub URL, YouTube URL, and the completed PDF report.

If you cannot build while recording, fix the build first then record a fresh complete build. If gallery says 401, use the correct token for source versus packaged mode. If port 8765 is busy, stop the previous receiver. A blank gallery before Start is expected. A failed upload status usually means the receiver is stopped. No desktop capture is performed by the automated tests.

## Files and cleanup

`launch_mario.py`: disclosed game entry point. `client.py`: consent and screenshot transport. `receiver.py`: authenticated receipt, bounded storage and HTML gallery. `build.ps1`: three visible applications. `test_demo.py`: synthetic image and consent tests. `assignment-report.pdf`: explanation to complete with your identity and real submission links.

Delete `captures` (or `dist/demo-data/captures`) after stopping apps to remove retained screenshots. Delete `.demo-token` (or packaged equivalent) and restart receiver to rotate credentials; restart companion and log in again. Never commit screenshots, tokens, virtual environments, builds, or recordings. `.gitignore` excludes these. Review `git status` before publishing.

## Attribution and distribution

Game source: https://github.com/marblexu/PythonSuperMario at the revision above; upstream credits https://github.com/justinmeister/Mario-Level-1 . Game art and names belong to their respective owners. No license file was found at the upstream root; do not assume unrestricted redistribution. The upstream source and game assets are downloaded separately by setup and excluded from this repository. Review permissions before redistributing bundled game binaries. The added demonstration code is provided for this assignment; no third-party license is asserted.

PyInstaller build option reference: https://pyinstaller.org/en/stable/usage.html .

Keyboard compatibility: launch_mario.py tracks key-down/key-up events directly and clears held keys on focus loss. Press Enter at the title screen, then arrows to move and A to jump. The troubleshooting build is dist/MarioConsentDemoFixed/MarioConsentDemoFixed.exe; normal build.ps1 includes the same fix.
