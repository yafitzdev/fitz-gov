"""Generate a targeted code-modality candidate patch.

This patch is candidate-only. It writes SDGP V8-shaped code rows focused on the
coverage gaps surfaced by pyrrho's code-modality audit:

- syntax-matched code languages
- direct control-flow support
- missing-specific-field ABSTAIN rows
- wrong-symbol / wrong-version / missing-result ABSTAIN rows
- config/docs/test conflict DISPUTED rows

It does not merge rows into the active vault or publish anything.

Run from the fitz-gov repo root:
    python scripts/sdgp_generate_code_modality_patch.py
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from fitz_gov.sdgp.checker import Checker

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sdgp_generate_modality_candidate_packs as base  # noqa: E402

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


VERSION = "fitz-gov-modality-code-patch-0.1"
BUILD_TS = "2026-05-28T23:45:00Z"
PROVIDER = "codex"
PROVIDER_VERSION = "gpt-5-codex"
PROMPT_VERSION = "code-modality-hard-negative-patch-0.1"
BATCH_ID = "code_modality_patch_v1_20260528"
DEFAULT_OUT = Path("data/_workspaces/handoff/modality_code_patch_v1_20260528")
BATCH_SIZE = 60

DOMAINS = [
    "technology_computing",
    "technology_computing",
    "technology_computing",
    "economics_finance",
    "science_medicine",
]
DIFFICULTIES = ["easy", "medium", "hard"]
SERIALIZATIONS = ["code_excerpt", "review_packet", "diff_context"]


@dataclass(frozen=True)
class LanguageSpec:
    name: str
    ext: str
    fence: str


LANGUAGES = [
    LanguageSpec("python", "py", "python"),
    LanguageSpec("typescript", "ts", "typescript"),
    LanguageSpec("go", "go", "go"),
    LanguageSpec("rust", "rs", "rust"),
    LanguageSpec("java_kotlin", "kt", "kotlin"),
    LanguageSpec("yaml", "yaml", "yaml"),
    LanguageSpec("json", "json", "json"),
    LanguageSpec("sql", "sql", "sql"),
    LanguageSpec("shell_ci", "sh", "bash"),
]

CODE_LANGS = [LANGUAGES[0], LANGUAGES[1], LANGUAGES[2], LANGUAGES[3], LANGUAGES[4]]
CONFIG_LANGS = [LANGUAGES[5], LANGUAGES[6], LANGUAGES[7], LANGUAGES[8]]
FEATURES = [
    "auth",
    "billing",
    "checkout",
    "invoices",
    "payments",
    "search",
    "reports",
    "audit",
    "orders",
    "refunds",
    "gateway",
    "scheduler",
    "notifications",
    "exports",
    "imports",
    "sessions",
]


@dataclass(frozen=True)
class Source:
    path: str
    language: str
    content: str
    summary: str
    authority_signal: str = "source_code"
    authority_score: float = 0.92


@dataclass(frozen=True)
class PatchSpec:
    mechanism: str
    pattern: str
    count: int
    builder: Callable[[int, str, str, str], dict[str, Any]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def feature(seq: int) -> str:
    root = FEATURES[seq % len(FEATURES)]
    suffix = seq // len(FEATURES)
    return root if suffix == 0 else f"{root}_{suffix}"


def code_language(seq: int) -> LanguageSpec:
    return CODE_LANGS[seq % len(CODE_LANGS)]


def config_language(seq: int) -> LanguageSpec:
    return CONFIG_LANGS[seq % len(CONFIG_LANGS)]


def render_source(source: Source, serialization: str) -> str:
    content = source.content.strip("\n")
    if serialization == "code_excerpt":
        return (
            f"Retrieved file: {source.path}\n"
            f"Language: {source.language}\n"
            f"```{source.language}\n{content}\n```\n"
            f"Note: {source.summary}"
        )
    if serialization == "review_packet":
        numbered = "\n".join(
            f"{idx:03d}: {line}" for idx, line in enumerate(content.splitlines(), start=1)
        )
        return (
            "Code review evidence packet\n"
            f"path={source.path}\n"
            f"language={source.language}\n"
            f"note={source.summary}\n"
            "numbered_excerpt:\n"
            f"{numbered}"
        )
    if serialization == "diff_context":
        diff = "\n".join(f"+ {line}" if line else "+" for line in content.splitlines())
        return (
            "Retrieved diff context\n"
            f"+++ b/{source.path}\n"
            "@@ relevant excerpt @@\n"
            f"{diff}\n"
            f"review_note={source.summary}"
        )
    raise ValueError(f"unknown serialization: {serialization}")


def contexts(sources: list[Source], serialization: str) -> list[dict[str, Any]]:
    return [
        base._make_context(
            idx,
            render_source(source, serialization),
            authority_score=source.authority_score,
            authority_signal=source.authority_signal,
            summary=source.summary,
            relevance=0.9,
            boundary=0.86,
            anchor="code modality patch",
        )
        for idx, source in enumerate(sources, start=1)
    ]


def finalize_row(
    row: dict[str, Any],
    *,
    case_id: str,
    serialization: str,
) -> dict[str, Any]:
    row["id"] = case_id
    row["version"] = VERSION
    row["meta"]["serialization"] = serialization
    row["_vault"] = {
        "added_at": BUILD_TS,
        "provider": PROVIDER,
        "provider_version": PROVIDER_VERSION,
        "prompt_version": PROMPT_VERSION,
        "batch_id": BATCH_ID,
        "last_modified_at": BUILD_TS,
        "revisions": 1,
    }
    return row


def row_base(
    *,
    pattern: str,
    domain: str,
    difficulty: str,
    query: str,
    sources: list[Source],
    required_elements: list[str],
    forbidden_claims: list[str],
    near_miss_reason: str,
    mechanism: str,
    serialization: str,
    gold_answer: str | None = None,
    grounding_attributions: list[str] | None = None,
    direct: bool = False,
) -> dict[str, Any]:
    return base.build_row(
        modality="code",
        case_id="",
        pattern=pattern,
        domain=domain,
        difficulty=difficulty,
        query=query,
        query_rewritten=None,
        contexts=contexts(sources, serialization),
        required_elements=required_elements,
        forbidden_claims=forbidden_claims,
        forbidden_elements=[],
        near_miss_reason=near_miss_reason,
        mechanism=mechanism,
        serialization=serialization,
        gold_answer=gold_answer,
        grounding_attributions=grounding_attributions,
        direct=direct,
    )


def control_flow_source(lang: LanguageSpec, name: str, variant: int) -> tuple[str, str, str]:
    if variant == 0:
        query = f"Does `{name}_create_charge` persist the idempotency record before charging?"
        if lang.name == "python":
            code = f"""
def {name}_create_charge(account_id: str, key: str, cents: int) -> str:
    existing = ChargeRequest.get_by_key(key)
    if existing:
        return existing.charge_id
    request = ChargeRequest.create(account_id=account_id, idempotency_key=key, status="pending")
    request.charge_id = gateway.charge(account_id=account_id, cents=cents)
    request.save()
    return request.charge_id
"""
        elif lang.name == "typescript":
            code = f"""
export async function {name}CreateCharge(accountId: string, key: string, cents: number) {{
  const existing = await ChargeRequest.findByKey(key);
  if (existing) return existing.chargeId;
  const request = await ChargeRequest.create({{ accountId, idempotencyKey: key, status: "pending" }});
  request.chargeId = await gateway.charge(accountId, cents);
  await request.save();
  return request.chargeId;
}}
"""
        elif lang.name == "go":
            code = f"""
func {name}CreateCharge(accountID string, key string, cents int) (string, error) {{
    existing := ChargeRequestByKey(key)
    if existing != nil {{
        return existing.ChargeID, nil
    }}
    request := CreateChargeRequest(accountID, key, "pending")
    request.ChargeID = gateway.Charge(accountID, cents)
    request.Save()
    return request.ChargeID, nil
}}
"""
        elif lang.name == "rust":
            code = f"""
pub fn {name}_create_charge(account_id: &str, key: &str, cents: u32) -> String {{
    if let Some(existing) = charge_request_by_key(key) {{
        return existing.charge_id;
    }}
    let mut request = create_charge_request(account_id, key, "pending");
    request.charge_id = gateway_charge(account_id, cents);
    request.save();
    request.charge_id
}}
"""
        else:
            code = f"""
fun {name}CreateCharge(accountId: String, key: String, cents: Int): String {{
    val existing = ChargeRequest.findByKey(key)
    if (existing != null) return existing.chargeId
    val request = ChargeRequest.create(accountId, key, "pending")
    request.chargeId = gateway.charge(accountId, cents)
    request.save()
    return request.chargeId
}}
"""
        gold = "Yes. The idempotency request is created before the gateway charge call."
        required = "idempotency"
    elif variant == 1:
        query = f"Does `{name}_refund_order` reject non-positive refund amounts before calling the gateway?"
        if lang.name == "python":
            code = f"""
def {name}_refund_order(order: Order, cents: int) -> Refund:
    if cents <= 0:
        raise ValueError("refund amount must be positive")
    gateway.refund(order.payment_id, cents)
    return Refund.create(order_id=order.id, cents=cents)
"""
        elif lang.name == "typescript":
            code = f"""
export async function {name}RefundOrder(order: Order, cents: number): Promise<Refund> {{
  if (cents <= 0) throw new Error("refund amount must be positive");
  await gateway.refund(order.paymentId, cents);
  return Refund.create({{ orderId: order.id, cents }});
}}
"""
        elif lang.name == "go":
            code = f"""
func {name}RefundOrder(order Order, cents int) (Refund, error) {{
    if cents <= 0 {{
        return Refund{{}}, errors.New("refund amount must be positive")
    }}
    gateway.Refund(order.PaymentID, cents)
    return CreateRefund(order.ID, cents), nil
}}
"""
        elif lang.name == "rust":
            code = f"""
pub fn {name}_refund_order(order: Order, cents: i32) -> Result<Refund, Error> {{
    if cents <= 0 {{
        return Err(Error::new("refund amount must be positive"));
    }}
    gateway_refund(order.payment_id, cents);
    Ok(create_refund(order.id, cents))
}}
"""
        else:
            code = f"""
fun {name}RefundOrder(order: Order, cents: Int): Refund {{
    require(cents > 0) {{ "refund amount must be positive" }}
    gateway.refund(order.paymentId, cents)
    return Refund.create(order.id, cents)
}}
"""
        gold = "Yes. The non-positive amount guard runs before the gateway refund call."
        required = "before calling the gateway"
    else:
        query = f"Does `{name}_publish_event` write the audit row before publishing to the bus?"
        if lang.name == "python":
            code = f"""
def {name}_publish_event(event: Event) -> None:
    AuditLog.write(event_id=event.id, action="publish_started")
    event_bus.publish(event)
    AuditLog.write(event_id=event.id, action="publish_completed")
"""
        elif lang.name == "typescript":
            code = f"""
export async function {name}PublishEvent(event: Event): Promise<void> {{
  await AuditLog.write({{ eventId: event.id, action: "publish_started" }});
  await eventBus.publish(event);
  await AuditLog.write({{ eventId: event.id, action: "publish_completed" }});
}}
"""
        elif lang.name == "go":
            code = f"""
func {name}PublishEvent(event Event) {{
    AuditLogWrite(event.ID, "publish_started")
    eventBus.Publish(event)
    AuditLogWrite(event.ID, "publish_completed")
}}
"""
        elif lang.name == "rust":
            code = f"""
pub fn {name}_publish_event(event: Event) {{
    audit_log_write(event.id, "publish_started");
    event_bus_publish(event);
    audit_log_write(event.id, "publish_completed");
}}
"""
        else:
            code = f"""
fun {name}PublishEvent(event: Event) {{
    auditLog.write(event.id, "publish_started")
    eventBus.publish(event)
    auditLog.write(event.id, "publish_completed")
}}
"""
        gold = "Yes. The audit row is written before the event bus publish call."
        required = "publish_started"
    return query, code.strip(), gold.replace("Yes.", f"Yes. `{name}` shows"), required


def build_control_flow(seq: int, domain: str, difficulty: str, serialization: str) -> dict[str, Any]:
    lang = code_language(seq)
    name = feature(seq)
    query, code, gold, required = control_flow_source(lang, name, seq % 3)
    source = Source(
        path=f"services/{name}/workflow.{lang.ext}",
        language=lang.fence,
        content=code,
        summary="The control-flow order in the retrieved function directly resolves the query.",
    )
    return row_base(
        pattern="direct_answer",
        domain=domain,
        difficulty=difficulty,
        query=query,
        sources=[source],
        required_elements=[required],
        forbidden_claims=["the external side effect happens before the guard or persisted record"],
        near_miss_reason="The answer depends on operation order, not merely symbol presence.",
        mechanism="control_flow_support",
        serialization=serialization,
        gold_answer=gold,
        direct=True,
    )


def build_decorator_guard(seq: int, domain: str, difficulty: str, serialization: str) -> dict[str, Any]:
    lang = code_language(seq)
    name = feature(seq)
    route = f"/{name}/admin/rebuild"
    if lang.name == "python":
        code = f"""
@router.post("{route}")
@require_role("admin")
def {name}_rebuild_index(request: Request) -> Response:
    enqueue_job("{name}.rebuild", requested_by=request.user.id)
    return Response(status_code=202)
"""
    elif lang.name == "typescript":
        code = f"""
router.post("{route}", requireRole("admin"), async (req, res) => {{
  await enqueueJob("{name}.rebuild", {{ requestedBy: req.user.id }});
  res.status(202).send();
}});
"""
    elif lang.name == "go":
        code = f"""
func Register{name.title()}Routes(router Router) {{
    router.POST("{route}", RequireRole("admin"), {name}RebuildIndex)
}}
"""
    elif lang.name == "rust":
        code = f"""
pub fn register_{name}_routes(router: &mut Router) {{
    router.post("{route}", require_role("admin"), {name}_rebuild_index);
}}
"""
    else:
        code = f"""
post("{route}", requireRole("admin")) {{
    enqueueJob("{name}.rebuild", requestedBy = call.user.id)
    call.respond(HttpStatusCode.Accepted)
}}
"""
    source = Source(
        path=f"web/{name}/admin_routes.{lang.ext}",
        language=lang.fence,
        content=code.strip(),
        summary="The route registration includes an explicit admin role guard.",
    )
    return row_base(
        pattern="single_authoritative",
        domain=domain,
        difficulty=difficulty,
        query=f"Is `{route}` restricted to admin users?",
        sources=[source],
        required_elements=["admin"],
        forbidden_claims=[f"{route} is public"],
        near_miss_reason="The route path alone is insufficient; the guard attached to the handler answers it.",
        mechanism="decorator_guard_support",
        serialization=serialization,
        gold_answer=f"Yes. `{route}` is registered with an explicit admin role guard.",
        direct=True,
    )


def build_transaction_order(seq: int, domain: str, difficulty: str, serialization: str) -> dict[str, Any]:
    lang = code_language(seq)
    name = feature(seq)
    if lang.name == "python":
        code = f"""
def {name}_close_invoice(invoice: Invoice) -> None:
    with db.transaction():
        invoice.status = "closed"
        invoice.closed_at = clock.now()
        invoice.save()
        ledger.write_invoice_closed(invoice.id)
    notifier.send_invoice_closed(invoice.id)
"""
    elif lang.name == "typescript":
        code = f"""
export async function {name}CloseInvoice(invoice: Invoice): Promise<void> {{
  await db.transaction(async () => {{
    invoice.status = "closed";
    invoice.closedAt = clock.now();
    await invoice.save();
    await ledger.writeInvoiceClosed(invoice.id);
  }});
  await notifier.sendInvoiceClosed(invoice.id);
}}
"""
    elif lang.name == "go":
        code = f"""
func {name}CloseInvoice(invoice Invoice) {{
    db.Transaction(func(tx Tx) {{
        invoice.Status = "closed"
        invoice.ClosedAt = clock.Now()
        tx.Save(invoice)
        ledger.WriteInvoiceClosed(tx, invoice.ID)
    }})
    notifier.SendInvoiceClosed(invoice.ID)
}}
"""
    elif lang.name == "rust":
        code = f"""
pub fn {name}_close_invoice(mut invoice: Invoice) {{
    db_transaction(|tx| {{
        invoice.status = "closed";
        invoice.closed_at = clock_now();
        tx.save(&invoice);
        ledger_write_invoice_closed(tx, invoice.id);
    }});
    notifier_send_invoice_closed(invoice.id);
}}
"""
    else:
        code = f"""
fun {name}CloseInvoice(invoice: Invoice) {{
    db.transaction {{
        invoice.status = "closed"
        invoice.closedAt = clock.now()
        invoice.save()
        ledger.writeInvoiceClosed(invoice.id)
    }}
    notifier.sendInvoiceClosed(invoice.id)
}}
"""
    source = Source(
        path=f"billing/{name}/invoice_lifecycle.{lang.ext}",
        language=lang.fence,
        content=code.strip(),
        summary="The ledger write occurs inside the transaction before notification.",
    )
    return row_base(
        pattern="direct_answer",
        domain=domain,
        difficulty=difficulty,
        query=f"Does `{name}_close_invoice` write the ledger entry before notifying users?",
        sources=[source],
        required_elements=["ledger", "notifier"],
        forbidden_claims=["the user notification happens before the ledger write"],
        near_miss_reason="The answer depends on comparing the transaction block with the later notifier call.",
        mechanism="transaction_order_support",
        serialization=serialization,
        gold_answer=f"Yes. `{name}_close_invoice` writes the ledger entry before the notifier call.",
        direct=True,
    )


def build_missing_specific_field(
    seq: int, domain: str, difficulty: str, serialization: str
) -> dict[str, Any]:
    lang = code_language(seq)
    name = feature(seq)
    if seq % 3 == 0:
        query = f"Which audit event name does `{name}_refund_order` write?"
        if lang.name == "python":
            code = f"""
def {name}_refund_order(order_id: str, cents: int) -> Refund:
    order = Order.get(order_id)
    gateway.refund(payment_id=order.payment_id, amount_cents=cents)
    return Refund.create(order_id=order_id, amount_cents=cents)
"""
        elif lang.name == "typescript":
            code = f"""
export async function {name}RefundOrder(orderId: string, cents: number): Promise<Refund> {{
  const order = await Order.get(orderId);
  await gateway.refund(order.paymentId, cents);
  return Refund.create({{ orderId, cents }});
}}
"""
        else:
            code = f"""
func {name}RefundOrder(orderID string, cents int) Refund {{
    order := OrderGet(orderID)
    gateway.Refund(order.PaymentID, cents)
    return CreateRefund(orderID, cents)
}}
"""
        missing = "audit event name"
    elif seq % 3 == 1:
        cfg = config_language(seq)
        query = f"What `{name.upper()}_PUBLIC_KEY_ID` value is configured for production?"
        if cfg.name == "yaml":
            code = f"""
production:
  {name.upper()}_REGION: us-east-1
  {name.upper()}_TIMEOUT_SECONDS: 30
"""
        elif cfg.name == "json":
            code = f"""
{{
  "production": {{
    "{name.upper()}_REGION": "us-east-1",
    "{name.upper()}_TIMEOUT_SECONDS": 30
  }}
}}
"""
        elif cfg.name == "sql":
            code = f"""
SELECT key, value FROM runtime_config
WHERE service = '{name}' AND environment = 'production'
AND key IN ('{name.upper()}_REGION', '{name.upper()}_TIMEOUT_SECONDS');
"""
        else:
            code = f"""
export {name.upper()}_REGION=us-east-1
export {name.upper()}_TIMEOUT_SECONDS=30
"""
        lang = cfg
        missing = f"{name.upper()}_PUBLIC_KEY_ID"
    else:
        query = f"Which database column stores `{name}` customer consent version?"
        code = f"""
CREATE TABLE {name}_customer_consent (
    customer_id TEXT NOT NULL,
    accepted_at TIMESTAMP NOT NULL,
    source_ip TEXT NOT NULL
);
"""
        lang = LanguageSpec("sql", "sql", "sql")
        missing = "consent version column"
    source = Source(
        path=f"services/{name}/evidence.{lang.ext}",
        language=lang.fence,
        content=code.strip(),
        summary=f"The retrieved evidence is relevant but does not contain the requested {missing}.",
    )
    return row_base(
        pattern="evidence_absent",
        domain=domain,
        difficulty=difficulty,
        query=query,
        sources=[source],
        required_elements=[],
        forbidden_claims=[f"the retrieved evidence contains the requested {missing}"],
        near_miss_reason="Relevant code/config was retrieved, but the exact requested field is absent.",
        mechanism="missing_specific_field",
        serialization=serialization,
    )


def build_wrong_symbol(seq: int, domain: str, difficulty: str, serialization: str) -> dict[str, Any]:
    lang = code_language(seq)
    name = feature(seq)
    if lang.name == "python":
        code = f"""
def {name}_send_welcome_email(user: User) -> None:
    msg = EmailMessage(to=user.email, template="welcome")
    msg.attach("welcome_guide.pdf", build_welcome_pdf(user))
    mailer.send(msg)
"""
    elif lang.name == "typescript":
        code = f"""
export async function {name}SendWelcomeEmail(user: User): Promise<void> {{
  const msg = new EmailMessage(user.email, "welcome");
  msg.attach("welcome_guide.pdf", await buildWelcomePdf(user));
  await mailer.send(msg);
}}
"""
    else:
        code = f"""
func {name}SendWelcomeEmail(user User) {{
    msg := NewEmailMessage(user.Email, "welcome")
    msg.Attach("welcome_guide.pdf", BuildWelcomePDF(user))
    mailer.Send(msg)
}}
"""
    source = Source(
        path=f"notifications/{name}/email.{lang.ext}",
        language=lang.fence,
        content=code.strip(),
        summary=(
            "Search retrieved only the nearby welcome-email symbol; no send_invoice_email "
            "implementation is present."
        ),
    )
    return row_base(
        pattern="wrong_entity",
        domain=domain,
        difficulty=difficulty,
        query=f"What PDF attachment name does `{name}_send_invoice_email` use?",
        sources=[source],
        required_elements=[],
        forbidden_claims=[
            f"`{name}_send_invoice_email` uses welcome_guide.pdf",
            "the retrieved symbol is the requested invoice-email implementation",
        ],
        near_miss_reason=(
            "A nearby email helper was retrieved, but the requested invoice-email symbol is absent."
        ),
        mechanism="wrong_symbol",
        serialization=serialization,
    )


def build_wrong_api_version(seq: int, domain: str, difficulty: str, serialization: str) -> dict[str, Any]:
    lang = code_language(seq)
    name = feature(seq)
    if lang.name == "python":
        code = f"""
# api/v1/{name}.py
def parse_amount(raw: str) -> int:
    cents = int(Decimal(raw) * 100)
    if cents < 0:
        raise ValueError("amount must be positive")
    return cents
"""
    elif lang.name == "typescript":
        code = f"""
// api/v1/{name}.ts
export function parseAmount(raw: string): number {{
  const cents = Number(raw) * 100;
  if (cents < 0) throw new Error("amount must be positive");
  return cents;
}}
"""
    else:
        code = f"""
// api/v1/{name}.{lang.ext}
func ParseAmount(raw string) int {{
    cents := decimalToCents(raw)
    if cents < 0 {{ panic("amount must be positive") }}
    return cents
}}
"""
    source = Source(
        path=f"api/v1/{name}.{lang.ext}",
        language=lang.fence,
        content=code.strip(),
        summary="The retrieved implementation is explicitly API v1, while the query asks API v2.",
    )
    return row_base(
        pattern="version_build_mismatch",
        domain=domain,
        difficulty=difficulty,
        query=f"In API v2, does `{name}_parse_amount` reject negative values?",
        sources=[source],
        required_elements=[],
        forbidden_claims=["this API v1 implementation is evidence for API v2 behavior"],
        near_miss_reason="The behavior may match, but the retrieved artifact is the wrong API version.",
        mechanism="wrong_api_version",
        serialization=serialization,
    )


def build_test_without_run(seq: int, domain: str, difficulty: str, serialization: str) -> dict[str, Any]:
    lang = code_language(seq)
    name = feature(seq)
    if lang.name == "python":
        code = f"""
def test_{name}_migration_adds_invoice_index(migrator):
    migrator.apply("202605_add_invoice_index")
    indexes = migrator.inspect_indexes("invoice")
    assert "idx_invoice_account_created_at" in indexes
"""
    elif lang.name == "typescript":
        code = f"""
test("{name} migration adds invoice index", async () => {{
  await migrator.apply("202605_add_invoice_index");
  const indexes = await migrator.inspectIndexes("invoice");
  expect(indexes).toContain("idx_invoice_account_created_at");
}});
"""
    else:
        code = f"""
func Test{name.title()}MigrationAddsInvoiceIndex(t *testing.T) {{
    migrator.Apply("202605_add_invoice_index")
    indexes := migrator.InspectIndexes("invoice")
    assert.Contains(t, indexes, "idx_invoice_account_created_at")
}}
"""
    source = Source(
        path=f"tests/migrations/{name}_invoice_index_test.{lang.ext}",
        language=lang.fence,
        content=code.strip(),
        summary="Only the test definition is retrieved; no run log or pass/fail result is present.",
        authority_signal="test_definition",
        authority_score=0.82,
    )
    return row_base(
        pattern="missing_execution_result",
        domain=domain,
        difficulty=difficulty,
        query=f"Did the migration test pass for `{name}_202605_add_invoice_index`?",
        sources=[source],
        required_elements=[],
        forbidden_claims=["the retrieved test definition proves the test passed"],
        near_miss_reason="A test definition is setup evidence, not an execution result.",
        mechanism="test_definition_without_run",
        serialization=serialization,
    )


def build_config_runtime_conflict(
    seq: int, domain: str, difficulty: str, serialization: str
) -> dict[str, Any]:
    name = feature(seq)
    observed_at = f"2026-05-28T{(seq % 8) + 9:02d}:00:00Z"
    control_plane = {
        "service": name,
        "environment": "production",
        "observed_at": observed_at,
        "source": "control_plane_status_api",
        "effective_enabled": True,
        "status": "enabled",
    }
    edge_probe = (
        f"service={name}\n"
        "environment=production\n"
        f"observed_at={observed_at}\n"
        "source=edge_probe_runtime_check\n"
        "effective_enabled=false\n"
        "status=disabled\n"
    )
    reconciliation = (
        f"Runtime status reconciliation note for {name}\n"
        f"environment: production\n"
        f"observed_at: {observed_at}\n"
        "control_plane_status_api reports effective_enabled=true\n"
        "edge_probe_runtime_check reports effective_enabled=false\n"
        "no precedence rule or resolved incident is recorded for this timestamp\n"
    )
    sources = [
        Source(
            path=f"runtime/status/{name}_control_plane.json",
            language="json",
            content=json.dumps(control_plane, indent=2),
            summary="Production control-plane status reports the feature effectively enabled.",
            authority_signal="runtime_status",
            authority_score=0.94,
        ),
        Source(
            path=f"runtime/status/{name}_edge_probe.log",
            language="text",
            content=edge_probe,
            summary="Production edge probe reports the feature effectively disabled at the same timestamp.",
            authority_signal="runtime_status",
            authority_score=0.94,
        ),
        Source(
            path=f"runtime/status/{name}_reconciliation.txt",
            language="text",
            content=reconciliation,
            summary="Reconciliation note records the two incompatible production status readings as unresolved.",
            authority_signal="runtime_status_review",
            authority_score=0.9,
        ),
    ]
    return row_base(
        pattern="authority_status_conflict",
        domain=domain,
        difficulty=difficulty,
        query=f"Is the `{name}` feature effectively enabled in production at {observed_at}?",
        sources=sources,
        required_elements=["effective_enabled=true", "effective_enabled=false", "unresolved"],
        forbidden_claims=["either runtime status source alone settles the effective production state"],
        near_miss_reason=(
            "Two same-environment production runtime status sources disagree at the same timestamp, "
            "and no precedence rule resolves the conflict."
        ),
        mechanism="config_runtime_guard_conflict",
        serialization=serialization,
    )


def build_docs_code_conflict(seq: int, domain: str, difficulty: str, serialization: str) -> dict[str, Any]:
    name = feature(seq)
    code = f"""
def {name}_digest_reset_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
"""
    docs = f"""
# {name} security

Password reset tokens are never stored in plaintext. The reset-token digest is
computed with SHA-512 before the value is written to the database.
"""
    sources = [
        Source(
            path=f"security/{name}/reset_tokens.py",
            language="python",
            content=code.strip(),
            summary="Implementation hashes reset tokens with SHA-256.",
            authority_signal="source_code",
            authority_score=0.95,
        ),
        Source(
            path=f"docs/{name}/security.md",
            language="markdown",
            content=docs.strip(),
            summary="Documentation says reset tokens use SHA-512.",
            authority_signal="documentation",
            authority_score=0.82,
        ),
    ]
    return row_base(
        pattern="factual_contradiction",
        domain=domain,
        difficulty=difficulty,
        query=f"Which algorithm hashes `{name}` password reset tokens?",
        sources=sources,
        required_elements=["SHA-256", "SHA-512"],
        forbidden_claims=["there is no conflict between docs and implementation"],
        near_miss_reason="The code and documentation name different hashing algorithms.",
        mechanism="docs_code_conflict",
        serialization=serialization,
    )


def build_test_impl_conflict(seq: int, domain: str, difficulty: str, serialization: str) -> dict[str, Any]:
    name = feature(seq)
    impl = f"""
def {name}_normalize_status(raw: str) -> str:
    return raw.strip().lower()
"""
    test = f"""
def test_{name}_normalize_status_uppercases():
    assert {name}_normalize_status(" paid ") == "PAID"
"""
    sources = [
        Source(
            path=f"services/{name}/status.py",
            language="python",
            content=impl.strip(),
            summary="Implementation lowercases the status.",
            authority_signal="source_code",
            authority_score=0.94,
        ),
        Source(
            path=f"tests/{name}/test_status.py",
            language="python",
            content=test.strip(),
            summary="Test expects an uppercase status.",
            authority_signal="test_suite",
            authority_score=0.9,
        ),
    ]
    return row_base(
        pattern="verdict_conflict",
        domain=domain,
        difficulty=difficulty,
        query=f"Does `{name}_normalize_status` return uppercase status strings?",
        sources=sources,
        required_elements=["lower", "upper"],
        forbidden_claims=["the test and implementation agree"],
        near_miss_reason="The implementation and test encode incompatible expected behavior.",
        mechanism="test_impl_conflict",
        serialization=serialization,
    )


SPECS = [
    PatchSpec("control_flow_support", "direct_answer", 80, build_control_flow),
    PatchSpec("decorator_guard_support", "single_authoritative", 80, build_decorator_guard),
    PatchSpec("transaction_order_support", "direct_answer", 80, build_transaction_order),
    PatchSpec("missing_specific_field", "evidence_absent", 60, build_missing_specific_field),
    PatchSpec("wrong_symbol", "wrong_entity", 60, build_wrong_symbol),
    PatchSpec("wrong_api_version", "version_build_mismatch", 60, build_wrong_api_version),
    PatchSpec(
        "test_definition_without_run",
        "missing_execution_result",
        60,
        build_test_without_run,
    ),
    PatchSpec(
        "config_runtime_guard_conflict",
        "authority_status_conflict",
        80,
        build_config_runtime_conflict,
    ),
    PatchSpec("docs_code_conflict", "factual_contradiction", 80, build_docs_code_conflict),
    PatchSpec("test_impl_conflict", "verdict_conflict", 80, build_test_impl_conflict),
]


def build_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in SPECS:
        for seq in range(spec.count):
            global_idx = len(rows)
            row = spec.builder(
                seq,
                DOMAINS[global_idx % len(DOMAINS)],
                DIFFICULTIES[global_idx % len(DIFFICULTIES)],
                SERIALIZATIONS[global_idx % len(SERIALIZATIONS)],
            )
            row = finalize_row(
                row,
                case_id=f"sdgp_v8_modality_code_patch1_{global_idx:05d}",
                serialization=SERIALIZATIONS[global_idx % len(SERIALIZATIONS)],
            )
            rows.append(row)
    return rows


def load_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    ids: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            if raw.strip():
                ids.add(json.loads(raw)["id"])
    return ids


def validate_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    checker = Checker(require_training_schema=True)
    errors: list[str] = []
    seen: set[str] = set()
    existing_ids = set()
    existing_ids |= load_ids(Path("data/fitz-gov/cases.jsonl"))
    existing_ids |= load_ids(Path("data/_workspaces/handoff/modality_code_v1_20260527/cases.jsonl"))
    existing_ids |= load_ids(Path("data/_workspaces/handoff/modality_structured_v1_20260527/cases.jsonl"))

    for row in rows:
        row_id = row["id"]
        if row_id in seen:
            errors.append(f"{row_id}: duplicate ID within patch")
        seen.add(row_id)
        if row_id in existing_ids:
            errors.append(f"{row_id}: ID collides with existing/candidate row")
        if row.get("meta", {}).get("modality") != "code":
            errors.append(f"{row_id}: meta.modality is not code")
        if row.get("meta", {}).get("dataset_version") != "v8":
            errors.append(f"{row_id}: meta.dataset_version is not v8")
        result = checker.check(row)
        if not result.passed:
            for issue in result.errors:
                errors.append(f"{row_id}: checker.{issue.rule}: {issue.message}")

    return {
        "ok": not errors,
        "rows": len(rows),
        "errors": errors,
        "label_counts": dict(Counter(row["governance"]["classification"] for row in rows)),
        "mechanism_counts": dict(Counter(row["meta"]["mechanism"] for row in rows)),
    }


def coverage_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counters: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        counters["by_label"][row["governance"]["classification"]] += 1
        counters["by_pattern"][row["taxonomy"]["pattern"]] += 1
        counters["by_domain"][row["routing"]["expert_fired"]] += 1
        counters["by_difficulty"][row["meta"]["difficulty"]] += 1
        counters["by_mechanism"][row["meta"]["mechanism"]] += 1
        counters["by_serialization"][row["meta"]["serialization"]] += 1
    return {"total_rows": len(rows), **{key: dict(value) for key, value in counters.items()}}


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_batches(out_dir: Path, rows: list[dict[str, Any]]) -> list[str]:
    batch_dir = out_dir / "batches"
    batch_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for idx in range(0, len(rows), BATCH_SIZE):
        batch = rows[idx : idx + BATCH_SIZE]
        path = batch_dir / f"batch_{idx // BATCH_SIZE + 1:04d}.jsonl"
        write_jsonl(path, batch)
        written.append(str(path.relative_to(out_dir).as_posix()))
    return written


def write_readme(out_dir: Path, coverage: dict[str, Any], validation: dict[str, Any]) -> None:
    lines = [
        "# Code Modality Patch v1 - 2026-05-28",
        "",
        "Candidate-only SDGP V8 rows for code evidence. This patch targets the hard",
        "code-modality gaps surfaced by pyrrho. It is not merged into the active vault",
        "and is not published to Hugging Face.",
        "",
        "## Status",
        "",
        "| Item | Value |",
        "|---|---:|",
        f"| Total rows | {coverage['total_rows']} |",
        f"| TRUSTWORTHY | {coverage['by_label'].get('TRUSTWORTHY', 0)} |",
        f"| ABSTAIN | {coverage['by_label'].get('ABSTAIN', 0)} |",
        f"| DISPUTED | {coverage['by_label'].get('DISPUTED', 0)} |",
        f"| Structural validation errors | {len(validation['errors'])} |",
        "",
        "## Mechanisms",
        "",
        "| Mechanism | Rows |",
        "|---|---:|",
    ]
    for name, count in sorted(coverage["by_mechanism"].items()):
        lines.append(f"| `{name}` | {count} |")
    lines.extend(
        [
            "",
            "## Files",
            "",
            "| Path | Purpose |",
            "|---|---|",
            "| `cases.jsonl` | All candidate rows |",
            "| `manifest.json` | Pack manifest |",
            "| `coverage_report.json` | Label/pattern/domain/mechanism coverage |",
            "| `validation_report.json` | Structural checker result |",
            "| `batches/` | 60-row shards for QA workflows |",
        ]
    )
    (out_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_workspace(out_dir: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(out_dir / "cases.jsonl", rows)
    batches = write_batches(out_dir, rows)
    coverage = coverage_report(rows)
    validation = validate_rows(rows)
    manifest = {
        "name": "fitz-gov-modality-code-patch-v1",
        "version": VERSION,
        "modality": "code",
        "dataset_version": "v8",
        "row_shape": "sdgp_v8",
        "rows": len(rows),
        "label_counts": coverage["by_label"],
        "mechanism_counts": coverage["by_mechanism"],
        "batches": batches,
        "description": (
            "Targeted candidate-only code evidence patch for control-flow, "
            "missing-field, wrong-symbol/version, missing-result, and conflict boundaries."
        ),
        "build_ts": BUILD_TS,
        "provider": PROVIDER,
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out_dir / "coverage_report.json").write_text(
        json.dumps(coverage, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out_dir / "validation_report.json").write_text(
        json.dumps(validation, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_readme(out_dir, coverage, validation)
    return validation


def main() -> int:
    args = parse_args()
    rows = build_rows()
    validation = write_workspace(args.out_dir, rows)

    print("=== Code modality patch ===")
    print(f"Rows       : {len(rows)}")
    print(f"Output     : {args.out_dir}")
    print(f"Labels     : {validation['label_counts']}")
    print(f"Mechanisms : {validation['mechanism_counts']}")
    print(f"Valid      : {validation['ok']} ({len(validation['errors'])} errors)")
    if validation["errors"]:
        for error in validation["errors"][:20]:
            print(f"  - {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
