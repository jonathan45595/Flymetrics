import os
import io
import wave
import av
import speech_recognition as sr
import math

def webm_to_wav_chunks(input_path, chunk_duration_sec=20):
    container = av.open(input_path)
    audio_stream = next(s for s in container.streams if s.type == 'audio')
    
    resampler = av.AudioResampler(format='s16', layout='mono', rate=16000)
    
    raw_frames = bytearray()
    for frame in container.decode(audio_stream):
        for resampled_frame in resampler.resample(frame):
            raw_frames.extend(bytes(resampled_frame.planes[0]))
            
    bytes_per_sec = 16000 * 2 # 16kHz, 16-bit (2 bytes per sample) mono
    total_sec = len(raw_frames) / bytes_per_sec
    
    chunk_size = chunk_duration_sec * bytes_per_sec
    chunks = []
    
    for i in range(0, len(raw_frames), chunk_size):
        chunk_raw = raw_frames[i : i + chunk_size]
        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(chunk_raw)
        wav_io.seek(0)
        chunks.append(wav_io)
        
    return chunks, total_sec

folder = r'C:\Users\migue\.gemini\antigravity-ide\brain\a8f93277-30bd-4e9c-bcc8-ac9e5808eb07\.user_uploaded'
files = [f for f in os.listdir(folder) if f.startswith('uploaded_media')]
files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)))

r = sr.Recognizer()

# Process all 5 recent audios
recent_files = files[-5:]
print(f"Processing {len(recent_files)} audio files:")
for idx, f in enumerate(recent_files, 1):
    path = os.path.join(folder, f)
    print(f"\n================ AUDIO #{idx}: {f} (size: {os.path.getsize(path)} bytes) ================")
    try:
        chunks, total_sec = webm_to_wav_chunks(path, 15)
        print(f"Duración total: ~{total_sec:.1f} segundos ({len(chunks)} partes)")
        full_text = []
        for c_idx, chunk_io in enumerate(chunks):
            with sr.AudioFile(chunk_io) as source:
                audio_data = r.record(source)
                try:
                    text_chunk = r.recognize_google(audio_data, language='es-CO')
                    full_text.append(text_chunk)
                except sr.UnknownValueError:
                    pass
                except Exception as ex:
                    print(f"  [Chunk {c_idx+1} error: {ex}]")
        print("TRANSCRIPCIÓN COMPLETA:")
        print(" ".join(full_text) if full_text else "(No se detectó voz)")
    except Exception as e:
        print(f"Error procesando audio: {e}")
