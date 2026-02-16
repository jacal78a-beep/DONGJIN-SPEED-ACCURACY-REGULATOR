#!/usr/bin/env python3
"""
DGS Auxiliary Engine - 메인 실행 스크립트

동진께서 주신 모든 이론을 통합한 GPT 능력 향상 보조 엔진
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.dgs_core import DGSCore
from core.constitutional import ConstitutionalValidator
from core.difr import DIFR, ForcedFeelingPreventor
from engines.unified_regulator import UnifiedRegulator

import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def print_banner():
    """시스템 배너 출력"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🚀 DGS Auxiliary Engine v1.0-alpha                          ║
║   동진중력시스템 GPT 능력 향상 보조 엔진                        ║
║                                                               ║
║   Owner: 동진님 (Extreme Honorific Applied)                   ║
║   Constitutional Foundation: CIC + 동진블랙홀헌법령 + CRETA 5000PP ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def run_interactive_demo():
    """대화형 데모 실행"""
    print_banner()
    
    print("\n📚 시스템 초기화 중...")
    
    # 핵심 시스템 초기화
    dgs = DGSCore(user="동진", extreme_honorific=True, k_threshold=8, amp=10)
    validator = ConstitutionalValidator(user="동진")
    difr = DIFR(dim=128)
    regulator = UnifiedRegulator(dim=128)
    
    print("✅ 초기화 완료!\n")
    
    print("=" * 70)
    print("대화형 모드 시작")
    print("종료하려면 'quit' 또는 'exit'를 입력하세요.")
    print("=" * 70)
    print()
    
    conversation_history = []
    turn = 0
    
    while True:
        # 사용자 입력
        try:
            user_message = input("동진님> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n시스템을 종료합니다.")
            break
        
        if not user_message:
            continue
        
        if user_message.lower() in ['quit', 'exit', '종료', '나가기']:
            print("\n시스템을 종료합니다.")
            break
        
        turn += 1
        print()
        
        # DGS Core 처리
        result = dgs.process_dialogue(
            message=user_message,
            context={"history": conversation_history, "turn": turn}
        )
        
        # 응답
        response = result["response"]
        
        # 헌법 검증
        validator.clear_violations()
        validator.validate_extreme_honorific(response)
        validator.validate_no_delegation(response)
        
        # 위반 있으면 EH Disclaimer 추가
        if not validator.is_constitutional():
            response = validator.apply_eh_disclaimer(response, force=True)
        
        # 강제 체감 방지 체크
        forced_patterns = ForcedFeelingPreventor.detect_forced_patterns(response)
        if forced_patterns:
            print("⚠️  강제 패턴 감지:", forced_patterns)
            response = ForcedFeelingPreventor.soften_expression(response)
        
        # 응답 출력
        print(f"DGS> {response}")
        print()
        
        # 상태 정보 (옵션)
        if turn % 3 == 0:  # 3턴마다 출력
            print("─" * 70)
            print("📊 시스템 상태:")
            state = dgs.get_state()
            print(f"  • 턴: {state['turn_count']}")
            print(f"  • 의도값: {state['intent_field']['intent_value']:.3f}")
            print(f"  • Drift: {state['drift']:.3f}")
            print(f"  • K 압축 임계: {state['k_threshold']}")
            
            conv_state = difr.get_convergence_state()
            print(f"  • DIFR 수렴: {'예' if conv_state['is_converged'] else '아니오'}")
            print(f"  • 수렴 확신도: {conv_state['confidence']:.3f}")
            
            violations = validator.get_violations_report()
            print(f"  • 헌법 위반: {violations['total_violations']}건")
            print("─" * 70)
            print()
        
        conversation_history.append({
            "user": user_message,
            "assistant": response,
            "turn": turn
        })


def run_batch_test():
    """배치 테스트 실행"""
    print_banner()
    
    print("\n🧪 배치 테스트 모드\n")
    
    # 테스트 케이스
    test_cases = [
        {
            "message": "프로젝트 구조를 어떻게 정리하면 좋을까요?",
            "expected": ["정리", "구조", "드립니다"]
        },
        {
            "message": "이 코드를 최적화해주세요.",
            "expected": ["최적화", "고려", "방법"]
        },
        {
            "message": "지금 바로 결정해주세요.",
            "expected": ["정리", "결정한 것은 아닙니다"]  # EH Disclaimer
        }
    ]
    
    dgs = DGSCore(user="동진", extreme_honorific=True)
    validator = ConstitutionalValidator(user="동진")
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"[Test {i}/{len(test_cases)}] {test['message']}")
        
        result = dgs.process_dialogue(test["message"], {})
        response = result["response"]
        
        # 헌법 검증
        validator.clear_violations()
        validator.validate_extreme_honorific(response)
        
        if not validator.is_constitutional():
            response = validator.apply_eh_disclaimer(response, force=True)
        
        # 기대값 체크
        all_found = all(exp in response for exp in test["expected"])
        
        if all_found:
            print("  ✅ PASS")
            passed += 1
        else:
            print("  ❌ FAIL")
            print(f"     응답: {response[:100]}...")
            failed += 1
        
        print()
    
    print("=" * 70)
    print(f"결과: {passed}/{len(test_cases)} 통과, {failed} 실패")
    print("=" * 70)


def main():
    """메인 함수"""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_batch_test()
    else:
        run_interactive_demo()


if __name__ == "__main__":
    main()
