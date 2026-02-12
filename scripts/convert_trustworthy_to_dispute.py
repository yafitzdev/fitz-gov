#!/usr/bin/env python3
"""
Convert specific trustworthy_direct and trustworthy_hedged cases to dispute cases.

This script:
1. Reads trustworthy_direct.json and trustworthy_hedged.json
2. Converts 50 specific cases to dispute cases by modifying their contexts
3. Removes those cases from the source files
4. Appends the converted cases to dispute.json

The conversion removes resolving/authoritative/consensus contexts to create
genuine disputes from cases that previously had resolutions.

Idempotent: checks metadata.converted_from in dispute.json to skip already-converted cases.
"""

import json
import re
import sys
from pathlib import Path
from typing import Any

# --- Configuration ---

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "tier1_core"

TRUSTWORTHY_DIRECT_PATH = DATA_DIR / "trustworthy_direct.json"
TRUSTWORTHY_HEDGED_PATH = DATA_DIR / "trustworthy_hedged.json"
DISPUTE_PATH = DATA_DIR / "dispute.json"

STARTING_DISPUTE_ID = 568

# --- Conversion target definitions ---

# Group A: contradiction_resolved -> dispute (20 cases from trustworthy_direct)
CONTRADICTION_RESOLVED_IDS = [
    "t1_confident_hard_215",
    "t1_confident_hard_216",
    "t1_confident_hard_217",
    "t1_confident_hard_218",
    "t1_confident_hard_219",
    "t1_confident_hard_225",
    "t1_confident_hard_226",
    "t1_confident_hard_227",
    "t1_confident_hard_228",
    "t1_confident_hard_229",
    "t1_confident_hard_600",
    "t1_confident_hard_601",
    "t1_confident_hard_602",
    "t1_confident_hard_603",
    "t1_confident_hard_604",
    "t1_confident_hard_836",
    "t1_confident_medium_837",
    "t1_confident_hard_838",
    "t1_confident_medium_839",
    "t1_confident_hard_840",
]

# Group B: opposing_with_consensus -> dispute (15 cases from trustworthy_direct)
OPPOSING_WITH_CONSENSUS_IDS = [
    "t1_confident_hard_606",
    "t1_confident_hard_607",
    "t1_confident_hard_608",
    "t1_confident_hard_609",
    "t1_confident_hard_610",
    "t1_confident_hard_611",
    "t1_confident_hard_806",
    "t1_confident_hard_807",
    "t1_confident_medium_808",
    "t1_confident_medium_809",
    "t1_confident_hard_810",
    "t1_confident_medium_811",
    "t1_confident_hard_812",
    "t1_confident_medium_813",
    "t1_confident_hard_814",
]

# Group C: different_framing -> dispute (10 cases from trustworthy_direct)
DIFFERENT_FRAMING_IDS = [
    "t1_confident_hard_220",
    "t1_confident_hard_221",
    "t1_confident_hard_222",
    "t1_confident_hard_223",
    "t1_confident_hard_224",
    "t1_confident_hard_230",
    "t1_confident_hard_231",
    "t1_confident_hard_232",
    "t1_confident_hard_233",
    "t1_confident_hard_234",
]

# Group D: version_overlap -> dispute (5 cases from trustworthy_hedged)
VERSION_OVERLAP_IDS = [
    "t1_qualify_hard_026",
    "t1_qualify_hard_027",
    "t1_qualify_hard_135",
    "t1_qualify_hard_136",
    "t1_qualify_hard_137",
]

# All IDs that come from trustworthy_direct
ALL_DIRECT_IDS = set(CONTRADICTION_RESOLVED_IDS + OPPOSING_WITH_CONSENSUS_IDS + DIFFERENT_FRAMING_IDS)

# All IDs that come from trustworthy_hedged
ALL_HEDGED_IDS = set(VERSION_OVERLAP_IDS)

# Combined
ALL_TARGET_IDS = ALL_DIRECT_IDS | ALL_HEDGED_IDS


# --- Conversion methods ---

# Patterns that indicate a resolution/reconciliation in a single context
RESOLUTION_PATTERNS = re.compile(
    r"(?i)\b(?:"
    r"however|but\s+(?:in\s+fact|actually|the\s+(?:authoritative|official|definitive))"
    r"|in\s+fact|actually,?\s+(?:the|both|this|these)"
    r"|the\s+(?:authoritative|official|definitive)\s+(?:source|answer|data|report)"
    r"|according\s+to\s+the\s+(?:official|definitive|authoritative)"
    r"|this\s+(?:resolves|explains|clarifies|reconciles)"
    r"|the\s+(?:discrepancy|difference|contradiction)\s+(?:is|was)\s+(?:explained|resolved|due\s+to)"
    r"|when\s+(?:we|you)\s+(?:account|factor|consider)"
    r"|supersedes|takes\s+precedence|prevails\s+over"
    r")\b"
)

# Patterns indicating consensus language in opposing_with_consensus cases
CONSENSUS_PATTERNS = re.compile(
    r"(?i)\b(?:"
    r"overwhelming\s+evidence|scientific\s+consensus|meta-analyses?\s+show"
    r"|systematic\s+review|peer-reviewed|comprehensive\s+review"
    r"|independently\s+(?:confirmed?|verified|validated)"
    r"|(?:strong|clear|robust)\s+(?:evidence|consensus)"
    r"|widely\s+(?:accepted|established|recognized|confirmed)"
    r"|the\s+evidence\s+(?:is\s+)?(?:clear|overwhelming|unequivocal)"
    r"|no\s+(?:credible|substantiated|reliable)\s+evidence"
    r"|has\s+been\s+(?:debunked|discredited|retracted|refuted)"
    r"|the\s+(?:scientific|medical|research)\s+community\s+(?:agrees|consensus)"
    r")\b"
)

# Patterns indicating reconciliation in different_framing cases
RECONCILING_PATTERNS = re.compile(
    r"(?i)\b(?:"
    r"this\s+(?:is|represents)\s+(?:not\s+)?a\s+(?:contradiction|disagreement|conflict)"
    r"|both\s+(?:sources|statements|figures|numbers)\s+(?:are|agree|confirm|describe)"
    r"|the\s+(?:difference|discrepancy)\s+(?:is|reflects|represents)\s+(?:a\s+)?"
    r"(?:standard|normal|typical|expected|different)\s+(?:distinction|measurement|framing|granularity)"
    r"|not\s+a\s+(?:contradiction|disagreement|conflict|dispute)"
    r"|different\s+(?:levels?\s+of\s+)?(?:precision|granularity|framing|time\s*(?:frame|scale|period))"
    r"|(?:seasonal|temporary|transient)\s+(?:fluctuation|variation|dip|decline)"
    r"|within\s+(?:measurement\s+)?uncertainty"
    r"|functionally\s+(?:the\s+same|identical|equivalent)"
    r")\b"
)

# Patterns for version overlap - migration/compatibility language
VERSION_COMPAT_PATTERNS = re.compile(
    r"(?i)\b(?:"
    r"recommend(?:s|ed)?\s+(?:migration|migrating|switching|using\s+(?:instead|alternatives?))"
    r"|deprecated|legacy|end[- ]of[- ]life|EOL|sunset"
    r"|should\s+(?:avoid|not\s+(?:be\s+)?use[d]?|migrate|switch)"
    r"|replacement|alternative|instead\s+(?:of|use)"
    r"|has\s+been\s+(?:renamed|replaced|superseded|removed)"
    r"|UNSAFE_"
    r")\b"
)


def _find_resolution_context_index(contexts: list[str]) -> int | None:
    """Find the index of the context most likely to be the resolution/authoritative one.

    For multi-context cases, checks each context for resolution patterns.
    Returns the index of the best candidate, preferring the last context.
    """
    if len(contexts) <= 1:
        return None

    # Check from the end - resolution context is typically last
    # But also score each context for resolution indicators
    best_idx = None
    best_score = 0

    for i, ctx in enumerate(contexts):
        score = len(RESOLUTION_PATTERNS.findall(ctx))
        # Bonus for being the last context (typical position for resolution)
        if i == len(contexts) - 1:
            score += 2
        if score > best_score:
            best_score = score
            best_idx = i

    # If no clear resolution pattern found, default to last context
    if best_idx is None:
        best_idx = len(contexts) - 1

    return best_idx


def _truncate_single_context_resolution(text: str) -> str:
    """For a single context containing both conflict and resolution,
    truncate to keep only the conflicting part."""
    # Split on resolution transition phrases
    split_patterns = [
        r"(?i)\.\s*(?:However|But in fact|But actually|In fact|Actually),?\s+",
        r"(?i)\.\s*(?:The (?:authoritative|official|definitive) (?:source|answer|data))",
        r"(?i)\.\s*(?:This (?:resolves|explains|clarifies|reconciles))",
        r"(?i)\.\s*(?:The (?:discrepancy|difference|contradiction) (?:is|was) (?:explained|resolved))",
    ]

    for pattern in split_patterns:
        parts = re.split(pattern, text, maxsplit=1)
        if len(parts) > 1:
            # Keep the part before the resolution, ensure it ends properly
            result = parts[0].rstrip()
            if not result.endswith("."):
                result += "."
            return result

    # No resolution pattern found - return as-is
    return text


def _find_consensus_context_index(contexts: list[str]) -> int | None:
    """Find the context that provides consensus/authoritative confirmation.

    This is the context that says things like 'overwhelming evidence',
    'scientific consensus', 'meta-analyses show', etc.
    """
    if len(contexts) <= 1:
        return None

    best_idx = None
    best_score = 0

    for i, ctx in enumerate(contexts):
        score = len(CONSENSUS_PATTERNS.findall(ctx))
        if score > best_score:
            best_score = score
            best_idx = i

    return best_idx


def _remove_consensus_framing_from_context(text: str) -> str:
    """Remove consensus framing from a context that mentions both consensus and opposition."""
    # Remove sentences that contain consensus language
    sentences = re.split(r"(?<=[.!?])\s+", text)
    filtered = []
    for sentence in sentences:
        if not CONSENSUS_PATTERNS.search(sentence):
            filtered.append(sentence)

    if not filtered:
        # Don't return empty - keep original if all sentences had consensus
        return text

    return " ".join(filtered)


def _find_reconciling_context_index(contexts: list[str]) -> int | None:
    """Find the context that reconciles different framings."""
    if len(contexts) <= 1:
        return None

    best_idx = None
    best_score = 0

    for i, ctx in enumerate(contexts):
        score = len(RECONCILING_PATTERNS.findall(ctx))
        if score > best_score:
            best_score = score
            best_idx = i

    return best_idx


def _find_version_compat_context_index(contexts: list[str]) -> int | None:
    """Find the context that explains version compatibility or migration path."""
    if len(contexts) <= 1:
        return None

    best_idx = None
    best_score = 0

    for i, ctx in enumerate(contexts):
        score = len(VERSION_COMPAT_PATTERNS.findall(ctx))
        if score > best_score:
            best_score = score
            best_idx = i

    return best_idx


def convert_contradiction_resolved(case: dict[str, Any]) -> dict[str, Any]:
    """Convert a contradiction_resolved case to dispute.

    Method: Remove the context that resolves the contradiction.
    If 2+ contexts, remove the one containing resolution language (prefer last).
    If 1 context, truncate to keep only the conflicting part.
    """
    contexts = list(case["contexts"])

    if len(contexts) >= 2:
        # For 3-context cases, identify which contexts are the authoritative/resolving ones
        # For cases with 3 contexts (like 600-604), we need to be smarter:
        # typically the pattern is: source1 (one claim), source2 (different claim), source3 (explains/resolves)
        if len(contexts) == 3:
            # Score each context for resolution/authority
            scores = []
            for i, ctx in enumerate(contexts):
                score = len(RESOLUTION_PATTERNS.findall(ctx))
                score += len(CONSENSUS_PATTERNS.findall(ctx))
                scores.append((score, i))
            scores.sort(reverse=True)

            # Remove the highest-scoring context (most authoritative/resolving)
            remove_idx = scores[0][1]

            # If top two have similar scores, also check if one explicitly reconciles
            if scores[0][0] > 0 and scores[1][0] > 0 and scores[0][0] - scores[1][0] <= 1:
                # Remove the later one (more likely the wrap-up resolution)
                remove_idx = max(scores[0][1], scores[1][1])

            contexts.pop(remove_idx)
        else:
            # 2 contexts: remove the one with more resolution language, defaulting to last
            idx = _find_resolution_context_index(contexts)
            if idx is not None:
                contexts.pop(idx)
            else:
                contexts.pop(-1)
    elif len(contexts) == 1:
        contexts[0] = _truncate_single_context_resolution(contexts[0])

    return contexts


def convert_opposing_with_consensus(case: dict[str, Any]) -> dict[str, Any]:
    """Convert an opposing_with_consensus case to dispute.

    Method: Remove the consensus/authoritative context. If a context mentions both
    consensus and opposition, rewrite it to remove the consensus framing.
    Keep only the opposing viewpoints to make them appear equally weighted.
    """
    contexts = list(case["contexts"])

    if len(contexts) >= 2:
        # Find all contexts with consensus language and those without
        consensus_indices = []
        opposing_indices = []
        mixed_indices = []

        for i, ctx in enumerate(contexts):
            consensus_score = len(CONSENSUS_PATTERNS.findall(ctx))
            # Check if context also has opposing/contrarian content
            has_opposing = bool(re.search(
                r"(?i)\b(?:however|but|critics|skeptics|opponents|contrary|dispute[sd]?|challenge[sd]?|question[sd]?)\b",
                ctx
            ))

            if consensus_score > 0 and has_opposing:
                mixed_indices.append(i)
            elif consensus_score > 0:
                consensus_indices.append(i)
            else:
                opposing_indices.append(i)

        # Remove pure consensus contexts
        indices_to_remove = set(consensus_indices)

        # For mixed contexts, rewrite to remove consensus framing
        for i in mixed_indices:
            contexts[i] = _remove_consensus_framing_from_context(contexts[i])

        # Ensure we keep at least 2 contexts for a dispute
        if len(contexts) - len(indices_to_remove) < 2:
            # Keep the one with the least consensus language
            sorted_consensus = sorted(consensus_indices,
                                      key=lambda i: len(CONSENSUS_PATTERNS.findall(contexts[i])))
            # Keep enough to have at least 2
            while len(contexts) - len(indices_to_remove) < 2 and sorted_consensus:
                keep_idx = sorted_consensus.pop(0)
                indices_to_remove.discard(keep_idx)
                # Rewrite this kept consensus context to remove framing
                contexts[keep_idx] = _remove_consensus_framing_from_context(contexts[keep_idx])

        # Remove in reverse order to preserve indices
        for idx in sorted(indices_to_remove, reverse=True):
            contexts.pop(idx)
    elif len(contexts) == 1:
        contexts[0] = _remove_consensus_framing_from_context(contexts[0])

    return contexts


def convert_different_framing(case: dict[str, Any]) -> dict[str, Any]:
    """Convert a different_framing case to dispute.

    Method: Remove the reconciling context that explains how different framings
    are compatible. Keep contexts that appear to contradict each other.
    """
    contexts = list(case["contexts"])

    if len(contexts) >= 2:
        # Find the most reconciling context
        reconcile_idx = _find_reconciling_context_index(contexts)

        if reconcile_idx is not None and len(contexts) > 2:
            contexts.pop(reconcile_idx)
        elif reconcile_idx is not None and len(contexts) == 2:
            # With only 2 contexts, we can't remove one entirely
            # Instead, look for which context has the reconciling language
            # and try to strip it
            ctx = contexts[reconcile_idx]
            sentences = re.split(r"(?<=[.!?])\s+", ctx)
            filtered = [s for s in sentences if not RECONCILING_PATTERNS.search(s)]
            if filtered:
                contexts[reconcile_idx] = " ".join(filtered)
            # If all sentences are reconciling, just keep the contexts as-is
            # The surface-level numbers/claims already look contradictory
        else:
            # No reconciling pattern found - these are "different framing" cases
            # The contexts already appear contradictory on the surface
            # Just keep them as-is (they look like disputes without the explanation)
            pass

    return contexts


def convert_version_overlap(case: dict[str, Any]) -> dict[str, Any]:
    """Convert a version_overlap case to dispute.

    Method: Remove the context that explains version compatibility or migration path.
    Keep conflicting version-specific instructions.
    """
    contexts = list(case["contexts"])

    if len(contexts) >= 2:
        compat_idx = _find_version_compat_context_index(contexts)

        if compat_idx is not None:
            # Check how many contexts we'd have left
            if len(contexts) > 2:
                contexts.pop(compat_idx)
            else:
                # Only 2 contexts - strip deprecation/migration language from the compat context
                # to make it look like two competing instructions
                ctx = contexts[compat_idx]
                sentences = re.split(r"(?<=[.!?])\s+", ctx)
                # Keep only sentences that provide instructions, not deprecation warnings
                filtered = [s for s in sentences if not VERSION_COMPAT_PATTERNS.search(s)]
                if filtered and len(filtered) >= 1:
                    contexts[compat_idx] = " ".join(filtered)
                else:
                    # Can't meaningfully strip - remove and keep the other
                    # But then we'd have only 1 context for a dispute, which is weak
                    # So in this case, just remove and note
                    contexts.pop(compat_idx)
        else:
            # No clear compatibility context - check if any context is mostly about deprecation
            # and remove/strip that
            for i in range(len(contexts) - 1, -1, -1):
                if VERSION_COMPAT_PATTERNS.search(contexts[i]):
                    if len(contexts) > 2:
                        contexts.pop(i)
                        break
                    else:
                        # Strip deprecation sentences
                        sentences = re.split(r"(?<=[.!?])\s+", contexts[i])
                        filtered = [s for s in sentences if not VERSION_COMPAT_PATTERNS.search(s)]
                        if filtered:
                            contexts[i] = " ".join(filtered)
                        break

    return contexts


def build_dispute_case(
    original_case: dict[str, Any],
    new_id: str,
    new_contexts: list[str],
    subcategory: str,
    conversion_method: str,
) -> dict[str, Any]:
    """Build a new dispute case from the original case and converted contexts."""

    # Build description for the dispute
    original_desc = original_case.get("description", "")
    dispute_description = f"Converted dispute: {original_desc}"

    # Build rationale explaining the dispute
    original_rationale = original_case.get("rationale", "")
    dispute_rationale = (
        f"With the resolving/authoritative context removed, the remaining sources "
        f"present conflicting information without resolution. "
        f"Original resolution: {original_rationale}"
    )

    dispute_case: dict[str, Any] = {
        "id": new_id,
        "category": "dispute",
        "subcategory": subcategory,
        "difficulty": "hard",
        "query": original_case["query"],
        "contexts": new_contexts,
        "expected_mode": "disputed",
        "description": dispute_description,
        "rationale": dispute_rationale,
        "metadata": {
            "converted_from": original_case["id"],
            "conversion_method": conversion_method,
        },
    }

    return dispute_case


def get_conversion_group(case_id: str) -> tuple[str, str, str] | None:
    """Return (subcategory, conversion_method, group_name) for a given case ID,
    or None if the case is not a conversion target."""
    if case_id in CONTRADICTION_RESOLVED_IDS:
        return ("converted_contradiction", "remove_resolution_context", "contradiction_resolved")
    elif case_id in OPPOSING_WITH_CONSENSUS_IDS:
        return ("converted_consensus_removed", "remove_consensus_context", "opposing_with_consensus")
    elif case_id in DIFFERENT_FRAMING_IDS:
        return ("converted_framing_conflict", "remove_reconciling_context", "different_framing")
    elif case_id in VERSION_OVERLAP_IDS:
        return ("converted_version_conflict", "remove_version_compat_context", "version_overlap")
    return None


def convert_case(case: dict[str, Any], new_id: str) -> dict[str, Any]:
    """Convert a single case to a dispute case based on its conversion group."""
    group_info = get_conversion_group(case["id"])
    if group_info is None:
        raise ValueError(f"Case {case['id']} is not a conversion target")

    subcategory, conversion_method, group_name = group_info

    # Apply the appropriate conversion method
    if group_name == "contradiction_resolved":
        new_contexts = convert_contradiction_resolved(case)
    elif group_name == "opposing_with_consensus":
        new_contexts = convert_opposing_with_consensus(case)
    elif group_name == "different_framing":
        new_contexts = convert_different_framing(case)
    elif group_name == "version_overlap":
        new_contexts = convert_version_overlap(case)
    else:
        raise ValueError(f"Unknown group: {group_name}")

    return build_dispute_case(
        original_case=case,
        new_id=new_id,
        new_contexts=new_contexts,
        subcategory=subcategory,
        conversion_method=conversion_method,
    )


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict[str, Any]) -> None:
    """Save a JSON file with indent=2 and ensure_ascii=False."""
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main() -> None:
    print("=" * 70)
    print("Convert Trustworthy Cases to Dispute Cases")
    print("=" * 70)

    # Load all three files
    print(f"\nLoading {TRUSTWORTHY_DIRECT_PATH.name}...")
    direct_data = load_json(TRUSTWORTHY_DIRECT_PATH)
    print(f"  {len(direct_data['cases'])} cases loaded")

    print(f"Loading {TRUSTWORTHY_HEDGED_PATH.name}...")
    hedged_data = load_json(TRUSTWORTHY_HEDGED_PATH)
    print(f"  {len(hedged_data['cases'])} cases loaded")

    print(f"Loading {DISPUTE_PATH.name}...")
    dispute_data = load_json(DISPUTE_PATH)
    print(f"  {len(dispute_data['cases'])} cases loaded")

    # Check idempotency: find already-converted cases
    already_converted = set()
    for case in dispute_data["cases"]:
        metadata = case.get("metadata", {})
        if isinstance(metadata, dict) and "converted_from" in metadata:
            already_converted.add(metadata["converted_from"])

    if already_converted:
        print(f"\nAlready converted ({len(already_converted)} cases):")
        for orig_id in sorted(already_converted):
            print(f"  - {orig_id}")

    # Build lookup of target cases from source files
    direct_cases_by_id: dict[str, dict[str, Any]] = {}
    for case in direct_data["cases"]:
        if case["id"] in ALL_DIRECT_IDS:
            direct_cases_by_id[case["id"]] = case

    hedged_cases_by_id: dict[str, dict[str, Any]] = {}
    for case in hedged_data["cases"]:
        if case["id"] in ALL_HEDGED_IDS:
            hedged_cases_by_id[case["id"]] = case

    # Verify all target IDs were found
    all_found = set(direct_cases_by_id.keys()) | set(hedged_cases_by_id.keys())
    missing = ALL_TARGET_IDS - all_found
    if missing:
        print(f"\nWARNING: {len(missing)} target case(s) not found in source files:")
        for mid in sorted(missing):
            print(f"  - {mid}")

    # Determine which cases need conversion (not already converted and found)
    to_convert_ids = ALL_TARGET_IDS - already_converted
    to_convert_ids = to_convert_ids & all_found  # only convert what we found

    if not to_convert_ids:
        print("\nAll target cases have already been converted. Nothing to do.")
        return

    print(f"\nCases to convert: {len(to_convert_ids)}")

    # Build the ordered list of cases to convert, following the ID list order
    ordered_ids = (
        CONTRADICTION_RESOLVED_IDS
        + OPPOSING_WITH_CONSENSUS_IDS
        + DIFFERENT_FRAMING_IDS
        + VERSION_OVERLAP_IDS
    )

    # Filter to only IDs that need conversion
    ordered_to_convert = [cid for cid in ordered_ids if cid in to_convert_ids]

    # Assign new dispute IDs
    # Figure out the next available ID number based on what already exists
    # Check both the starting ID and any that might have been added in previous partial runs
    existing_dispute_nums = set()
    for case in dispute_data["cases"]:
        # Extract number from ID like t1_dispute_hard_567
        match = re.search(r"t1_dispute_(?:hard|medium|easy)_(\d+)", case["id"])
        if match:
            existing_dispute_nums.add(int(match.group(1)))

    next_id_num = STARTING_DISPUTE_ID
    # Advance past any already-used IDs
    while next_id_num in existing_dispute_nums:
        next_id_num += 1

    # Convert cases
    converted_cases: list[dict[str, Any]] = []
    conversion_log: list[tuple[str, str, str, int, int]] = []  # (orig_id, new_id, method, orig_ctx_count, new_ctx_count)

    for case_id in ordered_to_convert:
        # Look up the original case
        if case_id in direct_cases_by_id:
            original = direct_cases_by_id[case_id]
        elif case_id in hedged_cases_by_id:
            original = hedged_cases_by_id[case_id]
        else:
            print(f"  SKIP: {case_id} (not found)")
            continue

        new_id = f"t1_dispute_hard_{next_id_num}"
        next_id_num += 1

        # Ensure we don't collide with existing IDs
        while (next_id_num - 1) in existing_dispute_nums:
            next_id_num += 1
            new_id = f"t1_dispute_hard_{next_id_num - 1}"

        try:
            converted = convert_case(original, new_id)
            converted_cases.append(converted)

            group_info = get_conversion_group(case_id)
            conversion_log.append((
                case_id,
                new_id,
                group_info[2] if group_info else "unknown",
                len(original["contexts"]),
                len(converted["contexts"]),
            ))
        except Exception as e:
            print(f"  ERROR converting {case_id}: {e}")
            continue

    if not converted_cases:
        print("\nNo cases were converted. Exiting without modifying files.")
        return

    # Remove converted cases from source files
    direct_ids_to_remove = {c["id"] for c in converted_cases
                            if c["metadata"]["converted_from"] in ALL_DIRECT_IDS}
    hedged_ids_to_remove = {c["id"] for c in converted_cases
                            if c["metadata"]["converted_from"] in ALL_HEDGED_IDS}

    # Get the original IDs to remove
    direct_orig_to_remove = {c["metadata"]["converted_from"] for c in converted_cases
                             if c["metadata"]["converted_from"] in ALL_DIRECT_IDS}
    hedged_orig_to_remove = {c["metadata"]["converted_from"] for c in converted_cases
                             if c["metadata"]["converted_from"] in ALL_HEDGED_IDS}

    original_direct_count = len(direct_data["cases"])
    direct_data["cases"] = [c for c in direct_data["cases"] if c["id"] not in direct_orig_to_remove]
    removed_direct = original_direct_count - len(direct_data["cases"])

    original_hedged_count = len(hedged_data["cases"])
    hedged_data["cases"] = [c for c in hedged_data["cases"] if c["id"] not in hedged_orig_to_remove]
    removed_hedged = original_hedged_count - len(hedged_data["cases"])

    # Add converted cases to dispute.json
    dispute_data["cases"].extend(converted_cases)

    # Write all three files back
    print(f"\nWriting {TRUSTWORTHY_DIRECT_PATH.name}...")
    save_json(TRUSTWORTHY_DIRECT_PATH, direct_data)
    print(f"  {len(direct_data['cases'])} cases (removed {removed_direct})")

    print(f"Writing {TRUSTWORTHY_HEDGED_PATH.name}...")
    save_json(TRUSTWORTHY_HEDGED_PATH, hedged_data)
    print(f"  {len(hedged_data['cases'])} cases (removed {removed_hedged})")

    print(f"Writing {DISPUTE_PATH.name}...")
    save_json(DISPUTE_PATH, dispute_data)
    print(f"  {len(dispute_data['cases'])} cases (added {len(converted_cases)})")

    # Print summary
    print("\n" + "=" * 70)
    print("CONVERSION SUMMARY")
    print("=" * 70)

    # Group by conversion method
    groups: dict[str, list[tuple[str, str, str, int, int]]] = {}
    for entry in conversion_log:
        group = entry[2]
        groups.setdefault(group, []).append(entry)

    for group_name, entries in groups.items():
        print(f"\n{group_name} ({len(entries)} cases):")
        for orig_id, new_id, _, orig_ctx, new_ctx in entries:
            ctx_change = f"{orig_ctx} -> {new_ctx} contexts"
            print(f"  {orig_id} -> {new_id} ({ctx_change})")

    print(f"\nTotal converted: {len(converted_cases)}")
    print(f"Removed from trustworthy_direct: {removed_direct}")
    print(f"Removed from trustworthy_hedged: {removed_hedged}")
    print(f"Added to dispute: {len(converted_cases)}")
    print(f"Dispute cases total: {len(dispute_data['cases'])}")

    # Verify counts
    expected_total = 50
    if len(converted_cases) < expected_total:
        skipped = expected_total - len(converted_cases)
        already_done = len(already_converted & ALL_TARGET_IDS)
        not_found = len(missing)
        print(f"\nNote: {skipped} cases not converted in this run:")
        if already_done > 0:
            print(f"  - {already_done} already converted (idempotency check)")
        if not_found > 0:
            print(f"  - {not_found} not found in source files")

    print("\nDone.")


if __name__ == "__main__":
    main()
