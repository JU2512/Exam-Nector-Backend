from app.services.whisper_service import transcribe_audio

text = transcribe_audio("app/temp/sample.wav")
print("TRANSCRIPTION:")
print(text)
