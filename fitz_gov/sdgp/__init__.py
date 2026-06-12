"""fitz-gov Synthetic Data Generation Pipeline (SDGP).

The cell-targeted generator that produces fitz-gov V6+ cases. Distinct from
the older corpus-based `fitz_gov.generator` which mapped a user-supplied chunk
corpus into the legacy 4-class scheme.

Pipeline (per pyrrho ROADMAP.md §4):

    Distribution Monitor (cell coverage)
        ↓
    Cell Gap Vector (which taxonomy × domain × difficulty cell is sparsest)
        ↓
    Case Generator (Claude Code / Codex subagent / local LLM, cell-spec prompt)
        ↓
    Structural Checker (schema + signal coherence + taxonomy pattern match)
        ↓
    Blind Labeler (opposite model, independent labeling)
        ↓
    Conflict Resolver (disagreements → human review queue)
        ↓
    Vault (idempotent append + cell index + provenance)
        ↓
    Distribution Monitor (updated)

This package builds those layers from the inside out — the taxonomy and
vault first (everything else depends on them), then the checker, then the
provider abstraction + gap detector + prompts + orchestrator.
"""

from .checker import (
    Checker,
    CheckIssue,
    CheckResult,
    Severity,
    case_dedup_hash,
    hashes_from,
)
from .blind_label import (
    BLIND_LABEL_SYSTEM,
    ParsedBlindLabel,
    blind_label_assessment_rows,
    blind_label_score_summary,
    build_blind_label_prompt,
    bucketed_assessment_rows,
    case_ids_from_rows,
    disagreement_rows,
    label_queue_row,
    markdown_score_report,
    normalize_label,
    parse_blind_label_response,
    review_queue_rows,
    sample_queue_rows,
    second_pass_ledger_rows,
)
from .completeness import (
    CompletenessIssue,
    audit_case_completeness,
    cases_needing_training_completion,
    is_training_complete,
    summarize_completeness,
)
from .cost import CostTracker, estimate_tokens
from .evaluation_completion import (
    EVALUATION_COMPLETION_SYSTEM,
    build_evaluation_completion_prompt,
    complete_evaluation_with_provider,
    parse_evaluation_completion_response,
)
from .evaluation_fields import (
    EvaluationIssue,
    EvaluationPromotionResult,
    audit_evaluation_fields,
    build_canonical_evaluation,
    merge_evaluation_overlay,
    needs_evaluation_enrichment,
    promote_evaluation_fields,
)
from .gap_detector import (
    CellFilter,
    CellTarget,
    Gap,
    GapDetector,
    PriorityWeights,
    rank_from_vault,
)
from .retrieval_control_gap_detector import (
    CollapsedAnswerabilityShape,
    RetrievalControlCell,
    RetrievalControlCellFilter,
    RetrievalControlCellTarget,
    RetrievalControlGap,
    RetrievalControlGapDetector,
    RetrievalControlPriorityWeights,
    V9_ALL_COLLAPSED_ANSWERABILITY_SHAPES,
    V9_ANSWERABILITY_COLLAPSE,
    V9_MINORITY_ANSWERABILITY_SHAPES,
    all_retrieval_control_cells,
    cell_for_case,
    collapse_answerability_shape,
    detailed_answerability_shapes_for,
    parse_retrieval_control_cell_id,
    retrieval_control_cell_counts,
)
from .llm_enrich import (
    ENRICHMENT_SYSTEM,
    EnrichmentResult,
    build_enrichment_prompt,
    case_needs_enrichment,
    cases_needing_enrichment,
    enrich_case_with_provider,
    merge_enrichment,
    parse_enrichment_response,
)
from .monitor import (
    CoverageAxis,
    by_class,
    by_difficulty,
    by_domain,
    by_pattern,
    format_coverage_report,
    report_for_vault,
    write_coverage_report,
)
from .modality import DEFAULT_MODALITY, MODALITIES, MODALITY_SET, set_modality, validate_modality
from .near_miss import (
    PATTERN_NEIGHBORS,
    NearMissOrchestrator,
    build_near_miss_prompt,
    neighbors_of,
)
from .orchestrator import (
    BatchReport,
    GenerationResult,
    Orchestrator,
    Outcome,
    parse_case_json,
)
from .prompts import (
    DIFFICULTY_HINTS,
    DOMAIN_HINTS,
    MODALITY_HINTS,
    PATTERN_GUIDANCE,
    SYSTEM_MESSAGE,
    GeneratorPrompt,
    build_prompt,
    build_prompt_for_cell,
    few_shot_for_cell,
)
from .providers import (
    BlindLabelPair,
    FileHandoffProvider,
    GenerateRequest,
    LmStudioProvider,
    LocalLlmProvider,
    Provider,
    ProviderError,
    ProviderHTTPError,
    ProviderTimeoutError,
    RoundRobinProvider,
    StubProvider,
    make_default_local,
    providers_from_env,
)
from .qa import (
    assign_query_grouped_splits,
    blind_label_manifest_rows,
    blind_label_queue_rows,
    cross_label_query_groups,
    duplicate_summary,
    exact_input_hash,
    exact_input_label_hash,
    query_duplicate_groups,
    rows_from_cases,
    split_assignment_rows,
    split_summary,
)
from .taxonomy import (
    PATTERN_DESCRIPTIONS,
    PATTERN_MIN_CONTEXTS,
    PATTERN_TO_CLASS,
    PRIMARY_DOMAINS,
    V8_GAP_PATTERNS,
    Cell,
    Difficulty,
    Domain,
    GovernanceClass,
    PatternCheckResult,
    TaxonomyPattern,
    all_cells,
    check_pattern_structure,
    governance_class_of,
    parse_cell_id,
    patterns_of,
)
from .v7_completion import (
    V7_COMPLETION_SYSTEM,
    V7CompletionResult,
    build_v7_completion_prompt,
    case_needs_v7_completion,
    cases_needing_v7_completion,
)
from .v7_completion import complete_case_with_provider as complete_v7_case_with_provider
from .v7_completion import (
    merge_v7_completion,
    parse_v7_completion_response,
)
from .vault import (
    CASES_FILE,
    INDEX_FILE,
    VAULT_KEY,
    CorruptVaultError,
    DuplicateCaseError,
    Provenance,
    Vault,
    VaultError,
    drop_vault_fields,
    new_batch_id,
)

__all__ = [
    # taxonomy
    "Cell",
    "Difficulty",
    "Domain",
    "GovernanceClass",
    "PATTERN_DESCRIPTIONS",
    "PATTERN_MIN_CONTEXTS",
    "PATTERN_TO_CLASS",
    "PRIMARY_DOMAINS",
    "V8_GAP_PATTERNS",
    "PatternCheckResult",
    "TaxonomyPattern",
    "all_cells",
    "check_pattern_structure",
    "governance_class_of",
    "parse_cell_id",
    "patterns_of",
    # modality
    "DEFAULT_MODALITY",
    "MODALITIES",
    "MODALITY_SET",
    "set_modality",
    "validate_modality",
    # vault
    "CASES_FILE",
    "INDEX_FILE",
    "VAULT_KEY",
    "CorruptVaultError",
    "DuplicateCaseError",
    "Provenance",
    "Vault",
    "VaultError",
    "drop_vault_fields",
    "new_batch_id",
    # checker
    "CheckIssue",
    "CheckResult",
    "Checker",
    "Severity",
    "case_dedup_hash",
    "hashes_from",
    # blind label
    "BLIND_LABEL_SYSTEM",
    "ParsedBlindLabel",
    "blind_label_assessment_rows",
    "blind_label_score_summary",
    "build_blind_label_prompt",
    "bucketed_assessment_rows",
    "case_ids_from_rows",
    "disagreement_rows",
    "label_queue_row",
    "markdown_score_report",
    "normalize_label",
    "parse_blind_label_response",
    "review_queue_rows",
    "sample_queue_rows",
    "second_pass_ledger_rows",
    # completeness
    "CompletenessIssue",
    "audit_case_completeness",
    "cases_needing_training_completion",
    "is_training_complete",
    "summarize_completeness",
    # evaluation fields
    "EVALUATION_COMPLETION_SYSTEM",
    "EvaluationIssue",
    "EvaluationPromotionResult",
    "audit_evaluation_fields",
    "build_canonical_evaluation",
    "build_evaluation_completion_prompt",
    "complete_evaluation_with_provider",
    "merge_evaluation_overlay",
    "needs_evaluation_enrichment",
    "parse_evaluation_completion_response",
    "promote_evaluation_fields",
    # gap detector
    "CellFilter",
    "CellTarget",
    "Gap",
    "GapDetector",
    "PriorityWeights",
    "rank_from_vault",
    # V9 retrieval-control gap detector
    "CollapsedAnswerabilityShape",
    "RetrievalControlCell",
    "RetrievalControlCellFilter",
    "RetrievalControlCellTarget",
    "RetrievalControlGap",
    "RetrievalControlGapDetector",
    "RetrievalControlPriorityWeights",
    "V9_ALL_COLLAPSED_ANSWERABILITY_SHAPES",
    "V9_ANSWERABILITY_COLLAPSE",
    "V9_MINORITY_ANSWERABILITY_SHAPES",
    "all_retrieval_control_cells",
    "cell_for_case",
    "collapse_answerability_shape",
    "detailed_answerability_shapes_for",
    "parse_retrieval_control_cell_id",
    "retrieval_control_cell_counts",
    # providers
    "BlindLabelPair",
    "FileHandoffProvider",
    "GenerateRequest",
    "LmStudioProvider",
    "LocalLlmProvider",
    "Provider",
    "ProviderError",
    "ProviderHTTPError",
    "ProviderTimeoutError",
    "RoundRobinProvider",
    "StubProvider",
    "make_default_local",
    "providers_from_env",
    # qa
    "assign_query_grouped_splits",
    "blind_label_manifest_rows",
    "blind_label_queue_rows",
    "cross_label_query_groups",
    "duplicate_summary",
    "exact_input_hash",
    "exact_input_label_hash",
    "query_duplicate_groups",
    "rows_from_cases",
    "split_assignment_rows",
    "split_summary",
    # prompts
    "DIFFICULTY_HINTS",
    "DOMAIN_HINTS",
    "MODALITY_HINTS",
    "PATTERN_GUIDANCE",
    "SYSTEM_MESSAGE",
    "GeneratorPrompt",
    "build_prompt",
    "build_prompt_for_cell",
    "few_shot_for_cell",
    # orchestrator
    "BatchReport",
    "GenerationResult",
    "Orchestrator",
    "Outcome",
    "parse_case_json",
    # monitor
    "CoverageAxis",
    "by_class",
    "by_difficulty",
    "by_domain",
    "by_pattern",
    "format_coverage_report",
    "report_for_vault",
    "write_coverage_report",
    # cost
    "CostTracker",
    "estimate_tokens",
    # near-miss
    "PATTERN_NEIGHBORS",
    "NearMissOrchestrator",
    "build_near_miss_prompt",
    "neighbors_of",
    # llm enrichment (Phase 0b)
    "ENRICHMENT_SYSTEM",
    "EnrichmentResult",
    "build_enrichment_prompt",
    "case_needs_enrichment",
    "cases_needing_enrichment",
    "enrich_case_with_provider",
    "merge_enrichment",
    "parse_enrichment_response",
    # v7 completion
    "V7_COMPLETION_SYSTEM",
    "V7CompletionResult",
    "build_v7_completion_prompt",
    "case_needs_v7_completion",
    "cases_needing_v7_completion",
    "complete_v7_case_with_provider",
    "merge_v7_completion",
    "parse_v7_completion_response",
]
