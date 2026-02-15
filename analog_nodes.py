"""
Analog Circuit Nodes
====================

Node implementations for all analog circuit components.
Each node wraps an AnalogComponent from the framework.
"""

import numpy as np
from node_system import (
    NodeBase, NodeFactory, SignalType, ParameterSmoother
)
from analog_synth_framework import (
    VCOCircuit, MoogLadderFilter, StateVariableFilter,
    AnalogADSR, LFO, midi_to_frequency
)


# ============================================================================
# OSCILLATOR NODES
# ============================================================================

@NodeFactory.register
class OscillatorNode(NodeBase):
    """
    Voltage-Controlled Oscillator (VCO) node.
    
    Generates audio waveforms with analog characteristics.
    """
    
    def __init__(self, node_id=None, sample_rate=44100.0):
        super().__init__(node_id, sample_rate)
        self.category = "Oscillators"
        self.description = "Analog-style oscillator with multiple waveforms"
        
        # Create the underlying circuit
        self.oscillator = VCOCircuit(sample_rate)
    
    def _setup_ports(self):
        # Inputs
        self.add_input_port("frequency", SignalType.CONTROL, default_value=440.0)
        self.add_input_port("fm_mod", SignalType.AUDIO, default_value=0.0)
        self.add_input_port("pwm_mod", SignalType.CONTROL, default_value=0.0)
        
        # Outputs
        self.add_output_port("output", SignalType.AUDIO)
    
    def _setup_parameters(self):
        self.parameters = {
            'waveform': 'saw',      # saw, square, triangle, sine
            'frequency': 440.0,     # Hz
            'pulse_width': 0.5,     # 0.0 to 1.0
            'detune': 0.0,         # semitones
            'drift_amount': 0.001,  # analog drift
        }
        
        # Parameter smoothers
        self._freq_smoother = ParameterSmoother(self.sample_rate, 0.001)
        self._pw_smoother = ParameterSmoother(self.sample_rate, 0.005)
    
    def process(self, buffer_size: int):
        # Get inputs
        freq_mod = self.get_input("frequency", buffer_size)
        fm_mod = self.get_input("fm_mod", buffer_size)
        pwm_mod = self.get_input("pwm_mod", buffer_size)
        
        # Update oscillator parameters
        base_freq = self.parameters['frequency']
        self.oscillator.set_parameter('waveform', self.parameters['waveform'])
        self.oscillator.set_parameter('drift_amount', self.parameters['drift_amount'])
        
        # Process with modulation
        output = np.zeros(buffer_size)
        
        for i in range(buffer_size):
            # Smooth frequency changes
            current_freq = self._freq_smoother.process(base_freq + freq_mod[i])
            self.oscillator.set_parameter('frequency', current_freq)
            
            # Pulse width modulation
            pw = self.parameters['pulse_width'] + pwm_mod[i]
            pw = np.clip(pw, 0.01, 0.99)
            smooth_pw = self._pw_smoother.process(pw)
            self.oscillator.set_parameter('pulse_width', smooth_pw)
            
            # Generate single sample
            sample = self.oscillator.process(fm_mod[i:i+1])
            output[i] = sample[0]
        
        return {'output': output}


# ============================================================================
# FILTER NODES
# ============================================================================

@NodeFactory.register
class MoogFilterNode(NodeBase):
    """
    Moog Ladder Filter node (4-pole lowpass).
    
    The classic warm, resonant filter with analog characteristics.
    """
    
    def __init__(self, node_id=None, sample_rate=44100.0):
        super().__init__(node_id, sample_rate)
        self.category = "Filters"
        self.description = "Moog Ladder Filter with non-linear saturation"
        
        self.filter = MoogLadderFilter(sample_rate)
    
    def _setup_ports(self):
        # Inputs
        self.add_input_port("input", SignalType.AUDIO, default_value=0.0)
        self.add_input_port("cutoff_mod", SignalType.CONTROL, default_value=0.0)
        self.add_input_port("resonance_mod", SignalType.CONTROL, default_value=0.0)
        
        # Outputs
        self.add_output_port("output", SignalType.AUDIO)
    
    def _setup_parameters(self):
        self.parameters = {
            'cutoff': 1000.0,      # Hz
            'resonance': 0.0,      # 0.0 to 1.0
            'drive': 1.0,          # 1.0 to 10.0
            'cutoff_mod_amount': 1.0,  # modulation depth
        }
        
        self._cutoff_smoother = ParameterSmoother(self.sample_rate, 0.005)
    
    def process(self, buffer_size: int):
        # Get inputs
        input_signal = self.get_input("input", buffer_size)
        cutoff_mod = self.get_input("cutoff_mod", buffer_size)
        resonance_mod = self.get_input("resonance_mod", buffer_size)
        
        # Update filter
        base_cutoff = self.parameters['cutoff']
        base_resonance = self.parameters['resonance']
        mod_amount = self.parameters['cutoff_mod_amount']
        
        self.filter.set_parameter('drive', self.parameters['drive'])
        
        output = np.zeros(buffer_size)
        
        for i in range(buffer_size):
            # Modulate cutoff
            modulated_cutoff = base_cutoff * (1.0 + mod_amount * cutoff_mod[i])
            modulated_cutoff = np.clip(modulated_cutoff, 20.0, self.sample_rate * 0.45)
            smooth_cutoff = self._cutoff_smoother.process(modulated_cutoff)
            
            # Modulate resonance
            modulated_res = base_resonance + resonance_mod[i]
            modulated_res = np.clip(modulated_res, 0.0, 1.0)
            
            self.filter.set_parameter('cutoff', smooth_cutoff)
            self.filter.set_parameter('resonance', modulated_res)
            
            # Process
            output[i] = self.filter.process(input_signal[i:i+1])[0]
        
        return {'output': output}


@NodeFactory.register
class StateVariableFilterNode(NodeBase):
    """
    State Variable Filter node (multimode).
    
    Provides lowpass, highpass, bandpass, and notch outputs.
    """
    
    def __init__(self, node_id=None, sample_rate=44100.0):
        super().__init__(node_id, sample_rate)
        self.category = "Filters"
        self.description = "Multimode filter with LP/HP/BP/Notch outputs"
        
        self.filter = StateVariableFilter(sample_rate)
    
    def _setup_ports(self):
        self.add_input_port("input", SignalType.AUDIO, default_value=0.0)
        self.add_input_port("cutoff_mod", SignalType.CONTROL, default_value=0.0)
        
        # Multiple outputs
        self.add_output_port("output", SignalType.AUDIO)
    
    def _setup_parameters(self):
        self.parameters = {
            'cutoff': 1000.0,
            'resonance': 0.0,
            'mode': 'lowpass',  # lowpass, highpass, bandpass, notch
        }
    
    def process(self, buffer_size: int):
        input_signal = self.get_input("input", buffer_size)
        cutoff_mod = self.get_input("cutoff_mod", buffer_size)
        
        base_cutoff = self.parameters['cutoff']
        self.filter.set_parameter('resonance', self.parameters['resonance'])
        self.filter.set_parameter('mode', self.parameters['mode'])
        
        output = np.zeros(buffer_size)
        
        for i in range(buffer_size):
            cutoff = base_cutoff + cutoff_mod[i] * 1000.0
            cutoff = np.clip(cutoff, 20.0, self.sample_rate * 0.45)
            self.filter.set_parameter('cutoff', cutoff)
            output[i] = self.filter.process(input_signal[i:i+1])[0]
        
        return {'output': output}


# ============================================================================
# ENVELOPE NODES
# ============================================================================

@NodeFactory.register
class ADSRNode(NodeBase):
    """
    ADSR Envelope Generator node.
    
    Generates envelope curves based on gate input.
    """
    
    def __init__(self, node_id=None, sample_rate=44100.0):
        super().__init__(node_id, sample_rate)
        self.category = "Envelopes"
        self.description = "Analog-style ADSR envelope generator"
        
        self.envelope = AnalogADSR(sample_rate)
    
    def _setup_ports(self):
        self.add_input_port("gate", SignalType.GATE, default_value=0.0)
        self.add_output_port("output", SignalType.CONTROL)
    
    def _setup_parameters(self):
        self.parameters = {
            'attack': 0.01,
            'decay': 0.1,
            'sustain': 0.7,
            'release': 0.3,
        }
        
        self._last_gate = False
    
    def process(self, buffer_size: int):
        gate_signal = self.get_input("gate", buffer_size)
        
        # Update envelope parameters
        self.envelope.set_parameter('attack', self.parameters['attack'])
        self.envelope.set_parameter('decay', self.parameters['decay'])
        self.envelope.set_parameter('sustain', self.parameters['sustain'])
        self.envelope.set_parameter('release', self.parameters['release'])
        
        output = np.zeros(buffer_size)
        
        for i in range(buffer_size):
            # Check for gate changes
            current_gate = gate_signal[i] > 0.5
            if current_gate != self._last_gate:
                self.envelope.trigger(current_gate)
                self._last_gate = current_gate
            
            # Generate envelope
            output[i] = self.envelope.process_sample()
        
        return {'output': output}


# ============================================================================
# LFO NODES
# ============================================================================

@NodeFactory.register
class LFONode(NodeBase):
    """
    Low Frequency Oscillator node.
    
    Generates modulation signals.
    """
    
    def __init__(self, node_id=None, sample_rate=44100.0):
        super().__init__(node_id, sample_rate)
        self.category = "Modulators"
        self.description = "Low frequency oscillator for modulation"
        
        self.lfo = LFO(sample_rate)
    
    def _setup_ports(self):
        self.add_input_port("rate_mod", SignalType.CONTROL, default_value=0.0)
        self.add_output_port("output", SignalType.CONTROL)
    
    def _setup_parameters(self):
        self.parameters = {
            'frequency': 1.0,
            'waveform': 'sine',  # sine, triangle, saw, square, random
            'amplitude': 1.0,
        }
    
    def process(self, buffer_size: int):
        rate_mod = self.get_input("rate_mod", buffer_size)
        
        # Update LFO
        self.lfo.set_parameter('waveform', self.parameters['waveform'])
        
        # Generate with rate modulation
        output = np.zeros(buffer_size)
        base_freq = self.parameters['frequency']
        amplitude = self.parameters['amplitude']
        
        # For simplicity, use average rate mod
        avg_rate_mod = np.mean(rate_mod)
        self.lfo.set_parameter('frequency', base_freq * (1.0 + avg_rate_mod))
        
        lfo_output = self.lfo.process(buffer_size)
        output = lfo_output * amplitude
        
        return {'output': output}


# ============================================================================
# UTILITY NODES
# ============================================================================

@NodeFactory.register
class MixerNode(NodeBase):
    """
    Audio mixer node with multiple inputs.
    """
    
    def __init__(self, node_id=None, sample_rate=44100.0, num_channels=4):
        self.num_channels = num_channels
        super().__init__(node_id, sample_rate)
        self.category = "Utility"
        self.description = f"Mix {num_channels} audio signals"
    
    def _setup_ports(self):
        for i in range(self.num_channels):
            self.add_input_port(f"input_{i+1}", SignalType.AUDIO, default_value=0.0)
        
        self.add_output_port("output", SignalType.AUDIO)
    
    def _setup_parameters(self):
        self.parameters = {
            f'level_{i+1}': 1.0 / self.num_channels
            for i in range(self.num_channels)
        }
        self.parameters['master_level'] = 1.0
    
    def process(self, buffer_size: int):
        # Mix all inputs
        output = np.zeros(buffer_size)
        
        for i in range(self.num_channels):
            input_signal = self.get_input(f"input_{i+1}", buffer_size)
            level = self.parameters[f'level_{i+1}']
            output += input_signal * level
        
        # Apply master level
        output *= self.parameters['master_level']
        
        return {'output': output}


@NodeFactory.register
class GainNode(NodeBase):
    """Simple gain/amplifier node."""
    
    def __init__(self, node_id=None, sample_rate=44100.0):
        super().__init__(node_id, sample_rate)
        self.category = "Utility"
        self.description = "Amplifier/attenuator with gain control"
    
    def _setup_ports(self):
        self.add_input_port("input", SignalType.AUDIO, default_value=0.0)
        self.add_input_port("gain_mod", SignalType.CONTROL, default_value=0.0)
        self.add_output_port("output", SignalType.AUDIO)
    
    def _setup_parameters(self):
        self.parameters = {
            'gain_db': 0.0,  # -60 to +24 dB
        }
    
    def process(self, buffer_size: int):
        input_signal = self.get_input("input", buffer_size)
        gain_mod = self.get_input("gain_mod", buffer_size)
        
        # Convert dB to linear
        gain_linear = 10.0 ** (self.parameters['gain_db'] / 20.0)
        
        # Apply gain with modulation
        output = input_signal * gain_linear * (1.0 + gain_mod)
        
        return {'output': output}


@NodeFactory.register
class VCANode(NodeBase):
    """
    Voltage-Controlled Amplifier.
    
    Multiplies audio by control signal.
    """
    
    def __init__(self, node_id=None, sample_rate=44100.0):
        super().__init__(node_id, sample_rate)
        self.category = "Utility"
        self.description = "Voltage-controlled amplifier"
    
    def _setup_ports(self):
        self.add_input_port("input", SignalType.AUDIO, default_value=0.0)
        self.add_input_port("control", SignalType.CONTROL, default_value=1.0)
        self.add_output_port("output", SignalType.AUDIO)
    
    def _setup_parameters(self):
        self.parameters = {}
    
    def process(self, buffer_size: int):
        input_signal = self.get_input("input", buffer_size)
        control_signal = self.get_input("control", buffer_size)
        
        output = input_signal * control_signal
        
        return {'output': output}


@NodeFactory.register
class AudioOutputNode(NodeBase):
    """
    Audio output node - marks the final output of the patch.
    """
    
    def __init__(self, node_id=None, sample_rate=44100.0):
        super().__init__(node_id, sample_rate)
        self.category = "I/O"
        self.description = "Audio output (DAC)"
        self.is_output = True
    
    def _setup_ports(self):
        self.add_input_port("left", SignalType.AUDIO, default_value=0.0)
        self.add_input_port("right", SignalType.AUDIO, default_value=0.0)
    
    def _setup_parameters(self):
        self.parameters = {
            'volume': 1.0,
        }
    
    def process(self, buffer_size: int):
        left = self.get_input("left", buffer_size)
        right = self.get_input("right", buffer_size)
        
        volume = self.parameters['volume']
        
        return {
            'left': left * volume,
            'right': right * volume,
        }


@NodeFactory.register
class MIDINoteNode(NodeBase):
    """
    MIDI Note input node.
    
    Converts MIDI note number to frequency and gate.
    """
    
    def __init__(self, node_id=None, sample_rate=44100.0):
        super().__init__(node_id, sample_rate)
        self.category = "I/O"
        self.description = "MIDI note to CV converter"
    
    def _setup_ports(self):
        self.add_output_port("frequency", SignalType.CONTROL)
        self.add_output_port("gate", SignalType.GATE)
        self.add_output_port("velocity", SignalType.CONTROL)
    
    def _setup_parameters(self):
        self.parameters = {
            'note': 60,        # MIDI note number
            'gate_on': False,  # Note on/off
            'velocity': 1.0,   # 0.0 to 1.0
        }
    
    def process(self, buffer_size: int):
        # Convert MIDI to frequency
        note = self.parameters['note']
        frequency = midi_to_frequency(note)
        
        # Generate outputs
        freq_out = np.full(buffer_size, frequency)
        gate_out = np.full(buffer_size, 1.0 if self.parameters['gate_on'] else 0.0)
        vel_out = np.full(buffer_size, self.parameters['velocity'])
        
        return {
            'frequency': freq_out,
            'gate': gate_out,
            'velocity': vel_out,
        }


@NodeFactory.register
class ConstantNode(NodeBase):
    """Constant value node."""
    
    def __init__(self, node_id=None, sample_rate=44100.0):
        super().__init__(node_id, sample_rate)
        self.category = "Utility"
        self.description = "Constant value source"
    
    def _setup_ports(self):
        self.add_output_port("output", SignalType.CONTROL)
    
    def _setup_parameters(self):
        self.parameters = {
            'value': 0.0,
        }
    
    def process(self, buffer_size: int):
        output = np.full(buffer_size, self.parameters['value'])
        return {'output': output}


@NodeFactory.register
class ScopeNode(NodeBase):
    """
    Oscilloscope node for viewing signals.
    Stores recent signal history.
    """
    
    def __init__(self, node_id=None, sample_rate=44100.0):
        super().__init__(node_id, sample_rate)
        self.category = "Debug"
        self.description = "Signal visualizer"
        self.history = np.zeros(sample_rate)  # 1 second history
        self.write_pos = 0
    
    def _setup_ports(self):
        self.add_input_port("input", SignalType.AUDIO, default_value=0.0)
        self.add_output_port("output", SignalType.AUDIO)  # Pass-through
    
    def _setup_parameters(self):
        self.parameters = {}
    
    def process(self, buffer_size: int):
        input_signal = self.get_input("input", buffer_size)
        
        # Store in history buffer
        for i in range(buffer_size):
            self.history[self.write_pos] = input_signal[i]
            self.write_pos = (self.write_pos + 1) % len(self.history)
        
        return {'output': input_signal}
    
    def get_history(self, num_samples: int = None):
        """Get recent signal history."""
        if num_samples is None:
            num_samples = len(self.history)
        
        num_samples = min(num_samples, len(self.history))
        
        # Read from circular buffer
        if self.write_pos >= num_samples:
            return self.history[self.write_pos - num_samples:self.write_pos]
        else:
            # Wrap around
            part1 = self.history[self.write_pos - num_samples:]
            part2 = self.history[:self.write_pos]
            return np.concatenate([part1, part2])
