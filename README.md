# Photon - The Ultimate Game on Planet Earth

## Team

| GitHub Username | Real Name     |
| --------------- | ------------- |
| cadenWieties    | Caden Wieties |
| EJoeCodes       | Ethan Mulder  |

## Sprint 3 Features

1. Splash screen with logo
2. Player entry screen with hardware ID input
3. Postgres DB lookup and player insert
4. UDP send for equipment ID on player entry
5. Ability to change UDP target IP
6. F5 to start game and switch to play action display
7. F12 to clear all player entries
8. Play action display with red/green team rosters
9. 30 second game start countdown timer

## Sprint 4 Features

1. Splash screen with logo
2. Player entry screen with hardware ID input
3. Postgres DB lookup and player insert
4. UDP send for equipment ID on player entry
5. Ability to change UDP target IP
6. F5 to start game and switch to play action display
7. F12 to clear all player entries
8. 30 second game start countdown timer
9. 6 minute gameplay timer
10. Live scoring updates from UDP messages
11. Friendly fire handling
12. Base scoring with persistent base marker
13. Team total score updates
14. Play-by-play event log
15. Random MP3 music playback during the game
16. Game start/end broadcast codes

## Requirements

- Debian/Ubuntu Linux
- Python 3
- PostgreSQL (must be running before launch)
- python3-venv, python3-tk (installed by install.sh)

## Assets needed

Place these in the repo before running:

- `assets/logo.png`
- `assets/baseicon.jpg`
- MP3 files inside `assets/music/`

## Setup

```bash
chmod +x install.sh
./install.sh
source .venv/bin/activate
python3 ui_app.py
```

## Notes

- Run install.sh from the repo root
- Logo should be placed at assets/logo.png
- App falls back to mock DB and UDP if real services are unavailable
