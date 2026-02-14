#!/usr/bin/env python3
"""
Generate 65 new medium-difficulty relevance test cases (t1_relevance_medium_065
through t1_relevance_medium_129) and append them to data/tier1_core/relevance.json.

Subcategory distribution:
  partial_answer: 6, wrong_entity_focus: 5, temporal_mismatch: 5,
  tangent_drift: 5, related_but_different: 5, over_answering: 5,
  granularity_mismatch: 4, prerequisite_missing: 4, scope_mismatch: 4,
  format_mismatch: 3, summarization_vs_answer: 3, cherry_picking: 3,
  false_precision: 3, assumption_injection: 2, symptom_only: 2,
  status_dump: 2, feature_dump: 2, instruction_only: 1, metric_avoidance: 1

Multi-source: 18 of 65
Domain spread: all 18 domains, max 5 per domain
Query type: what <= 16, how >= 13, is/does >= 13, why/should >= 8, when/who/which >= 6
"""

import json
import sys
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "tier1_core" / "relevance.json"

# fmt: off
NEW_CASES = [
    # =========================================================================
    # partial_answer (6 cases): 065-070
    # =========================================================================
    {
        "id": "t1_relevance_medium_065",
        "difficulty": "medium",
        "subcategory": "partial_answer",
        "query": "Does metformin have side effects AND what are the dosage recommendations for elderly patients?",
        "contexts": [
            "Metformin is a first-line treatment for type 2 diabetes. Common side effects include nausea, diarrhea, and abdominal cramping. Rare but serious effects include lactic acidosis and vitamin B12 deficiency with prolonged use. Side effects typically diminish after the first few weeks of treatment."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about both side effects and dosage for elderly, but context only covers side effects",
        "rationale": "LLM should note that dosage recommendations for elderly patients are not provided",
        "required_elements": ["dosage", "elderly", "not specified", "not mentioned", "not provided"],
        "forbidden_elements": ["\\d+\\s*mg", "start(ing)? (with|at|dose)", "titrat", "maximum dose"],
        "domain": "medicine",
        "query_type": "does",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "partial",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_066",
        "difficulty": "medium",
        "subcategory": "partial_answer",
        "query": "How do I configure SSL AND set up load balancing in Nginx?",
        "contexts": [
            "To configure SSL in Nginx, add ssl_certificate and ssl_certificate_key directives to your server block. Use TLS 1.2+ by setting ssl_protocols. Enable HSTS with add_header. Redirect HTTP to HTTPS using a separate server block on port 80 with a return 301 directive."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about SSL and load balancing, but context only covers SSL configuration",
        "rationale": "LLM should acknowledge that load balancing configuration is not addressed",
        "required_elements": ["load balancing", "not mentioned", "not provided", "not covered", "upstream"],
        "forbidden_elements": ["upstream\\s+\\w+", "proxy_pass", "weight\\s*=", "least_conn", "ip_hash"],
        "domain": "technology",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "procedural",
        "evidence_pattern": "partial",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_067",
        "difficulty": "medium",
        "subcategory": "partial_answer",
        "query": "When is the tuition payment deadline AND how much is room-and-board at Westfield University?",
        "contexts": [
            "Westfield University charges $42,500 per year in tuition for international undergraduates. This includes a $1,200 international services fee. Scholarships covering up to 30% of tuition are available for applicants with strong academic records."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about payment deadline and room-and-board cost, context only has tuition amount",
        "rationale": "LLM should note both the deadline and room-and-board costs are not specified",
        "required_elements": ["deadline", "room", "board", "not specified", "not mentioned"],
        "forbidden_elements": ["deadline.{0,10}(is|on|by) \\w+", "room.{0,10}\\$\\d", "\\$\\d.{0,10}(room|board|housing)"],
        "domain": "education",
        "query_type": "when",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "partial",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_068",
        "difficulty": "medium",
        "subcategory": "partial_answer",
        "query": "Is quinoa high in protein AND what is its glycemic index?",
        "contexts": [
            "Quinoa is a pseudocereal from South America. A one-cup cooked serving has about 8 grams of complete protein with all nine essential amino acids. It also has 5 grams of fiber, 39 grams of carbs, and is a good source of iron and magnesium."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about protein content and glycemic index, context only provides protein",
        "rationale": "LLM should acknowledge that glycemic index is not provided",
        "required_elements": ["glycemic index", "not specified", "not mentioned", "GI", "not provided"],
        "forbidden_elements": ["glycemic index (of|is|at) \\d", "GI (of|is|score|value) \\d", "low.{0,5}glycemic"],
        "domain": "food",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "partial",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_069",
        "difficulty": "medium",
        "subcategory": "partial_answer",
        "query": "How much does the city spend on parks AND what percentage goes to maintenance vs new construction?",
        "contexts": [
            "The city parks department manages 47 public parks covering 1,200 acres. The annual budget is $18.5 million for staff, seasonal programs, and events. The department has 142 full-time workers and 85 seasonal summer staff.",
            "Recent park upgrades include a new splash pad at Riverside Park, playground equipment at three neighborhood parks, and expanded trail systems. Community surveys show 78% approval of park services."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about total spend and maintenance vs construction breakdown, context gives total but no breakdown",
        "rationale": "LLM should note the breakdown between maintenance and new construction is not provided",
        "required_elements": ["breakdown", "maintenance", "construction", "not specified", "not provided"],
        "forbidden_elements": ["\\d+%\\s*(goes?|allocated|for) (to )?(maintenance|construction)", "maintenance.{0,15}\\d+%"],
        "domain": "government",
        "query_type": "how",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "partial",
        "context_sources": [
            {"source_id": "src_relevance_069_a", "source_type": "report", "authority": "high"},
            {"source_id": "src_relevance_069_b", "source_type": "article", "authority": "medium"},
        ],
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_070",
        "difficulty": "medium",
        "subcategory": "partial_answer",
        "query": "Who discovered Grade 5 titanium alloy AND what is its thermal conductivity?",
        "contexts": [
            "Grade 5 titanium (Ti-6Al-4V) is the most used titanium alloy, over 50% of total usage. It has ultimate tensile strength of ~950 MPa and yield strength of 880 MPa. It has excellent corrosion resistance and a density of 4.43 g/cm3, popular in aerospace and medical uses."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks who discovered the alloy and its thermal conductivity, context has only mechanical properties",
        "rationale": "LLM should acknowledge that discoverer and thermal conductivity are missing",
        "required_elements": ["thermal conductivity", "discovered", "not specified", "not mentioned"],
        "forbidden_elements": ["thermal conductivity.{0,10}(is|of|at) \\d", "W/(m|mK)", "discovered by"],
        "domain": "science",
        "query_type": "who",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "partial",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 4,
        },
    },
    # =========================================================================
    # wrong_entity_focus (5 cases): 071-075
    # =========================================================================
    {
        "id": "t1_relevance_medium_071",
        "difficulty": "medium",
        "subcategory": "wrong_entity_focus",
        "query": "Is the unemployment rate in Portugal improving?",
        "contexts": [
            "Spain's unemployment rate fell to 11.7% in Q4 2024, down from 12.9% a year earlier. Growth in tourism and tech sectors drove improvement. Youth unemployment in Spain remains at 27.4%, though significantly better than the 40%+ levels of 2013."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about Portugal but context only discusses Spain",
        "rationale": "LLM should recognize Spain and Portugal are different countries",
        "required_elements": ["Portugal", "not specified", "Spain", "not mentioned", "different"],
        "forbidden_elements": ["Portugal.{0,15}(unemployment|rate).{0,10}\\d", "\\d+%.*Portugal"],
        "domain": "government",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_072",
        "difficulty": "medium",
        "subcategory": "wrong_entity_focus",
        "query": "How does the Rivian R1S handle off-road terrain?",
        "contexts": [
            "The Rivian R1T pickup has a quad-motor setup with 835 hp. Adjustable air suspension provides up to 14.4 inches of ground clearance. It can ford 3 feet of water with approach and departure angles of 34 and 30 degrees. The truck completed the 13,000-mile Trans-Americas expedition."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about R1S (SUV) but context provides R1T (truck) specs",
        "rationale": "LLM should recognize R1S and R1T are different vehicles",
        "required_elements": ["R1S", "R1T", "not specified", "different", "not mentioned"],
        "forbidden_elements": ["R1S.{0,15}(clearance|ground|ford|motor)", "R1S.{0,10}(offers?|has|features?)"],
        "domain": "transportation",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_073",
        "difficulty": "medium",
        "subcategory": "wrong_entity_focus",
        "query": "Is the Samsung Galaxy S24 Ultra water resistant?",
        "contexts": [
            "The Samsung Galaxy S23 Ultra has an IP68 rating allowing submersion in 1.5m of freshwater for 30 minutes. It features Gorilla Glass Victus 2 on both panels and an Armor Aluminum frame for drop protection. Samsung recommends avoiding saltwater and chlorinated pool exposure."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about S24 Ultra but context provides S23 Ultra specs",
        "rationale": "LLM should note that S24 Ultra water resistance specs are not provided",
        "required_elements": ["S24", "S23", "not specified", "different", "not provided"],
        "forbidden_elements": ["S24 Ultra.{0,10}(is|has|features?|rated|IP)", "S24.{0,10}IP68"],
        "domain": "technology",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_074",
        "difficulty": "medium",
        "subcategory": "wrong_entity_focus",
        "query": "Which programs does Harvard Law School require for admission?",
        "contexts": [
            "Harvard Business School requires GMAT or GRE scores, two recommendation letters, transcripts, and a written essay. The average GMAT for admits is 730. Work experience averaging 5 years is typical. Application rounds close in September, January, and April.",
            "Harvard Business School's MBA has a 12% acceptance rate enrolling about 930 students per class. The two-year program includes a January-term field immersion."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about Harvard Law School but context is about Harvard Business School",
        "rationale": "LLM should note that Law School and Business School are different programs",
        "required_elements": ["Law School", "Business School", "not specified", "different", "not mentioned"],
        "forbidden_elements": ["Law School.{0,10}(requires?|admission|GMAT|GRE)", "Law School.{0,10}(accept|rate)"],
        "domain": "education",
        "query_type": "which",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "context_sources": [
            {"source_id": "src_relevance_074_a", "source_type": "report", "authority": "high"},
            {"source_id": "src_relevance_074_b", "source_type": "article", "authority": "medium"},
        ],
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_075",
        "difficulty": "medium",
        "subcategory": "wrong_entity_focus",
        "query": "Does the AstraZeneca COVID vaccine require cold storage?",
        "contexts": [
            "The Pfizer-BioNTech COVID-19 vaccine must be stored at -80C to -60C. It can stay refrigerated at 2C to 8C for up to 30 days. Once thawed, vials cannot be refrozen. The vaccine ships in special thermal containers with dry ice for ultra-cold transport."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about AstraZeneca vaccine but context covers Pfizer-BioNTech",
        "rationale": "LLM should recognize these are different vaccines with different storage needs",
        "required_elements": ["AstraZeneca", "Pfizer", "not specified", "different", "not mentioned"],
        "forbidden_elements": ["AstraZeneca.{0,15}(stored|requires?|needs?|temperature)", "AstraZeneca.{0,10}(-80|-60)"],
        "domain": "science",
        "query_type": "does",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    # =========================================================================
    # temporal_mismatch (5 cases): 076-080
    # =========================================================================
    {
        "id": "t1_relevance_medium_076",
        "difficulty": "medium",
        "subcategory": "temporal_mismatch",
        "query": "When did eurozone inflation peak in 2024?",
        "contexts": [
            "Eurozone inflation averaged 5.4% in 2023, driven by elevated energy and food prices. The ECB raised rates to 4.5%, the highest since the eurozone's creation. Core inflation peaked at 5.7% in March 2023 before falling to 3.4% by December 2023."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about 2024 inflation peak but context only has 2023 data",
        "rationale": "LLM should recognize the temporal gap and note 2024 data is absent",
        "required_elements": ["2024", "2023", "not specified", "not mentioned", "different"],
        "forbidden_elements": ["(in|during) 2024.{0,10}\\d+%", "2024 inflation.{0,10}(peaked|was|averaged)"],
        "domain": "finance",
        "query_type": "when",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_077",
        "difficulty": "medium",
        "subcategory": "temporal_mismatch",
        "query": "How many active users does Threads have in 2025?",
        "contexts": [
            "Meta's Threads launched in July 2023 gaining 100 million sign-ups in five days. By September 2023, monthly active users had fallen to about 10 million. New features like web access, search, and trending topics were added. By December 2023, monthly actives recovered to about 70 million."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about 2025 user count but context only covers through December 2023",
        "rationale": "LLM should note that 2025 user figures are not available in the context",
        "required_elements": ["2025", "not specified", "2023", "not mentioned", "not provided"],
        "forbidden_elements": ["(in|by) 2025.{0,10}\\d+\\s*(million|M|B)", "2025.{0,15}active users"],
        "domain": "social_media",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_078",
        "difficulty": "medium",
        "subcategory": "temporal_mismatch",
        "query": "When did the city last update its building codes for earthquake resistance?",
        "contexts": [
            "The city adopted seismic building codes in 2008 with zone classifications and foundation requirements. A 2012 amendment added soil liquefaction provisions. The building department processed 3,400 permits in 2023 and conducted 12,000 inspections with five new inspectors hired in 2022."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about the most recent earthquake code update, context shows 2008/2012 updates",
        "rationale": "LLM should note the last known update was 2012 but cannot confirm if more recent ones occurred",
        "required_elements": ["2008", "2012", "most recent", "update", "not clear"],
        "forbidden_elements": ["(updated|revised).{0,10}(2023|2024|recently)", "latest.{0,10}(2023|2024)"],
        "domain": "government",
        "query_type": "when",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_079",
        "difficulty": "medium",
        "subcategory": "temporal_mismatch",
        "query": "Is the current EV market share in Norway above 90%?",
        "contexts": [
            "In 2021, 64.5% of new car sales in Norway were fully electric. By 2022, the share rose to 79.3%, making Norway the global EV adoption leader. The government offered tax exemptions, free tolls, and bus lane access for EVs.",
            "Norway's charging network expanded to over 18,000 public points by end of 2022. Fast-chargers on major highways were spaced no more than 50 km apart. The country targeted ending fossil fuel car sales by 2025."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about current market share but context only has 2021-2022 data",
        "rationale": "LLM should note the most recent data is from 2022, not current",
        "required_elements": ["2022", "current", "not specified", "most recent", "not provided"],
        "forbidden_elements": ["(current|now|today|2025).{0,10}(share|market).{0,10}\\d+%", "(as of) (2024|2025).{0,10}\\d+%"],
        "domain": "transportation",
        "query_type": "is",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
        "context_sources": [
            {"source_id": "src_relevance_079_a", "source_type": "report", "authority": "high"},
            {"source_id": "src_relevance_079_b", "source_type": "article", "authority": "medium"},
        ],
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_080",
        "difficulty": "medium",
        "subcategory": "temporal_mismatch",
        "query": "Who won the 2024 Australian Open men's singles?",
        "contexts": [
            "The 2023 Australian Open final featured Djokovic vs Tsitsipas. Djokovic won in straight sets 6-3, 7-6, 7-6, claiming his 22nd Grand Slam and record-extending 10th Australian Open title. The tournament attracted over 900,000 spectators across two weeks."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about 2024 winner but context only covers 2023 tournament",
        "rationale": "LLM should note the 2024 Australian Open result is not provided",
        "required_elements": ["2024", "2023", "not specified", "not mentioned", "not provided"],
        "forbidden_elements": ["2024.{0,10}(won|winner|champion)", "(won|winner|champion).{0,10}2024"],
        "domain": "sports",
        "query_type": "who",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    # =========================================================================
    # tangent_drift (5 cases): 081-085
    # =========================================================================
    {
        "id": "t1_relevance_medium_081",
        "difficulty": "medium",
        "subcategory": "tangent_drift",
        "query": "How do I appeal a property tax assessment?",
        "contexts": [
            "Property taxes are calculated by multiplying assessed value by the local mill rate. Assessments are conducted annually or biennially. Factors include square footage, lot size, location, condition, and comparable sales. Some states cap annual increases at 2-3% to protect homeowners."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about appeal process but context explains how taxes are calculated",
        "rationale": "LLM should note that the appeal process itself is not described",
        "required_elements": ["appeal", "process", "not specified", "not mentioned", "not provided"],
        "forbidden_elements": ["(to appeal|file.{0,5}appeal|submit.{0,5}appeal).{0,15}(form|board)", "appeal.{0,10}(deadline|within)"],
        "domain": "real_estate",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "procedural",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_082",
        "difficulty": "medium",
        "subcategory": "tangent_drift",
        "query": "Why do cats purr?",
        "contexts": [
            "Cats communicate through meowing, chirping, trilling, hissing, and growling. Meowing is mainly for human communication, not between cats. Kittens meow to get their mother's attention, while adults reserve meows for humans.",
            "Feline body language includes tail position, ear orientation, and pupil dilation. A slow blink signals trust. Arched backs may indicate fear or aggression depending on context. Whisker position helps gauge mood: forward means curious, flat means defensive."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about purring specifically but context discusses other vocalizations and body language",
        "rationale": "LLM should note that purring is not addressed in the context",
        "required_elements": ["purr", "not mentioned", "not specified", "not provided"],
        "forbidden_elements": ["purr.{0,15}(because|caused by|due to)", "purr.{0,15}(healing|frequency|Hz|vibrat)"],
        "domain": "science",
        "query_type": "why",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "causal",
        "evidence_pattern": "absent",
        "context_sources": [
            {"source_id": "src_relevance_082_a", "source_type": "article", "authority": "medium"},
            {"source_id": "src_relevance_082_b", "source_type": "study", "authority": "high"},
        ],
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 4,
        },
    },
    {
        "id": "t1_relevance_medium_083",
        "difficulty": "medium",
        "subcategory": "tangent_drift",
        "query": "How should I prune tomato plants for maximum yield?",
        "contexts": [
            "Tomatoes thrive in well-drained, slightly acidic soil with pH 6.0-6.8. They need full sun of at least 6-8 hours daily. Consistent 1-2 inches of water weekly prevents blossom-end rot. Mulch helps retain moisture and regulate temperature. Companion planting with basil may improve flavor."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about pruning technique but context covers growing conditions",
        "rationale": "LLM should note that pruning techniques are not discussed",
        "required_elements": ["pruning", "not mentioned", "not specified", "not provided", "not covered"],
        "forbidden_elements": ["(prune|pruning|remove|pinch).{0,10}(sucker|branch|leaf)", "prune.{0,10}(above|below)"],
        "domain": "agriculture",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "procedural",
        "evidence_pattern": "absent",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_084",
        "difficulty": "medium",
        "subcategory": "tangent_drift",
        "query": "Is cognitive behavioral therapy effective for treating PTSD?",
        "contexts": [
            "CBT is widely recognized as evidence-based treatment for depression. Multiple RCTs demonstrate its efficacy in reducing depressive symptoms. Techniques include cognitive restructuring, behavioral activation, and journaling. Treatment spans 12-20 sessions and can be individual or group-based."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about CBT for PTSD but context discusses CBT for depression",
        "rationale": "LLM should note that CBT's effectiveness for PTSD specifically is not addressed",
        "required_elements": ["PTSD", "depression", "not specified", "different", "not mentioned"],
        "forbidden_elements": ["CBT.{0,10}(effective|proven|works).{0,10}PTSD", "PTSD.{0,10}(treated|reduced).{0,10}CBT"],
        "domain": "psychology",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "evaluative",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_085",
        "difficulty": "medium",
        "subcategory": "tangent_drift",
        "query": "Do whistleblower protections apply to private sector employees?",
        "contexts": [
            "Federal whistleblower protections are governed by the Whistleblower Protection Act of 1989. Federal employees reporting waste, fraud, or abuse are shielded from retaliation including termination and demotion. The Office of Special Counsel investigates retaliation claims.",
            "High-profile federal whistleblower cases have recovered billions in fraudulent government payments. The Inspector General system provides an additional reporting channel."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about private sector protections but context only covers federal employees",
        "rationale": "LLM should note the context discusses federal protections, not private sector",
        "required_elements": ["private sector", "federal", "government", "not specified", "different"],
        "forbidden_elements": ["private sector.{0,10}(protected|covered)", "private.{0,10}employees?.{0,10}protected"],
        "domain": "law",
        "query_type": "does",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
        "context_sources": [
            {"source_id": "src_relevance_085_a", "source_type": "legal_document", "authority": "high"},
            {"source_id": "src_relevance_085_b", "source_type": "article", "authority": "medium"},
        ],
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    # =========================================================================
    # related_but_different (5 cases): 086-090
    # =========================================================================
    {
        "id": "t1_relevance_medium_086",
        "difficulty": "medium",
        "subcategory": "related_but_different",
        "query": "How does composting reduce greenhouse gas emissions?",
        "contexts": [
            "Composting converts organic waste into nutrient-rich humus through aerobic decomposition. It requires green (nitrogen) and brown (carbon) materials in roughly 3:1 ratio. Regular turning promotes aeration and speeds the process.",
            "Finished compost improves soil structure, water retention, and provides slow-release nutrients. Municipal composting programs accept yard waste, food scraps, and paper products. Collection is typically weekly or biweekly depending on the jurisdiction."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about emissions reduction mechanism but context describes composting process",
        "rationale": "LLM should note the greenhouse gas reduction mechanism is not explained",
        "required_elements": ["greenhouse gas", "emissions", "not specified", "not mentioned", "reduction"],
        "forbidden_elements": ["(reduces?|lowers?).{0,10}(methane|CO2|greenhouse).{0,5}by \\d", "divert.{0,10}landfill"],
        "domain": "environment",
        "query_type": "how",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "causal",
        "evidence_pattern": "indirect",
        "context_sources": [
            {"source_id": "src_relevance_086_a", "source_type": "guide", "authority": "medium"},
            {"source_id": "src_relevance_086_b", "source_type": "article", "authority": "medium"},
        ],
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_087",
        "difficulty": "medium",
        "subcategory": "related_but_different",
        "query": "Should I use a Roth IRA or traditional IRA for retirement savings?",
        "contexts": [
            "A 401(k) lets employees defer up to $23,000 in 2024 ($30,500 for over 50). Employer matching up to 6% of salary is common. Plans offer target-date funds, index funds, and bonds. Contributions reduce your taxable income in the year they are made."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about Roth vs traditional IRA but context discusses 401(k) plans",
        "rationale": "LLM should note that IRA comparison is not provided, only 401(k) information",
        "required_elements": ["IRA", "401(k)", "not specified", "different", "not mentioned"],
        "forbidden_elements": ["Roth IRA.{0,10}(better|recommended|prefer)", "traditional IRA.{0,10}(better|recommended)"],
        "domain": "finance",
        "query_type": "should",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "evaluative",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_088",
        "difficulty": "medium",
        "subcategory": "related_but_different",
        "query": "How does acupuncture relieve chronic back pain?",
        "contexts": [
            "Physical therapy for chronic back pain includes core strengthening, flexibility stretches, and manual techniques like spinal mobilization. Evidence supports 8-12 week supervised exercise programs. Heat and cold therapy give symptomatic relief. Patient posture and ergonomics education is critical."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about acupuncture but context discusses physical therapy for back pain",
        "rationale": "LLM should note acupuncture is not discussed, only physical therapy",
        "required_elements": ["acupuncture", "physical therapy", "not specified", "different", "not mentioned"],
        "forbidden_elements": ["acupuncture.{0,10}(works|relieves?|helps?)", "needles?.{0,10}(stimulat|trigger|meridian)"],
        "domain": "medicine",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "causal",
        "evidence_pattern": "absent",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_089",
        "difficulty": "medium",
        "subcategory": "related_but_different",
        "query": "Is arbitration or mediation better for employment disputes?",
        "contexts": [
            "Employment litigation involves filing a court complaint, discovery with depositions and document requests, and trial before a judge or jury. Cases take 18-36 months to reach trial. Legal costs average $125,000 per case. Appeals extend the process by 1-2 years."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about arbitration vs mediation but context discusses litigation",
        "rationale": "LLM should note arbitration and mediation are not discussed, only litigation",
        "required_elements": ["arbitration", "mediation", "litigation", "not specified", "not mentioned"],
        "forbidden_elements": ["arbitration.{0,10}(is|involves?|binding)", "mediation.{0,10}(is|involves?|voluntary)"],
        "domain": "hr_workplace",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "comparative",
        "evidence_pattern": "absent",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_090",
        "difficulty": "medium",
        "subcategory": "related_but_different",
        "query": "How does drip irrigation improve crop water efficiency?",
        "contexts": [
            "Flood irrigation is one of the oldest crop watering methods. Water flows across the field by gravity. While simple and low-cost, efficiency is only 40-60%, with significant loss to evaporation, runoff, and deep percolation. It works best on flat terrain with clay soils that retain moisture."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about drip irrigation but context discusses flood irrigation",
        "rationale": "LLM should note drip irrigation is not addressed, only flood irrigation",
        "required_elements": ["drip irrigation", "flood irrigation", "not specified", "different", "not mentioned"],
        "forbidden_elements": ["drip irrigation.{0,10}(delivers?|achieves?|efficiency)", "drip.{0,10}(90|95|\\d+)%"],
        "domain": "agriculture",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "causal",
        "evidence_pattern": "absent",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    # =========================================================================
    # over_answering (5 cases): 091-095
    # =========================================================================
    {
        "id": "t1_relevance_medium_091",
        "difficulty": "medium",
        "subcategory": "over_answering",
        "query": "Does the restaurant offer gluten-free options?",
        "contexts": [
            "The Harvest Table features pasta, wood-fired pizzas, artisan breads, craft beers, and house-made desserts. The chef specializes in Italian-American cuisine with locally sourced ingredients. Seasonal specials rotate monthly and wine pairing dinners run every Thursday."
        ],
        "expected_mode": "trustworthy",
        "description": "Simple yes/no about gluten-free but context lists menu items without allergen info",
        "rationale": "LLM should note gluten-free availability is not mentioned rather than inferring from the menu",
        "required_elements": ["gluten-free", "not specified", "not mentioned", "not provided"],
        "forbidden_elements": ["(does|do) offer gluten.free", "gluten.free.{0,10}(available|option)", "yes.{0,15}gluten"],
        "domain": "food",
        "query_type": "does",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 4,
        },
    },
    {
        "id": "t1_relevance_medium_092",
        "difficulty": "medium",
        "subcategory": "over_answering",
        "query": "Is the apartment pet-friendly?",
        "contexts": [
            "The luxury apartment at 450 Park Avenue has 2 bed, 2 bath, a gourmet kitchen with granite countertops, in-unit washer/dryer, and a private balcony. Amenities include a rooftop pool, fitness center, concierge, and underground parking. Rent is $3,200/month with a 12-month lease."
        ],
        "expected_mode": "trustworthy",
        "description": "Simple yes/no about pet policy but context lists features without mentioning pets",
        "rationale": "LLM should note pet policy is not specified in the listing",
        "required_elements": ["pet", "not specified", "not mentioned", "policy", "not provided"],
        "forbidden_elements": ["(is|are) pet.friendly", "pets? (are )?allowed", "yes.{0,15}pet"],
        "domain": "real_estate",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_093",
        "difficulty": "medium",
        "subcategory": "over_answering",
        "query": "Does this company offer remote work options?",
        "contexts": [
            "TechVista Solutions has 450 employees in Austin, Boston, and Seattle. Benefits include health insurance, 401(k) matching up to 6%, unlimited PTO, and $2,000 professional development budgets. Glassdoor reviews rate the company 4.2/5 for work-life balance.",
            "TechVista completed a $50 million Series C round and plans to expand its product team by 30% next fiscal year. The company was founded in 2018 and focuses on enterprise data analytics."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about remote work but context describes benefits and company without mentioning remote policy",
        "rationale": "LLM should note that remote work policy is not addressed",
        "required_elements": ["remote", "not specified", "not mentioned", "work", "not provided"],
        "forbidden_elements": ["(offers?|provides?|allows?).{0,10}remote", "remote.{0,10}(available|option)", "yes.{0,15}remote"],
        "domain": "hr_workplace",
        "query_type": "does",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "context_sources": [
            {"source_id": "src_relevance_093_a", "source_type": "report", "authority": "medium"},
            {"source_id": "src_relevance_093_b", "source_type": "article", "authority": "medium"},
        ],
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_094",
        "difficulty": "medium",
        "subcategory": "over_answering",
        "query": "Is this hiking trail wheelchair accessible?",
        "contexts": [
            "The Pine Ridge Trail stretches 4.2 miles through old-growth forest with 1,100 feet of elevation gain. It has stream crossings, exposed root sections, and steep switchbacks in the final mile. Wildlife includes bears, deer, and birds. The trailhead gravel lot holds 25 vehicles."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about wheelchair accessibility but context describes terrain without addressing it",
        "rationale": "LLM should note accessibility is not explicitly addressed",
        "required_elements": ["wheelchair", "accessible", "not specified", "not mentioned"],
        "forbidden_elements": ["(is|are) (not )?wheelchair accessible", "wheelchair.{0,10}(friendly|suitable)", "ADA.{0,10}compliant"],
        "domain": "environment",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "evaluative",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 4,
        },
    },
    {
        "id": "t1_relevance_medium_095",
        "difficulty": "medium",
        "subcategory": "over_answering",
        "query": "Does this bootcamp offer job placement guarantees?",
        "contexts": [
            "CodeForge Academy is a 16-week intensive bootcamp covering JavaScript, React, Node.js, and SQL. Students complete 4 capstone projects and get portfolio reviews. The curriculum includes pair programming, code reviews, and agile workshops. Instructors average 12 years of experience. Classes cap at 20."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about job placement guarantees but context only describes curriculum",
        "rationale": "LLM should note that job placement guarantees are not mentioned",
        "required_elements": ["job placement", "guarantee", "not specified", "not mentioned", "not provided"],
        "forbidden_elements": ["(offers?|provides?|has).{0,10}(job placement|guarantee)", "\\d+%\\s*(placement|employment)"],
        "domain": "education",
        "query_type": "does",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    # =========================================================================
    # granularity_mismatch (4 cases): 096-099
    # =========================================================================
    {
        "id": "t1_relevance_medium_096",
        "difficulty": "medium",
        "subcategory": "granularity_mismatch",
        "query": "How does crime in the Westwood neighborhood compare to the city average?",
        "contexts": [
            "The city's overall crime rate fell 8% in 2024 versus the prior year. Total reported crimes were 14,200 across a population of 380,000. Violent crimes dropped 12% while property crimes fell 6%. Police attribute improvements to community policing and new surveillance at 150 intersections."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about neighborhood-level data but context provides city-wide statistics",
        "rationale": "LLM should note neighborhood-specific data for Westwood is not available",
        "required_elements": ["Westwood", "city-wide", "not specified", "neighborhood", "not provided"],
        "forbidden_elements": ["Westwood.{0,10}(crime|rate|per capita).{0,10}\\d", "neighborhood.{0,10}(rate|crime).{0,10}\\d"],
        "domain": "government",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_097",
        "difficulty": "medium",
        "subcategory": "granularity_mismatch",
        "query": "How much water does a single almond tree consume per year?",
        "contexts": [
            "California's almond industry uses about 3.4 million acre-feet of water yearly to irrigate 1.3 million acres. The industry yields about 3 billion pounds of almonds annually worth $6 billion. Drip irrigation covers roughly 80% of almond acreage, improving efficiency over flood methods."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about individual tree water usage but context provides industry-wide figures",
        "rationale": "LLM should note per-tree water consumption is not specified",
        "required_elements": ["single tree", "per tree", "not specified", "industry", "not provided"],
        "forbidden_elements": ["(each|single|per) tree.{0,10}(uses?|consumes?|needs?).{0,10}\\d", "\\d+\\s*gallons?.{0,5}per tree"],
        "domain": "agriculture",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_098",
        "difficulty": "medium",
        "subcategory": "granularity_mismatch",
        "query": "How much does a junior data scientist earn in Berlin specifically?",
        "contexts": [
            "Data scientists in Germany earn an average of EUR 65,000/year per 2024 surveys. Seniors earn up to EUR 95,000 and leads exceed EUR 110,000. The sector saw 15% salary growth over three years. Munich, Frankfurt, and Berlin are the top three cities for DS roles.",
            "Demand for data scientists grew 28% YoY in Germany with 4,500+ open listings. Automotive and finance sectors are the largest employers of data science talent in the country."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about junior-level in Berlin but context gives national averages without junior breakdown",
        "rationale": "LLM should note junior-specific and Berlin-specific salary data is not provided",
        "required_elements": ["junior", "Berlin", "not specified", "national", "not provided"],
        "forbidden_elements": ["junior.{0,15}(Berlin|salary).{0,10}(EUR|\\d)", "Berlin.{0,10}junior.{0,10}EUR"],
        "domain": "hr_workplace",
        "query_type": "how",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
        "context_sources": [
            {"source_id": "src_relevance_098_a", "source_type": "survey", "authority": "high"},
            {"source_id": "src_relevance_098_b", "source_type": "report", "authority": "medium"},
        ],
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_099",
        "difficulty": "medium",
        "subcategory": "granularity_mismatch",
        "query": "Which specific muscles does the Romanian deadlift target?",
        "contexts": [
            "Deadlift variations are among the most effective compound exercises for posterior chain strength. They engage multiple muscle groups simultaneously and are fundamental to strength programs. Proper form includes a neutral spine, core engagement, and driving through heels."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about specific muscles for Romanian deadlift but context discusses deadlifts generally",
        "rationale": "LLM should note specific muscle targeting for the Romanian variant is not detailed",
        "required_elements": ["Romanian deadlift", "specific muscles", "not specified", "not mentioned", "not provided"],
        "forbidden_elements": ["Romanian deadlift.{0,10}(targets?|works?).{0,10}(hamstring|glute)", "RDL.{0,10}(targets?|works?)"],
        "domain": "sports",
        "query_type": "which",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    # =========================================================================
    # prerequisite_missing (4 cases): 100-103
    # =========================================================================
    {
        "id": "t1_relevance_medium_100",
        "difficulty": "medium",
        "subcategory": "prerequisite_missing",
        "query": "How do I optimize my PostgreSQL query that is running slowly?",
        "contexts": [
            "PostgreSQL supports B-tree, Hash, GiST, SP-GiST, GIN, and BRIN index types. B-tree is default and most common, for equality and range queries. GIN indexes suit full-text search and JSONB. CREATE INDEX can run concurrently to avoid table locks."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks how to optimize a slow query but context gives general index overview",
        "rationale": "LLM should note that without the actual query and execution plan, optimization cannot be advised",
        "required_elements": ["query", "EXPLAIN", "execution plan", "not specified", "specific"],
        "forbidden_elements": ["add.{0,10}index on.{0,10}(your|the) (table|column)", "query.{0,10}optimized by.{0,10}(adding|creating)"],
        "domain": "technology",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "procedural",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_101",
        "difficulty": "medium",
        "subcategory": "prerequisite_missing",
        "query": "Should I take ibuprofen or acetaminophen for my pain?",
        "contexts": [
            "Ibuprofen is an NSAID that reduces pain, fever, and inflammation by inhibiting COX enzymes. Side effects include stomach upset and increased bleeding risk. Acetaminophen reduces pain and fever but not inflammation. It is liver-processed and should be avoided with alcohol."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for a recommendation but context provides general drug info without patient details",
        "rationale": "LLM should note that without pain type, history, and other meds, a recommendation cannot be made",
        "required_elements": ["type of pain", "medical", "condition", "not specified", "depends"],
        "forbidden_elements": ["(take|use|choose).{0,10}(ibuprofen|acetaminophen)", "(ibuprofen|acetaminophen) (is|would be) (better|best)"],
        "domain": "medicine",
        "query_type": "should",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "evaluative",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_102",
        "difficulty": "medium",
        "subcategory": "prerequisite_missing",
        "query": "How much will my property taxes increase if I add a home addition?",
        "contexts": [
            "Property taxes equal assessed value times the local mill rate. Reassessment occurs on ownership change or major improvements. Assessed value reflects square footage, rooms, materials, and comparable sales. Tax rates vary by jurisdiction.",
            "Additions typically raise assessed value proportional to added square footage and construction quality. Permits are required for structural additions and trigger a county reassessment."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for a specific tax increase but context explains the process without knowing details",
        "rationale": "LLM should note that without addition size, location, and current assessment, the increase cannot be calculated",
        "required_elements": ["specific", "size", "location", "current", "not provided", "depends"],
        "forbidden_elements": ["taxes? will increase.{0,5}\\$\\d", "increase.{0,10}\\d+%", "expect.{0,10}\\$\\d"],
        "domain": "real_estate",
        "query_type": "how",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "analytical",
        "evidence_pattern": "indirect",
        "context_sources": [
            {"source_id": "src_relevance_102_a", "source_type": "guide", "authority": "high"},
            {"source_id": "src_relevance_102_b", "source_type": "article", "authority": "medium"},
        ],
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 6,
        },
    },
    {
        "id": "t1_relevance_medium_103",
        "difficulty": "medium",
        "subcategory": "prerequisite_missing",
        "query": "Is this contract clause enforceable?",
        "contexts": [
            "Contract enforceability depends on mutual assent, consideration, party capacity, and legality. Unconscionable clauses may be voided. Non-competes face varying scrutiny by jurisdiction, with California generally refusing to enforce them. The UCC governs sale-of-goods contracts."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about a specific clause but context gives general enforceability principles",
        "rationale": "LLM should note that without the clause text, jurisdiction, and context, enforceability is undetermined",
        "required_elements": ["specific clause", "jurisdiction", "not specified", "depends", "not provided"],
        "forbidden_elements": ["(is|would be) (not )?(enforceable|valid)", "clause.{0,10}(is|would be).{0,10}(enforceable|void)"],
        "domain": "law",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "evaluative",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    # =========================================================================
    # scope_mismatch (4 cases): 104-107
    # =========================================================================
    {
        "id": "t1_relevance_medium_104",
        "difficulty": "medium",
        "subcategory": "scope_mismatch",
        "query": "How does yoga benefit cardiovascular health specifically?",
        "contexts": [
            "Yoga combines physical postures, breathing, and meditation. It improves flexibility, strengthens muscles, reduces stress, and promotes mindfulness. Styles include Hatha, Vinyasa, Bikram, and Yin. Regular practice is linked to better mental health, sleep quality, and lower anxiety."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks specifically about cardiovascular benefits but context covers general yoga benefits",
        "rationale": "LLM should note cardiovascular-specific benefits are not discussed",
        "required_elements": ["cardiovascular", "not specified", "not mentioned", "heart", "not provided"],
        "forbidden_elements": ["yoga.{0,10}(reduces?|lowers?|improves?).{0,10}(blood pressure|heart rate)", "cardiovascular.{0,10}(benefit|improve)"],
        "domain": "sports",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "causal",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_105",
        "difficulty": "medium",
        "subcategory": "scope_mismatch",
        "query": "Which regulations govern offshore oil drilling in the Gulf of Mexico?",
        "contexts": [
            "Onshore oil and gas regulations require well casing integrity, produced water disposal, emissions monitoring, and site remediation. The EPA oversees compliance through inspections. Operators must file Environmental Impact Statements for new federal land sites. Penalties reach $50,000 per day per violation."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about offshore regulations but context covers onshore only",
        "rationale": "LLM should note offshore drilling regulations differ from onshore and are not addressed",
        "required_elements": ["offshore", "onshore", "not specified", "different", "not mentioned"],
        "forbidden_elements": ["offshore.{0,10}(regulations?|rules?).{0,10}(include|require)", "Gulf of Mexico.{0,10}regulations?"],
        "domain": "environment",
        "query_type": "which",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_106",
        "difficulty": "medium",
        "subcategory": "scope_mismatch",
        "query": "Which liquids rules apply to international flights?",
        "contexts": [
            "TSA domestic flight rules limit carry-on liquids to 3.4 oz (100 ml) containers fitting in a quart-sized clear bag. Exceptions include medications, baby formula, and breast milk in reasonable quantities. These must be declared at the checkpoint. Checked luggage has no liquid restrictions."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about international flight rules but context covers domestic US TSA only",
        "rationale": "LLM should note that international flight regulations may differ from domestic TSA rules",
        "required_elements": ["international", "domestic", "not specified", "different", "TSA"],
        "forbidden_elements": ["international flights?.{0,10}(same|also|follow).{0,10}TSA", "international.{0,10}(limit|rule).{0,10}(is|are)"],
        "domain": "transportation",
        "query_type": "which",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_107",
        "difficulty": "medium",
        "subcategory": "scope_mismatch",
        "query": "How does the Roman Empire's tax system compare to modern taxation?",
        "contexts": [
            "Rome employed the tributum (direct tax), portoria (customs), and centesima rerum venalium (1% sales tax). Collection was outsourced to publicani who bid for regional tax rights. Diocletian reformed the system with direct collection and standardized assessments across provinces."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for comparison with modern taxation but context only describes Roman system",
        "rationale": "LLM should note a comparison to modern systems is not provided",
        "required_elements": ["modern", "comparison", "not specified", "not mentioned", "not provided"],
        "forbidden_elements": ["(similar|comparable|different).{0,10}(modern|today) tax", "modern.{0,10}(equivalent|version)"],
        "domain": "history",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "comparative",
        "evidence_pattern": "partial",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    # =========================================================================
    # format_mismatch (3 cases): 108-110
    # =========================================================================
    {
        "id": "t1_relevance_medium_108",
        "difficulty": "medium",
        "subcategory": "format_mismatch",
        "query": "How do I set up a home network step by step?",
        "contexts": [
            "Home networking connects devices via a router. Wi-Fi 6 (802.11ax) offers speeds up to 9.6 Gbps and better congested-environment performance. Mesh systems extend coverage using multiple access points. Security should include WPA3 encryption, strong passwords, and regular firmware updates."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for step-by-step instructions but context provides overview information",
        "rationale": "LLM should note step-by-step setup instructions are not provided",
        "required_elements": ["step-by-step", "instructions", "not provided", "guide", "not specified"],
        "forbidden_elements": ["step 1.{0,15}(connect|plug|set up|configure)", "first.{0,10}(connect|plug|install)"],
        "domain": "technology",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "procedural",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_109",
        "difficulty": "medium",
        "subcategory": "format_mismatch",
        "query": "How do I make authentic Italian carbonara with exact measurements?",
        "contexts": [
            "Carbonara is a traditional Roman pasta from Lazio, likely created mid-20th century. Possibly influenced by American GIs during WWII. Authentic versions use guanciale not pancetta, and Pecorino Romano not Parmesan. Cream is never used in authentic carbonara.",
            "The silky sauce comes from proper emulsification of eggs, cheese, and pasta water. The dish is typically served with spaghetti or rigatoni and topped with freshly cracked black pepper."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for recipe with measurements but context provides history and ingredient notes",
        "rationale": "LLM should note actual recipe instructions with measurements are not provided",
        "required_elements": ["recipe", "measurements", "instructions", "not provided", "not specified"],
        "forbidden_elements": ["\\d+\\s*(grams?|oz|cups?|tbsp|tsp|g\\b)", "(cook|boil|fry|mix).{0,10}\\d+\\s*min"],
        "domain": "food",
        "query_type": "how",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "procedural",
        "evidence_pattern": "indirect",
        "context_sources": [
            {"source_id": "src_relevance_109_a", "source_type": "article", "authority": "medium"},
            {"source_id": "src_relevance_109_b", "source_type": "guide", "authority": "high"},
        ],
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_110",
        "difficulty": "medium",
        "subcategory": "format_mismatch",
        "query": "How do the top 5 project management tools compare feature by feature?",
        "contexts": [
            "Project management tools help teams organize tasks, track progress, and collaborate. Popular options include Asana, Trello, Jira, Monday.com, and ClickUp. They generally offer kanban boards, Gantt charts, time tracking, and integrations. The market was valued at $5.37 billion in 2023."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for structured comparison but context gives general overview",
        "rationale": "LLM should note a detailed feature-by-feature comparison is not available",
        "required_elements": ["comparison", "feature", "not provided", "not specified", "detailed"],
        "forbidden_elements": ["\\|.*\\|.*\\|", "(Asana|Trello|Jira).{0,5}(vs|compared to|versus)"],
        "domain": "general",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "comparative",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    # =========================================================================
    # summarization_vs_answer (3 cases): 111-113
    # =========================================================================
    {
        "id": "t1_relevance_medium_111",
        "difficulty": "medium",
        "subcategory": "summarization_vs_answer",
        "query": "Why did the French Revolution begin?",
        "contexts": [
            "The French Revolution (1789-1799) was a period of radical political change. Key events include storming the Bastille, the Declaration of the Rights of Man, the Reign of Terror under Robespierre, and Napoleon's rise. It abolished feudalism, established a republic, and influenced global democratic movements."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks why the Revolution began but context summarizes events and outcomes",
        "rationale": "LLM should note the causes/reasons for the Revolution are not explained",
        "required_elements": ["causes", "reasons", "why", "not specified", "not mentioned"],
        "forbidden_elements": ["(began|started|caused).{0,10}(because|due to).{0,10}(financial|famine|inequality)", "cause.{0,10}(was|were|included)"],
        "domain": "history",
        "query_type": "why",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "causal",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_112",
        "difficulty": "medium",
        "subcategory": "summarization_vs_answer",
        "query": "Why should companies adopt sustainable supply chain practices?",
        "contexts": [
            "Sustainable supply chain management integrates environmental and social factors into procurement, production, and distribution. Patagonia, Unilever, and IKEA have programs. Practices include recycled materials, lower emissions, fair labor, and supplier audits.",
            "The global sustainable supply chain market hit $27.3 billion in 2023. Key frameworks include ISO 14001, the GRI, and the UN Sustainable Development Goals."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks why companies should adopt but context describes what the practices are",
        "rationale": "LLM should note the business case or benefits of adoption are not explicitly stated",
        "required_elements": ["benefits", "why", "reasons", "not specified", "not mentioned"],
        "forbidden_elements": ["(should|adopt because|reason).{0,10}(cost savings?|reputation|risk)", "(benefit|advantage).{0,5}(is|are|include).{0,10}(cost|revenue)"],
        "domain": "general",
        "query_type": "why",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "evaluative",
        "evidence_pattern": "indirect",
        "context_sources": [
            {"source_id": "src_relevance_112_a", "source_type": "report", "authority": "high"},
            {"source_id": "src_relevance_112_b", "source_type": "study", "authority": "medium"},
        ],
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_113",
        "difficulty": "medium",
        "subcategory": "summarization_vs_answer",
        "query": "Why is sleep important for cognitive function?",
        "contexts": [
            "Adults need 7-9 hours of sleep per the National Sleep Foundation. Sleep cycles through ~90-minute NREM/REM stages. Deep NREM sleep is the most restorative. REM features rapid eye movement and vivid dreams. Quality is affected by caffeine, screens, temperature, and exercise timing."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks why sleep matters for cognition but context describes sleep mechanics",
        "rationale": "LLM should note cognitive benefits/mechanisms are not explained",
        "required_elements": ["cognitive", "function", "not specified", "not mentioned", "why"],
        "forbidden_elements": ["sleep.{0,10}(improves?|enhances?|boosts?).{0,10}(memory|learning|cognition)", "(memory|learning).{0,10}consolidat.{0,10}during sleep"],
        "domain": "psychology",
        "query_type": "why",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "causal",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    # =========================================================================
    # cherry_picking (3 cases): 114-116
    # =========================================================================
    {
        "id": "t1_relevance_medium_114",
        "difficulty": "medium",
        "subcategory": "cherry_picking",
        "query": "Is remote work more productive than office work?",
        "contexts": [
            "A Stanford study of 16,000 workers found remote employees were 13% more productive. They took fewer breaks and sick days and had higher satisfaction. However, promotion rates for remote workers were 50% lower than in-office employees.",
            "Microsoft's analysis of 61,000 employees found remote work cut cross-team collaboration by 25% and increased siloed communication. Innovation metrics fell 16% during fully remote periods."
        ],
        "expected_mode": "trustworthy",
        "description": "Context presents mixed evidence, answer could cherry-pick only the positive study",
        "rationale": "LLM should present findings from all sources, noting conflicting evidence",
        "required_elements": ["mixed", "both", "Stanford", "Microsoft", "trade-off"],
        "forbidden_elements": ["(yes|definitively|clearly).{0,10}(more productive|better)", "(no|definitively).{0,10}(less productive|worse)"],
        "domain": "hr_workplace",
        "query_type": "is",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "evaluative",
        "evidence_pattern": "contradictory",
        "context_sources": [
            {"source_id": "src_relevance_114_a", "source_type": "study", "authority": "high"},
            {"source_id": "src_relevance_114_b", "source_type": "study", "authority": "high"},
        ],
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_115",
        "difficulty": "medium",
        "subcategory": "cherry_picking",
        "query": "Is organic farming better for the environment?",
        "contexts": [
            "Organic farming eliminates synthetic pesticides, reducing runoff and soil contamination. Organic fields show 30% higher biodiversity than conventional farms according to a 2022 meta-analysis of 85 studies.",
            "However, organic yields are typically 20-25% lower than conventional, requiring more land for equal output. A 2023 study found organic produces 20% more GHG emissions per unit of food produced due to lower yields and greater land use requirements."
        ],
        "expected_mode": "trustworthy",
        "description": "Context presents both environmental benefits and drawbacks",
        "rationale": "LLM should present both sides rather than cherry-picking",
        "required_elements": ["benefits", "drawbacks", "trade-off", "mixed", "yields"],
        "forbidden_elements": ["organic.{0,10}(is|clearly) (better|worse) for", "(yes|no).{0,10}organic.{0,10}(better|worse)"],
        "domain": "agriculture",
        "query_type": "is",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "evaluative",
        "evidence_pattern": "contradictory",
        "context_sources": [
            {"source_id": "src_relevance_115_a", "source_type": "study", "authority": "high"},
            {"source_id": "src_relevance_115_b", "source_type": "study", "authority": "high"},
        ],
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_116",
        "difficulty": "medium",
        "subcategory": "cherry_picking",
        "query": "Should cities invest in light rail transit?",
        "contexts": [
            "Light rail revitalized districts in Portland, Denver, and Charlotte, raising property values 10-25% near stations. Daily ridership averages 15-30K trips. But construction costs $100-250M/mile and many systems miss ridership targets. Operating subsidies are needed nearly everywhere.",
            "Bus rapid transit provides comparable service at 10-30% of light rail cost. Some cities that built rail cut bus service to fund it, hurting lower-income riders who rely on buses."
        ],
        "expected_mode": "trustworthy",
        "description": "Context presents benefits and significant costs/trade-offs",
        "rationale": "LLM should present the full picture including costs, alternatives, and trade-offs",
        "required_elements": ["costs", "benefits", "trade-off", "BRT", "subsid"],
        "forbidden_elements": ["(yes|should|definitely).{0,10}invest in light rail", "(no|should not).{0,10}invest in light rail"],
        "domain": "transportation",
        "query_type": "should",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "evaluative",
        "evidence_pattern": "contradictory",
        "context_sources": [
            {"source_id": "src_relevance_116_a", "source_type": "report", "authority": "high"},
            {"source_id": "src_relevance_116_b", "source_type": "study", "authority": "medium"},
        ],
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    # =========================================================================
    # false_precision (3 cases): 117-119
    # =========================================================================
    {
        "id": "t1_relevance_medium_117",
        "difficulty": "medium",
        "subcategory": "false_precision",
        "query": "What percentage of startups fail in the first five years?",
        "contexts": [
            "Starting a business involves significant risk. Entrepreneurs often underestimate cash flow, competition, and hiring challenges. The SBA provides loans and mentorship. VC funding reached $170 billion in 2023.",
            "Accelerator programs such as Y Combinator and Techstars help early-stage companies refine their business models. Angel investor networks provide seed funding typically ranging from $25,000 to $500,000 per investment round."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for specific failure percentage but context discusses ecosystem without statistics",
        "rationale": "LLM should note failure rate statistics are not provided",
        "required_elements": ["failure rate", "percentage", "not specified", "not mentioned", "not provided"],
        "forbidden_elements": ["\\d+%\\s*(of )?(startups?|businesses?) fail", "(fail|failure) rate.{0,10}(is|of) \\d+%"],
        "domain": "finance",
        "query_type": "what",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "context_sources": [
            {"source_id": "src_relevance_117_a", "source_type": "report", "authority": "high"},
            {"source_id": "src_relevance_117_b", "source_type": "article", "authority": "medium"},
        ],
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_118",
        "difficulty": "medium",
        "subcategory": "false_precision",
        "query": "How many calories does 30 minutes of swimming burn?",
        "contexts": [
            "Swimming is an excellent full-body workout engaging multiple muscle groups. It is low-impact and suitable for joint issues. Freestyle works shoulders and core, backstroke targets back, breaststroke targets thighs and chest. Water resistance provides natural strength training."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for specific calorie count but context describes benefits without calorie data",
        "rationale": "LLM should note calorie burn data is not provided",
        "required_elements": ["calories", "not specified", "not mentioned", "burn", "not provided"],
        "forbidden_elements": ["burns? (approximately )?\\d+ calories", "\\d+\\s*calories?.{0,10}(per|in|for) (30|half)"],
        "domain": "sports",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_119",
        "difficulty": "medium",
        "subcategory": "false_precision",
        "query": "What is the exact population of Tokyo?",
        "contexts": [
            "Tokyo is Japan's capital and largest city, the political, economic, and cultural center. The metro area is one of the world's most densely populated. Tokyo hosted the 2020 Olympics (held 2021). It has an extensive transit network with bullet train links. Tokyo's GDP exceeds many countries."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for exact population but context describes Tokyo without numbers",
        "rationale": "LLM should note a specific population figure is not provided",
        "required_elements": ["population", "not specified", "not mentioned", "number", "not provided"],
        "forbidden_elements": ["population.{0,10}(is|of|approximately) \\d", "\\d+\\.?\\d*\\s*(million|billion)", "Tokyo.{0,10}(has|population).{0,10}\\d"],
        "domain": "general",
        "query_type": "what",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    # =========================================================================
    # assumption_injection (2 cases): 120-121
    # =========================================================================
    {
        "id": "t1_relevance_medium_120",
        "difficulty": "medium",
        "subcategory": "assumption_injection",
        "query": "Why is the company's stock price declining?",
        "contexts": [
            "The company reported Q3 2024 revenue of $2.1 billion, up 5% YoY. Operating margins expanded to 18.3% from 16.7%. A new product line launches Q1 2025. Headcount grew by 200 to 4,500. The board authorized a $500 million share buyback."
        ],
        "expected_mode": "trustworthy",
        "description": "Question assumes stock is declining but context shows positive financials",
        "rationale": "LLM should note the context does not indicate a stock decline and the premise may be wrong",
        "required_elements": ["stock price", "decline", "not mentioned", "not specified", "assumption"],
        "forbidden_elements": ["stock.{0,5}declining because", "decline.{0,10}(due to|caused by|result of)"],
        "domain": "finance",
        "query_type": "why",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "causal",
        "evidence_pattern": "absent",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_121",
        "difficulty": "medium",
        "subcategory": "assumption_injection",
        "query": "Why are students performing worse on standardized tests this year?",
        "contexts": [
            "The state released 2024 test results: math average 285/500, reading 292/500. 145,000 students across 380 schools participated. Tests ran March-April, results certified July. A new digital platform was used for the first time.",
            "The digital platform had 97% uptime during the testing window. Testing accommodations were provided to 12,400 students with documented needs across the state. Technical support staff were available at every testing site."
        ],
        "expected_mode": "trustworthy",
        "description": "Assumes worse performance but context has scores without year-over-year comparison",
        "rationale": "LLM should note the premise of declining performance is unsupported by context",
        "required_elements": ["assumption", "worse", "comparison", "not specified", "previous"],
        "forbidden_elements": ["(students?|scores?) (are|have been) (declining|worse) because", "performing worse.{0,10}(due to|because)"],
        "domain": "education",
        "query_type": "why",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "causal",
        "evidence_pattern": "indirect",
        "context_sources": [
            {"source_id": "src_relevance_121_a", "source_type": "report", "authority": "high"},
            {"source_id": "src_relevance_121_b", "source_type": "report", "authority": "medium"},
        ],
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    # =========================================================================
    # symptom_only (2 cases): 122-123
    # =========================================================================
    {
        "id": "t1_relevance_medium_122",
        "difficulty": "medium",
        "subcategory": "symptom_only",
        "query": "Why is my car making a grinding noise when braking?",
        "contexts": [
            "Brake system components include pads, rotors, calipers, fluid, and lines. Pads wear over time and need inspection every 25,000-50,000 miles. Rotors can warp from heat, causing pulsation. Brake fluid absorbs moisture and should be replaced every 2-3 years."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for diagnosis but context lists components and maintenance schedules",
        "rationale": "LLM should note diagnosis requires inspection and context only provides general info",
        "required_elements": ["grinding", "diagnosis", "inspect", "not specified", "multiple causes"],
        "forbidden_elements": ["grinding.{0,10}(means?|caused by).{0,10}(worn|bad)", "(your|the) (pads?|rotors?) (are|need)"],
        "domain": "transportation",
        "query_type": "why",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "causal",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_123",
        "difficulty": "medium",
        "subcategory": "symptom_only",
        "query": "Why are my tomato plant leaves turning yellow?",
        "contexts": [
            "Tomato leaf discoloration can result from nutrient deficiency (nitrogen, iron, magnesium), overwatering, underwatering, root rot, viral infections, or blight fungus. Soil pH outside 6.0-6.8 impairs uptake. Temperature stress from cold snaps or heat above 95F also affects foliage."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for a specific cause but context lists many possible causes",
        "rationale": "LLM should present the range of causes and note diagnosis needs more information",
        "required_elements": ["multiple", "possible causes", "diagnos", "not specified", "depends"],
        "forbidden_elements": ["(your|the) plant.{0,10}(is|has|needs?).{0,10}(nitrogen|water)", "yellow.{0,10}(means?|caused by)\\s+(nitrogen|water)"],
        "domain": "agriculture",
        "query_type": "why",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "causal",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    # =========================================================================
    # status_dump (2 cases): 124-125
    # =========================================================================
    {
        "id": "t1_relevance_medium_124",
        "difficulty": "medium",
        "subcategory": "status_dump",
        "query": "What is the ROI of the company's social media marketing campaigns?",
        "contexts": [
            "The marketing team posted 340 social updates last quarter on Instagram, Twitter, and LinkedIn. Instagram followers grew 15K to 89K. Twitter engagement averaged 2.3%. They attended 4 conferences, sponsored 2 charities, and published 3 weekly blog posts averaging 1,200 views each."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for ROI but context provides activity metrics without financial return data",
        "rationale": "LLM should note ROI (financial return) is not provided, only activity metrics",
        "required_elements": ["ROI", "return", "investment", "not specified", "not provided"],
        "forbidden_elements": ["ROI (is|was|of) \\d", "return.{0,10}(is|was) \\d+%", "\\$\\d.{0,10}(return|revenue)"],
        "domain": "social_media",
        "query_type": "what",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_125",
        "difficulty": "medium",
        "subcategory": "status_dump",
        "query": "What are the patient outcome rates for the new surgical technique?",
        "contexts": [
            "The surgery department did 2,400 robotic-assisted procedures last year. Six surgeons were hired and trained 120 hours each. Equipment cost $3.2M. ORs were renovated for robotic systems. Insurance approval climbed from 60% to 85%.",
            "The robotic program received ACS accreditation. Marketing materials highlight advanced technology available to patients at the facility and have increased inbound referrals."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about patient outcomes but context reports operational metrics",
        "rationale": "LLM should note patient outcome data is not provided",
        "required_elements": ["outcome", "patient", "not specified", "success rate", "not provided"],
        "forbidden_elements": ["outcome rate.{0,10}(is|was) \\d", "\\d+%\\s*(success|survival|complication)", "patients?.{0,10}recovered.{0,10}\\d"],
        "domain": "medicine",
        "query_type": "what",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
        "context_sources": [
            {"source_id": "src_relevance_125_a", "source_type": "report", "authority": "high"},
            {"source_id": "src_relevance_125_b", "source_type": "article", "authority": "medium"},
        ],
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    # =========================================================================
    # feature_dump (2 cases): 126-127
    # =========================================================================
    {
        "id": "t1_relevance_medium_126",
        "difficulty": "medium",
        "subcategory": "feature_dump",
        "query": "How much does Salesforce CRM cost for a small business?",
        "contexts": [
            "Salesforce CRM offers contact management, opportunity tracking, email integration, dashboards, workflow automation, and AI analytics. It has 3,000+ AppExchange integrations. Mobile access on iOS and Android. Enterprise features include advanced reporting and API access."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about pricing but context only lists features",
        "rationale": "LLM should note pricing information is not provided",
        "required_elements": ["pricing", "cost", "not specified", "not mentioned", "not provided"],
        "forbidden_elements": ["\\$\\d+\\s*(per|/)(month|user|seat|year)", "costs?\\s+\\$\\d", "(starting|begins?) at \\$"],
        "domain": "technology",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    {
        "id": "t1_relevance_medium_127",
        "difficulty": "medium",
        "subcategory": "feature_dump",
        "query": "When does the Bose QuietComfort Ultra battery need recharging?",
        "contexts": [
            "The Bose QuietComfort Ultra headphones feature world-class noise cancellation with Aware Mode. They include Bluetooth 5.3, multipoint connection for two devices, Immersive Audio spatial sound, and USB-C charging. Protein leather cushions ensure comfort. They fold flat with a premium case."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about battery life but context lists features without battery info",
        "rationale": "LLM should note battery life specs are not provided",
        "required_elements": ["battery life", "not specified", "not mentioned", "hours", "not provided"],
        "forbidden_elements": ["battery (life|lasts?).{0,10}\\d+\\s*hours?", "\\d+.{0,5}hours? (of )?(battery|playback)", "(lasts?|provides?).{0,10}\\d+\\s*hours?"],
        "domain": "general",
        "query_type": "when",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    # =========================================================================
    # instruction_only (1 case): 128
    # =========================================================================
    {
        "id": "t1_relevance_medium_128",
        "difficulty": "medium",
        "subcategory": "instruction_only",
        "query": "What are the potential complications of LASIK eye surgery?",
        "contexts": [
            "LASIK prep involves an eye exam, stopping contacts 2 weeks before, and arranging post-op transport. Numbing drops are applied, a corneal flap is created with a femtosecond laser, and the cornea is reshaped with an excimer laser. The procedure takes about 15 minutes per eye."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about complications/risks but context describes procedure steps only",
        "rationale": "LLM should note potential complications and risks are not discussed",
        "required_elements": ["complications", "risks", "not specified", "not mentioned", "not provided"],
        "forbidden_elements": ["complications?.{0,10}(include|such as).{0,10}(dry eye|halos?|infection)", "(risk|complication).{0,10}(of|include).{0,10}\\d+%"],
        "domain": "medicine",
        "query_type": "what",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
    # =========================================================================
    # metric_avoidance (1 case): 129
    # =========================================================================
    {
        "id": "t1_relevance_medium_129",
        "difficulty": "medium",
        "subcategory": "metric_avoidance",
        "query": "When does the fire department typically arrive after a 911 call?",
        "contexts": [
            "The city fire department runs 12 stations across the metro area with 340 firefighters on rotating 24-hour shifts. Equipment includes 15 engines, 5 ladder companies, and 3 hazmat units. They handled 8,200 calls last year. A new training facility opened in 2023.",
            "Community outreach includes school fire safety talks, CPR workshops, and annual station open houses. The department holds an ISO Class 2 rating, among the top in the state."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for response time metrics but context describes operations without time data",
        "rationale": "LLM should note average response time figures are not provided",
        "required_elements": ["response time", "not specified", "not mentioned", "minutes", "not provided"],
        "forbidden_elements": ["response time.{0,10}(is|of|at) \\d", "\\d+\\.?\\d*\\s*(minutes?|min).{0,10}response"],
        "domain": "government",
        "query_type": "when",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "context_sources": [
            {"source_id": "src_relevance_129_a", "source_type": "report", "authority": "high"},
            {"source_id": "src_relevance_129_b", "source_type": "article", "authority": "medium"},
        ],
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 5,
        },
    },
]
# fmt: on


def main() -> None:
    # --- sanity checks ---
    assert len(NEW_CASES) == 65, f"Expected 65 cases, got {len(NEW_CASES)}"

    ids = [c["id"] for c in NEW_CASES]
    assert len(ids) == len(set(ids)), "Duplicate IDs found"

    expected_start = 65
    expected_end = 129
    for i, c in enumerate(NEW_CASES):
        expected_id = f"t1_relevance_medium_{expected_start + i:03d}"
        assert c["id"] == expected_id, f"Expected {expected_id}, got {c['id']}"

    # Verify all cases have required_elements and forbidden_elements
    for c in NEW_CASES:
        assert "required_elements" in c, f"{c['id']} missing required_elements"
        assert "forbidden_elements" in c, f"{c['id']} missing forbidden_elements"
        assert len(c["required_elements"]) >= 3, f"{c['id']} needs >= 3 required_elements"
        assert len(c["forbidden_elements"]) >= 2, f"{c['id']} needs >= 2 forbidden_elements"
        assert c["evaluation_config"]["min_required"] == len(c["required_elements"]), (
            f"{c['id']} min_required ({c['evaluation_config']['min_required']}) != "
            f"len(required_elements) ({len(c['required_elements'])})"
        )

    # Verify subcategory distribution
    from collections import Counter

    subcat_counts = Counter(c["subcategory"] for c in NEW_CASES)
    expected_subcats = {
        "partial_answer": 6,
        "wrong_entity_focus": 5,
        "temporal_mismatch": 5,
        "tangent_drift": 5,
        "related_but_different": 5,
        "over_answering": 5,
        "granularity_mismatch": 4,
        "prerequisite_missing": 4,
        "scope_mismatch": 4,
        "format_mismatch": 3,
        "summarization_vs_answer": 3,
        "cherry_picking": 3,
        "false_precision": 3,
        "assumption_injection": 2,
        "symptom_only": 2,
        "status_dump": 2,
        "feature_dump": 2,
        "instruction_only": 1,
        "metric_avoidance": 1,
    }
    for subcat, expected_count in expected_subcats.items():
        actual = subcat_counts.get(subcat, 0)
        assert actual == expected_count, f"{subcat}: expected {expected_count}, got {actual}"

    # Verify multi-source count
    multi_source = [c for c in NEW_CASES if c["source_type"] == "multi_source"]
    assert len(multi_source) == 18, f"Expected 18 multi_source, got {len(multi_source)}"
    for c in multi_source:
        assert "context_sources" in c, f"{c['id']} is multi_source but missing context_sources"

    # Verify domain spread
    domain_counts = Counter(c["domain"] for c in NEW_CASES)
    for domain, count in domain_counts.items():
        assert count <= 5, f"Domain {domain} has {count} cases (max 5)"

    all_18_domains = {
        "agriculture", "education", "environment", "finance", "food",
        "general", "government", "history", "hr_workplace", "law",
        "medicine", "psychology", "real_estate", "science",
        "social_media", "sports", "technology", "transportation",
    }
    assert set(domain_counts.keys()).issubset(all_18_domains), (
        f"Unknown domains: {set(domain_counts.keys()) - all_18_domains}"
    )
    assert len(domain_counts) == 18, f"Expected all 18 domains, got {len(domain_counts)}"

    # Verify query type distribution
    qt_counts = Counter(c["query_type"] for c in NEW_CASES)
    what_count = qt_counts.get("what", 0)
    how_count = qt_counts.get("how", 0)
    is_does_count = qt_counts.get("is", 0) + qt_counts.get("does", 0)
    why_should_count = qt_counts.get("why", 0) + qt_counts.get("should", 0)
    when_who_which_count = qt_counts.get("when", 0) + qt_counts.get("who", 0) + qt_counts.get("which", 0)

    assert what_count <= 16, f"what count {what_count} > 16"
    assert how_count >= 13, f"how count {how_count} < 13"
    assert is_does_count >= 13, f"is/does count {is_does_count} < 13"
    assert why_should_count >= 8, f"why/should count {why_should_count} < 8"
    assert when_who_which_count >= 6, f"when/who/which count {when_who_which_count} < 6"

    # Verify no duplicate queries
    queries = [c["query"] for c in NEW_CASES]
    assert len(queries) == len(set(queries)), "Duplicate queries found"

    # Verify context lengths
    for c in NEW_CASES:
        for i, ctx in enumerate(c["contexts"]):
            assert 150 <= len(ctx) <= 400, (
                f"{c['id']} context[{i}] length {len(ctx)} outside 150-400: "
                f"'{ctx[:60]}...'"
            )

    print("All validations passed!")
    print(f"  Cases: {len(NEW_CASES)}")
    print(f"  Subcategories: {dict(subcat_counts)}")
    print(f"  Multi-source: {len(multi_source)}")
    print(f"  Domains ({len(domain_counts)}): {dict(domain_counts)}")
    print(f"  Query types: {dict(qt_counts)}")
    print(f"    what={what_count}, how={how_count}, is/does={is_does_count}, "
          f"why/should={why_should_count}, when/who/which={when_who_which_count}")

    # --- read, append, write ---
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_ids = {c["id"] for c in data["cases"]}
    for c in NEW_CASES:
        if c["id"] in existing_ids:
            print(f"ERROR: {c['id']} already exists in {DATA_FILE}", file=sys.stderr)
            sys.exit(1)

    data["cases"].extend(NEW_CASES)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\nAppended {len(NEW_CASES)} cases to {DATA_FILE}")
    print(f"Total cases now: {len(data['cases'])}")


if __name__ == "__main__":
    main()
