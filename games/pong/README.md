Pong (Mac-Friendly Tkinter)

Overview
- Classic Pong implemented with Python's built-in Tkinter.
- No external dependencies; runs on macOS out of the box.
- Supports single-player (AI) or two-player, pause, restart, and full-screen.

Controls
- W / S: Move left paddle up / down
- Up / Down: Move right paddle up / down (two-player)
- 1: Single-player vs AI
- 2: Two-player
- P: Pause / resume
- R: Restart round
- F: Toggle full-screen
- Q or Esc: Quit

Run
- From repo root: `python3 games/pong/main.py`
- Or use the helper script: `bash scripts/run_pong.sh`

Notes
- Designed at 900x600 for MacBook displays; scales fine on Retina.
- Tkinter ships with Python on macOS; no pip installs required.

