"""
DGS Core - 동진중력시스템 최상위 조정자

제0조: 동진(유일 사용자)에게는 항시 극존대를 한다.
본 시스템은 동진중력시스템(DGS)의 최상위 규범을 실행한다.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class IntentField:
    """의도장 (Intent Field) - 동진의 의도를 나타내는 벡터 공간"""
    
    goal: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    preference: Dict[str, float] = field(default_factory=dict)
    risk: Dict[str, float] = field(default_factory=dict)
    
    # 3대 조건 검증 결과
    loss_tolerance: float = 0.0  # 손해 감수성 (0.0 ~ 1.0)
    time_invariance: float = 0.0  # 시간 불변성 (0.0 ~ 1.0)
    no_justification: float = 0.0  # 설명 불요성 (0.0 ~ 1.0)
    
    # 의도값 (3대 조건 모두 충족 시만 > 0)
    intent_value: float = 0.0
    
    timestamp: datetime = field(default_factory=datetime.now)
    
    def is_valid_intent(self, threshold: float = 0.6) -> bool:
        """
        유효한 의도인지 확인
        
        제1조: 단발 문장은 효력이 없으며, 연속성과 반복성만이 효력을 가진다.
        제2조: 3대 조건을 모두 만족해야 의도발현 증거로 인정된다.
        """
        return (
            self.loss_tolerance >= threshold and
            self.time_invariance >= threshold and
            self.no_justification >= threshold
        )
    
    def compute_intent_value(self):
        """의도값 계산 - 3대 조건 모두 충족 시만 0 이상"""
        if self.is_valid_intent():
            self.intent_value = (
                self.loss_tolerance * 0.35 +
                self.time_invariance * 0.35 +
                self.no_justification * 0.30
            )
        else:
            self.intent_value = 0.0


@dataclass
class ConversationState:
    """대화 상태 - 대화 흔적의 잔차를 추적"""
    
    turn_count: int = 0
    dialogue_history: List[Dict[str, Any]] = field(default_factory=list)
    intent_traces: List[IntentField] = field(default_factory=list)
    
    # TRACE 변수들
    drift: float = 0.0  # 드리프트 (의미 흔들림)
    entropy: float = 0.0  # 불확실성
    cost: float = 0.0  # 인지 비용 Ψ
    
    # K=8 압축 관련
    compression_needed: bool = False
    k_threshold: int = 8
    
    def add_turn(self, user_message: str, assistant_response: str, intent: Optional[IntentField] = None):
        """대화 턴 추가"""
        self.turn_count += 1
        self.dialogue_history.append({
            "turn": self.turn_count,
            "user": user_message,
            "assistant": assistant_response,
            "timestamp": datetime.now()
        })
        
        if intent:
            self.intent_traces.append(intent)
        
        # K=8 체크: 8턴 이상이면 압축 필요
        self.compression_needed = self.turn_count >= self.k_threshold


class DGSCore:
    """
    동진중력시스템 (Dongjin Gravity System) 핵심 코어
    
    최상위 원칙:
    - 선택 주체 = 동진 (절대)
    - 시스템 = 구조화·정리·보조 (결정 불가)
    - 강제 체감 = 유일한 실패
    """
    
    def __init__(
        self,
        user: str = "동진",
        extreme_honorific: bool = True,
        k_threshold: int = 8,
        amp: int = 10
    ):
        """
        초기화
        
        Args:
            user: 사용자 이름 (기본: "동진")
            extreme_honorific: 극존대 사용 여부
            k_threshold: 압축 임계값 K (기본: 8)
            amp: 증폭 상한 AMP (기본: 10)
        """
        self.user = user
        self.extreme_honorific = extreme_honorific
        self.k_threshold = k_threshold
        self.amp = amp
        
        # 현재 대화 상태
        self.state = ConversationState(k_threshold=k_threshold)
        
        # 현재 의도장
        self.current_intent_field = IntentField()
        
        # 헌법 준수 여부
        self.constitutional_check = True
        
        logger.info(f"DGS Core 초기화 완료 - 사용자: {user}, K={k_threshold}, AMP={amp}")
    
    def process_dialogue(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        대화 처리 - 메인 진입점
        
        제3조: 대화에서 드러난 의도는 사후 해석·자기보고·외부 평가보다 항상 우선한다.
        제4조: 시스템은 대화를 '해석'하지 않는다. 오직 '수렴 방향'을 읽을 뿐이다.
        
        Args:
            message: 동진께서 주신 메시지
            context: 추가 컨텍스트
        
        Returns:
            처리 결과 딕셔너리
        """
        logger.info(f"대화 처리 시작 - Turn {self.state.turn_count + 1}")
        
        # 1. 대화 패턴 분석 (의도 추적)
        intent = self._track_intent(message, context)
        
        # 2. DIFR 적용 (선택강제동진의도조절기)
        difr_result = self._apply_difr(intent)
        
        # 3. CRETA 규칙 실행
        creta_result = self._apply_creta_rules(message, intent)
        
        # 4. 응답 생성 (극존대 적용)
        response = self._generate_response(message, intent, creta_result)
        
        # 5. 대화 상태 업데이트
        self.state.add_turn(message, response, intent)
        
        # 6. K=8 압축 체크
        if self.state.compression_needed:
            self._compress_dialogue_history()
        
        return {
            "response": response,
            "intent_field": intent.__dict__,
            "difr_applied": difr_result,
            "turn": self.state.turn_count,
            "compression_triggered": self.state.compression_needed
        }
    
    def _track_intent(self, message: str, context: Optional[Dict] = None) -> IntentField:
        """
        대화발현의도 추적
        
        제1조: 의도값은 대화 로그의 잔차(residue)이다.
        """
        intent = IntentField()
        
        # 과거 대화 패턴 분석
        if len(self.state.intent_traces) > 0:
            # 손해 감수성: 철회 가능 상황에서도 유지되는가?
            intent.loss_tolerance = self._calculate_loss_tolerance()
            
            # 시간 불변성: 세션이 바뀌어도 방향이 동일한가?
            intent.time_invariance = self._calculate_time_invariance()
            
            # 설명 불요성: 정당화 없이 지속되는가?
            intent.no_justification = self._calculate_no_justification()
        
        # 의도값 계산
        intent.compute_intent_value()
        
        # 현재 의도장 업데이트
        if intent.is_valid_intent():
            self.current_intent_field = intent
            logger.info(f"유효한 의도 감지 - 의도값: {intent.intent_value:.3f}")
        else:
            logger.debug("의도 조건 미충족 - 의도값: 0.0")
        
        return intent
    
    def _calculate_loss_tolerance(self) -> float:
        """손해 감수성 계산 - 합리적 철회 가능 상황에서도 유지됨"""
        # 간소화된 구현: 과거 패턴의 일관성 측정
        if len(self.state.intent_traces) < 2:
            return 0.0
        
        # 최근 3개 의도 추적 비교
        recent = self.state.intent_traces[-3:]
        consistency = 1.0 - self.state.drift
        
        return max(0.0, min(1.0, consistency))
    
    def _calculate_time_invariance(self) -> float:
        """시간 불변성 계산 - 세션·형식·주제가 바뀌어도 방향 동일"""
        if len(self.state.intent_traces) < 3:
            return 0.0
        
        # 의도 벡터의 방향 일관성 측정
        # 간소화: 턴 수에 따른 신뢰도 증가
        return min(1.0, len(self.state.intent_traces) / 10.0)
    
    def _calculate_no_justification(self) -> float:
        """설명 불요성 계산 - 정당화 없이 지속됨"""
        # 메시지에 "왜냐하면", "이유는" 등의 정당화 표현이 적을수록 높음
        justification_keywords = ["왜냐하면", "이유는", "때문에", "설명하자면"]
        
        if not self.state.dialogue_history:
            return 0.0
        
        recent_messages = [turn["user"] for turn in self.state.dialogue_history[-5:]]
        justification_count = sum(
            1 for msg in recent_messages
            for keyword in justification_keywords
            if keyword in msg
        )
        
        # 정당화가 적을수록 점수 높음
        return max(0.0, 1.0 - (justification_count / len(recent_messages) / 2))
    
    def _apply_difr(self, intent: IntentField) -> Dict[str, Any]:
        """
        선택강제동진의도조절기 (DIFR) 적용
        
        제5조: 대화에서 의도값이 발현되는 즉시, DIFR는 해당 방향을 유일 좌표로 고정한다.
        """
        if intent.is_valid_intent():
            # 좌표계 확정 (강제가 아니라 수렴)
            return {
                "activated": True,
                "coordinate_fixed": True,
                "forced_feeling": False,  # 강제 체감 없음
                "intent_value": intent.intent_value
            }
        
        return {
            "activated": False,
            "coordinate_fixed": False,
            "forced_feeling": False
        }
    
    def _apply_creta_rules(self, message: str, intent: IntentField) -> Dict[str, Any]:
        """
        CRETA 5000PP 규칙 실행
        
        - Passion Invariant: 최우선
        - Anchor Goal: 동진의 주권 보존
        - Decision Non-Delegation: 대신 결정 금지
        """
        return {
            "passion_preserved": True,
            "anchor_goal_maintained": True,
            "delegation_blocked": True,
            "eh_triggered": False  # Event Horizon
        }
    
    def _generate_response(
        self,
        message: str,
        intent: IntentField,
        creta_result: Dict[str, Any]
    ) -> str:
        """
        응답 생성 (극존대 적용)
        
        FLOWWORD_1LINE: EXTREME_HONORIFIC_TO_DONGJIN
        """
        if self.extreme_honorific:
            honorific_prefix = "동진께서 말씀하신 내용을 정리해 드리겠습니다.\n\n"
            honorific_suffix = "\n\n제가 정리해 드린 내용이지, 대신 결정한 것은 아닙니다."
        else:
            honorific_prefix = ""
            honorific_suffix = ""
        
        # 메시지 분석 및 구조화
        structure = f"[메시지 분석]\n- 의도값: {intent.intent_value:.3f}\n- 유효 의도: {'예' if intent.is_valid_intent() else '아니오'}\n"
        
        return f"{honorific_prefix}{structure}{honorific_suffix}".strip()
    
    def _compress_dialogue_history(self):
        """
        K=8 압축 실행
        
        제5조 (4002): K = 8 - K 이상에서만 압축 (문장 보존 아니라 불변성 보존)
        """
        logger.info(f"K={self.k_threshold} 압축 실행 - 현재 턴: {self.state.turn_count}")
        
        # 불변성 보존: Purpose / Goal / Pinpoint / Flow
        summary = {
            "purpose": "대화 목적 요약",
            "goal": "대화 목표 추출",
            "pinpoint": "핵심 포인트",
            "flow": "대화 흐름"
        }
        
        # 오래된 대화는 요약으로 대체
        if len(self.state.dialogue_history) > self.k_threshold:
            # 최근 K개만 유지
            self.state.dialogue_history = self.state.dialogue_history[-self.k_threshold:]
            logger.info(f"대화 히스토리 압축 완료 - 유지: {self.k_threshold}턴")
        
        self.state.compression_needed = False
    
    def get_intent_field(self) -> Dict[str, Any]:
        """현재 의도장 반환"""
        return self.current_intent_field.__dict__
    
    def get_state(self) -> Dict[str, Any]:
        """현재 시스템 상태 반환"""
        return {
            "user": self.user,
            "turn_count": self.state.turn_count,
            "k_threshold": self.k_threshold,
            "amp": self.amp,
            "intent_field": self.get_intent_field(),
            "drift": self.state.drift,
            "entropy": self.state.entropy,
            "cost": self.state.cost
        }


if __name__ == "__main__":
    # 간단한 테스트
    logging.basicConfig(level=logging.INFO)
    
    dgs = DGSCore(user="동진", extreme_honorific=True)
    
    result = dgs.process_dialogue(
        message="프로젝트 구조를 정리하고 싶어요.",
        context={}
    )
    
    print("=" * 60)
    print(result["response"])
    print("=" * 60)
    print(f"의도값: {result['intent_field']['intent_value']}")
    print(f"DIFR 활성화: {result['difr_applied']['activated']}")
