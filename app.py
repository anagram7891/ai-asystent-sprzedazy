import streamlit as st
import openai
import os
import tempfile
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import av
import queue
import threading
import time

openai.api_key = os.getenv("OPENAI_API_KEY")

st.title("🎙️ AI Asystent Sprzedaży Energii")
st.write("Nagraj rozmowę w przeglądarce. Asystent stworzy pytania, coaching i follow-up.")

audio_buffer = queue.Queue()

# Konfiguracja klienta WebRTC
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

    if st.button("⏹️ Zatrzymaj nagrywanie i prześlij"):
        processor.recording = False

        if processor.audio_frames:
            # Zapis do pliku WAV
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                container = av.open(f.name, mode='w', format='wav')
                stream = container.add_stream('pcm_s16le', rate=processor.audio_frames[0].sample_rate)
                stream.channels = processor.audio_frames[0].layout.channels

                for frame in processor.audio_frames:
                    frame.pts = None  # ważne!
                    container.mux(stream.encode(frame))
                container.mux(stream.encode())
                container.close()
                audio_path = f.name

            with st.spinner("⏳ Przesyłam do AI..."):
                with open(audio_path, "rb") as audio_file:
                    transcript_response = openai.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                    transcript = transcript_response.text

                # Tworzenie promptu
                prompt = f"""
Jesteś AI-asystentem handlowca. Analizujesz rozmowę z klientem.

Na podstawie rozmowy:
- Podaj 2–3 pytania, które warto zadać klientowi.
- Zasugeruj 1 konkretną zmianę w zachowaniu handlowca (coaching).
- Zasugeruj działanie follow-up.

Rozmowa:
{transcript}
"""

                completion = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}]
                )
                result = completion.choices[0].message.content

            st.success("Gotowe!")
            st.markdown("### 💡 Sugestie AI")
            st.write(result)
        else:
            st.warning("Brak zarejestrowanych danych audio.")
