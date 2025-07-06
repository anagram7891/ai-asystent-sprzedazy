import streamlit as st
import openai
import os
import tempfile

# Ustawienie klucza API OpenAI (wprowadzisz go później w sekcji Secrets)
import os
openai.api_key = os.environ.get("OPENAI_API_KEY")

st.title("🎙️ AI Asystent Sprzedaży Energii")
st.write("Nagraj rozmowę lub wgraj plik audio. Asystent stworzy transkrypcję i zaproponuje pytania oraz działania.")

audio_file = st.file_uploader("Wgraj plik audio (MP3/WAV)", type=["mp3", "wav"])

if audio_file is not None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(audio_file.read())
        tmp_file_path = tmp_file.name

    with st.spinner("🔍 Przetwarzam nagranie..."):
        audio = open(tmp_file_path, "rb")
        transcript_response = openai.Audio.transcribe("whisper-1", audio)
        transcript = transcript_response["text"]

        prompt = f"""Jesteś AI-asystentem handlowca. Analizujesz rozmowę z klientem.
Na podstawie poniższej rozmowy:
- Jakie są potrzeby klienta?
- Jakie pytania warto zadać?
- Jakie działania follow-up zaproponować?

Rozmowa:
{transcript}
"""

        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        suggestions = completion["choices"][0]["message"]["content"]

    st.subheader("📝 Transkrypcja rozmowy")
    st.write(transcript)

    st.subheader("💡 Sugestie AI")
    st.write(suggestions)
