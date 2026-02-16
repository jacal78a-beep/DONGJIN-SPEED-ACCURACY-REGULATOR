"""
TRACE Regulator + INTENT Regulator + 곡률 선택기
통합 조절 엔진

- TRACE: 확률 분포 흔들림 제어
- INTENT: 의도 좌표계 제어  
- CURV: 곡률 기반 자연 수렴
"""

from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass
import numpy as np
import logging

logger = logging.getLogger(__name__)


@dataclass
class TraceState:
    """TRACE 상태 변수"""
    
    # 핵심 지표
    H: float = 0.0  # Entropy (불확실성)
    D: float = 0.0  # Drift (판단 흔들림)
    Psi: float = 0.0  # Ψ (인지/확인 비용)
    
    # 보조 지표
    semantic_load: float = 0.0
    dialogue_density: float = 0.0
    
    # 합리 구간 (Reasonable Band)
    in_reasonable_band: bool = False
    
    def compute_reasonable_band(
        self,
        D_max: float = 0.15,
        Psi_max: float = 0.5,
        H_relax: bool = True
    ) -> bool:
        """
        합리 구간 판정
        
        선택강제조절기: (D ≤ Dmax) ∧ (Ψ ≤ Ψmax) ⇒ DECIDE
        H(불확실성)는 처벌 안 함
        """
        d_ok = self.D <= D_max
        psi_ok = self.Psi <= Psi_max
        
        # H는 관대하게 (또는 무시)
        self.in_reasonable_band = d_ok and psi_ok
        
        return self.in_reasonable_band


@dataclass
class IntentSignal:
    """의도 신호"""
    
    goal_vector: np.ndarray  # 목적 신호
    constraint_set: List[str]  # 제약 조건
    tone_bias: float = 0.5  # 톤 편향 (0: formal, 1: casual)
    distance: float = 0.5  # 전문가 거리 (0: expert, 1: novice)
    risk_posture: float = 0.5  # 위험 감수 성향


@dataclass
class CurvatureField:
    """곡률장 (Curvature Field)"""
    
    # V9.6 다차원 의도-곡률 엔진 (MDIC)
    Gamma: float = 1.0  # 맥락적 관성 (흐름 안정성)
    Lambda: float = 1.0  # 의도 부합도 (정렬 강도)
    Phi_Intent: float = 1.0  # 의도적 잠재력 (명령 에너지)
    
    gradient: Optional[np.ndarray] = None  # ∇CURV
    
    def compute_correction(
        self,
        x: np.ndarray,
        context: Dict[str, Any]
    ) -> float:
        """
        보정 함수 R(x,c)
        
        V9.6: R(x,c) = exp(-[∇CURV·Γ + Φ/(Λ+ε)])
        """
        epsilon = 1e-10
        
        if self.gradient is None:
            self.gradient = np.zeros_like(x)
        
        # 곡률 기울기 항
        curv_term = np.dot(self.gradient, x) * self.Gamma
        
        # 의도 정렬 항
        intent_term = self.Phi_Intent / (self.Lambda + epsilon)
        
        # 보정 계수
        R = np.exp(-(curv_term + intent_term))
        
        return float(R)


class UnifiedRegulator:
    """
    통합 조절기
    
    TRACE + INTENT + CURV를 하나의 파이프라인으로 통합
    """
    
    def __init__(
        self,
        dim: int = 128,
        D_max: float = 0.15,
        Psi_max: float = 0.5
    ):
        self.dim = dim
        self.D_max = D_max
        self.Psi_max = Psi_max
        
        # 현재 상태
        self.trace = TraceState()
        self.curvature = CurvatureField()
        self.intent_signal: Optional[IntentSignal] = None
        
        # 이력
        self.trace_history: List[TraceState] = []
        
        logger.info("통합 조절기 초기화 완료")
    
    def extract_intent_signal(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> IntentSignal:
        """
        의도 신호 추출
        
        INTENT REGULATOR: Intent Signal Extraction
        """
        # 간소화된 구현 (실제로는 NLP 모델 사용 가능)
        
        # 목적 벡터 (임베딩)
        goal_vector = np.random.randn(self.dim)
        goal_vector = goal_vector / np.linalg.norm(goal_vector)
        
        # 제약 추출
        constraints = []
        if "빠르게" in user_input or "급" in user_input:
            constraints.append("time_pressure")
        if "정확" in user_input or "꼼꼼" in user_input:
            constraints.append("accuracy_priority")
        
        # 톤 분석
        formal_keywords = ["합니다", "습니다", "되오니"]
        casual_keywords = ["해요", "이에요", "좀"]
        
        formal_count = sum(1 for kw in formal_keywords if kw in user_input)
        casual_count = sum(1 for kw in casual_keywords if kw in user_input)
        
        tone_bias = casual_count / (formal_count + casual_count + 1)
        
        signal = IntentSignal(
            goal_vector=goal_vector,
            constraint_set=constraints,
            tone_bias=tone_bias,
            distance=0.3,  # 기본값
            risk_posture=0.5
        )
        
        self.intent_signal = signal
        logger.debug(f"의도 신호 추출: {len(constraints)}개 제약, 톤={tone_bias:.2f}")
        
        return signal
    
    def update_trace(
        self,
        prob_dist: Optional[np.ndarray] = None,
        prev_output: Optional[str] = None,
        current_output: Optional[str] = None
    ):
        """
        TRACE 지표 업데이트
        
        H: Entropy (확률 분포 넓이)
        D: Drift (출력 흔들림)
        Ψ: 인지/확인 비용
        """
        # Entropy 계산
        if prob_dist is not None:
            prob_dist = prob_dist + 1e-10  # 안정화
            prob_dist = prob_dist / np.sum(prob_dist)
            self.trace.H = -np.sum(prob_dist * np.log(prob_dist))
        
        # Drift 계산 (이전 출력과의 차이)
        if prev_output and current_output:
            # 간소화: 문자열 유사도 기반
            from difflib import SequenceMatcher
            similarity = SequenceMatcher(None, prev_output, current_output).ratio()
            self.trace.D = 1.0 - similarity
        else:
            self.trace.D = 0.0
        
        # Ψ (인지 비용) - 턴 수, 재확인 횟수 등에 비례
        self.trace.Psi = len(self.trace_history) * 0.05
        
        # 합리 구간 판정
        self.trace.compute_reasonable_band(self.D_max, self.Psi_max)
        
        # 이력 저장
        self.trace_history.append(TraceState(
            H=self.trace.H,
            D=self.trace.D,
            Psi=self.trace.Psi,
            in_reasonable_band=self.trace.in_reasonable_band
        ))
        
        logger.debug(
            f"TRACE 업데이트: H={self.trace.H:.3f}, "
            f"D={self.trace.D:.3f}, Ψ={self.trace.Psi:.3f}, "
            f"합리구간={self.trace.in_reasonable_band}"
        )
    
    def update_curvature(
        self,
        intent_alignment: float,
        context_momentum: float = 1.0
    ):
        """
        곡률장 업데이트
        
        V9.6 MDIC:
        - Γ (맥락적 관성): 흐름 안정성
        - Λ (의도 부합도): 정렬 강도
        - Φ (의도 잠재력): 명령 에너지
        """
        self.curvature.Gamma = context_momentum
        self.curvature.Lambda = intent_alignment
        
        # Φ는 의도 신호의 강도
        if self.intent_signal:
            self.curvature.Phi_Intent = np.linalg.norm(
                self.intent_signal.goal_vector
            )
        
        logger.debug(
            f"곡률 업데이트: Γ={self.curvature.Gamma:.3f}, "
            f"Λ={self.curvature.Lambda:.3f}, Φ={self.curvature.Phi_Intent:.3f}"
        )
    
    def should_force_closure(self) -> Tuple[bool, str]:
        """
        강제 닫힘 여부 판정
        
        선택강제조절기: (D ≤ Dmax) ∧ (Ψ ≤ Ψmax) ⇒ DECIDE
        
        Returns:
            (should_close, reason)
        """
        if self.trace.in_reasonable_band:
            return True, "합리 구간 내: 닫힘 허용"
        
        # 개별 조건 체크
        reasons = []
        if self.trace.D > self.D_max:
            reasons.append(f"Drift 초과 ({self.trace.D:.3f} > {self.D_max})")
        if self.trace.Psi > self.Psi_max:
            reasons.append(f"비용 초과 ({self.trace.Psi:.3f} > {self.Psi_max})")
        
        return False, "; ".join(reasons)
    
    def apply_correction(
        self,
        output_vector: np.ndarray,
        context: Dict[str, Any]
    ) -> np.ndarray:
        """
        곡률 보정 적용
        
        V9.6: P'(x|c) = P(x|c) × R(x,c)
        """
        R = self.curvature.compute_correction(output_vector, context)
        corrected = output_vector * R
        
        # 정규화
        corrected = corrected / (np.linalg.norm(corrected) + 1e-10)
        
        logger.debug(f"곡률 보정: R={R:.4f}")
        
        return corrected
    
    def regulate(
        self,
        user_input: str,
        output_candidate: str,
        context: Dict[str, Any],
        prob_dist: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        통합 조절 실행
        
        파이프라인:
        1. 의도 신호 추출
        2. TRACE 업데이트
        3. 곡률장 업데이트
        4. 강제 닫힘 판정
        5. 보정 적용
        """
        # 1. 의도 신호
        signal = self.extract_intent_signal(user_input, context)
        
        # 2. TRACE 업데이트
        prev_output = context.get("previous_output")
        self.update_trace(prob_dist, prev_output, output_candidate)
        
        # 3. 곡률 업데이트
        intent_alignment = 0.8  # 실제로는 계산 필요
        self.update_curvature(intent_alignment)
        
        # 4. 강제 닫힘 판정
        should_close, reason = self.should_force_closure()
        
        # 5. 보정 (벡터로 변환 필요 시)
        # 간소화: 문자열 그대로 반환
        
        result = {
            "regulated_output": output_candidate,
            "should_close": should_close,
            "closure_reason": reason,
            "trace_state": {
                "H": self.trace.H,
                "D": self.trace.D,
                "Psi": self.trace.Psi,
                "in_reasonable_band": self.trace.in_reasonable_band
            },
            "curvature_state": {
                "Gamma": self.curvature.Gamma,
                "Lambda": self.curvature.Lambda,
                "Phi": self.curvature.Phi_Intent
            },
            "intent_signal": {
                "constraints": signal.constraint_set,
                "tone": signal.tone_bias,
                "distance": signal.distance
            }
        }
        
        return result
    
    def get_state_summary(self) -> Dict[str, Any]:
        """현재 상태 요약"""
        return {
            "trace": {
                "H": self.trace.H,
                "D": self.trace.D,
                "Psi": self.trace.Psi,
                "reasonable": self.trace.in_reasonable_band
            },
            "curvature": {
                "Gamma": self.curvature.Gamma,
                "Lambda": self.curvature.Lambda,
                "Phi": self.curvature.Phi_Intent
            },
            "history_length": len(self.trace_history)
        }


if __name__ == "__main__":
    # 테스트
    logging.basicConfig(level=logging.DEBUG)
    
    regulator = UnifiedRegulator(dim=128)
    
    # 시뮬레이션
    user_input = "이 프로젝트를 빠르게 정리해주세요."
    output = "프로젝트 구조를 다음과 같이 정리하겠습니다..."
    
    context = {
        "previous_output": None,
        "turn": 1
    }
    
    result = regulator.regulate(
        user_input=user_input,
        output_candidate=output,
        context=context
    )
    
    print("\n=== 조절 결과 ===")
    print(f"닫힘 허용: {result['should_close']}")
    print(f"이유: {result['closure_reason']}")
    print(f"\nTRACE: {result['trace_state']}")
    print(f"곡률: {result['curvature_state']}")
    print(f"의도: {result['intent_signal']}")
