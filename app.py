import streamlit as st
from streamlit_audio_recorder import audio_recorder
import openai
import os

st.title("🎙️ AI Asystent Sprzedaży Energii")
st.write("Nagraj rozmowę w przeglądarce. Asystent stworzy pytania, coaching i follow-up.")

openai.api_key = os.getenv("OPENAI_API_KEY")

audio_bytes = audio_recorder(pause_threshold=3.0, sample_rate=16000)

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    st.success("🎧 Nagranie gotowe! Przetwarzam...")

    with st.spinner("🔍 Przesyłam do OpenAI..."):
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp.flush()

            with open(tmp.name, "rb") as f:
                transcript_response = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=f
                )
                transcript = transcript_response.text

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
        result = response.choices[0].message.content

    st.markdown("## 💡 Sugestie AI")
    st.write(result)
