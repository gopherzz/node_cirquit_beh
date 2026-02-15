# 🎛️ Analog Circuit Node-Based Synthesis Framework - Master Index

## Welcome! 👋

This is a complete modular synthesis framework that simulates analog circuits and provides a node-based patching interface for creating synthesizers, effects, and experimental sound design tools.

---

## 🚀 Start Here

**New to the project?** Follow this path:

1. **[GETTING_STARTED.md](GETTING_STARTED.md)** ← **START HERE**
   - Complete installation guide
   - Step-by-step setup
   - First sound in 5 minutes
   - Troubleshooting

2. **[QUICKSTART.md](QUICKSTART.md)**
   - Fast-track to making sounds
   - Common recipes
   - Parameter guide

3. **Run the examples:**
   ```bash
   python3 examples.py
   python3 node_examples.py
   ```

4. **Open the visual editor:**
   ```bash
   open node_editor.html
   ```

---

## 📚 Documentation Index

### Getting Started
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Complete setup guide with troubleshooting
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute quick start tutorial
- **[README.md](README.md)** - Project overview and features

### Core Framework
- **[EXTENSION_GUIDE.md](EXTENSION_GUIDE.md)** - Create custom analog circuits
  - Adding oscillators
  - Designing filters
  - Effects processors
  - Advanced DSP techniques

### Node System
- **[NODE_SYSTEM_README.md](NODE_SYSTEM_README.md)** - Complete node system guide
  - Available nodes
  - Creating patches
  - Custom nodes
  - Signal routing

---

## 📁 Project Files

### Core Framework

| File | Description | Lines | Purpose |
|------|-------------|-------|---------|
| `analog_synth_framework.py` | Main framework | ~700 | Analog circuit components |
| `examples.py` | Framework examples | ~600 | How to use framework |

**Components in framework:**
- `VCOCircuit` - Voltage-controlled oscillator
- `MoogLadderFilter` - Classic Moog filter
- `StateVariableFilter` - Multimode filter
- `AnalogADSR` - Envelope generator
- `LFO` - Low frequency oscillator
- `AnalogSynthVoice` - Complete synthesizer voice
- `PresetManager` - Save/load patches

### Node System

| File | Description | Lines | Purpose |
|------|-------------|-------|---------|
| `node_system.py` | Node engine | ~500 | Graph management & routing |
| `analog_nodes.py` | Node implementations | ~600 | Wrapper nodes for components |
| `node_examples.py` | Node examples | ~400 | Example patches |

**Available nodes:**
- **Oscillators**: OscillatorNode (VCO)
- **Filters**: MoogFilterNode, StateVariableFilterNode
- **Envelopes**: ADSRNode
- **Modulators**: LFONode
- **Utility**: MixerNode, GainNode, VCANode, ConstantNode
- **I/O**: MIDINoteNode, AudioOutputNode
- **Debug**: ScopeNode

### Visual Interface

| File | Description | Size | Purpose |
|------|-------------|------|---------|
| `node_editor.html` | Web-based editor | ~31KB | Interactive patch editor |

**Features:**
- Drag-and-drop nodes
- Visual connection routing
- Real-time parameter editing
- Patch save/load
- Professional UI

### Configuration

| File | Description | Purpose |
|------|-------------|---------|
| `requirements.txt` | Python dependencies | Package list |

---

## 🎯 Usage Patterns

### Pattern 1: Direct Framework (Simple)

```python
from analog_synth_framework import AnalogSynthVoice, midi_to_frequency

voice = AnalogSynthVoice(44100)
voice.osc1.set_parameter('waveform', 'saw')
voice.note_on(midi_to_frequency(60))
audio = voice.render(44100)
```

**Use when:**
- Simple sounds
- Single voice
- Quick experiments

### Pattern 2: Node System (Modular)

```python
from node_system import NodeGraph
from analog_nodes import *

graph = NodeGraph(44100)
# Add and connect nodes
outputs = graph.process(512)
```

**Use when:**
- Complex routing
- Modular patches
- Multiple voices
- Experimental designs

### Pattern 3: Visual Editor (Interactive)

Open `node_editor.html` in browser
- Drag nodes
- Connect visually
- Tweak parameters
- Export patch

**Use when:**
- Learning
- Experimenting
- Visualizing signal flow
- Quick prototyping

---

## 🎵 Example Sounds

After running the examples, you'll have these audio files:

### Framework Examples (`python3 examples.py`)
1. `example1_basic_note.wav` - Simple synthesizer note
2. `example2_bass_line.wav` - Sequenced bass line
3. `example3_pad_sound.wav` - Layered pad sound
4. `example4_filter_sweep.wav` - Automated filter sweep
5. `example5_preset_test.wav` - Preset demonstration
6. `example6_waveforms.png` - Waveform analysis
7. `example7_envelopes.png` - Envelope visualization

### Node Examples (`python3 node_examples.py`)
1. `node_example1_basic_synth.wav` - Basic monosynth
2. `node_example2_detuned.wav` - Detuned dual oscillator
3. `node_example3_lfo.wav` - LFO modulated filter

### Visualizations
- `circuit_analysis.png` - Complete circuit analysis

---

## 🎓 Learning Path

### Week 1: Basics
- [ ] Install everything ([GETTING_STARTED.md](GETTING_STARTED.md))
- [ ] Run all examples
- [ ] Create first sound with framework
- [ ] Explore visual editor
- [ ] Modify parameters

**Focus:** Understanding components and signal flow

### Week 2: Framework
- [ ] Read [QUICKSTART.md](QUICKSTART.md)
- [ ] Study `examples.py` code
- [ ] Create 5 different sounds
- [ ] Experiment with modulation
- [ ] Save presets

**Focus:** Mastering the framework

### Week 3: Node System
- [ ] Read [NODE_SYSTEM_README.md](NODE_SYSTEM_README.md)
- [ ] Study `node_examples.py` code
- [ ] Create patches in Python
- [ ] Use visual editor
- [ ] Connect complex routing

**Focus:** Modular thinking

### Week 4: Extension
- [ ] Read [EXTENSION_GUIDE.md](EXTENSION_GUIDE.md)
- [ ] Create custom circuit
- [ ] Design custom node
- [ ] Build an effect
- [ ] Contribute ideas

**Focus:** Creating new components

---

## 🛠️ Common Tasks

### Task: Create a Bass Sound

```python
from analog_synth_framework import AnalogSynthVoice, midi_to_frequency

voice = AnalogSynthVoice(44100)
voice.osc1.set_parameter('waveform', 'square')
voice.filter.set_parameter('cutoff', 400.0)
voice.filter.set_parameter('resonance', 0.85)
voice.amp_envelope.set_parameter('attack', 0.001)
voice.amp_envelope.set_parameter('decay', 0.15)

voice.note_on(midi_to_frequency(36))  # C2
audio = voice.render(44100)
```

### Task: Create a Lead Sound

```python
voice.osc1.set_parameter('waveform', 'saw')
voice.filter.set_parameter('cutoff', 3000.0)
voice.filter.set_parameter('resonance', 0.6)
voice.filter_env_amount = 1.5
voice.lfo_to_filter_amount = 0.15

voice.note_on(midi_to_frequency(69))  # A4
```

### Task: Add LFO Modulation

```python
from node_system import NodeGraph
from analog_nodes import *

graph = NodeGraph(44100)
lfo = LFONode(sample_rate=44100)
filter_node = MoogFilterNode(sample_rate=44100)

lfo.set_parameter('frequency', 4.0)
lfo.set_parameter('waveform', 'sine')

graph.add_node(lfo)
graph.add_node(filter_node)
graph.connect(lfo.node_id, 'output', filter_node.node_id, 'cutoff_mod')
```

### Task: Save a Preset

```python
from analog_synth_framework import PresetManager

pm = PresetManager()
pm.save_preset('My Lead', voice)
pm.export_presets('my_sounds.json')
```

---

## 🔧 Troubleshooting Quick Reference

| Problem | File to Check | Solution |
|---------|---------------|----------|
| Installation issues | [GETTING_STARTED.md](GETTING_STARTED.md) | Step-by-step install |
| No sound | [QUICKSTART.md](QUICKSTART.md) | Parameter guide |
| Framework usage | [README.md](README.md) | Overview & examples |
| Custom circuits | [EXTENSION_GUIDE.md](EXTENSION_GUIDE.md) | Creation guide |
| Node system | [NODE_SYSTEM_README.md](NODE_SYSTEM_README.md) | Node documentation |

---

## 📊 Feature Matrix

| Feature | Framework | Node System | Visual Editor |
|---------|-----------|-------------|---------------|
| Create sounds | ✅ Easy | ✅ Flexible | ✅ Interactive |
| Modular routing | ⚠️ Limited | ✅ Full | ✅ Visual |
| Learning curve | 🟢 Low | 🟡 Medium | 🟢 Low |
| Flexibility | 🟡 Medium | 🟢 High | 🟡 Medium |
| Prototyping | 🟢 Fast | 🟡 Medium | 🟢 Very Fast |
| Production | ✅ Ready | ✅ Ready | ⚠️ Frontend only |

**Legend:**
- 🟢 Best choice
- 🟡 Good choice
- ⚠️ Consider alternatives
- ✅ Supported
- ❌ Not supported

---

## 🎨 Use Cases

### Sound Design
- Synthesizer sounds
- Bass lines
- Pads and textures
- Lead sounds
- Effects

**Best tool:** Framework or Node System

### Learning DSP
- Understanding filters
- Envelope shaping
- Modulation
- Signal flow

**Best tool:** Visual Editor + Documentation

### Prototyping
- Quick experiments
- Testing ideas
- Parameter exploration

**Best tool:** Framework for speed, Visual Editor for learning

### Production
- Complete instruments
- Effects chains
- Polyphonic systems

**Best tool:** Node System for flexibility

### Education
- Teaching synthesis
- DSP courses
- Interactive demos

**Best tool:** Visual Editor + Examples

---

## 🚦 Quick Status Check

Run this to verify everything works:

```bash
# 1. Framework test
python3 -c "from analog_synth_framework import *; print('✅ Framework OK')"

# 2. Node test
python3 -c "from node_system import *; from analog_nodes import *; print('✅ Nodes OK')"

# 3. Dependencies
python3 -c "import numpy, scipy, matplotlib; print('✅ Dependencies OK')"

# 4. Generate test
python3 examples.py > /dev/null 2>&1 && echo "✅ Examples OK"
```

All should show ✅

---

## 📞 Support

### Self-Help Resources
1. Check [GETTING_STARTED.md](GETTING_STARTED.md) troubleshooting section
2. Review example code in `examples.py` and `node_examples.py`
3. Read relevant documentation file
4. Check code comments

### Debug Checklist
- [ ] Python 3.8+ installed?
- [ ] All dependencies installed?
- [ ] All files present?
- [ ] Using correct file paths?
- [ ] Sample rate consistent?

---

## 🎯 Quick Reference

### Key Concepts
- **Analog Circuit Behavior**: Digital modeling of analog circuits
- **Node System**: Modular patching like hardware synthesizers
- **Signal Types**: Audio (44.1kHz), Control (modulation), Gate (triggers)
- **Processing Order**: Topologically sorted for correct signal flow

### Common Parameters
- **Oscillator**: frequency, waveform, pulse_width
- **Filter**: cutoff, resonance, drive
- **Envelope**: attack, decay, sustain, release
- **LFO**: frequency, waveform, amplitude

### File Formats
- **.wav**: Audio output (16-bit PCM, 44.1kHz)
- **.json**: Presets and patches
- **.png**: Visualizations
- **.html**: Visual editor

---

## 📈 Version History

**v1.0** (February 2026)
- Initial release
- Complete framework
- Node system
- Visual editor
- Full documentation

---

## 📜 License

MIT License - Free to use, modify, and distribute

---

## 🙏 Acknowledgments

Built with:
- NumPy for computation
- SciPy for audio I/O
- Matplotlib for visualization
- Love for analog synthesis

Inspired by:
- Moog synthesizers
- Modular synthesis
- Max/MSP
- VCV Rack
- Reaktor

---

## 🎉 Let's Begin!

Ready to start? Go to **[GETTING_STARTED.md](GETTING_STARTED.md)** for complete setup instructions!

Questions about the framework? Check **[README.md](README.md)**

Want to create custom circuits? See **[EXTENSION_GUIDE.md](EXTENSION_GUIDE.md)**

Ready for modular synthesis? Read **[NODE_SYSTEM_README.md](NODE_SYSTEM_README.md)**

**Have fun creating amazing sounds! 🎛️🎵🔊**
