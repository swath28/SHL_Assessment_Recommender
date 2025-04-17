import os
import streamlit as st
import requests

# --- CONFIG ---
st.set_page_config(page_title="SHL Assessment Recommender", layout="centered")
# Change this to your Render service URL + /recommend
API_URL = os.environ.get(
    "API_URL",
    "https://<your‑render‑service‑subdomain>.onrender.com/recommend"
)

# --- UI ---
st.title("SHL Assessment Recommender")
st.write("Enter a natural‑language query or a job‑description URL below, then hit **Recommend**.")

query = st.text_area("Your query or JD URL", height=120)

if st.button("Recommend"):
    if not query.strip():
        st.warning("Please enter a query or URL first.")
    else:
        payload = {}
        # detect if it's a URL
        if query.lower().startswith("http"):
            payload["jd_url"] = query.strip()
        else:
            payload["query_text"] = query.strip()

        # fire off
        with st.spinner("Finding the best SHL assessments…"):
            try:
                r = requests.post(API_URL, json=payload, timeout=20)
                r.raise_for_status()
                results = r.json()
            except requests.exceptions.Timeout:
                st.error("Request timed out. The server may be busy or unreachable.")
                st.stop()
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the recommendation API. Check your API_URL.")
                st.stop()
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.stop()

        # display
        if not results:
            st.info("No recommendations returned.")
        else:
            for item in results:
                st.markdown(f"### [{item['name']}]({item['url']})")
                cols = st.columns([1,1,1])
                cols[0].write(f"**Remote:** {item.get('remoteTesting') or 'N/A'}")
                cols[1].write(f"**Adaptive:** {item.get('adaptiveIRT') or 'N/A'}")
                cols[2].write(f"**Duration:** {item.get('duration') or 'N/A'}  •  **Type:** {item.get('testType') or 'N/A'}")
