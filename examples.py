"""
Example Usage Scripts for Analog Circuit Synthesis Framework
=============================================================

This file demonstrates various ways to use the framework to create
synthesizer sounds and custom circuits.
"""

import numpy as np
import matplotlib.pyplot as plt
from analog_synth_framework import (
    AnalogSynthVoice,
    VCOCircuit,
    MoogLadderFilter,
    StateVariableFilter,
    AnalogADSR,
    LFO,
    midi_to_frequency,
    PresetManager
)


# ============================================================================
# EXAMPLE 1: Basic Synthesizer Note
# ============================================================================

def example_1_basic_note():
    """Generate a simple synthesizer note."""
    print("Example 1: Generating a basic synthesizer note...")
    
    sample_rate = 44100
    duration = 2.0
    buffer_size = int(sample_rate * duration)
    
    # Create a voice
    voice = AnalogSynthVoice(sample_rate)
    
    # Configure oscillators
    voice.osc1.set_parameter('waveform', 'saw')
    voice.osc2.set_parameter('waveform', 'square')
    voice.osc2.set_parameter('frequency', 440.0 * 1.01)  # Slight detune
    voice.osc_mix = 0.5  # Equal mix
    
    # Configure filter
    voice.filter.set_parameter('cutoff', 2000.0)
    voice.filter.set_parameter('resonance', 0.6)
    
    # Configure envelopes
    voice.amp_envelope.set_parameter('attack', 0.01)
    voice.amp_envelope.set_parameter('decay', 0.3)
    voice.amp_envelope.set_parameter('sustain', 0.7)
    voice.amp_envelope.set_parameter('release', 0.5)
    
    voice.filter_envelope.set_parameter('attack', 0.01)
    voice.filter_envelope.set_parameter('decay', 0.5)
    voice.filter_envelope.set_parameter('sustain', 0.3)
    voice.filter_envelope.set_parameter('release', 0.3)
    
    voice.filter_env_amount = 2.0  # Strong filter modulation
    
    # Trigger note
    voice.note_on(midi_to_frequency(60))  # Middle C
    
    # Render audio
    audio = voice.render(buffer_size)
    
    # Release after 1 second
    release_point = int(sample_rate * 1.0)
    voice.note_off()
    audio[release_point:] = voice.render(buffer_size - release_point)
    
    # Normalize
    audio = audio / np.max(np.abs(audio))
    
    # Save to file
    try:
        from scipy.io import wavfile
        wavfile.write('/home/claude/example1_basic_note.wav', sample_rate, 
                     (audio * 32767).astype(np.int16))
        print("✓ Audio saved to example1_basic_note.wav")
    except ImportError:
        print("! scipy not available, cannot save WAV file")
    
    return audio


# ============================================================================
# EXAMPLE 2: Bass Line with LFO Modulation
# ============================================================================

def example_2_bass_line():
    """Create a bass line with filter modulation."""
    print("\nExample 2: Creating a bass line with LFO modulation...")
    
    sample_rate = 44100
    voice = AnalogSynthVoice(sample_rate)
    
    # Configure for bass sound
    voice.osc1.set_parameter('waveform', 'saw')
    voice.osc2.set_parameter('waveform', 'square')
    voice.osc2.set_parameter('pulse_width', 0.3)
    voice.osc_mix = 0.7
    
    # Low filter for bass
    voice.filter.set_parameter('cutoff', 400.0)
    voice.filter.set_parameter('resonance', 0.8)
    voice.filter.set_parameter('drive', 2.0)
    
    # Punchy envelope
    voice.amp_envelope.set_parameter('attack', 0.001)
    voice.amp_envelope.set_parameter('decay', 0.2)
    voice.amp_envelope.set_parameter('sustain', 0.4)
    voice.amp_envelope.set_parameter('release', 0.1)
    
    voice.filter_envelope.set_parameter('attack', 0.001)
    voice.filter_envelope.set_parameter('decay', 0.15)
    voice.filter_envelope.set_parameter('sustain', 0.0)
    voice.filter_envelope.set_parameter('release', 0.1)
    
    # LFO modulation
    voice.lfo.set_parameter('frequency', 4.0)
    voice.lfo.set_parameter('waveform', 'sine')
    voice.lfo_to_filter_amount = 0.3
    voice.filter_env_amount = 1.5
    
    # Bass line notes (in MIDI)
    notes = [36, 36, 43, 36, 41, 36, 39, 36]  # C2, C2, G2, C2, F2, C2, Eb2, C2
    note_duration = 0.4
    gap_duration = 0.05
    
    audio_segments = []
    
    for note in notes:
        # Note on
        voice.note_on(midi_to_frequency(note))
        
        # Render note
        note_samples = int(sample_rate * note_duration)
        audio = voice.render(note_samples)
        
        # Note off
        voice.note_off()
        
        # Render gap
        gap_samples = int(sample_rate * gap_duration)
        gap = voice.render(gap_samples)
        
        audio_segments.append(audio)
        audio_segments.append(gap)
        
        # Reset for next note
        voice.amp_envelope.reset()
        voice.filter_envelope.reset()
    
    # Concatenate
    full_audio = np.concatenate(audio_segments)
    
    # Normalize
    full_audio = full_audio / np.max(np.abs(full_audio))
    
    # Save
    try:
        from scipy.io import wavfile
        wavfile.write('/home/claude/example2_bass_line.wav', sample_rate,
                     (full_audio * 32767).astype(np.int16))
        print("✓ Bass line saved to example2_bass_line.wav")
    except ImportError:
        print("! scipy not available, cannot save WAV file")
    
    return full_audio


# ============================================================================
# EXAMPLE 3: Pad Sound with Multiple Voices
# ============================================================================

def example_3_pad_sound():
    """Create a lush pad sound by layering detuned voices."""
    print("\nExample 3: Creating a pad sound with multiple voices...")
    
    sample_rate = 44100
    duration = 3.0
    buffer_size = int(sample_rate * duration)
    
    # Create multiple voices with slight detuning
    num_voices = 4
    detune_amounts = [-0.05, -0.02, 0.02, 0.05]
    
    voices = []
    for i in range(num_voices):
        voice = AnalogSynthVoice(sample_rate)
        
        # Slow attack for pad
        voice.amp_envelope.set_parameter('attack', 0.5)
        voice.amp_envelope.set_parameter('decay', 0.5)
        voice.amp_envelope.set_parameter('sustain', 0.8)
        voice.amp_envelope.set_parameter('release', 1.0)
        
        voice.filter_envelope.set_parameter('attack', 1.0)
        voice.filter_envelope.set_parameter('decay', 1.0)
        voice.filter_envelope.set_parameter('sustain', 0.6)
        voice.filter_envelope.set_parameter('release', 1.0)
        
        # Configure oscillators
        voice.osc1.set_parameter('waveform', 'saw')
        voice.osc2.set_parameter('waveform', 'square')
        voice.osc2.set_parameter('pulse_width', 0.5)
        voice.osc_mix = 0.5
        
        # Bright filter
        voice.filter.set_parameter('cutoff', 4000.0)
        voice.filter.set_parameter('resonance', 0.3)
        voice.filter_env_amount = 0.5
        
        # Slow LFO for movement
        voice.lfo.set_parameter('frequency', 0.3 + i * 0.1)
        voice.lfo.set_parameter('waveform', 'sine')
        voice.lfo_to_filter_amount = 0.2
        
        # Apply detune
        base_freq = midi_to_frequency(60)  # C4
        voice.note_on(base_freq * (1.0 + detune_amounts[i]))
        
        voices.append(voice)
    
    # Render all voices
    mixed_audio = np.zeros(buffer_size)
    
    for voice in voices:
        audio = voice.render(buffer_size)
        mixed_audio += audio / num_voices
    
    # Normalize
    mixed_audio = mixed_audio / np.max(np.abs(mixed_audio))
    
    # Save
    try:
        from scipy.io import wavfile
        wavfile.write('/home/claude/example3_pad_sound.wav', sample_rate,
                     (mixed_audio * 32767).astype(np.int16))
        print("✓ Pad sound saved to example3_pad_sound.wav")
    except ImportError:
        print("! scipy not available, cannot save WAV file")
    
    return mixed_audio


# ============================================================================
# EXAMPLE 4: Filter Sweep Demonstration
# ============================================================================

def example_4_filter_sweep():
    """Demonstrate filter cutoff sweep."""
    print("\nExample 4: Demonstrating filter cutoff sweep...")
    
    sample_rate = 44100
    duration = 4.0
    buffer_size = int(sample_rate * duration)
    
    # Create oscillator
    osc = VCOCircuit(sample_rate)
    osc.set_parameter('frequency', 110.0)  # Low A
    osc.set_parameter('waveform', 'saw')
    
    # Create filter
    filt = MoogLadderFilter(sample_rate)
    filt.set_parameter('resonance', 0.8)
    filt.set_parameter('drive', 1.5)
    
    # Generate sawtooth
    audio = osc.process(np.zeros(buffer_size))
    
    # Apply filter with sweeping cutoff
    filtered = np.zeros(buffer_size)
    
    for i in range(buffer_size):
        # Exponential sweep from 200 Hz to 8000 Hz
        progress = i / buffer_size
        cutoff = 200.0 * (8000.0 / 200.0) ** progress
        filt.set_parameter('cutoff', cutoff)
        
        # Process single sample
        filtered[i] = filt.process(audio[i:i+1])[0]
    
    # Normalize
    filtered = filtered / np.max(np.abs(filtered))
    
    # Save
    try:
        from scipy.io import wavfile
        wavfile.write('/home/claude/example4_filter_sweep.wav', sample_rate,
                     (filtered * 32767).astype(np.int16))
        print("✓ Filter sweep saved to example4_filter_sweep.wav")
    except ImportError:
        print("! scipy not available, cannot save WAV file")
    
    # Plot spectrogram
    try:
        from scipy import signal as sp_signal
        
        f, t, Sxx = sp_signal.spectrogram(filtered, sample_rate, nperseg=1024)
        
        plt.figure(figsize=(12, 6))
        plt.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), shading='gouraud')
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.title('Filter Sweep Spectrogram')
        plt.colorbar(label='Power [dB]')
        plt.ylim(0, 10000)
        plt.tight_layout()
        plt.savefig('/home/claude/example4_spectrogram.png', dpi=150)
        print("✓ Spectrogram saved to example4_spectrogram.png")
        plt.close()
    except ImportError:
        print("! scipy not available for spectrogram")
    
    return filtered


# ============================================================================
# EXAMPLE 5: Preset Management
# ============================================================================

def example_5_presets():
    """Demonstrate preset saving and loading."""
    print("\nExample 5: Demonstrating preset management...")
    
    sample_rate = 44100
    preset_manager = PresetManager()
    
    # Create preset 1: Bright Lead
    voice1 = AnalogSynthVoice(sample_rate)
    voice1.osc1.set_parameter('waveform', 'saw')
    voice1.filter.set_parameter('cutoff', 3000.0)
    voice1.filter.set_parameter('resonance', 0.7)
    voice1.amp_envelope.set_parameter('attack', 0.01)
    voice1.amp_envelope.set_parameter('decay', 0.2)
    voice1.amp_envelope.set_parameter('sustain', 0.8)
    voice1.amp_envelope.set_parameter('release', 0.3)
    
    preset_manager.save_preset('Bright Lead', voice1)
    print("✓ Saved preset: Bright Lead")
    
    # Create preset 2: Deep Bass
    voice2 = AnalogSynthVoice(sample_rate)
    voice2.osc1.set_parameter('waveform', 'square')
    voice2.filter.set_parameter('cutoff', 500.0)
    voice2.filter.set_parameter('resonance', 0.9)
    voice2.amp_envelope.set_parameter('attack', 0.001)
    voice2.amp_envelope.set_parameter('decay', 0.3)
    voice2.amp_envelope.set_parameter('sustain', 0.5)
    voice2.amp_envelope.set_parameter('release', 0.2)
    
    preset_manager.save_preset('Deep Bass', voice2)
    print("✓ Saved preset: Deep Bass")
    
    # Export presets
    preset_manager.export_presets('/home/claude/synth_presets.json')
    print("✓ Exported presets to synth_presets.json")
    
    # Load preset into new voice
    voice3 = AnalogSynthVoice(sample_rate)
    preset_manager.load_preset('Bright Lead', voice3)
    print("✓ Loaded preset: Bright Lead into new voice")
    
    # Test the loaded preset
    voice3.note_on(midi_to_frequency(72))  # C5
    audio = voice3.render(int(sample_rate * 1.5))
    
    try:
        from scipy.io import wavfile
        audio = audio / np.max(np.abs(audio))
        wavfile.write('/home/claude/example5_preset_test.wav', sample_rate,
                     (audio * 32767).astype(np.int16))
        print("✓ Preset test saved to example5_preset_test.wav")
    except ImportError:
        print("! scipy not available")
    
    return preset_manager


# ============================================================================
# EXAMPLE 6: Waveform Comparison
# ============================================================================

def example_6_waveform_comparison():
    """Compare different oscillator waveforms."""
    print("\nExample 6: Comparing oscillator waveforms...")
    
    sample_rate = 44100
    duration = 0.01  # 10ms for clear waveform view
    buffer_size = int(sample_rate * duration)
    
    osc = VCOCircuit(sample_rate)
    osc.set_parameter('frequency', 440.0)
    
    waveforms = ['sine', 'saw', 'square', 'triangle']
    colors = ['blue', 'red', 'green', 'purple']
    
    plt.figure(figsize=(14, 10))
    
    for idx, (waveform, color) in enumerate(zip(waveforms, colors)):
        osc.reset()
        osc.set_parameter('waveform', waveform)
        audio = osc.process(np.zeros(buffer_size))
        
        # Time domain
        plt.subplot(4, 2, idx * 2 + 1)
        t = np.linspace(0, duration, buffer_size)
        plt.plot(t * 1000, audio, color=color, linewidth=2)
        plt.title(f'{waveform.capitalize()} - Time Domain')
        plt.xlabel('Time (ms)')
        plt.ylabel('Amplitude')
        plt.grid(True, alpha=0.3)
        plt.ylim(-1.2, 1.2)
        
        # Frequency domain
        plt.subplot(4, 2, idx * 2 + 2)
        fft = np.fft.rfft(audio)
        freqs = np.fft.rfftfreq(buffer_size, 1/sample_rate)
        magnitude = np.abs(fft)
        magnitude_db = 20 * np.log10(magnitude + 1e-10)
        
        plt.plot(freqs[:200], magnitude_db[:200], color=color, linewidth=2)
        plt.title(f'{waveform.capitalize()} - Frequency Domain')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude (dB)')
        plt.grid(True, alpha=0.3)
        plt.ylim(-60, 20)
    
    plt.tight_layout()
    plt.savefig('/home/claude/example6_waveforms.png', dpi=150)
    print("✓ Waveform comparison saved to example6_waveforms.png")
    plt.close()


# ============================================================================
# EXAMPLE 7: Envelope Visualization
# ============================================================================

def example_7_envelope_shapes():
    """Visualize different envelope shapes."""
    print("\nExample 7: Visualizing envelope shapes...")
    
    sample_rate = 44100
    env = AnalogADSR(sample_rate)
    
    # Different envelope configurations
    configs = [
        {'name': 'Pluck', 'attack': 0.001, 'decay': 0.1, 'sustain': 0.0, 'release': 0.05},
        {'name': 'Pad', 'attack': 0.5, 'decay': 0.5, 'sustain': 0.8, 'release': 1.0},
        {'name': 'Organ', 'attack': 0.001, 'decay': 0.0, 'sustain': 1.0, 'release': 0.1},
        {'name': 'Piano', 'attack': 0.01, 'decay': 0.3, 'sustain': 0.5, 'release': 0.5},
    ]
    
    plt.figure(figsize=(14, 10))
    
    for idx, config in enumerate(configs):
        env.reset()
        env.set_parameter('attack', config['attack'])
        env.set_parameter('decay', config['decay'])
        env.set_parameter('sustain', config['sustain'])
        env.set_parameter('release', config['release'])
        
        # Trigger note
        env.trigger(True)
        
        # Hold for 1 second, then release
        hold_time = 1.0
        release_time = 1.5
        total_samples = int(sample_rate * (hold_time + release_time))
        
        envelope = []
        for i in range(total_samples):
            if i == int(sample_rate * hold_time):
                env.trigger(False)  # Release
            envelope.append(env.process_sample())
        
        envelope = np.array(envelope)
        t = np.linspace(0, hold_time + release_time, total_samples)
        
        plt.subplot(2, 2, idx + 1)
        plt.plot(t, envelope, linewidth=2)
        plt.axvline(hold_time, color='red', linestyle='--', alpha=0.5, label='Release')
        plt.title(f"{config['name']} Envelope\n" + 
                 f"A={config['attack']:.3f} D={config['decay']:.3f} " +
                 f"S={config['sustain']:.2f} R={config['release']:.3f}")
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.ylim(-0.1, 1.1)
    
    plt.tight_layout()
    plt.savefig('/home/claude/example7_envelopes.png', dpi=150)
    print("✓ Envelope shapes saved to example7_envelopes.png")
    plt.close()


# ============================================================================
# MAIN RUNNER
# ============================================================================

def run_all_examples():
    """Run all examples."""
    print("=" * 70)
    print("ANALOG CIRCUIT SYNTHESIS FRAMEWORK - EXAMPLES")
    print("=" * 70)
    
    try:
        example_1_basic_note()
        example_2_bass_line()
        example_3_pad_sound()
        example_4_filter_sweep()
        example_5_presets()
        example_6_waveform_comparison()
        example_7_envelope_shapes()
        
        print("\n" + "=" * 70)
        print("✓ All examples completed successfully!")
        print("=" * 70)
        print("\nGenerated files:")
        print("  - example1_basic_note.wav")
        print("  - example2_bass_line.wav")
        print("  - example3_pad_sound.wav")
        print("  - example4_filter_sweep.wav")
        print("  - example4_spectrogram.png")
        print("  - example5_preset_test.wav")
        print("  - example6_waveforms.png")
        print("  - example7_envelopes.png")
        print("  - synth_presets.json")
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
