import streamlit as st
import openai
import os
import tempfile
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import av
import queue
import time

# Ustawienie klucza OpenAI
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Interfejs
st.title("🎙️ AI Asystent Sprzedaży B2B")
st.write("Nagraj rozmowę w przeglądarce. Asystent stworzy pytania, coaching i follow-up.")

# Bufor audio
audio_buffer = queue.Queue()

# Konfiguracja WebRTC
client_settings = ClientSettings(
    media_stream_constraints={"audio": True, "video": False},
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
)

class AudioProcessor:
    def __init__(self):
        self.recording = False
        self.audio_frames = []

    def recv(self, frame: av.AudioFrame):
        if self.recording:
            self.audio_frames.append(frame)
        return frame

processor = AudioProcessor()

# Streamlit WebRTC
webrtc_ctx = webrtc_streamer(
    key="audio",
    mode=WebRtcMode.SENDONLY,
    in_audio_frame_callback=processor.recv,
    client_settings=client_settings,
    media_stream_constraints={"audio": True, "video": False}
)

if webrtc_ctx.state.playing:
    if st.button("⏺️ Rozpocznij nagrywanie"):
        processor.recording = True
        processor.audio_frames = []
        st.session_state["recording_started"] = time.time()
        st.info("Nagrywanie rozpoczęte...")

    if st.button("⏹️ Zatrzymaj nagrywanie i prześlij"):
        processor.recording = False

        if processor.audio_frames:
            # Zapis audio do pliku tymczasowego .wav
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                container = av.open(f.name, mode='w', format='wav')
                stream = container.add_stream('pcm_s16le', rate=processor.audio_frames[0].sample_rate)
                stream.channels = processor.audio_frames[0].layout.channels

                for frame in processor.audio_frames:
                    frame.pts = None
                    container.mux(stream.encode(frame))
                container.mux(stream.encode())
                container.close()
                audio_path = f.name

            # Transkrypcja
            with st.spinner("⏳ Przesyłanie audio do transkrypcji..."):
                with open(audio_path, "rb") as audio_file:
                    transcript_response = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                    transcript = transcript_response["text"]

            # Prompt do GPT-4
            with st.spinner("🧠 Generuję sugestie AI..."):
                prompt = f"""
Jesteś AI-asystentem handlowca. Analizujesz rozmowę z klientem.

Na podstawie rozmowy:
1. Podaj 2–3 pytania, które warto zadać klientowi.
2. Zasugeruj 1 konkretną zmianę w zachowaniu handlowca (coaching).
3. Zasugeruj działanie follow-up.

Rozmowa:
{transcript}
"""

                completion = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )
                result = completion.choices[0].message.content

            # Wyświetlenie wyniku
            st.success("Gotowe!")
            st.markdown("### 💡 Sugestie AI")
            st.write(result)
        else:
            st.warning("Brak danych audio do przetworzenia.")
