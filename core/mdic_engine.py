"""Multi-Dimensional Intent-Curvature Engine (MDIC)

Implements the upgraded curvature selection system with:
- Contextual momentum (Γ)
- Intent alignment (Λ)
- Intentional potential (Φ_Intent)

Based on: 다차원곡율선택기.txt v9.6
"""
import numpy as np
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class MDICEngine:
    """다차원 의도-곡률 엔진"""
    
    def __init__(self, epsilon: float = 1e-8):
        self.epsilon = epsilon
        self.gamma_t = 1.0  # Contextual momentum
        self.phi_intent = 1.0  # Intentional potential
        
    def calculate_curvature_correction(self,
                                       x: np.ndarray,
                                       context: np.ndarray,
                                       intent_signal: Optional[np.ndarray] = None) -> float:
        """Calculate curvature correction R(x,c)
        
        R(x,c) = exp(-[∇CURV(x,c) · Γ(t) + Φ_Intent / (Λ(x,c) + ε)])
        
        Args:
            x: Current state vector
            context: Context vector
            intent_signal: Optional intent signal vector
            
        Returns:
            Curvature correction factor
        """
        try:
            # Calculate curvature gradient
            grad_curv = self._compute_curvature_gradient(x, context)
            
            # Calculate intent alignment
            lambda_xc = self._compute_intent_alignment(x, context, intent_signal)
            
            # Apply correction formula - FIX: ensure scalar result
            grad_term = np.dot(grad_curv, np.ones_like(grad_curv)) * self.gamma_t
            if isinstance(grad_term, np.ndarray):
                grad_term = float(grad_term.item()) if grad_term.size == 1 else float(np.sum(grad_term))
            
            correction = np.exp(-(
                grad_term + 
                self.phi_intent / (lambda_xc + self.epsilon)
            ))
            
            return float(correction)
            
        except Exception as e:
            logger.error(f"MDIC curvature correction failed: {e}")
            return 1.0
    
    def _compute_curvature_gradient(self, x: np.ndarray, c: np.ndarray) -> np.ndarray:
        """Compute curvature gradient ∇CURV(x,c)"""
        # Simplified curvature gradient based on state-context divergence
        if len(x) != len(c):
            # Adjust dimensions if necessary
            min_len = min(len(x), len(c))
            x = x[:min_len]
            c = c[:min_len]
        
        gradient = x - c
        norm = np.linalg.norm(gradient)
        if norm > self.epsilon:
            gradient = gradient / norm
        
        return gradient
    
    def _compute_intent_alignment(self,
                                  x: np.ndarray,
                                  c: np.ndarray,
                                  intent: Optional[np.ndarray] = None) -> float:
        """Compute intent alignment Λ(x,c)
        
        Higher Λ means better alignment with user's intent
        """
        if intent is None:
            # Default alignment based on state-context similarity
            if len(x) != len(c):
                min_len = min(len(x), len(c))
                x = x[:min_len]
                c = c[:min_len]
            
            similarity = np.dot(x, c) / (np.linalg.norm(x) * np.linalg.norm(c) + self.epsilon)
            return float(max(0.0, similarity))
        else:
            # Alignment with explicit intent signal
            if len(x) != len(intent):
                min_len = min(len(x), len(intent))
                x = x[:min_len]
                intent = intent[:min_len]
            
            alignment = np.dot(x, intent) / (np.linalg.norm(x) * np.linalg.norm(intent) + self.epsilon)
            return float(max(0.0, alignment))
    
    def update_contextual_momentum(self, new_gamma: float):
        """Update contextual momentum Γ(t)"""
        self.gamma_t = max(0.0, new_gamma)
    
    def update_intentional_potential(self, new_phi: float):
        """Update intentional potential Φ_Intent"""
        self.phi_intent = max(0.0, new_phi)
    
    def predictive_terrain_design(self,
                                  current_state: np.ndarray,
                                  future_states: list,
                                  context: np.ndarray) -> Dict:
        """Design predictive terrain considering future states
        
        Implements '예측적 지형 설계' from theory
        """
        corrections = []
        
        for future_state in future_states:
            correction = self.calculate_curvature_correction(
                np.array(future_state),
                context
            )
            corrections.append(correction)
        
        return {
            'corrections': corrections,
            'mean_correction': np.mean(corrections),
            'smoothness': 1.0 / (np.std(corrections) + self.epsilon)
        }
