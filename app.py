import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import openai
import av
import queue
import tempfile
import os
import time

# 🔐 Klucz API (Render odczyta z Environment Variables)
openai.api_key = os.getenv("OPENAI_API_KEY")

st.title("🎙️ AI Asystent Sprzedaży B2B")
st.markdown("Nagraj rozmowę – otrzymasz 2–3 pytania, coaching i follow-up od AI.")

# 🎤 Bufor do nagrań audio
audio_buffer = queue.Queue()

# 🎛️ Przechwytywanie audio
class AudioProcessor:
    def __init__(self):
        self.recording = False
        self.audio_frames = []

    def recv(self, frame: av.AudioFrame):
        if self.recording:
            self.audio_frames.append(frame)
        return frame

processor = AudioProcessor()

# 🔴 WebRTC – nagrywanie online
webrtc_ctx = webrtc_streamer(
    key="audio",
    mode=WebRtcMode.SENDONLY,
    audio_frame_callback=processor.recv,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True,
)

# ⏺️ Start i stop nagrywania
if webrtc_ctx.state.playing:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏺️ Start nagrywania"):
            processor.recording = True
            processor.audio_frames = []
            st.session_state["start_time"] = time.time()
    with col2:
        if st.button("⏹️ Stop i analizuj"):
            processor.recording = False

            if processor.audio_frames:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    # zapis audio do pliku
                    container = av.open(f.name, mode='w', format='wav')
                    stream = container.add_stream('pcm_s16le', rate=processor.audio_frames[0].sample_rate)
                    stream.channels = processor.audio_frames[0].layout.channels

                    for frame in processor.audio_frames:
                        frame.pts = None
                        container.mux(stream.encode(frame))
                    container.mux(stream.encode())
                    container.close()
                    audio_path = f.name

                with st.spinner("🧠 Przesyłanie do AI..."):
                    with open(audio_path, "rb") as audio_file:
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
            else:
                st.warning("Brak nagrania. Upewnij się, że włączyłeś mikrofon.")
