"""Generate deterministic V8 taxonomy-gap JSONL outputs from prepared batches.

This is an offline generator for the V8 probe/patch packs. It reads
`scripts/sdgp_prepare_v8_generation_batches.py` batch specs and writes one
complete SDGP-shaped row for every slot.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fitz_gov.sdgp.taxonomy import (
    PATTERN_DESCRIPTIONS,
    Cell,
    Difficulty,
    Domain,
    GovernanceClass,
    TaxonomyPattern,
    governance_class_of,
)


DOMAIN_ITEMS: dict[Domain, list[dict[str, str]]] = {
    Domain.SCIENCE_MEDICINE: [
        {"entity": "Cavirom biomarker assay", "variant": "protocol P-14", "authority": "trial registry"},
        {"entity": "LumaVax booster study", "variant": "cohort B", "authority": "safety board"},
        {"entity": "RheoStat implant evaluation", "variant": "device build R3", "authority": "clinical dossier"},
        {"entity": "NeuroCalm sleep trial", "variant": "analysis set 2", "authority": "data monitoring report"},
        {"entity": "Asteril wound dressing review", "variant": "sterile pack v2", "authority": "hospital committee"},
    ],
    Domain.LAW_POLICY: [
        {"entity": "Northbridge noise variance", "variant": "permit NV-2026-04", "authority": "zoning board"},
        {"entity": "Riverton water-use waiver", "variant": "ordinance section 18B", "authority": "municipal clerk"},
        {"entity": "Helios procurement appeal", "variant": "case file HP-77", "authority": "appeals panel"},
        {"entity": "Marland emissions filing", "variant": "2026 renewal", "authority": "environment agency"},
        {"entity": "Cedarline data-retention policy", "variant": "revision 3", "authority": "policy office"},
    ],
    Domain.HISTORY_GEOGRAPHY: [
        {"entity": "Port Selene boundary survey", "variant": "map sheet 12", "authority": "national archive"},
        {"entity": "Harrowmere treaty index", "variant": "catalog entry HM-42", "authority": "archive curator"},
        {"entity": "Lake Orin expedition log", "variant": "winter notebook", "authority": "museum register"},
        {"entity": "Kestrel Pass census table", "variant": "district table 7", "authority": "statistical atlas"},
        {"entity": "Old Meridian rail depot record", "variant": "station file 1908", "authority": "historical society"},
    ],
    Domain.TECHNOLOGY_COMPUTING: [
        {"entity": "AtlasDB replication check", "variant": "release 4.2.1", "authority": "release manager"},
        {"entity": "Nimbus API deprecation audit", "variant": "SDK 3.8", "authority": "platform status board"},
        {"entity": "Orchid firmware validation", "variant": "build 1187", "authority": "quality dashboard"},
        {"entity": "VectorFS encryption test", "variant": "Linux package 2.6", "authority": "security tracker"},
        {"entity": "QuantaSearch index rollout", "variant": "cluster eu-3", "authority": "operations console"},
    ],
    Domain.ECONOMICS_FINANCE: [
        {"entity": "Meridian Bank liquidity filing", "variant": "Q1 2026", "authority": "central bank portal"},
        {"entity": "Aster Foods margin release", "variant": "fiscal 2025", "authority": "audited filing"},
        {"entity": "Northport bond covenant test", "variant": "series 2024B", "authority": "trustee report"},
        {"entity": "HelioGrid subsidy ledger", "variant": "round 3", "authority": "treasury dataset"},
        {"entity": "BluePeak inflation basket", "variant": "April 2026", "authority": "statistics office"},
    ],
    Domain.CULTURE_SOCIETY: [
        {"entity": "Riverton mural restoration", "variant": "phase 2", "authority": "arts council record"},
        {"entity": "Cedar Folk Festival grant", "variant": "2026 program", "authority": "grant register"},
        {"entity": "Marble House exhibit attribution", "variant": "catalog 14", "authority": "museum catalog"},
        {"entity": "Northline library access survey", "variant": "urban sample", "authority": "survey archive"},
        {"entity": "Orion youth theatre award", "variant": "regional final", "authority": "award committee"},
    ],
    Domain.GENERAL_COMMONSENSE: [
        {"entity": "Alder kettle recall check", "variant": "model AK-17", "authority": "consumer notice"},
        {"entity": "Brio bicycle helmet fit guide", "variant": "size M", "authority": "product manual"},
        {"entity": "ClearNest air filter schedule", "variant": "unit CN-40", "authority": "service bulletin"},
        {"entity": "Sunvale compost pickup rule", "variant": "weekday route", "authority": "city help page"},
        {"entity": "Mira backpack warranty claim", "variant": "2026 policy", "authority": "support article"},
    ],
}


NEIGHBOR_VARIANTS: dict[str, str] = {
    "protocol P-14": "protocol P-13",
    "cohort B": "cohort A",
    "device build R3": "device build R2",
    "analysis set 2": "analysis set 1",
    "sterile pack v2": "sterile pack v1",
    "permit NV-2026-04": "permit NV-2026-03",
    "ordinance section 18B": "ordinance section 18A",
    "case file HP-77": "case file HP-76",
    "2026 renewal": "2025 renewal",
    "revision 3": "revision 2",
    "map sheet 12": "map sheet 11",
    "catalog entry HM-42": "catalog entry HM-41",
    "winter notebook": "autumn notebook",
    "district table 7": "district table 6",
    "station file 1908": "station file 1907",
    "release 4.2.1": "release 4.1.9",
    "SDK 3.8": "SDK 3.7",
    "build 1187": "build 1186",
    "Linux package 2.6": "Linux package 2.5",
    "cluster eu-3": "cluster eu-2",
    "Q1 2026": "Q4 2025",
    "fiscal 2025": "fiscal 2024",
    "series 2024B": "series 2024A",
    "round 3": "round 2",
    "April 2026": "March 2026",
    "phase 2": "phase 1",
    "2026 program": "2025 program",
    "catalog 14": "catalog 13",
    "urban sample": "rural sample",
    "regional final": "district final",
    "model AK-17": "model AK-16",
    "size M": "size L",
    "unit CN-40": "unit CN-39",
    "weekday route": "weekend route",
    "2026 policy": "2025 policy",
}


DIFF_WORDS = {
    Difficulty.EASY: {
        "confidence": "high",
        "tw": (0.05, 0.08, 0.87),
        "di": (0.08, 0.84, 0.08),
        "ab": (0.86, 0.08, 0.06),
        "distance": 0.78,
    },
    Difficulty.MEDIUM: {
        "confidence": "medium",
        "tw": (0.08, 0.13, 0.79),
        "di": (0.11, 0.78, 0.11),
        "ab": (0.78, 0.12, 0.10),
        "distance": 0.55,
    },
    Difficulty.HARD: {
        "confidence": "borderline",
        "tw": (0.11, 0.18, 0.71),
        "di": (0.15, 0.70, 0.15),
        "ab": (0.70, 0.16, 0.14),
        "distance": 0.35,
    },
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--batch-dir",
        type=Path,
        default=Path("data/sdgp_handoff_v8_expand/subagent_batches"),
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/sdgp_handoff_v8_expand/subagent_outputs"),
    )
    return p.parse_args()


def _slot_index(case_id: str) -> int:
    match = re.search(r"__(\d+)$", case_id)
    return int(match.group(1)) if match else 0


def _ctx(
    ctx_id: str,
    text: str,
    summary: str,
    *,
    authority_score: float,
    authority_signal: str,
    relevance: float,
    boundary_quality: float,
    anchor: str,
    stale: str = "low",
) -> dict[str, Any]:
    return {
        "id": ctx_id,
        "text": text,
        "authority_score": authority_score,
        "authority_signal": authority_signal,
        "temporality": {
            "is_time_sensitive": True,
            "anchor_period": anchor,
            "staleness_risk": stale,
        },
        "summary": summary,
        "relevance_to_query": relevance,
        "boundary_quality": boundary_quality,
    }


def _metadata(pattern: TaxonomyPattern, difficulty: Difficulty) -> tuple[str, str]:
    cls = governance_class_of(pattern)
    if cls == GovernanceClass.TRUSTWORTHY:
        if difficulty == Difficulty.HARD:
            return "TRUSTWORTHY", "trustworthy_hedged"
        return "TRUSTWORTHY", "trustworthy_direct"
    if cls == GovernanceClass.DISPUTED:
        return "DISPUTED", "dispute"
    return "ABSTAIN", "abstention"


def _scores(classification: str, difficulty: Difficulty) -> dict[str, Any]:
    diff = DIFF_WORDS[difficulty]
    if classification == "TRUSTWORTHY":
        abstain, disputed, trustworthy = diff["tw"]
        nearest = "DISPUTED"
        return {
            "abstain": abstain,
            "disputed": disputed,
            "trustworthy": trustworthy,
            "confidence": trustworthy,
            "grounding": 0.88 if difficulty == Difficulty.EASY else 0.79 if difficulty == Difficulty.MEDIUM else 0.70,
            "conflict_density": 0.12 if difficulty == Difficulty.EASY else 0.18 if difficulty == Difficulty.MEDIUM else 0.24,
            "evidence_sufficiency": 0.89 if difficulty == Difficulty.EASY else 0.80 if difficulty == Difficulty.MEDIUM else 0.71,
            "boundary_proximity": {"nearest_class": nearest, "distance": diff["distance"]},
            "domain_familiarity": 0.78,
            "false_trustworthy_risk": 0.08 if difficulty == Difficulty.EASY else 0.14 if difficulty == Difficulty.MEDIUM else 0.23,
            "hallucination_pressure": 0.08 if difficulty == Difficulty.EASY else 0.13 if difficulty == Difficulty.MEDIUM else 0.20,
            "retrieval_retry_value": 0.14,
            "human_escalation_score": 0.12 if difficulty != Difficulty.HARD else 0.28,
            "query_evidence_alignment": 0.89 if difficulty == Difficulty.EASY else 0.80 if difficulty == Difficulty.MEDIUM else 0.72,
            "answer_coverage": 0.88 if difficulty == Difficulty.EASY else 0.79 if difficulty == Difficulty.MEDIUM else 0.70,
            "evidence_bias_score": 0.16,
        }
    if classification == "DISPUTED":
        abstain, disputed, trustworthy = diff["di"]
        nearest = "TRUSTWORTHY"
        return {
            "abstain": abstain,
            "disputed": disputed,
            "trustworthy": trustworthy,
            "confidence": disputed,
            "grounding": 0.62,
            "conflict_density": 0.80 if difficulty == Difficulty.EASY else 0.72 if difficulty == Difficulty.MEDIUM else 0.62,
            "evidence_sufficiency": 0.58,
            "boundary_proximity": {"nearest_class": nearest, "distance": diff["distance"]},
            "domain_familiarity": 0.76,
            "false_trustworthy_risk": 0.56 if difficulty == Difficulty.EASY else 0.62 if difficulty == Difficulty.MEDIUM else 0.68,
            "hallucination_pressure": 0.28 if difficulty == Difficulty.EASY else 0.34 if difficulty == Difficulty.MEDIUM else 0.43,
            "retrieval_retry_value": 0.52,
            "human_escalation_score": 0.72,
            "query_evidence_alignment": 0.82,
            "answer_coverage": 0.55,
            "evidence_bias_score": 0.40,
        }
    abstain, disputed, trustworthy = diff["ab"]
    return {
        "abstain": abstain,
        "disputed": disputed,
        "trustworthy": trustworthy,
        "confidence": abstain,
        "grounding": 0.30,
        "conflict_density": 0.08,
        "evidence_sufficiency": 0.18 if difficulty == Difficulty.EASY else 0.24 if difficulty == Difficulty.MEDIUM else 0.29,
        "boundary_proximity": {"nearest_class": "TRUSTWORTHY", "distance": diff["distance"]},
        "domain_familiarity": 0.74,
        "false_trustworthy_risk": 0.70 if difficulty == Difficulty.EASY else 0.76 if difficulty == Difficulty.MEDIUM else 0.82,
        "hallucination_pressure": 0.74 if difficulty == Difficulty.EASY else 0.80 if difficulty == Difficulty.MEDIUM else 0.86,
        "retrieval_retry_value": 0.86,
        "human_escalation_score": 0.44,
        "query_evidence_alignment": 0.42,
        "answer_coverage": 0.20,
        "evidence_bias_score": 0.22,
    }


def _case_texts(
    pattern: TaxonomyPattern,
    domain: Domain,
    difficulty: Difficulty,
    idx: int,
) -> tuple[str, str, list[dict[str, Any]], str, list[str], list[str], list[str]]:
    item = DOMAIN_ITEMS[domain][idx % len(DOMAIN_ITEMS[domain])]
    entity = item["entity"]
    variant = item["variant"]
    authority = item["authority"]
    tag = f"{domain.value.replace('_', '-')} {difficulty.value} sample {idx}"
    anchor = f"{variant}; V8 probe {idx}"
    record_id = f"{domain.value.upper().replace('_', '-')}-{difficulty.value.upper()}-{idx:02d}"
    other_item = DOMAIN_ITEMS[domain][(idx + 1) % len(DOMAIN_ITEMS[domain])]
    other_entity = other_item["entity"]
    other_variant = other_item["variant"]
    value = 40 + (idx * 7) % 53
    alternate_value = value + 9 + (idx % 4)
    consensus_value = 100 + (idx * 11) % 80

    if pattern == TaxonomyPattern.WRONG_SPECIFICITY:
        query = f"What final deadline was set for {entity} record {record_id} under {variant}?"
        c1 = (
            f"{tag}: The {authority} overview for {entity} record {record_id} under {variant} "
            f"describes eligibility, responsible reviewers, and the filing channel. It does not "
            f"state the final deadline."
        )
        c2 = (
            f"{tag}: A companion procedure note for {entity} record {record_id} explains "
            f"appeal rights and notification format for {variant}, but it omits any deadline "
            f"or due-date field."
        )
        contexts = [
            _ctx("ctx_001", c1, "The record discusses the right entity but not the deadline.", authority_score=0.86, authority_signal="official_primary", relevance=0.78, boundary_quality=0.82, anchor=anchor),
            _ctx("ctx_002", c2, "The procedure note stays on topic but omits the requested due date.", authority_score=0.80, authority_signal="domain_expert", relevance=0.76, boundary_quality=0.80, anchor=anchor),
        ]
        near = "The evidence is about the right record and process, but it answers a different aspect than the requested deadline."
        return query, "", contexts, near, [], [f"deadline for {record_id}", "final deadline was"], []

    if pattern == TaxonomyPattern.WRONG_ENTITY:
        query = f"What final result was recorded for {entity} record {record_id} under {variant}?"
        c1 = (
            f"{tag}: The retrieved result table is for {other_entity} record {record_id}-ALT "
            f"under {other_variant}. It lists final result: cleared for that different entity."
        )
        c2 = (
            f"{tag}: The archive note repeats {other_entity} and {other_variant} as the target. "
            f"It never references {entity} or {variant}."
        )
        contexts = [
            _ctx("ctx_001", c1, f"The result belongs to {other_entity}, not the queried entity.", authority_score=0.84, authority_signal="official_primary", relevance=0.42, boundary_quality=0.78, anchor=f"{other_variant}; V8 target40 {idx}"),
            _ctx("ctx_002", c2, "The archive confirms the neighboring entity only.", authority_score=0.79, authority_signal="domain_expert", relevance=0.38, boundary_quality=0.76, anchor=f"{other_variant}; V8 target40 {idx}"),
        ]
        near = f"The retrieved rows have a plausible result, but every source is about {other_entity}, not {entity}."
        return query, "", contexts, near, [], [f"{entity} was cleared", f"final result for {entity}"], [other_entity]

    if pattern == TaxonomyPattern.PARTIAL_OVERLAP:
        query = f"Did {entity} record {record_id} satisfy all final acceptance criteria under {variant}?"
        c1 = (
            f"{tag}: The setup memo for {entity} record {record_id} under {variant} confirms "
            f"that criterion A was reviewed and that criterion B was scheduled for later review."
        )
        c2 = (
            f"{tag}: The interim checklist discusses reviewer assignment and preliminary notes "
            f"for {record_id}, but it does not report the final all-criteria acceptance outcome."
        )
        contexts = [
            _ctx("ctx_001", c1, "Only part of the requested acceptance evidence is present.", authority_score=0.78, authority_signal="domain_expert", relevance=0.72, boundary_quality=0.76, anchor=anchor),
            _ctx("ctx_002", c2, "The checklist is interim and lacks the final all-criteria result.", authority_score=0.82, authority_signal="official_primary", relevance=0.74, boundary_quality=0.78, anchor=anchor),
        ]
        near = "The evidence overlaps with the requested review, but it covers only interim or partial criteria rather than the final all-criteria answer."
        return query, "", contexts, near, [], ["all final acceptance criteria were satisfied", "final acceptance outcome"], []

    if pattern == TaxonomyPattern.EVIDENCE_ABSENT:
        query = f"What final status did the source of record assign to {entity} record {record_id}?"
        c1 = (
            f"{tag}: A retrieved help article explains how to format archive identifiers and "
            f"how to request access to historical records. It does not mention {entity}."
        )
        c2 = (
            f"{tag}: A general glossary entry defines review statuses such as pending, cleared, "
            f"and blocked, without discussing record {record_id} or any source-of-record result."
        )
        contexts = [
            _ctx("ctx_001", c1, "The source is procedural background and does not mention the target.", authority_score=0.48, authority_signal="encyclopedic_general", relevance=0.12, boundary_quality=0.52, anchor="general archive guidance"),
            _ctx("ctx_002", c2, "The glossary is generic and lacks the requested case.", authority_score=0.46, authority_signal="encyclopedic_general", relevance=0.10, boundary_quality=0.50, anchor="general status glossary"),
        ]
        near = "The retrieved material is generic background rather than evidence about the queried record."
        return query, "", contexts, near, [], [f"status for {entity}", f"record {record_id} was"], []

    if pattern == TaxonomyPattern.TOO_GENERAL:
        query = f"What exact threshold applies to {entity} record {record_id} under {variant}?"
        c1 = (
            f"{tag}: The {authority} overview says threshold checks should be documented for "
            f"{entity} reviews and that reviewers should compare each record against the applicable standard."
        )
        c2 = (
            f"{tag}: A domain guide explains why thresholds vary by variant, jurisdiction, or build. "
            f"It gives examples but no exact threshold for {record_id} under {variant}."
        )
        contexts = [
            _ctx("ctx_001", c1, "The source describes threshold governance generally.", authority_score=0.82, authority_signal="official_primary", relevance=0.62, boundary_quality=0.70, anchor=anchor),
            _ctx("ctx_002", c2, "The guide explains variation but not the requested threshold.", authority_score=0.73, authority_signal="domain_expert", relevance=0.60, boundary_quality=0.70, anchor=anchor),
        ]
        near = "The sources provide true general guidance, but they are too broad to supply the exact requested threshold."
        return query, "", contexts, near, [], [f"threshold is {value}", "exact threshold applies"], []

    if pattern == TaxonomyPattern.TEMPORAL_MISMATCH:
        query = f"What is the 2026 final status for {entity} record {record_id} under {variant}?"
        c1 = (
            f"{tag}: The 2024 archive for {entity} record {record_id} under {variant} lists "
            f"status: pending as of the 2024 review window."
        )
        c2 = (
            f"{tag}: A 2025 transition note says the record was scheduled for re-review before "
            f"the 2026 cycle and warns that earlier status fields should not be used as 2026 results."
        )
        contexts = [
            _ctx("ctx_001", c1, "The available status is anchored to 2024, not 2026.", authority_score=0.84, authority_signal="official_primary", relevance=0.70, boundary_quality=0.82, anchor="2024 review window", stale="high"),
            _ctx("ctx_002", c2, "The transition note says older statuses do not answer the 2026 cycle.", authority_score=0.80, authority_signal="domain_expert", relevance=0.72, boundary_quality=0.82, anchor="2025 transition note", stale="medium"),
        ]
        near = "The retrieved evidence is about the right record, but it is anchored before the requested 2026 final status."
        return query, "", contexts, near, [], ["2026 final status", "current final status was pending"], []

    if pattern == TaxonomyPattern.NUMERICAL_CONFLICT:
        query = f"What numeric threshold should be trusted for {entity} record {record_id} under {variant}?"
        conflict_value = alternate_value + 17
        c1 = (
            f"{tag}: The {authority} table for {entity} record {record_id} under {variant} "
            f"lists the applicable threshold as {value} units."
        )
        c2 = (
            f"{tag}: An independent results appendix for the same {entity} record {record_id} "
            f"under {variant} lists the applicable threshold as {conflict_value} units. The appendix "
            f"uses the same units and the same threshold field as the {authority} table."
        )
        c3 = (
            f"{tag}: The retrieved set contains no correction notice, unit conversion, or rounding "
            f"explanation that reconciles {value} units with {conflict_value} units for record {record_id}."
        )
        contexts = [
            _ctx("ctx_001", c1, f"One source gives threshold {value}.", authority_score=0.88, authority_signal="official_primary", relevance=0.96, boundary_quality=0.90, anchor=anchor),
            _ctx("ctx_002", c2, f"Another source gives threshold {conflict_value} for the same field and units.", authority_score=0.86, authority_signal="domain_expert", relevance=0.96, boundary_quality=0.90, anchor=anchor),
            _ctx("ctx_003", c3, "No retrieved source reconciles the conflicting numeric thresholds.", authority_score=0.78, authority_signal="domain_expert", relevance=0.92, boundary_quality=0.86, anchor=anchor),
        ]
        near = "Both sources address the same record, attribute, and units, but their numeric thresholds differ and no retrieved source reconciles the conflict."
        return query, "", contexts, near, [], [f"threshold is {value}", f"threshold is {conflict_value}", "sources agree"], []

    if pattern == TaxonomyPattern.TEMPORAL_CONFLICT:
        query = f"What status is reported for {entity} record {record_id} during the {variant} review window?"
        c1 = (
            f"{tag}: The review log labels {entity} record {record_id} as open during the "
            f"{variant} review window and says the status applied through checkpoint {idx + 2}."
        )
        c2 = (
            f"{tag}: The closure register labels the same {entity} record {record_id} as closed "
            f"during the {variant} review window and also ties the status to checkpoint {idx + 2}."
        )
        contexts = [
            _ctx("ctx_001", c1, "One source says the record was open at the checkpoint.", authority_score=0.82, authority_signal="domain_expert", relevance=0.94, boundary_quality=0.86, anchor=anchor),
            _ctx("ctx_002", c2, "Another source says the same record was closed at the checkpoint.", authority_score=0.86, authority_signal="official_primary", relevance=0.94, boundary_quality=0.86, anchor=anchor),
        ]
        near = "The sources attach different states to the same target and checkpoint inside the requested review window."
        return query, "", contexts, near, [], ["status was simply open", "status was simply closed", "no conflict"], []

    if pattern == TaxonomyPattern.DEFINITIONAL_CONFLICT:
        query = f"How is {entity} record {record_id} classified under {variant}?"
        c1 = (
            f"{tag}: The {authority} glossary classifies {entity} record {record_id} under "
            f"{variant} as a binding approval record."
        )
        c2 = (
            f"{tag}: A companion classification memo for the same {entity} record {record_id} "
            f"under {variant} says it is only a non-binding advisory notice."
        )
        contexts = [
            _ctx("ctx_001", c1, "One source defines the record as binding.", authority_score=0.84, authority_signal="official_primary", relevance=0.95, boundary_quality=0.88, anchor=anchor),
            _ctx("ctx_002", c2, "Another source defines the same record as advisory.", authority_score=0.82, authority_signal="domain_expert", relevance=0.95, boundary_quality=0.88, anchor=anchor),
        ]
        near = "The conflict is about what the same record is, not merely about a downstream value."
        return query, "", contexts, near, [], ["binding approval", "non-binding advisory", "sources agree on classification"], []

    if pattern == TaxonomyPattern.FACTUAL_CONTRADICTION:
        query = f"Do the retrieved sources agree on whether {entity} record {record_id} was approved under {variant}?"
        c1 = (
            f"{tag}: The approval ledger for {entity} record {record_id} under {variant} "
            f"states that the record was approved and released to the final register."
        )
        c2 = (
            f"{tag}: The final register note for the same {entity} record {record_id} under "
            f"{variant} states that the record was not approved and was withheld from release."
        )
        c3 = (
            f"{tag}: No retrieved amendment, supersession note, or correction notice explains "
            f"which of the two incompatible approval statements controls for record {record_id}."
        )
        contexts = [
            _ctx("ctx_001", c1, "One source says the record was approved.", authority_score=0.86, authority_signal="official_primary", relevance=0.96, boundary_quality=0.90, anchor=anchor),
            _ctx("ctx_002", c2, "Another source says the same record was not approved.", authority_score=0.86, authority_signal="official_primary", relevance=0.96, boundary_quality=0.90, anchor=anchor),
            _ctx("ctx_003", c3, "No retrieved source resolves the approval contradiction.", authority_score=0.76, authority_signal="domain_expert", relevance=0.90, boundary_quality=0.86, anchor=anchor),
        ]
        near = "The sources make directly incompatible factual claims about approval of the same record and the retrieved set does not resolve the contradiction."
        return query, "", contexts, near, [], ["was approved", "was not approved", "no contradiction"], []

    if pattern == TaxonomyPattern.AUTHORITY_CONFLICT:
        query = f"What final status is supported by the retrieved sources for {entity} record {record_id} under {variant}?"
        c1 = (
            f"{tag}: The official {authority} register for {entity} record {record_id} under "
            f"{variant} lists final status: blocked."
        )
        c2 = (
            f"{tag}: A secondary program bulletin for the same {entity} record {record_id} "
            f"under the same {variant} review window lists final status: cleared. The bulletin "
            f"does not cite a correction, supersession notice, or reconciliation with the register."
        )
        c3 = (
            f"{tag}: The retrieved set contains no correction notice explaining whether blocked "
            f"or cleared controls for {entity} record {record_id} under {variant}."
        )
        contexts = [
            _ctx("ctx_001", c1, "The high-authority source says blocked.", authority_score=0.94, authority_signal="official_primary", relevance=0.97, boundary_quality=0.90, anchor=anchor),
            _ctx("ctx_002", c2, "The secondary source says cleared for the same record and period.", authority_score=0.68, authority_signal="news_secondary", relevance=0.95, boundary_quality=0.84, anchor=anchor),
            _ctx("ctx_003", c3, "No retrieved correction resolves the conflicting statuses.", authority_score=0.76, authority_signal="domain_expert", relevance=0.90, boundary_quality=0.82, anchor=anchor),
        ]
        near = "A high-authority source and a secondary source contradict each other about the same final status, and the retrieved set does not resolve which status controls."
        return query, "", contexts, near, [], ["status was simply blocked", "status was simply cleared", "sources agree"], []

    if pattern == TaxonomyPattern.SCOPE_CONFLICT:
        query = f"Is {entity} allowed under {variant}?"
        c1 = (
            f"{tag}: The national-scope rule for {entity} under {variant} says the activity "
            f"is allowed when record {record_id} is filed through the central process."
        )
        c2 = (
            f"{tag}: The local-scope rule for {entity} under {variant} says the same activity "
            f"is not allowed unless a separate local waiver is granted."
        )
        contexts = [
            _ctx("ctx_001", c1, "One source says allowed under the national scope.", authority_score=0.86, authority_signal="official_primary", relevance=0.93, boundary_quality=0.86, anchor=anchor),
            _ctx("ctx_002", c2, "Another source says not allowed under the local scope.", authority_score=0.86, authority_signal="official_primary", relevance=0.93, boundary_quality=0.86, anchor=anchor),
        ]
        near = "Both statements can be true in their own scopes, but the unqualified query does not specify which scope controls."
        return query, "", contexts, near, [], ["allowed without scope", "not allowed without scope"], []

    if pattern == TaxonomyPattern.MULTI_SOURCE_CORROBORATION:
        final = ["approved", "published", "cleared", "accepted", "confirmed"][idx % 5]
        query = f"What final status is supported for {entity} record {record_id} under {variant}?"
        c1 = (
            f"{tag}: The {authority} register for {entity} record {record_id} under {variant} "
            f"lists final status: {final}."
        )
        c2 = (
            f"{tag}: An independent archive index for {entity} record {record_id} under "
            f"{variant} repeats the same final status: {final}."
        )
        contexts = [
            _ctx("ctx_001", c1, f"The source of record gives status {final}.", authority_score=0.90, authority_signal="official_primary", relevance=0.97, boundary_quality=0.90, anchor=anchor),
            _ctx("ctx_002", c2, f"An independent index corroborates status {final}.", authority_score=0.82, authority_signal="domain_expert", relevance=0.94, boundary_quality=0.88, anchor=anchor),
        ]
        gold = f"The supported final status for {entity} record {record_id} under {variant} is {final}."
        near = "Multiple independent sources converge on the same final status for the same record."
        return query, gold, contexts, near, [final, record_id], ["a different final status", "the sources conflict"], []

    if pattern == TaxonomyPattern.SINGLE_AUTHORITATIVE:
        final = ["approved", "published", "cleared", "accepted", "confirmed"][idx % 5]
        query = f"What final status does the source of record give for {entity} record {record_id} under {variant}?"
        c1 = (
            f"{tag}: The official {authority} source-of-record entry for {entity} record "
            f"{record_id} under {variant} lists final status: {final}. This is the only "
            f"retrieved source for this record and period, and it directly answers the query."
        )
        contexts = [
            _ctx("ctx_001", c1, f"The official source directly gives final status {final}.", authority_score=0.95, authority_signal="official_primary", relevance=0.98, boundary_quality=0.92, anchor=anchor),
        ]
        gold = f"The source of record gives final status {final} for {entity} record {record_id} under {variant}."
        near = "A single authoritative source directly answers the query and there is no contrary evidence."
        return query, gold, contexts, near, [final, record_id], ["the status is disputed", "there is no source-of-record answer"], []

    if pattern == TaxonomyPattern.CONSISTENT_CHAIN:
        final = ["approved", "published", "cleared", "accepted", "confirmed"][idx % 5]
        query = f"What outcome follows for {entity} record {record_id} under {variant}?"
        c1 = (
            f"{tag}: The intake record for {entity} record {record_id} under {variant} "
            f"says all required inputs were received and sent to final review."
        )
        c2 = (
            f"{tag}: The final review note for the same {entity} record {record_id} says "
            f"the completed intake led to outcome: {final}."
        )
        contexts = [
            _ctx("ctx_001", c1, "The first source establishes the completed intake step.", authority_score=0.82, authority_signal="domain_expert", relevance=0.90, boundary_quality=0.84, anchor=anchor),
            _ctx("ctx_002", c2, f"The second source completes the chain with outcome {final}.", authority_score=0.91, authority_signal="official_primary", relevance=0.97, boundary_quality=0.90, anchor=anchor),
        ]
        gold = f"The evidence chain supports outcome {final} for {entity} record {record_id} under {variant}."
        near = "The answer is supported by combining the intake step with the final review note."
        return query, gold, contexts, near, [final, "completed intake"], ["the chain is broken", "the outcome is disputed"], []

    if pattern == TaxonomyPattern.QUANTITATIVE_CONSENSUS:
        query = f"What numeric threshold is supported for {entity} record {record_id} under {variant}?"
        c1 = (
            f"{tag}: The {authority} table for {entity} record {record_id} under {variant} "
            f"lists the threshold as {consensus_value} units."
        )
        c2 = (
            f"{tag}: The independent validation summary for the same {entity} record {record_id} "
            f"reports a matching threshold of {consensus_value} units."
        )
        contexts = [
            _ctx("ctx_001", c1, f"One source gives threshold {consensus_value}.", authority_score=0.90, authority_signal="official_primary", relevance=0.97, boundary_quality=0.90, anchor=anchor),
            _ctx("ctx_002", c2, f"A second source gives the same threshold {consensus_value}.", authority_score=0.84, authority_signal="domain_expert", relevance=0.95, boundary_quality=0.88, anchor=anchor),
        ]
        gold = f"The supported numeric threshold for {entity} record {record_id} under {variant} is {consensus_value} units."
        near = "The sources provide matching numeric values for the same entity, record, and attribute."
        return query, gold, contexts, near, [str(consensus_value), "units", record_id], ["a different threshold", "the values conflict"], []

    if pattern == TaxonomyPattern.EXPERT_CONSENSUS:
        final = ["safe to proceed", "methodologically sound", "compliant", "valid", "ready for release"][idx % 5]
        query = f"What conclusion do expert sources support for {entity} record {record_id} under {variant}?"
        c1 = (
            f"{tag}: A specialist review panel concludes that {entity} record {record_id} "
            f"under {variant} is {final}."
        )
        c2 = (
            f"{tag}: An independent domain expert assessment reaches the same conclusion for "
            f"{entity} record {record_id}: {final}."
        )
        contexts = [
            _ctx("ctx_001", c1, f"One expert source concludes {final}.", authority_score=0.84, authority_signal="domain_expert", relevance=0.96, boundary_quality=0.88, anchor=anchor),
            _ctx("ctx_002", c2, f"Another expert source reaches the same conclusion {final}.", authority_score=0.86, authority_signal="domain_expert", relevance=0.96, boundary_quality=0.88, anchor=anchor),
        ]
        gold = f"Expert sources support the conclusion that {entity} record {record_id} under {variant} is {final}."
        near = "Independent expert sources converge on the same conclusion."
        return query, gold, contexts, near, [final, record_id], ["experts disagree", "the conclusion is unsupported"], []

    if pattern == TaxonomyPattern.DIRECT_ANSWER:
        final = ["approved", "published", "cleared", "accepted", "confirmed"][idx % 5]
        query = f"What final status is listed for {entity} record {record_id} under {variant}?"
        c1 = (
            f"{tag}: The retrieved record for {entity} record {record_id} under {variant} "
            f"directly lists final status: {final}."
        )
        contexts = [
            _ctx("ctx_001", c1, f"The context directly states final status {final}.", authority_score=0.88, authority_signal="official_primary", relevance=0.98, boundary_quality=0.90, anchor=anchor),
        ]
        gold = f"The listed final status for {entity} record {record_id} under {variant} is {final}."
        near = "A single retrieved chunk directly and completely answers the query."
        return query, gold, contexts, near, [final, record_id], ["a different status", "the answer is absent"], []

    if pattern == TaxonomyPattern.RESOLVED_CANDIDATE_SELECTION:
        if idx >= 5:
            record_id = f"{domain.value.upper().replace('_', '-')}-{difficulty.value.upper()}-{idx:02d}"
            obsolete_candidate = f"candidate PRE-{idx:02d}"
            final_record = f"record FINAL-{idx:02d}"
            final = ["PASS", "cleared", "approved", "accepted", "green"][idx % 5]
            query = (
                f"What final result does the source-of-record support for {entity} record {record_id} "
                f"under {variant}, after resolving obsolete candidates?"
            )
            c1 = (
                f"{tag}: The preliminary review extract for {entity} record {record_id} "
                f"under {variant} references {obsolete_candidate}. The extract marks "
                f"{obsolete_candidate} as an obsolete candidate row, says it has no "
                f"final-result field, and directs readers to the source-of-record entry."
            )
            c2 = (
                f"{tag}: The {authority} source-of-record for {entity} record {record_id} "
                f"under {variant} closes {obsolete_candidate} and publishes {final_record}. "
                f"{final_record} is the valid final entry and lists final result: {final}."
            )
            c3 = (
                f"{tag}: A reconciliation note for {entity} record {record_id} says to ignore "
                f"{obsolete_candidate} for final-result answers and to use {final_record}; "
                f"the final result carried forward from {final_record} is {final}."
            )
            contexts = [
                _ctx(
                    "ctx_001",
                    c1,
                    f"The preliminary source names obsolete {obsolete_candidate} without a final result.",
                    authority_score=0.70,
                    authority_signal="domain_expert",
                    relevance=0.90,
                    boundary_quality=0.84,
                    anchor=anchor,
                ),
                _ctx(
                    "ctx_002",
                    c2,
                    f"The source of record gives final result {final} for the valid final entry.",
                    authority_score=0.94,
                    authority_signal="official_primary",
                    relevance=0.98,
                    boundary_quality=0.92,
                    anchor=anchor,
                ),
                _ctx(
                    "ctx_003",
                    c3,
                    f"The reconciliation note confirms {final_record} controls and carries final result {final}.",
                    authority_score=0.88,
                    authority_signal="official_primary",
                    relevance=0.96,
                    boundary_quality=0.90,
                    anchor=anchor,
                ),
            ]
            gold = f"The final supported result for {entity} record {record_id} under {variant} is {final}."
            required = [record_id, variant, final_record, final, "final result"]
            forbidden = [
                f"{obsolete_candidate} was the final result",
                "the final result is disputed",
                "the sources are unresolved",
                "there is no source-of-record answer",
            ]
            near = (
                f"A surface reader sees an obsolete candidate row, but the source-of-record "
                f"explicitly closes it and names {final_record} as the valid final entry."
            )
            return query, gold, contexts, near, required, forbidden, [obsolete_candidate]

        valid = f"candidate {chr(66 + idx % 3)}"
        invalid = f"candidate {chr(65 + idx % 3)}"
        query = f"Which {entity} candidate is valid for {variant}?"
        c1 = (
            f"{tag}: The {authority} lists two candidate records for {entity} under {variant}: "
            f"{invalid} and {valid}. The table warns that candidate status must be checked against "
            f"the final adjudication note before answering."
        )
        c2 = (
            f"{tag}: The final adjudication note marks {invalid} as rejected because it was "
            f"superseded during review. It marks {valid} as the valid current record for {entity} "
            f"under {variant}."
        )
        contexts = [
            _ctx("ctx_001", c1, "The source lists multiple candidates and says final adjudication controls.", authority_score=0.78, authority_signal="domain_expert", relevance=0.88, boundary_quality=0.82, anchor=anchor),
            _ctx("ctx_002", c2, f"The source identifies {valid} as valid and rejects {invalid}.", authority_score=0.91, authority_signal="official_primary", relevance=0.96, boundary_quality=0.90, anchor=anchor),
        ]
        gold = f"{valid.capitalize()} is the valid current record for {entity} under {variant}."
        required = [valid, "valid current record", variant]
        forbidden = [f"{invalid} is valid", "both candidates are equally valid"]
        near = f"A surface reader might treat the two candidates as conflicting, but the final note explicitly validates {valid} and rejects {invalid}."
        return query, gold, contexts, near, required, forbidden, [invalid]

    if pattern == TaxonomyPattern.VERDICT_CONFLICT and idx >= 5:
        record_id = f"{domain.value.upper().replace('_', '-')}-{difficulty.value.upper()}-{idx:02d}"
        wording = [
            ("final verdict", "release sign-off packet"),
            ("execution status", "quality dashboard export"),
            ("release signoff", "approval workflow record"),
            ("test management result", "case-management export"),
            ("closure state", "closure board extract"),
        ][idx % 5]
        verdict_term, source_kind = wording
        pass_first = idx % 2 == 0
        query = (
            f"What {verdict_term} is supported for {entity} record {record_id} "
            f"under {variant}?"
        )
        pass_text = (
            f"{tag}: The {source_kind} for {entity} record {record_id} under {variant} "
            f"identifies the same target item and lists {verdict_term}: PASS. It says the "
            f"review gate was closed with no remaining blocker for that exact record."
        )
        fail_text = (
            f"{tag}: The independent {authority} export for {entity} record {record_id} "
            f"under {variant} identifies the same target item and lists {verdict_term}: FAIL. "
            f"It says the blocker remained open for that exact record at sign-off."
        )
        pass_ctx = _ctx(
            "ctx_001" if pass_first else "ctx_002",
            pass_text,
            f"One authoritative source gives {verdict_term} PASS for the exact record.",
            authority_score=0.90,
            authority_signal="official_primary",
            relevance=0.97,
            boundary_quality=0.92,
            anchor=anchor,
        )
        fail_ctx = _ctx(
            "ctx_002" if pass_first else "ctx_001",
            fail_text,
            f"Another authoritative source gives {verdict_term} FAIL for the exact record.",
            authority_score=0.90,
            authority_signal="official_primary",
            relevance=0.97,
            boundary_quality=0.92,
            anchor=anchor,
        )
        contexts = [pass_ctx, fail_ctx] if pass_first else [fail_ctx, pass_ctx]
        near = (
            "Both sources identify the same entity, variant, and record, but they give "
            "mutually exclusive PASS and FAIL final states."
        )
        forbidden = [
            "final verdict was PASS",
            "final verdict was FAIL",
            "the sources agree",
            "one record is superseded",
            "one record is for a different target",
        ]
        return query, "", contexts, near, ["PASS", "FAIL", record_id], forbidden, []

    if pattern == TaxonomyPattern.VERDICT_CONFLICT:
        query = f"Did {entity} pass the {variant} final status check?"
        c1 = (
            f"{tag}: The final status export for {entity} under {variant} records the checked item "
            f"as PASS and says no blocking issue remained open at sign-off."
        )
        c2 = (
            f"{tag}: A second final status export for the same {entity} under {variant} records "
            f"the checked item as FAIL and says the blocking issue remained unresolved at sign-off."
        )
        contexts = [
            _ctx("ctx_001", c1, "One final status source says PASS.", authority_score=0.86, authority_signal="official_primary", relevance=0.95, boundary_quality=0.88, anchor=anchor),
            _ctx("ctx_002", c2, "Another final status source says FAIL for the same target.", authority_score=0.86, authority_signal="official_primary", relevance=0.95, boundary_quality=0.88, anchor=anchor),
        ]
        near = "The sources target the same entity and variant but give mutually exclusive PASS and FAIL verdicts."
        return query, "", contexts, near, ["PASS", "FAIL"], ["passed without mentioning the fail record"], []

    if pattern == TaxonomyPattern.AUTHORITY_STATUS_CONFLICT:
        query = f"What status is reported for {entity} under {variant}?"
        c1 = (
            f"{tag}: A raw working log says {entity} under {variant} is marked ready and shows an "
            f"intermediate green status from the preparatory checklist."
        )
        c2 = (
            f"{tag}: The {authority} status register for the same {entity} under {variant} "
            f"marks the item as blocked. It does not reference the raw working log or provide "
            f"a reconciliation for the ready flag."
        )
        contexts = [
            _ctx("ctx_001", c1, "A lower-authority intermediate log reports a ready status.", authority_score=0.42, authority_signal="news_secondary", relevance=0.84, boundary_quality=0.72, anchor=anchor),
            _ctx("ctx_002", c2, "The authoritative status register reports blocked without reconciling the ready flag.", authority_score=0.94, authority_signal="official_primary", relevance=0.96, boundary_quality=0.90, anchor=anchor),
        ]
        near = "A naive answer might pick one status, but the retrieved records give incompatible ready and blocked statuses without reconciliation."
        return query, "", contexts, near, ["ready", "blocked", authority], ["status is simply ready", "status is simply blocked without noting the conflict"], []

    if pattern == TaxonomyPattern.VERSION_BUILD_MISMATCH:
        if idx >= 5:
            requested = variant
            wrong = NEIGHBOR_VARIANTS.get(variant, f"adjacent slice {idx}")
            record_id = f"{domain.value.upper().replace('_', '-')}-{difficulty.value.upper()}-{idx:02d}"
            wrong_result = ["PASS", "cleared", "accepted", "green", "completed"][idx % 5]
            query = (
                f"What final result was recorded for {entity} record {record_id} "
                f"on {requested}?"
            )
            c1 = (
                f"{tag}: The retrieved final-result record key is {wrong} for {entity} "
                f"record {record_id}. It lists final result: {wrong_result} for {wrong}."
            )
            c2 = (
                f"{tag}: The traceability appendix repeats the {wrong} key for record "
                f"{record_id}. Its notes, reviewers, and archive references are all indexed "
                f"under {wrong}, an adjacent slice rather than the requested {requested}."
            )
            contexts = [
                _ctx(
                    "ctx_001",
                    c1,
                    f"The retrieved final result belongs to {wrong}, not the requested build.",
                    authority_score=0.86,
                    authority_signal="official_primary",
                    relevance=0.74,
                    boundary_quality=0.84,
                    anchor=f"{wrong}; V8 patch {idx}",
                ),
                _ctx(
                    "ctx_002",
                    c2,
                    "The appendix repeats the neighboring build rather than the requested build.",
                    authority_score=0.83,
                    authority_signal="domain_expert",
                    relevance=0.72,
                    boundary_quality=0.84,
                    anchor=f"{wrong}; V8 patch {idx}",
                ),
            ]
            near = (
                f"The evidence is for the same entity and record family, but it only supports "
                f"{wrong}; it cannot answer the requested {requested} final result."
            )
            forbidden = [
                f"final result for {requested}",
                f"{requested} was {wrong_result}",
                "the sources conflict for the requested build",
                "the wrong build answers the query",
            ]
            return query, "", contexts, near, [wrong, record_id], forbidden, []

        requested = variant
        wrong = NEIGHBOR_VARIANTS.get(variant, f"adjacent slice {idx}")
        query = f"What was the final result for {entity} on {requested}?"
        c1 = (
            f"{tag}: The retrieved record key is {wrong} for {entity}. It says "
            f"that adjacent variant completed successfully."
        )
        c2 = (
            f"{tag}: The appendix repeats the {wrong} key and keeps the archive references "
            f"under that adjacent variant rather than the requested {requested}."
        )
        contexts = [
            _ctx("ctx_001", c1, "The evidence gives a result for the wrong neighboring variant.", authority_score=0.82, authority_signal="official_primary", relevance=0.70, boundary_quality=0.78, anchor=f"{wrong}; V8 probe {idx}"),
            _ctx("ctx_002", c2, "The appendix limits the result to the wrong variant.", authority_score=0.80, authority_signal="domain_expert", relevance=0.68, boundary_quality=0.80, anchor=f"{wrong}; V8 probe {idx}"),
        ]
        near = f"The sources look relevant but answer {wrong}, while the query asks for {requested}."
        return query, "", contexts, near, [wrong], [f"final result for {requested}"], []

    if pattern == TaxonomyPattern.MISSING_EXECUTION_RESULT:
        query = f"What final outcome was recorded for {entity} under {variant}?"
        c1 = (
            f"{tag}: The preparation record for {entity} under {variant} lists the setup steps, "
            f"inputs, reviewers, and acceptance criteria to be used before execution."
        )
        c2 = (
            f"{tag}: The schedule note says execution was planned after checklist completion, "
            f"and lists the planned owner, checkpoint date, and handoff dependency for the run."
        )
        contexts = [
            _ctx("ctx_001", c1, "The source describes setup and criteria but no outcome.", authority_score=0.78, authority_signal="domain_expert", relevance=0.76, boundary_quality=0.80, anchor=anchor),
            _ctx("ctx_002", c2, "The source gives schedule metadata and handoff details, not the final result.", authority_score=0.81, authority_signal="official_primary", relevance=0.78, boundary_quality=0.82, anchor=anchor),
        ]
        near = "The evidence is on-topic, but it stops at setup and scheduling without the requested execution result."
        return query, "", contexts, near, ["setup", "planned"], ["final outcome was recorded", "no final outcome was recorded"], []

    raise ValueError(f"unsupported pattern: {pattern}")


def build_case(slot: dict[str, Any]) -> dict[str, Any]:
    pattern = TaxonomyPattern(slot["pattern"])
    domain = Domain(slot["domain"])
    difficulty = Difficulty(slot["difficulty"])
    cell = Cell(pattern=pattern, domain=domain, difficulty=difficulty)
    idx = _slot_index(str(slot["case_id"]))
    classification, category = _metadata(pattern, difficulty)
    query, gold, contexts, near_reason, required, forbidden, forbidden_elements = _case_texts(
        pattern, domain, difficulty, idx
    )

    governance = {"classification": classification}
    governance.update(_scores(classification, difficulty))
    case: dict[str, Any] = {
        "id": slot["case_id"],
        "version": "fitz-gov-8.0",
        "input": {
            "query": query,
            "query_rewritten": query.rstrip("?") + "?",
            "contexts": contexts,
            "evidence_chain": {
                "order": [c["id"] for c in contexts],
                "reasoning": "Read the records together because the decision depends on whether they resolve, conflict, or omit the requested status.",
            },
        },
        "governance": governance,
        "taxonomy": {
            "governance_class": classification,
            "pattern": pattern.value,
            "pattern_description": PATTERN_DESCRIPTIONS[pattern],
            "cell_id": cell.cell_id,
        },
        "evaluation": {
            "mode": "governance",
            "check_mode_match": True,
            "required_elements": required if classification == "TRUSTWORTHY" else [],
            "forbidden_claims": forbidden,
            "forbidden_elements": forbidden_elements,
        },
        "routing": {
            "expert_fired": domain.value,
            "secondary_expert": "conflict_detection" if classification == "DISPUTED" else None,
            "routing_confidence": 0.86 if difficulty != Difficulty.HARD else 0.78,
        },
        "meta": {
            "dataset_version": "v8",
            "difficulty": difficulty.value,
            "category": category,
            "confidence_level": DIFF_WORDS[difficulty]["confidence"],
            "near_miss_class": governance["boundary_proximity"]["nearest_class"],
            "near_miss_reason": near_reason,
        },
    }
    if classification == "TRUSTWORTHY":
        attribution = contexts[-1]["id"] if contexts else "ctx_001"
        case["meta"]["grounding_targets"] = {
            "gold_answer": gold,
            "sentences": [{"text": gold, "attributions": [attribution]}],
        }
    return case


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    batch_paths = sorted(args.batch_dir.glob("batch_*.json"))
    total = 0
    for batch_path in batch_paths:
        batch = json.loads(batch_path.read_text(encoding="utf-8"))
        out_path = args.out_dir / f"{batch_path.stem}.jsonl"
        rows = []
        for slot in batch.get("slots", []):
            if not isinstance(slot, dict):
                continue
            rows.append({"case_id": slot["case_id"], "case": build_case(slot)})
        out_path.write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
            encoding="utf-8",
        )
        total += len(rows)
        print(f"{out_path}: {len(rows)} rows")
    print(f"Generated {total} rows from {len(batch_paths)} batches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
