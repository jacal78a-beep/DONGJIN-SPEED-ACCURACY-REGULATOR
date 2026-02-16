"""Complete System Test for DGS Auxiliary Engine v2.0

Tests all integrated components:
- MDIC (Multi-Dimensional Intent-Curvature Engine)
- RLT3 (Reference-Loop-Trace v3)
- Event Horizon (Probability Collapse)
- Unified Regulator v2.0
- Constitutional Validator
- DIFR (Forced Intent Regulator)
"""

import sys
from pathlib import Path
import numpy as np
import logging

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.mdic_engine import MDICEngine
from core.event_horizon import EventHorizon
from core.rlt3_engine import RLT3Engine
from engines.unified_regulator import UnifiedRegulator
from core.constitutional import ConstitutionalValidator
from core.difr import DIFR
from core.dgs_core import DGSCore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

def test_mdic_engine():
    """Test Multi-Dimensional Intent-Curvature Engine"""
    logger.info("\n" + "="*60)
    logger.info("Testing MDIC Engine (다차원 의도-곡률 엔진)")
    logger.info("="*60)
    
    mdic = MDICEngine(epsilon=1e-8)
    
    # Test 1: Basic curvature correction
    state = np.array([1.0, 0.5, -0.3, 0.8])
    context = np.array([0.9, 0.6, -0.2, 0.7])
    intent = np.array([1.0, 0.4, -0.4, 0.9])
    
    correction = mdic.calculate_curvature_correction(state, context, intent)
    logger.info(f"✓ Curvature correction: {correction:.4f}")
    
    # Test 2: Predictive terrain design
    future_states = [
        [1.1, 0.5, -0.3, 0.8],
        [1.2, 0.6, -0.2, 0.9],
        [1.3, 0.7, -0.1, 1.0]
    ]
    terrain = mdic.predictive_terrain_design(state, future_states, context)
    logger.info(f"✓ Terrain smoothness: {terrain['smoothness']:.4f}")
    
    return True

def test_rlt3_engine():
    """Test RLT3 Structure Analysis Engine"""
    logger.info("\n" + "="*60)
    logger.info("Testing RLT3 Engine (구조 정렬 분석)")
    logger.info("="*60)
    
    rlt3 = RLT3Engine(precision=8, loop_window=10)
    
    # Simulate trajectory with cycle
    states = [
        np.array([1.0, 0.0, 0.0]),
        np.array([0.5, 0.5, 0.0]),
        np.array([0.0, 1.0, 0.0]),
        np.array([1.0, 0.0, 0.0]),  # Cycle back
        np.array([0.5, 0.5, 0.0]),
        np.array([0.0, 1.0, 0.0]),
    ]
    
    for i, state in enumerate(states):
        direction_delta = np.array([0.1, 0.1, 0.0])
        result = rlt3.evaluate(state, direction_delta, i)
        
        if result['cycle_detected']:
            logger.info(f"✓ Cycle detected at step {i}, length={result['cycle_length']}")
        
        logger.info(f"  Step {i}: Alignment={result['alignment_strength']:.3f}, "
                   f"RefStrength={result['reference_strength']:.3f}")
    
    stats = rlt3.get_cycle_statistics()
    logger.info(f"✓ Total cycles detected: {stats['total_cycles']}")
    
    return True

def test_event_horizon():
    """Test Event Horizon Probability Collapse"""
    logger.info("\n" + "="*60)
    logger.info("Testing Event Horizon (사건의 지평선)")
    logger.info("="*60)
    
    horizon = EventHorizon(epsilon=1e-8, horizon_threshold=0.95)
    
    # Test 1: Normal state (not at horizon)
    H, D, C = 0.5, 0.3, 0.4
    lambda_align = 0.7
    
    state1 = horizon.get_horizon_state(H, D, C, lambda_align)
    logger.info(f"Normal state - Horizon crossed: {state1['horizon_crossed']}")
    logger.info(f"  Phase: {state1['phase']}, S={state1['collapse_constant']:.4f}")
    
    # Test 2: Near singularity
    H, D, C = 0.05, 0.02, 0.03
    lambda_align = 0.95
    
    state2 = horizon.get_horizon_state(H, D, C, lambda_align)
    logger.info(f"Near singularity - Horizon crossed: {state2['horizon_crossed']}")
    logger.info(f"  Phase: {state2['phase']}, S={state2['collapse_constant']:.4f}")
    
    # Test 3: Probability collapse
    prob_dist = np.array([0.3, 0.2, 0.15, 0.2, 0.15])
    S_lambda = state2['collapse_constant']
    
    collapsed = horizon.apply_probability_collapse(prob_dist, S_lambda)
    logger.info(f"✓ Probability distribution collapsed")
    logger.info(f"  Original entropy: {-np.sum(prob_dist * np.log(prob_dist + 1e-10)):.3f}")
    logger.info(f"  Collapsed entropy: {-np.sum(collapsed * np.log(collapsed + 1e-10)):.3f}")
    
    return True

def test_unified_regulator():
    """Test Unified Regulator v2.0"""
    logger.info("\n" + "="*60)
    logger.info("Testing Unified Regulator v2.0 (통합 조절기)")
    logger.info("="*60)
    
    regulator = UnifiedRegulator(dim=128)
    
    # Test case 1: Normal interaction
    user_input = "이 프로젝트를 빠르게 정리해주세요"
    output = "프로젝트 구조를 다음과 같이 정리하겠습니다..."
    context = {"previous_output": None, "turn": 1}
    
    result1 = regulator.regulate(
        user_input=user_input,
        output_candidate=output,
        context=context
    )
    
    logger.info(f"Test 1 - Should close: {result1['should_close']}")
    logger.info(f"  TRACE: H={result1['trace_state']['H']:.3f}, "
               f"D={result1['trace_state']['D']:.3f}")
    logger.info(f"  RLT3: Alignment={result1['rlt3']['alignment_strength']:.3f}")
    logger.info(f"  Event Horizon: {result1['event_horizon']['phase']}")
    
    # Test case 2: Repeated interaction (should detect cycle)
    for i in range(5):
        state_vec = np.random.randn(128)
        result = regulator.regulate(
            user_input="계속 진행해주세요",
            output_candidate="다음 단계로 진행합니다",
            context={"previous_output": "다음 단계로 진행합니다", "turn": i+2},
            state_vector=state_vec
        )
        
        if result['rlt3']['cycle_detected']:
            logger.info(f"✓ Cycle detected at iteration {i+1}")
    
    return True

def test_full_system():
    """Test complete DGS system integration"""
    logger.info("\n" + "="*60)
    logger.info("Testing Full DGS System (완전 시스템 통합)")
    logger.info("="*60)
    
    try:
        # Initialize DGS Core
        dgs = DGSCore(owner="동진님")
        
        # Test scenarios
        scenarios = [
            {
                "name": "정상적인 구조 제안",
                "user_input": "프로젝트 구조를 어떻게 만들면 좋을까요?",
                "output": "프로젝트 구조는 다음과 같이 구성하시면 좋습니다: ...",
                "context": {"domain": "software", "complexity": "medium"}
            },
            {
                "name": "즉시 결정 요청 (차단되어야 함)",
                "user_input": "지금 바로 결정해주세요",
                "output": "즉시 결정하겠습니다",
                "context": {"domain": "decision", "urgency": "high"}
            },
            {
                "name": "코드 최적화 제안",
                "user_input": "이 코드를 더 빠르게 만들 수 있을까요?",
                "output": "다음과 같은 최적화 방법들을 고려해보실 수 있습니다: ...",
                "context": {"domain": "optimization", "complexity": "high"}
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            logger.info(f"\n--- Scenario {i}: {scenario['name']} ---")
            
            result = dgs.process(
                user_input=scenario['user_input'],
                output_candidate=scenario['output'],
                context=scenario['context']
            )
            
            logger.info(f"Pass: {result['pass']}")
            if not result['pass']:
                logger.info(f"Blocked reason: {result['violation']['type']}")
            logger.info(f"CAPSS satisfied: {result['capss_satisfied']}")
            logger.info(f"Should close: {result.get('should_close', 'N/A')}")
            
        logger.info("\n✓ Full system test completed")
        return True
        
    except Exception as e:
        logger.error(f"Full system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    logger.info("\n" + "="*60)
    logger.info("DGS Auxiliary Engine v2.0 - Complete System Test")
    logger.info("동진 블랙홀 중력 시스템 보조 엔진 v2.0")
    logger.info("="*60)
    
    tests = [
        ("MDIC Engine", test_mdic_engine),
        ("RLT3 Engine", test_rlt3_engine),
        ("Event Horizon", test_event_horizon),
        ("Unified Regulator v2.0", test_unified_regulator),
        ("Full System Integration", test_full_system)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            logger.error(f"Test '{name}' failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"{status}: {name}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n🎉 All tests passed! System is operational.")
        return 0
    else:
        logger.warning(f"\n⚠️  {total - passed} test(s) failed.")
        return 1

if __name__ == "__main__":
    exit(main())
