import os
import io
import wave
import av
import speech_recognition as sr

def webm_to_wav(input_path):
    container = av.open(input_path)
    audio_stream = next(s for s in container.streams if s.type == 'audio')
    
    # Resample to 16kHz mono 16-bit PCM
    resampler = av.AudioResampler(format='s16', layout='mono', rate=16000)
    
    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        
        for frame in container.decode(audio_stream):
            for resampled_frame in resampler.resample(frame):
                wav_file.writeframes(bytes(resampled_frame.planes[0]))
                
    wav_io.seek(0)
    return wav_io

folder = r'C:\Users\migue\.gemini\antigravity-ide\brain\a8f93277-30bd-4e9c-bcc8-ac9e5808eb07\.user_uploaded'
files = [f for f in os.listdir(folder) if f.startswith('uploaded_media')]
files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)))

r = sr.Recognizer()

# Focus on the most recent 6 audio files
for f in files[-6:]:
    path = os.path.join(folder, f)
    print(f"\n================ TRANSCRIBING: {f} (size: {os.path.getsize(path)} bytes) ================")
    try:
        wav_io = webm_to_wav(path)
        with sr.AudioFile(wav_io) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language='es-CO')
            print(f"TRANSCRIPCIÓN:\n\"{text}\"")
    except Exception as e:
        print(f"Error: {e}")
