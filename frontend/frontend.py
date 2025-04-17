import streamlit as st
import requests

# SANITY CHECK – you should see this immediately after saving
st.write("👋 Hello! Streamlit is running.")

# Your real app
API_URL = "http://10.31.11.49:8000/recommend"

st.title("SHL Assessment Recommender")

query = st.text_area("Enter your query or job‑description URL")
if st.button("Recommend"):
    # Decide whether it's a URL or plain text
    payload = (
        {"jd_url": query}
        if query.strip().lower().startswith("http")
        else {"query_text": query}
    )
    resp = requests.post(API_URL, json=payload)
    if resp.status_code == 200:
        data = resp.json()
        for item in data:
            st.markdown(
                f"- **[{item['name']}]({item['url']})**   \n"
                f"  • Remote: {item['remoteTesting']} • Adaptive: {item['adaptiveIRT']}   \n"
                f"  • Duration: {item['duration']} • Type: {item['testType']}"
            )
    else:
        st.error(f"Error {resp.status_code}: {resp.text}")
