# Analog Circuit Framework - Extension Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Core Architecture](#core-architecture)
3. [Creating Custom Analog Components](#creating-custom-analog-components)
4. [Advanced Circuit Modeling Techniques](#advanced-circuit-modeling-techniques)
5. [Integration Guide](#integration-guide)
6. [Examples](#examples)

---

## Introduction

This framework simulates analog circuit behavior using Digital Signal Processing (DSP) techniques. It models the non-linear characteristics of electronic components, providing authentic vintage synthesizer sound.

### Key Concepts

**Virtual Analog (VA) Synthesis**: Digital recreation of analog circuits using mathematical models that capture:
- Non-linear behavior (saturation, distortion)
- Component tolerances and drift
- Zero-delay feedback loops
- Thermal effects

**Band-Limited Synthesis**: Anti-aliasing techniques that prevent digital artifacts when generating waveforms with sharp discontinuities.

---

## Core Architecture

### Component Hierarchy

```
AnalogComponent (Abstract Base Class)
    ├── Oscillators (VCOCircuit, etc.)
    ├── Filters (MoogLadderFilter, StateVariableFilter, etc.)
    ├── Envelopes (AnalogADSR, etc.)
    └── Modulators (LFO, etc.)
```

### Base Class Structure

Every analog component inherits from `AnalogComponent` and must implement:

- `__init__(sample_rate)`: Initialize with sample rate
- `process(input_signal)`: Process audio samples
- `reset()`: Reset internal state
- `_parameters`: User-adjustable parameters
- `_state`: Internal circuit state variables

---

## Creating Custom Analog Components

### Step 1: Define Your Component Class

```python
from analog_synth_framework import AnalogComponent
import numpy as np

class MyCustomCircuit(AnalogComponent):
    """
    Brief description of what this circuit does.
    
    This docstring should explain:
    - The analog circuit being modeled
    - Its behavior and characteristics
    - Available parameters
    """
    
    def __init__(self, sample_rate: float = 44100.0):
        super().__init__(sample_rate)
        
        # Define user-adjustable parameters
        self._parameters = {
            'param1': default_value1,
            'param2': default_value2,
        }
        
        # Define internal state variables
        self._state = {
            'state_var1': 0.0,
            'state_var2': 0.0,
        }
```

### Step 2: Implement Required Methods

#### Reset Method
```python
def reset(self):
    """Reset circuit to initial state."""
    self._state['state_var1'] = 0.0
    self._state['state_var2'] = 0.0
```

#### Process Method
```python
def process(self, input_signal: np.ndarray) -> np.ndarray:
    """
    Process audio through the circuit.
    
    Parameters:
    -----------
    input_signal : np.ndarray
        Input audio samples
        
    Returns:
    --------
    np.ndarray : Processed audio
    """
    output = np.zeros_like(input_signal)
    
    for i in range(len(input_signal)):
        # Your circuit simulation logic here
        output[i] = self._simulate_one_sample(input_signal[i])
    
    return output
```

### Step 3: Add Circuit-Specific Methods

```python
def _simulate_one_sample(self, input_sample: float) -> float:
    """Simulate one sample through the circuit."""
    # Access parameters
    param1 = self._parameters['param1']
    
    # Read current state
    state = self._state['state_var1']
    
    # Perform circuit calculation
    output = input_sample * param1 + state
    
    # Update state
    self._state['state_var1'] = output * 0.5
    
    return output
```

---

## Advanced Circuit Modeling Techniques

### 1. Non-Linear Saturation

Analog circuits exhibit saturation when signals exceed component limits. Model this with soft-clipping functions:

```python
def _soft_clip_tanh(self, x: float, drive: float = 1.0) -> float:
    """
    Hyperbolic tangent saturation (models transistor/tube behavior).
    
    Parameters:
    -----------
    x : float
        Input signal
    drive : float
        Amount of saturation (1.0 = linear, higher = more saturation)
    """
    return np.tanh(x * drive)

def _soft_clip_polynomial(self, x: float) -> float:
    """
    Polynomial soft clipping (computationally cheaper).
    """
    x = np.clip(x, -1.5, 1.5)
    if abs(x) < 1.0:
        return x
    return np.sign(x) * (1.0 - (2.0 - abs(x))**2 / 3.0)
```

### 2. One-Pole Filter (RC Circuit)

The fundamental building block of many analog filters:

```python
class OnePoleFilter(AnalogComponent):
    """
    Simple one-pole lowpass filter (models RC circuit).
    
    Transfer function: H(s) = 1 / (1 + s*RC)
    """
    
    def __init__(self, sample_rate: float = 44100.0):
        super().__init__(sample_rate)
        self._parameters = {
            'cutoff': 1000.0,  # Hz
        }
        self._state = {
            'z1': 0.0,  # Previous output
        }
    
    def reset(self):
        self._state['z1'] = 0.0
    
    def process(self, input_signal: np.ndarray) -> np.ndarray:
        output = np.zeros_like(input_signal)
        cutoff = self._parameters['cutoff']
        
        # Calculate coefficient using bilinear transform
        fc = cutoff / self.sample_rate
        b = 2.0 - np.cos(2.0 * np.pi * fc)
        a = b - np.sqrt(b * b - 1.0)
        
        for i in range(len(input_signal)):
            # Apply difference equation
            output[i] = a * input_signal[i] + (1.0 - a) * self._state['z1']
            self._state['z1'] = output[i]
        
        return output
```

### 3. Zero-Delay Feedback (ZDF)

Essential for accurate filter modeling with feedback loops:

```python
class ZDFOnePole(AnalogComponent):
    """
    Zero-delay feedback one-pole filter.
    More accurate than traditional IIR, especially at high cutoff frequencies.
    """
    
    def __init__(self, sample_rate: float = 44100.0):
        super().__init__(sample_rate)
        self._parameters = {'cutoff': 1000.0}
        self._state = {'s': 0.0}  # Integrator state
    
    def reset(self):
        self._state['s'] = 0.0
    
    def process(self, input_signal: np.ndarray) -> np.ndarray:
        output = np.zeros_like(input_signal)
        cutoff = self._parameters['cutoff']
        
        # Compute g coefficient (TPT - Topology Preserving Transform)
        fc = cutoff / self.sample_rate
        g = np.tan(np.pi * fc)
        
        for i in range(len(input_signal)):
            # Zero-delay feedback calculation
            v = (input_signal[i] - self._state['s']) * g / (1.0 + g)
            lp = v + self._state['s']
            
            # Update state
            self._state['s'] = lp + v
            
            output[i] = lp
        
        return output
```

### 4. Analog Component Tolerances

Add realistic component drift and variation:

```python
class DriftingOscillator(VCOCircuit):
    """Oscillator with analog-style frequency drift."""
    
    def __init__(self, sample_rate: float = 44100.0):
        super().__init__(sample_rate)
        self._parameters['temperature_drift'] = 0.001
        self._state['temperature_lfo_phase'] = 0.0
        self._state['random_offset'] = np.random.uniform(-0.0005, 0.0005)
    
    def _apply_drift(self, frequency: float) -> float:
        """Apply temperature drift and component tolerances."""
        # Temperature drift (very slow)
        temp_lfo = np.sin(2.0 * np.pi * self._state['temperature_lfo_phase'])
        temp_drift = 1.0 + self._parameters['temperature_drift'] * temp_lfo
        
        # Component tolerance (fixed random offset)
        tolerance = 1.0 + self._state['random_offset']
        
        # Update temperature LFO (0.01 Hz)
        self._state['temperature_lfo_phase'] += 0.01 * self.dt
        if self._state['temperature_lfo_phase'] >= 1.0:
            self._state['temperature_lfo_phase'] -= 1.0
        
        return frequency * temp_drift * tolerance
```

### 5. Oversampling for Non-Linear Processes

When applying heavy non-linear processing, oversample to prevent aliasing:

```python
class OversampledDistortion(AnalogComponent):
    """
    Distortion with 2x oversampling to reduce aliasing.
    """
    
    def __init__(self, sample_rate: float = 44100.0):
        super().__init__(sample_rate)
        self._parameters = {
            'drive': 1.0,
            'mix': 1.0,
        }
        self._oversample_rate = sample_rate * 2.0
        
    def reset(self):
        pass
    
    def _upsample(self, signal: np.ndarray) -> np.ndarray:
        """Simple 2x upsampling with linear interpolation."""
        upsampled = np.zeros(len(signal) * 2)
        upsampled[::2] = signal
        upsampled[1::2] = (signal + np.roll(signal, -1)) / 2.0
        return upsampled
    
    def _downsample(self, signal: np.ndarray) -> np.ndarray:
        """Simple 2x downsampling."""
        return signal[::2]
    
    def _distortion(self, x: float, drive: float) -> float:
        """Non-linear distortion function."""
        return np.tanh(x * drive)
    
    def process(self, input_signal: np.ndarray) -> np.ndarray:
        drive = self._parameters['drive']
        mix = np.clip(self._parameters['mix'], 0.0, 1.0)
        
        # Upsample
        upsampled = self._upsample(input_signal)
        
        # Apply distortion at higher sample rate
        distorted = np.array([self._distortion(s, drive) for s in upsampled])
        
        # Downsample
        output = self._downsample(distorted)
        
        # Mix with dry signal
        output = mix * output + (1.0 - mix) * input_signal
        
        return output
```

---

## Integration Guide

### Adding Your Component to a Voice

#### Method 1: Direct Integration

```python
from analog_synth_framework import AnalogSynthVoice

class ExtendedSynthVoice(AnalogSynthVoice):
    """Synth voice with custom component."""
    
    def __init__(self, sample_rate: float = 44100.0):
        super().__init__(sample_rate)
        
        # Add your custom component
        self.my_circuit = MyCustomCircuit(sample_rate)
        
    def render(self, buffer_size: int) -> np.ndarray:
        """Render with custom circuit in signal chain."""
        # Get basic synthesis output
        output = super().render(buffer_size)
        
        # Process through your custom circuit
        output = self.my_circuit.process(output)
        
        return output
```

#### Method 2: Replace Existing Components

```python
from analog_synth_framework import AnalogSynthVoice

class CustomFilterVoice(AnalogSynthVoice):
    """Voice using a custom filter instead of Moog ladder."""
    
    def __init__(self, sample_rate: float = 44100.0):
        super().__init__(sample_rate)
        
        # Replace the filter
        self.filter = MyCustomFilter(sample_rate)
```

### Creating a New Circuit Category

```python
# In your extension file

class EffectsProcessor(AnalogComponent):
    """Base class for effects processors."""
    
    def __init__(self, sample_rate: float = 44100.0):
        super().__init__(sample_rate)
        self._parameters = {
            'wet_dry_mix': 0.5,
            'bypass': False,
        }
    
    def process(self, input_signal: np.ndarray) -> np.ndarray:
        if self._parameters['bypass']:
            return input_signal
        
        wet = self._process_effect(input_signal)
        mix = self._parameters['wet_dry_mix']
        
        return mix * wet + (1.0 - mix) * input_signal
    
    @abstractmethod
    def _process_effect(self, input_signal: np.ndarray) -> np.ndarray:
        """Override this in your effect."""
        pass


class AnalogChorus(EffectsProcessor):
    """Analog-style chorus effect."""
    
    def __init__(self, sample_rate: float = 44100.0):
        super().__init__(sample_rate)
        self._parameters.update({
            'rate': 0.5,
            'depth': 0.5,
        })
        self._state = {
            'buffer': np.zeros(int(sample_rate * 0.05)),  # 50ms delay line
            'write_pos': 0,
            'lfo_phase': 0.0,
        }
    
    def reset(self):
        self._state['buffer'] = np.zeros_like(self._state['buffer'])
        self._state['write_pos'] = 0
        self._state['lfo_phase'] = 0.0
    
    def _process_effect(self, input_signal: np.ndarray) -> np.ndarray:
        output = np.zeros_like(input_signal)
        buffer = self._state['buffer']
        buffer_size = len(buffer)
        
        rate = self._parameters['rate']
        depth = self._parameters['depth']
        
        for i in range(len(input_signal)):
            # Write to delay buffer
            buffer[self._state['write_pos']] = input_signal[i]
            
            # Calculate modulated delay time
            lfo = np.sin(2.0 * np.pi * self._state['lfo_phase'])
            delay_samples = 0.02 * self.sample_rate * (1.0 + depth * lfo)
            
            # Read from buffer with interpolation
            read_pos = (self._state['write_pos'] - int(delay_samples)) % buffer_size
            frac = delay_samples - int(delay_samples)
            
            sample1 = buffer[read_pos]
            sample2 = buffer[(read_pos - 1) % buffer_size]
            delayed = sample1 + frac * (sample2 - sample1)
            
            output[i] = delayed
            
            # Update positions
            self._state['write_pos'] = (self._state['write_pos'] + 1) % buffer_size
            self._state['lfo_phase'] += rate * self.dt
            if self._state['lfo_phase'] >= 1.0:
                self._state['lfo_phase'] -= 1.0
        
        return output
```

---

## Examples

### Example 1: Simple Distortion Circuit

```python
from analog_synth_framework import AnalogComponent
import numpy as np

class DiodeClipper(AnalogComponent):
    """
    Models a diode clipping circuit (like in guitar distortion pedals).
    """
    
    def __init__(self, sample_rate: float = 44100.0):
        super().__init__(sample_rate)
        self._parameters = {
            'threshold': 0.3,  # Clipping threshold
            'drive': 1.0,      # Input gain
        }
        self._state = {}
    
    def reset(self):
        pass
    
    def _diode_model(self, x: float, threshold: float) -> float:
        """
        Exponential diode model.
        Conducts when voltage exceeds threshold.
        """
        if x > threshold:
            return threshold + (1.0 - np.exp(-(x - threshold))) * 0.1
        elif x < -threshold:
            return -threshold - (1.0 - np.exp(-(-x - threshold))) * 0.1
        return x
    
    def process(self, input_signal: np.ndarray) -> np.ndarray:
        output = np.zeros_like(input_signal)
        threshold = self._parameters['threshold']
        drive = self._parameters['drive']
        
        for i in range(len(input_signal)):
            # Apply input gain
            driven = input_signal[i] * drive
            
            # Apply diode clipping
            clipped = self._diode_model(driven, threshold)
            
            # Output with compensation
            output[i] = clipped / drive
        
        return output


# Usage
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    # Create test signal
    sample_rate = 44100
    duration = 0.1
    t = np.linspace(0, duration, int(sample_rate * duration))
    test_signal = np.sin(2 * np.pi * 440 * t)
    
    # Process through distortion
    distortion = DiodeClipper(sample_rate)
    distortion.set_parameter('drive', 5.0)
    output = distortion.process(test_signal)
    
    # Plot
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(t[:500], test_signal[:500], label='Input')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(2, 1, 2)
    plt.plot(t[:500], output[:500], label='Output', color='red')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('/home/claude/distortion_example.png')
```

### Example 2: Sample & Hold Circuit

```python
class SampleAndHold(AnalogComponent):
    """
    Sample & Hold circuit - captures and holds input value.
    Commonly used for random stepped modulation.
    """
    
    def __init__(self, sample_rate: float = 44100.0):
        super().__init__(sample_rate)
        self._parameters = {
            'rate': 10.0,  # Sample rate in Hz
        }
        self._state = {
            'held_value': 0.0,
            'phase': 0.0,
        }
    
    def reset(self):
        self._state['held_value'] = 0.0
        self._state['phase'] = 0.0
    
    def process(self, input_signal: np.ndarray) -> np.ndarray:
        output = np.zeros_like(input_signal)
        rate = self._parameters['rate']
        
        for i in range(len(input_signal)):
            # Check if it's time to sample
            if self._state['phase'] >= 1.0:
                self._state['held_value'] = input_signal[i]
                self._state['phase'] = 0.0
            
            output[i] = self._state['held_value']
            
            # Update phase
            self._state['phase'] += rate * self.dt
        
        return output
```

### Example 3: Ring Modulator

```python
class RingModulator(AnalogComponent):
    """
    Ring modulator - multiplies two signals together.
    Creates inharmonic sidebands for bell-like tones.
    """
    
    def __init__(self, sample_rate: float = 44100.0):
        super().__init__(sample_rate)
        self._parameters = {
            'carrier_freq': 440.0,
            'mix': 1.0,
        }
        self._state = {
            'carrier_phase': 0.0,
        }
    
    def reset(self):
        self._state['carrier_phase'] = 0.0
    
    def process(self, input_signal: np.ndarray) -> np.ndarray:
        output = np.zeros_like(input_signal)
        freq = self._parameters['carrier_freq']
        mix = np.clip(self._parameters['mix'], 0.0, 1.0)
        
        for i in range(len(input_signal)):
            # Generate carrier
            carrier = np.sin(2.0 * np.pi * self._state['carrier_phase'])
            
            # Ring modulation
            modulated = input_signal[i] * carrier
            
            # Mix
            output[i] = mix * modulated + (1.0 - mix) * input_signal[i]
            
            # Update phase
            self._state['carrier_phase'] += freq * self.dt
            if self._state['carrier_phase'] >= 1.0:
                self._state['carrier_phase'] -= 1.0
        
        return output
```

---

## Best Practices

### 1. Parameter Validation

Always validate and clip parameters to safe ranges:

```python
def process(self, input_signal: np.ndarray) -> np.ndarray:
    # Validate parameters
    cutoff = np.clip(self._parameters['cutoff'], 20.0, self.sample_rate * 0.45)
    resonance = np.clip(self._parameters['resonance'], 0.0, 1.0)
    
    # ... rest of processing
```

### 2. State Management

Keep state variables organized and document their purpose:

```python
self._state = {
    'z1': 0.0,          # Previous output sample
    'z2': 0.0,          # Two samples ago
    'integrator': 0.0,  # Integrator accumulator
}
```

### 3. Performance Optimization

For real-time use, vectorize operations when possible:

```python
# Slow: Loop over samples
for i in range(len(input_signal)):
    output[i] = input_signal[i] * gain

# Fast: Vectorized operation
output = input_signal * gain
```

### 4. Documentation

Document the circuit behavior and reference papers:

```python
class MyFilter(AnalogComponent):
    """
    Digital model of the XYZ analog filter.
    
    References:
    -----------
    [1] Author et al., "Paper Title", Conference, Year
    [2] Book Title, Chapter X
    
    Circuit Description:
    -------------------
    This filter uses a ladder topology with zero-delay feedback...
    """
```

### 5. Testing

Always test your components with various inputs:

```python
def test_my_circuit():
    circuit = MyCustomCircuit(44100)
    
    # Test with DC
    dc_input = np.ones(1000)
    dc_output = circuit.process(dc_input)
    assert np.all(np.isfinite(dc_output)), "Output contains NaN or Inf"
    
    # Test with sine wave
    t = np.linspace(0, 1, 44100)
    sine = np.sin(2 * np.pi * 440 * t)
    output = circuit.process(sine)
    
    # Check for stability
    assert np.max(np.abs(output)) < 100, "Output is unstable"
```

---

## Troubleshooting Common Issues

### Issue 1: Instability / Explosion

**Symptoms**: Output goes to infinity or NaN

**Solutions**:
- Check feedback loops for instability
- Limit filter coefficients (cutoff < 0.45 * sample_rate)
- Add soft clipping to prevent runaway values
- Use double precision for accumulating values

```python
# Add safety clipping
output[i] = np.clip(calculation_result, -10.0, 10.0)
```

### Issue 2: Zipper Noise

**Symptoms**: Clicking when parameters change

**Solutions**:
- Smooth parameter changes with one-pole filters

```python
class SmoothedParameter:
    def __init__(self, sample_rate, time_constant=0.001):
        self.sample_rate = sample_rate
        self.time_constant = time_constant
        self.current_value = 0.0
        self.coef = np.exp(-1.0 / (time_constant * sample_rate))
    
    def process(self, target_value):
        self.current_value = target_value + (self.current_value - target_value) * self.coef
        return self.current_value
```

### Issue 3: Aliasing

**Symptoms**: High-frequency noise, harshness

**Solutions**:
- Use band-limited waveform generation
- Apply oversampling for non-linear processes
- Low-pass filter modulation signals

---

## Additional Resources

### Papers & Books

1. Välimäki & Huovilainen - "Oscillator and Filter Algorithms for Virtual Analog Synthesis"
2. Julius O. Smith - "Physical Audio Signal Processing"
3. Zavalishin - "The Art of VA Filter Design"

### Online Resources

- KVR Audio Developer Forum
- musicdsp.org
- The Audio Programmer community

---

## Support & Contributing

For issues or questions, please refer to the main framework documentation or community forums.

Happy circuit building! 🎛️🔊
