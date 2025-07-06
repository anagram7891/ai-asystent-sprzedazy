import streamlit as st
from openai import OpenAI
import os
import tempfile

# 🔐 Ustawienie klucza API z Render (Environment Variables)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

st.title("🎙️ AI Asystent Sprzedaży Energii")
st.write("Nagraj rozmowę lub wgraj plik audio. Asystent stworzy transkrypcję i zaproponuje pytania oraz działania.")

audio_file = st.file_uploader("📤 Wgraj plik audio (MP3/WAV)", type=["mp3", "wav"])

if audio_file is not None:
    # Zapisz plik tymczasowo
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_file.read())
        tmp_file_path = tmp_file.name

    with st.spinner("🔍 Przetwarzam nagranie..."):
        with open(tmp_file_path, "rb") as audio:
            transcript_response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio
            )
        transcript = transcript_response.text

        # Prompt dla ChatGPT
        prompt = f"""Jesteś AI-asystentem handlowca. Analizujesz rozmowę z klientem.
Na podstawie poniższej rozmowy:
- Jakie są potrzeby klienta?
- Jakie pytania warto zadać?
- Jakie działania follow-up zaproponować?

Rozmowa:
{transcript}
"""

        chat_response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        suggestions = chat_response.choices[0].message.content

    # Wyświetl wyniki
    st.subheader("📝 Transkrypcja rozmowy")
    st.write(transcript)

    st.subheader("💡 Sugestie AI")
    st.write(suggestions)
