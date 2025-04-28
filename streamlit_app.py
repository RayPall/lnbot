# streamlit_app.py
import requests, streamlit as st

WEBHOOK = "https://hook.eu2.make.com/syxvccar1q9bkkcilcjcni7437v9yqd4"  # ← Make webhook

st.set_page_config(page_title="LinkedIn bot", page_icon="📝")
st.title("LinkedIn bot 📝")

with st.form("form"):
    topic = st.text_area("Jaké má být téma příspěvku?")
    persona = st.radio(
        "Čím stylem má být příspěvek napsán?",
        ("Daniel Šturm", "Martin Cígler", "Marek Steiger",
         "Kristína Pastierik", "Lucie Jahnová"))
    email = st.text_input("Na jaký e-mail poslat draft?")
    ok = st.form_submit_button("Odeslat")

if ok:
    # ⬇︎ JSON ve formátu, který Make očekává
    data = {
        "personName": persona,       # <jméno persony>
        "postContent": topic,        # <obsah příspěvku>
        "responseMail": email        # <e-mail pro zaslání draftu>
    }

    with st.spinner("Generuji pomocí ChatGPT…"):
        res = requests.post(WEBHOOK, json=data, timeout=120)

    if not res.ok:
        st.error(f"Chyba {res.status_code}: {res.text}")
        st.stop()

    # bezpečné načtení odpovědi (ať je to JSON objekt nebo prostý text)
    try:
        payload = res.json()
        post = payload["post"] if isinstance(payload, dict) else str(payload)
    except ValueError:
        post = res.text

    st.success("Hotovo! Zde je vygenerovaný příspěvek:")
    st.code(post, language="markdown")
