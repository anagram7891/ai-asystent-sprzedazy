import streamlit as st
import openai
import os
import tempfile
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import asyncio
import streamlit.components.v1 as components

openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="AI Asystent Sprzedaży", layout="centered")
st.title("🎙️ AI Asystent Sprzedaży Energii")

st.markdown("**Nagraj rozmowę. AI zaproponuje pytania, coaching i follow-up.**")

uploaded_file = st.file_uploader("📤 Wgraj plik audio (MP3/WAV)", type=["mp3", "wav"])

if uploaded_file:
    with st.spinner("🔎 Przesyłanie do OpenAI..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        with open(tmp_path, "rb") as audio_file:
            transcript_response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            transcript = transcript_response.text

        prompt = f"""
Jesteś AI-asystentem sprzedaży B2B w branży energii. 
Na podstawie rozmowy:

1. Podaj 2–3 pytania, które warto zadać klientowi.
2. Zasugeruj jedną zmianę w zachowaniu handlowca (coaching).
3. Zasugeruj działanie follow-up.

Rozmowa klienta:
{transcript}
"""

        completion = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        result = completion.choices[0].message.content

    st.success("✅ Gotowe! Zobacz sugestie poniżej:")
    st.markdown("### 💬 Pytania do klienta, coaching i follow-up:")
    st.write(result)
