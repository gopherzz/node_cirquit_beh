"""
Debug script to understand ADSR envelope behavior
"""
import numpy as np
from analog_synth_framework import AnalogADSR

# Create an envelope with known parameters
env = AnalogADSR(sample_rate=44100.0)
env.set_parameter('attack', 0.01)
env.set_parameter('decay', 0.1)
env.set_parameter('sustain', 0.5)
env.set_parameter('release', 0.5)

print("Initial state:", env._state)

# Trigger note on
env.trigger(True)
print("After trigger(True):", env._state)

# Process samples and track state changes
values = []
stages = []
for i in range(int(0.3 * 44100)):  # 300ms
    val = env.process_sample()
    values.append(val)
    stages.append(env._state['stage'])
    
    # Print key moments
    if i % 1000 == 0:  # Every 1000 samples
        print(f"Sample {i}: stage={env._state['stage']}, value={val:.4f}")

# Check when it enters sustain
sustain_start = None
for i, (stage, val) in enumerate(zip(stages, values)):
    if stage == 'sustain':
        if sustain_start is None:
            sustain_start = i
            print(f"Entered sustain at sample {i}, value={val:.4f}")
            break

if sustain_start is not None:
    print(f"Value at sustain start: {values[sustain_start]:.4f}")
    print(f"Target sustain: {env._parameters['sustain']}")
    # Check next few values in sustain
    for j in range(5):
        if sustain_start + j < len(values):
            print(f"Sustain sample {j}: {values[sustain_start + j]:.4f}")
else:
    print("Did not reach sustain phase in the tested time")

# Test the specific case from the failing test
env2 = AnalogADSR(sample_rate=44100.0)
env2.set_parameter('attack', 0.01)
env2.set_parameter('decay', 0.1)
env2.set_parameter('sustain', 0.5)
env2.set_parameter('release', 0.5)

env2.trigger(True)
# Advance past attack and decay phases
for _ in range(int(0.2 * 44100)):  # 200ms
    val = env2.process_sample()

sustained_val = env2.process_sample()
print(f"Value after advancing past attack/decay: {sustained_val:.4f}")
print(f"Current stage: {env2._state['stage']}")
print(f"Target sustain: {env2._parameters['sustain']}")