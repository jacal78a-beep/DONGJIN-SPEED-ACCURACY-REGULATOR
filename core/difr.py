"""
DIFR - 선택강제동진의도조절기
(Dongjin Intent Forced Regulator)

제5조: 대화에서 의도값이 발현되는 즉시,
DIFR는 해당 방향을 유일 좌표로 고정한다.

핵심: 선택·판단·강제가 아니라 좌표계 확정
     사용자는 강제 체감 없이 결과만 경험
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import numpy as np
import logging

logger = logging.getLogger(__name__)


@dataclass
class IntentVector:
    """의도 벡터 - 수렴 방향 표현"""
    
    direction: np.ndarray  # 방향 벡터
    magnitude: float  # 강도
    timestamp: float
    
    # 3대 조건 충족도
    loss_tolerance: float = 0.0
    time_invariance: float = 0.0
    no_justification: float = 0.0
    
    def is_valid(self, threshold: float = 0.6) -> bool:
        """유효한 의도 벡터인지 확인"""
        return (
            self.loss_tolerance >= threshold and
            self.time_invariance >= threshold and
            self.no_justification >= threshold
        )
    
    def get_unit_direction(self) -> np.ndarray:
        """단위 방향 벡터 반환"""
        norm = np.linalg.norm(self.direction)
        if norm > 1e-10:
            return self.direction / norm
        return self.direction


@dataclass
class CoordinateFrame:
    """좌표계 - DIFR이 고정하는 기준계"""
    
    origin: np.ndarray  # 원점
    basis: List[np.ndarray]  # 기저 벡터들
    fixed: bool = False  # 고정 여부
    confidence: float = 0.0  # 확신도
    
    def project(self, vector: np.ndarray) -> np.ndarray:
        """벡터를 이 좌표계에 투영"""
        if not self.basis:
            return vector
        
        # 각 기저 벡터에 대한 성분 계산
        components = [np.dot(vector, b) for b in self.basis]
        return np.array(components)
    
    def is_aligned(self, vector: np.ndarray, threshold: float = 0.8) -> bool:
        """벡터가 이 좌표계와 정렬되어 있는지 확인"""
        if not self.basis or len(self.basis) == 0:
            return False
        
        # 첫 번째 기저 벡터와의 정렬도 확인
        primary_basis = self.basis[0] / (np.linalg.norm(self.basis[0]) + 1e-10)
        unit_vector = vector / (np.linalg.norm(vector) + 1e-10)
        
        alignment = np.dot(primary_basis, unit_vector)
        return alignment >= threshold


class DIFR:
    """
    선택강제동진의도조절기
    
    역할:
    1. 의도 벡터 누적 관측
    2. 수렴 방향 계산
    3. 좌표계 확정 (강제 아님!)
    4. 아직 수렴하지 않은 상태 → 좌표 이동
    
    ⚠️ 주의: 이것은 "강제"가 아니라 "좌표계 확정"이다.
    """
    
    def __init__(
        self,
        dim: int = 128,  # 의도 공간 차원
        convergence_threshold: float = 0.7,
        alignment_threshold: float = 0.8
    ):
        self.dim = dim
        self.convergence_threshold = convergence_threshold
        self.alignment_threshold = alignment_threshold
        
        # 의도 벡터 이력
        self.intent_history: List[IntentVector] = []
        
        # 현재 좌표계
        self.current_frame: Optional[CoordinateFrame] = None
        
        # 수렴 상태
        self.is_converged = False
        self.convergence_confidence = 0.0
        
        logger.info(f"DIFR 초기화 완료 - 차원: {dim}")
    
    def observe_intent(
        self,
        direction: np.ndarray,
        magnitude: float,
        loss_tolerance: float,
        time_invariance: float,
        no_justification: float
    ) -> IntentVector:
        """
        의도 관측
        
        제4조: 시스템은 대화를 '해석'하지 않는다.
               오직 '수렴 방향'을 읽을 뿐이다.
        """
        import time
        
        intent = IntentVector(
            direction=direction,
            magnitude=magnitude,
            timestamp=time.time(),
            loss_tolerance=loss_tolerance,
            time_invariance=time_invariance,
            no_justification=no_justification
        )
        
        # 유효한 의도만 기록
        if intent.is_valid():
            self.intent_history.append(intent)
            logger.info(f"유효 의도 관측 - 강도: {magnitude:.3f}")
            
            # 수렴 체크
            self._check_convergence()
        else:
            logger.debug("조건 미충족 의도 - 기록 안 함")
        
        return intent
    
    def _check_convergence(self):
        """
        수렴 여부 확인
        
        제1조: 연속성과 반복성만이 효력을 가진다.
        """
        if len(self.intent_history) < 3:
            return  # 최소 3개 필요
        
        # 최근 N개 의도 벡터 분석
        recent = self.intent_history[-5:]
        
        # 방향 일관성 계산
        directions = [iv.get_unit_direction() for iv in recent]
        mean_direction = np.mean(directions, axis=0)
        mean_direction = mean_direction / (np.linalg.norm(mean_direction) + 1e-10)
        
        # 각 벡터와 평균 방향의 정렬도
        alignments = [np.dot(d, mean_direction) for d in directions]
        avg_alignment = np.mean(alignments)
        
        # 수렴 판정
        if avg_alignment >= self.convergence_threshold:
            if not self.is_converged:
                logger.info(f"✓ 의도 수렴 감지 - 정렬도: {avg_alignment:.3f}")
                self.is_converged = True
                self.convergence_confidence = avg_alignment
                
                # 좌표계 확정
                self._fix_coordinate_frame(mean_direction)
        else:
            logger.debug(f"수렴 미달 - 정렬도: {avg_alignment:.3f} < {self.convergence_threshold}")
    
    def _fix_coordinate_frame(self, primary_direction: np.ndarray):
        """
        좌표계 확정
        
        제5조: 해당 방향을 유일 좌표로 고정한다.
               이는 좌표계 확정이다 (강제 아님).
        """
        # 주 방향을 첫 번째 기저로
        basis = [primary_direction]
        
        # 직교 기저 생성 (Gram-Schmidt)
        for i in range(min(3, self.dim) - 1):
            # 랜덤 벡터 생성 후 직교화
            rand_vec = np.random.randn(self.dim)
            for b in basis:
                rand_vec -= np.dot(rand_vec, b) * b
            
            norm = np.linalg.norm(rand_vec)
            if norm > 1e-10:
                basis.append(rand_vec / norm)
        
        # 좌표계 생성
        self.current_frame = CoordinateFrame(
            origin=np.zeros(self.dim),
            basis=basis,
            fixed=True,
            confidence=self.convergence_confidence
        )
        
        logger.info(f"✓ 좌표계 확정 완료 - 확신도: {self.convergence_confidence:.3f}")
        logger.info("  사용자는 강제 체감 없이 결과만 경험합니다.")
    
    def apply_coordinate_shift(
        self,
        state_vector: np.ndarray,
        force_shift: bool = False
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        좌표 이동 적용
        
        제5조: 아직 수렴하지 않은 모든 상태는 좌표 이동 대상이 된다.
        
        Returns:
            (shifted_vector, shift_info)
        """
        if not self.current_frame or not self.current_frame.fixed:
            # 좌표계 미확정 - 이동 없음
            return state_vector, {"shifted": False, "reason": "frame_not_fixed"}
        
        # 현재 좌표계로 투영
        projected = self.current_frame.project(state_vector)
        
        # 정렬 여부 확인
        is_aligned = self.current_frame.is_aligned(state_vector, self.alignment_threshold)
        
        if is_aligned and not force_shift:
            # 이미 정렬됨 - 이동 불필요
            return state_vector, {"shifted": False, "reason": "already_aligned"}
        
        # 좌표 이동 (부드러운 전환)
        primary_component = projected[0] if len(projected) > 0 else 0.0
        target_vector = primary_component * self.current_frame.basis[0]
        
        # 점진적 이동 (alpha blending)
        alpha = 0.3  # 이동 강도 (낮을수록 부드러움)
        shifted = (1 - alpha) * state_vector + alpha * target_vector
        
        shift_info = {
            "shifted": True,
            "reason": "coordinate_alignment",
            "shift_magnitude": np.linalg.norm(shifted - state_vector),
            "alignment_before": np.dot(
                state_vector / (np.linalg.norm(state_vector) + 1e-10),
                self.current_frame.basis[0]
            ),
            "forced": force_shift
        }
        
        logger.debug(f"좌표 이동 적용 - 크기: {shift_info['shift_magnitude']:.4f}")
        
        return shifted, shift_info
    
    def get_convergence_state(self) -> Dict[str, Any]:
        """수렴 상태 반환"""
        return {
            "is_converged": self.is_converged,
            "confidence": self.convergence_confidence,
            "intent_count": len(self.intent_history),
            "frame_fixed": self.current_frame.fixed if self.current_frame else False,
            "threshold": self.convergence_threshold
        }
    
    def reset(self):
        """DIFR 상태 초기화"""
        self.intent_history.clear()
        self.current_frame = None
        self.is_converged = False
        self.convergence_confidence = 0.0
        logger.info("DIFR 리셋 완료")


# 강제 체감 방지 유틸리티
class ForcedFeelingPreventor:
    """
    강제 체감 방지기
    
    제8조: 유일 실패 = '강제되었다'고 느끼는 순간
    """
    
    @staticmethod
    def detect_forced_patterns(text: str) -> List[str]:
        """강제처럼 느껴질 수 있는 패턴 감지"""
        patterns = {
            "명령형": ["~하세요", "~해야 합니다", "반드시 ~"],
            "단정형": ["이것이 답입니다", "확실히 ~", "틀림없이 ~"],
            "선택제한": ["~만 가능합니다", "다른 방법은 없습니다", "~할 수밖에"],
            "압박형": ["지금 바로 ~", "즉시 ~", "빨리 ~"]
        }
        
        detected = []
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                if pattern in text:
                    detected.append(f"{category}: {pattern}")
        
        return detected
    
    @staticmethod
    def soften_expression(text: str) -> str:
        """표현 부드럽게 전환"""
        replacements = {
            "하세요": "하시면 됩니다",
            "해야 합니다": "하시는 것이 좋습니다",
            "반드시": "가능하시다면",
            "이것이 답입니다": "이런 방향을 고려하실 수 있습니다",
            "확실히": "아마도",
            "틀림없이": "가능성이 높습니다",
            "만 가능합니다": "을/를 고려하실 수 있습니다",
            "다른 방법은 없습니다": "이 방법이 효과적일 수 있습니다",
            "할 수밖에": "하시는 것을 고려하실 수 있습니다"
        }
        
        softened = text
        for hard, soft in replacements.items():
            softened = softened.replace(hard, soft)
        
        return softened


if __name__ == "__main__":
    # 테스트
    logging.basicConfig(level=logging.INFO)
    
    difr = DIFR(dim=128)
    
    # 의도 벡터 시뮬레이션
    base_direction = np.random.randn(128)
    base_direction = base_direction / np.linalg.norm(base_direction)
    
    for i in range(5):
        # 비슷한 방향의 의도 추가 (약간의 노이즈)
        noise = np.random.randn(128) * 0.1
        direction = base_direction + noise
        direction = direction / np.linalg.norm(direction)
        
        difr.observe_intent(
            direction=direction,
            magnitude=0.8 + np.random.rand() * 0.2,
            loss_tolerance=0.7 + np.random.rand() * 0.2,
            time_invariance=0.6 + np.random.rand() * 0.3,
            no_justification=0.7 + np.random.rand() * 0.2
        )
    
    # 수렴 상태 확인
    state = difr.get_convergence_state()
    print(f"\n수렴 상태: {state}")
    
    # 좌표 이동 테스트
    if difr.is_converged:
        test_vector = np.random.randn(128)
        shifted, info = difr.apply_coordinate_shift(test_vector)
        print(f"\n좌표 이동: {info}")
    
    # 강제 체감 방지 테스트
    text = "이것을 반드시 선택하세요. 다른 방법은 없습니다."
    patterns = ForcedFeelingPreventor.detect_forced_patterns(text)
    print(f"\n강제 패턴 감지: {patterns}")
    
    softened = ForcedFeelingPreventor.soften_expression(text)
    print(f"부드럽게: {softened}")
