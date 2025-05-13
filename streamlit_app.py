# streamlit_app.py
import requests, streamlit as st

# ⬇︎ nový Make webhook
WEBHOOK = "https://hook.eu2.make.com/6m46qtelfmarmwpq1jqgomm403eg5xkw"

st.set_page_config(page_title="LinkedIn bot", page_icon="📝")
st.title("LinkedIn bot 📝")

# ----------------------- formulář ---------------------------------------------
with st.form("form"):
    topic = st.text_area("Jaké má být téma příspěvku?")
    persona = st.radio(
        "Čím stylem má být příspěvek napsán?",
        ("Daniel Šturm", "Martin Cígler", "Marek Steiger",
         "Kristína Pastierik", "Lucie Jahnová"))
    email = st.text_input("Na jaký e-mail poslat draft?")
    ok = st.form_submit_button("Odeslat")

# ----------------------- odeslání do Make --------------------------------------
if ok:
    data = {
        "personName": persona,
        "postContent": topic,
        "responseMail": email
    }

    with st.spinner("Generuji pomocí ChatGPT…"):
        res = requests.post(WEBHOOK, json=data, timeout=120)

    if not res.ok:
        st.error(f"Chyba {res.status_code}: {res.text}")
        st.stop()

    try:
        payload = res.json()
        post = payload["post"] if isinstance(payload, dict) else str(payload)
    except ValueError:
        post = res.text

    # ---------- zobraz výsledný post v podobě čitelného textu ------------------
    post_md = post.strip().replace("\n", "  \n")   # 2 mezery + \n = hard‑break v MD
    st.success("Hotovo! Zde je vygenerovaný příspěvek:")
    st.markdown(post_md)
