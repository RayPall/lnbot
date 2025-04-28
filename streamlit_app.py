# streamlit_app.py
import requests, streamlit as st

WEBHOOK = "https://hook.eu2.make.com/syxvccar1q9bkkcilcjcni7437v9yqd4"  # ⬅︎ tvůj Make webhook

st.title("LinkedIn bot 📝")

with st.form("form"):
    topic   = st.text_area("Jaké má být téma příspěvku?")
    persona = st.radio(
        "Čím stylem má být příspěvek napsán?",
        ("Daniel Šturm", "Martin Cígler", "Marek Steiger",
         "Kristína Pastierik", "Lucie Jahnová"))
    email   = st.text_input("Na jaký e-mail poslat draft?")
    ok = st.form_submit_button("Odeslat")

if ok:
    data = {"topic": topic, "persona": persona, "email": email}
    with st.spinner("Generuji pomocí ChatGPT…"):
        r = requests.post(WEBHOOK, json=data, timeout=120)
    if r.ok:
        post = r.json().get("post", "")
        st.success("Hotovo! Zde je vygenerovaný příspěvek:")
        st.code(post, language="markdown")
    else:
        st.error(f"Chyba {r.status_code}: {r.text}")
