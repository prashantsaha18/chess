# ♟ ML Chess Online

Full-featured chess with AI opponents, real-time online multiplayer, user accounts, and Elo ratings.

## Features

### 🔐 User System
- Register / Login with hashed passwords (bcrypt)
- Session tokens (7-day expiry)
- Profile with Elo, W/L/D stats

### 🌐 Online Multiplayer
- Create a game (choose White/Black/Random)
- Join open games from the lobby
- Real-time board sync via Neon PostgreSQL (polls every 3s)
- In-game chat between players
- Draw offers / accept / decline
- Resign at any time
- Elo rating updates after each game (K=32, standard formula)

### 🤖 4 AI Difficulty Levels
| Mode         | Algorithm              | Est. Elo |
|--------------|------------------------|----------|
| Beginner     | Random + captures      | ~400     |
| Intermediate | Minimax depth-2        | ~800     |
| Difficult    | Alpha-Beta depth-3     | ~1200    |
| Advanced     | Full Alpha-Beta depth-4| ~1600    |

### 👥 Local 2-Player
Pass-and-play with custom player names.

## Deploy to Streamlit Cloud

1. Push this folder to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo → main file: `app.py`
4. Add secret in Streamlit Cloud dashboard:
   ```
   DATABASE_URL = "postgresql://neondb_owner:<password>@<host>/neondb?sslmode=require"
   ```
5. Deploy!

## Local Setup

```bash
pip install -r requirements.txt
export DATABASE_URL="postgresql://..."
streamlit run app.py
```

## Architecture

```
chess_app/
├── app.py           # Streamlit UI (auth, lobby, online game, AI game)
├── chess_engine.py  # AI: Minimax + Alpha-Beta + piece-square tables
├── database.py      # PostgreSQL: users, sessions, games, chat
├── requirements.txt
└── README.md
```

## Database Schema (Neon PostgreSQL)

- **users** — id, username, email, password_hash, elo, wins, losses, draws
- **sessions** — token, user_id, expires_at
- **online_games** — id, white_id, black_id, fen, pgn_moves, status, result, draw offers
- **game_chat** — game_id, user_id, message, created_at
