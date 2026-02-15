# Complete Setup Guide - Analog Circuit Node-Based Synthesis Framework

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Project Structure](#project-structure)
3. [Installation Steps](#installation-steps)
4. [Quick Start Guide](#quick-start-guide)
5. [Running Examples](#running-examples)
6. [Using the Visual Editor](#using-the-visual-editor)
7. [Creating Your First Patch](#creating-your-first-patch)
8. [Troubleshooting](#troubleshooting)
9. [Next Steps](#next-steps)

---

## 🖥️ System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 100MB for project files
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 20.04+)
- **Web Browser**: Chrome, Firefox, Safari, or Edge (for visual editor)

### Python Packages Required
- `numpy` - Numerical computing
- `scipy` - Scientific computing and audio I/O
- `matplotlib` - Plotting and visualization

---

## 📁 Project Structure

```
analog-synthesis-framework/
│
├── 📄 README.md                          # Main project overview
├── 📄 QUICKSTART.md                      # 5-minute quick start
├── 📄 EXTENSION_GUIDE.md                 # How to create custom circuits
├── 📄 NODE_SYSTEM_README.md              # Node system documentation
├── 📄 GETTING_STARTED.md                 # This file
├── 📄 requirements.txt                   # Python dependencies
│
├── 🎛️ CORE FRAMEWORK
│   ├── analog_synth_framework.py         # Core analog circuit components
│   │   ├── AnalogComponent (base class)
│   │   ├── VCOCircuit (oscillator)
│   │   ├── MoogLadderFilter (filter)
│   │   ├── StateVariableFilter (multimode filter)
│   │   ├── AnalogADSR (envelope)
│   │   ├── LFO (modulator)
│   │   ├── AnalogSynthVoice (complete synth)
│   │   └── PresetManager (save/load sounds)
│   │
│   └── examples.py                       # Framework usage examples
│       ├── example_1_basic_note()
│       ├── example_2_bass_line()
│       ├── example_3_pad_sound()
│       ├── example_4_filter_sweep()
│       └── More...
│
├── 🔗 NODE SYSTEM
│   ├── node_system.py                    # Node graph engine
│   │   ├── NodeBase (base class)
│   │   ├── NodeGraph (patch manager)
│   │   ├── NodeFactory (node registry)
│   │   ├── Connection (routing)
│   │   └── Signal types & utilities
│   │
│   ├── analog_nodes.py                   # Node implementations
│   │   ├── OscillatorNode
│   │   ├── MoogFilterNode
│   │   ├── StateVariableFilterNode
│   │   ├── ADSRNode
│   │   ├── LFONode
│   │   ├── MixerNode
│   │   ├── GainNode
│   │   ├── VCANode
│   │   ├── MIDINoteNode
│   │   ├── AudioOutputNode
│   │   ├── ConstantNode
│   │   └── ScopeNode
│   │
│   └── node_examples.py                  # Node system examples
│       ├── example_1_basic_synth()
│       ├── example_2_detuned_synth()
│       └── example_3_lfo_filter()
│
├── 🎨 VISUAL EDITOR
│   └── node_editor.html                  # Web-based node editor
│       ├── Interactive canvas
│       ├── Node library
│       ├── Properties panel
│       └── Connection routing
│
└── 🎵 GENERATED FILES (after running)
    ├── example1_basic_note.wav
    ├── example2_bass_line.wav
    ├── example3_pad_sound.wav
    ├── example4_filter_sweep.wav
    ├── node_example1_basic_synth.wav
    ├── node_example2_detuned.wav
    ├── node_example3_lfo.wav
    ├── circuit_analysis.png
    └── synth_presets.json
```

---

## 🚀 Installation Steps

### Step 1: Download the Project

Save all project files to a folder on your computer:

```bash
# Create project directory
mkdir analog-synthesis
cd analog-synthesis

# All files should be in this directory
```

**Files you should have:**
```
analog-synthesis/
├── analog_synth_framework.py
├── node_system.py
├── analog_nodes.py
├── examples.py
├── node_examples.py
├── node_editor.html
├── requirements.txt
├── README.md
├── QUICKSTART.md
├── EXTENSION_GUIDE.md
├── NODE_SYSTEM_README.md
└── GETTING_STARTED.md (this file)
```

### Step 2: Install Python

**Check if Python is installed:**

```bash
python3 --version
# or
python --version
```

You should see: `Python 3.8.x` or higher

**If not installed:**

- **Windows**: Download from [python.org](https://www.python.org/downloads/)
  - ✅ Check "Add Python to PATH" during installation
- **macOS**: 
  ```bash
  brew install python3
  ```
- **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt update
  sudo apt install python3 python3-pip
  ```

### Step 3: Install Dependencies

Open a terminal/command prompt in the project directory:

```bash
# Navigate to project folder
cd /path/to/analog-synthesis

# Install required packages
pip3 install -r requirements.txt

# Or install manually:
pip3 install numpy scipy matplotlib
```

**Verify installation:**

```bash
python3 -c "import numpy, scipy, matplotlib; print('All packages installed successfully!')"
```

You should see: `All packages installed successfully!`

### Step 4: Test the Installation

Run a simple test:

```bash
python3 -c "from analog_synth_framework import VCOCircuit; print('Framework loaded!')"
```

You should see: `Framework loaded!`

---

## 🎯 Quick Start Guide

### Test 1: Generate Your First Sound (2 minutes)

Create a file `test_sound.py`:

```python
from analog_synth_framework import AnalogSynthVoice, midi_to_frequency
from scipy.io import wavfile
import numpy as np

# Create synthesizer
voice = AnalogSynthVoice(sample_rate=44100)

# Configure sound
voice.osc1.set_parameter('waveform', 'saw')
voice.filter.set_parameter('cutoff', 2000.0)
voice.filter.set_parameter('resonance', 0.7)

# Play middle C
voice.note_on(midi_to_frequency(60))
audio = voice.render(44100)  # 1 second

# Save
audio = audio / np.max(np.abs(audio)) * 0.8
wavfile.write('my_first_sound.wav', 44100, (audio * 32767).astype(np.int16))

print("✓ Created my_first_sound.wav")
```

Run it:

```bash
python3 test_sound.py
```

**Result:** You should have `my_first_sound.wav` - a 1-second synthesizer note!

### Test 2: Run Framework Examples (5 minutes)

```bash
python3 examples.py
```

**This will:**
1. Generate 7 different synthesizer sounds
2. Create waveform visualizations
3. Demonstrate all framework features
4. Take about 30 seconds to complete

**Output files:**
- `example1_basic_note.wav`
- `example2_bass_line.wav`
- `example3_pad_sound.wav`
- `example4_filter_sweep.wav`
- `example5_preset_test.wav`
- `example6_waveforms.png`
- `example7_envelopes.png`
- `synth_presets.json`

### Test 3: Run Node System (5 minutes)

```bash
python3 node_examples.py
```

**This will:**
1. Create 3 complete synthesizer patches
2. Render them to audio
3. Demonstrate node-based synthesis

**Output files:**
- `node_example1_basic_synth.wav`
- `node_example2_detuned.wav`
- `node_example3_lfo.wav`

---

## 🎨 Using the Visual Editor

### Step 1: Open the Editor

**Option A - Double Click:**
Simply double-click `node_editor.html` in your file browser

**Option B - From Terminal:**

```bash
# macOS
open node_editor.html

# Linux
xdg-open node_editor.html

# Windows
start node_editor.html

# Or just open in any browser
firefox node_editor.html
```

### Step 2: Understanding the Interface

```
┌─────────────────────────────────────────────────────────────┐
│  🎛️ Node Editor                    ▶️ Render  💾 Save  🗑️  │
├──────────┬────────────────────────────────────┬─────────────┤
│          │                                    │             │
│  📦 Node │                                    │  ⚙️ Props   │
│  Library │         Canvas Area                │             │
│          │    (Drag nodes here)               │  Selected:  │
│  🎵 Osc  │                                    │  VCO        │
│   • VCO  │    ┌─────────┐                     │             │
│          │    │   VCO   │───→ ┌──────┐        │  Waveform:  │
│  🔊 Filt │    └─────────┘     │Filter│        │  [saw ▼]    │
│   • Moog │                    └──────┘        │             │
│   • SVF  │                       │            │  Frequency: │
│          │                       ↓            │  [440  ]    │
│  📈 Env  │                  ┌────────┐        │             │
│   • ADSR │                  │AudioOut│        │             │
│          │                  └────────┘        │             │
│  🌊 LFO  │                                    │             │
│          │                                    │             │
└──────────┴────────────────────────────────────┴─────────────┘
```

### Step 3: Create Your First Visual Patch

**Instructions:**

1. **Add a MIDI Note node**
   - Click "MIDI Note" in I/O section
   - It appears in the center

2. **Add an Oscillator**
   - Click "VCO" in Oscillators section
   - Drag it to the right of MIDI Note

3. **Add a Filter**
   - Click "Moog Filter" in Filters section
   - Drag it to the right of VCO

4. **Add Audio Output**
   - Click "Audio Out" in I/O section
   - Drag it to the far right

5. **Connect them:**
   - Click the blue circle (output) on MIDI Note labeled "frequency"
   - Click the blue circle (input) on VCO labeled "frequency"
   - Repeat: VCO "output" → Filter "input"
   - Repeat: Filter "output" → Audio Out "left"
   - Repeat: Filter "output" → Audio Out "right"

6. **Configure parameters:**
   - Click the MIDI Note node
   - In Properties panel (right side):
     - Set note: 60 (middle C)
     - Check "gate_on" checkbox
   - Click the VCO node
     - Set waveform: saw
   - Click the Filter node
     - Set cutoff: 1000
     - Set resonance: 0.7

7. **Test it:**
   - Click "▶️ Render" button
   - (In full implementation, this would generate audio)

### Step 4: Save Your Patch

Click "💾 Save" button to download your patch as JSON.

---

## 🎼 Creating Your First Patch (Python)

### Example: Simple Bass Synth

Create `my_bass_synth.py`:

```python
from node_system import NodeGraph
from analog_nodes import *
from scipy.io import wavfile
import numpy as np

# Setup
sample_rate = 44100
graph = NodeGraph(sample_rate)
graph.name = "My Bass Synth"

# Create nodes
midi = MIDINoteNode(sample_rate=sample_rate)
osc = OscillatorNode(sample_rate=sample_rate)
filter_node = MoogFilterNode(sample_rate=sample_rate)
filter_env = ADSRNode(sample_rate=sample_rate)
amp_env = ADSRNode(sample_rate=sample_rate)
vca = VCANode(sample_rate=sample_rate)
output = AudioOutputNode(sample_rate=sample_rate)

# Configure for bass sound
midi.set_parameter('note', 36)  # C2 - low bass note
midi.set_parameter('gate_on', True)

osc.set_parameter('waveform', 'square')
osc.set_parameter('pulse_width', 0.3)  # Fat square wave

filter_node.set_parameter('cutoff', 400.0)  # Low cutoff
filter_node.set_parameter('resonance', 0.85)  # High resonance
filter_node.set_parameter('drive', 2.5)  # Saturate it
filter_node.set_parameter('cutoff_mod_amount', 2.0)

filter_env.set_parameter('attack', 0.001)
filter_env.set_parameter('decay', 0.12)
filter_env.set_parameter('sustain', 0.0)
filter_env.set_parameter('release', 0.1)

amp_env.set_parameter('attack', 0.001)
amp_env.set_parameter('decay', 0.15)
amp_env.set_parameter('sustain', 0.5)
amp_env.set_parameter('release', 0.1)

# Add to graph
for node in [midi, osc, filter_node, filter_env, amp_env, vca, output]:
    graph.add_node(node)

# Connect (signal flow)
graph.connect(midi.node_id, 'frequency', osc.node_id, 'frequency')
graph.connect(midi.node_id, 'gate', filter_env.node_id, 'gate')
graph.connect(midi.node_id, 'gate', amp_env.node_id, 'gate')
graph.connect(osc.node_id, 'output', filter_node.node_id, 'input')
graph.connect(filter_env.node_id, 'output', filter_node.node_id, 'cutoff_mod')
graph.connect(filter_node.node_id, 'output', vca.node_id, 'input')
graph.connect(amp_env.node_id, 'output', vca.node_id, 'control')
graph.connect(vca.node_id, 'output', output.node_id, 'left')
graph.connect(vca.node_id, 'output', output.node_id, 'right')

print(graph.get_info())

# Render audio
duration = 1.5
buffer_size = int(sample_rate * duration)
chunk_size = 512

audio_left = []
audio_right = []

print("\nRendering bass note...")
for i in range(0, buffer_size, chunk_size):
    current_chunk = min(chunk_size, buffer_size - i)
    
    # Release note after 1 second
    if i == int(sample_rate * 1.0):
        midi.set_parameter('gate_on', False)
    
    outputs = graph.process(current_chunk)
    
    if output.node_id in outputs:
        audio_left.append(outputs[output.node_id]['left'])
        audio_right.append(outputs[output.node_id]['right'])

# Combine and normalize
audio_left = np.concatenate(audio_left)
audio_right = np.concatenate(audio_right)
audio_left = audio_left / np.max(np.abs(audio_left)) * 0.8
audio_right = audio_right / np.max(np.abs(audio_right)) * 0.8

# Save stereo
audio_stereo = np.column_stack((audio_left, audio_right))
wavfile.write('my_bass_synth.wav', sample_rate,
              (audio_stereo * 32767).astype(np.int16))

print("✓ Created my_bass_synth.wav")
```

Run it:

```bash
python3 my_bass_synth.py
```

**Result:** A punchy bass note in `my_bass_synth.wav`!

---

## 🔧 Troubleshooting

### Problem: `ModuleNotFoundError: No module named 'numpy'`

**Solution:**
```bash
pip3 install numpy scipy matplotlib
```

### Problem: `pip3: command not found`

**Solution:**
Try `pip` instead of `pip3`:
```bash
pip install numpy scipy matplotlib
```

Or install pip:
```bash
# Ubuntu/Debian
sudo apt install python3-pip

# macOS
python3 -m ensurepip
```

### Problem: No sound in generated WAV files

**Check:**
1. File was created: `ls -lh *.wav`
2. File size is reasonable (> 1KB)
3. Try a different media player
4. Check parameters aren't all zero

**Debug:**
```python
# Add to your script
print(f"Audio range: {audio.min()} to {audio.max()}")
print(f"Audio samples: {len(audio)}")
```

### Problem: Node editor doesn't open

**Solution:**
1. Make sure `node_editor.html` is in your directory
2. Try opening directly in browser:
   - Open Chrome/Firefox
   - File → Open File → Select `node_editor.html`

### Problem: Import errors between modules

**Solution:**
Make sure all files are in the same directory:
```bash
ls -1
# Should show:
# analog_synth_framework.py
# node_system.py
# analog_nodes.py
# examples.py
# node_examples.py
```

### Problem: `Permission denied` when running scripts

**Solution:**
```bash
chmod +x examples.py
python3 examples.py
```

### Problem: Audio is distorted/clipping

**Solution:**
The audio is being normalized. If it still clips:
```python
# Reduce gain
audio = audio / np.max(np.abs(audio)) * 0.5  # Instead of 0.8
```

---

## 📚 Next Steps

### 1. Explore Framework Examples

```bash
python3 examples.py
```

Study the code to understand:
- How oscillators work
- Filter configuration
- Envelope shaping
- Preset management

### 2. Read Documentation

- **QUICKSTART.md** - Get coding in 5 minutes
- **README.md** - Framework overview
- **EXTENSION_GUIDE.md** - Create custom circuits
- **NODE_SYSTEM_README.md** - Node system details

### 3. Experiment with Parameters

Modify `test_sound.py`:

```python
# Try different waveforms
voice.osc1.set_parameter('waveform', 'square')  # or 'triangle', 'sine'

# Adjust filter
voice.filter.set_parameter('cutoff', 5000.0)  # Brighter
voice.filter.set_parameter('resonance', 0.9)   # More resonance

# Change envelope
voice.amp_envelope.set_parameter('attack', 0.5)   # Slow attack
voice.amp_envelope.set_parameter('release', 2.0)  # Long release
```

### 4. Create Custom Nodes

See `EXTENSION_GUIDE.md` for:
- Creating new oscillator types
- Designing filters
- Building effects processors
- Advanced DSP techniques

### 5. Build Complete Instruments

Combine nodes to create:
- Polyphonic synthesizers
- Drum machines
- Effects processors
- Generative music systems

---

## 🎓 Learning Path

### Beginner (Week 1)
1. ✅ Install and test
2. ✅ Generate first sound
3. ✅ Run all examples
4. ✅ Modify parameters
5. ✅ Understand signal flow

### Intermediate (Week 2-3)
1. Create custom patches in Python
2. Use visual editor
3. Experiment with modulation
4. Build simple effects
5. Study the framework code

### Advanced (Week 4+)
1. Create custom nodes
2. Design new circuits
3. Implement effects chains
4. Build polyphonic system
5. Contribute to project

---

## 📞 Getting Help

### Check Documentation
- All `.md` files contain detailed info
- Code comments explain implementation
- Examples show best practices

### Debug Checklist
- [ ] Python 3.8+ installed?
- [ ] All packages installed?
- [ ] All files in same directory?
- [ ] Correct file names (case sensitive)?
- [ ] Sample rate consistent (44100)?

### Common Issues Reference

| Issue | Quick Fix |
|-------|-----------|
| Module not found | `pip3 install numpy scipy matplotlib` |
| No sound | Check parameters, verify file created |
| Distortion | Reduce gain multiplier |
| Slow performance | Reduce buffer_size or duration |
| Connection errors | Verify node IDs and port names |

---

## ✅ Verification Checklist

After installation, verify everything works:

```bash
# 1. Framework test
python3 -c "from analog_synth_framework import *; print('✓ Framework OK')"

# 2. Node system test
python3 -c "from node_system import *; from analog_nodes import *; print('✓ Node system OK')"

# 3. Generate test sound
python3 test_sound.py

# 4. Run examples
python3 examples.py

# 5. Run node examples
python3 node_examples.py

# 6. Open visual editor
open node_editor.html
```

All should complete without errors!

---

## 🎉 Success!

If you've made it here and all tests pass, you're ready to:
- Create analog synthesizer sounds
- Build modular patches
- Design custom circuits
- Explore sound design

**Happy synthesizing! 🎛️🎵**

---

## 📄 File Checklist

Before starting, ensure you have all these files:

```bash
# Core Framework (3 files)
[ ] analog_synth_framework.py    # Main framework
[ ] examples.py                  # Framework examples

# Node System (3 files)
[ ] node_system.py              # Node engine
[ ] analog_nodes.py             # Node implementations
[ ] node_examples.py            # Node examples

# Visual Interface (1 file)
[ ] node_editor.html            # Web editor

# Documentation (5 files)
[ ] README.md                   # Overview
[ ] QUICKSTART.md               # Quick start
[ ] EXTENSION_GUIDE.md          # Create custom circuits
[ ] NODE_SYSTEM_README.md       # Node system guide
[ ] GETTING_STARTED.md          # This file

# Configuration (1 file)
[ ] requirements.txt            # Python dependencies
```

Total: **13 files** needed to start

---

**Version:** 1.0  
**Last Updated:** February 2026  
**License:** MIT
