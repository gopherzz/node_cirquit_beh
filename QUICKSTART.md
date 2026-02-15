# Quick Start Tutorial - Analog Circuit Synthesis Framework

## Welcome! 🎛️

This tutorial will get you creating analog synthesizer sounds in minutes.

## What You'll Need

```bash
pip install numpy scipy matplotlib
```

## Your First Sound (5 minutes)

### Step 1: Import the Framework

```python
from analog_synth_framework import AnalogSynthVoice, midi_to_frequency
from scipy.io import wavfile
import numpy as np
```

### Step 2: Create a Voice

```python
# Initialize with standard sample rate
voice = AnalogSynthVoice(sample_rate=44100)
```

### Step 3: Configure the Sound

```python
# Set oscillator waveforms
voice.osc1.set_parameter('waveform', 'saw')    # Classic analog sound
voice.osc2.set_parameter('waveform', 'square') # Add thickness
voice.osc_mix = 0.5  # Equal mix of both oscillators

# Set filter characteristics
voice.filter.set_parameter('cutoff', 2000.0)    # Brightness
voice.filter.set_parameter('resonance', 0.7)    # Emphasis at cutoff

# Configure amplitude envelope (how the sound evolves)
voice.amp_envelope.set_parameter('attack', 0.01)   # 10ms attack
voice.amp_envelope.set_parameter('decay', 0.3)     # 300ms decay
voice.amp_envelope.set_parameter('sustain', 0.7)   # 70% sustain level
voice.amp_envelope.set_parameter('release', 0.5)   # 500ms release

# Add filter modulation for movement
voice.filter_env_amount = 2.0  # Strong filter sweep
```

### Step 4: Play a Note

```python
# Trigger middle C
voice.note_on(midi_to_frequency(60))

# Generate 1 second of audio
audio = voice.render(44100)

# Save to file
audio_normalized = audio / np.max(np.abs(audio))
wavfile.write('my_first_synth_sound.wav', 44100, 
              (audio_normalized * 32767).astype(np.int16))
```

**Done!** You've created your first analog synthesizer sound! 🎉

---

## Understanding the Components

### 1. Oscillators (Sound Sources)

Oscillators generate the raw audio waveforms:

```python
# Access oscillators
voice.osc1  # Oscillator 1
voice.osc2  # Oscillator 2

# Available waveforms
voice.osc1.set_parameter('waveform', 'saw')      # Bright, buzzy
voice.osc1.set_parameter('waveform', 'square')   # Hollow, woody
voice.osc1.set_parameter('waveform', 'triangle') # Soft, mellow
voice.osc1.set_parameter('waveform', 'sine')     # Pure tone

# For square wave, adjust pulse width
voice.osc1.set_parameter('pulse_width', 0.5)  # 0.1 to 0.9
```

**What it sounds like:**
- **Sawtooth**: Bright and buzzy - great for leads and bass
- **Square**: Hollow and reedy - classic for bass and retro sounds
- **Triangle**: Soft and mellow - good for pads
- **Sine**: Pure fundamental - electronic bass, subtle layers

### 2. Filter (Tone Shaper)

The filter removes frequencies and shapes the tone:

```python
voice.filter.set_parameter('cutoff', 1000.0)    # Hz (20 to 20000)
voice.filter.set_parameter('resonance', 0.8)    # 0.0 to 1.0
voice.filter.set_parameter('drive', 1.5)        # 1.0 to 10.0
```

**Parameters:**
- **Cutoff**: Frequency where filtering begins (lower = darker)
- **Resonance**: Emphasis at cutoff frequency (higher = more "wah")
- **Drive**: Input gain/saturation (higher = more distortion)

**Tips:**
- Cutoff 500-800 Hz: Deep bass
- Cutoff 1500-3000 Hz: Bright leads
- Cutoff 3000-8000 Hz: Airy pads
- Resonance 0.7-0.9: Classic analog character

### 3. Envelopes (Time Evolution)

Envelopes control how parameters change over time:

```python
# Amplitude envelope (controls volume)
voice.amp_envelope.set_parameter('attack', 0.01)   # Time to peak
voice.amp_envelope.set_parameter('decay', 0.2)     # Time to sustain
voice.amp_envelope.set_parameter('sustain', 0.7)   # Held level
voice.amp_envelope.set_parameter('release', 0.3)   # Time to silence

# Filter envelope (controls filter cutoff)
voice.filter_envelope.set_parameter('attack', 0.02)
voice.filter_envelope.set_parameter('decay', 0.4)
voice.filter_envelope.set_parameter('sustain', 0.3)
voice.filter_envelope.set_parameter('release', 0.2)

# How much filter envelope affects cutoff
voice.filter_env_amount = 2.0  # 0.0 to 5.0
```

**Common Envelope Shapes:**

```python
# Pluck (guitar, piano)
attack=0.001, decay=0.2, sustain=0.0, release=0.1

# Pad (strings, atmosphere)
attack=0.5, decay=0.5, sustain=0.8, release=1.0

# Organ (held notes)
attack=0.001, decay=0.0, sustain=1.0, release=0.1

# Bass (punchy)
attack=0.001, decay=0.15, sustain=0.5, release=0.1
```

### 4. LFO (Modulation)

Low Frequency Oscillator adds movement:

```python
voice.lfo.set_parameter('frequency', 5.0)       # Hz (0.1 to 20.0)
voice.lfo.set_parameter('waveform', 'sine')     # sine, triangle, saw, square

# Route LFO to filter
voice.lfo_to_filter_amount = 0.3  # 0.0 to 1.0
```

**LFO Applications:**
- Frequency 0.2-2 Hz: Slow filter sweep, vibrato
- Frequency 4-8 Hz: Tremolo, rhythmic effects
- Triangle wave: Smooth modulation
- Square wave: Rhythmic on/off

---

## Complete Example: Lead Sound

```python
from analog_synth_framework import *
from scipy.io import wavfile
import numpy as np

sample_rate = 44100
voice = AnalogSynthVoice(sample_rate)

# Two detuned sawtooth oscillators
voice.osc1.set_parameter('waveform', 'saw')
voice.osc1.set_parameter('frequency', 440.0)
voice.osc2.set_parameter('waveform', 'saw')
voice.osc2.set_parameter('frequency', 440.5)  # Slight detune
voice.osc_mix = 0.5

# Bright, resonant filter
voice.filter.set_parameter('cutoff', 3000.0)
voice.filter.set_parameter('resonance', 0.6)
voice.filter.set_parameter('drive', 1.2)

# Snappy envelope
voice.amp_envelope.set_parameter('attack', 0.01)
voice.amp_envelope.set_parameter('decay', 0.2)
voice.amp_envelope.set_parameter('sustain', 0.7)
voice.amp_envelope.set_parameter('release', 0.3)

# Filter movement
voice.filter_envelope.set_parameter('attack', 0.02)
voice.filter_envelope.set_parameter('decay', 0.3)
voice.filter_envelope.set_parameter('sustain', 0.4)
voice.filter_envelope.set_parameter('release', 0.2)
voice.filter_env_amount = 1.5

# Subtle vibrato
voice.lfo.set_parameter('frequency', 5.5)
voice.lfo.set_parameter('waveform', 'sine')
voice.lfo_to_filter_amount = 0.15

# Play note
voice.note_on(midi_to_frequency(69))  # A4
audio = voice.render(int(sample_rate * 2))

# Save
audio = audio / np.max(np.abs(audio))
wavfile.write('lead_sound.wav', sample_rate, 
              (audio * 32767).astype(np.int16))

print("Created lead_sound.wav")
```

---

## Complete Example: Bass Sound

```python
from analog_synth_framework import *
from scipy.io import wavfile
import numpy as np

sample_rate = 44100
voice = AnalogSynthVoice(sample_rate)

# Fat square wave
voice.osc1.set_parameter('waveform', 'square')
voice.osc1.set_parameter('pulse_width', 0.3)
voice.osc2.set_parameter('waveform', 'saw')
voice.osc_mix = 0.7

# Low, resonant filter
voice.filter.set_parameter('cutoff', 400.0)
voice.filter.set_parameter('resonance', 0.85)
voice.filter.set_parameter('drive', 2.5)

# Punchy envelope
voice.amp_envelope.set_parameter('attack', 0.001)
voice.amp_envelope.set_parameter('decay', 0.15)
voice.amp_envelope.set_parameter('sustain', 0.5)
voice.amp_envelope.set_parameter('release', 0.1)

# Fast filter decay
voice.filter_envelope.set_parameter('attack', 0.001)
voice.filter_envelope.set_parameter('decay', 0.12)
voice.filter_envelope.set_parameter('sustain', 0.0)
voice.filter_envelope.set_parameter('release', 0.1)
voice.filter_env_amount = 2.0

# Play low note
voice.note_on(midi_to_frequency(36))  # C2
audio = voice.render(int(sample_rate * 1.5))

# Save
audio = audio / np.max(np.abs(audio))
wavfile.write('bass_sound.wav', sample_rate, 
              (audio * 32767).astype(np.int16))

print("Created bass_sound.wav")
```

---

## Playing a Melody

```python
# MIDI note numbers
notes = [60, 64, 67, 72]  # C, E, G, C (C major chord)
note_duration = 0.5  # seconds

audio_segments = []

for midi_note in notes:
    # Trigger note
    voice.note_on(midi_to_frequency(midi_note))
    
    # Render
    samples = int(sample_rate * note_duration)
    audio = voice.render(samples)
    audio_segments.append(audio)
    
    # Release
    voice.note_off()
    
    # Reset envelopes for next note
    voice.amp_envelope.reset()
    voice.filter_envelope.reset()

# Combine all notes
full_audio = np.concatenate(audio_segments)

# Save
audio_normalized = full_audio / np.max(np.abs(full_audio))
wavfile.write('melody.wav', sample_rate, 
              (audio_normalized * 32767).astype(np.int16))
```

---

## Tips for Great Sounds

### 1. Oscillator Detuning
```python
# Slightly detune oscillators for thickness
voice.osc1.set_parameter('frequency', 440.0)
voice.osc2.set_parameter('frequency', 440.5)  # +0.5 Hz
```

### 2. Filter Envelope Amount
```python
# More filter modulation = more movement
voice.filter_env_amount = 0.0   # No modulation
voice.filter_env_amount = 1.0   # Moderate
voice.filter_env_amount = 3.0   # Extreme
```

### 3. Resonance Sweet Spots
```python
voice.filter.set_parameter('resonance', 0.3)  # Subtle
voice.filter.set_parameter('resonance', 0.7)  # Classic analog
voice.filter.set_parameter('resonance', 0.95) # Screaming
```

### 4. Drive for Character
```python
voice.filter.set_parameter('drive', 1.0)   # Clean
voice.filter.set_parameter('drive', 2.0)   # Warm
voice.filter.set_parameter('drive', 5.0)   # Distorted
```

---

## Sound Design Recipes

### Warm Pad
```python
voice.osc1.set_parameter('waveform', 'saw')
voice.osc2.set_parameter('waveform', 'triangle')
voice.osc_mix = 0.6
voice.filter.set_parameter('cutoff', 2500.0)
voice.filter.set_parameter('resonance', 0.3)
voice.amp_envelope.set_parameter('attack', 0.8)
voice.amp_envelope.set_parameter('release', 1.2)
voice.lfo_to_filter_amount = 0.2
```

### Pluck Synth
```python
voice.osc1.set_parameter('waveform', 'triangle')
voice.filter.set_parameter('cutoff', 4000.0)
voice.filter.set_parameter('resonance', 0.5)
voice.amp_envelope.set_parameter('attack', 0.001)
voice.amp_envelope.set_parameter('decay', 0.3)
voice.amp_envelope.set_parameter('sustain', 0.0)
voice.filter_env_amount = 2.0
```

### Brass Sound
```python
voice.osc1.set_parameter('waveform', 'saw')
voice.osc2.set_parameter('waveform', 'square')
voice.filter.set_parameter('cutoff', 1800.0)
voice.filter.set_parameter('resonance', 0.6)
voice.filter.set_parameter('drive', 2.0)
voice.amp_envelope.set_parameter('attack', 0.05)
voice.filter_env_amount = 1.2
```

### Acid Bass
```python
voice.osc1.set_parameter('waveform', 'saw')
voice.filter.set_parameter('cutoff', 300.0)
voice.filter.set_parameter('resonance', 0.9)
voice.filter.set_parameter('drive', 3.0)
voice.amp_envelope.set_parameter('attack', 0.001)
voice.amp_envelope.set_parameter('decay', 0.2)
voice.filter_envelope.set_parameter('decay', 0.15)
voice.filter_env_amount = 3.0
```

---

## Troubleshooting

### Problem: No sound
- Check that you called `voice.note_on()` before `render()`
- Verify sample rate matches (44100)
- Check audio levels aren't at zero

### Problem: Sound is distorted
- Reduce filter drive parameter
- Lower filter resonance
- Normalize audio before saving

### Problem: Sound is too quiet
```python
# Normalize audio
audio = audio / np.max(np.abs(audio)) * 0.8
```

### Problem: Clicks between notes
- Reset envelopes between notes:
```python
voice.amp_envelope.reset()
voice.filter_envelope.reset()
```

---

## Next Steps

1. **Experiment**: Try different combinations of parameters
2. **Read EXTENSION_GUIDE.md**: Learn to create custom circuits
3. **Run examples.py**: See advanced techniques
4. **Create presets**: Save your favorite sounds

```python
from analog_synth_framework import PresetManager

pm = PresetManager()
pm.save_preset('My Lead', voice)
pm.export_presets('my_sounds.json')
```

---

## Getting Help

- Check **README.md** for overview
- Read **EXTENSION_GUIDE.md** for advanced features
- Review **examples.py** for working code
- Examine the framework source code for implementation details

---

**Happy synthesizing! 🎹✨**

The analog warmth you seek is just a few parameters away!
