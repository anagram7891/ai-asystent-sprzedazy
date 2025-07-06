import streamlit as st
import openai
import os
import tempfile

openai.api_key = os.environ.get("OPENAI_API_KEY")

st.title("🎙️ AI Asystent Sprzedaży Energii")
st.write("Nagraj rozmowę lub wgraj plik audio. Asystent stworzy pytania, coaching i follow-up.")

audio_file = st.file_uploader("📤 Wgraj plik audio (MP3/WAV)", type=["mp3", "wav"])

if audio_file is not None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(audio_file.read())
        tmp_file_path = tmp_file.name

    with st.spinner("🔍 Przetwarzam nagranie..."):
        with open(tmp_file_path, "rb") as audio:
            transcript_response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio
            )
        transcript = transcript_response.text

        prompt = f"""
Na podstawie poniższej rozmowy:

1. Wygeneruj 2–3 trafne pytania, które handlowiec powinien zadać klientowi (max 300 znaków każde).
2. Daj 1–2 wskazówki coachingowe dla handlowca (np. "mów wolniej", "pogłęb temat").
3. Zaproponuj działania follow-up.

Rozmowa:
{transcript}
"""

        completion = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )

        result = completion.choices[0].message.content

    # --- Wyświetlanie bez transkrypcji ---
    st.subheader("💬 Sugestie pytań do klienta")
    st.markdown(result.split("2.")[0].strip())

    st.subheader("🎯 Coaching AI dla handlowca")
    st.markdown(result.split("2.")[1].split("3.")[0].strip())

    st.subheader("📩 Propozycje follow-up")
    st.markdown(result.split("3.")[1].strip())

