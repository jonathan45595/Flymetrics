import os
import io
import wave
import av
import speech_recognition as sr
import sys

sys.stdout.reconfigure(encoding='utf-8')

def webm_to_wav_chunks(input_path, chunk_duration_sec=12):
    container = av.open(input_path)
    audio_stream = next(s for s in container.streams if s.type == 'audio')
    
    resampler = av.AudioResampler(format='s16', layout='mono', rate=16000)
    
    raw_frames = bytearray()
    for frame in container.decode(audio_stream):
        for resampled_frame in resampler.resample(frame):
            raw_frames.extend(bytes(resampled_frame.planes[0]))
            
    bytes_per_sec = 16000 * 2 # 16kHz, 16-bit mono
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
print(f"Processing {len(recent_files)} audio files:", flush=True)

out_file = r'C:\Users\migue\OneDrive\Desktop\este es el verdadero - copia\flymetrics\scratch\transcripciones_resultado.txt'
with open(out_file, 'w', encoding='utf-8') as out:
    for idx, f in enumerate(recent_files, 1):
        path = os.path.join(folder, f)
        header = f"\n================ AUDIO #{idx}: {f} (size: {os.path.getsize(path)} bytes) ================"
        print(header, flush=True)
        out.write(header + '\n')
        try:
            chunks, total_sec = webm_to_wav_chunks(path, 12)
            dur_info = f"Duración total: ~{total_sec:.1f} segundos ({len(chunks)} partes)"
            print(dur_info, flush=True)
            out.write(dur_info + '\n')
            full_text = []
            for c_idx, chunk_io in enumerate(chunks):
                with sr.AudioFile(chunk_io) as source:
                    audio_data = r.record(source)
                    try:
                        text_chunk = r.recognize_google(audio_data, language='es-CO')
                        full_text.append(text_chunk)
                        print(f"  [Parte {c_idx+1}/{len(chunks)}]: {text_chunk}", flush=True)
                    except sr.UnknownValueError:
                        pass
                    except Exception as ex:
                        print(f"  [Parte {c_idx+1} error: {ex}]", flush=True)
            final_res = "TRANSCRIPCIÓN COMPLETA:\n" + (" ".join(full_text) if full_text else "(No se detectó voz)")
            print(final_res, flush=True)
            out.write(final_res + '\n')
            out.flush()
        except Exception as e:
            err_msg = f"Error procesando audio: {e}"
            print(err_msg, flush=True)
            out.write(err_msg + '\n')
print("\n--- PROCESO COMPLETADO ---", flush=True)
