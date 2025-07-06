import streamlit as st
import openai
from streamlit_audio_recorder import audio_recorder
import base64
import tempfile

# 🔐 Ustaw swój klucz API (upewnij się, że masz go w Render jako OPENAI_API_KEY)
openai.api_key = st.secrets.get("OPENAI_API_KEY")

st.title("🎙️ AI Asystent Sprzedaży B2B")
st.write("Nagraj wiadomość – AI zasugeruje pytania, coaching i follow-up.")

# 🔴 Nagrywanie dźwięku w przeglądarce
wav_audio_data = audio_recorder(pause_threshold=3.0, sample_rate=16000)

if wav_audio_data:
    st.audio(wav_audio_data, format="audio/wav")
    
    # Zapis tymczasowy
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(wav_audio_data)
        audio_path = tmp_file.name

    with st.spinner("⏳ Przesyłam do AI..."):
        with open(audio_path, "rb") as audio_file:
            transcript_response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
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

        completion = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        result = completion.choices[0].message.content

    st.success("✅ Gotowe!")
    st.markdown("### 💡 Sugestie AI")
    st.markdown(result)
else:
    st.info("🎤 Kliknij ikonę mikrofonu, aby rozpocząć nagrywanie.")
