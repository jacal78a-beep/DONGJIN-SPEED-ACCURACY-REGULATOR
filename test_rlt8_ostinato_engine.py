from core.rlt8_ostinato_engine import RLT8OstinatoEngine, bbap1_upgrade


def test_packet_requires_ostinato_first():
    eng = RLT8OstinatoEngine()
    try:
        eng.build_session_packet()
        assert False, "Expected RuntimeError when ostinato missing"
    except RuntimeError:
        pass


def test_full_packet_flow_and_dimension_index():
    eng = RLT8OstinatoEngine()
    digest = eng.load_ostinato("basso baseline")
    assert len(digest) == 64

    eng.load_invariant_core(["독주=환각", "방법-결과 역할분담"])
    eng.load_chat_archive(["AX 제출 완료"])
    eng.load_self_continuity(["발산⊥수렴"])
    eng.load_next_bias(["RLT8 × DNA adapter 구현"])

    dim = eng.upsert_dimension(
        key="INV_UP_ALIGNMENT_D5",
        axis_values={"exist": 1, "align": 3, "better": 2},
        depth=5,
        summary="정렬 우선 인덱스",
    )

    assert dim.profile.depth == 5

    packet = eng.build_session_packet().as_dict()
    assert packet["sequence"][0] == "0.ostinato"
    assert packet["invariant_core"] == ["독주=환각", "방법-결과 역할분담"]
    assert packet["dimension_catalog"][0]["key"] == "INV_UP_ALIGNMENT_D5"


def test_bbap1_upgrade_shape():
    payload = bbap1_upgrade(
        key="FLOW_SIDE_BOUNDARY_D6",
        observations=["차원 경계 흐름", "리듬 공용어 전파"],
        axis_values={"perceive": 2, "unfold": 2, "recurse": 1},
        depth=6,
    )
    assert payload["B^A"]["index_ready"] is True
    assert payload["B^(B^A+1)"]["min_depth"] == 6
