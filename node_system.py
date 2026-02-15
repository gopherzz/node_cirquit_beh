"""
Node-Based Analog Synthesis Engine
===================================

A modular node-based system for creating synthesizers and effects chains.
Inspired by modular synthesizers and node-based audio tools like Max/MSP, 
Reaktor, and VCV Rack.

Nodes can be connected together to create complex signal processing chains,
with full support for audio rate and control rate signals.
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum
import json
from dataclasses import dataclass, field
import uuid


# ============================================================================
# CORE NODE SYSTEM
# ============================================================================

class SignalType(Enum):
    """Types of signals that can flow between nodes."""
    AUDIO = "audio"      # Audio rate signals (44100 Hz)
    CONTROL = "control"  # Control rate signals (modulation)
    GATE = "gate"        # Gate/trigger signals (note on/off)
    MIDI = "midi"        # MIDI-style data


@dataclass
class NodePort:
    """Represents an input or output port on a node."""
    name: str
    signal_type: SignalType
    is_input: bool
    node_id: str
    default_value: float = 0.0
    
    def __hash__(self):
        return hash(f"{self.node_id}_{self.name}_{self.is_input}")


@dataclass
class Connection:
    """Represents a connection between two node ports."""
    source_node_id: str
    source_port: str
    dest_node_id: str
    dest_port: str
    connection_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __hash__(self):
        return hash(self.connection_id)


class NodeBase(ABC):
    """
    Base class for all nodes in the synthesis system.
    
    Every node can have multiple inputs and outputs, processes audio/control
    signals, and can be connected to other nodes.
    """
    
    def __init__(self, node_id: Optional[str] = None, sample_rate: float = 44100.0):
        self.node_id = node_id or str(uuid.uuid4())
        self.sample_rate = sample_rate
        self.dt = 1.0 / sample_rate
        
        # Port definitions
        self.input_ports: Dict[str, NodePort] = {}
        self.output_ports: Dict[str, NodePort] = {}
        
        # Incoming connections and their cached values
        self.connections: Dict[str, Connection] = {}
        self.input_buffers: Dict[str, np.ndarray] = {}
        
        # Node state
        self.parameters: Dict[str, Any] = {}
        self._internal_state: Dict[str, Any] = {}
        
        # Metadata
        self.name = self.__class__.__name__
        self.category = "Unknown"
        self.description = ""
        
        # Initialize the node
        self._setup_ports()
        self._setup_parameters()
    
    @abstractmethod
    def _setup_ports(self):
        """Define input and output ports for this node."""
        pass
    
    @abstractmethod
    def _setup_parameters(self):
        """Define parameters for this node."""
        pass
    
    @abstractmethod
    def process(self, buffer_size: int) -> Dict[str, np.ndarray]:
        """
        Process audio/control signals.
        
        Returns:
            Dictionary mapping output port names to signal buffers
        """
        pass
    
    def add_input_port(self, name: str, signal_type: SignalType, default_value: float = 0.0):
        """Add an input port to this node."""
        port = NodePort(
            name=name,
            signal_type=signal_type,
            is_input=True,
            node_id=self.node_id,
            default_value=default_value
        )
        self.input_ports[name] = port
        self.input_buffers[name] = None
    
    def add_output_port(self, name: str, signal_type: SignalType):
        """Add an output port to this node."""
        port = NodePort(
            name=name,
            signal_type=signal_type,
            is_input=False,
            node_id=self.node_id
        )
        self.output_ports[name] = port
    
    def set_parameter(self, name: str, value: Any):
        """Set a parameter value."""
        if name in self.parameters:
            self.parameters[name] = value
        else:
            raise ValueError(f"Unknown parameter: {name}")
    
    def get_parameter(self, name: str) -> Any:
        """Get a parameter value."""
        return self.parameters.get(name)
    
    def get_input(self, port_name: str, buffer_size: int) -> np.ndarray:
        """
        Get input signal from a port.
        Returns default value if not connected.
        """
        if self.input_buffers.get(port_name) is not None:
            return self.input_buffers[port_name]
        else:
            # Return default value
            default = self.input_ports[port_name].default_value
            return np.full(buffer_size, default)
    
    def reset(self):
        """Reset internal state."""
        self._internal_state.clear()


# ============================================================================
# NODE GRAPH / PATCH
# ============================================================================

class NodeGraph:
    """
    Manages a graph of connected nodes (a "patch").
    
    Handles connection management, topological sorting for processing order,
    and signal routing between nodes.
    """
    
    def __init__(self, sample_rate: float = 44100.0):
        self.sample_rate = sample_rate
        self.nodes: Dict[str, NodeBase] = {}
        self.connections: List[Connection] = []
        
        # Processing order (topologically sorted)
        self._processing_order: List[str] = []
        self._dirty = True  # Needs re-sorting
        
        # Metadata
        self.name = "Untitled Patch"
        self.description = ""
    
    def add_node(self, node: NodeBase) -> str:
        """Add a node to the graph."""
        self.nodes[node.node_id] = node
        self._dirty = True
        return node.node_id
    
    def remove_node(self, node_id: str):
        """Remove a node and all its connections."""
        if node_id not in self.nodes:
            return
        
        # Remove all connections involving this node
        self.connections = [
            conn for conn in self.connections
            if conn.source_node_id != node_id and conn.dest_node_id != node_id
        ]
        
        del self.nodes[node_id]
        self._dirty = True
    
    def connect(self, source_node_id: str, source_port: str,
                dest_node_id: str, dest_port: str) -> Connection:
        """Connect two nodes."""
        # Validate nodes exist
        if source_node_id not in self.nodes:
            raise ValueError(f"Source node {source_node_id} not found")
        if dest_node_id not in self.nodes:
            raise ValueError(f"Destination node {dest_node_id} not found")
        
        source_node = self.nodes[source_node_id]
        dest_node = self.nodes[dest_node_id]
        
        # Validate ports exist
        if source_port not in source_node.output_ports:
            raise ValueError(f"Source port {source_port} not found")
        if dest_port not in dest_node.input_ports:
            raise ValueError(f"Destination port {dest_port} not found")
        
        # Check for cycles (would cause infinite loop)
        if self._would_create_cycle(source_node_id, dest_node_id):
            raise ValueError("Connection would create a cycle")
        
        # Create connection
        connection = Connection(
            source_node_id=source_node_id,
            source_port=source_port,
            dest_node_id=dest_node_id,
            dest_port=dest_port
        )
        
        self.connections.append(connection)
        self._dirty = True
        
        return connection
    
    def disconnect(self, connection_id: str):
        """Remove a connection."""
        self.connections = [
            conn for conn in self.connections
            if conn.connection_id != connection_id
        ]
        self._dirty = True
    
    def _would_create_cycle(self, from_node: str, to_node: str) -> bool:
        """Check if adding a connection would create a cycle."""
        # Build adjacency list
        graph = {node_id: [] for node_id in self.nodes}
        for conn in self.connections:
            graph[conn.source_node_id].append(conn.dest_node_id)
        
        # Add potential new connection
        graph[from_node].append(to_node)
        
        # DFS to detect cycle
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph[node]:
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                if has_cycle(node):
                    return True
        
        return False
    
    def _topological_sort(self):
        """Sort nodes in processing order (topological sort)."""
        # Build adjacency list and in-degree count
        graph = {node_id: [] for node_id in self.nodes}
        in_degree = {node_id: 0 for node_id in self.nodes}
        
        for conn in self.connections:
            graph[conn.source_node_id].append(conn.dest_node_id)
            in_degree[conn.dest_node_id] += 1
        
        # Kahn's algorithm
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node_id = queue.pop(0)
            result.append(node_id)
            
            for neighbor in graph[node_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(self.nodes):
            raise RuntimeError("Cycle detected in graph")
        
        self._processing_order = result
        self._dirty = False
    
    def process(self, buffer_size: int) -> Dict[str, Dict[str, np.ndarray]]:
        """
        Process all nodes in the graph.
        
        Returns:
            Dictionary mapping node IDs to their output buffers
        """
        # Update processing order if needed
        if self._dirty:
            self._topological_sort()
        
        # Clear all input buffers
        for node in self.nodes.values():
            for port_name in node.input_buffers:
                node.input_buffers[port_name] = None
        
        # Process nodes in order
        outputs = {}
        
        for node_id in self._processing_order:
            node = self.nodes[node_id]
            
            # Route inputs from connections
            for conn in self.connections:
                if conn.dest_node_id == node_id:
                    source_node = self.nodes[conn.source_node_id]
                    source_output = outputs.get(conn.source_node_id, {})
                    
                    if conn.source_port in source_output:
                        node.input_buffers[conn.dest_port] = source_output[conn.source_port]
            
            # Process this node
            node_outputs = node.process(buffer_size)
            outputs[node_id] = node_outputs
        
        return outputs
    
    def get_output_nodes(self) -> List[NodeBase]:
        """Get all nodes with no outgoing connections (outputs)."""
        output_node_ids = set(self.nodes.keys())
        
        for conn in self.connections:
            if conn.source_node_id in output_node_ids:
                output_node_ids.remove(conn.source_node_id)
        
        return [self.nodes[node_id] for node_id in output_node_ids]
    
    def save_patch(self, filename: str):
        """Save patch to JSON file."""
        patch_data = {
            'name': self.name,
            'description': self.description,
            'sample_rate': self.sample_rate,
            'nodes': [],
            'connections': []
        }
        
        # Serialize nodes
        for node in self.nodes.values():
            node_data = {
                'id': node.node_id,
                'type': node.__class__.__name__,
                'name': node.name,
                'parameters': node.parameters,
            }
            patch_data['nodes'].append(node_data)
        
        # Serialize connections
        for conn in self.connections:
            conn_data = {
                'id': conn.connection_id,
                'source_node': conn.source_node_id,
                'source_port': conn.source_port,
                'dest_node': conn.dest_node_id,
                'dest_port': conn.dest_port,
            }
            patch_data['connections'].append(conn_data)
        
        with open(filename, 'w') as f:
            json.dump(patch_data, f, indent=2)
    
    def get_info(self) -> str:
        """Get human-readable info about the patch."""
        info = []
        info.append(f"Patch: {self.name}")
        info.append(f"Nodes: {len(self.nodes)}")
        info.append(f"Connections: {len(self.connections)}")
        info.append("")
        info.append("Node List:")
        for node in self.nodes.values():
            info.append(f"  - {node.name} ({node.node_id[:8]}...)")
            info.append(f"    Inputs: {list(node.input_ports.keys())}")
            info.append(f"    Outputs: {list(node.output_ports.keys())}")
        return "\n".join(info)


# ============================================================================
# HELPER CLASSES
# ============================================================================

class NodeFactory:
    """Factory for creating nodes by type name."""
    
    _registry: Dict[str, type] = {}
    
    @classmethod
    def register(cls, node_class: type):
        """Register a node class."""
        cls._registry[node_class.__name__] = node_class
        return node_class
    
    @classmethod
    def create(cls, node_type: str, sample_rate: float = 44100.0, **kwargs) -> NodeBase:
        """Create a node by type name."""
        if node_type not in cls._registry:
            raise ValueError(f"Unknown node type: {node_type}")
        
        node_class = cls._registry[node_type]
        return node_class(sample_rate=sample_rate, **kwargs)
    
    @classmethod
    def get_available_nodes(cls) -> List[str]:
        """Get list of available node types."""
        return list(cls._registry.keys())
    
    @classmethod
    def get_node_info(cls, node_type: str) -> Dict[str, Any]:
        """Get information about a node type."""
        if node_type not in cls._registry:
            return {}
        
        node_class = cls._registry[node_type]
        # Create temporary instance to get info
        temp_node = node_class(sample_rate=44100.0)
        
        return {
            'name': node_type,
            'category': temp_node.category,
            'description': temp_node.description,
            'inputs': {name: {'type': port.signal_type.value, 
                            'default': port.default_value}
                      for name, port in temp_node.input_ports.items()},
            'outputs': {name: {'type': port.signal_type.value}
                       for name, port in temp_node.output_ports.items()},
            'parameters': temp_node.parameters,
        }


# ============================================================================
# PARAMETER SMOOTHING (Anti-Zipper)
# ============================================================================

class ParameterSmoother:
    """Smooth parameter changes to prevent zipper noise."""
    
    def __init__(self, sample_rate: float, time_constant: float = 0.01):
        self.sample_rate = sample_rate
        self.time_constant = time_constant
        self.current_value = 0.0
        self.coef = np.exp(-1.0 / (time_constant * sample_rate))
    
    def process(self, target_value: float) -> float:
        """Smooth towards target value."""
        self.current_value = target_value + (self.current_value - target_value) * self.coef
        return self.current_value
    
    def process_buffer(self, target_value: float, buffer_size: int) -> np.ndarray:
        """Generate smoothed buffer."""
        output = np.zeros(buffer_size)
        for i in range(buffer_size):
            output[i] = self.process(target_value)
        return output
    
    def reset(self, value: float = 0.0):
        """Reset to a specific value."""
        self.current_value = value


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def mix_signals(*signals: np.ndarray, weights: Optional[List[float]] = None) -> np.ndarray:
    """Mix multiple signals together with optional weights."""
    if not signals:
        return np.array([])
    
    if weights is None:
        weights = [1.0 / len(signals)] * len(signals)
    
    result = np.zeros_like(signals[0])
    for signal, weight in zip(signals, weights):
        result += signal * weight
    
    return result


def db_to_linear(db: float) -> float:
    """Convert decibels to linear gain."""
    return 10.0 ** (db / 20.0)


def linear_to_db(linear: float) -> float:
    """Convert linear gain to decibels."""
    return 20.0 * np.log10(max(linear, 1e-10))


def midi_to_frequency(midi_note: int) -> float:
    """Convert MIDI note to frequency."""
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))


def frequency_to_midi(frequency: float) -> float:
    """Convert frequency to MIDI note (float)."""
    return 69.0 + 12.0 * np.log2(frequency / 440.0)


# ============================================================================
# SIGNAL GENERATORS
# ============================================================================

def generate_gate(buffer_size: int, gate_on: bool = True) -> np.ndarray:
    """Generate a gate signal."""
    return np.ones(buffer_size) if gate_on else np.zeros(buffer_size)


def generate_trigger(buffer_size: int, trigger_sample: int = 0) -> np.ndarray:
    """Generate a trigger signal (one sample high)."""
    trigger = np.zeros(buffer_size)
    if 0 <= trigger_sample < buffer_size:
        trigger[trigger_sample] = 1.0
    return trigger
