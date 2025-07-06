# 🎙️ AI Asystent Sprzedaży B2B

Aplikacja webowa oparta na Streamlit + OpenAI, umożliwiająca nagrywanie rozmów z klientami w przeglądarce i generowanie:

- pytań pod klienta,
- wskazówek coachingowych,
- działań follow-up.

## 🔧 Jak działa

1. Aplikacja nagrywa audio w przeglądarce.
2. Wysyła nagranie do OpenAI Whisper (`whisper-1`) do transkrypcji.
3. GPT-4 analizuje rozmowę i generuje sugestie.

## 🚀 Uruchomienie lokalne

### 1. Instalacja zależności

```bash
pip install -r requirements.txt
