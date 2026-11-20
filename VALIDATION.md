# Verification record

Generated-image simulation (20 November 2026): an isolated loopback receiver accepted two distinct 640 × 360 JPEGs produced by `simulate_sharing.py`. Both appeared in the authenticated gallery. The integration check used a shortened interval and confirmed there were no additional files after Stop. The normal interface sends one sample immediately and then waits 30 seconds between requests.

The separate verification replay uses a second loopback run at the normal interval. The receiver stored and listed two generated JPEGs 30.0 seconds apart. The gallery stayed unchanged for 35.0 seconds after the stop signal. The replay condenses the wait and is labeled as synthetic evidence.

Verified on Windows with Python 3.14.2, pygame-ce 2.5.8, Pillow 13.0.0 and PyInstaller 6.22.3 on 19 November 2026 (America/Toronto).

- `python -m unittest test_demo -q`: 2 tests passed. Synthetic images only; consent gate, authentication, malformed image rejection, image receipt, authenticated gallery, 30-second refresh, 20-image retention and traversal rejection verified.
- Upstream game initialized, ran its event loop and handled a timed quit using SDL dummy video/audio drivers. This verifies loading and basic execution, not interactive gameplay or sound.
- All three Windows applications built successfully. Latest build log: `build-verification.log`. Keep the full application folders, not just the exe files.
- The three-page assignment PDF was rendered and visually inspected.

Not yet verified: interactive packaged gameplay, actual desktop screenshot capture, live public ngrok access, the 30-second timed end-to-end desktop demonstration, and recording/upload/submission. These require a clean desktop, explicit consent in the companion, and the user's ngrok/YouTube/GitHub accounts. No real screenshots were collected during automated verification. Follow the README recording sequence and fill in the report evidence fields after performing it.

This is a consent-based adaptation. It does not claim to meet the PDF's hidden-Trojan requirement or guarantee marks.

Keyboard troubleshooting: test_keyboard.py passed for Enter, Right and A press/release and focus-loss clearing. The corrected separate build is MarioConsentDemoFixed. Interactive confirmation remains pending.

Troubleshooting update: added source/data maps to game packaging. Source-mode Enter-to-level transition passed; simulated Right-arrow input moved the player from x=110 to x=203. Interactive packaged confirmation is pending.
