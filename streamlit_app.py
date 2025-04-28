# ── streamlit_app.py ────────────────────────────────────────────────────────────
"""
Streamlit mini-apka, která:
1) zobrazí formulář (téma, persona, e-mail)
2) po odeslání pošle data přes webhook do Make
3) čeká max 90 s, než Make pošle výsledek na náš /callback
4) po přijetí zobrazí vygenerovaný příspěvek
"""
import os, uuid, time, sqlite3, requests, streamlit as st

# --- nastavení -----------------------------------------------------------------
MAKE_WEBHOOK_URL = os.getenv("https://hook.eu2.make.com/syxvccar1q9bkkcilcjcni7437v9yqd4")           # = https://hook.eu2.make.com/...
CALLBACK_DB      = "posts.db"                              # SQLite úložiště

# --- init DB (pokud ještě neexistuje) ------------------------------------------
con = sqlite3.connect(CALLBACK_DB)
con.execute("""CREATE TABLE IF NOT EXISTS posts(
                 correlation_id TEXT PRIMARY KEY,
                 email          TEXT,
                 content        TEXT,
                 received_at    TEXT)""")
con.commit()

# --- pomocné funkce ------------------------------------------------------------
def save_placeholder(cid: str, email: str):
    con.execute("INSERT OR IGNORE INTO posts(correlation_id,email,content,received_at) "
                "VALUES(?,?,NULL,NULL)", (cid, email))
    con.commit()

def fetch_post(cid: str):
    row = con.execute("SELECT content FROM posts WHERE correlation_id=?", (cid,)).fetchone()
    return row[0] if row and row[0] else None

def send_to_make(topic: str, persona: str, email: str, cid: str):
    payload = {
        "topic": topic,
        "persona": persona,
        "email": email,
        "correlation_id": cid,      # Make vrátí toto ID zpět v callbacku
    }
    requests.post(MAKE_WEBHOOK_URL, json=payload, timeout=10)

# ------------------------------------------------------------------------------
st.set_page_config(page_title="LinkedIn bot", page_icon="📝")
st.title("LinkedIn bot 📝")

with st.form("linkedin_form"):
    topic   = st.text_area("Jaké má být téma příspěvku?", max_chars=500)
    persona = st.radio("Čím stylem má být příspěvek napsán?",
                       ("Daniel Šturm", "Martin Cígler", "Marek Steiger",
                        "Kristína Pastierik", "Lucie Jahnová"))
    email   = st.text_input("Na jaký e-mail poslat draft příspěvku?")
    submitted = st.form_submit_button("Odeslat")

if submitted:
    # vygenerujeme korelační ID a placeholder v DB
    cid = str(uuid.uuid4())
    save_placeholder(cid, email)

    # odesíláme do Make
    try:
        send_to_make(topic, persona, email, cid)
    except Exception as e:
        st.error(f"Nepodařilo se kontaktovat Make webhook → {e}")
        st.stop()

    # čekáme, než Make vrátí výsledek
    with st.spinner("Generuji příspěvek pomocí ChatGPT…"):
        start = time.time()
        post = None
        while (time.time() - start) < 90:      # čekáme max 90 s
            time.sleep(3)
            post = fetch_post(cid)
            if post:
                break

    if post:
        st.success("Hotovo! 💪 Zde je vygenerovaný příspěvek:")
        st.code(post, language="markdown")
    else:
        st.warning("Generování trvá déle než obvyklých 90 s. "
                   "Příspěvek ti dorazí e-mailem hned, jak bude hotov.")

