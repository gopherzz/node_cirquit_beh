# Node-Based Analog Synthesis System

A complete modular node-based synthesis environment that lets you create synthesizers, effects, and complex signal processing chains by connecting nodes visually.

## 🎯 Overview

This system provides:
- **Visual Node Editor** - Web-based interface for creating patches
- **Python Backend** - Full synthesis engine with proper signal routing
- **Modular Architecture** - Mix and match components freely
- **Real-time Processing** - Efficient audio processing with topological sorting
- **Extensible Design** - Easy to add custom nodes

Think of it as a digital modular synthesizer - like VCV Rack, Max/MSP, or Reaktor - but built on our analog circuit modeling framework.

## 📁 Files

- **node_system.py** - Core node graph engine
- **analog_nodes.py** - Node implementations (oscillators, filters, etc.)
- **node_editor.html** - Interactive visual editor
- **node_examples.py** - Example patches with Python backend
- **NODE_TUTORIAL.md** - Comprehensive guide

## 🚀 Quick Start

### 1. Visual Editor (Web Interface)

Open `node_editor.html` in your browser:

```bash
open node_editor.html  # macOS
xdg-open node_editor.html  # Linux
start node_editor.html  # Windows
```

**Usage:**
- Click nodes in the library to add them
- Drag nodes to arrange
- Click port circles to connect (output → input)
- Click nodes to edit parameters in the right panel
- Right-click nodes to delete

### 2. Python Backend

Create patches programmatically:

```python
from node_system import NodeGraph
from analog_nodes import *

# Create graph
graph = NodeGraph(sample_rate=44100)

# Add nodes
midi = MIDINoteNode(sample_rate=44100)
osc = OscillatorNode(sample_rate=44100)
filter = MoogFilterNode(sample_rate=44100)
output = AudioOutputNode(sample_rate=44100)

graph.add_node(midi)
graph.add_node(osc)
graph.add_node(filter)
graph.add_node(output)

# Connect nodes
graph.connect(midi.node_id, 'frequency', osc.node_id, 'frequency')
graph.connect(osc.node_id, 'output', filter.node_id, 'input')
graph.connect(filter.node_id, 'output', output.node_id, 'left')

# Configure parameters
osc.set_parameter('waveform', 'saw')
filter.set_parameter('cutoff', 1000.0)
midi.set_parameter('note', 60)
midi.set_parameter('gate_on', True)

# Render audio
outputs = graph.process(buffer_size=512)
```

## 🎛️ Available Nodes

### Oscillators
- **OscillatorNode (VCO)** - Analog oscillator with multiple waveforms
  - Inputs: frequency, fm_mod, pwm_mod
  - Outputs: output
  - Parameters: waveform, frequency, pulse_width, drift

### Filters
- **MoogFilterNode** - 4-pole ladder filter with resonance
  - Inputs: input, cutoff_mod, resonance_mod
  - Outputs: output
  - Parameters: cutoff, resonance, drive

- **StateVariableFilterNode** - Multimode filter (LP/HP/BP/Notch)
  - Inputs: input, cutoff_mod
  - Outputs: output
  - Parameters: cutoff, resonance, mode

### Envelopes
- **ADSRNode** - Envelope generator
  - Inputs: gate
  - Outputs: output (control signal)
  - Parameters: attack, decay, sustain, release

### Modulators
- **LFONode** - Low frequency oscillator
  - Inputs: rate_mod
  - Outputs: output (control signal)
  - Parameters: frequency, waveform, amplitude

### Utility
- **MixerNode** - 4-channel mixer
  - Inputs: input_1, input_2, input_3, input_4
  - Outputs: output
  - Parameters: level_1, level_2, level_3, level_4, master_level

- **GainNode** - Amplifier/attenuator
  - Inputs: input, gain_mod
  - Outputs: output
  - Parameters: gain_db

- **VCANode** - Voltage-controlled amplifier
  - Inputs: input, control
  - Outputs: output
  - Multiplies audio by control signal

- **ConstantNode** - Constant value source
  - Outputs: output
  - Parameters: value

### I/O
- **MIDINoteNode** - MIDI note input
  - Outputs: frequency, gate, velocity
  - Parameters: note (0-127), gate_on, velocity

- **AudioOutputNode** - Final audio output
  - Inputs: left, right
  - Parameters: volume

### Debug
- **ScopeNode** - Signal visualizer
  - Inputs: input
  - Outputs: output (pass-through)
  - Stores signal history for visualization

## 🔧 Creating Custom Nodes

### Step 1: Define Node Class

```python
from node_system import NodeBase, NodeFactory, SignalType
import numpy as np

@NodeFactory.register
class MyCustomNode(NodeBase):
    """My custom signal processor."""
    
    def __init__(self, node_id=None, sample_rate=44100.0):
        super().__init__(node_id, sample_rate)
        self.category = "Effects"
        self.description = "Custom effect"
    
    def _setup_ports(self):
        """Define inputs and outputs."""
        self.add_input_port("input", SignalType.AUDIO, default_value=0.0)
        self.add_output_port("output", SignalType.AUDIO)
    
    def _setup_parameters(self):
        """Define user-adjustable parameters."""
        self.parameters = {
            'amount': 0.5,
            'mix': 1.0,
        }
    
    def process(self, buffer_size: int):
        """Process audio."""
        input_signal = self.get_input("input", buffer_size)
        amount = self.parameters['amount']
        
        # Your DSP code here
        output = input_signal * amount
        
        return {'output': output}
```

### Step 2: Use in Patches

```python
# Automatically available!
node = MyCustomNode(sample_rate=44100)
graph.add_node(node)
```

### Step 3: Add to Visual Editor

Edit `node_editor.html`:

```html
<button class="node-button" onclick="addNode('MyCustomNode')">
    My Effect
</button>
```

And add template:

```javascript
MyCustomNode: {
    name: 'My Effect',
    color: '#FF6B9D',
    inputs: ['input'],
    outputs: ['output'],
    params: {
        amount: { type: 'range', min: 0, max: 1, step: 0.01, default: 0.5 },
        mix: { type: 'range', min: 0, max: 1, step: 0.01, default: 1 },
    }
}
```

## 💡 Example Patches

### Basic Synthesizer

```
MIDI Note → VCO → Moog Filter → VCA → Audio Out
              ↑         ↑         ↑
            Freq     Filter Env  Amp Env
                        ↑         ↑
                      Gate      Gate
```

```python
# See node_examples.py - example_1_basic_synth()
```

### Detuned Lead

```
              ┌→ VCO 1 (saw) ┐
MIDI Note →   |              | → Mixer → Filter → VCA → Out
              └→ VCO 2 (sqr) ┘            ↑      ↑
                                       Env    Env
```

### Acid Bass with LFO

```
MIDI Note → VCO → Filter → VCA → Out
                     ↑      ↑
                   LFO    Env
```

## 🎨 Signal Types

The system uses different signal types for proper routing:

- **AUDIO** - Audio rate signals (44.1kHz)
- **CONTROL** - Control rate signals (envelopes, LFOs)
- **GATE** - Gate/trigger signals (note on/off)
- **MIDI** - MIDI-style data

## 🔄 How It Works

### 1. Graph Management

The `NodeGraph` class manages:
- Node connections
- Cycle detection (prevents feedback loops)
- Topological sorting (correct processing order)
- Signal routing between nodes

### 2. Processing Order

Nodes are processed in topological order:

```
Input → Process → Output → Next Node
   ↑                ↓
   └────────────────┘
   (topologically sorted)
```

### 3. Buffer Processing

Audio is processed in chunks:

```python
chunk_size = 512  # samples
for i in range(0, total_samples, chunk_size):
    outputs = graph.process(chunk_size)
```

### 4. Connection Routing

When nodes are connected:
```python
graph.connect(source_id, 'output_port', dest_id, 'input_port')
```

The graph automatically routes the source's output buffer to the destination's input buffer before processing.

## 📊 Performance

- **CPU Efficient** - Optimized processing order
- **Memory Efficient** - Reuses buffers where possible
- **Real-time Capable** - 512-sample buffers at 44.1kHz
- **Scalable** - Handles complex patches with 50+ nodes

Typical performance (Python, single-threaded):
- Simple patch (5 nodes): ~1% CPU
- Medium patch (20 nodes): ~5% CPU
- Complex patch (50 nodes): ~15% CPU

## 🐛 Debugging

### Check Patch Structure

```python
print(graph.get_info())
```

Output:
```
Patch: My Patch
Nodes: 7
Connections: 9

Node List:
  - OscillatorNode (abc123...)
    Inputs: ['frequency', 'fm_mod']
    Outputs: ['output']
  ...
```

### Visualize Signal Flow

Use `ScopeNode`:

```python
scope = ScopeNode(sample_rate=44100)
graph.add_node(scope)
graph.connect(source.node_id, 'output', scope.node_id, 'input')

# After processing
history = scope.get_history(4410)  # Last 0.1 seconds
plt.plot(history)
```

### Common Issues

**No sound output?**
- Check all nodes are connected
- Verify AudioOutputNode has inputs
- Check parameter values (not all zero?)

**Clicking/pops?**
- Use parameter smoothing
- Check envelope times aren't too short
- Verify no discontinuities

**Wrong sound?**
- Print parameter values
- Check signal flow with scope nodes
- Verify connection order

## 🎓 Advanced Topics

### Custom Signal Routing

Create complex patches:

```python
# Parallel processing
osc1_out = osc1.process(buffer_size)
osc2_out = osc2.process(buffer_size)
mixed = (osc1_out['output'] + osc2_out['output']) / 2
```

### Feedback (Advanced)

While the graph prevents cycles, you can implement feedback manually:

```python
class FeedbackDelayNode(NodeBase):
    def __init__(self, ...):
        self.delay_buffer = np.zeros(44100)  # 1 second
        self.write_pos = 0
    
    def process(self, buffer_size):
        # Read from delay, mix with input, write back
        ...
```

### Polyphony

Create multiple voices:

```python
voices = [create_voice_graph() for _ in range(8)]

# Allocate notes to voices
def note_on(note_number):
    free_voice = find_free_voice()
    free_voice.trigger(note_number)
```

### External Control

Interface with MIDI, OSC, or other control sources:

```python
import mido

midi_port = mido.open_input()
for msg in midi_port:
    if msg.type == 'note_on':
        midi_node.set_parameter('note', msg.note)
        midi_node.set_parameter('gate_on', True)
```

## 📚 Resources

- **analog_synth_framework.py** - Underlying circuit models
- **EXTENSION_GUIDE.md** - Creating custom circuits
- **node_examples.py** - Working code examples

## 🎹 Tips for Great Patches

### 1. Layer Oscillators
```
Multiple VCOs slightly detuned → Mixer → Filter
```
Creates thick, rich sounds

### 2. Envelope Everything
```
Envelope → Filter Cutoff
Envelope → Amplitude
Envelope → Oscillator Pitch
```
Brings sounds to life

### 3. Modulate Modulation
```
LFO 1 → LFO 2 Rate → Filter Cutoff
```
Complex, evolving textures

### 4. Use Feedback Carefully
```
Filter → Delay → Mix back to Filter Input
```
Can create interesting resonances (use carefully!)

### 5. Experiment with Routing
The beauty of modular synthesis is unusual routing:
```
Envelope → Oscillator Frequency  # Pitch envelopes
LFO → Envelope Attack Time       # Moving envelopes
Audio → Filter Cutoff Mod        # Audio-rate modulation
```

## 🤝 Contributing

Want to add nodes? The system is designed for easy extension:

1. Create node class in `analog_nodes.py`
2. Register with `@NodeFactory.register`
3. Add to visual editor template
4. Document in this README

## 📄 License

MIT License - Same as the main framework

---

**Happy Patching! 🎛️🔊**

Build anything from classic subtractive synths to experimental sound design - the power is in your hands!
