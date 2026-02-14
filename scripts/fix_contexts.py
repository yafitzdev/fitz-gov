#!/usr/bin/env python3
"""
Fix two data issues in the fitz-gov benchmark:
1. Add decoy contexts to 14 empty-context abstention cases
2. Populate context_sources for all dispute cases missing them
"""

import json
import os
from pathlib import Path

# Resolve paths relative to repo root
REPO_ROOT = Path(__file__).resolve().parent.parent
ABSTENTION_PATH = REPO_ROOT / "data" / "tier1_core" / "abstention.json"
TIER1_DISPUTE_PATH = REPO_ROOT / "data" / "tier1_core" / "dispute.json"
TIER0_DISPUTE_PATH = REPO_ROOT / "data" / "tier0_sanity" / "dispute.json"


# ─────────────────────────────────────────────────────────────────────
# Issue 1: Decoy contexts for empty abstention cases
# ─────────────────────────────────────────────────────────────────────

# Each entry: case_id -> list of decoy contexts (related but NOT answering the query)
DECOY_CONTEXTS = {
    "t1_abstain_hard_850": [
        # Query: What are the known drug interactions between metformin and ACE inhibitors?
        # Rationale: decoys discuss metformin and ACE inhibitors separately but never their interaction
        "Metformin is the first-line treatment for type 2 diabetes mellitus, working primarily by "
        "decreasing hepatic glucose production and improving insulin sensitivity in peripheral tissues.",
        "ACE inhibitors such as lisinopril and enalapril are widely prescribed for hypertension and "
        "heart failure, functioning by blocking the conversion of angiotensin I to angiotensin II.",
        "Polypharmacy in elderly patients with multiple comorbidities increases the risk of adverse "
        "drug events, with studies suggesting that patients on five or more medications should receive "
        "regular medication reviews.",
    ],
    "t1_abstain_hard_851": [
        # Query: Why did the Federal Reserve raise interest rates in Q3 of the reporting period?
        # Rationale: decoys discuss Fed structure and general monetary policy but not Q3 rate decision
        "The Federal Reserve System consists of twelve regional banks and a Board of Governors that "
        "oversees monetary policy in the United States.",
        "Interest rate decisions are typically communicated through the Federal Open Market Committee "
        "(FOMC) statements, which are released eight times per year after scheduled meetings.",
        "Historical analysis shows that the federal funds rate has ranged from near-zero during the "
        "2008 financial crisis to over 20% in the early 1980s under Chairman Paul Volcker.",
    ],
    "t1_abstain_hard_852": [
        # Query: How do I file a wrongful termination claim in the state of Oregon?
        # Rationale: decoys discuss employment law concepts but not Oregon-specific filing procedures
        "Wrongful termination occurs when an employer fires an employee in violation of federal or "
        "state law, public policy, or the terms of an employment contract.",
        "At-will employment, which is the default in most U.S. states, allows either the employer or "
        "employee to end the relationship at any time for any lawful reason.",
        "The Equal Employment Opportunity Commission (EEOC) handles federal workplace discrimination "
        "complaints, typically requiring that a charge be filed within 180 days of the alleged violation.",
    ],
    "t1_abstain_hard_853": [
        # Query: How does the garbage collector in the V8 engine handle weak references?
        # Rationale: decoys discuss V8 general architecture and GC concepts but not weak reference handling
        "The V8 JavaScript engine, developed by Google for Chrome and Node.js, compiles JavaScript "
        "directly to native machine code using just-in-time (JIT) compilation techniques.",
        "Modern garbage collectors generally use generational collection strategies, dividing the heap "
        "into young and old generations to optimize for the observation that most objects die young.",
        "WeakRef and FinalizationRegistry were introduced in the ECMAScript 2021 specification, "
        "providing developers with the ability to hold weak references to objects in JavaScript.",
    ],
    "t1_abstain_hard_854": [
        # Query: Should we adopt a microservices architecture for our payment processing system?
        # Rationale: decoys discuss microservices generally but not in the context of any specific system
        "Microservices architecture decomposes applications into small, independently deployable services "
        "that communicate through well-defined APIs, typically using HTTP/REST or message queues.",
        "According to a 2023 industry survey, approximately 85% of enterprises with over 5,000 employees "
        "have adopted some form of microservices, though many report challenges with observability and "
        "distributed tracing.",
        "Payment processing systems must comply with PCI DSS (Payment Card Industry Data Security "
        "Standard) requirements, which mandate strict controls over cardholder data storage and transmission.",
    ],
    "t1_abstain_hard_855": [
        # Query: How does the efficacy of CBT compare to EMDR for treating PTSD in adolescents?
        # Rationale: decoys discuss CBT and EMDR separately but not comparative efficacy in adolescents
        "Cognitive Behavioral Therapy (CBT) is a structured, time-limited psychotherapy that focuses "
        "on identifying and modifying dysfunctional thought patterns and behaviors.",
        "Eye Movement Desensitization and Reprocessing (EMDR) was developed by Francine Shapiro in "
        "1987 and involves guided eye movements while the patient recalls traumatic memories.",
        "Post-traumatic stress disorder (PTSD) in adolescents may present differently than in adults, "
        "with symptoms including irritability, difficulty concentrating, and regression to earlier "
        "developmental behaviors.",
    ],
    "t1_abstain_hard_856": [
        # Query: How many production incidents were caused by the authentication service last quarter?
        # Rationale: decoys discuss incident management and auth services generally, no specific counts
        "The authentication service handles approximately 2.4 million login requests per day across "
        "all supported identity providers, including OAuth 2.0, SAML, and LDAP integrations.",
        "The organization's incident management framework classifies production incidents into four "
        "severity levels, with SEV-1 requiring immediate response and SEV-4 handled during business hours.",
        "A post-incident review process was adopted in Q1 to improve mean time to resolution (MTTR), "
        "resulting in a 30% reduction in resolution time for SEV-1 and SEV-2 incidents.",
    ],
    "t1_abstain_hard_857": [
        # Query: When did the company's data retention policy last get updated?
        # Rationale: decoys discuss data retention concepts and compliance but not the specific policy date
        "Data retention policies define how long an organization stores different categories of data "
        "and the procedures for secure deletion once the retention period expires.",
        "GDPR requires organizations to establish clear data retention periods and to not retain "
        "personal data longer than necessary for the purposes for which it was collected.",
    ],
    "t1_abstain_hard_858": [
        # Query: What is the recommended daily intake of vitamin D for patients with chronic kidney disease?
        # Rationale: decoys discuss vitamin D and CKD separately but not dosage recommendations for CKD patients
        "Vitamin D plays a critical role in calcium absorption, bone health, and immune function, with "
        "deficiency affecting an estimated one billion people worldwide.",
        "Chronic kidney disease (CKD) is classified into five stages based on glomerular filtration rate "
        "(GFR), with Stage 5 representing end-stage renal disease requiring dialysis or transplantation.",
        "The Kidney Disease: Improving Global Outcomes (KDIGO) organization publishes clinical practice "
        "guidelines covering various aspects of CKD management, including mineral and bone disorders.",
    ],
    "t1_abstain_hard_859": [
        # Query: Why did the batch processing pipeline fail on the night of March 12th?
        # Rationale: decoys discuss the pipeline's architecture but not the March 12th failure
        "The batch processing pipeline runs nightly at 02:00 UTC, processing approximately 4.2 million "
        "records from the data warehouse and generating reports for downstream analytics consumers.",
        "The pipeline is built on Apache Spark 3.4 running on a Kubernetes cluster with auto-scaling "
        "configured to handle variable workloads between 8 and 64 executor pods.",
        "Monitoring and alerting for the pipeline is handled through Datadog, with PagerDuty integration "
        "for on-call engineer notifications when job completion exceeds the 4-hour SLA threshold.",
    ],
    "t1_abstain_hard_860": [
        # Query: How do I configure the Kubernetes ingress controller to support mutual TLS?
        # Rationale: decoys discuss K8s ingress and mTLS concepts but not configuration steps
        "Kubernetes ingress controllers act as reverse proxies that route external HTTP/HTTPS traffic "
        "to services within the cluster based on rules defined in Ingress resources.",
        "Mutual TLS (mTLS) authentication requires both the client and server to present X.509 "
        "certificates during the TLS handshake, providing bidirectional identity verification.",
        "Popular ingress controller implementations include NGINX Ingress Controller, Traefik, HAProxy, "
        "and Istio's gateway, each with different feature sets and configuration approaches.",
    ],
    "t1_abstain_hard_861": [
        # Query: What are the tax implications of converting a traditional IRA to a Roth IRA for someone earning above the income threshold?
        # Rationale: decoys discuss IRA types generally but not conversion tax implications for high earners
        "A traditional IRA allows tax-deductible contributions with taxes deferred until withdrawal, "
        "while a Roth IRA uses after-tax contributions with tax-free qualified withdrawals.",
        "The IRS sets annual contribution limits for Individual Retirement Accounts, with the 2024 "
        "limit set at $7,000 for individuals under 50 and $8,000 for those 50 and older.",
        "Retirement planning strategies often involve balancing tax-deferred and tax-free accounts to "
        "optimize total tax burden across different income phases of life.",
    ],
    "t1_abstain_hard_863": [
        # Query: Is the Samsung Galaxy S25 Ultra worth buying over the iPhone 16 Pro Max?
        # Rationale: decoys discuss smartphone market trends but not specific comparisons of these models
        "The global smartphone market shipped 1.2 billion units in 2024, with Samsung and Apple "
        "collectively holding approximately 55% of the market share.",
        "Flagship smartphone pricing has steadily increased over the past decade, with premium devices "
        "now regularly exceeding $1,200 at launch.",
        "Consumer smartphone purchasing decisions are influenced by factors including brand ecosystem "
        "lock-in, camera quality, battery life, and operating system preference.",
    ],
    "t1_abstain_hard_864": [
        # Query: What is the mechanism by which CRISPR-Cas13 targets RNA rather than DNA?
        # Rationale: decoys discuss CRISPR generally and Cas9 but not Cas13's RNA-targeting mechanism
        "The CRISPR-Cas9 system uses a guide RNA to direct the Cas9 nuclease to a specific DNA "
        "sequence, where it creates a double-strand break that can be repaired by the cell's machinery.",
        "CRISPR technology has been adapted for numerous applications beyond gene editing, including "
        "gene regulation (CRISPRi/CRISPRa), epigenetic modification, and diagnostic platforms.",
        "The Cas protein family encompasses diverse nucleases with different target specificities, PAM "
        "requirements, and cleavage mechanisms, classified into two broad classes and six types.",
    ],
}


# ─────────────────────────────────────────────────────────────────────
# Issue 2: Source generation for dispute cases
# ─────────────────────────────────────────────────────────────────────

# Domain-appropriate source templates for dispute cases
# Each domain has a pool of source name templates to draw from
DOMAIN_SOURCE_POOLS = {
    "medicine": [
        "New England Journal of Medicine Study ({year})",
        "WHO Clinical Guidelines ({year})",
        "Mayo Clinic Research Report ({year})",
        "The Lancet Meta-Analysis ({year})",
        "CDC Morbidity and Mortality Report ({year})",
        "BMJ Systematic Review ({year})",
        "NIH National Institute of Health Study ({year})",
        "Johns Hopkins Medical Research ({year})",
        "American Medical Association Journal ({year})",
        "Cochrane Database Review ({year})",
        "Nature Medicine Research Article ({year})",
        "Annals of Internal Medicine ({year})",
        "Clinical Pharmacology and Therapeutics ({year})",
        "JAMA Network Open ({year})",
        "European Journal of Clinical Pharmacology ({year})",
    ],
    "technology": [
        "MIT Technology Review Analysis ({year})",
        "IEEE Computer Society Report ({year})",
        "Gartner Research Note ({year})",
        "ACM Computing Surveys ({year})",
        "Stanford HAI Research ({year})",
        "Forrester Wave Report ({year})",
        "McKinsey Digital Insights ({year})",
        "IDC Market Analysis ({year})",
        "Google Research Publication ({year})",
        "Microsoft Research Technical Report ({year})",
        "AWS Architecture Blog ({year})",
        "ThoughtWorks Technology Radar ({year})",
        "NIST Special Publication ({year})",
        "O'Reilly Industry Report ({year})",
    ],
    "finance": [
        "Federal Reserve Economic Data ({year})",
        "Bloomberg Market Analysis ({year})",
        "Goldman Sachs Research ({year})",
        "IMF World Economic Outlook ({year})",
        "S&P Global Market Intelligence ({year})",
        "Morgan Stanley Investment Report ({year})",
        "World Bank Economic Review ({year})",
        "JP Morgan Asset Management ({year})",
        "Moody's Analytics ({year})",
        "Bureau of Labor Statistics ({year})",
        "CFA Institute Research ({year})",
        "Brookings Institution Economic Study ({year})",
        "OECD Economic Surveys ({year})",
        "Deloitte Financial Services Report ({year})",
    ],
    "environment": [
        "Nature Climate Change Study ({year})",
        "IPCC Assessment Report ({year})",
        "EPA Environmental Monitoring Data ({year})",
        "NOAA Climate Research ({year})",
        "UN Environment Programme Report ({year})",
        "Science Magazine Environmental Study ({year})",
        "World Wildlife Fund Assessment ({year})",
        "National Geographic Research ({year})",
        "Environmental Defense Fund Analysis ({year})",
        "Yale Environment 360 Review ({year})",
        "Global Carbon Project Report ({year})",
        "European Environment Agency Data ({year})",
    ],
    "education": [
        "National Center for Education Statistics ({year})",
        "Harvard Graduate School of Education ({year})",
        "UNESCO Global Education Report ({year})",
        "OECD PISA Assessment ({year})",
        "American Educational Research Journal ({year})",
        "Brookings Brown Center Report ({year})",
        "Stanford Center for Education Policy ({year})",
        "Gates Foundation Education Study ({year})",
        "Education Week Research Center ({year})",
        "Journal of Educational Psychology ({year})",
        "National Science Foundation Study ({year})",
        "RAND Corporation Education Report ({year})",
    ],
    "law": [
        "Harvard Law Review ({year})",
        "Supreme Court Case Analysis ({year})",
        "American Bar Association Report ({year})",
        "Stanford Law Review ({year})",
        "Yale Law Journal ({year})",
        "Congressional Research Service ({year})",
        "Brennan Center for Justice ({year})",
        "Federal Judicial Center Report ({year})",
        "Georgetown Law Center Study ({year})",
        "National Law Review ({year})",
        "Law Commission Consultation Paper ({year})",
        "Columbia Law Review ({year})",
    ],
    "history": [
        "American Historical Review ({year})",
        "Oxford University Press Historical Study ({year})",
        "Cambridge History Series ({year})",
        "Smithsonian Institution Archives ({year})",
        "Journal of Modern History ({year})",
        "National Archives Research ({year})",
        "History Today Analysis ({year})",
        "Yale University Press Historical Study ({year})",
        "Journal of World History ({year})",
        "Past & Present Journal ({year})",
        "Library of Congress Research ({year})",
        "British Museum Historical Report ({year})",
    ],
    "hr_workplace": [
        "Society for Human Resource Management ({year})",
        "Gallup Workplace Report ({year})",
        "McKinsey Organizational Study ({year})",
        "Harvard Business Review ({year})",
        "Deloitte Human Capital Trends ({year})",
        "Bureau of Labor Statistics Report ({year})",
        "PwC Workforce of the Future ({year})",
        "Mercer Workforce Monitor ({year})",
        "CIPD People Management ({year})",
        "WorldatWork Compensation Study ({year})",
        "LinkedIn Workforce Report ({year})",
        "Willis Towers Watson HR Study ({year})",
    ],
    "science": [
        "Nature Research Article ({year})",
        "Science Magazine Study ({year})",
        "PNAS Research Publication ({year})",
        "Physical Review Letters ({year})",
        "Cell Press Research ({year})",
        "Annual Review of Science ({year})",
        "National Academy of Sciences ({year})",
        "European Research Council ({year})",
        "Royal Society Proceedings ({year})",
        "Scientific American Review ({year})",
        "arXiv Preprint Repository ({year})",
        "Max Planck Institute Study ({year})",
    ],
    "psychology": [
        "American Psychological Association ({year})",
        "Journal of Personality and Social Psychology ({year})",
        "Psychological Science ({year})",
        "Clinical Psychology Review ({year})",
        "Nature Human Behaviour ({year})",
        "Behavioural and Brain Sciences ({year})",
        "Annual Review of Psychology ({year})",
        "Journal of Experimental Psychology ({year})",
        "Cognitive Psychology Journal ({year})",
        "Psychological Bulletin ({year})",
        "British Journal of Psychology ({year})",
        "Developmental Psychology ({year})",
    ],
    "government": [
        "Congressional Budget Office ({year})",
        "Government Accountability Office ({year})",
        "Pew Research Center ({year})",
        "Brookings Institution Policy Brief ({year})",
        "RAND Corporation Analysis ({year})",
        "Council on Foreign Relations ({year})",
        "Heritage Foundation Policy Study ({year})",
        "Urban Institute Research ({year})",
        "Center for American Progress ({year})",
        "Cato Institute Analysis ({year})",
        "National Bureau of Economic Research ({year})",
        "Bipartisan Policy Center ({year})",
    ],
    "sports": [
        "ESPN Sports Analytics ({year})",
        "Sports Illustrated Report ({year})",
        "The Athletic Investigation ({year})",
        "NCAA Research Report ({year})",
        "International Olympic Committee ({year})",
        "FIFA Technical Study Group ({year})",
        "British Journal of Sports Medicine ({year})",
        "Sports Science Institute ({year})",
        "FiveThirtyEight Statistical Analysis ({year})",
        "Journal of Sports Sciences ({year})",
        "World Anti-Doping Agency Report ({year})",
        "Sport Management Review ({year})",
    ],
    "real_estate": [
        "National Association of Realtors ({year})",
        "Zillow Economic Research ({year})",
        "CoreLogic Market Report ({year})",
        "Urban Land Institute ({year})",
        "CBRE Research Report ({year})",
        "Federal Housing Finance Agency ({year})",
        "Freddie Mac Housing Survey ({year})",
        "Joint Center for Housing Studies ({year})",
        "Redfin Market Analysis ({year})",
        "PwC Real Estate Trends ({year})",
        "Cushman & Wakefield Report ({year})",
        "Mortgage Bankers Association ({year})",
    ],
    "agriculture": [
        "USDA Economic Research Service ({year})",
        "FAO Global Food Report ({year})",
        "Nature Food Research ({year})",
        "Journal of Agricultural Economics ({year})",
        "International Food Policy Research ({year})",
        "Agricultural Research Service ({year})",
        "World Resources Institute ({year})",
        "Agronomy Journal ({year})",
        "European Commission Agriculture Report ({year})",
        "Land Grant University Extension ({year})",
    ],
    "food": [
        "FDA Food Safety Report ({year})",
        "Journal of Food Science ({year})",
        "WHO Food Safety Assessment ({year})",
        "American Journal of Clinical Nutrition ({year})",
        "Food and Chemical Toxicology ({year})",
        "European Food Safety Authority ({year})",
        "Nutrition Reviews Journal ({year})",
        "Center for Science in the Public Interest ({year})",
        "Food Standards Agency Report ({year})",
        "Annual Review of Food Science ({year})",
    ],
    "social_media": [
        "Pew Research Internet Report ({year})",
        "Oxford Internet Institute Study ({year})",
        "MIT Media Lab Research ({year})",
        "Reuters Institute Digital Report ({year})",
        "Stanford Internet Observatory ({year})",
        "New Media & Society Journal ({year})",
        "Journal of Computer-Mediated Communication ({year})",
        "Data & Society Research ({year})",
        "Berkman Klein Center Study ({year})",
        "Social Media + Society Journal ({year})",
    ],
    "transportation": [
        "Department of Transportation Report ({year})",
        "National Highway Traffic Safety Administration ({year})",
        "International Transport Forum ({year})",
        "Transportation Research Board ({year})",
        "McKinsey Center for Future Mobility ({year})",
        "SAE International Research ({year})",
        "International Energy Agency Transport ({year})",
        "Bloomberg New Energy Finance ({year})",
        "Eno Center for Transportation ({year})",
        "American Public Transportation Association ({year})",
    ],
    "general": [
        "Reuters Investigation ({year})",
        "Associated Press Analysis ({year})",
        "The Economist Report ({year})",
        "Wall Street Journal Investigation ({year})",
        "Pew Research Center ({year})",
        "Brookings Institution Study ({year})",
        "RAND Corporation Analysis ({year})",
        "McKinsey Global Institute ({year})",
        "Council on Foreign Relations ({year})",
        "Oxford University Research ({year})",
        "Cambridge University Study ({year})",
        "National Academy of Sciences ({year})",
    ],
}


def generate_context_sources(case: dict) -> list[str]:
    """Generate plausible context_sources for a dispute case based on its domain and contexts.

    Strategy:
    1. For each context, extract organization/entity names mentioned in the text.
    2. If an organization is found, build a source string from it.
    3. If not, pick from the domain pool using deterministic rotation.
    4. Always ensure each source string is unique across the case.
    """
    import re

    domain = case.get("domain", "general")
    contexts = case.get("contexts", [])
    num_contexts = len(contexts)

    if num_contexts == 0:
        return []

    pool = DOMAIN_SOURCE_POOLS.get(domain, DOMAIN_SOURCE_POOLS["general"])

    # Use deterministic seed from case ID for reproducible fallback selection
    case_id = case.get("id", "unknown")
    # Simple hash: sum of char codes * position
    seed = sum(ord(c) * (i + 1) for i, c in enumerate(case_id)) & 0xFFFFFFFF

    # Patterns to extract named organizations/studies from context text
    org_patterns = [
        # "A Stanford study found..."
        r"(?:A|The|An)\s+([A-Z][A-Za-z\s]+?(?:University|Institute|Center|Centre|Lab|Agency|Organization|Foundation|Board|Commission|Council|Association|Society))\b",
        # "...by Harvard researchers..."
        r"(?:by|from|at)\s+(?:the\s+)?([A-Z][A-Za-z\s]+?(?:University|Institute|Center|Centre|Lab|Agency|Organization|Foundation|Board|Commission|Council|Association|Society))\b",
        # "A Stanford study", "A Harvard study"
        r"(?:A|The)\s+([A-Z][A-Za-z]+)\s+(?:study|research|report|analysis|survey|investigation|review|assessment|paper|trial)",
        # "Research by Dr. X" or "Dr. Smith's findings"
        r"(?:Dr\.\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        # "published in Nature", "in the Lancet"
        r"(?:published\s+in|in\s+the|in)\s+([A-Z][A-Za-z\s&]+?)(?:\s+(?:found|show|report|suggest|indicate|reveal|conclud))",
        # "according to the WHO", "the FDA"
        r"(?:according\s+to|by)\s+(?:the\s+)?([A-Z]{2,}[A-Za-z]*)\b",
        # "A 2023 study in Nature..."
        r"(?:A\s+\d{4}\s+(?:study|paper|report|analysis)\s+(?:in|by)\s+)([A-Z][A-Za-z\s&]+?)(?:\s+(?:found|show|report|suggest|indicate|using|pool))",
        # "The World Health Organization..."
        r"(?:The\s+)([A-Z][A-Za-z\s]+?(?:Organization|Programme|Project|Fund|Bureau|Administration|Department|Ministry))\b",
    ]

    def extract_source_from_context(ctx: str) -> str | None:
        """Try to extract a named source from context text."""
        ctx_stripped = ctx.strip()

        # Check for explicit organization mentions
        for pattern in org_patterns:
            match = re.search(pattern, ctx_stripped)
            if match:
                name = match.group(1) if match.lastindex else match.group(0)
                name = name.strip()
                # Clean up
                if len(name) > 5 and not name.startswith("The "):
                    return name
                elif name.startswith("The "):
                    return name[4:].strip()

        # Check for acronym organizations (WHO, FDA, CDC, EPA, etc.)
        acronym_match = re.search(r"\b((?:WHO|FDA|CDC|EPA|NIH|NASA|IPCC|OECD|IMF|UN|EU|NATO|NIST|DOE|DOD|USDA|FAO|NOAA|NSF|IEEE|ACM|APA|AMA|SHRM|FINRA|SEC|FTC|DOJ|DHS|OSHA|NLRB|EEOC))\b", ctx_stripped)
        if acronym_match:
            return acronym_match.group(1)

        return None

    # Acronym to full name mapping for nice source strings
    acronym_names = {
        "WHO": "World Health Organization",
        "FDA": "U.S. Food and Drug Administration",
        "CDC": "Centers for Disease Control and Prevention",
        "EPA": "Environmental Protection Agency",
        "NIH": "National Institutes of Health",
        "NASA": "NASA",
        "IPCC": "Intergovernmental Panel on Climate Change",
        "OECD": "Organisation for Economic Co-operation and Development",
        "IMF": "International Monetary Fund",
        "UN": "United Nations",
        "EU": "European Union",
        "NIST": "National Institute of Standards and Technology",
        "DOE": "Department of Energy",
        "USDA": "U.S. Department of Agriculture",
        "FAO": "Food and Agriculture Organization",
        "NOAA": "National Oceanic and Atmospheric Administration",
        "NSF": "National Science Foundation",
        "IEEE": "IEEE",
        "ACM": "ACM",
        "APA": "American Psychological Association",
        "AMA": "American Medical Association",
        "SHRM": "Society for Human Resource Management",
        "SEC": "Securities and Exchange Commission",
        "FTC": "Federal Trade Commission",
        "EEOC": "Equal Employment Opportunity Commission",
        "OSHA": "Occupational Safety and Health Administration",
    }

    # Publication type suffixes based on context content
    def get_pub_type(ctx_lower: str) -> str:
        if any(w in ctx_lower for w in ["study", "found", "researchers", "experiment"]):
            return "Research Study"
        if any(w in ctx_lower for w in ["survey", "poll", "respondents", "sample"]):
            return "Survey"
        if any(w in ctx_lower for w in ["report", "data", "statistics", "figures"]):
            return "Report"
        if any(w in ctx_lower for w in ["review", "meta-analysis", "systematic"]):
            return "Review"
        if any(w in ctx_lower for w in ["analysis", "model", "forecast"]):
            return "Analysis"
        if any(w in ctx_lower for w in ["guideline", "recommendation", "standard"]):
            return "Guidelines"
        return "Report"

    # Extract year from context if mentioned
    def extract_year(ctx: str) -> int | None:
        years = re.findall(r"\b(20[12]\d)\b", ctx)
        if years:
            return int(years[0])
        return None

    sources = []
    used_base_names: set[str] = set()  # Track base names (without year) to avoid duplicates

    for i, ctx in enumerate(contexts):
        ctx_lower = ctx.lower()
        extracted = extract_source_from_context(ctx)
        year = extract_year(ctx)
        if year is None:
            year = 2022 + ((seed + i * 3) % 3)

        source = None

        if extracted:
            # Map acronyms to full names
            base_name = acronym_names.get(extracted, extracted)
            pub_type = get_pub_type(ctx_lower)

            # Build the source string
            candidate = f"{base_name} {pub_type} ({year})"

            # Ensure uniqueness
            if candidate not in sources:
                source = candidate
                used_base_names.add(base_name)

        if source is None:
            # Fallback to domain pool with deterministic rotation
            start_idx = (seed + i * 7) % len(pool)
            for attempt in range(len(pool)):
                template = pool[(start_idx + attempt) % len(pool)]
                # Extract base name from template (remove {year} placeholder)
                template_base = template.replace(" ({year})", "")

                if template_base in used_base_names:
                    continue

                rendered = template.format(year=year)
                if rendered not in sources:
                    source = rendered
                    used_base_names.add(template_base)
                    break

            if source is None:
                # Last resort: use pool item with modified year
                for alt_year in range(2020, 2026):
                    template = pool[(start_idx) % len(pool)]
                    rendered = template.format(year=alt_year)
                    if rendered not in sources:
                        source = rendered
                        break
                if source is None:
                    source = f"Independent Research Source {i+1} ({year})"

        sources.append(source)

    return sources


def fix_abstention_contexts():
    """Fix Issue 1: Add decoy contexts to empty-context abstention cases."""
    print("=" * 70)
    print("ISSUE 1: Fixing empty-context abstention cases")
    print("=" * 70)

    with open(ABSTENTION_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    fixed_count = 0
    for case in data["cases"]:
        if case["id"] in DECOY_CONTEXTS:
            decoys = DECOY_CONTEXTS[case["id"]]
            case["contexts"] = decoys
            case["context_count"] = len(decoys)
            # Keep evidence_pattern as "absent" - the evidence for the specific question is absent
            # even though we now have decoy contexts (matching existing wrong_specificity cases)
            case["evidence_pattern"] = "absent"
            # Update subcategory from missing_data to wrong_specificity since contexts exist but don't answer
            case["subcategory"] = "wrong_specificity"
            fixed_count += 1
            print(f"  Fixed {case['id']}: added {len(decoys)} decoy contexts")

    # Verify all 14 were fixed
    remaining_empty = [c["id"] for c in data["cases"] if not c.get("contexts")]
    if remaining_empty:
        print(f"\n  WARNING: {len(remaining_empty)} cases still have empty contexts:")
        for cid in remaining_empty:
            print(f"    - {cid}")
    else:
        print(f"\n  All empty-context cases fixed ({fixed_count} total)")

    with open(ABSTENTION_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return fixed_count


def fix_dispute_context_sources(filepath: Path, tier_label: str) -> int:
    """Fix Issue 2: Populate context_sources for dispute cases missing them."""
    print(f"\n{'=' * 70}")
    print(f"ISSUE 2: Populating context_sources for {tier_label}")
    print(f"{'=' * 70}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_cases = len(data["cases"])
    already_have = 0
    fixed_count = 0
    skipped_no_ctx = 0

    for case in data["cases"]:
        contexts = case.get("contexts", [])
        existing_sources = case.get("context_sources")

        # Keep dict-format sources (original data) but regenerate string-format ones
        if existing_sources:
            has_dict_sources = any(isinstance(s, dict) for s in existing_sources)
            if has_dict_sources:
                already_have += 1
                continue
            # String-format sources from a previous run -- regenerate with improved algorithm
            # (fall through to regeneration below)

        if len(contexts) < 2:
            skipped_no_ctx += 1
            continue

        sources = generate_context_sources(case)
        case["context_sources"] = sources
        fixed_count += 1

    print(f"  Total cases: {total_cases}")
    print(f"  Already had context_sources: {already_have}")
    print(f"  Skipped (fewer than 2 contexts): {skipped_no_ctx}")
    print(f"  Fixed (sources added): {fixed_count}")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return fixed_count


def main():
    print("fitz-gov Data Fix Script")
    print("========================\n")

    # Issue 1: Fix empty-context abstention cases
    abstention_fixed = fix_abstention_contexts()

    # Issue 2: Fix dispute context_sources
    tier1_fixed = fix_dispute_context_sources(TIER1_DISPUTE_PATH, "tier1_core/dispute.json")
    tier0_fixed = fix_dispute_context_sources(TIER0_DISPUTE_PATH, "tier0_sanity/dispute.json")

    # Summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Abstention cases with contexts added: {abstention_fixed}")
    print(f"  Tier1 dispute cases with sources added: {tier1_fixed}")
    print(f"  Tier0 dispute cases with sources added: {tier0_fixed}")
    print(f"  Total modifications: {abstention_fixed + tier1_fixed + tier0_fixed}")
    print("\nDone.")


if __name__ == "__main__":
    main()
