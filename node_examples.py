"""
Node-Based Synthesis Examples
==============================

Example patches demonstrating how to create synthesizers and effects
using the node-based system.
"""

import numpy as np
from scipy.io import wavfile
from node_system import NodeGraph
from analog_nodes import *


# ============================================================================
# EXAMPLE 1: Basic Monophonic Synthesizer
# ============================================================================

def example_1_basic_synth():
    """
    Create a simple monophonic synthesizer:
    MIDI Note → VCO → Filter → VCA → Audio Out
                        ↑       ↑
                   ADSR(Filter)  ADSR(Amp)
    """
    print("Example 1: Basic Monophonic Synthesizer")
    print("=" * 60)
    
    sample_rate = 44100
    graph = NodeGraph(sample_rate)
    graph.name = "Basic Monosynth"
    
    # Create nodes
    midi_node = MIDINoteNode(sample_rate=sample_rate)
    osc_node = OscillatorNode(sample_rate=sample_rate)
    filter_node = MoogFilterNode(sample_rate=sample_rate)
    filter_env = ADSRNode(sample_rate=sample_rate)
    amp_env = ADSRNode(sample_rate=sample_rate)
    vca_node = VCANode(sample_rate=sample_rate)
    output_node = AudioOutputNode(sample_rate=sample_rate)
    
    # Configure parameters
    midi_node.set_parameter('note', 60)  # Middle C
    midi_node.set_parameter('gate_on', True)
    
    osc_node.set_parameter('waveform', 'saw')
    osc_node.set_parameter('frequency', 440.0)
    
    filter_node.set_parameter('cutoff', 1000.0)
    filter_node.set_parameter('resonance', 0.7)
    filter_node.set_parameter('drive', 1.5)
    filter_node.set_parameter('cutoff_mod_amount', 2.0)
    
    filter_env.set_parameter('attack', 0.01)
    filter_env.set_parameter('decay', 0.3)
    filter_env.set_parameter('sustain', 0.3)
    filter_env.set_parameter('release', 0.2)
    
    amp_env.set_parameter('attack', 0.01)
    amp_env.set_parameter('decay', 0.2)
    amp_env.set_parameter('sustain', 0.7)
    amp_env.set_parameter('release', 0.4)
    
    # Add nodes to graph
    graph.add_node(midi_node)
    graph.add_node(osc_node)
    graph.add_node(filter_node)
    graph.add_node(filter_env)
    graph.add_node(amp_env)
    graph.add_node(vca_node)
    graph.add_node(output_node)
    
    # Create connections
    graph.connect(midi_node.node_id, 'frequency', osc_node.node_id, 'frequency')
    graph.connect(midi_node.node_id, 'gate', filter_env.node_id, 'gate')
    graph.connect(midi_node.node_id, 'gate', amp_env.node_id, 'gate')
    
    graph.connect(osc_node.node_id, 'output', filter_node.node_id, 'input')
    graph.connect(filter_env.node_id, 'output', filter_node.node_id, 'cutoff_mod')
    
    graph.connect(filter_node.node_id, 'output', vca_node.node_id, 'input')
    graph.connect(amp_env.node_id, 'output', vca_node.node_id, 'control')
    
    graph.connect(vca_node.node_id, 'output', output_node.node_id, 'left')
    graph.connect(vca_node.node_id, 'output', output_node.node_id, 'right')
    
    print(graph.get_info())
    print()
    
    # Render audio (2 seconds)
    duration = 2.0
    buffer_size = int(sample_rate * duration)
    chunk_size = 512
    
    audio_left = []
    audio_right = []
    
    print("Rendering audio...")
    for i in range(0, buffer_size, chunk_size):
        current_chunk = min(chunk_size, buffer_size - i)
        
        # Release note after 1 second
        if i == int(sample_rate * 1.0):
            midi_node.set_parameter('gate_on', False)
        
        outputs = graph.process(current_chunk)
        
        # Get audio output
        output_id = output_node.node_id
        if output_id in outputs:
            audio_left.append(outputs[output_id]['left'])
            audio_right.append(outputs[output_id]['right'])
    
    # Combine chunks
    audio_left = np.concatenate(audio_left)
    audio_right = np.concatenate(audio_right)
    
    # Normalize
    audio_left = audio_left / np.max(np.abs(audio_left)) * 0.8
    audio_right = audio_right / np.max(np.abs(audio_right)) * 0.8
    
    # Save stereo audio
    audio_stereo = np.column_stack((audio_left, audio_right))
    wavfile.write('/workspace/node_example1_basic_synth.wav', sample_rate,
                  (audio_stereo * 32767).astype(np.int16))
    
    print("✓ Saved node_example1_basic_synth.wav")
    print()


# ============================================================================
# EXAMPLE 2: Detuned Dual Oscillator Synth
# ============================================================================

def example_2_detuned_synth():
    """
    Two detuned oscillators mixed together for a thick sound.
    """
    print("Example 2: Detuned Dual Oscillator Synth")
    print("=" * 60)
    
    sample_rate = 44100
    graph = NodeGraph(sample_rate)
    
    # Create nodes
    midi_node = MIDINoteNode(sample_rate=sample_rate)
    osc1 = OscillatorNode(sample_rate=sample_rate)
    osc2 = OscillatorNode(sample_rate=sample_rate)
    mixer = MixerNode(sample_rate=sample_rate)
    filter_node = MoogFilterNode(sample_rate=sample_rate)
    filter_env = ADSRNode(sample_rate=sample_rate)
    amp_env = ADSRNode(sample_rate=sample_rate)
    vca = VCANode(sample_rate=sample_rate)
    output = AudioOutputNode(sample_rate=sample_rate)
    
    # Configure
    midi_node.set_parameter('note', 48)  # C3
    midi_node.set_parameter('gate_on', True)
    
    osc1.set_parameter('waveform', 'saw')
    osc2.set_parameter('waveform', 'square')
    osc2.set_parameter('pulse_width', 0.3)
    
    filter_node.set_parameter('cutoff', 2000.0)
    filter_node.set_parameter('resonance', 0.6)
    filter_node.set_parameter('cutoff_mod_amount', 1.5)
    
    filter_env.set_parameter('attack', 0.02)
    filter_env.set_parameter('decay', 0.4)
    filter_env.set_parameter('sustain', 0.4)
    filter_env.set_parameter('release', 0.3)
    
    amp_env.set_parameter('attack', 0.01)
    amp_env.set_parameter('decay', 0.3)
    amp_env.set_parameter('sustain', 0.6)
    amp_env.set_parameter('release', 0.5)
    
    # Add nodes
    for node in [midi_node, osc1, osc2, mixer, filter_node, 
                 filter_env, amp_env, vca, output]:
        graph.add_node(node)
    
    # Connect
    graph.connect(midi_node.node_id, 'frequency', osc1.node_id, 'frequency')
    graph.connect(midi_node.node_id, 'frequency', osc2.node_id, 'frequency')
    graph.connect(midi_node.node_id, 'gate', filter_env.node_id, 'gate')
    graph.connect(midi_node.node_id, 'gate', amp_env.node_id, 'gate')
    
    # Mix oscillators
    graph.connect(osc1.node_id, 'output', mixer.node_id, 'input_1')
    graph.connect(osc2.node_id, 'output', mixer.node_id, 'input_2')
    
    # Filter path
    graph.connect(mixer.node_id, 'output', filter_node.node_id, 'input')
    graph.connect(filter_env.node_id, 'output', filter_node.node_id, 'cutoff_mod')
    
    # VCA
    graph.connect(filter_node.node_id, 'output', vca.node_id, 'input')
    graph.connect(amp_env.node_id, 'output', vca.node_id, 'control')
    
    # Output
    graph.connect(vca.node_id, 'output', output.node_id, 'left')
    graph.connect(vca.node_id, 'output', output.node_id, 'right')
    
    print(graph.get_info())
    print()
    
    # Render
    duration = 2.5
    buffer_size = int(sample_rate * duration)
    chunk_size = 512
    
    audio_left = []
    audio_right = []
    
    print("Rendering audio...")
    for i in range(0, buffer_size, chunk_size):
        current_chunk = min(chunk_size, buffer_size - i)
        
        if i == int(sample_rate * 1.5):
            midi_node.set_parameter('gate_on', False)
        
        outputs = graph.process(current_chunk)
        output_id = output.node_id
        
        if output_id in outputs:
            audio_left.append(outputs[output_id]['left'])
            audio_right.append(outputs[output_id]['right'])
    
    audio_left = np.concatenate(audio_left)
    audio_right = np.concatenate(audio_right)
    
    audio_left = audio_left / np.max(np.abs(audio_left)) * 0.8
    audio_right = audio_right / np.max(np.abs(audio_right)) * 0.8
    
    audio_stereo = np.column_stack((audio_left, audio_right))
    wavfile.write('/workspace/node_example2_detuned.wav', sample_rate,
                  (audio_stereo * 32767).astype(np.int16))
    
    print("✓ Saved node_example2_detuned.wav")
    print()


# ============================================================================
# EXAMPLE 3: LFO Modulated Filter
# ============================================================================

def example_3_lfo_filter():
    """
    LFO modulating the filter cutoff for rhythmic movement.
    """
    print("Example 3: LFO Modulated Filter")
    print("=" * 60)
    
    sample_rate = 44100
    graph = NodeGraph(sample_rate)
    
    # Nodes
    midi_node = MIDINoteNode(sample_rate=sample_rate)
    osc = OscillatorNode(sample_rate=sample_rate)
    lfo = LFONode(sample_rate=sample_rate)
    filter_node = MoogFilterNode(sample_rate=sample_rate)
    amp_env = ADSRNode(sample_rate=sample_rate)
    vca = VCANode(sample_rate=sample_rate)
    output = AudioOutputNode(sample_rate=sample_rate)
    
    # Configure
    midi_node.set_parameter('note', 36)  # C2
    midi_node.set_parameter('gate_on', True)
    
    osc.set_parameter('waveform', 'saw')
    
    lfo.set_parameter('frequency', 4.0)  # 4 Hz
    lfo.set_parameter('waveform', 'triangle')
    lfo.set_parameter('amplitude', 0.5)
    
    filter_node.set_parameter('cutoff', 500.0)
    filter_node.set_parameter('resonance', 0.8)
    filter_node.set_parameter('drive', 2.0)
    filter_node.set_parameter('cutoff_mod_amount', 3.0)
    
    amp_env.set_parameter('attack', 0.001)
    amp_env.set_parameter('decay', 0.1)
    amp_env.set_parameter('sustain', 1.0)
    amp_env.set_parameter('release', 0.1)
    
    # Add
    for node in [midi_node, osc, lfo, filter_node, amp_env, vca, output]:
        graph.add_node(node)
    
    # Connect
    graph.connect(midi_node.node_id, 'frequency', osc.node_id, 'frequency')
    graph.connect(midi_node.node_id, 'gate', amp_env.node_id, 'gate')
    
    graph.connect(osc.node_id, 'output', filter_node.node_id, 'input')
    graph.connect(lfo.node_id, 'output', filter_node.node_id, 'cutoff_mod')
    
    graph.connect(filter_node.node_id, 'output', vca.node_id, 'input')
    graph.connect(amp_env.node_id, 'output', vca.node_id, 'control')
    
    graph.connect(vca.node_id, 'output', output.node_id, 'left')
    graph.connect(vca.node_id, 'output', output.node_id, 'right')
    
    print(graph.get_info())
    print()
    
    # Render
    duration = 3.0
    buffer_size = int(sample_rate * duration)
    chunk_size = 512
    
    audio_left = []
    audio_right = []
    
    print("Rendering audio...")
    for i in range(0, buffer_size, chunk_size):
        current_chunk = min(chunk_size, buffer_size - i)
        
        if i == int(sample_rate * 2.5):
            midi_node.set_parameter('gate_on', False)
        
        outputs = graph.process(current_chunk)
        output_id = output.node_id
        
        if output_id in outputs:
            audio_left.append(outputs[output_id]['left'])
            audio_right.append(outputs[output_id]['right'])
    
    audio_left = np.concatenate(audio_left)
    audio_right = np.concatenate(audio_right)
    
    audio_left = audio_left / np.max(np.abs(audio_left)) * 0.8
    audio_right = audio_right / np.max(np.abs(audio_right)) * 0.8
    
    audio_stereo = np.column_stack((audio_left, audio_right))
    wavfile.write('/workspace/node_example3_lfo.wav', sample_rate,
                  (audio_stereo * 32767).astype(np.int16))
    
    print("✓ Saved node_example3_lfo.wav")
    print()


# ============================================================================
# MAIN
# ============================================================================

def run_all_examples():
    """Run all node-based synthesis examples."""
    print("\n")
    print("=" * 70)
    print("NODE-BASED ANALOG SYNTHESIS EXAMPLES")
    print("=" * 70)
    print()
    
    try:
        example_1_basic_synth()
        example_2_detuned_synth()
        example_3_lfo_filter()
        
        print("=" * 70)
        print("✓ All examples completed successfully!")
        print("=" * 70)
        print("\nGenerated files:")
        print("  - node_example1_basic_synth.wav")
        print("  - node_example2_detuned.wav")
        print("  - node_example3_lfo.wav")
        print()
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
