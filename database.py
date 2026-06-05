import psycopg2
import psycopg2.extras
import bcrypt
import secrets
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# ─── Connection ───────────────────────────────────────────────────────────────
def _get_db_url():
    # 1. Streamlit secrets (Streamlit Cloud deployment)
    try:
        import streamlit as st
        return st.secrets["DATABASE_URL"]
    except Exception:
        pass
    # 2. Environment variable (local dev)
    url = os.environ.get("DATABASE_URL")
    if url:
        return url
    # 3. Hardcoded fallback
    return "postgresql://neondb_owner:npg_84AOmVnLvhkc@ep-falling-butterfly-aqapk41s.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

DB_URL = _get_db_url()

def get_conn():
    return psycopg2.connect(DB_URL, cursor_factory=psycopg2.extras.RealDictCursor)

# ─── Schema Setup ─────────────────────────────────────────────────────────────
def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id          SERIAL PRIMARY KEY,
                    username    TEXT UNIQUE NOT NULL,
                    email       TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    elo         INTEGER DEFAULT 1200,
                    wins        INTEGER DEFAULT 0,
                    losses      INTEGER DEFAULT 0,
                    draws       INTEGER DEFAULT 0,
                    created_at  TIMESTAMPTZ DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    token       TEXT PRIMARY KEY,
                    user_id     INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    expires_at  TIMESTAMPTZ NOT NULL,
                    created_at  TIMESTAMPTZ DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS online_games (
                    id          TEXT PRIMARY KEY,
                    white_id    INTEGER REFERENCES users(id),
                    black_id    INTEGER REFERENCES users(id),
                    fen         TEXT NOT NULL DEFAULT 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                    pgn_moves   TEXT DEFAULT '',
                    status      TEXT DEFAULT 'waiting',
                    result      TEXT,
                    white_draw_offer BOOLEAN DEFAULT FALSE,
                    black_draw_offer BOOLEAN DEFAULT FALSE,
                    created_at  TIMESTAMPTZ DEFAULT NOW(),
                    updated_at  TIMESTAMPTZ DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS game_chat (
                    id          SERIAL PRIMARY KEY,
                    game_id     TEXT REFERENCES online_games(id) ON DELETE CASCADE,
                    user_id     INTEGER REFERENCES users(id),
                    message     TEXT NOT NULL,
                    created_at  TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            conn.commit()

# ─── Auth ─────────────────────────────────────────────────────────────────────
def register_user(username: str, email: str, password: str) -> Dict:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id, username, elo",
                    (username.strip(), email.strip().lower(), hashed)
                )
                user = dict(cur.fetchone())
                conn.commit()
                return {"ok": True, "user": user}
    except psycopg2.errors.UniqueViolation:
        return {"ok": False, "error": "Username or email already exists"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def login_user(username: str, password: str) -> Dict:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE username = %s", (username.strip(),))
            user = cur.fetchone()
            if not user:
                return {"ok": False, "error": "User not found"}
            if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
                return {"ok": False, "error": "Wrong password"}
            # Create session
            token = secrets.token_urlsafe(32)
            expires = datetime.utcnow() + timedelta(days=7)
            cur.execute(
                "INSERT INTO sessions (token, user_id, expires_at) VALUES (%s, %s, %s)",
                (token, user["id"], expires)
            )
            conn.commit()
            return {"ok": True, "token": token, "user": dict(user)}

def get_user_by_token(token: str) -> Optional[Dict]:
    if not token:
        return None
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT u.* FROM users u
                JOIN sessions s ON s.user_id = u.id
                WHERE s.token = %s AND s.expires_at > NOW()
            """, (token,))
            row = cur.fetchone()
            return dict(row) if row else None

def logout_user(token: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM sessions WHERE token = %s", (token,))
            conn.commit()

def get_leaderboard(limit=10):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT username, elo, wins, losses, draws,
                       wins + losses + draws AS total_games
                FROM users ORDER BY elo DESC LIMIT %s
            """, (limit,))
            return [dict(r) for r in cur.fetchall()]

# ─── Online Game CRUD ─────────────────────────────────────────────────────────
def create_online_game(creator_id: int, play_as: str) -> str:
    game_id = secrets.token_urlsafe(8)
    white_id = creator_id if play_as == "white" else None
    black_id = creator_id if play_as == "black" else None
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO online_games (id, white_id, black_id, status)
                VALUES (%s, %s, %s, 'waiting')
            """, (game_id, white_id, black_id))
            conn.commit()
    return game_id

def join_online_game(game_id: str, joiner_id: int) -> Dict:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM online_games WHERE id = %s", (game_id,))
            game = cur.fetchone()
            if not game:
                return {"ok": False, "error": "Game not found"}
            if game["status"] != "waiting":
                return {"ok": False, "error": "Game already started or finished"}
            if game["white_id"] == joiner_id or game["black_id"] == joiner_id:
                return {"ok": False, "error": "You created this game"}

            if game["white_id"] is None:
                cur.execute("UPDATE online_games SET white_id=%s, status='active', updated_at=NOW() WHERE id=%s",
                            (joiner_id, game_id))
            elif game["black_id"] is None:
                cur.execute("UPDATE online_games SET black_id=%s, status='active', updated_at=NOW() WHERE id=%s",
                            (joiner_id, game_id))
            else:
                return {"ok": False, "error": "Game is full"}
            conn.commit()
            return {"ok": True}

def get_online_game(game_id: str) -> Optional[Dict]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT g.*,
                       w.username AS white_username, w.elo AS white_elo,
                       b.username AS black_username, b.elo AS black_elo
                FROM online_games g
                LEFT JOIN users w ON w.id = g.white_id
                LEFT JOIN users b ON b.id = g.black_id
                WHERE g.id = %s
            """, (game_id,))
            row = cur.fetchone()
            return dict(row) if row else None

def push_online_move(game_id: str, move_san: str, new_fen: str, game_over: bool, result: Optional[str]):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT pgn_moves FROM online_games WHERE id = %s", (game_id,))
            row = cur.fetchone()
            moves = row["pgn_moves"]
            moves = (moves + " " + move_san).strip() if moves else move_san

            status = "finished" if game_over else "active"
            cur.execute("""
                UPDATE online_games
                SET fen=%s, pgn_moves=%s, status=%s, result=%s,
                    white_draw_offer=FALSE, black_draw_offer=FALSE, updated_at=NOW()
                WHERE id=%s
            """, (new_fen, moves, status, result, game_id))

            if game_over and result:
                _update_elo_and_stats(cur, game_id, result)

            conn.commit()

def offer_draw(game_id: str, user_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT white_id, black_id FROM online_games WHERE id=%s", (game_id,))
            g = cur.fetchone()
            col = "white_draw_offer" if g["white_id"] == user_id else "black_draw_offer"
            cur.execute(f"UPDATE online_games SET {col}=TRUE, updated_at=NOW() WHERE id=%s", (game_id,))
            conn.commit()

def accept_draw(game_id: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE online_games SET status='finished', result='1/2-1/2',
                white_draw_offer=FALSE, black_draw_offer=FALSE, updated_at=NOW()
                WHERE id=%s
            """, (game_id,))
            _update_elo_and_stats(cur, game_id, "1/2-1/2")
            conn.commit()

def resign_game(game_id: str, user_id: int):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT white_id FROM online_games WHERE id=%s", (game_id,))
            g = cur.fetchone()
            result = "0-1" if g["white_id"] == user_id else "1-0"
            cur.execute("""
                UPDATE online_games SET status='finished', result=%s, updated_at=NOW()
                WHERE id=%s
            """, (result, game_id))
            _update_elo_and_stats(cur, game_id, result)
            conn.commit()

def _update_elo_and_stats(cur, game_id: str, result: str):
    cur.execute("SELECT white_id, black_id FROM online_games WHERE id=%s", (game_id,))
    g = cur.fetchone()
    if not g or not g["white_id"] or not g["black_id"]:
        return
    wid, bid = g["white_id"], g["black_id"]

    cur.execute("SELECT elo FROM users WHERE id=%s", (wid,))
    w_elo = cur.fetchone()["elo"]
    cur.execute("SELECT elo FROM users WHERE id=%s", (bid,))
    b_elo = cur.fetchone()["elo"]

    K = 32
    exp_w = 1 / (1 + 10 ** ((b_elo - w_elo) / 400))
    exp_b = 1 - exp_w

    if result == "1-0":
        sw, sb = 1, 0
    elif result == "0-1":
        sw, sb = 0, 1
    else:
        sw, sb = 0.5, 0.5

    new_w = max(100, int(w_elo + K * (sw - exp_w)))
    new_b = max(100, int(b_elo + K * (sb - exp_b)))

    w_col = ("wins" if sw == 1 else "losses" if sw == 0 else "draws")
    b_col = ("wins" if sb == 1 else "losses" if sb == 0 else "draws")

    cur.execute(f"UPDATE users SET elo=%s, {w_col}={w_col}+1 WHERE id=%s", (new_w, wid))
    cur.execute(f"UPDATE users SET elo=%s, {b_col}={b_col}+1 WHERE id=%s", (new_b, bid))

def get_waiting_games() -> list:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT g.id, g.created_at,
                       COALESCE(w.username, b.username) AS creator,
                       COALESCE(w.elo, b.elo) AS creator_elo,
                       CASE WHEN g.white_id IS NULL THEN 'black' ELSE 'white' END AS open_color
                FROM online_games g
                LEFT JOIN users w ON w.id = g.white_id
                LEFT JOIN users b ON b.id = g.black_id
                WHERE g.status = 'waiting'
                ORDER BY g.created_at DESC LIMIT 20
            """)
            return [dict(r) for r in cur.fetchall()]

def get_user_games(user_id: int) -> list:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT g.id, g.status, g.result, g.created_at,
                       w.username AS white_username, b.username AS black_username
                FROM online_games g
                LEFT JOIN users w ON w.id = g.white_id
                LEFT JOIN users b ON b.id = g.black_id
                WHERE g.white_id=%s OR g.black_id=%s
                ORDER BY g.updated_at DESC LIMIT 20
            """, (user_id, user_id))
            return [dict(r) for r in cur.fetchall()]

# ─── Chat ─────────────────────────────────────────────────────────────────────
def send_chat(game_id: str, user_id: int, message: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO game_chat (game_id, user_id, message) VALUES (%s, %s, %s)",
                (game_id, user_id, message[:200])
            )
            conn.commit()

def get_chat(game_id: str) -> list:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.message, c.created_at, u.username
                FROM game_chat c JOIN users u ON u.id = c.user_id
                WHERE c.game_id = %s ORDER BY c.created_at ASC LIMIT 50
            """, (game_id,))
            return [dict(r) for r in cur.fetchall()]