import time
import speech_recognition as sr
import keyboard
import pyperclip
import threading
import io
import wave

HOTKEY = "alt gr"  # skift fx til "f8" eller "right shift"

def get_microphone_names():
    """Returnér kun input-enheder (heuristisk filtrering)."""
    all_names = sr.Microphone.list_microphone_names() or []
    mic_names = []
    for i, n in enumerate(all_names):
        n_lower = n.lower()
        if any(word in n_lower for word in ["mic", "microphone", "headset", "input", "record", "capture"]):
            mic_names.append((i, n))
    return mic_names

def pick_microphone_index():
    mic_names = get_microphone_names()
    if not mic_names:
        print("Ingen mikrofoner fundet – viser alle devices i stedet:")
        all_names = sr.Microphone.list_microphone_names() or []
        for i, n in enumerate(all_names):
            print(f"  {i}: {n}")
        choice = input("Vælg device-nummer (Enter for standard): ").strip()
        return int(choice) if choice.isdigit() else None

    print("Tilgængelige mikrofoner:")
    for i, n in mic_names:
        print(f"  {i}: {n}")

    while True:
        choice = input("Vælg mikrofon-nummer (Enter for standard): ").strip()
        if choice == "":
            return None
        if choice.isdigit():
            idx = int(choice)
            if any(idx == i for i, _ in mic_names):
                return idx
        print("Ugyldigt valg. Prøv igen.")

def main():
    device_index = 1  # HyperX Cloud Alpha headset

    r = sr.Recognizer()
    r.energy_threshold = 20   # Konstant lav værdi for følsom opfangning
    r.dynamic_energy_threshold = False  # Deaktiver dynamisk justering
    r.pause_threshold = 0.3   # Kort pause før stop - bedre for korte klip
    r.non_speaking_duration = 0.2  # Skal være mindre end pause_threshold
    r.phrase_time_limit = None  # Ingen tidsbegrænsning på sætninger

    mic = sr.Microphone(device_index=device_index)

    # Vis hvilken der blev valgt
    all_names = sr.Microphone.list_microphone_names() or []
    chosen_index = mic.device_index
    chosen_name = (
        all_names[chosen_index] if chosen_index is not None and chosen_index < len(all_names) else "Standard (ukendt navn)"
    )
    print(f"\n> Bruger mikrofon [{chosen_index if chosen_index is not None else 'standard'}]: {chosen_name}", flush=True)

    print("Kalibrerer støj (0.3s)…", flush=True)
    with mic as source:
        r.adjust_for_ambient_noise(source, duration=0.3)

    # Sæt energy threshold til konstant 20 efter kalibrering
    r.energy_threshold = 20
    print(f"Energy threshold sat til konstant: {r.energy_threshold}", flush=True)

    print(f"Klar. Hold {HOTKEY.upper()} nede for at tale. Slip for at stoppe. (Ctrl+C for at afslutte)", flush=True)

    is_recording = False
    last_recognized_text = ""
    is_processing = False
    recording_start_time = None
    recorded_frames = []

    def audio_recorder():
        """Kontinuerlig audio optagelse mens knappen holdes nede"""
        nonlocal recorded_frames
        while True:
            if is_recording:
                try:
                    with mic as source:
                        # Optag små chunks og gem dem
                        audio = r.listen(source, timeout=0.1, phrase_time_limit=1.0)
                        recorded_frames.append(audio.frame_data)
                except sr.WaitTimeoutError:
                    continue
                except Exception:
                    continue
            else:
                time.sleep(0.01)

    def countdown_timer():
        """Viser nedtælling mens der optages"""
        while True:
            if is_recording and recording_start_time:
                elapsed = time.time() - recording_start_time
                remaining = max(0, 10.0 - elapsed)
                if remaining > 0:
                    print(f"\r🎤 [{remaining:.1f}s tilbage]", end="", flush=True)
                    time.sleep(0.1)
                else:
                    print(f"\r⏰ [MAX TIDEN NÅT - slip knappen!]", end="", flush=True)
                    time.sleep(0.1)
            else:
                time.sleep(0.1)

    # Start tråde
    recorder_thread = threading.Thread(target=audio_recorder, daemon=True)
    recorder_thread.start()
    timer_thread = threading.Thread(target=countdown_timer, daemon=True)
    timer_thread.start()

    def start_listening():
        nonlocal is_recording, last_recognized_text, recording_start_time, recorded_frames
        if not is_recording:
            is_recording = True
            recording_start_time = time.time()
            last_recognized_text = ""
            recorded_frames = []  # Reset optagelse

    def stop_listening():
        nonlocal is_recording, last_recognized_text, is_processing, recording_start_time, recorded_frames
        if is_recording:
            is_recording = False
            recording_start_time = None
            print("\n⏹️ [stopper optagelse - fanger sidste lyd…]", flush=True)

            # Vent længere på sidste chunks kommer ind
            time.sleep(2.0)

            # Saml alle optagede frames
            if recorded_frames:
                try:
                    is_processing = True

                    # Kombiner alle frames til ét audio objekt
                    combined_data = b''.join(recorded_frames)
                    audio = sr.AudioData(combined_data, mic.SAMPLE_RATE, mic.SAMPLE_WIDTH)

                    # Genkend det optagede
                    text = r.recognize_google(audio, language="da-DK")
                    if text.strip():
                        print(f"✓ {text}", flush=True)
                        last_recognized_text = text.strip()
                        pyperclip.copy(last_recognized_text)
                        print(f"[clipboard opdateret: '{last_recognized_text}']", flush=True)
                    else:
                        print("✗ (tom tekst)", flush=True)

                except sr.UnknownValueError:
                    print("✗ (uklart)", flush=True)
                except sr.RequestError as e:
                    print(f"✗ (forbindelsesfejl: {e})", flush=True)
                except Exception as e:
                    print(f"✗ (fejl: {e})", flush=True)
                finally:
                    is_processing = False
            else:
                print("✗ (ingen lyd optaget)", flush=True)

            print("[klar til næste]", flush=True)

    keyboard.on_press_key(HOTKEY, lambda e: start_listening())
    keyboard.on_release_key(HOTKEY, lambda e: stop_listening())

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopper…", flush=True)

if __name__ == "__main__":
    main()
