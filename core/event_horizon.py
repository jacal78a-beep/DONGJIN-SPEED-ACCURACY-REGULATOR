"""Event Horizon Module

Implements probability collapse mechanism when intent reaches singularity.

Based on: 사건의지평선.txt
"""
import numpy as np
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class EventHorizon:
    """사건의 지평선 - Probability collapse mechanism"""
    
    def __init__(self, 
                 epsilon: float = 1e-8,
                 horizon_threshold: float = 0.95):
        """
        Args:
            epsilon: Small constant for numerical stability
            horizon_threshold: Threshold for probability collapse (default: 0.95)
        """
        self.epsilon = epsilon
        self.horizon_threshold = horizon_threshold
        
    def check_horizon_crossing(self,
                              H: float,
                              D: float,
                              C: float,
                              reasonable_band: Tuple[float, float] = (0.1, 10.0)) -> bool:
        """Check if state has crossed event horizon
        
        Args:
            H: Entropy measure
            D: Drift measure  
            C: Cost measure
            reasonable_band: (min, max) values defining reasonable range
            
        Returns:
            True if horizon crossed (singularity reached)
        """
        # Check if all metrics are within reasonable band
        min_val, max_val = reasonable_band
        
        if not (min_val <= H <= max_val):
            return False
        if not (min_val <= D <= max_val):
            return False
        if not (min_val <= C <= max_val):
            return False
            
        # Calculate collapse acceleration S(Λ)
        denominator = H * D * C + self.epsilon
        S_lambda = 1.0 / denominator
        
        # Check if acceleration exceeds threshold
        return S_lambda > self.horizon_threshold
    
    def calculate_collapse_constant(self,
                                    H: float,
                                    D: float,
                                    C: float,
                                    lambda_alignment: float) -> float:
        """Calculate probability collapse constant S(Λ)
        
        S(Λ) = 1 / (H · D · C + ε) if (H,D,C) in reasonable band
        
        Args:
            H: Entropy (should be low for collapse)
            D: Drift (should be low for collapse)
            C: Cost (should be low for collapse)
            lambda_alignment: Intent alignment measure
            
        Returns:
            Collapse acceleration constant
        """
        try:
            denominator = H * D * C + self.epsilon
            S = 1.0 / denominator
            
            # Scale by intent alignment
            S_scaled = S * lambda_alignment
            
            return float(S_scaled)
            
        except Exception as e:
            logger.error(f"Collapse constant calculation failed: {e}")
            return 0.0
    
    def apply_probability_collapse(self,
                                   probabilities: np.ndarray,
                                   S_lambda: float) -> np.ndarray:
        """Apply probability collapse using S(Λ)
        
        P'(x|c) = norm(P(x|c) · R(x,c) · S(Λ))
        
        Args:
            probabilities: Original probability distribution
            S_lambda: Collapse constant
            
        Returns:
            Collapsed probability distribution
        """
        try:
            # Apply collapse acceleration
            collapsed = probabilities * S_lambda
            
            # Normalize
            total = np.sum(collapsed)
            if total > self.epsilon:
                collapsed = collapsed / total
            else:
                # If sum is too small, return uniform
                collapsed = np.ones_like(probabilities) / len(probabilities)
            
            return collapsed
            
        except Exception as e:
            logger.error(f"Probability collapse failed: {e}")
            return probabilities
    
    def get_horizon_state(self,
                         H: float,
                         D: float,
                         C: float,
                         lambda_alignment: float) -> Dict:
        """Get comprehensive horizon state
        
        Returns:
            Dictionary containing horizon metrics and state
        """
        crossed = self.check_horizon_crossing(H, D, C)
        S = self.calculate_collapse_constant(H, D, C, lambda_alignment)
        
        return {
            'horizon_crossed': crossed,
            'collapse_constant': S,
            'entropy': H,
            'drift': D,
            'cost': C,
            'alignment': lambda_alignment,
            'phase': self._determine_phase(H, D, C, lambda_alignment)
        }
    
    def _determine_phase(self,
                        H: float,
                        D: float,
                        C: float,
                        lambda_alignment: float) -> str:
        """Determine current phase relative to horizon
        
        Returns:
            Phase name: 'intent_generation', 'intent_concentration', 
                       'horizon_approach', 'singularity'
        """
        # Calculate combined metric
        combined = H * D * C
        
        if combined > 1.0:
            return 'intent_generation'
        elif combined > 0.1:
            return 'intent_concentration'
        elif combined > 0.01:
            return 'horizon_approach'
        else:
            if lambda_alignment > 0.8:
                return 'singularity'
            else:
                return 'horizon_approach'
    
    def smooth_rejection(self,
                        state: np.ndarray,
                        forbidden_direction: np.ndarray) -> np.ndarray:
        """Apply smooth rejection (부드러운 거부)
        
        Instead of hard blocking, creates energy gradient away from 
        forbidden directions.
        
        Args:
            state: Current state vector
            forbidden_direction: Direction to discourage
            
        Returns:
            Modified state with smooth rejection applied
        """
        try:
            # Normalize forbidden direction
            forbidden_norm = np.linalg.norm(forbidden_direction)
            if forbidden_norm > self.epsilon:
                forbidden_unit = forbidden_direction / forbidden_norm
            else:
                return state
            
            # Calculate projection onto forbidden direction
            projection = np.dot(state, forbidden_unit)
            
            # Apply smooth rejection (exponential decay)
            rejection_strength = np.exp(-abs(projection))
            
            # Modify state
            rejected_state = state - projection * forbidden_unit * (1 - rejection_strength)
            
            return rejected_state
            
        except Exception as e:
            logger.error(f"Smooth rejection failed: {e}")
            return state
