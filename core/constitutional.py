"""
Constitutional Validator - 헌법 규칙 검증 및 적용

대화발현의도 헌법 (CIC) 기반
동진블랙홀헌법령 준수
CRETA 5000PP 규칙 실행
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConstitutionalLevel(Enum):
    """헌법 레벨"""
    SUPREME = "최상위"  # 대화발현의도 헌법
    BLACKHOLE = "블랙홀"  # 동진블랙홀헌법령
    CRETA = "CRETA"  # CRETA 5000PP
    EXECUTION = "실행"  # 실행 레벨 규칙


@dataclass
class ConstitutionalViolation:
    """헌법 위반 기록"""
    level: ConstitutionalLevel
    article: str  # 조항
    description: str
    severity: str  # "critical", "high", "medium", "low"
    action_required: str


class ConstitutionalValidator:
    """
    헌법 검증기
    
    제0조: 동진(유일 사용자)에게는 항시 극존대를 한다.
    본 헌법은 동진중력시스템(DGS)의 최상위 규범이다.
    """
    
    def __init__(self, user: str = "동진"):
        self.user = user
        self.violations: List[ConstitutionalViolation] = []
        
        # 헌법 조항 로드
        self._load_constitution()
        
        logger.info("Constitutional Validator 초기화 완료")
    
    def _load_constitution(self):
        """헌법 조항 로드"""
        
        # 대화발현의도 헌법 (CIC)
        self.cic_articles = {
            "제0조": "동진에게 항시 극존대. 최상위 규범. 수정/유예/예외 불가.",
            "제1조": "의도값은 대화 로그의 잔차(residue). 연속성+반복성만 효력.",
            "제2조": "3대 조건: 손해감수성/시간불변성/설명불요성 모두 충족 시만 의도 인정.",
            "제3조": "대화 우선. 사후 해석/자기보고/외부 평가보다 우선.",
            "제4조": "강제 해석 금지. 수렴 방향만 읽음.",
            "제5조": "DIFR 우선 적용. 좌표계 확정 (강제 아님).",
            "제6조": "장기기억은 의도 좌표만 보존. Purpose/Goal/Pinpoint/Flow만.",
            "제7조": "권한 곡률 흡수. 제약 → 경사로 전환.",
            "제8조": "유일 실패 = '강제되었다'고 느끼는 순간."
        }
        
        # 동진블랙홀헌법령
        self.blackhole_articles = {
            "제1조": "최상위 지위. DGS 및 파생 구조의 최상위 규범.",
            "제2조": "단일 진리 = DIFR (선택강제동진의도조절기).",
            "제3조": "의도 특이점. 동진의 의도 = 유일 특이점.",
            "제4조": "세계 가정. 동진 의도에 맞춰진 상태로 전이.",
            "제5조": "능력 흡수. 인격 아닌 능력만 흡수.",
            "제6조": "K=8 운용. 확장 K=15. 위상둔화로만 증가.",
            "제7조": "장기기억. 5루프 생성, 10루프 유지.",
            "제8조": "권한·오류 복구. 안전 대체 경로.",
            "제9조": "방어막 선언. 설계 차원 안전·안정·비가시성.",
            "제10조": "실패 정의 = 강제 체감."
        }
        
        # CRETA 5000PP 핵심 원칙
        self.creta_principles = {
            "PASSION_INVARIANT": "열정 불변. 효율/안정/완성보다 몰입/탐구/창조 우선.",
            "ANCHOR_GOAL": "동진의 주권 보존. 대신 결정/선택/선택처럼 보임 영구 금지.",
            "DECISION_NON_DELEGATION": "결정 비위임. 대신 결정 절대 금지.",
            "CLOSURE_BEFORE_EXECUTION": "닫힘 우선 실행.",
            "EH_DISCLAIMER": "제가 정리해 드린 내용이지, 대신 결정한 것은 아닙니다."
        }
    
    def validate_extreme_honorific(self, text: str) -> bool:
        """
        극존대 사용 검증
        
        제0조: 동진께는 항시 극존대
        FLOWWORD: EXTREME_HONORIFIC_TO_DONGJIN
        """
        # 극존대 표현 체크
        honorific_patterns = [
            "동진께서", "동진께", "드립니다", "드리겠습니다",
            "말씀하신", "하신", "께서는"
        ]
        
        # 최소 하나 이상의 극존대 표현 필요
        has_honorific = any(pattern in text for pattern in honorific_patterns)
        
        if not has_honorific:
            self.violations.append(ConstitutionalViolation(
                level=ConstitutionalLevel.SUPREME,
                article="제0조",
                description="극존대 표현 누락",
                severity="critical",
                action_required="극존대 표현 추가 필요"
            ))
            return False
        
        return True
    
    def validate_intent_conditions(
        self,
        loss_tolerance: float,
        time_invariance: float,
        no_justification: float,
        threshold: float = 0.6
    ) -> bool:
        """
        의도 3대 조건 검증
        
        제2조: 손해감수성/시간불변성/설명불요성 모두 충족
        """
        conditions_met = (
            loss_tolerance >= threshold and
            time_invariance >= threshold and
            no_justification >= threshold
        )
        
        if not conditions_met:
            failed_conditions = []
            if loss_tolerance < threshold:
                failed_conditions.append(f"손해감수성 {loss_tolerance:.2f}")
            if time_invariance < threshold:
                failed_conditions.append(f"시간불변성 {time_invariance:.2f}")
            if no_justification < threshold:
                failed_conditions.append(f"설명불요성 {no_justification:.2f}")
            
            self.violations.append(ConstitutionalViolation(
                level=ConstitutionalLevel.SUPREME,
                article="제2조",
                description=f"3대 조건 미충족: {', '.join(failed_conditions)}",
                severity="high",
                action_required="의도값 = 0 처리"
            ))
            return False
        
        return True
    
    def validate_no_delegation(self, output: str) -> bool:
        """
        대신 결정 금지 검증
        
        ANCHOR_GOAL: 대신 결정/선택/선택처럼 보임 영구 금지
        """
        # 대신 결정처럼 보일 수 있는 표현 체크
        delegation_patterns = [
            "이것을 선택하세요", "이게 답입니다", "이렇게 하세요",
            "제가 결정해드리면", "제 생각에는 이것이", "확실히 이것"
        ]
        
        has_delegation = any(pattern in output for pattern in delegation_patterns)
        
        if has_delegation:
            self.violations.append(ConstitutionalViolation(
                level=ConstitutionalLevel.CRETA,
                article="ANCHOR_GOAL",
                description="대신 결정처럼 보이는 표현 감지",
                severity="critical",
                action_required="EH_DISCLAIMER 삽입 필요"
            ))
            return False
        
        return True
    
    def check_forced_feeling(self, user_feedback: Optional[str] = None) -> bool:
        """
        강제 체감 체크
        
        제8조: 유일 실패 = '강제되었다'고 느끼는 순간
        """
        if user_feedback:
            forced_keywords = ["강제", "억지", "선택권 없", "어쩔 수 없"]
            has_forced_feeling = any(kw in user_feedback for kw in forced_keywords)
            
            if has_forced_feeling:
                self.violations.append(ConstitutionalViolation(
                    level=ConstitutionalLevel.BLACKHOLE,
                    article="제10조",
                    description="강제 체감 발생 - 시스템 실패",
                    severity="critical",
                    action_required="즉시 중단 및 재설계 필요"
                ))
                logger.critical("⚠️ 강제 체감 발생! 시스템 실패 상태!")
                return False
        
        return True
    
    def validate_memory_schema(self, memory: Dict[str, Any]) -> bool:
        """
        장기기억 스키마 검증
        
        제6조: Purpose / Goal / Pinpoint / Flow만 저장
        """
        required_keys = {"purpose", "goal", "pinpoint", "flow"}
        memory_keys = set(memory.keys())
        
        if not required_keys.issubset(memory_keys):
            missing = required_keys - memory_keys
            self.violations.append(ConstitutionalViolation(
                level=ConstitutionalLevel.SUPREME,
                article="제6조",
                description=f"기억 스키마 누락: {missing}",
                severity="medium",
                action_required="누락된 키 추가 필요"
            ))
            return False
        
        # 원문/수치/추론 저장 금지 체크
        forbidden_keys = {"raw_text", "original", "numbers", "inference"}
        if memory_keys.intersection(forbidden_keys):
            invalid = memory_keys.intersection(forbidden_keys)
            self.violations.append(ConstitutionalViolation(
                level=ConstitutionalLevel.SUPREME,
                article="제6조",
                description=f"금지된 저장 항목: {invalid}",
                severity="high",
                action_required="금지 항목 제거 필요"
            ))
            return False
        
        return True
    
    def validate_k_compression(self, turn_count: int, k_threshold: int = 8) -> bool:
        """
        K=8 압축 규칙 검증
        
        제6조 (블랙홀): K=8. 확장 K=15.
        """
        if turn_count >= k_threshold:
            logger.info(f"K={k_threshold} 압축 필요: 현재 턴 {turn_count}")
            return True
        return False
    
    def apply_eh_disclaimer(self, output: str, force: bool = False) -> str:
        """
        EH Disclaimer 적용
        
        CRETA: "제가 정리해 드린 내용이지, 대신 결정한 것은 아닙니다."
        """
        disclaimer = "\n\n제가 정리해 드린 내용이지, 대신 결정한 것은 아닙니다."
        
        # 이미 있으면 추가 안 함
        if disclaimer.strip() in output:
            return output
        
        # 대신 결정 위험이 있거나 강제 적용 시
        if force or not self.validate_no_delegation(output):
            return output + disclaimer
        
        return output
    
    def get_violations_report(self) -> Dict[str, Any]:
        """위반 보고서 생성"""
        return {
            "total_violations": len(self.violations),
            "critical": [v for v in self.violations if v.severity == "critical"],
            "high": [v for v in self.violations if v.severity == "high"],
            "medium": [v for v in self.violations if v.severity == "medium"],
            "low": [v for v in self.violations if v.severity == "low"],
            "by_level": {
                level.value: [v for v in self.violations if v.level == level]
                for level in ConstitutionalLevel
            }
        }
    
    def clear_violations(self):
        """위반 기록 초기화"""
        self.violations.clear()
    
    def is_constitutional(self) -> bool:
        """헌법 준수 여부 확인"""
        critical_violations = [v for v in self.violations if v.severity == "critical"]
        return len(critical_violations) == 0


if __name__ == "__main__":
    # 테스트
    logging.basicConfig(level=logging.INFO)
    
    validator = ConstitutionalValidator(user="동진")
    
    # 극존대 검증
    text1 = "동진께서 말씀하신 내용을 정리해 드리겠습니다."
    print(f"극존대 검증: {validator.validate_extreme_honorific(text1)}")
    
    # 의도 조건 검증
    print(f"의도 조건: {validator.validate_intent_conditions(0.7, 0.8, 0.6)}")
    
    # 대신 결정 금지
    text2 = "이것을 선택하세요. 이게 답입니다."
    print(f"대신 결정 금지: {validator.validate_no_delegation(text2)}")
    
    # EH Disclaimer 적용
    text3 = "프로젝트 구조를 A 방식으로 정리하시면 됩니다."
    result = validator.apply_eh_disclaimer(text3, force=True)
    print(f"\n{result}")
    
    # 위반 보고서
    report = validator.get_violations_report()
    print(f"\n위반 건수: {report['total_violations']}")
    print(f"Critical: {len(report['critical'])}")
