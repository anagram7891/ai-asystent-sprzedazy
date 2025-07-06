import streamlit as st
from st_audiorec import st_audiorec
import openai
import os
import tempfile

openai.api_key = os.getenv("OPENAI_API_KEY")

st.title("🎙️ AI Asystent Sprzedaży B2B")
st.write("Nagraj rozmowę z klientem – otrzymasz 2–3 pytania, coaching i follow-up.")

wav_audio_data = st_audiorec()

if wav_audio_data is not None:
    st.audio(wav_audio_data, format='audio/wav')

    with st.spinner("🧠 Przesyłanie do AI..."):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(wav_audio_data)
            f_path = f.name

        with open(f_path, "rb") as audio_file:
            transcript_response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            transcript = transcript_response.text

        prompt = f"""
Jesteś AI-asystentem handlowca. Analizujesz rozmowę z klientem.

Na podstawie rozmowy:
1. Podaj 2–3 pytania, które warto teraz zadać klientowi.
2. Zasugeruj 1 konkretną poprawę w zachowaniu handlowca (coaching).
3. Zaproponuj działanie follow-up.

Rozmowa:
{transcript}
"""

        completion = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        result = completion.choices[0].message.content

        st.success("✅ Gotowe!")
        st.markdown("### 💡 Sugestie AI:")
        st.write(result)
