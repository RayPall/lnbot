# streamlit_app.py
# ------------------------------------------------------------------------------
# Aplikace:
#   1) Generování LinkedIn postu (s optional URL → text se pošle do Make)
#   2) Přidání nové persony (okamžitě se objeví v seznamu)
# ------------------------------------------------------------------------------
# ZÁVISLOSTI: streamlit, requests, beautifulsoup4
#   pip install -r requirements.txt   (přidej beautifulsoup4)
# ------------------------------------------------------------------------------

import json, re, requests, streamlit as st
from bs4 import BeautifulSoup

# --- Make webhooky ------------------------------------------------------------
WEBHOOK_POST    = "https://hook.eu2.make.com/6m46qtelfmarmwpq1jqgomm403eg5xkw"
WEBHOOK_PERSONA = "https://hook.eu2.make.com/9yo8y77db7i6do272joo7ybfoue1qcoc"   # ← doplň

# --- Výchozí persony ----------------------------------------------------------
DEFAULT_PERSONAS = [
    "Daniel Šturm", "Martin Cígler", "Marek Steiger",
    "Kristína Pastierik", "Lucie Jahnová"
]

# --- Session state ------------------------------------------------------------
if "person_list" not in st.session_state:
    st.session_state.person_list = DEFAULT_PERSONAS.copy()
if "show_persona_form" not in st.session_state:
    st.session_state.show_persona_form = False

# ------------------------------------------------------------------------------
st.set_page_config(page_title="LinkedIn bot", page_icon="📝")
st.title("LinkedIn bot 📝")

# ------------------------------------------------------------------------------ 
# Pomocná funkce: vytáhnout text z landing page
# ------------------------------------------------------------------------------
def extract_page_text(url: str, max_chars: int = 2000) -> str:
    r = requests.get(
        url,
        timeout=10,
        headers={"User-Agent": "Mozilla/5.0 (compatible; LinkedIn-bot/1.0)"}
    )
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    text = re.sub(r"\s+\n", "\n", text)          # odmazat konce řádků s mezerami
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text[:max_chars]

# ============================= 1) FORMULÁŘ POSTU ==============================
with st.form("post_form"):
    topic = st.text_area("Jaké má být téma příspěvku?")
    landing_url = st.text_input("URL stránky (volitelně)")
    persona = st.radio(
        "Čím stylem má být příspěvek napsán?",
        st.session_state.person_list
    )
    email = st.text_input("Na jaký e‑mail poslat draft?")
    submitted_post = st.form_submit_button("Odeslat")

# ---- Odeslat na Make ---------------------------------------------------------
if submitted_post:
    page_excerpt = ""
    if landing_url.strip():
        try:
            page_excerpt = extract_page_text(landing_url.strip())
        except Exception as e:
            st.warning(f"Nepodařilo se načíst stránku: {e}")

    post_payload = {
        "personName":   persona,
        "postContent":  topic,
        "responseMail": email,
        "sourcePage":   page_excerpt          # nový klíč
    }

    with st.spinner("Generuji pomocí ChatGPT…"):
        try:
            res = requests.post(WEBHOOK_POST, json=post_payload, timeout=120)
            res.raise_for_status()
        except Exception as e:
            st.error(f"Chyba při komunikaci s Make: {e}")
            st.stop()

    try:
        post_text = res.json().get("post", "")
    except (ValueError, AttributeError):
        post_text = res.text                     # fallback

    post_md = post_text.strip().replace("\n", "  \n")
    st.success("Hotovo! Zde je vygenerovaný příspěvek:")
    st.markdown(post_md)

# ============================ 2) PŘIDAT PERSONU ===============================
st.markdown("---")
st.header("➕ Přidat novou personu")

if not st.session_state.show_persona_form:
    if st.button("Přidat personu"):
        st.session_state.show_persona_form = True
        st.experimental_rerun()

else:
    with st.form("persona_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            name  = st.text_input("Jméno*")
            role  = st.text_input("Role / pozice*")
            tone  = st.text_area("Tone of Voice*")
        with col2:
            style   = st.text_area("Styl psaní*")
            lang    = st.selectbox("Jazyk*", ("Čeština", "Slovenština", "Angličtina", "Jiný"))
            sample  = st.text_area("Ukázkový příspěvek*")

        submitted_persona = st.form_submit_button("Uložit personu")

    if submitted_persona:
        if not name.strip():
            st.error("Jméno je povinné.")
            st.stop()

        persona_payload = {
            "name":     name.strip(),
            "role":     role.strip(),
            "tone":     tone.strip(),
            "style":    style.strip(),
            "language": lang,
            "sample":   sample.strip()
        }

        with st.spinner("Ukládám personu…"):
            try:
                rp = requests.post(WEBHOOK_PERSONA, json=persona_payload, timeout=30)
                rp.raise_for_status()
            except Exception as e:
                st.error(f"Chyba při ukládání: {e}")
                st.stop()

        st.session_state.person_list.append(name.strip())
        st.session_state.show_persona_form = False
        st.success("Persona uložena ✔️")
        st.experimental_rerun()
