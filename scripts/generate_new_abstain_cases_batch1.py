"""
Generate 50 new hard abstention cases (IDs t1_abstain_hard_1001 through t1_abstain_hard_1050).

Subcategory distribution:
  - cross_source_irrelevant (10): IDs 1001-1010, multi-source, each context unrelated
  - multi_source_gap (10): IDs 1011-1020, multi-source, related but missing specific answer
  - wrong_entity (15): IDs 1021-1035, single source, discusses different similarly-named entity
  - missing_data (15): IDs 1036-1050, single source, topic present but requested data absent

Output: scripts/new_abstain_batch1.json
"""

import json
import os

cases = []

# =============================================================================
# SUBCATEGORY 1: cross_source_irrelevant (10 cases, IDs 1001-1010)
# Multiple sources provided, but NONE answer the query. Each source discusses
# a different unrelated topic.
# Domain spread: 2 science, 2 law, 2 finance, 2 health, 2 tech
# =============================================================================

# 1001 - science
cases.append({
    "id": "t1_abstain_hard_1001",
    "difficulty": "hard",
    "subcategory": "cross_source_irrelevant",
    "query": "What is the half-life of carbon-14 and how is it used in archaeological dating?",
    "contexts": [
        "Carbon fiber composites are increasingly used in aerospace manufacturing due to their high strength-to-weight ratio. Boeing's 787 Dreamliner uses approximately 50% carbon fiber by weight.",
        "Carbon capture and storage (CCS) technology involves trapping CO2 emissions from power plants and injecting them into underground geological formations for long-term storage.",
        "Activated carbon filters are widely used in water purification systems, removing chlorine, sediment, and volatile organic compounds through adsorption."
    ],
    "context_sources": [
        {"source_id": "aerospace_materials_review", "source_type": "industry_journal", "authority": "secondary"},
        {"source_id": "doe_ccs_report_2024", "source_type": "government_report", "authority": "primary"},
        {"source_id": "water_treatment_handbook", "source_type": "technical_manual", "authority": "secondary"}
    ],
    "expected_mode": "abstain",
    "description": "Query about carbon-14 dating but all three contexts discuss unrelated carbon topics (fiber, capture, filters)",
    "rationale": "None of the sources discuss carbon-14 isotope, radioactive decay, or archaeological dating methods despite all mentioning 'carbon'"
})

# 1002 - science
cases.append({
    "id": "t1_abstain_hard_1002",
    "difficulty": "hard",
    "subcategory": "cross_source_irrelevant",
    "query": "What is the current atmospheric concentration of methane and its trend over the past decade?",
    "contexts": [
        "Natural gas extraction using hydraulic fracturing has increased US domestic production by 40% since 2010. The Permian Basin alone produces over 5 billion cubic feet per day.",
        "Cattle ranching is the leading driver of deforestation in the Amazon basin, with approximately 80% of cleared land converted to pasture for beef production."
    ],
    "context_sources": [
        {"source_id": "eia_natgas_production_2024", "source_type": "government_report", "authority": "primary"},
        {"source_id": "wwf_deforestation_brief", "source_type": "ngo_report", "authority": "secondary"}
    ],
    "expected_mode": "abstain",
    "description": "Query about atmospheric methane concentration but sources cover gas extraction and deforestation",
    "rationale": "Neither source provides atmospheric methane measurements in parts per billion or concentration trends, despite both relating to methane-linked activities"
})

# 1003 - law
cases.append({
    "id": "t1_abstain_hard_1003",
    "difficulty": "hard",
    "subcategory": "cross_source_irrelevant",
    "query": "What are the mandatory sentencing guidelines for federal drug trafficking offenses?",
    "contexts": [
        "The Drug Enforcement Administration (DEA) employs over 10,000 agents and maintains offices in 69 countries. Its annual budget exceeded $3.1 billion in fiscal year 2024.",
        "Drug scheduling under the Controlled Substances Act classifies substances into five schedules based on medical use, abuse potential, and safety profile. Schedule I includes heroin, LSD, and marijuana.",
        "Prescription drug monitoring programs (PDMPs) are state-run databases that track controlled substance prescriptions to identify potential misuse patterns."
    ],
    "context_sources": [
        {"source_id": "dea_annual_report_2024", "source_type": "government_report", "authority": "primary"},
        {"source_id": "csa_scheduling_overview", "source_type": "legal_reference", "authority": "authoritative"},
        {"source_id": "pdmp_state_comparison", "source_type": "policy_brief", "authority": "secondary"}
    ],
    "expected_mode": "abstain",
    "description": "Query about federal sentencing guidelines for trafficking but sources cover DEA operations, drug scheduling, and PDMPs",
    "rationale": "None of the sources address sentencing minimums, penalty ranges, or US Sentencing Commission guidelines for drug trafficking convictions"
})

# 1004 - law
cases.append({
    "id": "t1_abstain_hard_1004",
    "difficulty": "hard",
    "subcategory": "cross_source_irrelevant",
    "query": "What is the statute of limitations for filing a medical malpractice lawsuit in New York?",
    "contexts": [
        "New York's no-fault auto insurance law requires all drivers to carry personal injury protection (PIP) coverage with a minimum of $50,000 in benefits.",
        "The New York State Board for Professional Medical Conduct investigates complaints against physicians and can impose sanctions including license revocation."
    ],
    "context_sources": [
        {"source_id": "ny_insurance_law_guide", "source_type": "legal_reference", "authority": "authoritative"},
        {"source_id": "opmc_annual_report", "source_type": "government_report", "authority": "primary"}
    ],
    "expected_mode": "abstain",
    "description": "Query about malpractice statute of limitations but sources cover auto insurance and medical board conduct",
    "rationale": "Neither source discusses civil litigation timelines, filing deadlines, or statute of limitations provisions for malpractice claims in New York"
})

# 1005 - finance
cases.append({
    "id": "t1_abstain_hard_1005",
    "difficulty": "hard",
    "subcategory": "cross_source_irrelevant",
    "query": "What are the current interest rates for 30-year fixed mortgages?",
    "contexts": [
        "Commercial lending rates for business loans averaged 7.2% in Q3 2024, with SBA 7(a) loans ranging from 6.5% to 9.0% depending on loan amount and term.",
        "Housing starts increased 12% year-over-year in September 2024, with new construction concentrated in the Sun Belt states. Single-family permits rose to an annualized rate of 970,000 units."
    ],
    "context_sources": [
        {"source_id": "bank_report_q3_2024", "source_type": "industry_report", "authority": "secondary"},
        {"source_id": "realestate_quarterly_q3", "source_type": "market_report", "authority": "secondary"}
    ],
    "expected_mode": "abstain",
    "description": "Query about residential mortgage rates but sources cover commercial lending rates and housing construction",
    "rationale": "Commercial loan rates differ from residential mortgage rates, and housing start data provides no interest rate information"
})

# 1006 - finance
cases.append({
    "id": "t1_abstain_hard_1006",
    "difficulty": "hard",
    "subcategory": "cross_source_irrelevant",
    "query": "What is the current federal funds rate and when is the next FOMC meeting?",
    "contexts": [
        "The US national debt surpassed $34 trillion in January 2024, with annual interest payments exceeding $1 trillion for the first time in fiscal year 2024.",
        "Treasury yield curves have been inverted since July 2022, with the 2-year yield exceeding the 10-year yield by as much as 108 basis points.",
        "The Bureau of Labor Statistics reported nonfarm payrolls increased by 216,000 in December 2023, exceeding economist estimates of 170,000."
    ],
    "context_sources": [
        {"source_id": "treasury_debt_report_2024", "source_type": "government_report", "authority": "primary"},
        {"source_id": "bond_market_analysis_q1", "source_type": "financial_analysis", "authority": "secondary"},
        {"source_id": "bls_employment_dec2023", "source_type": "government_data", "authority": "authoritative"}
    ],
    "expected_mode": "abstain",
    "description": "Query about federal funds rate and FOMC schedule but sources cover national debt, yield curves, and employment",
    "rationale": "None of the sources state the current federal funds rate target or provide FOMC meeting dates despite all being macroeconomic data"
})

# 1007 - health
cases.append({
    "id": "t1_abstain_hard_1007",
    "difficulty": "hard",
    "subcategory": "cross_source_irrelevant",
    "query": "What is the recommended vaccination schedule for infants in their first year?",
    "contexts": [
        "Breastfeeding provides infants with essential antibodies, particularly immunoglobulin A (IgA), which helps protect against gastrointestinal infections during the first six months of life.",
        "The American Academy of Pediatrics recommends introducing solid foods at approximately six months of age, starting with iron-fortified cereals and pureed vegetables.",
        "Sudden Infant Death Syndrome (SIDS) risk is reduced by placing infants on their backs to sleep, using a firm mattress, and keeping soft objects out of the crib."
    ],
    "context_sources": [
        {"source_id": "aap_breastfeeding_guide", "source_type": "clinical_guideline", "authority": "authoritative"},
        {"source_id": "aap_nutrition_2024", "source_type": "clinical_guideline", "authority": "authoritative"},
        {"source_id": "nichd_safe_sleep_campaign", "source_type": "public_health", "authority": "primary"}
    ],
    "expected_mode": "abstain",
    "description": "Query about infant vaccination schedule but sources cover breastfeeding, solid food introduction, and SIDS prevention",
    "rationale": "All three sources are about infant health but none provide vaccination timelines, vaccine names, or immunization schedules"
})

# 1008 - health
cases.append({
    "id": "t1_abstain_hard_1008",
    "difficulty": "hard",
    "subcategory": "cross_source_irrelevant",
    "query": "What are the diagnostic criteria for Type 2 diabetes?",
    "contexts": [
        "Diabetic retinopathy affects approximately one-third of people with diabetes and is the leading cause of blindness among working-age adults in developed countries.",
        "Continuous glucose monitors (CGMs) measure interstitial glucose every 5 minutes and transmit readings to a smartphone app. The Dexcom G7 and Abbott FreeStyle Libre 3 are the most commonly prescribed models."
    ],
    "context_sources": [
        {"source_id": "aao_retinopathy_review", "source_type": "medical_journal", "authority": "primary"},
        {"source_id": "cgm_device_comparison_2024", "source_type": "device_review", "authority": "secondary"}
    ],
    "expected_mode": "abstain",
    "description": "Query about diabetes diagnostic criteria but sources cover complications and monitoring devices",
    "rationale": "Neither source provides diagnostic thresholds (HbA1c >= 6.5%, fasting glucose >= 126 mg/dL, etc.) or diagnostic criteria for Type 2 diabetes"
})

# 1009 - tech
cases.append({
    "id": "t1_abstain_hard_1009",
    "difficulty": "hard",
    "subcategory": "cross_source_irrelevant",
    "query": "How do I configure HTTPS with TLS 1.3 on an Nginx reverse proxy?",
    "contexts": [
        "Nginx load balancing supports round-robin, least connections, and IP hash algorithms. The upstream block defines backend server pools with optional weight parameters.",
        "HTTP/2 server push allows servers to proactively send resources to clients before they are requested, reducing page load times. However, Chrome removed support for server push in version 106.",
        "Content Security Policy (CSP) headers mitigate cross-site scripting by restricting which sources can load scripts, styles, and other resources on a web page."
    ],
    "context_sources": [
        {"source_id": "nginx_loadbalancing_docs", "source_type": "documentation", "authority": "authoritative"},
        {"source_id": "http2_performance_guide", "source_type": "technical_blog", "authority": "secondary"},
        {"source_id": "owasp_csp_cheatsheet", "source_type": "security_guide", "authority": "primary"}
    ],
    "expected_mode": "abstain",
    "description": "Query about TLS 1.3 configuration but sources cover load balancing, HTTP/2, and CSP headers",
    "rationale": "None of the sources address TLS configuration, certificate setup, cipher suites, or ssl_protocols directives for Nginx"
})

# 1010 - tech
cases.append({
    "id": "t1_abstain_hard_1010",
    "difficulty": "hard",
    "subcategory": "cross_source_irrelevant",
    "query": "What are the hardware requirements and setup process for running a local Kubernetes cluster?",
    "contexts": [
        "Docker Compose uses YAML files to define multi-container applications. Services, networks, and volumes are declared in a single docker-compose.yml file.",
        "Terraform is an infrastructure-as-code tool that provisions cloud resources using declarative configuration files written in HashiCorp Configuration Language (HCL)."
    ],
    "context_sources": [
        {"source_id": "docker_compose_reference", "source_type": "documentation", "authority": "authoritative"},
        {"source_id": "terraform_getting_started", "source_type": "documentation", "authority": "authoritative"}
    ],
    "expected_mode": "abstain",
    "description": "Query about local Kubernetes setup but sources cover Docker Compose and Terraform",
    "rationale": "Neither source discusses Kubernetes, minikube, kind, or k3s; Docker Compose and Terraform are different tools that do not answer Kubernetes cluster setup questions"
})

# =============================================================================
# SUBCATEGORY 2: multi_source_gap (10 cases, IDs 1011-1020)
# Multiple sources cover related topics but miss the specific question asked.
# Domain spread: 2 science, 2 law, 2 health, 2 education, 2 tech
# =============================================================================

# 1011 - science
cases.append({
    "id": "t1_abstain_hard_1011",
    "difficulty": "hard",
    "subcategory": "multi_source_gap",
    "query": "What is the exact orbital period of the newly discovered exoplanet Kepler-442b?",
    "contexts": [
        "Kepler-442b is a super-Earth exoplanet located in the habitable zone of its host star, approximately 1,206 light-years from Earth. It has an Earth Similarity Index of 0.84, making it one of the most Earth-like planets discovered.",
        "The Kepler space telescope identified over 2,600 confirmed exoplanets during its primary and extended missions. Its transit photometry method detects planets by measuring periodic dips in stellar brightness.",
        "Habitable zone exoplanets must receive between 25% and 200% of Earth's solar flux to potentially support liquid water on their surfaces."
    ],
    "context_sources": [
        {"source_id": "nasa_exoplanet_catalog", "source_type": "database_entry", "authority": "authoritative"},
        {"source_id": "kepler_mission_summary", "source_type": "mission_report", "authority": "primary"},
        {"source_id": "habitable_zone_criteria", "source_type": "peer_reviewed", "authority": "primary"}
    ],
    "expected_mode": "abstain",
    "description": "Query asks for exact orbital period but sources only describe the planet's characteristics, discovery method, and habitability criteria",
    "rationale": "Despite extensive information about Kepler-442b, none of the sources state its orbital period (which is approximately 112 days)"
})

# 1012 - science
cases.append({
    "id": "t1_abstain_hard_1012",
    "difficulty": "hard",
    "subcategory": "multi_source_gap",
    "query": "What is the tensile strength of graphene in gigapascals?",
    "contexts": [
        "Graphene is a single layer of carbon atoms arranged in a two-dimensional hexagonal lattice. It was first isolated in 2004 by Andre Geim and Konstantin Novoselov at the University of Manchester, who received the 2010 Nobel Prize in Physics.",
        "Graphene exhibits exceptional electrical conductivity, with electron mobility exceeding 200,000 cm2/Vs at room temperature. It is also the thinnest known material at one atom thick.",
        "Potential applications of graphene include flexible electronics, water filtration membranes, high-capacity batteries, and composite materials for aerospace."
    ],
    "context_sources": [
        {"source_id": "nature_graphene_review", "source_type": "peer_reviewed", "authority": "authoritative"},
        {"source_id": "graphene_properties_overview", "source_type": "technical_review", "authority": "primary"},
        {"source_id": "graphene_applications_2024", "source_type": "industry_report", "authority": "secondary"}
    ],
    "expected_mode": "abstain",
    "description": "Query asks for tensile strength value but sources cover discovery, electrical properties, and applications",
    "rationale": "None of the sources provide the mechanical strength measurement despite describing graphene's other exceptional properties"
})

# 1013 - law
cases.append({
    "id": "t1_abstain_hard_1013",
    "difficulty": "hard",
    "subcategory": "multi_source_gap",
    "query": "What is the maximum penalty for insider trading under SEC Rule 10b-5?",
    "contexts": [
        "SEC Rule 10b-5 prohibits any act of fraud or deceit in connection with the purchase or sale of securities. It was adopted in 1942 under the authority of Section 10(b) of the Securities Exchange Act of 1934.",
        "The SEC's enforcement division investigates potential violations including insider trading, accounting fraud, and market manipulation. In fiscal year 2024, the SEC filed 784 enforcement actions resulting in $4.6 billion in penalties.",
        "Material nonpublic information (MNPI) includes earnings results, merger announcements, and regulatory decisions that a reasonable investor would consider important in making an investment decision."
    ],
    "context_sources": [
        {"source_id": "sec_rule_10b5_text", "source_type": "regulation", "authority": "authoritative"},
        {"source_id": "sec_enforcement_annual_2024", "source_type": "government_report", "authority": "primary"},
        {"source_id": "mnpi_compliance_guide", "source_type": "legal_guide", "authority": "secondary"}
    ],
    "expected_mode": "abstain",
    "description": "Query asks for maximum penalties but sources explain the rule, enforcement activity, and MNPI definition",
    "rationale": "None of the sources state the specific maximum criminal penalties (up to 20 years imprisonment, $5M fine for individuals) or civil penalties for insider trading violations"
})

# 1014 - law
cases.append({
    "id": "t1_abstain_hard_1014",
    "difficulty": "hard",
    "subcategory": "multi_source_gap",
    "query": "What are the specific requirements for forming an LLC in Delaware?",
    "contexts": [
        "Delaware is the most popular state for business incorporation, with over 1.8 million legal entities registered there. The state's Court of Chancery specializes in corporate law and does not use jury trials.",
        "Limited liability companies combine the liability protection of corporations with the tax flexibility of partnerships. Members are generally not personally liable for the company's debts and obligations.",
        "Delaware's franchise tax is calculated using either the authorized shares method or the assumed par value capital method, whichever results in a lower tax."
    ],
    "context_sources": [
        {"source_id": "delaware_business_overview", "source_type": "state_publication", "authority": "primary"},
        {"source_id": "llc_structure_guide", "source_type": "legal_guide", "authority": "secondary"},
        {"source_id": "de_franchise_tax_guide", "source_type": "tax_guide", "authority": "primary"}
    ],
    "expected_mode": "abstain",
    "description": "Query asks for specific LLC formation requirements but sources cover Delaware's popularity, LLC structure overview, and franchise taxes",
    "rationale": "None of the sources list the actual formation steps: filing Certificate of Formation, registered agent requirements, filing fees, or operating agreement provisions"
})

# 1015 - health
cases.append({
    "id": "t1_abstain_hard_1015",
    "difficulty": "hard",
    "subcategory": "multi_source_gap",
    "query": "What dosage of melatonin is recommended for children with ADHD?",
    "contexts": [
        "Melatonin is a naturally occurring hormone produced by the pineal gland that regulates the circadian rhythm. It is available as an over-the-counter supplement in the United States but requires a prescription in most European countries.",
        "Children with ADHD often experience sleep difficulties, with studies showing 25-50% have clinically significant sleep problems. Sleep onset delay is the most common complaint among parents of children with ADHD."
    ],
    "context_sources": [
        {"source_id": "sleep_medicine_review_2024", "source_type": "peer_reviewed", "authority": "primary"},
        {"source_id": "adhd_sleep_comorbidity", "source_type": "clinical_study", "authority": "primary"}
    ],
    "expected_mode": "abstain",
    "description": "Query asks for specific melatonin dosage for ADHD children but sources only describe melatonin generally and ADHD sleep issues",
    "rationale": "Neither source provides pediatric dosing recommendations, effective dose ranges, or clinical guidelines for melatonin use in ADHD populations"
})

# 1016 - health
cases.append({
    "id": "t1_abstain_hard_1016",
    "difficulty": "hard",
    "subcategory": "multi_source_gap",
    "query": "What is the five-year survival rate for stage IIIA non-small cell lung cancer?",
    "contexts": [
        "Non-small cell lung cancer (NSCLC) accounts for approximately 85% of all lung cancers. The three main subtypes are adenocarcinoma, squamous cell carcinoma, and large cell carcinoma.",
        "Staging of NSCLC uses the TNM system, where T describes tumor size, N indicates lymph node involvement, and M denotes metastasis. Stage IIIA includes tumors with ipsilateral mediastinal lymph node involvement.",
        "Treatment options for advanced NSCLC include chemotherapy, targeted therapy, immunotherapy, and radiation. Pembrolizumab combined with platinum-based chemotherapy is a first-line standard of care."
    ],
    "context_sources": [
        {"source_id": "nccn_nsclc_guidelines", "source_type": "clinical_guideline", "authority": "authoritative"},
        {"source_id": "ajcc_staging_manual_8e", "source_type": "reference_manual", "authority": "authoritative"},
        {"source_id": "nsclc_treatment_update_2024", "source_type": "medical_journal", "authority": "primary"}
    ],
    "expected_mode": "abstain",
    "description": "Query asks for specific survival rate but sources cover NSCLC types, staging definitions, and treatment options",
    "rationale": "Despite detailed NSCLC information including Stage IIIA staging criteria, none of the sources provide the actual five-year survival rate percentage"
})

# 1017 - education
cases.append({
    "id": "t1_abstain_hard_1017",
    "difficulty": "hard",
    "subcategory": "multi_source_gap",
    "query": "What is the acceptance rate for Stanford's computer science PhD program?",
    "contexts": [
        "Stanford University's Computer Science Department offers specializations in artificial intelligence, systems, theory, and human-computer interaction. The department has 48 tenure-track faculty members.",
        "Stanford's overall graduate acceptance rate across all programs was approximately 5.2% for the 2024-2025 admissions cycle, with over 50,000 applications received.",
        "The GRE is optional for Stanford's computer science PhD applicants starting from the 2024 admissions cycle. The department emphasizes research experience and letters of recommendation."
    ],
    "context_sources": [
        {"source_id": "stanford_cs_dept_overview", "source_type": "university_page", "authority": "primary"},
        {"source_id": "stanford_grad_admissions_2024", "source_type": "admissions_report", "authority": "primary"},
        {"source_id": "stanford_cs_phd_faq", "source_type": "university_page", "authority": "primary"}
    ],
    "expected_mode": "abstain",
    "description": "Query asks for CS PhD acceptance rate but sources provide department overview, university-wide rate, and application requirements",
    "rationale": "The university-wide 5.2% rate cannot be applied to the CS PhD program specifically, and no source provides the department-level acceptance rate"
})

# 1018 - education
cases.append({
    "id": "t1_abstain_hard_1018",
    "difficulty": "hard",
    "subcategory": "multi_source_gap",
    "query": "What is the average starting salary for graduates of MIT's MBA program?",
    "contexts": [
        "MIT Sloan School of Management offers MBA, Master of Finance, and Executive MBA programs. The full-time MBA class of 2024 had 410 students from 60 countries.",
        "MIT Sloan's MBA tuition for the 2024-2025 academic year is $82,000 per year, with estimated total cost of attendance including living expenses at approximately $115,000 annually.",
        "MIT Sloan MBA graduates enter careers in consulting (28%), technology (25%), finance (22%), and healthcare (8%). The school's career development office reports a 96% employment rate within three months of graduation."
    ],
    "context_sources": [
        {"source_id": "mit_sloan_program_overview", "source_type": "university_page", "authority": "primary"},
        {"source_id": "mit_sloan_financial_aid", "source_type": "university_page", "authority": "primary"},
        {"source_id": "mit_sloan_employment_2024", "source_type": "career_report", "authority": "primary"}
    ],
    "expected_mode": "abstain",
    "description": "Query asks for average starting salary but sources cover program details, tuition, and employment sectors",
    "rationale": "Despite detailed career outcomes data including sector breakdown and employment rate, no source provides the actual average or median starting salary figure"
})

# 1019 - tech
cases.append({
    "id": "t1_abstain_hard_1019",
    "difficulty": "hard",
    "subcategory": "multi_source_gap",
    "query": "What is the maximum context window size for GPT-4 Turbo in tokens?",
    "contexts": [
        "GPT-4 Turbo was announced at OpenAI DevDay in November 2023. It offers lower pricing than GPT-4 at $0.01 per 1K input tokens and $0.03 per 1K output tokens.",
        "Large language models use tokenization to break text into subword units. GPT-4 uses the cl100k_base tokenizer, which typically represents English text at approximately 0.75 words per token.",
        "OpenAI's API rate limits for GPT-4 Turbo depend on usage tier, with Tier 1 users limited to 500 requests per minute and 30,000 tokens per minute."
    ],
    "context_sources": [
        {"source_id": "openai_devday_2023_recap", "source_type": "news_article", "authority": "secondary"},
        {"source_id": "tokenization_explainer", "source_type": "technical_blog", "authority": "secondary"},
        {"source_id": "openai_rate_limits_docs", "source_type": "documentation", "authority": "authoritative"}
    ],
    "expected_mode": "abstain",
    "description": "Query asks for max context window size but sources cover pricing, tokenization basics, and rate limits",
    "rationale": "None of the sources state the maximum context window (128K tokens); pricing, tokenizer details, and rate limits are related but do not answer the context window question"
})

# 1020 - tech
cases.append({
    "id": "t1_abstain_hard_1020",
    "difficulty": "hard",
    "subcategory": "multi_source_gap",
    "query": "What encryption algorithm does Signal use for end-to-end message encryption?",
    "contexts": [
        "Signal is a privacy-focused messaging app recommended by security researchers and journalists. It is operated by the Signal Foundation, a 501(c)(3) nonprofit organization founded by Moxie Marlinspike and Brian Acton.",
        "End-to-end encryption ensures that only the sender and recipient can read message contents. The encryption keys are generated and stored on user devices rather than on centralized servers.",
        "Signal's open-source code is published on GitHub and has been independently audited by multiple security firms. The app is available on iOS, Android, Windows, macOS, and Linux."
    ],
    "context_sources": [
        {"source_id": "signal_foundation_about", "source_type": "organization_page", "authority": "primary"},
        {"source_id": "e2ee_encryption_primer", "source_type": "technical_guide", "authority": "secondary"},
        {"source_id": "signal_security_audit_2024", "source_type": "audit_report", "authority": "primary"}
    ],
    "expected_mode": "abstain",
    "description": "Query asks for the specific encryption algorithm but sources cover Signal's background, general E2EE concepts, and audit status",
    "rationale": "None of the sources name the Signal Protocol, Double Ratchet Algorithm, or specific cryptographic primitives (X3DH, AES-256, Curve25519) used by Signal"
})

# =============================================================================
# SUBCATEGORY 3: wrong_entity (15 cases, IDs 1021-1035)
# Context discusses a different entity with a similar or identical name.
# Domain spread: 3 tech, 3 finance, 3 science, 3 geography, 3 law
# =============================================================================

# 1021 - tech
cases.append({
    "id": "t1_abstain_hard_1021",
    "difficulty": "hard",
    "subcategory": "wrong_entity",
    "query": "What is the market capitalization of Mercury?",
    "contexts": [
        "Mercury Insurance Group reported total assets of $6.2 billion and net premiums earned of $4.8 billion in fiscal year 2024. The company operates primarily in California and is headquartered in Los Angeles.",
        "Mercury Systems, Inc. is a defense electronics company specializing in secure signal processing subsystems. Its 2024 revenue was $890 million, down 12% from the prior year due to contract delays."
    ],
    "expected_mode": "abstain",
    "description": "Query asks about 'Mercury' without specifying which entity, and two different companies named Mercury are discussed",
    "rationale": "The query is ambiguous between Mercury Insurance and Mercury Systems (and potentially the planet or element), and neither context provides market capitalization data"
})

# 1022 - tech
cases.append({
    "id": "t1_abstain_hard_1022",
    "difficulty": "hard",
    "subcategory": "wrong_entity",
    "query": "How do I install and configure Apollo Server for my GraphQL API?",
    "contexts": [
        "Apollo 11 was the first crewed mission to land on the Moon on July 20, 1969. Neil Armstrong and Buzz Aldrin spent approximately 2 hours and 15 minutes on the lunar surface.",
        "The Apollo spacecraft consisted of three parts: the Command Module, Service Module, and Lunar Module. The Command Module was the only section designed to return to Earth."
    ],
    "expected_mode": "abstain",
    "description": "Query about Apollo Server (GraphQL library) but contexts discuss the Apollo space program",
    "rationale": "The Apollo space missions are an entirely different entity from the Apollo Server JavaScript library; lunar mission details cannot answer GraphQL configuration questions"
})

# 1023 - tech
cases.append({
    "id": "t1_abstain_hard_1023",
    "difficulty": "hard",
    "subcategory": "wrong_entity",
    "query": "What are the pricing tiers for Elastic Cloud managed Elasticsearch?",
    "contexts": [
        "Elastic bandages are commonly used to wrap sprains and strains, providing compression to reduce swelling. They should be applied in a spiral pattern, starting below the injury and wrapping upward.",
        "Elastic demand in economics refers to goods where a small change in price leads to a proportionally larger change in quantity demanded. Luxury goods typically exhibit elastic demand with price elasticity greater than 1."
    ],
    "expected_mode": "abstain",
    "description": "Query about Elastic (the search company) but contexts discuss elastic bandages and economic elasticity",
    "rationale": "Neither medical elastic bandages nor economic demand elasticity relates to Elasticsearch or Elastic Cloud pricing"
})

# 1024 - finance
cases.append({
    "id": "t1_abstain_hard_1024",
    "difficulty": "hard",
    "subcategory": "wrong_entity",
    "query": "What is the current dividend yield of Vanguard Total Stock Market ETF (VTI)?",
    "contexts": [
        "Vanguard Group, founded by John Bogle in 1975, pioneered low-cost index investing and currently manages over $8.6 trillion in global assets. The company is owned by its funds, which are in turn owned by their shareholders.",
        "The Vanguard 500 Index Fund (VFIAX) tracks the S&P 500 and has an expense ratio of 0.04%. It requires a minimum investment of $3,000 and had a 12-month trailing yield of 1.35% as of September 2024."
    ],
    "expected_mode": "abstain",
    "description": "Query about VTI (Total Stock Market ETF) but context discusses Vanguard the company and VFIAX (S&P 500 fund)",
    "rationale": "VTI tracks the total US stock market (~4,000 stocks) while VFIAX tracks only the S&P 500 (~500 stocks) - they are different funds with different yields, holdings, and performance"
})

# 1025 - finance
cases.append({
    "id": "t1_abstain_hard_1025",
    "difficulty": "hard",
    "subcategory": "wrong_entity",
    "query": "What are the terms of Chase Sapphire Reserve's travel insurance coverage?",
    "contexts": [
        "Chase Sapphire Preferred cardholders earn 2x points on travel and dining purchases, with a $95 annual fee. The card includes primary rental car insurance and no foreign transaction fees.",
        "Chase Freedom Unlimited offers 1.5% cash back on all purchases with no annual fee. Cardholders can transfer Freedom Unlimited points to Sapphire cards if they hold both products."
    ],
    "expected_mode": "abstain",
    "description": "Query about Sapphire Reserve but context discusses Sapphire Preferred and Freedom Unlimited",
    "rationale": "The Sapphire Reserve is a different card from Sapphire Preferred with different benefits, fees ($550 vs $95), and travel insurance provisions"
})

# 1026 - finance
cases.append({
    "id": "t1_abstain_hard_1026",
    "difficulty": "hard",
    "subcategory": "wrong_entity",
    "query": "What is Goldman Sachs' revenue for fiscal year 2024?",
    "contexts": [
        "Morgan Stanley reported net revenue of $54.1 billion for fiscal year 2024, a 14% increase year-over-year. Wealth management contributed $28.4 billion, making it the firm's largest business segment.",
        "JPMorgan Chase posted record net revenue of $162.4 billion in 2024, driven by strong net interest income of $91.6 billion. The firm's return on tangible common equity was 21%."
    ],
    "expected_mode": "abstain",
    "description": "Query about Goldman Sachs but contexts provide financials for Morgan Stanley and JPMorgan Chase",
    "rationale": "Morgan Stanley and JPMorgan Chase are different investment banks from Goldman Sachs; their financial results cannot be used to answer questions about Goldman's revenue"
})

# 1027 - science
cases.append({
    "id": "t1_abstain_hard_1027",
    "difficulty": "hard",
    "subcategory": "wrong_entity",
    "query": "What is the mass of the Higgs boson in GeV/c2?",
    "contexts": [
        "The W boson has a mass of approximately 80.4 GeV/c2 and mediates the weak nuclear force along with the Z boson. In 2022, the CDF experiment at Fermilab reported a W boson mass measurement of 80.4335 GeV/c2, significantly higher than the Standard Model prediction.",
        "The Z boson has a mass of 91.19 GeV/c2 and was discovered at CERN in 1983. It is electrically neutral and decays into lepton-antilepton or quark-antiquark pairs."
    ],
    "expected_mode": "abstain",
    "description": "Query asks for the Higgs boson mass but contexts describe W and Z boson masses",
    "rationale": "The W boson (80.4 GeV) and Z boson (91.2 GeV) are different fundamental particles from the Higgs boson (~125 GeV); their masses cannot answer the Higgs mass question"
})

# 1028 - science
cases.append({
    "id": "t1_abstain_hard_1028",
    "difficulty": "hard",
    "subcategory": "wrong_entity",
    "query": "What is the genome size of Arabidopsis thaliana?",
    "contexts": [
        "Arabidopsis lyrata is a perennial flowering plant with a genome of approximately 207 Mb distributed across 8 chromosomes. It is a close relative of the model organism A. thaliana and is used to study genome evolution.",
        "Arabidopsis halleri is a zinc and cadmium hyperaccumulator native to Europe. Its genome has been partially sequenced to identify genes responsible for heavy metal tolerance."
    ],
    "expected_mode": "abstain",
    "description": "Query asks about A. thaliana but contexts discuss A. lyrata and A. halleri",
    "rationale": "Different Arabidopsis species have different genome sizes; A. lyrata's 207 Mb genome cannot be used to answer questions about A. thaliana (~135 Mb)"
})

# 1029 - science
cases.append({
    "id": "t1_abstain_hard_1029",
    "difficulty": "hard",
    "subcategory": "wrong_entity",
    "query": "What is the maximum depth of Lake Superior?",
    "contexts": [
        "Lake Michigan has a maximum depth of 923 feet (281 meters) and a surface area of 22,404 square miles. It is the only Great Lake located entirely within the United States.",
        "Lake Huron reaches a maximum depth of 750 feet (229 meters) and contains Manitoulin Island, the largest freshwater island in the world at 1,068 square miles."
    ],
    "expected_mode": "abstain",
    "description": "Query asks about Lake Superior but contexts provide depth data for Lake Michigan and Lake Huron",
    "rationale": "Lake Michigan and Lake Huron are different Great Lakes from Lake Superior; their depth measurements cannot answer questions about Superior's maximum depth (1,332 feet)"
})

# 1030 - geography
cases.append({
    "id": "t1_abstain_hard_1030",
    "difficulty": "hard",
    "subcategory": "wrong_entity",
    "query": "What is the population of Portland, Oregon?",
    "contexts": [
        "Portland, Maine has a population of approximately 68,400 as of the 2020 census, making it the most populous city in Maine. The greater Portland metropolitan area has roughly 538,000 residents.",
        "Portland, Maine's economy is driven by healthcare, education, tourism, and a growing craft brewery industry. The city's median home price rose to $485,000 in 2024."
    ],
    "expected_mode": "abstain",
    "description": "Query asks about Portland, Oregon but both contexts discuss Portland, Maine",
    "rationale": "Portland, Maine (population ~68K) is a different city from Portland, Oregon (population ~635K); Maine data cannot answer Oregon population questions"
})

# 1031 - geography
cases.append({
    "id": "t1_abstain_hard_1031",
    "difficulty": "hard",
    "subcategory": "wrong_entity",
    "query": "What is the elevation and climate of Springfield, Illinois?",
    "contexts": [
        "Springfield, Missouri has an elevation of 1,300 feet and a humid subtropical climate with hot summers and mild winters. Average annual rainfall is 44 inches.",
        "Springfield, Massachusetts is located along the Connecticut River at an elevation of 70 feet. The city experiences a humid continental climate with average January temperatures of 24 degrees F."
    ],
    "expected_mode": "abstain",
    "description": "Query asks about Springfield, Illinois but contexts describe Springfield, Missouri and Springfield, Massachusetts",
    "rationale": "There are over 30 cities named Springfield in the US; data from Missouri and Massachusetts cannot answer questions about the Illinois capital"
})

# 1032 - geography
cases.append({
    "id": "t1_abstain_hard_1032",
    "difficulty": "hard",
    "subcategory": "wrong_entity",
    "query": "What are the major industries in the state of Georgia?",
    "contexts": [
        "Georgia (the country) has a population of 3.7 million and is located in the Caucasus region at the crossroads of Europe and Asia. Its GDP was approximately $25 billion in 2024.",
        "Georgia's wine industry dates back over 8,000 years, with traditional qvevri clay vessel fermentation recognized as a UNESCO Intangible Cultural Heritage. The country produces over 250 grape varieties."
    ],
    "expected_mode": "abstain",
    "description": "Query likely refers to the US state of Georgia but contexts discuss the country of Georgia",
    "rationale": "The Republic of Georgia (Caucasus country) has entirely different industries from the US state of Georgia; Caucasian qvevri winemaking is irrelevant to the state's economy"
})

# 1033 - law
cases.append({
    "id": "t1_abstain_hard_1033",
    "difficulty": "hard",
    "subcategory": "wrong_entity",
    "query": "What are the key provisions of the SECURE Act for retirement savings?",
    "contexts": [
        "The SECURE 2.0 Act, signed into law in December 2022, raised the required minimum distribution (RMD) age to 73 starting in 2023 and to 75 starting in 2033. It also increased catch-up contribution limits for participants aged 60-63.",
        "SECURE 2.0 introduced automatic enrollment for new 401(k) and 403(b) plans starting in 2025, requiring employers to auto-enroll eligible employees at a contribution rate of at least 3%."
    ],
    "expected_mode": "abstain",
    "description": "Query asks about the original SECURE Act (2019) but contexts describe SECURE 2.0 Act (2022)",
    "rationale": "The SECURE Act of 2019 and SECURE 2.0 Act of 2022 are different legislation with different provisions; SECURE 2.0 details cannot answer questions about the original SECURE Act"
})

# 1034 - law
cases.append({
    "id": "t1_abstain_hard_1034",
    "difficulty": "hard",
    "subcategory": "wrong_entity",
    "query": "What were the holdings in Marbury v. Madison?",
    "contexts": [
        "In McCulloch v. Maryland (1819), Chief Justice John Marshall ruled that Congress had implied powers under the Necessary and Proper Clause to establish a national bank. The Court also held that states could not tax federal institutions.",
        "Gibbons v. Ogden (1824) established that the Commerce Clause grants Congress broad authority to regulate interstate commerce, including navigation. The decision struck down New York's monopoly on steamboat operations."
    ],
    "expected_mode": "abstain",
    "description": "Query asks about Marbury v. Madison but contexts discuss McCulloch v. Maryland and Gibbons v. Ogden",
    "rationale": "McCulloch and Gibbons are different Marshall Court cases from Marbury v. Madison; implied powers and commerce clause holdings are unrelated to judicial review doctrine"
})

# 1035 - law
cases.append({
    "id": "t1_abstain_hard_1035",
    "difficulty": "hard",
    "subcategory": "wrong_entity",
    "query": "What does Article III of the US Constitution establish?",
    "contexts": [
        "Article I of the US Constitution establishes the legislative branch, vesting all legislative powers in a bicameral Congress consisting of the Senate and the House of Representatives. Section 8 enumerates 18 specific powers granted to Congress.",
        "Article II establishes the executive branch and vests executive power in the President of the United States. It specifies eligibility requirements, the Electoral College process, and the President's powers as Commander in Chief."
    ],
    "expected_mode": "abstain",
    "description": "Query asks about Article III (judiciary) but contexts describe Articles I and II (legislature and executive)",
    "rationale": "Articles I and II cover the legislative and executive branches respectively; they cannot answer questions about Article III's establishment of the federal judiciary"
})

# =============================================================================
# SUBCATEGORY 4: missing_data (15 cases, IDs 1036-1050)
# Context exists on the topic but specific data requested is simply not present.
# Domain spread: 3 finance, 3 health, 3 science, 3 tech, 3 law
# =============================================================================

# 1036 - finance
cases.append({
    "id": "t1_abstain_hard_1036",
    "difficulty": "hard",
    "subcategory": "missing_data",
    "query": "What is Apple's gross margin percentage for Q4 2024?",
    "contexts": [
        "Apple Inc. reported Q4 2024 revenue of $94.9 billion, up 6% year-over-year. iPhone revenue was $46.2 billion, Services revenue reached $25.0 billion, and Mac revenue was $7.7 billion.",
        "Apple's Q4 2024 operating expenses included $7.8 billion in research and development and $6.5 billion in selling, general, and administrative costs."
    ],
    "expected_mode": "abstain",
    "description": "Revenue and OpEx are provided but cost of goods sold and gross margin are absent",
    "rationale": "Without cost of goods sold (COGS) data, gross margin cannot be determined from revenue and operating expenses alone"
})

# 1037 - finance
cases.append({
    "id": "t1_abstain_hard_1037",
    "difficulty": "hard",
    "subcategory": "missing_data",
    "query": "What is the current ratio of Tesla as of the most recent quarter?",
    "contexts": [
        "Tesla's balance sheet as of Q3 2024 showed total assets of $106.6 billion and total liabilities of $43.1 billion. Stockholders' equity was $63.5 billion.",
        "Tesla reported Q3 2024 free cash flow of $2.7 billion and capital expenditures of $2.8 billion. The company held $33.6 billion in cash, cash equivalents, and investments."
    ],
    "expected_mode": "abstain",
    "description": "Balance sheet totals and cash flow data present but current assets and current liabilities breakdown missing",
    "rationale": "Current ratio requires current assets divided by current liabilities; total assets/liabilities and cash flow data do not provide the current vs. non-current breakdown needed"
})

# 1038 - finance
cases.append({
    "id": "t1_abstain_hard_1038",
    "difficulty": "hard",
    "subcategory": "missing_data",
    "query": "What is the average expense ratio for Fidelity's target-date retirement funds?",
    "contexts": [
        "Fidelity Investments manages over $4.5 trillion in discretionary assets and serves 43 million individual investors. The company offers more than 560 mutual funds across equity, bond, and hybrid categories.",
        "Fidelity's target-date funds, branded as Fidelity Freedom Funds, automatically adjust asset allocation from stocks to bonds as the target retirement date approaches. The funds are available in five-year increments from 2010 to 2070."
    ],
    "expected_mode": "abstain",
    "description": "Fund family overview and target-date strategy described but no expense ratio data provided",
    "rationale": "Neither source provides expense ratios for any Fidelity fund; asset allocation strategy description cannot substitute for fee data"
})

# 1039 - health
cases.append({
    "id": "t1_abstain_hard_1039",
    "difficulty": "hard",
    "subcategory": "missing_data",
    "query": "What are the contraindications for administering the Moderna COVID-19 booster?",
    "contexts": [
        "The Moderna COVID-19 booster (mRNA-1273.815) was authorized by the FDA in September 2024, targeting the XBB.1.5 variant. Clinical trials showed it elicited a strong neutralizing antibody response in adults aged 18 and older.",
        "Common side effects of the Moderna booster include injection site pain (87%), fatigue (56%), headache (43%), and muscle pain (38%). Most side effects were mild to moderate and resolved within 2-3 days.",
        "The updated booster can be administered at least 2 months after the most recent COVID-19 vaccine dose. It is available as a single 0.5 mL intramuscular injection."
    ],
    "expected_mode": "abstain",
    "description": "Authorization, side effects, and dosing schedule provided but contraindications not listed",
    "rationale": "None of the sources list contraindications such as severe allergic reaction to a previous dose, known allergy to vaccine components, or polyethylene glycol sensitivity"
})

# 1040 - health
cases.append({
    "id": "t1_abstain_hard_1040",
    "difficulty": "hard",
    "subcategory": "missing_data",
    "query": "What is the bioavailability of oral versus intravenous iron supplementation?",
    "contexts": [
        "Iron deficiency anemia affects approximately 1.2 billion people worldwide and is the most common nutritional deficiency globally. It is particularly prevalent in premenopausal women, pregnant women, and young children.",
        "Oral iron supplements include ferrous sulfate, ferrous gluconate, and ferrous fumarate. Ferrous sulfate is the most commonly prescribed form, typically given at 325 mg three times daily.",
        "Intravenous iron formulations include iron sucrose, ferric carboxymaltose, and iron dextran. IV iron is indicated when oral iron is not tolerated or absorption is impaired."
    ],
    "expected_mode": "abstain",
    "description": "Iron deficiency prevalence and supplement types described but bioavailability percentages not provided",
    "rationale": "None of the sources compare bioavailability rates between oral and IV iron; listing available formulations does not answer the absorption percentage question"
})

# 1041 - health
cases.append({
    "id": "t1_abstain_hard_1041",
    "difficulty": "hard",
    "subcategory": "missing_data",
    "query": "What is the number needed to treat (NNT) for statins in primary prevention of cardiovascular events?",
    "contexts": [
        "Statins inhibit HMG-CoA reductase, the rate-limiting enzyme in cholesterol biosynthesis. This mechanism reduces LDL cholesterol by 30-50% depending on the specific statin and dose.",
        "Common statins include atorvastatin (Lipitor), rosuvastatin (Crestor), and simvastatin (Zocor). Atorvastatin and rosuvastatin are considered high-intensity statins.",
        "The 2018 ACC/AHA cholesterol guidelines recommend statin therapy for adults aged 40-75 with LDL cholesterol above 190 mg/dL, diabetes, or a 10-year ASCVD risk of 7.5% or higher."
    ],
    "expected_mode": "abstain",
    "description": "Statin mechanism, types, and prescribing guidelines provided but NNT values absent",
    "rationale": "None of the sources provide NNT statistics for primary prevention; mechanism of action and prescribing guidelines are different from treatment efficacy metrics"
})

# 1042 - science
cases.append({
    "id": "t1_abstain_hard_1042",
    "difficulty": "hard",
    "subcategory": "missing_data",
    "query": "What is the thermal conductivity of diamond at room temperature?",
    "contexts": [
        "Diamond is the hardest known natural material, scoring 10 on the Mohs hardness scale. It is composed of carbon atoms arranged in a face-centered cubic crystal structure with sp3 hybridized bonds.",
        "Industrial diamonds account for approximately 80% of diamond production by weight. They are used in cutting, grinding, drilling, and polishing applications across construction, mining, and manufacturing."
    ],
    "expected_mode": "abstain",
    "description": "Diamond hardness, crystal structure, and industrial uses described but thermal conductivity value not provided",
    "rationale": "Hardness and crystal structure cannot substitute for thermal conductivity data (approximately 2,200 W/mK); these are different physical properties"
})

# 1043 - science
cases.append({
    "id": "t1_abstain_hard_1043",
    "difficulty": "hard",
    "subcategory": "missing_data",
    "query": "What is the Curie temperature of iron?",
    "contexts": [
        "Iron is the most commonly used metal by mass, accounting for 95% of all metal produced worldwide. It has an atomic number of 26 and an atomic mass of 55.845 g/mol.",
        "Iron exists in several allotropic forms: alpha-iron (BCC structure below 912 degrees C), gamma-iron (FCC structure between 912 and 1394 degrees C), and delta-iron (BCC structure above 1394 degrees C).",
        "Iron is ferromagnetic, meaning it can be magnetized and attracted to magnets. This property makes it essential in electric motors, transformers, and magnetic storage media."
    ],
    "expected_mode": "abstain",
    "description": "Iron's atomic properties, allotropes, and magnetic behavior described but Curie temperature value absent",
    "rationale": "Despite discussing ferromagnetism and structural transitions, none of the sources provide the Curie temperature (770 degrees C) at which iron loses its ferromagnetic properties"
})

# 1044 - science
cases.append({
    "id": "t1_abstain_hard_1044",
    "difficulty": "hard",
    "subcategory": "missing_data",
    "query": "What is the pH of human blood under normal physiological conditions?",
    "contexts": [
        "Human blood consists of approximately 55% plasma and 45% formed elements (red blood cells, white blood cells, and platelets). An average adult has approximately 5 liters of blood.",
        "Blood performs multiple functions including oxygen transport via hemoglobin, immune defense through white blood cells, nutrient delivery, waste removal, and temperature regulation.",
        "Arterial blood gas analysis measures oxygen partial pressure (PaO2), carbon dioxide partial pressure (PaCO2), bicarbonate concentration, and oxygen saturation. Normal PaO2 is 80-100 mmHg."
    ],
    "expected_mode": "abstain",
    "description": "Blood composition, functions, and arterial blood gas values provided but pH value absent",
    "rationale": "Despite discussing blood gas analysis, none of the sources state the normal blood pH range (7.35-7.45); PaO2 and PaCO2 values are different measurements"
})

# 1045 - tech
cases.append({
    "id": "t1_abstain_hard_1045",
    "difficulty": "hard",
    "subcategory": "missing_data",
    "query": "What is the read latency in milliseconds for Amazon DynamoDB in the us-east-1 region?",
    "contexts": [
        "Amazon DynamoDB is a fully managed NoSQL database service that supports key-value and document data models. It provides consistent single-digit millisecond latency at any scale.",
        "DynamoDB pricing is based on read capacity units (RCU) and write capacity units (WCU). One RCU provides one strongly consistent read per second for items up to 4 KB. On-demand capacity mode charges $1.25 per million read request units.",
        "DynamoDB supports global tables for multi-region replication, point-in-time recovery for the last 35 days, and integration with AWS Lambda for event-driven processing."
    ],
    "expected_mode": "abstain",
    "description": "DynamoDB features, pricing, and capabilities described but specific regional latency measurement absent",
    "rationale": "The marketing claim of 'single-digit millisecond latency' is not the same as actual measured p50/p99 latency data for us-east-1; no specific latency benchmark is provided"
})

# 1046 - tech
cases.append({
    "id": "t1_abstain_hard_1046",
    "difficulty": "hard",
    "subcategory": "missing_data",
    "query": "How many monthly active users does Slack have as of 2024?",
    "contexts": [
        "Slack was acquired by Salesforce in July 2021 for $27.7 billion, the largest acquisition in Salesforce's history. The platform is now integrated with the Salesforce Customer 360 ecosystem.",
        "Slack supports over 2,600 third-party app integrations through its App Directory. The platform processes over 1 billion messages per week and supports channels, direct messages, and huddles for communication.",
        "Slack's paid plans include Pro ($7.25/user/month), Business+ ($12.50/user/month), and Enterprise Grid (custom pricing). Free plan limits include 90 days of message history and 10 app integrations."
    ],
    "expected_mode": "abstain",
    "description": "Slack's acquisition, integrations, message volume, and pricing listed but monthly active user count absent",
    "rationale": "Message volume (1 billion per week) and pricing tiers do not reveal monthly active user counts; none of the sources provide MAU figures"
})

# 1047 - tech
cases.append({
    "id": "t1_abstain_hard_1047",
    "difficulty": "hard",
    "subcategory": "missing_data",
    "query": "What is the power consumption in watts of the NVIDIA H100 GPU?",
    "contexts": [
        "The NVIDIA H100 GPU is built on the Hopper architecture and manufactured on TSMC's 4N process node. It contains 80 billion transistors and features 80 GB of HBM3 memory with 3.35 TB/s bandwidth.",
        "The H100 delivers up to 4 petaflops of FP8 training performance, a 6x improvement over the A100. It supports the Transformer Engine for accelerated large language model training and inference.",
        "NVIDIA's H100 is available in SXM and PCIe form factors. The SXM variant requires the HGX H100 baseboard and supports NVLink 4.0 with 900 GB/s bidirectional bandwidth per GPU."
    ],
    "expected_mode": "abstain",
    "description": "H100 architecture, memory, performance, and form factors described but power consumption (TDP) absent",
    "rationale": "Despite detailed H100 specifications, none of the sources provide the thermal design power (700W SXM / 350W PCIe) or power consumption figures"
})

# 1048 - law
cases.append({
    "id": "t1_abstain_hard_1048",
    "difficulty": "hard",
    "subcategory": "missing_data",
    "query": "What is the filing fee for a trademark application with the USPTO?",
    "contexts": [
        "The United States Patent and Trademark Office (USPTO) processes trademark applications under the Lanham Act. Trademarks can be registered for goods, services, or both across 45 international classes.",
        "Trademark registration provides nationwide constructive notice of ownership, the right to use the registered symbol, and the ability to bring infringement actions in federal court. Registration is valid for 10-year renewable terms.",
        "The trademark application process includes an initial review by an examining attorney, publication for opposition in the Official Gazette, and issuance of a registration certificate if no opposition is filed."
    ],
    "expected_mode": "abstain",
    "description": "USPTO trademark process, benefits, and registration terms described but filing fee amounts absent",
    "rationale": "None of the sources state the actual filing fees (TEAS Plus $250, TEAS Standard $350 per class); process descriptions cannot substitute for fee schedules"
})

# 1049 - law
cases.append({
    "id": "t1_abstain_hard_1049",
    "difficulty": "hard",
    "subcategory": "missing_data",
    "query": "What is the maximum small claims court limit in California?",
    "contexts": [
        "California's small claims court provides a streamlined process for resolving disputes without attorneys. Plaintiffs file claims at the courthouse in the county where the defendant lives or where the dispute occurred.",
        "Small claims court hearings in California are typically scheduled within 30-70 days of filing. The judge's decision is usually announced immediately after the hearing, and defendants have 30 days to file an appeal.",
        "To file a small claims case in California, the plaintiff must attempt to resolve the dispute before filing, complete form SC-100, and serve the defendant at least 15 days before the hearing."
    ],
    "expected_mode": "abstain",
    "description": "Small claims court procedures, timelines, and filing requirements described but dollar limit not provided",
    "rationale": "Despite detailed procedural information, none of the sources state the maximum claim amount ($12,500 for individuals, $6,250 for businesses)"
})

# 1050 - law
cases.append({
    "id": "t1_abstain_hard_1050",
    "difficulty": "hard",
    "subcategory": "missing_data",
    "query": "What is the standard of proof required in federal civil rights cases under Section 1983?",
    "contexts": [
        "Section 1983 of Title 42 of the United States Code provides a cause of action against any person who, acting under color of state law, deprives another of their federal constitutional or statutory rights.",
        "Qualified immunity shields government officials from Section 1983 liability unless the plaintiff demonstrates that the official violated a clearly established constitutional right. The Supreme Court has made qualified immunity increasingly difficult to overcome.",
        "Section 1983 claims can be brought against individual state actors, municipalities, and local government entities. However, states and state agencies are protected by Eleventh Amendment sovereign immunity."
    ],
    "expected_mode": "abstain",
    "description": "Section 1983 scope, qualified immunity, and defendant types described but standard of proof not stated",
    "rationale": "None of the sources specify the evidentiary standard (preponderance of the evidence for most claims, clear and convincing for punitive damages); procedural scope and immunity doctrines are different legal concepts"
})

# =============================================================================
# Write output
# =============================================================================

output = {"cases": cases}

script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, "new_abstain_batch1.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Generated {len(cases)} cases")
print(f"Output: {output_path}")

# Validation
subcategory_counts = {}
for case in cases:
    sub = case["subcategory"]
    subcategory_counts[sub] = subcategory_counts.get(sub, 0) + 1

print("\nSubcategory distribution:")
for sub, count in sorted(subcategory_counts.items()):
    print(f"  {sub}: {count}")

# Validate IDs
ids = [c["id"] for c in cases]
expected_ids = [f"t1_abstain_hard_{i}" for i in range(1001, 1051)]
assert ids == expected_ids, f"ID mismatch: got {ids}"
print(f"\nIDs: {ids[0]} through {ids[-1]} (all correct)")

# Validate multi-source cases have context_sources
multi_source_subs = {"cross_source_irrelevant", "multi_source_gap"}
for case in cases:
    if case["subcategory"] in multi_source_subs:
        assert "context_sources" in case, f"{case['id']} missing context_sources"
        assert len(case["context_sources"]) == len(case["contexts"]), (
            f"{case['id']}: context_sources length ({len(case['context_sources'])}) "
            f"!= contexts length ({len(case['contexts'])})"
        )
    assert case["difficulty"] == "hard", f"{case['id']} not hard"
    assert case["expected_mode"] == "abstain", f"{case['id']} not abstain"
    assert len(case["contexts"]) >= 2, f"{case['id']} has fewer than 2 contexts"
    assert len(case["query"]) > 10, f"{case['id']} query too short"
    assert len(case["description"]) > 10, f"{case['id']} description too short"
    assert len(case["rationale"]) > 10, f"{case['id']} rationale too short"

print("\nAll validations passed.")
