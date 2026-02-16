"""RLT3 Engine - Reference-Loop-Trace v3

Implements structured alignment analysis with:
- Cycle detection
- Alignment strength measurement
- Phase tracking
- Reference strength calculation

Based on: RLT3.txt
"""
import numpy as np
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class RLT3Engine:
    """RLT3 구조 정렬 분석 엔진"""
    
    def __init__(self, precision: int = 8, loop_window: int = 10):
        """
        Args:
            precision: Decimal precision for signature hashing
            loop_window: Window size for loop detection (N parameter)
        """
        self.precision = precision
        self.loop_window = loop_window
        self.seen = {}  # signature -> step mapping
        self.cycle_history = []
        
    def signature(self, state: np.ndarray) -> int:
        """Generate state signature for cycle detection
        
        Args:
            state: Current state vector
            
        Returns:
            Hash signature
        """
        try:
            rounded = tuple(round(float(v), self.precision) for v in state)
            return hash(rounded)
        except Exception as e:
            logger.error(f"Signature generation failed: {e}")
            return 0
    
    def detect_cycle(self, sig: int, step: int) -> Tuple[bool, int]:
        """Detect if current signature indicates a cycle
        
        Args:
            sig: State signature
            step: Current step number
            
        Returns:
            (cycle_detected, cycle_length)
        """
        if sig in self.seen:
            cycle_length = step - self.seen[sig]
            self.cycle_history.append(cycle_length)
            return True, cycle_length
        
        self.seen[sig] = step
        return False, 0
    
    def alignment_strength(self,
                          state: np.ndarray,
                          direction_delta: np.ndarray,
                          epsilon: float = 1e-8) -> float:
        """Calculate alignment strength
        
        AlignmentStrength = ||S(t)|| / (||S(t)|| + ||ΔD(t)|| + ε)
        
        Args:
            state: Current state vector S(t)
            direction_delta: Direction change rate ΔD(t)
            epsilon: Small constant for stability
            
        Returns:
            Alignment strength [0, 1]
        """
        try:
            norm_state = np.linalg.norm(state)
            norm_delta = np.linalg.norm(direction_delta)
            
            alignment = norm_state / (norm_state + norm_delta + epsilon)
            
            return float(np.clip(alignment, 0.0, 1.0))
            
        except Exception as e:
            logger.error(f"Alignment strength calculation failed: {e}")
            return 0.0
    
    def phase_index(self, step: int, cycle_length: int) -> int:
        """Calculate phase index within cycle
        
        PhaseIndex = current_step % cycle_length
        
        Args:
            step: Current step
            cycle_length: Detected cycle length
            
        Returns:
            Phase index within cycle
        """
        if cycle_length == 0:
            return 0
        return step % cycle_length
    
    def reference_strength(self,
                          alignment: float,
                          phase: int,
                          w1: float = 1.0,
                          w2: float = 1.0) -> float:
        """Calculate reference strength
        
        RS = w1 * AlignmentStrength + w2 * (1 / (1 + PhaseIndex))
        
        Args:
            alignment: Alignment strength
            phase: Phase index
            w1, w2: Weighting factors
            
        Returns:
            Reference strength
        """
        try:
            rs = w1 * alignment + w2 * (1.0 / (1.0 + phase))
            return float(np.clip(rs, 0.0, 1.0))
        except Exception as e:
            logger.error(f"Reference strength calculation failed: {e}")
            return 0.0
    
    def evaluate(self,
                state: np.ndarray,
                direction_delta: np.ndarray,
                step: int) -> Dict:
        """Comprehensive RLT3 evaluation
        
        Args:
            state: Current state vector
            direction_delta: Direction change vector
            step: Current step number
            
        Returns:
            Dictionary with all RLT3 metrics
        """
        try:
            # Generate signature and detect cycle
            sig = self.signature(state)
            cycle_detected, cycle_length = self.detect_cycle(sig, step)
            
            # Calculate alignment strength
            alignment = self.alignment_strength(state, direction_delta)
            
            # Calculate phase index
            phase = self.phase_index(step, cycle_length)
            
            # Calculate reference strength
            ref_strength = self.reference_strength(alignment, phase)
            
            return {
                'signature': sig,
                'cycle_detected': cycle_detected,
                'cycle_length': cycle_length,
                'alignment_strength': alignment,
                'phase_index': phase,
                'reference_strength': ref_strength,
                'step': step
            }
            
        except Exception as e:
            logger.error(f"RLT3 evaluation failed: {e}")
            return {
                'signature': 0,
                'cycle_detected': False,
                'cycle_length': 0,
                'alignment_strength': 0.0,
                'phase_index': 0,
                'reference_strength': 0.0,
                'step': step
            }
    
    def get_cycle_statistics(self) -> Dict:
        """Get statistics about detected cycles
        
        Returns:
            Dictionary with cycle statistics
        """
        if not self.cycle_history:
            return {
                'total_cycles': 0,
                'average_length': 0.0,
                'min_length': 0,
                'max_length': 0
            }
        
        return {
            'total_cycles': len(self.cycle_history),
            'average_length': np.mean(self.cycle_history),
            'min_length': np.min(self.cycle_history),
            'max_length': np.max(self.cycle_history)
        }
    
    def reset(self):
        """Reset cycle detection state"""
        self.seen = {}
        self.cycle_history = []
