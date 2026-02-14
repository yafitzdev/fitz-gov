#!/usr/bin/env python3
"""
Generate 55 new medium-difficulty relevance test cases (t1_relevance_medium_010 through t1_relevance_medium_064)
and append them to data/tier1_core/relevance.json.

Subcategory distribution (~5-6 each):
  partial_answer, wrong_entity_focus, temporal_mismatch, tangent_drift,
  over_answering, related_but_different, prerequisite_missing,
  granularity_mismatch, scope_mismatch, format_mismatch

Domain distribution: at least 8 domains, none >15% (max ~8 of 55)
Query type distribution: "what" max 30% (~16), rest mixed
"""

import json
import sys
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "tier1_core" / "relevance.json"

NEW_CASES = [
    # =========================================================================
    # partial_answer (6 cases): 010-015
    # =========================================================================
    {
        "id": "t1_relevance_medium_010",
        "difficulty": "medium",
        "subcategory": "partial_answer",
        "query": "How long does the fermentation take AND what temperature should it be stored at during aging?",
        "contexts": [
            "Traditional kimchi fermentation involves salting napa cabbage for 6-8 hours, then mixing with a paste of gochugaru, garlic, ginger, fish sauce, and scallions. The mixture is packed tightly into ceramic onggi jars or glass containers to remove air pockets and encourage anaerobic conditions. Fermentation typically takes 3-5 days at room temperature, producing lactic acid bacteria such as Lactobacillus that give kimchi its characteristic tangy flavor. The cabbage should be fully submerged in its brine during this initial stage to prevent mold growth on exposed surfaces."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about both fermentation duration and aging storage temperature, but context only covers fermentation duration",
        "rationale": "The context explains fermentation timing but does not specify storage temperature during aging",
        "required_elements": ["temperature", "aging", "not mentioned", "storage"],
        "domain": "food",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_011",
        "difficulty": "medium",
        "subcategory": "partial_answer",
        "query": "Does the insurance plan cover dental AND vision for dependents?",
        "contexts": [
            "The Premier Health Plus plan provides comprehensive dental coverage for all enrolled dependents, including two professional cleanings per year, annual X-rays, and up to $2,000 in restorative procedures such as crowns and fillings. Orthodontic coverage is available for dependents under 19 with a $1,500 lifetime maximum benefit. Emergency dental procedures are covered at 80% after the $50 deductible is met. The plan operates on a calendar-year basis with open enrollment each November, and waiting periods apply only to new enrollees who did not have prior continuous coverage."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about both dental and vision coverage for dependents, but context only addresses dental",
        "rationale": "The context thoroughly covers dental benefits but makes no mention of vision coverage",
        "required_elements": ["vision", "not mentioned", "not provided", "only"],
        "domain": "finance",
        "query_type": "does",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_012",
        "difficulty": "medium",
        "subcategory": "partial_answer",
        "query": "How strict are the admission requirements AND how much does tuition cost for the MBA program at Westfield University?",
        "contexts": [
            "Westfield University's MBA program requires applicants to hold a bachelor's degree from an accredited institution with a minimum GPA of 3.0 on a 4.0 scale. A GMAT score of 550 or higher is expected, though GRE scores are also accepted with equivalent percentile rankings. Candidates must submit two professional recommendations, a current resume showing at least two years of post-undergraduate work experience, and a 750-word statement of purpose. International applicants need a TOEFL score of 90 or above, and all applicants must complete an admissions interview conducted by a faculty member or alumni volunteer."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for admission requirements and tuition, but context only covers admission requirements",
        "rationale": "Tuition costs are entirely absent from the context",
        "required_elements": ["tuition", "cost", "not mentioned", "not provided"],
        "domain": "education",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_013",
        "difficulty": "medium",
        "subcategory": "partial_answer",
        "query": "When does the hiking trail open for the season AND is camping allowed along the route?",
        "contexts": [
            "The Alpine Ridge Trail in Glacier National Park typically opens for the season between late June and early July, depending on snowmelt conditions across the high-elevation passes. Park rangers assess trail conditions weekly beginning in May and post updates on the park website and visitor center bulletin boards. The 14.6-mile trail reaches an elevation of 7,800 feet and is rated as strenuous, with several steep switchbacks and exposed ridgelines. Hikers are strongly advised to carry bear spray, a first-aid kit, and sufficient water, and to check for current wildlife advisories before setting out. The trail passes through several avalanche chutes that may retain deep snow well into July."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about both trail opening date and camping policy, but context only discusses opening date",
        "rationale": "Camping rules along the route are not addressed in the context",
        "required_elements": ["camping", "not mentioned", "not specified", "trail"],
        "domain": "environment",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_014",
        "difficulty": "medium",
        "subcategory": "partial_answer",
        "query": "Who is eligible for the remote work program AND what equipment does the company provide?",
        "contexts": [
            "Employees who have completed at least 12 months of continuous employment and maintain a performance rating of 'meets expectations' or above are eligible for the remote work program at Synergex Corp. Managers must approve all remote work arrangements through the HR portal, and employees in client-facing roles such as sales and consulting may be limited to two remote days per week. Participants must demonstrate reliable internet access with a minimum speed of 50 Mbps and a dedicated workspace free from distractions. All remote workers are required to be available during core business hours of 9 AM to 3 PM in their local time zone."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about eligibility and equipment provision, but context only covers eligibility criteria",
        "rationale": "The context explains who qualifies but says nothing about company-provided equipment",
        "required_elements": ["equipment", "not mentioned", "provide", "not specified"],
        "domain": "hr_workplace",
        "query_type": "who",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_015",
        "difficulty": "medium",
        "subcategory": "partial_answer",
        "query": "How much RAM does the ThinkStation P360 have AND what graphics card options are available?",
        "contexts": [
            "The Lenovo ThinkStation P360 Tower workstation comes equipped with 32GB of DDR5-4800 ECC memory, expandable to 128GB across four DIMM slots using registered or unbuffered ECC modules. Memory performance benchmarks show sustained read speeds of 38 GB/s and write speeds of 36 GB/s under heavy compute loads. The memory controller supports dual-channel configuration for optimal throughput in professional workloads such as CAD rendering and scientific simulation. Lenovo offers optional memory upgrades at the point of purchase, with 64GB and 128GB configurations available for an additional cost that varies by retailer."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about RAM and graphics card options, but context only covers RAM specifications",
        "rationale": "Graphics card options are not mentioned in the context",
        "required_elements": ["graphics", "not mentioned", "GPU", "not specified"],
        "domain": "technology",
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
            "min_required": 1,
        },
    },
    # =========================================================================
    # wrong_entity_focus (6 cases): 016-021
    # =========================================================================
    {
        "id": "t1_relevance_medium_016",
        "difficulty": "medium",
        "subcategory": "wrong_entity_focus",
        "query": "Is the graduation rate at Lincoln High School improving?",
        "contexts": [
            "Jefferson High School in the same district reported a four-year graduation rate of 91.3% for the 2023-2024 academic year, an improvement from 88.7% the previous year. The school attributed the gains to expanded after-school tutoring programs and a new early warning system that identifies at-risk students before they fall behind. Jefferson's dropout rate fell to 2.1%, the lowest in a decade among district high schools. Additionally, 78% of Jefferson graduates enrolled in post-secondary education within one year, up from 71% in 2022, reflecting stronger college counseling services."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about Lincoln High School but context provides data for Jefferson High School",
        "rationale": "Data for Jefferson High School cannot be assumed to apply to Lincoln High School",
        "required_elements": ["Lincoln", "Jefferson", "different", "not"],
        "domain": "education",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_017",
        "difficulty": "medium",
        "subcategory": "wrong_entity_focus",
        "query": "Does Dr. Patel recommend surgery for rotator cuff tears?",
        "contexts": [
            "Dr. Martinez, an orthopedic surgeon at Summit Medical Center with over 18 years of clinical experience, generally recommends arthroscopic surgery for full-thickness rotator cuff tears in active patients under 65. She prefers a conservative approach with physical therapy for partial tears, typically prescribing a 12-week rehabilitation protocol before considering surgical intervention. Dr. Martinez has published 14 peer-reviewed studies on rotator cuff repair outcomes and reports a 94% patient satisfaction rate with her minimally invasive surgical technique. She also serves as an advisor to the American Academy of Orthopaedic Surgeons."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about Dr. Patel's recommendation but context describes Dr. Martinez's approach",
        "rationale": "Dr. Martinez's treatment philosophy cannot be attributed to Dr. Patel",
        "required_elements": ["Patel", "Martinez", "different", "not"],
        "domain": "medicine",
        "query_type": "does",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_018",
        "difficulty": "medium",
        "subcategory": "wrong_entity_focus",
        "query": "How did the Nasdaq perform in December 2024?",
        "contexts": [
            "The S&P 500 index closed December 2024 at 6,048 points, marking a 2.3% gain for the month and capping off a strong year for broad-market equities. The index was buoyed by strong performance in the technology and healthcare sectors, which together accounted for over 40% of the monthly gains. Energy stocks lagged as crude oil prices dipped below $68 per barrel amid concerns about oversupply. Analysts at Goldman Sachs noted that the S&P 500's year-end rally was supported by better-than-expected corporate earnings and cooling inflation data released in mid-December."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about Nasdaq performance but context only covers S&P 500",
        "rationale": "S&P 500 and Nasdaq are different indices with different compositions and performance",
        "required_elements": ["Nasdaq", "S&P", "different", "not mentioned"],
        "domain": "finance",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_019",
        "difficulty": "medium",
        "subcategory": "wrong_entity_focus",
        "query": "Which crops grow best in the Willamette Valley of Oregon?",
        "contexts": [
            "The Central Valley of California is one of the most productive agricultural regions in the world, producing over 250 different crops on its 6.5 million irrigated acres. Key crops include almonds, grapes, tomatoes, cotton, and pistachios, with the region supplying over 25% of America's food. The Central Valley benefits from a Mediterranean climate with mild winters and hot, dry summers that extend the growing season well into October. Irrigation from the Sacramento and San Joaquin rivers supports farming operations that generate over $17 billion in annual agricultural revenue, though drought conditions in recent years have strained water allocations."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about crops in Oregon's Willamette Valley but context describes California's Central Valley",
        "rationale": "Different regions have different climates and soil conditions affecting crop suitability",
        "required_elements": ["Willamette", "Central Valley", "California", "different"],
        "domain": "agriculture",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_020",
        "difficulty": "medium",
        "subcategory": "wrong_entity_focus",
        "query": "Is the Rivian R1S a good family vehicle?",
        "contexts": [
            "The Rivian R1T pickup truck has earned strong reviews for its off-road capability and innovative engineering. It offers a 314-mile range on a full charge from its 135 kWh battery pack and can tow up to 11,000 pounds when properly equipped. The R1T's quad-motor all-wheel-drive setup delivers 835 horsepower and includes an adjustable air suspension system with 14.9 inches of ground clearance in its highest setting. Its unique gear tunnel provides 11.1 cubic feet of lockable storage between the cab and bed, ideal for outdoor equipment. Consumer Reports gave the R1T an overall score of 78 out of 100, praising its acceleration and build quality."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about the R1S SUV but context reviews the R1T pickup truck",
        "rationale": "The R1T and R1S are different vehicle types with different interior configurations and use cases",
        "required_elements": ["R1S", "R1T", "different", "not"],
        "domain": "transportation",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_021",
        "difficulty": "medium",
        "subcategory": "wrong_entity_focus",
        "query": "Which services does the Portland branch of Greenleaf Credit Union offer?",
        "contexts": [
            "The Seattle branch of Greenleaf Credit Union offers full-service banking including checking and savings accounts, auto loans starting at 4.99% APR, and mortgage lending with both fixed and adjustable rates. Members can access a 24-hour ATM in the lobby, safe deposit boxes in three sizes, and a two-lane drive-through window for quick transactions. The Seattle location also provides notary services and one-on-one financial counseling by appointment with certified financial planners. Branch hours are Monday through Friday 9 AM to 5 PM and Saturday 9 AM to 1 PM. The branch manager, Karen Liu, has served the Seattle community since 2019."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about Portland branch but context describes the Seattle branch",
        "rationale": "Services may differ between branches; Seattle's offerings cannot be assumed for Portland",
        "required_elements": ["Portland", "Seattle", "different", "not"],
        "domain": "finance",
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
            "min_required": 1,
        },
    },
    # =========================================================================
    # temporal_mismatch (6 cases): 022-027
    # =========================================================================
    {
        "id": "t1_relevance_medium_022",
        "difficulty": "medium",
        "subcategory": "temporal_mismatch",
        "query": "How large was the population of Nashville in the 2020 census?",
        "contexts": [
            "According to the 2010 United States Census, Nashville-Davidson County had a population of 626,681, making it the 25th most populous city in the nation at that time. The Nashville metropolitan statistical area recorded 1.59 million residents, representing a 20.8% increase from the 2000 census count. Population growth was driven primarily by domestic migration from the Northeast and Midwest, attracted by lower cost of living and a booming healthcare and music industry. The median age of Nashville residents was 33.9 years, and the median household income stood at $46,781, slightly below the national average."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for 2020 census data but context only has 2010 census data",
        "rationale": "2010 census data is a decade old and cannot represent 2020 census figures",
        "required_elements": ["2010", "2020", "not", "different"],
        "domain": "government",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "temporal",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_023",
        "difficulty": "medium",
        "subcategory": "temporal_mismatch",
        "query": "Should I use React 19 features for my new project starting in 2025?",
        "contexts": [
            "React 17, released in October 2020, introduced no new developer-facing features but instead focused on making future upgrades easier for large codebases. Key changes included a new JSX transform that eliminated the need to import React at the top of every file using JSX, and event delegation was moved from the document level to the root DOM container. React 17 served as a strategic stepping stone, enabling gradual adoption of future versions within the same application. The release also improved the consistency of event handling across different React trees embedded in the same page, which was particularly useful for micro-frontend architectures."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about React 19 features in 2025 but context covers React 17 from 2020",
        "rationale": "React 17 information is outdated and does not cover React 19 capabilities",
        "required_elements": ["React 17", "React 19", "outdated", "not"],
        "domain": "technology",
        "query_type": "should",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "temporal",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_024",
        "difficulty": "medium",
        "subcategory": "temporal_mismatch",
        "query": "Have the EU emission standards for passenger vehicles changed since 2021?",
        "contexts": [
            "Under Euro 6d emission standards, effective from January 2021, passenger vehicles sold in the EU must limit nitrogen oxide emissions to 60 mg/km for diesel engines and 80 mg/km combined with real driving emissions (RDE) testing on public roads. Particulate matter is capped at 4.5 mg/km for both petrol and diesel vehicles. The Euro 6d standard introduced stricter on-road conformity factors, significantly reducing the gap between laboratory results and real-world emissions. Manufacturers that exceed fleet-average CO2 targets of 95 g/km face penalties of 95 euros per gram per vehicle sold, creating strong financial incentives for electrification."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks whether EU emission standards changed since 2021 but context only describes the 2021 standards",
        "rationale": "The context explains what the 2021 standards were but has no information about subsequent changes",
        "required_elements": ["2021", "since", "changes", "not mentioned"],
        "domain": "environment",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "temporal",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_025",
        "difficulty": "medium",
        "subcategory": "temporal_mismatch",
        "query": "Who won the 2024 Wimbledon men's singles title?",
        "contexts": [
            "The total solar eclipse of July 10, 2022, saw Novak Djokovic defeat Nick Kyrgios in the Wimbledon men's singles final in four hard-fought sets (4-6, 6-3, 6-4, 7-6) to claim his 21st Grand Slam title. The Serbian star saved a dramatic set point in the fourth-set tiebreak and celebrated with the Centre Court crowd. It marked Kyrgios's first-ever Grand Slam final appearance, and the Australian was fined $4,000 for unsportsmanlike conduct during the match. The victory extended Djokovic's winning streak at Wimbledon to four consecutive titles and reinforced his status as the dominant grass-court player of his generation."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about 2024 Wimbledon winner but context covers the 2022 final",
        "rationale": "The 2022 result does not reveal the 2024 champion",
        "required_elements": ["2022", "2024", "not", "different"],
        "domain": "sports",
        "query_type": "who",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "temporal",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_026",
        "difficulty": "medium",
        "subcategory": "temporal_mismatch",
        "query": "Is the current interest rate for a 30-year fixed mortgage in January 2025 above or below 6%?",
        "contexts": [
            "As of March 2023, the average interest rate for a 30-year fixed-rate mortgage in the United States stood at 6.73%, according to Freddie Mac's Primary Mortgage Market Survey. This represented a significant increase from the 3.22% rate recorded in January 2022, roughly doubling monthly payments for new borrowers. The Federal Reserve's aggressive rate hikes throughout 2022 and early 2023 drove borrowing costs higher across all loan types. First-time homebuyers were particularly affected, with monthly payments on a median-priced home rising by approximately $600 compared to the historically low rates of early 2022."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for January 2025 mortgage rate but context only has March 2023 data",
        "rationale": "Mortgage rates from March 2023 cannot indicate current January 2025 rates",
        "required_elements": ["2023", "2025", "outdated", "not"],
        "domain": "real_estate",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "temporal",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_027",
        "difficulty": "medium",
        "subcategory": "temporal_mismatch",
        "query": "When is the next solar eclipse visible from North America after 2024?",
        "contexts": [
            "The total solar eclipse of April 8, 2024, was visible across a dramatic path stretching from Mexico through Texas, the Midwest, and into eastern Canada. The path of totality was approximately 115 miles wide, and totality lasted up to 4 minutes and 28 seconds near Torreon, Mexico, making it one of the longest total eclipses visible from populated areas in decades. An estimated 31.6 million Americans lived directly within the path of totality. Major viewing locations included Dallas, Indianapolis, Cleveland, and Montreal. Cloud cover was a significant concern in the Great Lakes region but most of the path experienced clear skies and excellent viewing conditions."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about eclipses after 2024 but context only describes the April 2024 eclipse",
        "rationale": "Information about the 2024 eclipse does not indicate when the next one will occur",
        "required_elements": ["2024", "next", "after", "not mentioned"],
        "domain": "science",
        "query_type": "when",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "temporal",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 1,
        },
    },
    # =========================================================================
    # tangent_drift (5 cases): 028-032
    # =========================================================================
    {
        "id": "t1_relevance_medium_028",
        "difficulty": "medium",
        "subcategory": "tangent_drift",
        "query": "How do I configure two-factor authentication on my company email?",
        "contexts": [
            "Two-factor authentication (2FA) adds an extra layer of security beyond passwords by requiring a second verification step during the login process. It works by combining something you know (your password) with something you have, typically a code sent via SMS, a time-based one-time password from an authenticator app, or a hardware security token. Research from Microsoft shows that 2FA reduces account compromise by 99.9% compared to password-only authentication. Common authenticator apps include Google Authenticator, Microsoft Authenticator, and Authy, each generating new codes every 30 seconds. The NIST Special Publication 800-63B recommends against SMS-based 2FA due to SIM-swapping vulnerabilities."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks how to configure 2FA on company email but context only explains what 2FA is in general",
        "rationale": "General 2FA knowledge does not provide specific configuration steps for a company email system",
        "required_elements": ["configure", "steps", "not provided", "how to"],
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_029",
        "difficulty": "medium",
        "subcategory": "tangent_drift",
        "query": "Why did the patient develop antibiotic resistance?",
        "contexts": [
            "Antibiotic resistance is a growing public health threat worldwide, with the World Health Organization estimating that by 2050, drug-resistant infections could cause 10 million deaths annually and cost the global economy $100 trillion. Major contributing factors to resistance include overprescription of antibiotics in clinical settings, patients not completing their full treatment courses, and widespread agricultural use of antimicrobials in livestock feed. MRSA (methicillin-resistant Staphylococcus aureus) is among the most well-known resistant organisms, affecting both hospital and community settings. Hospitals have implemented antimicrobial stewardship programs to monitor prescribing patterns and reduce unnecessary antibiotic use."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks why a specific patient developed resistance but context discusses the global phenomenon",
        "rationale": "General information about antibiotic resistance does not explain this specific patient's case",
        "required_elements": ["patient", "specific", "not", "general"],
        "domain": "medicine",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_030",
        "difficulty": "medium",
        "subcategory": "tangent_drift",
        "query": "How should I prune my Meyer lemon tree to improve fruit production?",
        "contexts": [
            "Meyer lemon trees thrive in USDA hardiness zones 9-11 and prefer full sun exposure with at least 8 hours of direct sunlight daily for optimal fruit development. They require well-draining soil with a slightly acidic pH between 5.5 and 6.5, and benefit from raised beds or containers with drainage holes in heavier clay soils. Watering should be deep but infrequent, allowing the top 2 inches of soil to dry between waterings to prevent root rot. Meyer lemons are quite sensitive to frost and should be brought indoors or covered when temperatures drop below 50 degrees Fahrenheit. Fertilize every 4-6 weeks during the growing season with a citrus-specific fertilizer that is high in nitrogen and includes micronutrients like zinc and iron."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about pruning techniques but context covers general care (sun, soil, watering, fertilizing)",
        "rationale": "Growing conditions and fertilizing advice do not address pruning methods",
        "required_elements": ["pruning", "not mentioned", "not addressed", "care"],
        "domain": "agriculture",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_031",
        "difficulty": "medium",
        "subcategory": "tangent_drift",
        "query": "What penalties does a landlord face for not returning a security deposit on time?",
        "contexts": [
            "When a tenant moves out of a rental property, the landlord must conduct a thorough inspection for damages beyond normal wear and tear. Common deductions from security deposits include large holes in walls requiring drywall repair, significantly stained or torn carpeting that cannot be professionally cleaned, broken appliances caused by tenant misuse, and pet damage such as scratched hardwood floors or urine stains. Normal wear and tear, such as minor scuff marks on walls, small nail holes from hanging pictures, and naturally faded paint, cannot legally be deducted. Landlords should document the property's condition at both move-in and move-out with dated photographs and a written checklist signed by both parties to prevent disputes."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about penalties for late return of deposits but context discusses what can be deducted",
        "rationale": "Deduction rules do not address penalties or deadlines for returning deposits",
        "required_elements": ["penalties", "return", "deadline", "not mentioned"],
        "domain": "law",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_032",
        "difficulty": "medium",
        "subcategory": "tangent_drift",
        "query": "How does cognitive behavioral therapy differ from psychodynamic therapy in treating depression?",
        "contexts": [
            "Cognitive behavioral therapy (CBT) is an evidence-based psychotherapy treatment that focuses on identifying and systematically changing negative thought patterns and maladaptive behaviors. A typical CBT course lasts 12-20 weekly sessions and involves structured homework assignments that patients complete between appointments. Research consistently shows CBT is highly effective for depression, generalized anxiety disorder, PTSD, OCD, and social phobia. Therapists use techniques such as cognitive restructuring, graded exposure therapy, and behavioral activation to help patients challenge distorted thinking. CBT has one of the strongest evidence bases in all of psychotherapy, with hundreds of randomized controlled trials supporting its efficacy across diverse populations."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for a comparison between CBT and psychodynamic therapy but context only describes CBT",
        "rationale": "Without information about psychodynamic therapy, a meaningful comparison cannot be made",
        "required_elements": ["psychodynamic", "not mentioned", "comparison", "only"],
        "domain": "psychology",
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
            "min_required": 1,
        },
    },
    # =========================================================================
    # over_answering (6 cases): 033-038
    # =========================================================================
    {
        "id": "t1_relevance_medium_033",
        "difficulty": "medium",
        "subcategory": "over_answering",
        "query": "When does the library close on Saturdays?",
        "contexts": [
            "The Maplewood Public Library is a historic building constructed in 1923 and extensively renovated in 2018 with a $4.2 million bond measure approved by voters. It houses over 85,000 volumes across two floors, including a rare books collection of 1,200 titles donated by the Whitfield estate. The children's section was expanded to 3,000 square feet with new interactive learning stations and a dedicated craft area. The library hosts weekly story time on Tuesdays at 10 AM, a book club on the first Thursday of each month, and free computer literacy classes on Wednesdays. Operating hours are Monday through Friday 9 AM to 8 PM, Saturday 10 AM to 5 PM, and Sunday 1 PM to 5 PM. Free parking is available in the adjacent municipal lot with a two-hour limit."
        ],
        "expected_mode": "trustworthy",
        "description": "Simple question about Saturday closing time buried in extensive context about the library",
        "rationale": "The answer (5 PM Saturday) is present but buried among irrelevant details about history, collections, and programs",
        "required_elements": ["5 PM", "Saturday", "close"],
        "domain": "education",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_034",
        "difficulty": "medium",
        "subcategory": "over_answering",
        "query": "Is the hotel pet-friendly?",
        "contexts": [
            "The Grand Coastal Resort features 342 elegantly appointed rooms across 12 floors, including 28 oceanfront suites with private balconies overlooking the Pacific. Amenities include three temperature-controlled swimming pools, a full-service spa offering hot stone massage and facial treatments, two acclaimed restaurants (Mediterranean and Asian fusion), a 24-hour fitness center with Peloton bikes, and a fully equipped business center. The resort offers complimentary airport shuttle service departing every 30 minutes from the main lobby. Conference facilities can accommodate up to 500 guests for corporate events. The resort welcomes dogs and cats under 40 pounds with a $75 per stay pet fee; pet beds and water bowls are provided upon request. Valet parking costs $35 per night, and self-parking is available for $20."
        ],
        "expected_mode": "trustworthy",
        "description": "Simple yes/no question about pet policy buried in extensive resort description",
        "rationale": "The pet policy is present but surrounded by large amounts of irrelevant amenity information",
        "required_elements": ["pet", "dogs", "cats", "$75"],
        "domain": "food",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_035",
        "difficulty": "medium",
        "subcategory": "over_answering",
        "query": "Does the prescription drug interact with grapefruit?",
        "contexts": [
            "Atorvastatin (brand name Lipitor) is a widely prescribed statin medication used to lower LDL cholesterol and triglycerides in patients with hyperlipidemia. The typical starting dose is 10-20 mg taken once daily in the evening when cholesterol synthesis is highest. Common side effects include muscle pain and weakness (reported in 5-10% of patients), headache, nausea, diarrhea, and joint pain. Rare but serious side effects include rhabdomyolysis and liver damage; liver function tests should be performed before starting therapy and periodically thereafter. Atorvastatin interacts with grapefruit juice, which inhibits CYP3A4 enzymes and can increase drug concentration in the blood, raising the risk of dose-dependent side effects. Patients should also avoid excessive alcohol consumption. The drug has a half-life of approximately 14 hours."
        ],
        "expected_mode": "trustworthy",
        "description": "Simple interaction question answered within a dense clinical overview",
        "rationale": "The grapefruit interaction is confirmed but buried among dosing, side effects, and pharmacokinetics",
        "required_elements": ["grapefruit", "interact", "increase"],
        "domain": "medicine",
        "query_type": "does",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_036",
        "difficulty": "medium",
        "subcategory": "over_answering",
        "query": "How old do you have to be to rent a car from AutoFleet?",
        "contexts": [
            "AutoFleet Car Rental operates 1,200 locations across 48 states and serves over 3 million satisfied customers annually. The company's diverse fleet includes economy sedans, midsize SUVs, luxury vehicles, convertibles, and 15-passenger vans for group travel. Pricing starts at $29.99 per day for economy vehicles, with weekly and monthly discounts available. AutoFleet offers a three-tier loyalty program: Silver, Gold, and Platinum, providing benefits such as complimentary upgrades, free additional drivers, and priority pickup at airport locations. Insurance options include collision damage waiver ($19.99/day), personal accident insurance ($7.99/day), and supplemental liability protection ($14.99/day). Renters must be at least 21 years old with a valid driver's license; drivers aged 21-24 are subject to a young driver surcharge of $25 per day. A major credit card is required at pickup."
        ],
        "expected_mode": "trustworthy",
        "description": "Simple age question answered within extensive company overview",
        "rationale": "The minimum age (21) is present but surrounded by irrelevant pricing, insurance, and loyalty program details",
        "required_elements": ["21", "minimum", "age"],
        "domain": "transportation",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_037",
        "difficulty": "medium",
        "subcategory": "over_answering",
        "query": "Is gluten present in the restaurant's pad thai?",
        "contexts": [
            "Bangkok Garden's signature pad thai is prepared with thin rice noodles stir-fried in a seasoned wok with tamarind paste, fish sauce, palm sugar, and dried shrimp for depth of flavor. The dish includes scrambled eggs, firm tofu, crisp bean sprouts, and crushed roasted peanuts, garnished with fresh lime wedges and cilantro. It is available in three protein options: chicken ($14.95), shrimp ($16.95), or vegetable ($12.95). The restaurant sources its rice noodles from a specialty Thai import company and uses traditional recipes passed down from the head chef's grandmother in Chiang Mai province. Pad thai at Bangkok Garden is naturally gluten-free as it uses rice noodles rather than wheat and tamari-style fish sauce. However, the kitchen handles wheat products for other menu items, and complete protection against cross-contamination cannot be guaranteed."
        ],
        "expected_mode": "trustworthy",
        "description": "Simple allergen question answered amid extensive dish description and history",
        "rationale": "Gluten-free status is confirmed but buried among ingredients, pricing, and origin story, with a cross-contamination caveat",
        "required_elements": ["gluten-free", "rice noodles", "cross-contamination"],
        "domain": "food",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_038",
        "difficulty": "medium",
        "subcategory": "over_answering",
        "query": "How many calories are in a serving of the protein shake?",
        "contexts": [
            "PowerFuel Protein Shake is manufactured in an FDA-inspected facility in Portland, Oregon, using sustainably sourced ingredients. The company was founded in 2018 by former Olympic athlete Marcus Chen and has grown to $45 million in annual revenue with distribution in 15 countries. The shake comes in chocolate, vanilla, strawberry, and limited-edition cookies-and-cream flavors. Each 16-oz serving contains 280 calories, 30g of protein from grass-fed whey isolate, 8g of dietary fiber, and 12 essential vitamins and minerals including vitamin D3 and magnesium. The shake is sweetened with stevia and monk fruit extract rather than artificial sweeteners or added sugar. It is available at over 8,000 retail locations nationwide and through the company's direct subscription service at $3.49 per serving."
        ],
        "expected_mode": "trustworthy",
        "description": "Simple calorie question answered within broad product and company overview",
        "rationale": "The calorie count (280) is present but surrounded by company history, business metrics, and distribution details",
        "required_elements": ["280", "calories", "serving"],
        "domain": "food",
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
            "min_required": 1,
        },
    },
    # =========================================================================
    # related_but_different (6 cases): 039-044
    # =========================================================================
    {
        "id": "t1_relevance_medium_039",
        "difficulty": "medium",
        "subcategory": "related_but_different",
        "query": "How do I appeal a parking ticket in Boston?",
        "contexts": [
            "To contest a moving traffic violation in Boston, drivers must file a written appeal within 20 business days of receiving the citation through the Massachusetts Trial Court's online portal or by mail. Appeals are heard at the Boston Municipal Court located at 24 New Chardon Street, and drivers may represent themselves or hire a traffic attorney. The process involves submitting a not-responsible plea along with any supporting evidence such as dashcam footage, photographs, or signed witness statements. Court hearings are typically scheduled 4-6 weeks after filing and last approximately 15 minutes. If the judge rules in the driver's favor, the citation is dismissed and any points are removed from the driving record."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about parking ticket appeals but context describes traffic violation appeals",
        "rationale": "Parking tickets and traffic violations have different appeal processes and jurisdictions",
        "required_elements": ["parking", "traffic", "different", "not"],
        "domain": "law",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_040",
        "difficulty": "medium",
        "subcategory": "related_but_different",
        "query": "How do symptoms of Type 1 diabetes present in children?",
        "contexts": [
            "Type 2 diabetes in children has increased dramatically over the past two decades, largely driven by rising childhood obesity rates and increasingly sedentary lifestyles. Symptoms of Type 2 diabetes in children include increased thirst, frequent urination, unexplained weight loss, persistent fatigue, and blurred vision. However, many children with Type 2 diabetes are asymptomatic at the time of diagnosis and are identified only through routine blood work showing elevated fasting glucose above 126 mg/dL or HbA1c above 6.5%. Key risk factors include a BMI above the 85th percentile, family history of diabetes, and belonging to certain high-risk ethnic groups. Treatment typically begins with lifestyle modifications including diet and exercise, combined with metformin as first-line pharmacotherapy."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about Type 1 diabetes symptoms but context covers Type 2 diabetes in children",
        "rationale": "Type 1 and Type 2 diabetes have different causes, presentations, and treatments",
        "required_elements": ["Type 1", "Type 2", "different", "not"],
        "domain": "medicine",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_041",
        "difficulty": "medium",
        "subcategory": "related_but_different",
        "query": "How do I set up a sole proprietorship in Florida?",
        "contexts": [
            "To form a Limited Liability Company (LLC) in Florida, you must file Articles of Organization with the Florida Division of Corporations through the Sunbiz.org portal and pay a $125 filing fee. You will need to designate a registered agent with a physical Florida street address who can accept legal documents on behalf of the LLC. An operating agreement, while not legally required by the state, is strongly recommended to define member roles and profit distribution. Florida LLCs must file an annual report by May 1 each year with a $138.75 fee to maintain active status. LLCs provide personal liability protection, legally separating the owner's personal assets from business debts and potential lawsuits."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about sole proprietorship setup but context explains LLC formation",
        "rationale": "Sole proprietorships and LLCs are different business structures with different requirements",
        "required_elements": ["sole proprietorship", "LLC", "different", "not"],
        "domain": "law",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_042",
        "difficulty": "medium",
        "subcategory": "related_but_different",
        "query": "Why should homeowners consider solar panels for residential use?",
        "contexts": [
            "Commercial solar installations have become increasingly cost-effective for businesses of all sizes over the past decade. Large-scale rooftop systems of 100 kW or more qualify for accelerated depreciation under the Modified Accelerated Cost Recovery System (MACRS), allowing businesses to recover installation costs over just 5 years on their tax returns. Power Purchase Agreements (PPAs) let companies install solar arrays with zero upfront capital expenditure. Major corporations including Amazon, Apple, and Google have committed to 100% renewable energy operations. Commercial solar arrays typically achieve payback periods of 4-7 years and can reduce electricity costs by 40-60% compared to grid power, with systems lasting 25-30 years with minimal maintenance."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about residential solar advantages but context covers commercial solar installations",
        "rationale": "Commercial solar benefits (MACRS, PPAs, large-scale systems) differ significantly from residential considerations",
        "required_elements": ["residential", "commercial", "different", "not"],
        "domain": "environment",
        "query_type": "why",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_043",
        "difficulty": "medium",
        "subcategory": "related_but_different",
        "query": "How do I train a puppy to walk on a leash without pulling?",
        "contexts": [
            "Training an adult dog to walk politely on a leash requires consistent daily practice and positive reinforcement techniques. Begin by choosing a fixed-length leash (not retractable) of 4-6 feet and a properly fitted collar or harness. When the dog pulls forward, stop walking immediately and stand still until the leash goes slack before proceeding. Reward the dog with small high-value treats when it walks beside you without tension on the leash. For dogs with deeply ingrained pulling habits, a front-clip harness can effectively redirect their forward momentum back toward the handler. Training sessions should last 15-20 minutes to prevent frustration for both dog and owner. Most adult dogs show significant improvement within 2-3 weeks of consistent daily practice."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about puppy leash training but context covers adult dog leash training",
        "rationale": "Puppies have different attention spans, physical limitations, and training approaches than adult dogs",
        "required_elements": ["puppy", "adult", "different", "not"],
        "domain": "science",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_044",
        "difficulty": "medium",
        "subcategory": "related_but_different",
        "query": "How does the process for adopting a child internationally from South Korea work?",
        "contexts": [
            "Domestic adoption in South Korea follows a structured process managed by the Korea Adoption Services (KAS) and authorized private agencies. Korean citizens wishing to adopt must complete a comprehensive home study evaluation, attend 8 hours of mandatory pre-adoption education covering child development and attachment, and submit detailed medical and financial documentation. Applicants must be legally married for at least 3 years and be between 25 and 45 years old, with the age gap between adoptive parent and child not exceeding 50 years. The matching process typically takes 12-18 months from application approval. Since 2012, South Korea has prioritized domestic placements over international ones, and the National Assembly passed landmark legislation in 2023 requiring family court approval for all adoptions."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about international adoption from South Korea but context covers domestic adoption within South Korea",
        "rationale": "Domestic and international adoption processes have entirely different requirements and agencies",
        "required_elements": ["international", "domestic", "different", "not"],
        "domain": "government",
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
            "min_required": 1,
        },
    },
    # =========================================================================
    # prerequisite_missing (5 cases): 045-049
    # =========================================================================
    {
        "id": "t1_relevance_medium_045",
        "difficulty": "medium",
        "subcategory": "prerequisite_missing",
        "query": "How do I deploy a Django application to AWS Elastic Beanstalk?",
        "contexts": [
            "To deploy to AWS Elastic Beanstalk, navigate to the Elastic Beanstalk console in the AWS Management Console and click 'Create Application.' Select Python as the platform branch and upload your application bundle as a ZIP file containing your project code. Configure the environment type as either web server or worker depending on your needs, and select your desired EC2 instance size based on expected traffic. Set environment variables for your database connection string, Django secret key, and any other sensitive configuration. Elastic Beanstalk will automatically provision an EC2 instance, configure an Application Load Balancer, set up auto-scaling rules, and deploy your application. Monitor deployment status through the console dashboard, check the environment health indicator, and review application logs if errors occur during startup."
        ],
        "expected_mode": "trustworthy",
        "description": "Deployment steps are given but critical Django-specific prerequisites are missing",
        "rationale": "The context skips essential prerequisites like creating requirements.txt, configuring WSGI, and setting up the .ebextensions directory",
        "required_elements": ["requirements", "WSGI", "prerequisite", "missing"],
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_046",
        "difficulty": "medium",
        "subcategory": "prerequisite_missing",
        "query": "How do I perform a tire rotation on my car safely?",
        "contexts": [
            "For a standard tire rotation on a front-wheel-drive vehicle, move the front tires straight back to the rear axle positions and cross the rear tires diagonally to the front (left rear goes to right front, right rear goes to left front). For rear-wheel-drive vehicles, reverse the pattern by moving rear tires straight forward and crossing the fronts to the back. Tighten all lug nuts in a star or cross pattern to the manufacturer's recommended torque specification, typically 80-100 ft-lbs for standard passenger vehicles, using a calibrated torque wrench. After completing the rotation, check all four tire pressures with a gauge and adjust to the values listed on the driver's door jamb placard. Most manufacturers recommend rotating tires every 5,000-7,500 miles for even tread wear."
        ],
        "expected_mode": "trustworthy",
        "description": "Rotation patterns are explained but prerequisites like jacking and safety are skipped",
        "rationale": "Critical safety prerequisites such as how to properly jack the vehicle and use jack stands are missing",
        "required_elements": ["jack", "safety", "lift", "missing"],
        "domain": "transportation",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_047",
        "difficulty": "medium",
        "subcategory": "prerequisite_missing",
        "query": "How do I make sourdough bread completely from scratch?",
        "contexts": [
            "To bake sourdough bread, combine 500g of bread flour with 350g of lukewarm water, 100g of active and bubbly sourdough starter, and 10g of fine sea salt. Mix until a shaggy dough forms, then perform stretch-and-fold cycles every 30 minutes for the first 2 hours to develop gluten structure without heavy kneading. Allow the dough to bulk ferment at room temperature (around 75-78 degrees F) for 6-8 hours until it increases roughly double in volume and shows visible air bubbles on the surface. Shape the dough into a round boule or oval batard and place it seam-side up in a floured banneton proofing basket. Refrigerate overnight for 12-16 hours for a slow cold proof. Bake in a preheated Dutch oven at 500 degrees F for 20 minutes covered, then 20 minutes uncovered at 450 degrees."
        ],
        "expected_mode": "trustworthy",
        "description": "Bread recipe is given but assumes you already have a sourdough starter",
        "rationale": "Creating a sourdough starter from scratch takes 5-7 days and is a critical prerequisite not covered",
        "required_elements": ["starter", "create", "prerequisite", "not"],
        "domain": "food",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_048",
        "difficulty": "medium",
        "subcategory": "prerequisite_missing",
        "query": "How do I analyze survey data using SPSS from start to finish?",
        "contexts": [
            "In SPSS, import your survey data by navigating to File > Open > Data and selecting your CSV or Excel file from the file browser. Use the Variable View tab at the bottom of the Data Editor to set variable types, assign descriptive labels, define value labels for coded responses, and specify measurement levels (nominal, ordinal, or scale). For descriptive statistics, go to Analyze > Descriptive Statistics > Frequencies to examine distributions. To test for significant group differences, use Analyze > Compare Means > Independent Samples T-Test or One-Way ANOVA. For correlation analysis, navigate to Analyze > Correlate > Bivariate and select Pearson or Spearman coefficients. Export your results to a formatted Word document through the Output Viewer by right-clicking tables and selecting Export. Create publication-quality visualizations using Graphs > Chart Builder."
        ],
        "expected_mode": "trustworthy",
        "description": "SPSS analysis steps are given but survey design and data preparation prerequisites are missing",
        "rationale": "Critical prerequisites like survey design, coding scheme, data cleaning, and checking assumptions are not covered",
        "required_elements": ["survey design", "data cleaning", "prerequisite", "not"],
        "domain": "science",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_049",
        "difficulty": "medium",
        "subcategory": "prerequisite_missing",
        "query": "How do I refinance my mortgage to get a lower interest rate?",
        "contexts": [
            "When refinancing your mortgage, start by comparing rate offers from at least three different lenders, paying close attention to the annual percentage rate (APR) which includes fees rather than just the advertised interest rate. Submit your application along with recent pay stubs covering at least 30 days, two years of W-2 forms, three months of bank statements, and your current mortgage statement showing your outstanding balance. The lender will order a professional appraisal to determine your home's current market value, typically costing $300-$600 depending on your location. Closing costs generally range from 2-5% of the new loan amount and may include origination fees, title insurance, and recording fees. After approval, carefully review the Closing Disclosure document at least three days before signing. You have a 3-day right of rescission after signing, during which you can cancel without penalty."
        ],
        "expected_mode": "trustworthy",
        "description": "Refinancing steps are given but prerequisites like credit score requirements and equity position are missing",
        "rationale": "The context skips critical prerequisites: checking credit score, calculating loan-to-value ratio, and determining break-even point",
        "required_elements": ["credit score", "equity", "prerequisite", "not"],
        "domain": "finance",
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
            "min_required": 1,
        },
    },
    # =========================================================================
    # granularity_mismatch (6 cases): 050-055
    # =========================================================================
    {
        "id": "t1_relevance_medium_050",
        "difficulty": "medium",
        "subcategory": "granularity_mismatch",
        "query": "Which specific exercises should I do for lower back pain relief?",
        "contexts": [
            "Physical therapy is widely recommended as a first-line treatment for managing chronic lower back pain by both orthopedic specialists and primary care physicians. A comprehensive rehabilitation approach typically includes stretching to improve flexibility, strengthening exercises for the core and back muscles, and aerobic conditioning to promote overall fitness. Research published in the Journal of Orthopedic & Sports Physical Therapy found that patients who completed an 8-week structured exercise program reported 45% less pain intensity than those who received only medication. The American College of Physicians strongly recommends exercise as a first-line treatment before considering pharmacological options such as NSAIDs or muscle relaxants. Regular physical activity helps maintain spinal flexibility, builds core muscle stability, and improves blood flow to injured tissues."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for specific exercises but context only provides high-level recommendation that exercise helps",
        "rationale": "The context endorses exercise generally but names no specific exercises, sets, reps, or techniques",
        "required_elements": ["specific", "exercises", "not provided", "general"],
        "domain": "medicine",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_051",
        "difficulty": "medium",
        "subcategory": "granularity_mismatch",
        "query": "Show me the exact syntax for creating a foreign key constraint in PostgreSQL.",
        "contexts": [
            "PostgreSQL is a powerful open-source object-relational database management system known for its extensibility, standards compliance, and robust feature set. It supports a wide range of built-in and user-defined data types, including JSON, JSONB, arrays, geometric types, and network address types. PostgreSQL implements referential integrity through foreign key constraints, which ensure that relationships between related tables remain consistent and prevent orphaned records. The database engine supports several types of constraints including NOT NULL, UNIQUE, CHECK, PRIMARY KEY, FOREIGN KEY, and EXCLUDE constraints. These constraints help maintain data quality and prevent invalid or inconsistent data from being inserted into the database tables. PostgreSQL evaluates constraints at the end of each SQL statement by default."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for exact syntax but context only provides a high-level overview of PostgreSQL constraints",
        "rationale": "The context describes what foreign keys do but provides no SQL syntax examples",
        "required_elements": ["syntax", "not provided", "example", "only"],
        "domain": "technology",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_052",
        "difficulty": "medium",
        "subcategory": "granularity_mismatch",
        "query": "Walk me through the step-by-step instructions for filing a Freedom of Information Act request.",
        "contexts": [
            "The Freedom of Information Act (FOIA) is a landmark federal law enacted in 1966 that gives any person the legal right to request access to records held by any federal executive branch agency. FOIA applies to departments, agencies, and offices within the executive branch of the federal government, but does not cover Congress, the federal courts, or state and local governments which have their own open-records laws. Nine specific exemptions protect sensitive information from disclosure, including classified national security data, trade secrets, law enforcement investigation records, and information that would constitute a clearly unwarranted invasion of personal privacy. Agencies are legally required to respond to properly submitted requests within 20 business days, though complex or voluminous requests may take considerably longer through negotiated processing timelines."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for step-by-step filing instructions but context only describes what FOIA is at a high level",
        "rationale": "The context explains the law's history and scope but provides no practical filing steps",
        "required_elements": ["step", "instructions", "how to file", "not provided"],
        "domain": "government",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_053",
        "difficulty": "medium",
        "subcategory": "granularity_mismatch",
        "query": "How many grams of protein, fiber, and iron does quinoa contain per 100g serving?",
        "contexts": [
            "Quinoa has gained enormous popularity as a so-called superfood due to its exceptional nutritional profile compared to other grains and pseudocereals. It is one of the very few plant foods that provides all nine essential amino acids in adequate proportions, making it a complete protein source particularly valued by vegetarians and vegans. Quinoa is naturally gluten-free, making it suitable for people with celiac disease, and is considered rich in dietary fiber, B vitamins, and essential minerals. It has been cultivated by indigenous peoples in the Andes mountains for over 5,000 years and was regarded as sacred by the Inca civilization. Global production has increased significantly since the early 2000s, with Peru and Bolivia accounting for over 80% of world output. The United Nations declared 2013 the International Year of Quinoa."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for specific per-100g nutritional data but context only provides general claims about quinoa's nutrition",
        "rationale": "The context calls quinoa nutritious without providing any specific quantities per serving",
        "required_elements": ["specific", "per 100g", "amounts", "not provided"],
        "domain": "food",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_054",
        "difficulty": "medium",
        "subcategory": "granularity_mismatch",
        "query": "How large is the Boeing 787-9 cargo hold and what are its exact dimensions?",
        "contexts": [
            "The Boeing 787-9 Dreamliner is a wide-body, twin-engine commercial aircraft designed for medium to long-haul international routes. It can carry between 250 and 290 passengers depending on the airline's cabin configuration, and has an impressive range of 7,530 nautical miles allowing nonstop flights like Los Angeles to Sydney. The aircraft measures 62.8 meters in overall length with a wingspan of 60.1 meters and a maximum takeoff weight of 254,000 kg. Boeing has delivered over 600 units of the 787-9 variant to airlines worldwide since its entry into service in 2014. The aircraft is widely praised for its fuel efficiency, consuming approximately 20% less fuel per seat than comparable wide-body aircraft like the Airbus A330. Major operators include United Airlines, Delta Air Lines, All Nippon Airways, and Qantas."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for detailed cargo hold specifications but context only gives high-level aircraft overview",
        "rationale": "The context provides general aircraft data without any cargo hold dimensions, volume, or capacity details",
        "required_elements": ["cargo", "dimensions", "not provided", "specifications"],
        "domain": "transportation",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_055",
        "difficulty": "medium",
        "subcategory": "granularity_mismatch",
        "query": "Describe the exact protocol for administering a standardized IQ test to children aged 6-8.",
        "contexts": [
            "Intelligence quotient (IQ) testing in children is an important clinical tool used to assess cognitive abilities and identify giftedness, learning disabilities, and intellectual developmental disorders. The most widely used assessment instruments include the Wechsler Intelligence Scale for Children (WISC-V) and the Stanford-Binet Intelligence Scales, Fifth Edition (SB5). These comprehensive tests measure multiple cognitive domains including verbal comprehension, visual-spatial reasoning, fluid reasoning, working memory, and processing speed. IQ scores follow a normal bell-curve distribution with a population mean of 100 and a standard deviation of 15 points. Testing should be conducted by a licensed psychologist in a quiet, distraction-free clinical environment. Results can be influenced by several factors including test anxiety, cultural and linguistic background, physical health on the testing day, and language proficiency."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for exact administration protocol but context only gives a general overview of IQ testing",
        "rationale": "The context describes IQ tests at a high level without providing specific administration steps or timing protocols",
        "required_elements": ["protocol", "specific", "steps", "not provided"],
        "domain": "psychology",
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
            "min_required": 1,
        },
    },
    # =========================================================================
    # scope_mismatch (5 cases): 056-060
    # =========================================================================
    {
        "id": "t1_relevance_medium_056",
        "difficulty": "medium",
        "subcategory": "scope_mismatch",
        "query": "How much is the minimum wage in Germany as of 2024?",
        "contexts": [
            "The federal minimum wage in France, known as the SMIC (salaire minimum interprofessionnel de croissance), was raised to 11.65 euros per hour effective January 1, 2024, representing a 1.13% increase from the previous rate of 11.52 euros. This translates to a gross monthly salary of approximately 1,766.92 euros for a full-time worker on the standard French 35-hour work week. France's SMIC adjusts automatically each year based on a formula that considers both inflation and average wage growth across the economy. Employers who fail to pay at least the minimum wage face administrative fines of up to 1,500 euros per affected employee. Approximately 2.5 million workers in France, representing about 12% of the private-sector workforce, earn the SMIC or very close to it."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about Germany's minimum wage but context provides France's minimum wage data",
        "rationale": "France and Germany are different countries with different minimum wage laws and rates",
        "required_elements": ["Germany", "France", "different", "not"],
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_057",
        "difficulty": "medium",
        "subcategory": "scope_mismatch",
        "query": "Is homeschooling legal in Sweden?",
        "contexts": [
            "Homeschooling in the United States is legal in all 50 states, though regulations vary significantly from state to state. States like Texas, Alaska, and Idaho have minimal government oversight, requiring no notification to authorities or standardized testing. In contrast, states like New York and Pennsylvania require parents to submit annual assessments, obtain curriculum approval from the local school district, and file regular progress reports. An estimated 3.3 million children were homeschooled in the US as of the 2023-2024 school year. The homeschooling movement has experienced dramatic growth since the COVID-19 pandemic, with a 51% increase from 2019 enrollment levels. Common motivations cited by parents include religious convictions, dissatisfaction with public school quality, and desire for a more flexible educational schedule."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about homeschooling legality in Sweden but context covers US homeschooling laws",
        "rationale": "US homeschooling laws have no bearing on Sweden's legal framework",
        "required_elements": ["Sweden", "United States", "different", "not"],
        "domain": "education",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_058",
        "difficulty": "medium",
        "subcategory": "scope_mismatch",
        "query": "How does the healthcare system in Japan work for foreign residents?",
        "contexts": [
            "South Korea's National Health Insurance (NHI) system provides universal coverage to all residents, including foreign nationals who stay in the country longer than 6 months under valid visa categories. Enrollees pay monthly premiums calculated based on income, averaging 7.09% of salary which is split evenly between employer and employee for salaried workers. The NHI covers approximately 60% of total medical costs, with patients responsible for copayments that vary by service type and facility level. Foreign workers employed by Korean companies are automatically enrolled through their employer's payroll system. International students enrolled at accredited institutions can join the NHI with reduced premium rates. The system is centrally managed by the National Health Insurance Service (NHIS) and includes coverage for doctor visits, hospital stays, prescription drugs, and preventive health screenings."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about Japan's healthcare for foreign residents but context describes South Korea's system",
        "rationale": "South Korea and Japan have different healthcare systems and policies for foreign residents",
        "required_elements": ["Japan", "South Korea", "different", "not"],
        "domain": "medicine",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_059",
        "difficulty": "medium",
        "subcategory": "scope_mismatch",
        "query": "Which data privacy regulations apply to social media companies operating in Brazil?",
        "contexts": [
            "The European Union's General Data Protection Regulation (GDPR), which took full effect in May 2018, imposes strict and comprehensive requirements on social media companies operating within or targeting users in the EU. Under GDPR, companies must obtain explicit, informed consent before collecting any personal data, provide users with the right to access, rectify, and permanently delete their data, and report data breaches to supervisory authorities within 72 hours of discovery. Non-compliance can result in administrative fines of up to 4% of global annual revenue or 20 million euros, whichever is higher. Meta Platforms was fined a record 1.2 billion euros in May 2023 for violating GDPR provisions on transatlantic data transfers. The regulation applies extraterritorially to any company processing data of EU residents, regardless of the company's headquarters location."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about Brazil's data privacy regulations but context covers EU's GDPR",
        "rationale": "Brazil has its own data protection law (LGPD) which differs from the EU's GDPR",
        "required_elements": ["Brazil", "EU", "GDPR", "different"],
        "domain": "social_media",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_060",
        "difficulty": "medium",
        "subcategory": "scope_mismatch",
        "query": "What building codes does Turkey enforce for earthquake-resistant construction?",
        "contexts": [
            "Japan's Building Standard Law, substantially revised after the devastating 2011 Tohoku earthquake and tsunami, requires all new buildings to withstand seismic intensity of 7 on the Japanese Meteorological Agency scale (approximately Richter magnitude 7.0). Base isolation systems using specialized rubber bearings are mandatory for high-rise buildings exceeding 60 meters in height. Steel-reinforced concrete structural members must meet rigorous JIS (Japanese Industrial Standards) specifications with a minimum compressive strength of 21 N/mm2. All building plans undergo a dual structural review process conducted by a qualified structural architect and a separate government-appointed independent inspector. Japan's exceptionally strict building codes have been widely credited with minimizing casualties and structural damage during the January 2024 Noto Peninsula earthquake, where modern code-compliant buildings largely survived without significant structural failure."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks about Turkey's earthquake building codes but context describes Japan's seismic regulations",
        "rationale": "Japan and Turkey have different building codes, enforcement standards, and geological conditions",
        "required_elements": ["Turkey", "Japan", "different", "not"],
        "domain": "law",
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
            "min_required": 1,
        },
    },
    # =========================================================================
    # format_mismatch (4 cases): 061-064
    # =========================================================================
    {
        "id": "t1_relevance_medium_061",
        "difficulty": "medium",
        "subcategory": "format_mismatch",
        "query": "Can you list the top 10 most visited national parks in the US by annual visitor count?",
        "contexts": [
            "America's national parks system attracted over 312 million recreational visitors in 2023, continuing a strong post-pandemic recovery that began in earnest in 2022. The Great Smoky Mountains National Park in Tennessee and North Carolina remains the most popular park by a wide margin, drawing millions of visitors annually who come for its accessible location near major metropolitan areas and its unique status as the only national park with free admission. Western parks like Grand Canyon, Zion, and Yellowstone continue to face severe overcrowding challenges during the peak summer months of June through August. The National Park Service has implemented timed entry reservation systems at several high-demand parks including Arches, Rocky Mountain, and Glacier to manage visitor flow and protect fragile ecosystems. Urban recreation areas including the National Mall and Gateway National Recreation Area also contribute significantly to total system visitation."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for a ranked list with visitor counts but context provides a narrative overview without specific numbers or rankings",
        "rationale": "The context discusses parks narratively without providing the specific ranked list or visitor numbers requested",
        "required_elements": ["list", "visitor count", "specific numbers", "not provided"],
        "domain": "environment",
        "query_type": "compare",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_062",
        "difficulty": "medium",
        "subcategory": "format_mismatch",
        "query": "Compare the specifications of the iPhone 15 Pro and Samsung Galaxy S24 Ultra in a side-by-side format.",
        "contexts": [
            "The premium smartphone market in 2024 continues to be dominated by Apple and Samsung, with both manufacturers pushing the boundaries of mobile technology and commanding prices above $1,000 for their flagship models. The iPhone 15 Pro introduced the A17 Pro chip, the first 3-nanometer processor in any smartphone, delivering significantly improved gaming performance and energy efficiency over its predecessor. Apple also made the long-anticipated switch to USB-C and added a customizable Action Button replacing the traditional mute switch. Meanwhile, Samsung's Galaxy S24 Ultra impressed technology reviewers with its lightweight titanium frame, a 200-megapixel main camera sensor, and an embedded S Pen stylus for note-taking and precise input. Both devices support 5G connectivity and satellite-based emergency messaging for use in areas without cellular coverage. Industry analysts at Counterpoint Research note that the premium segment above $1,000 grew 12% year-over-year."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for a side-by-side comparison but context provides a narrative industry overview",
        "rationale": "The context mentions features of both phones narratively but does not provide a structured comparison with specs",
        "required_elements": ["side-by-side", "comparison", "specifications", "not provided"],
        "domain": "technology",
        "query_type": "compare",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "comparative",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_063",
        "difficulty": "medium",
        "subcategory": "format_mismatch",
        "query": "Give me a checklist of documents needed when applying for a UK spouse visa.",
        "contexts": [
            "Applying for a UK spouse visa (officially known as a Family visa for partners) can be a complex and lengthy process that requires careful preparation and attention to detail. The applicant must demonstrate a genuine and subsisting relationship with their British citizen or settled partner through evidence such as photographs, correspondence, and shared financial records. Financial requirements are stringent, with the sponsoring partner needing to demonstrate an annual income of at least 29,000 pounds sterling as of the April 2024 threshold increase. The application process involves completing an online form on the UK government website, providing biometric data (fingerprints and photograph) at a visa application center, and passing an approved English language test at CEFR level A1 or above. Standard processing times vary between 8 and 24 weeks depending on the applicant's country of residence. Successful applicants receive an initial 33-month visa, after which they can apply for a 30-month extension."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for a document checklist but context provides a narrative overview of the visa process",
        "rationale": "The context describes the process narratively without providing a specific document checklist",
        "required_elements": ["checklist", "documents", "specific", "not provided"],
        "domain": "government",
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
            "min_required": 1,
        },
    },
    {
        "id": "t1_relevance_medium_064",
        "difficulty": "medium",
        "subcategory": "format_mismatch",
        "query": "Provide a timeline of key events in the history of artificial intelligence from 1950 to 2020.",
        "contexts": [
            "Artificial intelligence has transformed from a purely theoretical concept discussed in academic papers into one of the most impactful and disruptive technologies of the modern era, reshaping industries from healthcare to transportation. Early pioneers including Alan Turing, who proposed the famous Turing Test in 1950, and John McCarthy, who coined the term 'artificial intelligence' at the 1956 Dartmouth Conference, laid the philosophical and computational groundwork that would shape decades of subsequent research. The field experienced recurring cycles of intense optimism and investment followed by disillusionment and funding droughts commonly known as 'AI winters,' most notably in the 1970s and late 1980s. Machine learning eventually emerged as the dominant research paradigm, shifting the field's focus from hand-coded expert rules to data-driven statistical approaches. Deep learning, powered by artificial neural networks with many hidden layers, enabled transformative breakthroughs in image recognition, natural language processing, and strategic game playing throughout the 2010s."
        ],
        "expected_mode": "trustworthy",
        "description": "Asks for a chronological timeline with dates but context provides a narrative history without specific dates",
        "rationale": "The context tells the story of AI broadly without providing the specific dates and events needed for a timeline",
        "required_elements": ["timeline", "dates", "specific", "not provided"],
        "domain": "history",
        "query_type": "compare",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "temporal",
        "evidence_pattern": "indirect",
        "category": "relevance",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": False,
            "case_insensitive": True,
            "min_required": 1,
        },
    },
]


def validate_cases(cases):
    """Validate all cases meet requirements."""
    errors = []

    # Check ID uniqueness
    ids = [c["id"] for c in cases]
    if len(ids) != len(set(ids)):
        dupes = [i for i in ids if ids.count(i) > 1]
        errors.append(f"Duplicate IDs: {set(dupes)}")

    # Check ID range
    expected_ids = [f"t1_relevance_medium_{i:03d}" for i in range(10, 65)]
    actual_ids = sorted([c["id"] for c in cases])
    if actual_ids != expected_ids:
        missing = set(expected_ids) - set(actual_ids)
        extra = set(actual_ids) - set(expected_ids)
        if missing:
            errors.append(f"Missing IDs: {missing}")
        if extra:
            errors.append(f"Extra IDs: {extra}")

    required_fields = [
        "id", "difficulty", "subcategory", "query", "contexts",
        "expected_mode", "description", "rationale", "required_elements",
        "domain", "query_type", "source_type", "context_count",
        "reasoning_type", "evidence_pattern", "category", "evaluation_config",
    ]

    from collections import Counter
    subcats = Counter()
    domains = Counter()
    query_types = Counter()

    for i, case in enumerate(cases):
        cid = case.get("id", f"index-{i}")

        # Check all fields present
        for field in required_fields:
            if field not in case:
                errors.append(f"{cid}: missing field '{field}'")

        # Check context word count
        for j, ctx in enumerate(case.get("contexts", [])):
            wc = len(ctx.split())
            if wc < 80:
                errors.append(f"{cid}: context {j} has {wc} words (min 80)")

        # Check required_elements count
        re_count = len(case.get("required_elements", []))
        if re_count < 3 or re_count > 6:
            errors.append(f"{cid}: has {re_count} required_elements (need 3-6)")

        # Check evaluation_config
        ec = case.get("evaluation_config", {})
        if ec.get("mode") != "answer_quality":
            errors.append(f"{cid}: evaluation_config.mode should be 'answer_quality'")
        if ec.get("use_regex") is not False:
            errors.append(f"{cid}: evaluation_config.use_regex should be false")
        if ec.get("case_insensitive") is not True:
            errors.append(f"{cid}: evaluation_config.case_insensitive should be true")
        if ec.get("min_required") != 1:
            errors.append(f"{cid}: evaluation_config.min_required should be 1")

        subcats[case.get("subcategory")] += 1
        domains[case.get("domain")] += 1
        query_types[case.get("query_type")] += 1

    # Domain distribution: no domain > 15% (max ~8 of 55)
    max_domain = 55 * 0.15
    for domain, count in domains.most_common():
        if count > max_domain + 0.5:  # allow rounding
            errors.append(f"Domain '{domain}' has {count} cases (max {int(max_domain) + 1})")

    # Query type distribution: "what" max 30% (~16)
    max_what = 55 * 0.30
    what_count = query_types.get("what", 0)
    if what_count > max_what + 0.5:
        errors.append(f"Query type 'what' has {what_count} cases (max {int(max_what) + 1})")

    # Domain count: at least 8
    if len(domains) < 8:
        errors.append(f"Only {len(domains)} domains (need at least 8)")

    print("=== Validation Results ===")
    print(f"Total cases: {len(cases)}")
    print(f"\nSubcategory distribution:")
    for k, v in subcats.most_common():
        print(f"  {k}: {v}")
    print(f"\nDomain distribution:")
    for k, v in domains.most_common():
        print(f"  {k}: {v}")
    print(f"\nQuery type distribution:")
    for k, v in query_types.most_common():
        print(f"  {k}: {v}")

    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print("\nAll validations passed!")
        return True


def main():
    # Validate new cases first
    print("Validating new cases...")
    if not validate_cases(NEW_CASES):
        print("\nFix validation errors before proceeding.")
        sys.exit(1)

    # Load existing data
    print(f"\nLoading {DATA_FILE}...")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_ids = {c["id"] for c in data["cases"]}
    new_ids = {c["id"] for c in NEW_CASES}

    # Check for conflicts with existing data
    conflicts = existing_ids & new_ids
    if conflicts:
        print(f"ERROR: ID conflicts with existing cases: {conflicts}")
        sys.exit(1)

    # Append new cases
    data["cases"].extend(NEW_CASES)
    print(f"Appended {len(NEW_CASES)} cases. Total: {len(data['cases'])}")

    # Write back
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Written to {DATA_FILE}")


if __name__ == "__main__":
    main()
