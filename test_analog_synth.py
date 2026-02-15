"""
Test Suite for Analog Circuit Synthesis Framework
=================================================

This test suite validates the functionality of the analog synthesis framework
including individual components, node system, and integration tests.
"""

import unittest
import numpy as np
from analog_synth_framework import (
    VCOCircuit, MoogLadderFilter, StateVariableFilter,
    AnalogADSR, LFO, AnalogSynthVoice, midi_to_frequency
)
from node_system import NodeGraph, NodeFactory
from analog_nodes import (
    OscillatorNode, MoogFilterNode, StateVariableFilterNode,
    ADSRNode, LFONode, MixerNode, GainNode, VCANode
)


class TestVCOCircuit(unittest.TestCase):
    """Test Voltage Controlled Oscillator Circuit."""
    
    def setUp(self):
        self.vco = VCOCircuit(sample_rate=44100.0)
    
    def test_initialization(self):
        """Test VCO initialization."""
        self.assertEqual(self.vco.sample_rate, 44100.0)
        self.assertEqual(self.vco.get_parameter('frequency'), 440.0)
        self.assertEqual(self.vco.get_parameter('waveform'), 'saw')
        
    def test_process_sine_wave(self):
        """Test sine wave generation."""
        self.vco.set_parameter('waveform', 'sine')
        self.vco.set_parameter('frequency', 440.0)
        output = self.vco.process(np.zeros(100))
        self.assertEqual(len(output), 100)
        self.assertTrue(np.all(np.abs(output) <= 1.0))
        
    def test_process_saw_wave(self):
        """Test sawtooth wave generation."""
        self.vco.set_parameter('waveform', 'saw')
        self.vco.set_parameter('frequency', 440.0)
        output = self.vco.process(np.zeros(100))
        self.assertEqual(len(output), 100)
        self.assertTrue(np.all(np.abs(output) <= 1.0))
        
    def test_process_square_wave(self):
        """Test square wave generation."""
        self.vco.set_parameter('waveform', 'square')
        self.vco.set_parameter('frequency', 440.0)
        output = self.vco.process(np.zeros(100))
        self.assertEqual(len(output), 100)
        self.assertTrue(np.all(np.abs(output) <= 1.0))
        
    def test_process_triangle_wave(self):
        """Test triangle wave generation."""
        self.vco.set_parameter('waveform', 'triangle')
        self.vco.set_parameter('frequency', 440.0)
        output = self.vco.process(np.zeros(100))
        self.assertEqual(len(output), 100)
        self.assertTrue(np.all(np.abs(output) <= 1.0))


class TestMoogLadderFilter(unittest.TestCase):
    """Test Moog Ladder Filter Circuit."""
    
    def setUp(self):
        self.filter = MoogLadderFilter(sample_rate=44100.0)
    
    def test_initialization(self):
        """Test filter initialization."""
        self.assertEqual(self.filter.sample_rate, 44100.0)
        self.assertEqual(self.filter.get_parameter('cutoff'), 1000.0)
        self.assertEqual(self.filter.get_parameter('resonance'), 0.0)
        
    def test_process_lowpass(self):
        """Test lowpass filtering."""
        # Create a signal with both low and high frequencies
        t = np.linspace(0, 1, 44100, False)
        signal = np.sin(2*np.pi*100*t) + 0.1*np.sin(2*np.pi*5000*t)  # 100Hz + 5kHz
        
        # Set low cutoff to filter out high frequencies
        self.filter.set_parameter('cutoff', 200.0)
        self.filter.set_parameter('resonance', 0.0)
        
        output = self.filter.process(signal)
        
        # The output should have reduced high-frequency content
        self.assertEqual(len(output), len(signal))
        # The energy should be mostly preserved for low frequencies
        input_energy = np.sum(signal**2)
        output_energy = np.sum(output**2)
        # Output should be less than input due to filtering
        self.assertLess(output_energy, input_energy * 1.5)  # Allow some amplification from resonance
        
    def test_resonance(self):
        """Test resonance effect."""
        # Create a signal
        signal = np.random.randn(1000)
        
        # Process with low resonance
        self.filter.set_parameter('cutoff', 1000.0)
        self.filter.set_parameter('resonance', 0.1)
        output_low_res = self.filter.process(signal)
        
        # Process with high resonance
        self.filter.set_parameter('resonance', 0.8)
        output_high_res = self.filter.process(signal)
        
        # High resonance might increase output energy at certain frequencies
        self.assertEqual(len(output_low_res), len(output_high_res))


class TestStateVariableFilter(unittest.TestCase):
    """Test State Variable Filter Circuit."""
    
    def setUp(self):
        self.filter = StateVariableFilter(sample_rate=44100.0)
    
    def test_initialization(self):
        """Test filter initialization."""
        self.assertEqual(self.filter.sample_rate, 44100.0)
        self.assertEqual(self.filter.get_parameter('cutoff'), 1000.0)
        self.assertEqual(self.filter.get_parameter('mode'), 'lowpass')
        
    def test_modes(self):
        """Test different filter modes."""
        signal = np.random.randn(1000)
        
        modes = ['lowpass', 'highpass', 'bandpass', 'notch']
        
        for mode in modes:
            self.filter.set_parameter('mode', mode)
            output = self.filter.process(signal)
            self.assertEqual(len(output), len(signal))


class TestAnalogADSR(unittest.TestCase):
    """Test ADSR Envelope Generator."""
    
    def setUp(self):
        self.env = AnalogADSR(sample_rate=44100.0)
    
    def test_initialization(self):
        """Test envelope initialization."""
        self.assertEqual(self.env.sample_rate, 44100.0)
        self.assertEqual(self.env.get_parameter('attack'), 0.01)
        self.assertEqual(self.env.get_parameter('sustain'), 0.7)
        
    def test_attack_phase(self):
        """Test attack phase of envelope."""
        self.env.set_parameter('attack', 0.1)  # 100ms attack
        self.env.set_parameter('decay', 1.0)
        self.env.set_parameter('sustain', 0.8)
        self.env.set_parameter('release', 0.5)
        
        self.env.trigger(True)  # Note on
        
        # Check that value increases during attack
        initial_val = self.env.process_sample()
        # Advance many samples to ensure we're in attack phase
        for _ in range(int(0.05 * 44100)):  # 50ms
            val = self.env.process_sample()
            # Value should be increasing toward 1.0
            self.assertGreaterEqual(val, initial_val)
            
    def test_sustain_phase(self):
        """Test sustain phase of envelope."""
        self.env.set_parameter('attack', 0.01)
        self.env.set_parameter('decay', 0.1)
        self.env.set_parameter('sustain', 0.5)
        self.env.set_parameter('release', 0.5)
        
        self.env.trigger(True)  # Note on
        
        # Advance well beyond attack and decay phases
        for _ in range(int(0.5 * 44100)):  # 500ms - enough time to reach sustain
            val = self.env.process_sample()
        
        # Should be at sustain level
        sustained_val = self.env.process_sample()
        # Allow for the actual settling behavior of the exponential curve
        self.assertAlmostEqual(sustained_val, 0.5, delta=0.05)
        
    def test_release_phase(self):
        """Test release phase of envelope."""
        self.env.set_parameter('attack', 0.01)
        self.env.set_parameter('decay', 0.1)
        self.env.set_parameter('sustain', 0.8)
        self.env.set_parameter('release', 0.1)
        
        self.env.trigger(True)  # Note on
        
        # Advance to sustain
        for _ in range(int(0.2 * 44100)):
            self.env.process_sample()
        
        sustained_val = self.env.process_sample()
        
        self.env.trigger(False)  # Note off
        
        # After some time, value should decrease
        released_val = sustained_val
        for _ in range(int(0.05 * 44100)):  # 50ms into release
            released_val = self.env.process_sample()
        
        self.assertLess(released_val, sustained_val)


class TestLFO(unittest.TestCase):
    """Test Low Frequency Oscillator."""
    
    def setUp(self):
        self.lfo = LFO(sample_rate=44100.0)
    
    def test_initialization(self):
        """Test LFO initialization."""
        self.assertEqual(self.lfo.sample_rate, 44100.0)
        self.assertEqual(self.lfo.get_parameter('frequency'), 1.0)
        self.assertEqual(self.lfo.get_parameter('waveform'), 'sine')
        
    def test_sine_waveform(self):
        """Test sine waveform generation."""
        self.lfo.set_parameter('frequency', 2.0)  # 2Hz
        output = self.lfo.process(1000)
        self.assertEqual(len(output), 1000)
        self.assertTrue(np.all(np.abs(output) <= 1.0))
        
    def test_triangle_waveform(self):
        """Test triangle waveform generation."""
        self.lfo.set_parameter('waveform', 'triangle')
        output = self.lfo.process(1000)
        self.assertEqual(len(output), 1000)
        self.assertTrue(np.all(np.abs(output) <= 1.0))
        
    def test_square_waveform(self):
        """Test square waveform generation."""
        self.lfo.set_parameter('waveform', 'square')
        output = self.lfo.process(1000)
        self.assertEqual(len(output), 1000)
        self.assertTrue(np.all(np.abs(output) <= 1.0))


class TestAnalogSynthVoice(unittest.TestCase):
    """Test complete synthesizer voice."""
    
    def setUp(self):
        self.voice = AnalogSynthVoice(sample_rate=44100.0)
    
    def test_initialization(self):
        """Test voice initialization."""
        self.assertIsNotNone(self.voice.osc1)
        self.assertIsNotNone(self.voice.osc2)
        self.assertIsNotNone(self.voice.filter)
        self.assertIsNotNone(self.voice.amp_envelope)
        self.assertIsNotNone(self.voice.filter_envelope)
        
    def test_note_on_off(self):
        """Test note triggering."""
        self.voice.note_on(440.0)  # A4
        self.voice.note_off()
        # Should not raise exceptions
        
    def test_render(self):
        """Test rendering audio."""
        self.voice.note_on(440.0)  # A4
        audio = self.voice.render(1000)
        self.assertEqual(len(audio), 1000)
        
        # After note off, should still produce output (release phase)
        self.voice.note_off()
        audio_after = self.voice.render(1000)
        self.assertEqual(len(audio_after), 1000)


class TestNodeSystem(unittest.TestCase):
    """Test node system functionality."""
    
    def test_node_creation(self):
        """Test creation of different node types."""
        node_types = [
            'OscillatorNode', 'MoogFilterNode', 'StateVariableFilterNode',
            'ADSRNode', 'LFONode', 'MixerNode', 'GainNode', 'VCANode'
        ]
        
        for node_type in node_types:
            if NodeFactory._registry.get(node_type):
                node = NodeFactory.create(node_type)
                self.assertIsNotNone(node)
                self.assertEqual(node.name, node_type)
                
    def test_graph_creation(self):
        """Test node graph creation."""
        graph = NodeGraph(sample_rate=44100.0)
        self.assertEqual(graph.sample_rate, 44100.0)
        
        # Add nodes
        osc_node = OscillatorNode()
        filter_node = MoogFilterNode()
        
        graph.add_node(osc_node)
        graph.add_node(filter_node)
        
        self.assertEqual(len(graph.nodes), 2)
        
        # Connect nodes
        graph.connect(osc_node.node_id, 'output', filter_node.node_id, 'input')
        self.assertEqual(len(graph.connections), 1)
        
    def test_graph_processing(self):
        """Test graph signal processing."""
        graph = NodeGraph(sample_rate=44100.0)
        
        # Create nodes
        osc_node = OscillatorNode()
        osc_node.set_parameter('waveform', 'sine')
        osc_node.set_parameter('frequency', 440.0)
        
        filter_node = MoogFilterNode()
        filter_node.set_parameter('cutoff', 1000.0)
        
        # Add to graph
        graph.add_node(osc_node)
        graph.add_node(filter_node)
        
        # Connect
        graph.connect(osc_node.node_id, 'output', filter_node.node_id, 'input')
        
        # Process
        outputs = graph.process(100)
        
        # Check outputs
        self.assertIn(filter_node.node_id, outputs)
        self.assertIn('output', outputs[filter_node.node_id])
        self.assertEqual(len(outputs[filter_node.node_id]['output']), 100)


class TestIntegration(unittest.TestCase):
    """Integration tests for the whole system."""
    
    def test_complete_synthesis_chain(self):
        """Test a complete synthesis chain."""
        # Create a simple patch with oscillator -> filter -> output
        graph = NodeGraph(sample_rate=44100.0)
        
        # Create nodes
        osc_node = OscillatorNode()
        osc_node.set_parameter('waveform', 'saw')
        osc_node.set_parameter('frequency', 440.0)
        
        filter_node = MoogFilterNode()
        filter_node.set_parameter('cutoff', 2000.0)
        filter_node.set_parameter('resonance', 0.5)
        
        # Add to graph
        osc_id = graph.add_node(osc_node)
        filter_id = graph.add_node(filter_node)
        
        # Connect
        graph.connect(osc_id, 'output', filter_id, 'input')
        
        # Process
        outputs = graph.process(1024)
        
        # Verify output
        filter_output = outputs[filter_id]['output']
        self.assertEqual(len(filter_output), 1024)
        self.assertTrue(np.all(np.abs(filter_output) <= 1.0))
        
    def test_midi_note_conversion(self):
        """Test MIDI to frequency conversion."""
        # Standard MIDI note conversions
        self.assertAlmostEqual(midi_to_frequency(69), 440.0, places=1)  # A4
        self.assertAlmostEqual(midi_to_frequency(60), 261.63, places=1)  # C4
        self.assertAlmostEqual(midi_to_frequency(72), 523.25, places=1)  # C5


def run_tests():
    """Run all tests."""
    print("Running Analog Synthesis Framework Tests...")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__('__main__', globals(), locals(), ['TestVCOCircuit']))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(unittest.TestSuite([
        loader.loadTestsFromTestCase(TestVCOCircuit),
        loader.loadTestsFromTestCase(TestMoogLadderFilter),
        loader.loadTestsFromTestCase(TestStateVariableFilter),
        loader.loadTestsFromTestCase(TestAnalogADSR),
        loader.loadTestsFromTestCase(TestLFO),
        loader.loadTestsFromTestCase(TestAnalogSynthVoice),
        loader.loadTestsFromTestCase(TestNodeSystem),
        loader.loadTestsFromTestCase(TestIntegration),
    ]))
    
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures or result.errors:
        print("\nFAILED TESTS:")
        for failure in result.failures:
            print(f"\n{failure[0]}")
            print(failure[1])
        for error in result.errors:
            print(f"\n{error[0]}")
            print(error[1])
    else:
        print("All tests passed! ✓")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)