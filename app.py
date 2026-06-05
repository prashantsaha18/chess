import streamlit as st
import chess
import time
import random
from chess_engine import ChessAI, get_ai, evaluate_board
import os
import streamlit.components.v1 as components

parent_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(parent_dir, "chessboard_component")
chessboard_component = components.declare_component("chessboard_component", path=build_dir)

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="♟ ML Chess Online",
    page_icon="♟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {
  --gold: #c9a84c; --cream: #f5f0e8; --dark: #1a1410; --brown: #3d2b1f;
  --green: #4ade80; --yellow: #facc15; --orange: #fb923c;
  --purple: #e879f9; --blue: #60a5fa; --red: #f87171;
}
.stApp { background: linear-gradient(135deg,#0f0c08 0%,#1a1410 50%,#0d0a06 100%); font-family:'IBM Plex Mono',monospace; }
h1,h2,h3 { font-family:'Playfair Display',serif !important; color:var(--gold) !important; }
.main-title { font-family:'Playfair Display',serif; font-size:3rem; font-weight:900; color:var(--gold); text-align:center; letter-spacing:.05em; text-shadow:0 0 40px rgba(201,168,76,.4); margin-bottom:.2rem; }
.subtitle { font-family:'IBM Plex Mono',monospace; color:#8a7a6a; text-align:center; font-size:.8rem; letter-spacing:.3em; text-transform:uppercase; margin-bottom:1.5rem; }
.card { background:rgba(201,168,76,.06); border:1px solid rgba(201,168,76,.15); border-radius:12px; padding:1.2rem 1.5rem; margin:.6rem 0; }
.badge { display:inline-block; padding:3px 12px; border-radius:20px; font-size:.72rem; font-weight:600; letter-spacing:.1em; text-transform:uppercase; font-family:'IBM Plex Mono',monospace; }
.badge-green  { background:#1a3a2a; color:#4ade80; border:1px solid #4ade80; }
.badge-yellow { background:#2a2a1a; color:#facc15; border:1px solid #facc15; }
.badge-orange { background:#2a1a1a; color:#fb923c; border:1px solid #fb923c; }
.badge-purple { background:#1f1020; color:#e879f9; border:1px solid #e879f9; }
.badge-blue   { background:#0e1e3a; color:#60a5fa; border:1px solid #60a5fa; }
.badge-red    { background:#2a0e0e; color:#f87171; border:1px solid #f87171; }
.badge-gold   { background:#2a1e08; color:#c9a84c; border:1px solid #c9a84c; }
.stat-row { display:flex; justify-content:space-between; align-items:center; padding:.35rem 0; border-bottom:1px solid rgba(201,168,76,.08); font-size:.8rem; color:#c8b89a; }
.stat-val { color:var(--gold); font-weight:600; }
.move-pill { display:inline-block; background:rgba(201,168,76,.1); border:1px solid rgba(201,168,76,.2); border-radius:4px; padding:2px 7px; margin:2px; font-size:.75rem; color:#c9a84c; }
.status-bar { background:rgba(201,168,76,.08); border:1px solid rgba(201,168,76,.2); border-radius:8px; padding:.7rem 1.2rem; text-align:center; font-size:.88rem; color:var(--cream); margin:.6rem 0; }
.check-alert { background:rgba(239,68,68,.15); border:1px solid rgba(239,68,68,.4); border-radius:8px; padding:.6rem 1rem; color:#fca5a5; font-size:.85rem; text-align:center; margin:.5rem 0; }
.winner-box { background:linear-gradient(135deg,rgba(201,168,76,.15),rgba(201,168,76,.05)); border:2px solid var(--gold); border-radius:12px; padding:1.5rem; text-align:center; margin:.8rem 0; }
.stButton > button { background:linear-gradient(135deg,#c9a84c,#a07830) !important; color:#0f0c08 !important; font-family:'IBM Plex Mono',monospace !important; font-weight:600 !important; border:none !important; border-radius:8px !important; letter-spacing:.05em !important; width:100% !important; }
.stButton > button:hover { background:linear-gradient(135deg,#e0b85c,#c9a84c) !important; box-shadow:0 4px 20px rgba(201,168,76,.3) !important; }
.stTextInput > div > div > input, .stTextInput > div > div > input:focus { background:rgba(201,168,76,.05) !important; border:1px solid rgba(201,168,76,.25) !important; border-radius:8px !important; color:var(--cream) !important; font-family:'IBM Plex Mono',monospace !important; }
.stSelectbox label,.stRadio label,.stTextInput label { color:#c9a84c !important; font-family:'IBM Plex Mono',monospace !important; font-size:.82rem !important; }
[data-testid="stSidebar"] { background:rgba(15,12,8,.97) !important; border-right:1px solid rgba(201,168,76,.15) !important; }
.divider { border:none; border-top:1px solid rgba(201,168,76,.12); margin:.8rem 0; }
.chess-board { display:grid; grid-template-columns:22px repeat(8,58px); grid-template-rows:repeat(8,58px) 22px; border:3px solid #c9a84c; border-radius:4px; overflow:hidden; box-shadow:0 8px 40px rgba(0,0,0,.7); }
.chess-cell { width:58px; height:58px; display:flex; align-items:center; justify-content:center; font-size:1.9rem; cursor:pointer; user-select:none; position:relative; }
.chess-cell:hover { filter:brightness(1.15); }
.rank-lbl,.file-lbl { display:flex; align-items:center; justify-content:center; font-size:.68rem; color:#c9a84c; font-family:'IBM Plex Mono',monospace; font-weight:600; background:#1a1410; }
.hint-dot::after { content:''; position:absolute; width:18px; height:18px; border-radius:50%; background:rgba(0,160,0,.4); }
.hint-cap::after { content:''; position:absolute; inset:0; border:4px solid rgba(0,180,0,.5); border-radius:50%; }
.chat-msg { padding:.4rem .8rem; margin:.25rem 0; border-radius:6px; font-size:.78rem; }
.chat-me { background:rgba(201,168,76,.12); border-left:3px solid #c9a84c; }
.chat-other { background:rgba(96,165,250,.08); border-left:3px solid #60a5fa; }
.online-indicator { display:inline-block; width:8px; height:8px; background:#4ade80; border-radius:50%; margin-right:6px; box-shadow:0 0 6px #4ade80; }
.elo-badge { display:inline-block; background:rgba(201,168,76,.15); border:1px solid rgba(201,168,76,.3); border-radius:4px; padding:1px 8px; font-size:.75rem; color:#c9a84c; }
.waiting-pulse { animation:pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
input[type="password"] { color:var(--cream) !important; }
</style>
""", unsafe_allow_html=True)

# ─── DB Init ──────────────────────────────────────────────────────────────────
@st.cache_resource
def setup_db():
    try:
        from database import init_db
        init_db()
        return True
    except Exception as e:
        st.warning(f"⚠ DB connection failed: {e}. Online features disabled.")
        return False

db_ok = setup_db()

# ─── State ────────────────────────────────────────────────────────────────────
DEFAULTS = {
    "board": chess.Board(), "game_mode": None, "ai_difficulty": "intermediate",
    "selected_square": None, "move_history": [], "game_over": False,
    "player_color": chess.WHITE, "ai": None, "last_move": None,
    "promotion_pending": None, "captured_white": [], "captured_black": [],
    "player1_name": "Player 1", "player2_name": "Player 2",
    "flip_board": False,
    # Auth
    "auth_token": None, "current_user": None,
    # Online
    "online_game_id": None, "chat_input": "", "last_online_fen": None,
    "online_color": None,
    "last_click_timestamp": 0,
    "last_clicked_val": -1,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── Helpers ──────────────────────────────────────────────────────────────────
PIECE_SYMBOLS = {
    (chess.PAWN,chess.WHITE):'♙',(chess.PAWN,chess.BLACK):'♟',
    (chess.KNIGHT,chess.WHITE):'♘',(chess.KNIGHT,chess.BLACK):'♞',
    (chess.BISHOP,chess.WHITE):'♗',(chess.BISHOP,chess.BLACK):'♝',
    (chess.ROOK,chess.WHITE):'♖',(chess.ROOK,chess.BLACK):'♜',
    (chess.QUEEN,chess.WHITE):'♕',(chess.QUEEN,chess.BLACK):'♛',
    (chess.KING,chess.WHITE):'♔',(chess.KING,chess.BLACK):'♚',
}
FILE_NAMES = 'abcdefgh'
RANK_NAMES = '12345678'

def get_clicked_square(clicked_sq):
    if clicked_sq is None:
        return None
    if isinstance(clicked_sq, dict):
        click_time = clicked_sq.get("timestamp")
        if click_time != st.session_state.get("last_click_timestamp"):
            st.session_state.last_click_timestamp = click_time
            return clicked_sq.get("sq")
        return None
    if isinstance(clicked_sq, int):
        if clicked_sq != st.session_state.get("last_clicked_val"):
            st.session_state.last_clicked_val = clicked_sq
            return clicked_sq
        return None
    if isinstance(clicked_sq, str):
        try:
            val = int(clicked_sq)
            if val != st.session_state.get("last_clicked_val"):
                st.session_state.last_clicked_val = val
                return val
        except ValueError:
            pass
    return None

def get_legal_dests(board, from_sq):
    return {m.to_square for m in board.legal_moves if m.from_square == from_sq}

def do_move(board, move):
    captured = board.piece_at(move.to_square)
    if board.is_en_passant(move):
        ep_sq = chess.square(chess.square_file(move.to_square), chess.square_rank(move.from_square))
        captured = board.piece_at(ep_sq)
    if captured:
        sym = PIECE_SYMBOLS.get((captured.piece_type, captured.color), '')
        if captured.color == chess.WHITE:
            st.session_state.captured_white.append(sym)
        else:
            st.session_state.captured_black.append(sym)
    san = board.san(move)
    board.push(move)
    st.session_state.move_history.append(san)
    st.session_state.last_move = move
    return san

def needs_promotion(board, move):
    p = board.piece_at(move.from_square)
    if p and p.piece_type == chess.PAWN:
        r = chess.square_rank(move.to_square)
        if (p.color == chess.WHITE and r == 7) or (p.color == chess.BLACK and r == 0):
            return True
    return False

MODE_INFO = {
    "beginner":     {"label":"Beginner",    "elo":"~400",  "depth":0,"badge":"badge-green", "desc":"Random with captures"},
    "intermediate": {"label":"Intermediate","elo":"~800",  "depth":2,"badge":"badge-yellow","desc":"Minimax depth-2"},
    "difficult":    {"label":"Difficult",   "elo":"~1200", "depth":3,"badge":"badge-orange","desc":"Alpha-Beta depth-3"},
    "advanced":     {"label":"Advanced",    "elo":"~1600", "depth":4,"badge":"badge-purple","desc":"Full Alpha-Beta depth-4"},
    "two_player":   {"label":"2 Players",   "elo":"—",     "depth":0,"badge":"badge-blue",  "desc":"Local pass-and-play"},
    "online":       {"label":"Online",      "elo":"Live",  "depth":0,"badge":"badge-gold",  "desc":"Play vs real opponents"},
}

def status_text(board, mode, pcolor):
    if board.is_checkmate():
        winner = "Black" if board.turn == chess.WHITE else "White"
        if mode == "two_player":
            nm = st.session_state.player1_name if winner=="White" else st.session_state.player2_name
            return f"♚ Checkmate! {nm} wins!"
        return f"♚ Checkmate! {'You lose!' if board.turn==pcolor else 'You win!'}"
    if board.is_stalemate():           return "½ Stalemate — Draw!"
    if board.is_insufficient_material(): return "½ Draw — Insufficient material"
    if board.is_fifty_moves():         return "½ Draw — 50-move rule"
    if board.is_repetition():          return "½ Draw — Threefold repetition"
    if board.is_check():               return "⚠ Check!"
    turn = "White" if board.turn==chess.WHITE else "Black"
    if mode == "two_player":
        nm = st.session_state.player1_name if board.turn==chess.WHITE else st.session_state.player2_name
        return f"▶ {nm}'s turn ({turn})"
    if mode == "online":
        return f"▶ {'Your' if board.turn==pcolor else 'Opponent'}'s turn ({turn})"
    return "▶ Your turn" if board.turn==pcolor else "⏳ AI thinking..."

def render_board_html(board, flip=False):
    sel = st.session_state.selected_square
    last = st.session_state.last_move
    legal_dests = get_legal_dests(board, sel) if sel is not None else set()
    files = range(7,-1,-1) if flip else range(8)
    ranks = range(8) if flip else range(7,-1,-1)
    LIGHT,DARK,SEL_L,SEL_D = "#f0d9b5","#b58863","#7fc97f","#5a9c5a"
    html = '<div class="chess-board">'
    html += '<div class="rank-lbl"></div>'
    for f in files:
        html += f'<div class="file-lbl">{FILE_NAMES[f]}</div>'
    for r in ranks:
        html += f'<div class="rank-lbl">{RANK_NAMES[r]}</div>'
        for f in files:
            sq = chess.square(f,r)
            piece = board.piece_at(sq)
            is_light = (f+r)%2==1
            bg = LIGHT if is_light else DARK
            extra = ""
            if sq==sel:
                bg = SEL_L if is_light else SEL_D
            elif last and (sq==last.from_square or sq==last.to_square):
                bg = "#d4c87a" if is_light else "#9e9a4a"
            if sq in legal_dests:
                extra = "hint-cap" if piece else "hint-dot"
            if piece and piece.piece_type==chess.KING and board.is_check() and piece.color==board.turn:
                bg = "#cc3c3c" if is_light else "#a02828"
            sym = PIECE_SYMBOLS.get((piece.piece_type,piece.color),'') if piece else ''
            html += f'<div class="chess-cell {extra}" style="background:{bg};" data-sq="{sq}">{sym}</div>'
    html += '<div class="rank-lbl"></div>'
    for f in files:
        html += f'<div class="file-lbl">{FILE_NAMES[f]}</div>'
    html += '</div>'
    return html

# ─── Auth UI ──────────────────────────────────────────────────────────────────
def auth_sidebar():
    user = st.session_state.current_user
    if user:
        st.markdown(f"""
        <div class="card">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:.5rem;">
            <span class="online-indicator"></span>
            <strong style="color:#c9a84c;">{user['username']}</strong>
          </div>
          <div class="stat-row"><span>Elo</span><span class="stat-val">{user['elo']}</span></div>
          <div class="stat-row"><span>W/L/D</span><span class="stat-val">{user['wins']}/{user['losses']}/{user['draws']}</span></div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚪 Logout"):
            if db_ok:
                from database import logout_user
                logout_user(st.session_state.auth_token)
            st.session_state.current_user = None
            st.session_state.auth_token = None
            st.rerun()
    else:
        tab_login, tab_reg = st.tabs(["Login", "Register"])
        with tab_login:
            uname = st.text_input("Username", key="li_user")
            pwd   = st.text_input("Password", type="password", key="li_pass")
            if st.button("🔑 Login"):
                if not db_ok:
                    st.error("DB offline"); return
                from database import login_user
                res = login_user(uname, pwd)
                if res["ok"]:
                    st.session_state.auth_token = res["token"]
                    st.session_state.current_user = res["user"]
                    st.success(f"Welcome, {res['user']['username']}!")
                    st.rerun()
                else:
                    st.error(res["error"])
        with tab_reg:
            ru = st.text_input("Username", key="reg_u")
            re = st.text_input("Email",    key="reg_e")
            rp = st.text_input("Password", type="password", key="reg_p")
            if st.button("📝 Register"):
                if not db_ok:
                    st.error("DB offline"); return
                if len(rp) < 6:
                    st.error("Password must be ≥ 6 chars"); return
                from database import register_user
                res = register_user(ru, re, rp)
                if res["ok"]:
                    st.success("Account created! Please login.")
                else:
                    st.error(res["error"])

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="main-title" style="font-size:1.8rem;">♟ ML Chess</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle" style="font-size:.65rem;">Online · AI · Multiplayer</div>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Auth
    auth_sidebar()
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown("### 🎮 Game Mode")
    mode_opts = list(MODE_INFO.keys())
    mode_labels = [MODE_INFO[m]["label"] for m in mode_opts]
    sel_idx = st.radio("mode", range(len(mode_opts)), format_func=lambda i: mode_labels[i], index=1, label_visibility="collapsed")
    mode_choice = mode_opts[sel_idx]

    if mode_choice not in ("two_player","online"):
        player_side = st.radio("Play as", ["White ♔","Black ♚"], index=0)
        st.session_state.player_color = chess.WHITE if "White" in player_side else chess.BLACK

    if mode_choice == "two_player":
        st.session_state.player1_name = st.text_input("White player", value=st.session_state.player1_name)
        st.session_state.player2_name = st.text_input("Black player", value=st.session_state.player2_name)

    info = MODE_INFO[mode_choice]
    st.markdown(f"""
    <div class="card">
      <span class="{info['badge']} badge">{info['label']}</span>
      <div style="margin-top:.6rem;">
        <div class="stat-row"><span>Est. Elo</span><span class="stat-val">{info['elo']}</span></div>
        <div class="stat-row" style="border:none;"><span style="color:#7a6a5a;font-size:.74rem;">{info['desc']}</span></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🆕 New Game"):
            if mode_choice == "online" and not st.session_state.current_user:
                st.error("Login to play online")
            else:
                st.session_state.board = chess.Board()
                st.session_state.game_mode = mode_choice
                st.session_state.selected_square = None
                st.session_state.move_history = []
                st.session_state.game_over = False
                st.session_state.last_move = None
                st.session_state.promotion_pending = None
                st.session_state.captured_white = []
                st.session_state.captured_black = []
                st.session_state.online_game_id = None
                st.session_state.online_color = None
                st.session_state.last_online_fen = None
                st.session_state.ai = None if mode_choice in ("two_player","online") else get_ai(mode_choice)
                st.rerun()
    with col_b:
        if st.button("↩ Undo"):
            if st.session_state.board.move_stack and st.session_state.game_mode not in ("online",):
                st.session_state.board.pop()
                if st.session_state.move_history: st.session_state.move_history.pop()
                if st.session_state.game_mode not in ("two_player",) and st.session_state.board.move_stack:
                    st.session_state.board.pop()
                    if st.session_state.move_history: st.session_state.move_history.pop()
                st.session_state.selected_square = None
                st.session_state.last_move = None
                st.session_state.game_over = False
                st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    cap_w = " ".join(st.session_state.captured_white) or "—"
    cap_b = " ".join(st.session_state.captured_black) or "—"
    st.markdown(f'<div style="font-size:.85rem;color:#f5f0e8;margin:.2rem 0;">⬛ took: {cap_w}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:.85rem;color:#8a7a6a;margin:.2rem 0;">⬜ took: {cap_b}</div>', unsafe_allow_html=True)

# ─── Main ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">♟ ML Chess Online</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Minimax AI · Real-time Online Play · Elo Ranking</div>', unsafe_allow_html=True)

if st.session_state.game_mode is None:
    # Landing
    st.markdown("""
    <div style="text-align:center;padding:2rem 0 1rem;">
      <div style="font-size:4rem;">♛</div>
      <div style="color:#c8b89a;font-family:\'IBM Plex Mono\',monospace;font-size:.95rem;margin:.5rem 0;">
        Select a mode in the sidebar and press <strong style="color:#c9a84c;">New Game</strong>
      </div>
    </div>
    """, unsafe_allow_html=True)
    cols = st.columns(3)
    for i,(k,v) in enumerate(MODE_INFO.items()):
        with cols[i%3]:
            st.markdown(f"""
            <div class="card" style="text-align:center;min-height:130px;">
              <div class="{v['badge']} badge" style="margin-bottom:.6rem;">{v['label']}</div>
              <div style="color:#c9a84c;font-size:1.1rem;font-weight:700;">{v['elo']}</div>
              <div style="color:#7a6a5a;font-size:.72rem;margin-top:.3rem;">{v['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
    st.stop()

# ─── ONLINE MODE ──────────────────────────────────────────────────────────────
if st.session_state.game_mode == "online":
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=3000, key="online_refresh")

    user = st.session_state.current_user
    if not user:
        st.error("You must be logged in to play online.")
        st.stop()

    from database import (create_online_game, join_online_game, get_online_game,
                          push_online_move, get_waiting_games, get_user_games,
                          offer_draw, accept_draw, resign_game, send_chat, get_chat,
                          get_leaderboard, get_user_by_token)

    # Refresh user stats
    fresh = get_user_by_token(st.session_state.auth_token)
    if fresh:
        st.session_state.current_user = fresh
        user = fresh

    gid = st.session_state.online_game_id

    # ── No active game: lobby ──────────────────────────────────────────────────
    if not gid:
        tab_lobby, tab_create, tab_history, tab_lb = st.tabs(["🏠 Lobby","➕ Create Game","📋 My Games","🏆 Leaderboard"])

        with tab_lobby:
            st.markdown("### Open Games")
            waiting = get_waiting_games()
            if not waiting:
                st.markdown('<div class="card" style="text-align:center;color:#7a6a5a;">No open games. Create one!</div>', unsafe_allow_html=True)
            for g in waiting:
                col1,col2,col3 = st.columns([3,2,2])
                with col1:
                    st.markdown(f'<div style="color:#c8b89a;font-size:.85rem;">🎮 <strong style="color:#c9a84c;">{g["creator"]}</strong> <span class="elo-badge">{g["creator_elo"]}</span></div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div style="font-size:.8rem;color:#7a6a5a;">Plays <strong style="color:#f5f0e8;">{g["open_color"]}</strong></div>', unsafe_allow_html=True)
                with col3:
                    if st.button(f"Join", key=f"join_{g['id']}"):
                        res = join_online_game(g["id"], user["id"])
                        if res["ok"]:
                            game_data = get_online_game(g["id"])
                            st.session_state.online_game_id = g["id"]
                            st.session_state.online_color = chess.WHITE if game_data["white_id"]==user["id"] else chess.BLACK
                            st.session_state.board = chess.Board()
                            st.session_state.move_history = []
                            st.session_state.last_move = None
                            st.session_state.game_over = False
                            st.rerun()
                        else:
                            st.error(res["error"])
                st.markdown('<hr class="divider">', unsafe_allow_html=True)

        with tab_create:
            st.markdown("### Create a New Online Game")
            play_as = st.radio("Play as", ["White ♔","Black ♚","Random 🎲"], horizontal=True)
            if st.button("🎮 Create Game & Wait for Opponent"):
                color_choice = "white" if "White" in play_as else ("black" if "Black" in play_as else random.choice(["white","black"]))
                new_gid = create_online_game(user["id"], color_choice)
                st.session_state.online_game_id = new_gid
                st.session_state.online_color = chess.WHITE if color_choice=="white" else chess.BLACK
                st.session_state.board = chess.Board()
                st.session_state.move_history = []
                st.session_state.last_move = None
                st.session_state.game_over = False
                st.rerun()

        with tab_history:
            st.markdown("### My Recent Games")
            games = get_user_games(user["id"])
            if not games:
                st.markdown('<div class="card" style="color:#7a6a5a;">No games yet.</div>', unsafe_allow_html=True)
            for g in games:
                w,b = g["white_username"] or "?", g["black_username"] or "?"
                res = g["result"] or "—"
                status = g["status"]
                badge = "badge-green" if (res=="1-0" and g.get("white_username")==user["username"]) or (res=="0-1" and g.get("black_username")==user["username"]) else ("badge-red" if res in ("1-0","0-1") else "badge-yellow")
                st.markdown(f"""
                <div class="card" style="display:flex;justify-content:space-between;align-items:center;padding:.7rem 1rem;">
                  <span style="color:#c8b89a;font-size:.82rem;">♔ {w} vs ♚ {b}</span>
                  <span class="{badge} badge">{res if status=='finished' else status}</span>
                  {'<a href="?gid='+g["id"]+'" style="color:#c9a84c;font-size:.75rem;">Resume</a>' if status=='active' else ''}
                </div>
                """, unsafe_allow_html=True)
                if status == "active":
                    if st.button(f"▶ Resume", key=f"resume_{g['id']}"):
                        gd = get_online_game(g["id"])
                        st.session_state.online_game_id = g["id"]
                        st.session_state.online_color = chess.WHITE if gd["white_id"]==user["id"] else chess.BLACK
                        b2 = chess.Board()
                        for san in gd["pgn_moves"].split() if gd["pgn_moves"] else []:
                            try: b2.push_san(san)
                            except: pass
                        st.session_state.board = b2
                        st.session_state.move_history = gd["pgn_moves"].split() if gd["pgn_moves"] else []
                        st.session_state.game_over = False
                        st.rerun()

        with tab_lb:
            st.markdown("### 🏆 Leaderboard")
            lb = get_leaderboard(15)
            st.markdown("""
            <div class="card">
            <div class="stat-row" style="font-weight:700;color:#c9a84c;">
              <span>#  Player</span><span>Elo</span><span>W / L / D</span>
            </div>""", unsafe_allow_html=True)
            for i,row in enumerate(lb):
                medal = ["🥇","🥈","🥉"][i] if i < 3 else f"{i+1}."
                me = "color:#c9a84c;font-weight:700;" if row["username"]==user["username"] else ""
                st.markdown(f"""
                <div class="stat-row" style="{me}">
                  <span>{medal} {row['username']}</span>
                  <span class="stat-val">{row['elo']}</span>
                  <span style="font-size:.75rem;">{row['wins']}/{row['losses']}/{row['draws']}</span>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    # ── Active online game ─────────────────────────────────────────────────────
    game_data = get_online_game(gid)
    if not game_data:
        st.error("Game not found.")
        st.session_state.online_game_id = None
        st.rerun()

    my_color = st.session_state.online_color
    board = st.session_state.board

    # Sync from DB
    if game_data["status"] == "waiting":
        st.markdown(f"""
        <div class="card" style="text-align:center;padding:2rem;">
          <div class="waiting-pulse" style="font-size:2.5rem;margin-bottom:1rem;">⏳</div>
          <div style="color:#c9a84c;font-size:1.1rem;font-weight:700;">Waiting for opponent…</div>
          <div style="color:#7a6a5a;font-size:.82rem;margin-top:.5rem;">Share Game ID: <strong style="color:#c8b89a;">{gid}</strong></div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("❌ Cancel Game"):
            st.session_state.online_game_id = None
            st.rerun()
        st.stop()

    # Sync moves from DB
    db_moves = game_data["pgn_moves"].split() if game_data["pgn_moves"] else []
    if len(db_moves) != len(st.session_state.move_history):
        b2 = chess.Board()
        for san in db_moves:
            try: b2.push_san(san)
            except: pass
        st.session_state.board = b2
        st.session_state.move_history = db_moves
        if b2.move_stack:
            st.session_state.last_move = b2.peek()
        board = b2

    if game_data["status"] == "finished" and not st.session_state.game_over:
        st.session_state.game_over = True

    # Player names
    w_name = game_data["white_username"] or "?"
    b_name = game_data["black_username"] or "?"
    w_elo  = game_data["white_elo"] or "?"
    b_elo  = game_data["black_elo"] or "?"

    col_board, col_side = st.columns([3,2], gap="large")

    with col_board:
        # Player tags
        top_name    = b_name if my_color==chess.WHITE else w_name
        top_elo     = b_elo  if my_color==chess.WHITE else w_elo
        bottom_name = w_name if my_color==chess.WHITE else b_name
        bottom_elo  = w_elo  if my_color==chess.WHITE else b_elo
        top_sym    = "♟" if my_color==chess.WHITE else "♙"
        bottom_sym = "♙" if my_color==chess.WHITE else "♟"

        st.markdown(f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:.4rem;"><span style="font-size:1.4rem;">{top_sym}</span><strong style="color:#c8b89a;">{top_name}</strong><span class="elo-badge">{top_elo}</span></div>', unsafe_allow_html=True)

        stat = status_text(board, "online", my_color)
        is_check = board.is_check()
        st.markdown(f'<div class="{"check-alert" if is_check else "status-bar"}">{stat}</div>', unsafe_allow_html=True)

        # Draw offer notification
        my_is_white = my_color == chess.WHITE
        opp_offered = game_data["black_draw_offer"] if my_is_white else game_data["white_draw_offer"]
        if opp_offered and not st.session_state.game_over:
            st.warning("🤝 Opponent offers a draw!")
            dc1,dc2 = st.columns(2)
            with dc1:
                if st.button("✅ Accept Draw"):
                    accept_draw(gid)
                    st.session_state.game_over = True
                    st.rerun()
            with dc2:
                if st.button("❌ Decline"):
                    st.rerun()

        # Promotion
        if st.session_state.promotion_pending:
            st.markdown('<div class="card"><strong style="color:#c9a84c;">Choose promotion:</strong></div>', unsafe_allow_html=True)
            pc1,pc2,pc3,pc4 = st.columns(4)
            promo_p = [(chess.QUEEN,"♕","Queen"),(chess.ROOK,"♖","Rook"),(chess.BISHOP,"♗","Bishop"),(chess.KNIGHT,"♘","Knight")]
            for i,(pt,sym,nm) in enumerate(promo_p):
                with [pc1,pc2,pc3,pc4][i]:
                    if st.button(f"{sym}\n{nm}", key=f"pro_{pt}"):
                        pend = st.session_state.promotion_pending
                        mv = chess.Move(pend.from_square, pend.to_square, promotion=pt)
                        san = do_move(board, mv)
                        st.session_state.promotion_pending = None
                        is_over = board.is_game_over()
                        result = board.result() if is_over else None
                        push_online_move(gid, san, board.fen(), is_over, result)
                        if is_over: st.session_state.game_over = True
                        st.rerun()

        # Board
        flip = (my_color == chess.BLACK)
        board_html = render_board_html(board, flip=flip)
        clicked_sq = chessboard_component(html=board_html, key=f"online_board_{gid}", height=510)
        
        clicked = get_clicked_square(clicked_sq)
        if clicked is not None and not st.session_state.game_over and game_data["status"]=="active":
            is_my_turn = board.turn == my_color
            if is_my_turn and not st.session_state.promotion_pending:
                sel = st.session_state.selected_square
                if sel is None:
                    p = board.piece_at(clicked)
                    if p and p.color == board.turn:
                        st.session_state.selected_square = clicked
                else:
                    dests = get_legal_dests(board, sel)
                    if clicked in dests:
                        mv = chess.Move(sel, clicked)
                        if needs_promotion(board, mv):
                            st.session_state.promotion_pending = mv
                            st.session_state.selected_square = None
                        else:
                            legal = [m for m in board.legal_moves if m.from_square==sel and m.to_square==clicked]
                            if legal:
                                san = do_move(board, legal[0])
                                is_over = board.is_game_over()
                                result = board.result() if is_over else None
                                push_online_move(gid, san, board.fen(), is_over, result)
                                if is_over:
                                    st.session_state.game_over = True
                        st.session_state.selected_square = None
                    elif board.piece_at(clicked) and board.piece_at(clicked).color==board.turn:
                        st.session_state.selected_square = clicked
                    else:
                        st.session_state.selected_square = None
            st.rerun()

        st.markdown(f'<div style="display:flex;align-items:center;gap:10px;margin-top:.4rem;"><span style="font-size:1.4rem;">{bottom_sym}</span><strong style="color:#c9a84c;">{bottom_name}</strong><span class="elo-badge">{bottom_elo}</span><span class="badge-green badge" style="font-size:.65rem;">YOU</span></div>', unsafe_allow_html=True)

        # Game over
        if st.session_state.game_over:
            res = game_data.get("result") or (board.result() if board.is_game_over() else "?")
            if res == "1-0":
                winner_name = w_name
            elif res == "0-1":
                winner_name = b_name
            else:
                winner_name = None
            msg = f"🏆 {winner_name} wins!" if winner_name else "½-½ Draw!"
            st.markdown(f'<div class="winner-box"><div style="font-size:2rem;">♛</div><div style="color:#c9a84c;font-size:1.2rem;font-weight:700;">{msg}</div><div style="color:#8a7a6a;font-size:.8rem;margin-top:.3rem;">Elo updated!</div></div>', unsafe_allow_html=True)
            if st.button("🏠 Back to Lobby"):
                st.session_state.online_game_id = None
                st.session_state.game_over = False
                st.rerun()

    with col_side:
        # Action buttons
        if not st.session_state.game_over:
            ac1,ac2 = st.columns(2)
            with ac1:
                if st.button("🤝 Offer Draw"):
                    offer_draw(gid, user["id"])
                    st.success("Draw offered!")
            with ac2:
                if st.button("🏳️ Resign"):
                    resign_game(gid, user["id"])
                    st.session_state.game_over = True
                    st.rerun()

        # Move history
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:.75rem;color:#8a7a6a;margin-bottom:.5rem;">MOVE HISTORY</div>', unsafe_allow_html=True)
        history = st.session_state.move_history
        if history:
            mhtml = ""
            for i in range(0,min(len(history),20),2):
                mhtml += f'<span style="color:#5a4a3a;font-size:.72rem;">{i//2+1}.</span> '
                mhtml += f'<span class="move-pill">{history[i]}</span> '
                if i+1 < len(history):
                    mhtml += f'<span class="move-pill" style="opacity:.7;">{history[i+1]}</span> '
            st.markdown(mhtml, unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#4a3a2a;font-size:.8rem;">No moves yet…</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Eval bar
        if not board.is_game_over():
            ev = evaluate_board(board)
            cl = max(-500,min(500,ev))
            pct = int((cl+500)/10)
            lbl = f"+{ev/100:.1f}" if ev>0 else f"{ev/100:.1f}"
            st.markdown(f"""
            <div class="card">
              <div style="font-size:.72rem;color:#8a7a6a;margin-bottom:.4rem;">EVALUATION</div>
              <div style="display:flex;align-items:center;gap:.4rem;">
                <span style="font-size:.7rem;color:#7a6a5a;">♚</span>
                <div style="flex:1;background:#2a1a10;border-radius:3px;height:10px;">
                  <div style="width:{pct}%;height:100%;background:linear-gradient(90deg,#c9a84c,#f5f0e8);border-radius:3px;"></div>
                </div>
                <span style="font-size:.7rem;color:#7a6a5a;">♔</span>
              </div>
              <div style="text-align:center;font-size:.78rem;color:#c9a84c;margin-top:.2rem;">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

        # Chat
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:.75rem;color:#8a7a6a;margin-bottom:.5rem;">💬 GAME CHAT</div>', unsafe_allow_html=True)
        chat_msgs = get_chat(gid)
        chat_html = ""
        for msg in chat_msgs[-12:]:
            is_me = msg["username"] == user["username"]
            cls = "chat-me" if is_me else "chat-other"
            chat_html += f'<div class="chat-msg {cls}"><strong style="color:{"#c9a84c" if is_me else "#60a5fa"};font-size:.72rem;">{msg["username"]}</strong><br>{msg["message"]}</div>'
        st.markdown(chat_html or '<div style="color:#4a3a2a;font-size:.78rem;">No messages yet…</div>', unsafe_allow_html=True)
        chat_in = st.text_input("Message", key="chat_field", label_visibility="collapsed", placeholder="Type a message…")
        if st.button("Send 💬"):
            if chat_in.strip():
                send_chat(gid, user["id"], chat_in.strip())
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# ─── LOCAL / AI GAME ──────────────────────────────────────────────────────────
board = st.session_state.board
mode  = st.session_state.game_mode

# No-op, clicks handled inline with component render

# AI move
if (not st.session_state.game_over and mode not in ("two_player","online")
        and board.turn != st.session_state.player_color
        and st.session_state.ai and not st.session_state.promotion_pending):
    with st.spinner("🤖 AI thinking…"):
        ai_mv = st.session_state.ai.get_move(board)
    if ai_mv: do_move(board, ai_mv)
    if board.is_game_over(): st.session_state.game_over = True
    st.rerun()

col_board, col_info = st.columns([3,2], gap="large")

with col_board:
    info2 = MODE_INFO[mode]
    st.markdown(f'<span class="{info2["badge"]} badge">{info2["label"]} — Elo {info2["elo"]}</span>', unsafe_allow_html=True)
    st.markdown("")
    stat = status_text(board, mode, st.session_state.player_color)
    is_check = board.is_check()
    st.markdown(f'<div class="{"check-alert" if is_check else "status-bar"}">{stat}</div>', unsafe_allow_html=True)

    if st.session_state.promotion_pending:
        pc1,pc2,pc3,pc4 = st.columns(4)
        promo_p = [(chess.QUEEN,"♕","Queen"),(chess.ROOK,"♖","Rook"),(chess.BISHOP,"♗","Bishop"),(chess.KNIGHT,"♘","Knight")]
        for i,(pt,sym,nm) in enumerate(promo_p):
            with [pc1,pc2,pc3,pc4][i]:
                if st.button(f"{sym}\n{nm}", key=f"lp_{pt}"):
                    pend = st.session_state.promotion_pending
                    mv = chess.Move(pend.from_square, pend.to_square, promotion=pt)
                    do_move(board, mv)
                    st.session_state.promotion_pending = None
                    if board.is_game_over(): st.session_state.game_over = True
                    st.rerun()

    flip = st.session_state.flip_board or (mode not in ("two_player","online") and st.session_state.player_color==chess.BLACK)
    clicked_sq = chessboard_component(html=render_board_html(board, flip=flip), key="local_board", height=510)
    
    clicked = get_clicked_square(clicked_sq)
    if clicked is not None and not st.session_state.game_over:
        if not st.session_state.promotion_pending:
            is_my = (mode=="two_player" or board.turn==st.session_state.player_color)
            sel = st.session_state.selected_square
            if is_my:
                if sel is None:
                    p = board.piece_at(clicked)
                    if p and p.color==board.turn:
                        st.session_state.selected_square = clicked
                else:
                    dests = get_legal_dests(board, sel)
                    if clicked in dests:
                        mv = chess.Move(sel, clicked)
                        if needs_promotion(board, mv):
                            st.session_state.promotion_pending = mv
                        else:
                            legal = [m for m in board.legal_moves if m.from_square==sel and m.to_square==clicked]
                            if legal: do_move(board, legal[0])
                        st.session_state.selected_square = None
                        if board.is_game_over(): st.session_state.game_over = True
                    elif board.piece_at(clicked) and board.piece_at(clicked).color==board.turn:
                        st.session_state.selected_square = clicked
                    else:
                        st.session_state.selected_square = None
        st.rerun()

    if st.session_state.game_over:
        res = board.result()
        msg = (f"🏆 {'White' if '1-0' in res else 'Black'} wins!" if res in ("1-0","0-1") else "½-½ Draw!")
        st.markdown(f'<div class="winner-box"><div style="font-size:2rem;">♛</div><div style="color:#c9a84c;font-size:1.2rem;font-weight:700;">{msg}</div></div>', unsafe_allow_html=True)

with col_info:
    if not board.is_game_over():
        ev = evaluate_board(board)
        cl = max(-500,min(500,ev))
        pct = int((cl+500)/10)
        lbl = f"+{ev/100:.1f}" if ev>0 else f"{ev/100:.1f}"
        st.markdown(f"""
        <div class="card">
          <div style="font-size:.72rem;color:#8a7a6a;margin-bottom:.4rem;">POSITION EVALUATION</div>
          <div style="display:flex;align-items:center;gap:.5rem;">
            <span style="font-size:.72rem;color:#7a6a5a;">♚</span>
            <div style="flex:1;background:#2a1a10;border-radius:3px;height:10px;">
              <div style="width:{pct}%;height:100%;background:linear-gradient(90deg,#c9a84c,#f5f0e8);border-radius:3px;"></div>
            </div>
            <span style="font-size:.72rem;color:#7a6a5a;">♔</span>
          </div>
          <div style="text-align:center;font-size:.8rem;color:#c9a84c;margin-top:.3rem;">{lbl}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:.75rem;color:#8a7a6a;margin-bottom:.5rem;">MOVE HISTORY</div>', unsafe_allow_html=True)
    history = st.session_state.move_history
    if history:
        mhtml = ""
        for i in range(0,min(len(history),20),2):
            mhtml += f'<span style="color:#5a4a3a;font-size:.72rem;">{i//2+1}.</span> '
            mhtml += f'<span class="move-pill">{history[i]}</span> '
            if i+1<len(history):
                mhtml += f'<span class="move-pill" style="opacity:.7;">{history[i+1]}</span> '
        st.markdown(mhtml, unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#4a3a2a;font-size:.8rem;">No moves yet…</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
      <div style="font-size:.75rem;color:#8a7a6a;margin-bottom:.4rem;">GAME STATS</div>
      <div class="stat-row"><span>Total moves</span><span class="stat-val">{len(history)}</span></div>
      <div class="stat-row"><span>Halfmove clock</span><span class="stat-val">{board.halfmove_clock}</span></div>
      <div class="stat-row" style="border:none;"><span>Full moves</span><span class="stat-val">{board.fullmove_number}</span></div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📖 How to play"):
        st.markdown("""
        <div style="font-size:.8rem;color:#c8b89a;line-height:1.8;">
        <strong style="color:#c9a84c;">🖱 Click to move:</strong> click piece → click destination<br>
        <strong style="color:#c9a84c;">🌐 Online:</strong> login → Create or Join a game<br>
        <strong style="color:#c9a84c;">🏆 Elo:</strong> ratings update after every online game<br>
        <strong style="color:#c9a84c;">💬 Chat:</strong> message opponent during online games<br>
        <strong style="color:#c9a84c;">🤝 Draw:</strong> offer draw; opponent must accept<br>
        <strong style="color:#c9a84c;">🏳 Resign:</strong> concede the game to opponent
        </div>
        """, unsafe_allow_html=True)
