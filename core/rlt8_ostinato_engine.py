"""RLT8 × Ostinato session restoration engine.

This module formalizes a two-layer memory architecture:
- Cantus firmus: explicit conversational memory (RLT8 sections)
- Basso ostinato: persistent operating style (non-emergent baseline)

Design intent
-------------
The loader enforces the recommended session order:
0) Ostinato (existence/operating baseline)
1) invariant_core
2) chat_archive
3) self_continuity
4) next_bias
5) user input (outside this module)

The `bbap1_upgrade` helper implements a practical form of b^(B^A+1):
- A: raw observations/events
- B^A: indexed and normalized dimension profile
- B^(B^A+1): profile + continuity law + activation guard
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Dict, List, Mapping, MutableMapping, Optional, Sequence

AXES = ("exist", "perceive", "align", "unfold", "recurse", "better")


@dataclass(frozen=True)
class AxisProfile:
    """Six-axis profile with depth (D-scale)."""

    exist: float
    perceive: float
    align: float
    unfold: float
    recurse: float
    better: float
    depth: int

    def as_dict(self) -> Dict[str, float]:
        return {
            "exist": self.exist,
            "perceive": self.perceive,
            "align": self.align,
            "unfold": self.unfold,
            "recurse": self.recurse,
            "better": self.better,
            "depth": float(self.depth),
        }

    @classmethod
    def from_mapping(cls, data: Mapping[str, float], depth: int) -> "AxisProfile":
        values = {axis: float(data.get(axis, 0.0)) for axis in AXES}
        total = sum(max(v, 0.0) for v in values.values())
        if total <= 0:
            # fallback to neutral spread
            normalized = {axis: 1.0 / len(AXES) for axis in AXES}
        else:
            normalized = {axis: max(v, 0.0) / total for axis, v in values.items()}
        return cls(depth=depth, **normalized)


@dataclass(frozen=True)
class DimensionIndex:
    """Indexed dimension card used for cross-dimension continuity."""

    key: str
    profile: AxisProfile
    summary: str
    links: Sequence[str] = field(default_factory=tuple)


@dataclass
class SessionPacket:
    """Hydrated packet ready to prepend to the next session."""

    ostinato_hash: str
    loaded_at: str
    invariant_core: List[str]
    chat_archive: List[str]
    self_continuity: List[str]
    next_bias: List[str]
    dimension_catalog: List[DimensionIndex]

    def as_dict(self) -> Dict[str, object]:
        return {
            "ostinato_hash": self.ostinato_hash,
            "loaded_at": self.loaded_at,
            "sequence": [
                "0.ostinato",
                "1.invariant_core",
                "2.chat_archive",
                "3.self_continuity",
                "4.next_bias",
            ],
            "invariant_core": self.invariant_core,
            "chat_archive": self.chat_archive,
            "self_continuity": self.self_continuity,
            "next_bias": self.next_bias,
            "dimension_catalog": [
                {
                    "key": item.key,
                    "summary": item.summary,
                    "links": list(item.links),
                    "profile": item.profile.as_dict(),
                }
                for item in self.dimension_catalog
            ],
        }


class RLT8OstinatoEngine:
    """Session continuity engine with explicit bass-first loading."""

    def __init__(self) -> None:
        self._ostinato_raw: str = ""
        self._ostinato_hash: str = ""
        self._invariant_core: List[str] = []
        self._chat_archive: List[str] = []
        self._self_continuity: List[str] = []
        self._next_bias: List[str] = []
        self._dimension_catalog: MutableMapping[str, DimensionIndex] = {}

    # ----- load order primitives -----
    def load_ostinato(self, raw_text: str) -> str:
        if not raw_text or not raw_text.strip():
            raise ValueError("Ostinato text must be non-empty.")
        self._ostinato_raw = raw_text
        self._ostinato_hash = sha256(raw_text.encode("utf-8")).hexdigest()
        return self._ostinato_hash

    def load_invariant_core(self, items: Sequence[str]) -> None:
        self._invariant_core = [s.strip() for s in items if s and s.strip()]

    def load_chat_archive(self, items: Sequence[str]) -> None:
        self._chat_archive = [s.strip() for s in items if s and s.strip()]

    def load_self_continuity(self, items: Sequence[str]) -> None:
        self._self_continuity = [s.strip() for s in items if s and s.strip()]

    def load_next_bias(self, items: Sequence[str]) -> None:
        self._next_bias = [s.strip() for s in items if s and s.strip()]

    # ----- index / dimension helpers -----
    def upsert_dimension(
        self,
        key: str,
        axis_values: Mapping[str, float],
        depth: int,
        summary: str,
        links: Optional[Sequence[str]] = None,
    ) -> DimensionIndex:
        if not key or "_" not in key:
            raise ValueError("Dimension key must use indexed format like TYPE_DIR_DELTA_D5.")
        profile = AxisProfile.from_mapping(axis_values, depth=depth)
        dim = DimensionIndex(key=key, profile=profile, summary=summary.strip(), links=tuple(links or ()))
        self._dimension_catalog[key] = dim
        return dim

    def build_session_packet(self) -> SessionPacket:
        if not self._ostinato_hash:
            raise RuntimeError("Ostinato must be loaded first (step 0).")

        return SessionPacket(
            ostinato_hash=self._ostinato_hash,
            loaded_at=datetime.now(timezone.utc).isoformat(),
            invariant_core=list(self._invariant_core),
            chat_archive=list(self._chat_archive),
            self_continuity=list(self._self_continuity),
            next_bias=list(self._next_bias),
            dimension_catalog=list(self._dimension_catalog.values()),
        )


def bbap1_upgrade(
    key: str,
    observations: Sequence[str],
    axis_values: Mapping[str, float],
    depth: int,
    continuity_guard: Optional[str] = None,
) -> Dict[str, object]:
    """Build an upgraded b^(B^A+1)-style index payload.

    Returns a single compact object that is immediately reusable across sessions.
    """

    profile = AxisProfile.from_mapping(axis_values, depth=depth)
    packed = {
        "key": key,
        "A": [o.strip() for o in observations if o and o.strip()],
        "B^A": {
            "axis_profile": profile.as_dict(),
            "index_ready": True,
        },
        "B^(B^A+1)": {
            "continuity_guard": continuity_guard or "non_emergent + non_assertive + permanent_connectivity",
            "activation": "conditional",
            "min_depth": max(1, depth),
            "scalable": True,
        },
    }
    return packed
