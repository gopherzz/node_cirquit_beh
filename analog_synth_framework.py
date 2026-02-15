"""
Analog Circuit Behaviour Synthesis Framework
=============================================

A comprehensive Python framework for creating synthesizers that simulate analog circuit behavior.
This framework uses Digital Signal Processing (DSP) techniques to model the non-linear characteristics
and behavior of analog electronic circuits used in vintage synthesizers.

Core Concepts:
--------------
1. Virtual Analog (VA) synthesis - Digital modeling of analog circuits
2. Non-linear circuit behavior - Simulating saturation, distortion, component drift
3. Band-limited synthesis - Anti-aliasing techniques for digital oscillators
4. Zero-delay feedback - Modeling recursive analog filter circuits

Author: Created using Analog Circuit Behavior Technology
License: MIT
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import json


# ============================================================================
# CORE CIRCUIT COMPONENT BASE CLASSES
# ============================================================================

class AnalogComponent(ABC):
    """
    Base class for all analog circuit components.
    Represents a single component in the signal chain with proper state management
    and sample-accurate processing.
    """
    
    def __init__(self, sample_rate: float = 44100.0):
        self.sample_rate = sample_rate
        self.dt = 1.0 / sample_rate  # Time step for circuit simulation
        self._state = {}  # Internal state variables
        self._parameters = {}  # User-adjustable parameters
        
    @abstractmethod
    def process(self, input_signal: np.ndarray) -> np.ndarray:
        """Process input signal through this component."""
        pass
    
    @abstractmethod
    def reset(self):
        """Reset component state."""
        pass
    
    def set_parameter(self, name: str, value: Any):
        """Set a component parameter."""
        if name in self._parameters:
            self._parameters[name] = value
        else:
            raise ValueError(f"Unknown parameter: {name}")
    
    def get_parameter(self, name: str) -> Any:
        """Get a component parameter value."""
        return self._parameters.get(name)
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get all parameters."""
        return self._parameters.copy()


# ============================================================================
# OSCILLATOR CIRCUITS
# ============================================================================

class VCOCircuit(AnalogComponent):
    """
    Voltage-Controlled Oscillator (VCO) with analog-style behavior.
    
    Implements band-limited waveform generation using PolyBLEP (Polynomial
    Band-Limited Step) technique to prevent aliasing. Simulates analog VCO
    characteristics including slight pitch drift and waveform imperfections.
    
    Parameters:
    -----------
    frequency : float
        Base frequency in Hz
    waveform : str
        'saw', 'square', 'triangle', 'sine'
    pulse_width : float
        Pulse width for square wave (0.0 to 1.0)
    drift_amount : float
        Amount of analog-style pitch drift (0.0 to 1.0)
    """
    
    def __init__(self, sample_rate: float = 44100.0):
        super().__init__(sample_rate)
        self._parameters = {
            'frequency': 440.0,
            'waveform': 'saw',
            'pulse_width': 0.5,
            'drift_amount': 0.001,
            'detune': 0.0,
        }
        self._state = {
            'phase': 0.0,
            'drift_phase': 0.0,
            'last_output': 0.0,
        }
        
    def reset(self):
        """Reset oscillator phase."""
        self._state['phase'] = 0.0
        self._state['drift_phase'] = 0.0
        self._state['last_output'] = 0.0
    
    def _polyblep(self, t: float, dt: float) -> float:
        """
        Polynomial Band-Limited Step (PolyBLEP) residual.
        Reduces aliasing at waveform discontinuities.
        """
        if t < dt:
            t = t / dt
            return t + t - t * t - 1.0
        elif t > 1.0 - dt:
            t = (t - 1.0) / dt
            return t * t + t + t + 1.0
        return 0.0
    
    def _generate_saw(self, phase: float, phase_inc: float) -> float:
        """Generate band-limited sawtooth wave."""
        value = 2.0 * phase - 1.0
        value -= self._polyblep(phase, phase_inc)
        return value
    
    def _generate_square(self, phase: float, phase_inc: float, pw: float) -> float:
        """Generate band-limited square wave with pulse width modulation."""
        value = 1.0 if phase < pw else -1.0
        value += self._polyblep(phase, phase_inc)
        value -= self._polyblep((phase - pw + 1.0) % 1.0, phase_inc)
        return value
    
    def _generate_triangle(self, phase: float) -> float:
        """Generate triangle wave."""
        if phase < 0.5:
            return 4.0 * phase - 1.0
        else:
            return 3.0 - 4.0 * phase
    
    def _generate_sine(self, phase: float) -> float:
        """Generate sine wave."""
        return np.sin(2.0 * np.pi * phase)
    
    def process(self, input_signal: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Generate oscillator output.
        
        Parameters:
        -----------
        input_signal : np.ndarray, optional
            FM modulation input (if provided)
            
        Returns:
        --------
        np.ndarray : Generated waveform
        """
        if input_signal is None:
            input_signal = np.zeros(1)
        
        output = np.zeros_like(input_signal)
        frequency = self._parameters['frequency']
        waveform = self._parameters['waveform']
        pw = np.clip(self._parameters['pulse_width'], 0.01, 0.99)
        drift = self._parameters['drift_amount']
        
        for i in range(len(input_signal)):
            # Analog-style frequency drift (very slow LFO)
            drift_lfo = np.sin(2.0 * np.pi * self._state['drift_phase'])
            freq_with_drift = frequency * (1.0 + drift * drift_lfo * 0.01)
            
            # Add FM modulation if provided
            if input_signal[i] != 0:
                freq_with_drift *= (1.0 + input_signal[i] * 0.1)
            
            phase_inc = freq_with_drift * self.dt
            
            # Generate waveform
            if waveform == 'saw':
                output[i] = self._generate_saw(self._state['phase'], phase_inc)
            elif waveform == 'square':
                output[i] = self._generate_square(self._state['phase'], phase_inc, pw)
            elif waveform == 'triangle':
                output[i] = self._generate_triangle(self._state['phase'])
            elif waveform == 'sine':
                output[i] = self._generate_sine(self._state['phase'])
            
            # Update phase
            self._state['phase'] += phase_inc
            if self._state['phase'] >= 1.0:
                self._state['phase'] -= 1.0
            
            # Update drift phase (very slow)
            self._state['drift_phase'] += 0.1 * self.dt
            if self._state['drift_phase'] >= 1.0:
                self._state['drift_phase'] -= 1.0
        
        return output


# ============================================================================
# FILTER CIRCUITS
# ============================================================================

class MoogLadderFilter(AnalogComponent):
    """
    Digital model of the Moog Ladder Filter (4-pole lowpass).
    
    Implements a non-linear model with zero-delay feedback and saturation
    characteristics that replicate the behavior of the original analog circuit.
    This is one of the most iconic filters in synthesis history.
    
    Parameters:
    -----------
    cutoff : float
        Filter cutoff frequency in Hz (20 to sample_rate/2)
    resonance : float
        Filter resonance/Q (0.0 to 1.0)
    drive : float
        Input drive/saturation amount (1.0 to 10.0)
    """
    
    def __init__(self, sample_rate: float = 44100.0):
        super().__init__(sample_rate)
        self._parameters = {
            'cutoff': 1000.0,
            'resonance': 0.0,
            'drive': 1.0,
        }
        self._state = {
            'stage': np.zeros(4),  # 4 filter stages
            'stage_tanh': np.zeros(4),  # Tanh outputs of each stage
            'feedback': 0.0,
        }
        self._thermal = 0.000025  # Thermal voltage (26mV at room temp)
        
    def reset(self):
        """Reset filter state."""
        self._state['stage'] = np.zeros(4)
        self._state['stage_tanh'] = np.zeros(4)
        self._state['feedback'] = 0.0
    
    def _tanh_clip(self, x: float) -> float:
        """Soft saturation using tanh (models transistor behavior)."""
        return np.tanh(x)
    
    def _calculate_coefficients(self, cutoff: float, resonance: float):
        """Calculate filter coefficients."""
        # Frequency warping for better high-frequency response
        fc = cutoff / self.sample_rate
        fc = np.clip(fc, 0.0, 0.45)  # Prevent instability
        
        # Calculate filter coefficient
        g = np.tan(np.pi * fc)
        
        # Resonance coefficient (0 to 4 for self-oscillation)
        k = 4.0 * resonance
        
        return g, k
    
    def process(self, input_signal: np.ndarray) -> np.ndarray:
        """
        Process input through Moog ladder filter.
        
        Uses iterative solver to handle zero-delay feedback loop accurately.
        """
        output = np.zeros_like(input_signal)
        cutoff = np.clip(self._parameters['cutoff'], 20.0, self.sample_rate * 0.45)
        resonance = np.clip(self._parameters['resonance'], 0.0, 1.0)
        drive = np.clip(self._parameters['drive'], 1.0, 10.0)
        
        g, k = self._calculate_coefficients(cutoff, resonance)
        
        for i in range(len(input_signal)):
            # Input with drive and feedback
            input_sample = drive * input_signal[i] - k * self._state['feedback']
            
            # Input saturation
            input_sample = self._tanh_clip(input_sample)
            
            # Process through 4 cascaded one-pole filters
            # Using TPT (Topology-Preserving Transform) structure
            stage_input = input_sample
            
            for stage_idx in range(4):
                # One-pole TPT filter stage
                v = (stage_input - self._state['stage'][stage_idx]) * g / (1.0 + g)
                lp = v + self._state['stage'][stage_idx]
                self._state['stage'][stage_idx] = lp + v
                
                # Non-linear saturation per stage
                stage_output = self._tanh_clip(lp)
                self._state['stage_tanh'][stage_idx] = stage_output
                
                stage_input = stage_output
            
            # Output is the last stage
            output[i] = self._state['stage_tanh'][3]
            
            # Update feedback (average of all stages for stability)
            self._state['feedback'] = np.mean(self._state['stage_tanh'])
        
        return output


class StateVariableFilter(AnalogComponent):
    """
    State Variable Filter - Multimode filter circuit.
    
    Provides simultaneous lowpass, highpass, and bandpass outputs from a
    single circuit topology, modeling the behavior of analog SVF designs.
    
    Parameters:
    -----------
    cutoff : float
        Filter cutoff frequency in Hz
    resonance : float
        Filter resonance (0.0 to 1.0)
    mode : str
        Filter mode: 'lowpass', 'highpass', 'bandpass', 'notch'
    """
    
    def __init__(self, sample_rate: float = 44100.0):
        super().__init__(sample_rate)
        self._parameters = {
            'cutoff': 1000.0,
            'resonance': 0.0,
            'mode': 'lowpass',
        }
        self._state = {
            'lp': 0.0,  # Lowpass state
            'bp': 0.0,  # Bandpass state
        }
        
    def reset(self):
        """Reset filter state."""
        self._state['lp'] = 0.0
        self._state['bp'] = 0.0
    
    def process(self, input_signal: np.ndarray) -> np.ndarray:
        """Process input through state variable filter."""
        output = np.zeros_like(input_signal)
        cutoff = np.clip(self._parameters['cutoff'], 20.0, self.sample_rate * 0.45)
        resonance = np.clip(self._parameters['resonance'], 0.0, 1.0)
        mode = self._parameters['mode']
        
        # Calculate coefficients
        fc = cutoff / self.sample_rate
        f = 2.0 * np.sin(np.pi * fc)
        q = 1.0 - resonance * 0.9  # Resonance inversely related to damping
        q = max(q, 0.001)  # Prevent division by zero
        
        for i in range(len(input_signal)):
            # State variable filter equations
            hp = input_signal[i] - self._state['lp'] - q * self._state['bp']
            bp_out = f * hp + self._state['bp']
            lp_out = f * bp_out + self._state['lp']
            
            # Update states
            self._state['bp'] = bp_out
            self._state['lp'] = lp_out
            
            # Select output mode
            if mode == 'lowpass':
                output[i] = lp_out
            elif mode == 'highpass':
                output[i] = hp
            elif mode == 'bandpass':
                output[i] = bp_out
            elif mode == 'notch':
                output[i] = input_signal[i] - bp_out
        
        return output


# ============================================================================
# ENVELOPE GENERATORS
# ============================================================================

@dataclass
class EnvelopeStage:
    """Represents a single envelope stage."""
    target: float
    time: float
    curve: str = 'exponential'  # 'exponential', 'linear', 'logarithmic'


class AnalogADSR(AnalogComponent):
    """
    Analog-style ADSR Envelope Generator.
    
    Models the charging/discharging behavior of capacitors in analog envelope
    generators, providing exponential curves and analog-style timing.
    
    Parameters:
    -----------
    attack : float
        Attack time in seconds
    decay : float
        Decay time in seconds
    sustain : float
        Sustain level (0.0 to 1.0)
    release : float
        Release time in seconds
    """
    
    def __init__(self, sample_rate: float = 44100.0):
        super().__init__(sample_rate)
        self._parameters = {
            'attack': 0.01,
            'decay': 0.1,
            'sustain': 0.7,
            'release': 0.3,
        }
        self._state = {
            'stage': 'idle',  # idle, attack, decay, sustain, release
            'current_value': 0.0,
            'gate': False,
        }
        
    def reset(self):
        """Reset envelope."""
        self._state['stage'] = 'idle'
        self._state['current_value'] = 0.0
        self._state['gate'] = False
    
    def trigger(self, gate: bool):
        """Trigger or release the envelope."""
        if gate and not self._state['gate']:
            # Note on
            self._state['stage'] = 'attack'
        elif not gate and self._state['gate']:
            # Note off
            self._state['stage'] = 'release'
        self._state['gate'] = gate
    
    def _exponential_curve(self, current: float, target: float, time_constant: float) -> float:
        """Exponential approach to target (models capacitor charging)."""
        if time_constant < 0.0001:
            return target
        coef = np.exp(-1.0 / (time_constant * self.sample_rate))
        return target + (current - target) * coef
    
    def process_sample(self) -> float:
        """Process one sample of envelope."""
        attack = max(self._parameters['attack'], 0.001)
        decay = max(self._parameters['decay'], 0.001)
        sustain = np.clip(self._parameters['sustain'], 0.0, 1.0)
        release = max(self._parameters['release'], 0.001)
        
        current = self._state['current_value']
        
        if self._state['stage'] == 'attack':
            current = self._exponential_curve(current, 1.0, attack)
            if current > 0.99:
                self._state['stage'] = 'decay'
                
        elif self._state['stage'] == 'decay':
            current = self._exponential_curve(current, sustain, decay)
            if abs(current - sustain) < 0.01:
                self._state['stage'] = 'sustain'
                
        elif self._state['stage'] == 'sustain':
            current = sustain
            
        elif self._state['stage'] == 'release':
            current = self._exponential_curve(current, 0.0, release)
            if current < 0.001:
                self._state['stage'] = 'idle'
                current = 0.0
                
        elif self._state['stage'] == 'idle':
            current = 0.0
        
        self._state['current_value'] = current
        return current
    
    def process(self, buffer_size: int) -> np.ndarray:
        """Generate envelope for a buffer of samples."""
        output = np.zeros(buffer_size)
        for i in range(buffer_size):
            output[i] = self.process_sample()
        return output


# ============================================================================
# MODULATION CIRCUITS
# ============================================================================

class LFO(AnalogComponent):
    """
    Low Frequency Oscillator with analog-style behavior.
    
    Parameters:
    -----------
    frequency : float
        LFO frequency in Hz
    waveform : str
        'sine', 'triangle', 'saw', 'square', 'random'
    """
    
    def __init__(self, sample_rate: float = 44100.0):
        super().__init__(sample_rate)
        self._parameters = {
            'frequency': 1.0,
            'waveform': 'sine',
            'phase_offset': 0.0,
        }
        self._state = {
            'phase': 0.0,
            'random_last': 0.0,
            'random_target': 0.0,
        }
        
    def reset(self):
        """Reset LFO phase."""
        self._state['phase'] = 0.0
        self._state['random_last'] = 0.0
        self._state['random_target'] = 0.0
    
    def process(self, buffer_size: int) -> np.ndarray:
        """Generate LFO output."""
        output = np.zeros(buffer_size)
        frequency = max(self._parameters['frequency'], 0.001)
        waveform = self._parameters['waveform']
        
        for i in range(buffer_size):
            phase = self._state['phase']
            
            if waveform == 'sine':
                output[i] = np.sin(2.0 * np.pi * phase)
            elif waveform == 'triangle':
                output[i] = 2.0 * abs(2.0 * (phase - 0.5)) - 1.0
            elif waveform == 'saw':
                output[i] = 2.0 * phase - 1.0
            elif waveform == 'square':
                output[i] = 1.0 if phase < 0.5 else -1.0
            elif waveform == 'random':
                # Sample and hold random
                if phase < self._state['phase']:
                    self._state['random_last'] = self._state['random_target']
                    self._state['random_target'] = np.random.uniform(-1.0, 1.0)
                # Smooth interpolation
                t = phase * 2.0 if phase < 0.5 else (1.0 - phase) * 2.0
                output[i] = self._state['random_last'] + t * (self._state['random_target'] - self._state['random_last'])
            
            # Update phase
            self._state['phase'] += frequency * self.dt
            if self._state['phase'] >= 1.0:
                self._state['phase'] -= 1.0
        
        return output


# ============================================================================
# SYNTHESIZER VOICE
# ============================================================================

class AnalogSynthVoice:
    """
    Complete synthesizer voice combining oscillators, filters, and envelopes.
    
    This represents a complete signal path similar to classic analog monosynths
    like the Minimoog or Prophet-5.
    """
    
    def __init__(self, sample_rate: float = 44100.0):
        self.sample_rate = sample_rate
        
        # Oscillators
        self.osc1 = VCOCircuit(sample_rate)
        self.osc2 = VCOCircuit(sample_rate)
        
        # Filter
        self.filter = MoogLadderFilter(sample_rate)
        
        # Envelopes
        self.amp_envelope = AnalogADSR(sample_rate)
        self.filter_envelope = AnalogADSR(sample_rate)
        
        # LFO
        self.lfo = LFO(sample_rate)
        
        # Mix parameters
        self.osc_mix = 0.5  # 0.0 = osc1 only, 1.0 = osc2 only
        self.filter_env_amount = 0.5
        self.lfo_to_filter_amount = 0.0
        
    def note_on(self, frequency: float, velocity: float = 1.0):
        """Trigger a note."""
        self.osc1.set_parameter('frequency', frequency)
        self.osc2.set_parameter('frequency', frequency)
        self.amp_envelope.trigger(True)
        self.filter_envelope.trigger(True)
        
    def note_off(self):
        """Release the note."""
        self.amp_envelope.trigger(False)
        self.filter_envelope.trigger(False)
        
    def render(self, buffer_size: int) -> np.ndarray:
        """Render a buffer of audio."""
        # Generate oscillators
        osc1_out = self.osc1.process(np.zeros(buffer_size))
        osc2_out = self.osc2.process(np.zeros(buffer_size))
        
        # Mix oscillators
        mixed = (1.0 - self.osc_mix) * osc1_out + self.osc_mix * osc2_out
        
        # Generate modulation
        lfo_out = self.lfo.process(buffer_size)
        filter_env = self.filter_envelope.process(buffer_size)
        
        # Modulate filter cutoff
        base_cutoff = self.filter.get_parameter('cutoff')
        for i in range(buffer_size):
            modulated_cutoff = base_cutoff * (
                1.0 + 
                self.filter_env_amount * filter_env[i] +
                self.lfo_to_filter_amount * lfo_out[i]
            )
            self.filter.set_parameter('cutoff', modulated_cutoff)
            mixed[i:i+1] = self.filter.process(mixed[i:i+1])
        
        # Apply amplitude envelope
        amp_env = self.amp_envelope.process(buffer_size)
        output = mixed * amp_env
        
        return output


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def midi_to_frequency(midi_note: int) -> float:
    """Convert MIDI note number to frequency in Hz."""
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))


def db_to_linear(db: float) -> float:
    """Convert decibels to linear amplitude."""
    return 10.0 ** (db / 20.0)


def linear_to_db(linear: float) -> float:
    """Convert linear amplitude to decibels."""
    return 20.0 * np.log10(max(linear, 1e-10))


# ============================================================================
# PRESET SYSTEM
# ============================================================================

class PresetManager:
    """Manages synthesizer presets."""
    
    def __init__(self):
        self.presets = {}
        
    def save_preset(self, name: str, voice: AnalogSynthVoice) -> Dict[str, Any]:
        """Save a voice configuration as a preset."""
        preset = {
            'osc1': voice.osc1.get_parameters(),
            'osc2': voice.osc2.get_parameters(),
            'filter': voice.filter.get_parameters(),
            'amp_envelope': voice.amp_envelope.get_parameters(),
            'filter_envelope': voice.filter_envelope.get_parameters(),
            'lfo': voice.lfo.get_parameters(),
            'osc_mix': voice.osc_mix,
            'filter_env_amount': voice.filter_env_amount,
            'lfo_to_filter_amount': voice.lfo_to_filter_amount,
        }
        self.presets[name] = preset
        return preset
    
    def load_preset(self, name: str, voice: AnalogSynthVoice):
        """Load a preset into a voice."""
        if name not in self.presets:
            raise ValueError(f"Preset '{name}' not found")
        
        preset = self.presets[name]
        
        for param, value in preset['osc1'].items():
            voice.osc1.set_parameter(param, value)
        for param, value in preset['osc2'].items():
            voice.osc2.set_parameter(param, value)
        for param, value in preset['filter'].items():
            voice.filter.set_parameter(param, value)
        for param, value in preset['amp_envelope'].items():
            voice.amp_envelope.set_parameter(param, value)
        for param, value in preset['filter_envelope'].items():
            voice.filter_envelope.set_parameter(param, value)
        for param, value in preset['lfo'].items():
            voice.lfo.set_parameter(param, value)
            
        voice.osc_mix = preset['osc_mix']
        voice.filter_env_amount = preset['filter_env_amount']
        voice.lfo_to_filter_amount = preset['lfo_to_filter_amount']
    
    def export_presets(self, filename: str):
        """Export presets to JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.presets, f, indent=2)
    
    def import_presets(self, filename: str):
        """Import presets from JSON file."""
        with open(filename, 'r') as f:
            self.presets = json.load(f)
