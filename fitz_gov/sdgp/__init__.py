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
    CheckIssue,
    CheckResult,
    Checker,
    Severity,
    case_dedup_hash,
    hashes_from,
)
from .gap_detector import (
    CellFilter,
    CellTarget,
    Gap,
    GapDetector,
    PriorityWeights,
    rank_from_vault,
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
from .taxonomy import (
    Cell,
    Difficulty,
    Domain,
    GovernanceClass,
    PATTERN_DESCRIPTIONS,
    PATTERN_MIN_CONTEXTS,
    PATTERN_TO_CLASS,
    PRIMARY_DOMAINS,
    PatternCheckResult,
    TaxonomyPattern,
    all_cells,
    check_pattern_structure,
    governance_class_of,
    parse_cell_id,
    patterns_of,
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
    "PatternCheckResult",
    "TaxonomyPattern",
    "all_cells",
    "check_pattern_structure",
    "governance_class_of",
    "parse_cell_id",
    "patterns_of",
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
    # gap detector
    "CellFilter",
    "CellTarget",
    "Gap",
    "GapDetector",
    "PriorityWeights",
    "rank_from_vault",
    # providers
    "BlindLabelPair",
    "FileHandoffProvider",
    "GenerateRequest",
    "LocalLlmProvider",
    "Provider",
    "ProviderError",
    "ProviderHTTPError",
    "ProviderTimeoutError",
    "RoundRobinProvider",
    "StubProvider",
    "make_default_local",
    "providers_from_env",
    # prompts
    "DIFFICULTY_HINTS",
    "DOMAIN_HINTS",
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
]
