# Windows Speech to Text

Et Python script til tale-til-tekst på Windows med hotkey aktivering.

## Hvad gør det?

Dette script lader dig:
- Holde en hotkey nede for at optage din stemme
- Automatisk konvertere talen til tekst på dansk
- Kopiere den genkendte tekst til clipboard
- Se real-time feedback under optagelse

## Krav

- Python 3.6+
- Internetforbindelse (bruger Google Speech Recognition)
- Mikrofon

## Installation

1. Klon repositoriet:
```bash
git clone https://github.com/thranefuglen/WindowsSpeechToText.git
cd WindowsSpeechToText
```

2. Installer dependencies:
```bash
pip install SpeechRecognition keyboard pyperclip pyaudio
```

## Brug

1. Kør scriptet:
```bash
python stt.py
```

2. Programmet viser tilgængelige mikrofoner og kalibrerer støj

3. Hold **Alt Gr** nede for at optage (ændr `HOTKEY` variablen i koden for anden knap)

4. Slip knappen for at stoppe og få teksten konverteret

5. Teksten kopieres automatisk til clipboard

## Konfiguration

Rediger følgende variabler i `stt.py`:

- `HOTKEY`: Skift hotkey (f.eks. "f8", "right shift")
- `device_index`: Vælg specifik mikrofon (se liste ved start)
- `energy_threshold`: Juster mikrofonfølsomhed
- `pause_threshold`: Tid før optagelse stopper

## Features

- ⏱️ Real-time nedtælling under optagelse
- 🎤 Automatisk clipboard kopiering
- 🔧 Mikrofon kalibrering og valg
- 🇩🇰 Dansk stemmegenkendelelse
- ⌨️ Hotkey aktivering

## Fejlfinding

**"Ingen lyd optaget"**: Kontroller mikrofon indstillinger og justér `energy_threshold`

**"Uklart"**: Tal tydeligere eller tættere på mikrofonen

**"Forbindelsesfejl"**: Kontroller internetforbindelse

**Hotkey virker ikke**: Kør som administrator eller skift til anden tast