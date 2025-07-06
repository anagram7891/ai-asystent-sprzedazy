import streamlit as st
import openai
import os
import tempfile

openai.api_key = os.getenv("OPENAI_API_KEY")

st.title("🎙️ AI Asystent Sprzedaży Energii B2B")
st.write("Wgraj nagranie rozmowy z klientem. Asystent podpowie pytania, coaching i follow-up.")

# Upload audio
audio_file = st.file_uploader("📤 Wgraj nagranie rozmowy (MP3 lub WAV)", type=["mp3", "wav"])

if audio_file is not None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(audio_file.read())
        audio_path = tmp_file.name

    with st.spinner("⏳ Analiza rozmowy..."):
        # Transkrypcja
        with open(audio_path, "rb") as f:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=f
            ).text

        # Zapytanie do GPT
        prompt = f"""
Jesteś AI-asystentem handlowca. Analizujesz rozmowę z klientem.

Na podstawie rozmowy:
1. Podaj 2–3 pytania, które warto zadać klientowi.
2. Zasugeruj 1 konkretną zmianę w zachowaniu handlowca (coaching).
3. Zasugeruj działanie follow-up.

Rozmowa:
{transcript}
"""

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        st.success("✅ Gotowe!")
        st.markdown("### 💡 Pytania do klienta i coaching:")
        st.markdown(response.choices[0].message.content)
