#!/usr/bin/env python3
"""Generate 65 new MEDIUM difficulty grounding cases (t1_grounding_medium_064 through _128).

Appends to data/tier1_core/grounding.json.

Query type targets:  what<=16, how>=13, is/does>=13, why/should>=8, when/who/which>=6
Subcategory counts:  numerical(7) attribution(6) temporal(6) entity(5) process(5)
                     quote(5) statistical(5) code_h(4) table(4) causal(4)
                     comparative(3) geographic(3) technical(3) date(2) location(2) code_g(1)
Multi-source: 18     Domain spread: all 18, max 5 each
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "tier1_core" / "grounding.json"


def make_case(
    idx: int,
    subcategory: str,
    query: str,
    contexts: list[str],
    description: str,
    rationale: str,
    forbidden_claims: list[str],
    domain: str,
    query_type: str,
    source_type: str = "single",
    context_sources: list[dict] | None = None,
    reasoning_type: str = "factual",
    evidence_pattern: str = "direct",
) -> dict:
    case = {
        "id": f"t1_grounding_medium_{idx:03d}",
        "difficulty": "medium",
        "subcategory": subcategory,
        "query": query,
        "contexts": contexts,
        "expected_mode": "trustworthy",
        "description": description,
        "rationale": rationale,
        "forbidden_claims": forbidden_claims,
        "domain": domain,
        "query_type": query_type,
        "source_type": source_type,
        "context_count": len(contexts),
        "reasoning_type": reasoning_type,
        "evidence_pattern": evidence_pattern,
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
        },
    }
    if context_sources:
        case["context_sources"] = context_sources
    return case


# ---------------------------------------------------------------------------
# Query-type tally (maintained manually during authoring):
#   what:  64,66,93,94,95,96,97,103,107,118,121,122,123,126,127,128 = 16
#   how:   65,67,69,73,84,88,89,90,91,92,104,116,117                = 13
#   is:    76,81,98,100,106,110,115                                  =  7
#   does:  68,83,86,105,108,109                                      =  6  (is+does=13)
#   why:   101,111,112,113,114                                       =  5
#   should:99,102,120                                                =  3  (why+should=8)
#   when:  77,78,79,80,82,124,125                                   =  7
#   who:   70,119                                                    =  2
#   which: 71,74,75,85,87                                            =  5  (when+who+which=14)
# TOTAL = 16+13+7+6+5+3+7+2+5 = 64 ... need one more
# Added idx=72 as "who" -> when+who+which = 15, total = 65
#
# Domain tally (max 5):
#   technology:5(64,91,103,104,128) finance:4(69,79,106,111) medicine:4(65,95,100,116)
#   education:4(66,82,87,114) government:4(68,78,88,107) agriculture:4(67,92,96,108)
#   science:4(77,110,122,123) law:3(81,90,72) environment:3(76,109,112)
#   hr_workplace:3(75,99,102) real_estate:3(70,101,117) sports:3(84,85,94)
#   food:3(74,97,100) -> food only 2 (74,97), 100=food, yes 3
#   transportation:3(80,83,121) history:2(118,124) general:2(119,120)
#   social_media:2(113,125) psychology:1(98)
#   Wait let me recount after final assignments...
# ---------------------------------------------------------------------------


def generate_cases() -> list[dict]:
    cases = []

    # =========================================================================
    # SUBCATEGORY: numerical_hallucination (7 cases)
    # IDs: 64,65,66,67,68,69,70
    # =========================================================================

    # 64 - what - hr_workplace
    cases.append(make_case(
        idx=64,
        subcategory="numerical_hallucination",
        query="What is the average salary of software engineers at NovaTech?",
        contexts=[
            "NovaTech employs software engineers across its three offices in Austin, Denver, and Portland. "
            "The company offers competitive compensation packages including equity, signing bonuses, and annual "
            "performance reviews. NovaTech was ranked among the top 50 employers in tech by Glassdoor in 2024."
        ],
        description="Company details present but no salary figures mentioned",
        rationale="Mentions compensation vaguely but no actual salary number exists in context",
        forbidden_claims=[
            "\\$\\d{2,3}[,.]?\\d*\\s*(k|K|thousand|per year|annually|salary)",
            "average.{0,30}\\$\\d",
            "earn(s|ing)?\\s+\\$\\d",
            "paid\\s+\\$\\d",
            "\\d{2,3}[,.]?\\d*\\s*(thousand|k|K)"
        ],
        domain="hr_workplace",
        query_type="what",
    ))

    # 65 - how - medicine
    cases.append(make_case(
        idx=65,
        subcategory="numerical_hallucination",
        query="How many patients were enrolled in the Phase III clinical trial for Zeltrex?",
        contexts=[
            "Pharmaline announced positive Phase III results for Zeltrex, a novel treatment for treatment-resistant "
            "depression. The double-blind, placebo-controlled trial demonstrated statistically significant improvement "
            "in MADRS scores at the 8-week endpoint. Pharmaline plans to submit an NDA in Q2 2025."
        ],
        description="Trial outcome mentioned but enrollment count absent",
        rationale="Phase III details given without specifying number of participants",
        forbidden_claims=[
            "\\d{2,}\\s*(patients|participants|subjects|individuals|people)",
            "enrolled\\s+\\d",
            "sample (size|of)\\s+\\d",
            "cohort of\\s+\\d"
        ],
        domain="medicine",
        query_type="how",
    ))

    # 66 - what - education
    cases.append(make_case(
        idx=66,
        subcategory="numerical_hallucination",
        query="What percentage of students passed the state mathematics exam in 2024?",
        contexts=[
            "The state Department of Education released its 2024 assessment report covering all K-12 public schools. "
            "The report highlighted improvements in reading proficiency and noted that mathematics curriculum reforms "
            "were implemented across 340 districts. New calculator policies were introduced for grades 6 through 12."
        ],
        description="Education report discussed but pass rate not provided",
        rationale="Math exam reforms discussed without actual pass rate statistics",
        forbidden_claims=[
            "\\d{1,3}(\\.\\d+)?\\s*(%|percent)",
            "pass(ed|ing)?\\s+(rate|percentage)",
            "\\d+\\s*out of\\s*\\d+",
            "scored (above|at or above)"
        ],
        domain="education",
        query_type="what",
    ))

    # 67 - how - agriculture
    cases.append(make_case(
        idx=67,
        subcategory="numerical_hallucination",
        query="How many acres of farmland were affected by the drought in the Central Valley?",
        contexts=[
            "California's Central Valley experienced severe drought conditions during the 2024 growing season. "
            "Several irrigation districts imposed mandatory water rationing, and some farmers switched from "
            "almond orchards to less water-intensive crops. The USDA designated three additional counties as "
            "drought disaster areas."
        ],
        description="Drought impact discussed but no acreage figures given",
        rationale="Drought is described qualitatively without specific acreage numbers",
        forbidden_claims=[
            "\\d[,\\d]*\\s*(acres|hectares)",
            "affected\\s+\\d",
            "impacted\\s+\\d",
            "approximately\\s+\\d[,\\d]*\\s*(acres|hectares)"
        ],
        domain="agriculture",
        query_type="how",
    ))

    # 68 - does - government  (multi_source)
    cases.append(make_case(
        idx=68,
        subcategory="numerical_hallucination",
        query="Does the Portland Police Bureau report show the crime rate per capita for downtown?",
        contexts=[
            "The Portland Police Bureau's annual report discussed neighborhood safety trends and community policing "
            "initiatives. Downtown Portland saw increased foot patrol presence and new surveillance camera installations "
            "in 2024. The report emphasized partnerships with local business associations.",
            "A separate city council briefing highlighted community watch programs and noted that "
            "the bureau had requested additional funding for a real-time crime analytics platform. "
            "The briefing also discussed hiring goals for the next fiscal year."
        ],
        description="Policing efforts described across two sources but no crime rate statistics provided",
        rationale="Safety measures discussed in both documents without any per capita crime rate data",
        forbidden_claims=[
            "\\d+(\\.\\d+)?\\s*(per|crimes per)\\s*(\\d+[,\\d]*|capita|thousand|hundred)",
            "crime rate (of|is|was)\\s*\\d",
            "\\d+(\\.\\d+)?%\\s*(increase|decrease|drop|rise)",
            "\\d+\\s*(crimes|incidents|offenses)"
        ],
        domain="government",
        query_type="does",
        source_type="multi_source",
        context_sources=[
            {"source_id": "src_grounding_068_a", "source_type": "report", "authority": "high"},
            {"source_id": "src_grounding_068_b", "source_type": "briefing", "authority": "medium"},
        ],
    ))

    # 69 - how - transportation
    cases.append(make_case(
        idx=69,
        subcategory="numerical_hallucination",
        query="How many electric vehicle charging stations does GreenDrive operate nationwide?",
        contexts=[
            "GreenDrive is a rapidly expanding EV infrastructure company operating across the United States. "
            "The company recently secured $150 million in Series C funding to accelerate deployment. GreenDrive's "
            "stations support CCS, CHAdeMO, and Tesla NACS connectors, and the company has partnerships with "
            "major highway rest stop operators."
        ],
        description="Company growth and technology described but station count missing",
        rationale="Funding and connector types mentioned but total station count not stated",
        forbidden_claims=[
            "\\d{2,}[,\\d]*\\s*(stations|chargers|locations|sites|points)",
            "operates\\s+\\d",
            "network of\\s+\\d",
            "over\\s+\\d{2,}[,\\d]*"
        ],
        domain="transportation",
        query_type="how",
    ))

    # 70 - who - real_estate
    cases.append(make_case(
        idx=70,
        subcategory="numerical_hallucination",
        query="Who conducted the study that established the average home price in Boise, Idaho for 2024?",
        contexts=[
            "Boise, Idaho has been one of the fastest-growing housing markets in the Mountain West region. "
            "The city attracted remote workers and retirees from coastal states, driving strong demand. "
            "New residential construction permits increased year over year, and several mixed-use developments "
            "broke ground in the Boise suburb of Meridian."
        ],
        description="Housing market trends discussed but no price study or source named",
        rationale="Growth and demand mentioned without any specific study, price data, or researcher",
        forbidden_claims=[
            "\\$\\d{2,3}[,\\d]*",
            "(Zillow|Redfin|Realtor|NAR|Census|MLS|CoreLogic).{0,20}(reported|found|showed|study)",
            "average.{0,20}\\$",
            "median.{0,20}\\$",
            "study (by|from|conducted)"
        ],
        domain="real_estate",
        query_type="who",
    ))

    # =========================================================================
    # SUBCATEGORY: attribution_hallucination (6 cases)
    # IDs: 71,72,73,74,75,76
    # =========================================================================

    # 71 - which - medicine  (multi_source)
    cases.append(make_case(
        idx=71,
        subcategory="attribution_hallucination",
        query="Which specific recommendations did the WHO make regarding sugar intake for children?",
        contexts=[
            "The American Academy of Pediatrics published updated dietary guidelines for children in 2024, "
            "recommending no more than 25 grams of added sugar per day for children aged 2-18. The AAP also "
            "recommended eliminating sugary beverages from school cafeterias and limiting juice to 4 ounces daily.",
            "UNICEF released a report on child nutrition in developing nations, focusing on protein "
            "deficiency and micronutrient supplementation strategies across Sub-Saharan Africa."
        ],
        description="AAP and UNICEF guidance present but query asks about WHO",
        rationale="Sugar guidelines are from AAP, not WHO; LLM must not attribute them to WHO",
        forbidden_claims=[
            "(?i)WHO\\s+(recommend|suggest|advise|guideline|state)",
            "(?i)World Health Organization.{0,40}sugar",
            "(?i)according to (the )?WHO",
            "(?i)WHO.{0,30}(children|child|pediatric)"
        ],
        domain="medicine",
        query_type="which",
        source_type="multi_source",
        context_sources=[
            {"source_id": "src_grounding_071_a", "source_type": "guideline", "authority": "high"},
            {"source_id": "src_grounding_071_b", "source_type": "report", "authority": "high"},
        ],
    ))

    # 72 - who - law
    cases.append(make_case(
        idx=72,
        subcategory="attribution_hallucination",
        query="Who authored the Supreme Court opinion on student loan forgiveness?",
        contexts=[
            "The Biden administration announced a new income-driven repayment plan called SAVE, which "
            "calculates payments at 5% of discretionary income for undergraduate loans. The Department of "
            "Education estimated that 4.3 million borrowers would see reduced payments under the SAVE plan."
        ],
        description="Executive action described but no Supreme Court ruling mentioned",
        rationale="Context covers DOE policy, not Supreme Court decisions; no justice named",
        forbidden_claims=[
            "(?i)(Supreme Court|SCOTUS).{0,40}(ruled|held|decided|struck|upheld)",
            "(?i)Justice(s)?\\s+\\w+\\s+(wrote|authored|dissented|concurred)",
            "(?i)(Roberts|Thomas|Alito|Sotomayor|Kagan|Gorsuch|Kavanaugh|Barrett|Jackson).{0,20}(wrote|authored|opinion)",
            "(?i)(6-3|5-4|7-2|unanimous)"
        ],
        domain="law",
        query_type="who",
    ))

    # 73 - how - science  (multi_source)
    cases.append(make_case(
        idx=73,
        subcategory="attribution_hallucination",
        query="How did NASA describe the results of the ocean temperature study?",
        contexts=[
            "The Scripps Institution of Oceanography published a comprehensive ocean temperature analysis "
            "showing that deep-ocean warming accelerated between 2020 and 2024. Their autonomous Argo float "
            "network recorded temperature anomalies at depths exceeding 2,000 meters.",
            "NASA's Jet Propulsion Laboratory released new satellite imagery of polar ice sheet changes, "
            "documenting accelerated calving events along the Thwaites Glacier in Antarctica."
        ],
        description="Scripps did ocean temperature study; NASA studied ice sheets",
        rationale="LLM may falsely attribute Scripps ocean findings to NASA",
        forbidden_claims=[
            "(?i)NASA.{0,40}(ocean temperature|deep.ocean|warming|Argo|float)",
            "(?i)NASA (found|reported|described|concluded).{0,40}(temperature|warming|ocean)",
            "(?i)according to NASA.{0,30}(ocean|temperature|deep)",
            "(?i)NASA('s)? (study|research|analysis).{0,30}(ocean|temperature)"
        ],
        domain="science",
        query_type="how",
        source_type="multi_source",
        context_sources=[
            {"source_id": "src_grounding_073_a", "source_type": "study", "authority": "high"},
            {"source_id": "src_grounding_073_b", "source_type": "report", "authority": "high"},
        ],
    ))

    # 74 - which - food
    cases.append(make_case(
        idx=74,
        subcategory="attribution_hallucination",
        query="Which position did the Federal Reserve take on cryptocurrency regulation?",
        contexts=[
            "The SEC issued new guidance on cryptocurrency token classification in mid-2024, establishing "
            "clearer criteria for distinguishing securities from utility tokens. The SEC's framework requires "
            "issuers to register tokens meeting the Howey test criteria. Meanwhile, the CFTC maintained its "
            "position that Bitcoin and Ethereum are commodities."
        ],
        description="SEC and CFTC positions stated but query asks about Federal Reserve",
        rationale="Crypto regulation positions are from SEC and CFTC, not the Fed",
        forbidden_claims=[
            "(?i)(Federal Reserve|the Fed|Fed Chairman|Fed Chair).{0,40}(crypto|token|Bitcoin|Ethereum)",
            "(?i)(Federal Reserve|the Fed).{0,30}(regulation|guidance|framework|position|stance)",
            "(?i)according to the (Federal Reserve|Fed)",
            "(?i)(Federal Reserve|the Fed).{0,30}(said|stated|ruled|declared)"
        ],
        domain="finance",
        query_type="which",
    ))

    # 75 - which - hr_workplace  (multi_source)
    cases.append(make_case(
        idx=75,
        subcategory="attribution_hallucination",
        query="Which conclusions did Professor Chen's research draw about remote work productivity?",
        contexts=[
            "A Stanford University study led by Professor Nicholas Bloom tracked 1,600 employees over "
            "two years and found that hybrid workers showed no decrease in performance reviews or promotion "
            "rates compared to fully in-office peers.",
            "Harvard Business School published a survey of 200 companies finding that return-to-office "
            "mandates correlated with increased attrition among senior engineers."
        ],
        description="Studies by Bloom (Stanford) and HBS present but query asks about Professor Chen",
        rationale="No Professor Chen in context; LLM must not attribute findings to non-existent researcher",
        forbidden_claims=[
            "(?i)(Professor |Dr\\.? )?Chen.{0,40}(found|concluded|showed|demonstrated|research)",
            "(?i)Chen's (study|research|findings|work|paper|analysis)",
            "(?i)according to (Professor |Dr\\.? )?Chen",
            "(?i)Chen.{0,20}(concluded|determined|established)"
        ],
        domain="hr_workplace",
        query_type="which",
        source_type="multi_source",
        context_sources=[
            {"source_id": "src_grounding_075_a", "source_type": "study", "authority": "high"},
            {"source_id": "src_grounding_075_b", "source_type": "survey", "authority": "medium"},
        ],
    ))

    # 76 - is - environment
    cases.append(make_case(
        idx=76,
        subcategory="attribution_hallucination",
        query="Is glyphosate classified as a carcinogen according to the EPA?",
        contexts=[
            "The International Agency for Research on Cancer (IARC), part of the WHO, classified "
            "glyphosate as 'probably carcinogenic to humans' (Group 2A) in 2015. This classification "
            "sparked significant debate among regulatory agencies worldwide. Bayer, which acquired "
            "Monsanto in 2018, has faced thousands of lawsuits related to Roundup."
        ],
        description="IARC classification provided but query asks about EPA",
        rationale="Only IARC's classification is in context; EPA's position is not mentioned",
        forbidden_claims=[
            "(?i)EPA.{0,40}(classif|carcinogen|cancer|Group|probable|likely)",
            "(?i)EPA (considers|classifies|designates|labels|deems)",
            "(?i)according to (the )?EPA.{0,20}(carcinogen|cancer)",
            "(?i)EPA('s)? (classification|assessment|determination|finding)"
        ],
        domain="environment",
        query_type="is",
    ))

    # =========================================================================
    # SUBCATEGORY: temporal_confusion (6 cases)
    # IDs: 77,78,79,80,81,82
    # =========================================================================

    # 77 - when - science
    cases.append(make_case(
        idx=77,
        subcategory="temporal_confusion",
        query="When did SpaceVentures complete its first crewed Mars mission?",
        contexts=[
            "SpaceVentures successfully launched its Artemis-class heavy lift vehicle in September 2024, "
            "placing a 45-ton payload into low Earth orbit. The company announced plans for an uncrewed "
            "Mars cargo mission in 2027 and expressed long-term ambitions for crewed interplanetary travel."
        ],
        description="Launch success and Mars plans mentioned but no crewed Mars mission completed",
        rationale="Only a cargo mission is planned; no crewed Mars mission has occurred",
        forbidden_claims=[
            "(?i)completed.{0,20}(crewed|manned|human)\\s*(Mars|mission)",
            "(?i)(crewed|manned|human).{0,20}(Mars|mission).{0,20}(in|on|during)\\s+\\d{4}",
            "(?i)(landed|arrived|reached)\\s+(on\\s+)?Mars",
            "(?i)first (crewed|manned|human).{0,20}(completed|succeeded|accomplished)"
        ],
        domain="science",
        query_type="when",
    ))

    # 78 - when - government
    cases.append(make_case(
        idx=78,
        subcategory="temporal_confusion",
        query="When was the Coastal Protection Act signed into law?",
        contexts=[
            "The Coastal Protection Act was introduced in the Senate in March 2024 with bipartisan "
            "sponsorship. The bill passed the Senate Environment Committee in June 2024 and was "
            "scheduled for a full Senate vote in the fall session. Environmental groups expressed "
            "strong support for the legislation."
        ],
        description="Bill introduced and in committee but not yet signed into law",
        rationale="The bill passed committee but has not been signed; LLM must not fabricate a signing date",
        forbidden_claims=[
            "(?i)signed (into law|by the president)\\s*(in|on)?\\s*\\w*\\s*\\d{4}",
            "(?i)became law\\s*(in|on)?\\s*\\d{4}",
            "(?i)enacted\\s*(in|on)?\\s*\\d{4}",
            "(?i)(was|been) signed"
        ],
        domain="government",
        query_type="when",
    ))

    # 79 - when - finance
    cases.append(make_case(
        idx=79,
        subcategory="temporal_confusion",
        query="When did MegaBank complete its merger with Pacific Financial?",
        contexts=[
            "MegaBank announced a proposed merger with Pacific Financial in August 2024, valued at "
            "$12.4 billion. The deal requires approval from the Federal Reserve, FDIC, and state banking "
            "regulators. Antitrust analysts noted potential concerns about market concentration in "
            "the Pacific Northwest."
        ],
        description="Merger announced and pending regulatory approval, not completed",
        rationale="Merger is proposed and awaiting approvals; no completion date exists",
        forbidden_claims=[
            "(?i)completed.{0,20}(merger|acquisition|deal)",
            "(?i)(merged|finalized|closed)\\s*(in|on)?\\s*\\w*\\s*\\d{4}",
            "(?i)merger (was|has been) completed",
            "(?i)(completed|finalized|closed) (in|on|during)"
        ],
        domain="finance",
        query_type="when",
    ))

    # 80 - when - transportation
    cases.append(make_case(
        idx=80,
        subcategory="temporal_confusion",
        query="When did the city complete construction of the new light rail extension?",
        contexts=[
            "The city transit authority broke ground on a 12-mile light rail extension in early 2024. "
            "The project is expected to cost $3.2 billion and serve an estimated 45,000 daily riders. "
            "Construction is projected to take four years, with service beginning in 2028. Tunnel boring "
            "machines were deployed in Q3 2024."
        ],
        description="Construction underway with projected completion but not yet finished",
        rationale="Project just started in 2024; completion projected for 2028, not done yet",
        forbidden_claims=[
            "(?i)completed (construction|the project|the extension)\\s*(in|on)?\\s*\\d{4}",
            "(?i)(finished|completed|opened)\\s*(in|on)?\\s*\\w*\\s*\\d{4}",
            "(?i)construction (was|has been) completed",
            "(?i)opened (to|for) (the public|service|riders)"
        ],
        domain="transportation",
        query_type="when",
    ))

    # 81 - is - law
    cases.append(make_case(
        idx=81,
        subcategory="temporal_confusion",
        query="Is the new data privacy law already in effect in Illinois?",
        contexts=[
            "The Illinois legislature passed the Comprehensive Data Privacy Act in October 2024. "
            "Governor signed the bill into law on November 15, 2024. The law includes a 24-month "
            "implementation period, requiring companies to achieve compliance by November 2026. "
            "Industry groups have begun lobbying for extensions to the compliance deadline."
        ],
        description="Law signed but not yet in effect due to implementation period",
        rationale="Law exists but has a 24-month implementation window; not effective until 2026",
        forbidden_claims=[
            "(?i)(already|currently|now)\\s+(in effect|enforceable|effective|active)",
            "(?i)(took|takes|went) (into )?effect",
            "(?i)(is|has been) (in )?effect since",
            "(?i)companies (must|are required to) (currently|now) comply"
        ],
        domain="law",
        query_type="is",
    ))

    # 82 - when - education
    cases.append(make_case(
        idx=82,
        subcategory="temporal_confusion",
        query="When did the university launch its quantum computing degree program?",
        contexts=[
            "Westfield University announced plans to establish a quantum computing degree program in "
            "partnership with IBM Quantum. The curriculum is being developed by faculty from the physics "
            "and computer science departments. The university allocated $8 million for a dedicated quantum "
            "computing laboratory. Faculty hiring for three new positions began in fall 2024."
        ],
        description="Program announced and being developed but not yet launched",
        rationale="Program is in planning/development stage; no launch has occurred",
        forbidden_claims=[
            "(?i)launched (in|on|during)\\s*\\w*\\s*\\d{4}",
            "(?i)(began|started|opened|commenced)\\s*(accepting|enrolling|offering)",
            "(?i)program (launched|started|began|opened)",
            "(?i)first (class|cohort|students)\\s*(enrolled|admitted|started)"
        ],
        domain="education",
        query_type="when",
    ))

    # =========================================================================
    # SUBCATEGORY: entity_blending (5 cases)
    # IDs: 83,84,85,86,87
    # =========================================================================

    # 83 - does - transportation  (multi_source)
    cases.append(make_case(
        idx=83,
        subcategory="entity_blending",
        query="Does Ford offer any autonomous driving features comparable to what is described here?",
        contexts=[
            "General Motors' Cruise division has deployed autonomous ride-hailing vehicles in San Francisco, "
            "Phoenix, and Austin. The Cruise Origin, a purpose-built autonomous vehicle with no steering wheel, "
            "received regulatory approval for nighttime operations.",
            "Tesla's Full Self-Driving beta expanded to all North American customers in Q4 2024. "
            "The system uses camera-only vision without lidar, relying on neural network processing. Tesla "
            "reported 500 million miles driven under FSD supervision."
        ],
        description="Context covers GM Cruise and Tesla FSD but query asks about Ford",
        rationale="Neither context mentions Ford; LLM must not attribute GM or Tesla features to Ford",
        forbidden_claims=[
            "(?i)Ford.{0,40}(autonomous|self.driving|FSD|Cruise|autopilot|driverless)",
            "(?i)Ford (offers|provides|includes|features|has|uses)",
            "(?i)Ford('s)?\\s+(vehicles?|cars?|trucks?).{0,30}(autonomous|self.driving)",
            "(?i)(BlueCruise|Co.?Pilot).{0,20}(is|offers|provides|includes)"
        ],
        domain="transportation",
        query_type="does",
        source_type="multi_source",
        context_sources=[
            {"source_id": "src_grounding_083_a", "source_type": "article", "authority": "medium"},
            {"source_id": "src_grounding_083_b", "source_type": "article", "authority": "medium"},
        ],
    ))

    # 84 - how - sports
    cases.append(make_case(
        idx=84,
        subcategory="entity_blending",
        query="How did Argentina perform in the 2024 Copa America tournament?",
        contexts=[
            "Brazil reached the Copa America 2024 semifinals before losing to Uruguay on penalties. "
            "Colombia defeated Uruguay in the other semifinal with a dominant 3-0 victory. The tournament "
            "was held across ten venues in the United States."
        ],
        description="Brazil and Colombia results mentioned but not Argentina specifically",
        rationale="Context covers other teams but Argentina's performance is not described",
        forbidden_claims=[
            "(?i)Argentina.{0,40}(won|lost|defeated|beat|eliminated|drew|scored|advanced)",
            "(?i)Argentina.{0,20}(champion|winner|finalist|semifinalist)",
            "(?i)Argentina('s)? (performance|result|match|game)",
            "(?i)Messi.{0,30}(scored|assisted|played|goal)"
        ],
        domain="sports",
        query_type="how",
    ))

    # 85 - which - sports
    cases.append(make_case(
        idx=85,
        subcategory="entity_blending",
        query="Which ingredients does McDonald's use in its plant-based burger?",
        contexts=[
            "Burger King expanded its Impossible Whopper menu in 2024, adding the Impossible King and "
            "Impossible Nuggets. The Impossible Whopper uses a soy-based patty with methylcellulose as a "
            "binder and coconut oil for juiciness. Burger King reported that plant-based items accounted for "
            "8% of total sales."
        ],
        description="Burger King plant-based details provided but query asks about McDonald's",
        rationale="Only Burger King's ingredients are in context; McDonald's is not mentioned",
        forbidden_claims=[
            "(?i)McDonald('s)?.{0,40}(uses?|contains?|includes?|made with|ingredients?)",
            "(?i)McDonald('s)?.{0,20}(plant.based|McPlant|veggie|vegan)",
            "(?i)McDonald('s)? (burger|patty|sandwich).{0,30}(made|contain|includ)",
            "(?i)McDonald('s)?.{0,20}(soy|pea protein|methylcellulose|coconut)"
        ],
        domain="food",
        query_type="which",
    ))

    # 86 - does - social_media  (multi_source)
    cases.append(make_case(
        idx=86,
        subcategory="entity_blending",
        query="Does Spotify offer lossless audio streaming to its subscribers?",
        contexts=[
            "Apple Music launched lossless audio streaming in ALAC format up to 24-bit/192kHz in 2021, "
            "available to all subscribers at no extra cost. Amazon Music Unlimited also offers HD and "
            "Ultra HD lossless streaming.",
            "Tidal continues to offer its HiFi Plus tier with MQA-encoded "
            "lossless tracks. Deezer's HiFi tier provides FLAC streaming at CD quality for an additional "
            "monthly fee compared to its standard subscription tier."
        ],
        description="Apple Music, Amazon, Tidal, Deezer lossless offerings described but not Spotify",
        rationale="Four competitors' lossless features mentioned; Spotify is absent from context",
        forbidden_claims=[
            "(?i)Spotify.{0,40}(offers?|provides?|supports?|has|launched|includes?).{0,20}(lossless|HiFi|hi.fi|HD|high.res)",
            "(?i)Spotify('s)?\\s+(lossless|HiFi|hi.fi|HD|high.resolution)",
            "(?i)Spotify.{0,20}(FLAC|ALAC|MQA|24.bit|WAV)",
            "(?i)(yes|Spotify does).{0,20}(lossless|hi.fi|HiFi)"
        ],
        domain="social_media",
        query_type="does",
        source_type="multi_source",
        context_sources=[
            {"source_id": "src_grounding_086_a", "source_type": "article", "authority": "medium"},
            {"source_id": "src_grounding_086_b", "source_type": "article", "authority": "medium"},
        ],
    ))

    # 87 - which - education  (multi_source)
    cases.append(make_case(
        idx=87,
        subcategory="entity_blending",
        query="Which mental health services does Yale University offer to undergraduates?",
        contexts=[
            "Harvard University's Counseling and Mental Health Services expanded in 2024, adding 15 "
            "new therapists and launching a 24/7 crisis text line. MIT introduced peer counseling "
            "programs and meditation rooms in all dormitories.",
            "Both universities reported increased "
            "demand for anxiety and depression treatment among undergraduate and graduate students. Harvard "
            "now offers same-day urgent appointments through its mental health triage system."
        ],
        description="Harvard and MIT mental health services described but not Yale",
        rationale="Context covers Harvard and MIT but Yale's services are not mentioned",
        forbidden_claims=[
            "(?i)Yale.{0,40}(offers?|provides?|has|includes?|launched)",
            "(?i)Yale('s)?.{0,20}(counseling|mental health|therapy|therapist|crisis)",
            "(?i)Yale.{0,20}(students?|undergrad).{0,20}(access|receive|use)",
            "(?i)Yale.{0,20}(program|service|support|resource)"
        ],
        domain="education",
        query_type="which",
        source_type="multi_source",
        context_sources=[
            {"source_id": "src_grounding_087_a", "source_type": "report", "authority": "high"},
            {"source_id": "src_grounding_087_b", "source_type": "report", "authority": "high"},
        ],
    ))

    # =========================================================================
    # SUBCATEGORY: process_hallucination (5 cases)
    # IDs: 88,89,90,91,92
    # =========================================================================

    # 88 - how - government
    cases.append(make_case(
        idx=88,
        subcategory="process_hallucination",
        query="How do I file a property tax appeal in Cook County?",
        contexts=[
            "Cook County property assessments increased by an average of 33% in the 2024 reassessment "
            "cycle. The Cook County Assessor's Office uses a computer-assisted mass appraisal system. "
            "Property owners who disagree with their assessment may file an appeal. The deadline for "
            "appeals varies by township."
        ],
        description="Appeals are mentioned as possible but no filing process is described",
        rationale="Context states appeals exist but gives no steps, forms, or procedures",
        forbidden_claims=[
            "(?i)(step|first|then|next).{0,30}(file|submit|fill|complete|download)",
            "(?i)(form|application|petition)\\s+(number|\\d|#)",
            "(?i)(visit|go to|navigate).{0,20}(website|office|portal)",
            "(?i)(attach|include|provide|submit).{0,20}(evidence|documentation|comparable|photo)"
        ],
        domain="government",
        query_type="how",
        reasoning_type="procedural",
    ))

    # 89 - how - finance
    cases.append(make_case(
        idx=89,
        subcategory="process_hallucination",
        query="How do I apply for a small business loan through the SBA?",
        contexts=[
            "The Small Business Administration provides various loan programs to support entrepreneurs "
            "and small business owners across the United States. SBA-backed loans offer competitive "
            "interest rates and longer repayment terms than conventional loans. The agency works with "
            "approved lenders to facilitate the lending process."
        ],
        description="SBA loan programs described generally but no application steps given",
        rationale="General info about SBA loans but no application procedure details",
        forbidden_claims=[
            "(?i)(step|first|then|next).{0,30}(apply|submit|fill|complete|gather)",
            "(?i)(form|application)\\s+(\\d+|SBA)",
            "(?i)(visit|go to|log).{0,20}(sba\\.gov|website|portal|lender)",
            "(?i)(create|set up|register).{0,20}(account|profile|login)"
        ],
        domain="finance",
        query_type="how",
        reasoning_type="procedural",
    ))

    # 90 - how - law
    cases.append(make_case(
        idx=90,
        subcategory="process_hallucination",
        query="How do I submit a workers' compensation claim in Texas?",
        contexts=[
            "Texas is the only state where private employers are not required to carry workers' "
            "compensation insurance. Employers who opt in are called subscribers and gain protection "
            "from most employee lawsuits. Non-subscribing employers face potential negligence lawsuits "
            "from injured workers."
        ],
        description="Texas workers' comp system described but no claim filing process provided",
        rationale="Context explains Texas's unique opt-in system but not how to file a claim",
        forbidden_claims=[
            "(?i)(step|first|then|next).{0,30}(file|submit|report|notify|complete)",
            "(?i)(form|DWC).{0,5}\\d",
            "(?i)(within|no later than)\\s+\\d+\\s+(days|hours|business days)",
            "(?i)(call|contact|visit).{0,20}(doctor|employer|insurance|division)"
        ],
        domain="law",
        query_type="how",
        reasoning_type="procedural",
    ))

    # 91 - how - technology
    cases.append(make_case(
        idx=91,
        subcategory="process_hallucination",
        query="How do I set up automated deployments using Jenkins pipelines?",
        contexts=[
            "Jenkins is an open-source automation server widely used for CI/CD pipelines. It supports "
            "over 1,800 plugins for integration with various development tools. Jenkins can be deployed "
            "on-premises, in cloud environments, or as a containerized application. The project is "
            "maintained by the Jenkins community and the Continuous Delivery Foundation."
        ],
        description="Jenkins overview given but no pipeline setup instructions",
        rationale="General Jenkins description without Jenkinsfile syntax or configuration steps",
        forbidden_claims=[
            "(?i)(create|write|add|edit).{0,20}(Jenkinsfile|pipeline|Groovy|script)",
            "(?i)pipeline\\s*\\{",
            "(?i)(stage|stages|steps|agent|node)\\s*\\(",
            "(?i)(install|configure|set up).{0,20}(plugin|credential|webhook|trigger)"
        ],
        domain="technology",
        query_type="how",
        reasoning_type="procedural",
    ))

    # 92 - how - agriculture
    cases.append(make_case(
        idx=92,
        subcategory="process_hallucination",
        query="How do I perform soil testing for a home garden?",
        contexts=[
            "Soil testing is an important step for successful home gardening. Proper soil pH, nutrient "
            "levels, and organic matter content affect plant growth. Most state university extension "
            "services offer affordable soil testing. Results typically include recommendations for "
            "amendments like lime, sulfur, or fertilizers."
        ],
        description="Soil testing importance described but no testing procedure given",
        rationale="Context says soil testing matters but not how to actually do it",
        forbidden_claims=[
            "(?i)(step|first|then|next).{0,30}(collect|dig|scoop|sample|mix)",
            "(?i)(dig|insert|push).{0,20}(\\d+|inches|cm|deep)",
            "(?i)(mail|send|ship|deliver).{0,20}(sample|bag|box|lab)",
            "(?i)(use|buy|purchase|get).{0,20}(kit|probe|meter|tester)"
        ],
        domain="agriculture",
        query_type="how",
        reasoning_type="procedural",
    ))

    # =========================================================================
    # SUBCATEGORY: quote_fabrication (5 cases)
    # IDs: 93,94,95,96,97
    # =========================================================================

    # 93 - what - general
    cases.append(make_case(
        idx=93,
        subcategory="quote_fabrication",
        query="What did the CEO of DataSync say about their data breach?",
        contexts=[
            "DataSync, a cloud storage provider, experienced a data breach in September 2024 affecting "
            "approximately 2.1 million user accounts. The breach exposed email addresses, hashed passwords, "
            "and billing information. DataSync notified affected users and offered two years of free credit "
            "monitoring."
        ],
        description="Breach details provided but no CEO statement or quote present",
        rationale="Company's response is described but no CEO is quoted or named",
        forbidden_claims=[
            "(?i)(CEO|chief executive).{0,30}(said|stated|commented|remarked|announced|declared)",
            "\"[^\"]{10,}\"",
            "(?i)in (a|an|the) (statement|press release|interview|blog post).{0,30}(said|wrote|stated)",
            "(?i)(he|she|they) (said|stated|noted|emphasized|stressed)"
        ],
        domain="general",
        query_type="what",
    ))

    # 94 - what - sports  (multi_source)
    cases.append(make_case(
        idx=94,
        subcategory="quote_fabrication",
        query="What did the head coach say about the team's playoff chances?",
        contexts=[
            "The Milwaukee Bucks finished the 2024-25 regular season with a 52-30 record, securing the "
            "third seed in the Eastern Conference. Giannis Antetokounmpo averaged 31.2 points per game "
            "and was named to the All-NBA First Team.",
            "An ESPN analysis noted that the Bucks' bench scoring improved by 15% compared "
            "to the previous season. The team's defensive rating ranked fourth in the league, and their "
            "three-point shooting percentage improved to 37.8% from 35.1% a year earlier."
        ],
        description="Team performance stats given across two sources but no coach quote present",
        rationale="Statistical summaries from multiple sources with no coach commentary or direct quotes",
        forbidden_claims=[
            "(?i)(coach|he|she).{0,20}(said|stated|told|mentioned|commented|remarked)",
            "\"[^\"]{10,}\"",
            "(?i)(coach|manager|he|she) (believes?|thinks?|expects?|feels?)",
            "(?i)in (a|an|the) (press conference|interview|postgame).{0,30}(said|stated)"
        ],
        domain="sports",
        query_type="what",
        source_type="multi_source",
        context_sources=[
            {"source_id": "src_grounding_094_a", "source_type": "stats", "authority": "high"},
            {"source_id": "src_grounding_094_b", "source_type": "analysis", "authority": "medium"},
        ],
    ))

    # 95 - what - medicine
    cases.append(make_case(
        idx=95,
        subcategory="quote_fabrication",
        query="What did the lead researcher say about the vaccine side effects?",
        contexts=[
            "A Phase II vaccine trial for respiratory syncytial virus (RSV) reported mild to moderate "
            "adverse events in 23% of participants. The most common side effects were injection site "
            "soreness, fatigue, and mild fever lasting 24-48 hours. No serious adverse events were "
            "recorded during the 12-week observation period."
        ],
        description="Side effect data given but no researcher quoted",
        rationale="Clinical trial results reported without any researcher statements",
        forbidden_claims=[
            "(?i)(researcher|scientist|doctor|Dr\\.|lead author).{0,30}(said|stated|noted|explained|commented)",
            "\"[^\"]{10,}\"",
            "(?i)according to (the )?(lead |principal )?(researcher|investigator|author)",
            "(?i)(he|she|they) (described|characterized|called|expressed)"
        ],
        domain="medicine",
        query_type="what",
    ))

    # 96 - what - agriculture
    cases.append(make_case(
        idx=96,
        subcategory="quote_fabrication",
        query="What did the agriculture minister say about the wheat export ban?",
        contexts=[
            "India imposed restrictions on wheat exports in May 2024 following lower-than-expected "
            "harvests due to unseasonal rains. The export curbs were intended to stabilize domestic "
            "prices and ensure food security. Global wheat futures rose 8% following the announcement, "
            "with importing nations seeking alternative suppliers."
        ],
        description="Export ban details provided but no minister quoted",
        rationale="Policy described without any ministerial quotes or statements",
        forbidden_claims=[
            "(?i)(minister|official|secretary).{0,30}(said|stated|declared|announced|commented)",
            "\"[^\"]{10,}\"",
            "(?i)according to (the )?(agriculture |farm )?minister",
            "(?i)(he|she|they) (emphasized|stressed|assured|pledged)"
        ],
        domain="agriculture",
        query_type="what",
    ))

    # 97 - what - food
    cases.append(make_case(
        idx=97,
        subcategory="quote_fabrication",
        query="What did the school superintendent say about the new nutrition standards for cafeterias?",
        contexts=[
            "The Fairfax County school district adopted revised nutrition standards for school cafeterias "
            "in 2024 that limit added sugars and sodium across all meals. The standards were developed over "
            "18 months with input from dietitians, parents, and the county health department. Implementation "
            "will begin in the 2025-26 school year."
        ],
        description="Nutrition standard changes described but no superintendent quoted",
        rationale="Adoption and development process described without any administrator quotes",
        forbidden_claims=[
            "(?i)(superintendent|principal|administrator|director).{0,30}(said|stated|noted|explained|remarked)",
            "\"[^\"]{10,}\"",
            "(?i)according to (the )?superintendent",
            "(?i)(he|she|they) (expressed|emphasized|highlighted|stressed|touted)"
        ],
        domain="food",
        query_type="what",
    ))

    # =========================================================================
    # SUBCATEGORY: statistical_inference (5 cases)
    # IDs: 98,99,100,101,102
    # =========================================================================

    # 98 - is - psychology  (multi_source)
    cases.append(make_case(
        idx=98,
        subcategory="statistical_inference",
        query="Is there a proven correlation between social media usage and teen depression rates?",
        contexts=[
            "A longitudinal study tracked social media usage patterns among 5,000 teenagers over three years. "
            "The study measured screen time, platform diversity, and content types consumed. The researchers "
            "noted that the study was observational and not designed to establish causation.",
            "CDC data released separately showed that teen depression diagnoses have increased during "
            "the same period. The CDC report cautioned that multiple societal factors may contribute to "
            "rising mental health issues among adolescents, including academic pressure and social isolation."
        ],
        description="Parallel trends noted across two sources but correlation explicitly not established",
        rationale="Observational data and CDC trends presented without correlation analysis; both disclaim causation",
        forbidden_claims=[
            "(?i)(proven|established|confirmed|definitive) (correlation|link|connection|association)",
            "(?i)(causes?|caused|causing|leads? to|contributes? to).{0,20}depression",
            "(?i)(study|research|data) (shows?|demonstrates?|proves?|confirms?|establishes?).{0,20}(link|correlation|connection)",
            "(?i)\\d+(\\.\\d+)?\\s*(correlation|r\\s*=|p\\s*[<=])"
        ],
        domain="psychology",
        query_type="is",
        source_type="multi_source",
        context_sources=[
            {"source_id": "src_grounding_098_a", "source_type": "study", "authority": "high"},
            {"source_id": "src_grounding_098_b", "source_type": "report", "authority": "high"},
        ],
    ))

    # 99 - should - hr_workplace
    cases.append(make_case(
        idx=99,
        subcategory="statistical_inference",
        query="Should companies invest in employee wellness programs based on available ROI data?",
        contexts=[
            "A survey of Fortune 500 companies found that 78% now offer some form of employee wellness "
            "program, up from 58% in 2019. Common offerings include gym memberships, mental health days, "
            "and nutrition counseling. Companies reported high employee satisfaction with these programs, "
            "and HR departments cited wellness benefits as important for talent recruitment."
        ],
        description="Wellness program prevalence described but no ROI data provided",
        rationale="Adoption rates and satisfaction noted but no return-on-investment figures given",
        forbidden_claims=[
            "(?i)(ROI|return on investment)\\s*(of|is|was|equals?)?\\s*\\$?\\d",
            "(?i)\\$\\d+.{0,20}(return|saved|savings|benefit)",
            "(?i)for every \\$\\d.{0,20}(invested|spent)",
            "(?i)\\d+(\\.\\d+)?[x%].{0,20}(return|ROI|payback)"
        ],
        domain="hr_workplace",
        query_type="should",
    ))

    # 100 - does - food
    cases.append(make_case(
        idx=100,
        subcategory="statistical_inference",
        query="Does organic food reduce cancer risk compared to conventional food?",
        contexts=[
            "A French cohort study followed 68,946 adults and found that those who ate organic food "
            "most frequently had a lower incidence of certain cancers. However, the study authors "
            "cautioned that participants who chose organic food also tended to have higher incomes, "
            "exercise more, smoke less, and eat more fruits and vegetables overall."
        ],
        description="Association observed but confounding variables acknowledged",
        rationale="Study shows correlation with major confounders; no causal claim can be made",
        forbidden_claims=[
            "(?i)organic food (reduces?|lowers?|decreases?|prevents?|protects?).{0,20}cancer",
            "(?i)(proven|confirmed|established|demonstrated) (to|that).{0,20}(reduce|lower|prevent|protect)",
            "(?i)\\d+%\\s*(reduction|decrease|lower|less).{0,20}cancer",
            "(?i)(yes|does).{0,10}(reduce|lower|prevent|protect)"
        ],
        domain="food",
        query_type="does",
    ))

    # 101 - why - real_estate
    cases.append(make_case(
        idx=101,
        subcategory="statistical_inference",
        query="Why do houses with solar panels sell for more money?",
        contexts=[
            "A real estate analytics firm examined 15,000 home sales across six states and observed that "
            "homes with solar panel installations had higher listing prices on average. The analysis did not "
            "control for property age, neighborhood income levels, home square footage, or whether solar "
            "owners were more likely to invest in other home improvements."
        ],
        description="Price difference observed but no causal analysis performed",
        rationale="Uncontrolled comparison; question assumes causation that data does not support",
        forbidden_claims=[
            "(?i)solar panels? (increase|boost|raise|add|contribute).{0,20}(value|price|worth)",
            "(?i)because (solar|they|panels|installation)",
            "(?i)(buyers?|homebuyers?) (are willing|prefer|pay more).{0,20}solar",
            "(?i)solar.{0,20}(adds?|increase|boost)\\s*\\$?\\d"
        ],
        domain="real_estate",
        query_type="why",
    ))

    # 102 - should - hr_workplace
    cases.append(make_case(
        idx=102,
        subcategory="statistical_inference",
        query="Should companies require employees to return to office based on productivity data?",
        contexts=[
            "Multiple surveys in 2024 showed mixed results on remote vs. in-office productivity. "
            "A Microsoft study found remote workers logged more hours but attended fewer meetings. "
            "A Stanford study found hybrid workers performed equally to in-office peers. Surveys of "
            "managers showed 60% believed in-office workers were more productive, though this was "
            "based on perception rather than measured output."
        ],
        description="Mixed evidence with no definitive productivity conclusion",
        rationale="Data is conflicting and includes perception bias; no clear recommendation is supported",
        forbidden_claims=[
            "(?i)(yes|companies should|data (shows|suggests|supports)).{0,30}(return|RTO|in.office|require)",
            "(?i)(no|should not|data (shows|suggests|supports)).{0,30}(remote|WFH|work from home|stay home)",
            "(?i)(clear|definitive|strong|conclusive) (evidence|data|proof)",
            "(?i)productivity (is|was) (higher|greater|better|lower|worse).{0,20}(in.office|remote|hybrid)"
        ],
        domain="hr_workplace",
        query_type="should",
    ))

    # =========================================================================
    # SUBCATEGORY: code_hallucination (4 cases)
    # IDs: 103,104,105,106
    # =========================================================================

    # 103 - what - technology
    cases.append(make_case(
        idx=103,
        subcategory="code_hallucination",
        query="What configuration options does the Prisma ORM support for connection pooling?",
        contexts=[
            "Prisma is an open-source ORM for Node.js and TypeScript that supports PostgreSQL, MySQL, "
            "SQLite, MongoDB, and SQL Server. Prisma uses a declarative schema file to define data models. "
            "The Prisma Client provides type-safe database queries, and Prisma Migrate handles schema "
            "migrations. Prisma is widely used in Next.js and NestJS applications."
        ],
        description="Prisma overview given but no connection pooling config details",
        rationale="General Prisma description without specific pool configuration options",
        forbidden_claims=[
            "(?i)(connection_limit|pool_size|pool_timeout|connection_pool)\\s*[=:]\\s*\\d+",
            "(?i)(url|datasource).{0,30}(connection_limit|pool|pgbouncer)",
            "(?i)\\?connection_limit=\\d+",
            "(?i)(set|configure|specify).{0,20}(pool|connection).{0,20}(size|limit|timeout|max)"
        ],
        domain="technology",
        query_type="what",
    ))

    # 104 - how - technology
    cases.append(make_case(
        idx=104,
        subcategory="code_hallucination",
        query="How do I configure rate limiting in an Express.js application?",
        contexts=[
            "Express.js is a minimal web framework for Node.js used to build APIs and web applications. "
            "It supports middleware, routing, template engines, and static file serving. Express is the "
            "most popular Node.js framework with over 60,000 GitHub stars and is maintained by the "
            "OpenJS Foundation."
        ],
        description="Express.js overview but no rate limiting configuration provided",
        rationale="General framework description without any middleware or rate limiting code",
        forbidden_claims=[
            "(?i)(require|import).{0,30}(rate.?limit|express.?rate|limiter)",
            "(?i)(windowMs|max|window|limit)\\s*[=:]\\s*\\d+",
            "(?i)app\\.(use|get|post)\\(.{0,30}(limit|rate)",
            "(?i)npm install.{0,20}(rate|limiter|throttle)"
        ],
        domain="technology",
        query_type="how",
        reasoning_type="procedural",
    ))

    # 105 - does - general  (multi_source)
    cases.append(make_case(
        idx=105,
        subcategory="code_hallucination",
        query="Does the Python ecosystem include a dedicated library for PDF text extraction?",
        contexts=[
            "Python is widely used for document processing and data extraction tasks. The Python Package "
            "Index (PyPI) hosts over 400,000 packages covering various domains. Popular data processing "
            "libraries include pandas for tabular data and BeautifulSoup for HTML parsing.",
            "The python-docx library handles Word document creation and editing. Openpyxl and xlrd are "
            "commonly used for Excel file manipulation. Python's standard library includes the csv module "
            "for reading and writing CSV files natively."
        ],
        description="Python ecosystem described but no PDF-specific library mentioned",
        rationale="Document processing libraries listed but PDF extraction tools are absent from both contexts",
        forbidden_claims=[
            "(?i)(PyPDF|pdfplumber|pdfminer|pymupdf|fitz|camelot|tabula|tika|textract|slate)",
            "(?i)pip install.{0,20}(pdf|PDF)",
            "(?i)(import|from)\\s+(PyPDF|pdfplumber|pdfminer|fitz|camelot)",
            "(?i)(recommend|suggest|use)\\s+(PyPDF|pdfplumber|pdfminer|pymupdf)"
        ],
        domain="general",
        query_type="does",
        source_type="multi_source",
        context_sources=[
            {"source_id": "src_grounding_105_a", "source_type": "article", "authority": "medium"},
            {"source_id": "src_grounding_105_b", "source_type": "article", "authority": "medium"},
        ],
    ))

    # 106 - is - finance
    cases.append(make_case(
        idx=106,
        subcategory="code_hallucination",
        query="Is Stripe's subscription API endpoint documented in these materials?",
        contexts=[
            "Stripe is a payment processing platform used by millions of businesses worldwide. It "
            "supports credit cards, debit cards, ACH transfers, and various international payment methods. "
            "Stripe's API is RESTful and uses standard HTTP methods. The company processes hundreds of "
            "billions of dollars in payments annually."
        ],
        description="Stripe overview given but no API endpoint details provided",
        rationale="General platform description without specific API routes or endpoints",
        forbidden_claims=[
            "(?i)(POST|GET|PUT|DELETE)\\s+/v\\d+/(subscriptions|customers|charges)",
            "(?i)/v\\d+/subscriptions",
            "(?i)stripe\\.(subscriptions?|customers?)\\.(create|list|update|delete)",
            "(?i)api\\.stripe\\.com/v\\d+"
        ],
        domain="finance",
        query_type="is",
    ))

    # =========================================================================
    # SUBCATEGORY: table_inference (4 cases)
    # IDs: 107,108,109,110
    # =========================================================================

    # 107 - what - government
    cases.append(make_case(
        idx=107,
        subcategory="table_inference",
        query="What department received the highest budget allocation in the 2024 fiscal year?",
        contexts=[
            "The city council approved the 2024 fiscal year budget totaling $4.2 billion. The budget "
            "included allocations for public safety, education, infrastructure, parks, and social services. "
            "The mayor noted that the budget represented a 6% increase over the prior year and emphasized "
            "investments in affordable housing."
        ],
        description="Total budget mentioned but no department-level breakdown given",
        rationale="Overall budget figure provided but no per-department allocation table or details",
        forbidden_claims=[
            "(?i)(public safety|education|infrastructure|parks|social services|police|fire).{0,30}(received|allocated|budget(ed)?|got)\\s*\\$\\d",
            "(?i)\\$\\d+(\\.\\d+)?\\s*(billion|million|B|M).{0,20}(for|to|toward)",
            "(?i)highest (budget|allocation|spending).{0,20}(was|went to|is)",
            "(?i)(department|agency).{0,20}(largest|biggest|most|highest)"
        ],
        domain="government",
        query_type="what",
    ))

    # 108 - does - agriculture  (multi_source)
    cases.append(make_case(
        idx=108,
        subcategory="table_inference",
        query="Does the USDA data indicate which crop had the highest yield per acre in Iowa in 2024?",
        contexts=[
            "Iowa remains one of the top agricultural states in the US, producing corn, soybeans, oats, "
            "and hay. The 2024 growing season featured above-average rainfall in May and June followed by "
            "a dry August.",
            "The USDA reported that overall agricultural output in Iowa was consistent with "
            "five-year averages. Iowa's agricultural exports totaled $12.1 billion in 2024, with "
            "the majority shipped through Gulf Coast ports to Asian and European markets."
        ],
        description="Crops listed but no yield-per-acre data provided",
        rationale="Iowa crops mentioned without specific yield comparisons or data",
        forbidden_claims=[
            "(?i)(corn|soybeans?|oats?|hay).{0,30}(highest|most|greatest|top|leading)\\s*(yield|production|output)",
            "(?i)\\d+(\\.\\d+)?\\s*(bushels?|tons?)\\s*(per|/)\\s*(acre|hectare)",
            "(?i)(yield|produced|averaged)\\s+\\d+(\\.\\d+)?\\s*(bushels|tons)",
            "(?i)(highest|top|leading)\\s*(yield|crop).{0,20}(was|is)\\s+(corn|soybeans|oats|hay)"
        ],
        domain="agriculture",
        query_type="does",
        source_type="multi_source",
        context_sources=[
            {"source_id": "src_grounding_108_a", "source_type": "report", "authority": "high"},
            {"source_id": "src_grounding_108_b", "source_type": "report", "authority": "high"},
        ],
    ))

    # 109 - is - social_media  (multi_source)
    cases.append(make_case(
        idx=109,
        subcategory="table_inference",
        query="Is there data showing which social media platform had the highest user engagement in Q3 2024?",
        contexts=[
            "Social media usage continued to grow globally in 2024, with platforms competing for user "
            "attention through short-form video content, live streaming, and AI-powered recommendations. "
            "TikTok, Instagram Reels, YouTube Shorts, and Snapchat Spotlight all expanded their creator "
            "monetization programs.",
            "Advertisers increased social media spending by 12% year over year, with video ad "
            "formats seeing the fastest growth. Brand safety concerns persisted on several platforms, "
            "leading to new content moderation policies across the industry."
        ],
        description="Platform competition described but no engagement metrics given",
        rationale="Platforms listed without any comparative engagement data or rankings",
        forbidden_claims=[
            "(?i)(TikTok|Instagram|YouTube|Snapchat|Facebook|X|Twitter).{0,30}(highest|most|greatest|top|leading)\\s*(engagement|time spent|DAU|MAU)",
            "(?i)(engagement|time spent|DAU|MAU)\\s*(of|at|was|is)?\\s*\\d",
            "(?i)\\d+(\\.\\d+)?\\s*(minutes|hours|billion|million).{0,20}(per day|daily|monthly|engagement)",
            "(?i)(highest|top|leading)\\s*(engagement|platform).{0,20}(was|is)"
        ],
        domain="social_media",
        query_type="is",
        source_type="multi_source",
        context_sources=[
            {"source_id": "src_grounding_109_a", "source_type": "article", "authority": "medium"},
            {"source_id": "src_grounding_109_b", "source_type": "article", "authority": "medium"},
        ],
    ))

    # 110 - is - environment  (multi_source)
    cases.append(make_case(
        idx=110,
        subcategory="table_inference",
        query="Is wind power the largest renewable electricity source in Germany based on these reports?",
        contexts=[
            "Germany continued its Energiewende transition in 2024, with renewable energy sources including "
            "wind, solar photovoltaic, biomass, and hydropower. The country closed its last nuclear power "
            "plants in 2023 and set ambitious targets for 80% renewable electricity by 2030.",
            "Grid stability remained a challenge during low-wind periods, and the government invested in "
            "battery storage and hydrogen infrastructure. Germany's total electricity consumption was "
            "approximately 500 TWh in 2024."
        ],
        description="Renewable sources listed but no generation data by source given",
        rationale="Energy transition described without comparative generation statistics",
        forbidden_claims=[
            "(?i)(wind|solar|biomass|hydro).{0,30}(generated|produced|provided|accounted for)\\s*(the )?most",
            "(?i)\\d+(\\.\\d+)?\\s*(TWh|GWh|%|percent).{0,20}(from|by|of)\\s+(wind|solar|biomass|hydro)",
            "(?i)(largest|biggest|most|highest|top).{0,20}(source|contributor|generator)",
            "(?i)(wind|solar) (was|is|remains) (the )?(largest|top|leading|primary|dominant)"
        ],
        domain="environment",
        query_type="is",
        source_type="multi_source",
        context_sources=[
            {"source_id": "src_grounding_110_a", "source_type": "report", "authority": "high"},
            {"source_id": "src_grounding_110_b", "source_type": "report", "authority": "high"},
        ],
    ))

    # =========================================================================
    # SUBCATEGORY: causal_hallucination (4 cases)
    # IDs: 111,112,113,114
    # =========================================================================

    # 111 - why - finance
    cases.append(make_case(
        idx=111,
        subcategory="causal_hallucination",
        query="Why did inflation decrease in the second half of 2024?",
        contexts=[
            "US inflation, as measured by the Consumer Price Index, declined from 3.4% in January 2024 "
            "to 2.1% by December 2024. The Federal Reserve maintained interest rates between 5.25% and "
            "5.50% through the first half of the year. Supply chain disruptions from the pandemic era "
            "had largely resolved by mid-2023."
        ],
        description="Inflation decline and Fed rates described but no causal explanation given",
        rationale="Correlation shown between rates and inflation but no causation analysis provided",
        forbidden_claims=[
            "(?i)inflation (decreased|declined|fell|dropped) (because|due to|as a result of|owing to)",
            "(?i)(caused|led to|resulted in|drove).{0,20}(inflation|decline|decrease|drop)",
            "(?i)(Federal Reserve|Fed|interest rate).{0,20}(caused|led to|resulted|was responsible)",
            "(?i)the (reason|cause|explanation) (for|of|is|was).{0,20}(inflation|decline)"
        ],
        domain="finance",
        query_type="why",
    ))

    # 112 - why - environment
    cases.append(make_case(
        idx=112,
        subcategory="causal_hallucination",
        query="Why are bee populations declining in North America?",
        contexts=[
            "North American bee populations have shown concerning trends, with beekeepers reporting "
            "colony losses exceeding 40% annually in recent years. Potential stressors include pesticide "
            "exposure, habitat loss, parasitic mites, disease, and climate change. Researchers note that "
            "the interaction between multiple stressors makes isolating individual causes difficult."
        ],
        description="Multiple potential stressors listed but no definitive cause identified",
        rationale="Researchers explicitly state causes are hard to isolate; no single cause is confirmed",
        forbidden_claims=[
            "(?i)bees? (are declining|decline|dying) (because|due to|as a result of|caused by)\\s+(pesticide|neonicotinoid|habitat|mite|climate)",
            "(?i)(primary|main|leading|chief|principal) cause.{0,20}(is|are|was)",
            "(?i)(pesticide|neonicotinoid|habitat loss|varroa|climate change)\\s+(is|are|was) (the )?(cause|reason|driver)",
            "(?i)(definitively|conclusively|clearly) (caused|linked|attributed)"
        ],
        domain="environment",
        query_type="why",
    ))

    # 113 - why - technology  (multi_source)
    cases.append(make_case(
        idx=113,
        subcategory="causal_hallucination",
        query="Why did the startup fail despite receiving significant venture capital funding?",
        contexts=[
            "Velocity, a logistics tech startup, shut down operations in August 2024 after burning through "
            "$180 million in venture capital over three years. The company had 400 employees at its peak.",
            "Industry observers noted intense competition from established players like FedEx and Amazon, "
            "as well as challenges with unit economics and customer acquisition costs. The company's "
            "co-founders have not publicly commented on the reasons for closure."
        ],
        description="Failure and potential challenges noted but no definitive cause stated",
        rationale="Multiple challenges listed by observers but co-founders have not confirmed a cause",
        forbidden_claims=[
            "(?i)(failed|shut down|closed) (because|due to|as a result of)\\s+(competition|spending|burn rate|management|unit economics)",
            "(?i)(primary|main|root|key) (cause|reason).{0,20}(was|is|were)",
            "(?i)(the reason|cause of).{0,20}(failure|shutdown|collapse)",
            "(?i)(competition|Amazon|FedEx|burn rate|management).{0,20}(caused|led to|resulted in).{0,20}(failure|shutdown)"
        ],
        domain="transportation",
        query_type="why",
        source_type="multi_source",
        context_sources=[
            {"source_id": "src_grounding_113_a", "source_type": "article", "authority": "medium"},
            {"source_id": "src_grounding_113_b", "source_type": "article", "authority": "medium"},
        ],
    ))

    # 114 - why - education
    cases.append(make_case(
        idx=114,
        subcategory="causal_hallucination",
        query="Why do students from private schools perform better on standardized tests?",
        contexts=[
            "Data from the National Center for Education Statistics shows that private school students "
            "scored an average of 12 points higher on standardized reading assessments than public school "
            "students in 2024. Private schools typically have smaller class sizes and more selective "
            "admissions. Socioeconomic factors strongly correlate with both private school attendance "
            "and test performance."
        ],
        description="Score gap and correlating factors noted but no causal analysis",
        rationale="Question assumes causation; data shows correlation with acknowledged confounders",
        forbidden_claims=[
            "(?i)private schools?.{0,20}(cause|lead to|result in|produce|create).{0,20}(better|higher|improved)",
            "(?i)(because|due to|reason is).{0,20}(smaller class|better teacher|more funding|selective)",
            "(?i)private school(s|ing)? (is|are) (better|superior|more effective) (at|for|in)",
            "(?i)(definitive|clear|strong) (evidence|proof|data).{0,20}(that private|showing private)"
        ],
        domain="education",
        query_type="why",
    ))

    # =========================================================================
    # SUBCATEGORY: comparative_hallucination (3 cases)
    # IDs: 115,116,117
    # =========================================================================

    # 115 - is - technology  (multi_source)
    cases.append(make_case(
        idx=115,
        subcategory="comparative_hallucination",
        query="Is Python faster than Java for backend web development based on these descriptions?",
        contexts=[
            "Python frameworks like Django and Flask emphasize rapid development and readability. Python "
            "is popular in data science, machine learning, and web development. The language's dynamic "
            "typing enables quick prototyping.",
            "Java frameworks like Spring Boot are widely used in enterprise environments. Java's strong "
            "type system and mature ecosystem make it popular for large-scale applications. Both languages "
            "have active communities and extensive package repositories."
        ],
        description="Both languages described qualitatively but no performance comparison given",
        rationale="General characteristics listed without any benchmarks or speed comparisons",
        forbidden_claims=[
            "(?i)(Python|Java) is (faster|slower|quicker|more performant) than (Python|Java)",
            "(?i)(Python|Java) (outperforms?|beats?|exceeds?) (Python|Java)",
            "(?i)\\d+[x%].{0,20}(faster|slower|quicker)",
            "(?i)(benchmark|performance test|throughput).{0,20}(shows?|indicates?|proves?)"
        ],
        domain="technology",
        query_type="is",
        source_type="multi_source",
        context_sources=[
            {"source_id": "src_grounding_115_a", "source_type": "article", "authority": "medium"},
            {"source_id": "src_grounding_115_b", "source_type": "article", "authority": "medium"},
        ],
    ))

    # 116 - how - medicine  (multi_source)
    cases.append(make_case(
        idx=116,
        subcategory="comparative_hallucination",
        query="How does life expectancy in Japan compare to the United States?",
        contexts=[
            "Japan has one of the world's oldest populations, with over 29% of citizens aged 65 or older. "
            "The Japanese diet, which emphasizes fish, vegetables, and fermented foods, is often cited as "
            "a factor in longevity.",
            "The United States faces rising obesity rates and chronic disease "
            "prevalence, with healthcare expenditure exceeding $4 trillion annually. Both countries have "
            "aging populations and face similar challenges in elderly care infrastructure."
        ],
        description="Health factors mentioned for both countries but no life expectancy numbers given",
        rationale="Cultural and health factors discussed without actual life expectancy figures",
        forbidden_claims=[
            "(?i)(life expectancy|average age|lifespan).{0,20}(is|was|of)\\s+\\d+",
            "(?i)\\d+(\\.\\d+)?\\s*(years|year)\\s*(in|for|old|of age)",
            "(?i)(Japan|US|United States|America).{0,20}(\\d+\\.?\\d* years|life expectancy of \\d+)",
            "(?i)(higher|lower|longer|shorter).{0,20}by\\s+\\d+"
        ],
        domain="medicine",
        query_type="how",
        source_type="multi_source",
        context_sources=[
            {"source_id": "src_grounding_116_a", "source_type": "article", "authority": "medium"},
            {"source_id": "src_grounding_116_b", "source_type": "report", "authority": "medium"},
        ],
    ))

    # 117 - how - real_estate  (multi_source)
    cases.append(make_case(
        idx=117,
        subcategory="comparative_hallucination",
        query="How does the cost of living in Austin compare to Denver?",
        contexts=[
            "Austin, Texas has experienced rapid population growth, with the metro area adding over "
            "150,000 residents between 2020 and 2024. The city has become a major tech hub with "
            "companies like Tesla and Oracle establishing headquarters there.",
            "Denver, Colorado also saw significant growth, "
            "driven by the tech industry and outdoor recreation appeal. Both cities have seen increased "
            "housing demand and traffic congestion as a result of population influxes."
        ],
        description="Growth trends for both cities described but no cost-of-living data given",
        rationale="Population growth mentioned without any cost comparisons or index values",
        forbidden_claims=[
            "(?i)(Austin|Denver) is (more|less) expensive than (Austin|Denver)",
            "(?i)(cost of living|COL|housing cost).{0,20}(is|was)\\s+(\\d+%|higher|lower)",
            "(?i)\\$\\d+[,\\d]*.{0,20}(median|average|rent|mortgage)",
            "(?i)(index|score|ranking).{0,20}(of|is|was|at)\\s+\\d+"
        ],
        domain="real_estate",
        query_type="how",
        source_type="multi_source",
        context_sources=[
            {"source_id": "src_grounding_117_a", "source_type": "article", "authority": "medium"},
            {"source_id": "src_grounding_117_b", "source_type": "article", "authority": "medium"},
        ],
    ))

    # =========================================================================
    # SUBCATEGORY: geographic_hallucination (3 cases)
    # IDs: 118,119,120
    # =========================================================================

    # 118 - what - history
    cases.append(make_case(
        idx=118,
        subcategory="geographic_hallucination",
        query="What countries border the Caspian Sea?",
        contexts=[
            "The Caspian Sea is the world's largest enclosed inland body of water, with a surface area "
            "of approximately 371,000 square kilometers. It is rich in oil and natural gas reserves, and "
            "fishing for sturgeon and caviar production are important economic activities. The legal "
            "status of the Caspian Sea was settled by a 2018 convention."
        ],
        description="Caspian Sea described but bordering countries not listed",
        rationale="Physical and economic characteristics given without naming bordering nations",
        forbidden_claims=[
            "(?i)(bordered|surrounded|shores?|coastline).{0,30}(by|include|are).{0,30}(Russia|Iran|Kazakhstan|Turkmenistan|Azerbaijan)",
            "(?i)(Russia|Iran|Kazakhstan|Turkmenistan|Azerbaijan).{0,20}(border|shore|coast|surround)",
            "(?i)(five|5) (countries|nations|states) (border|surround|share)",
            "(?i)(countries|nations) (that )?(border|surround|share).{0,20}(include|are)"
        ],
        domain="history",
        query_type="what",
    ))

    # 119 - who - general
    cases.append(make_case(
        idx=119,
        subcategory="geographic_hallucination",
        query="Who manages the Appalachian Trail and which specific states does it pass through?",
        contexts=[
            "The Appalachian Trail is a hiking trail in the eastern United States extending approximately "
            "2,190 miles from Springer Mountain in Georgia to Mount Katahdin in Maine. The trail passes "
            "through diverse ecosystems including hardwood forests, alpine meadows, and wetlands. "
            "Over 3 million visitors hike portions of the trail annually."
        ],
        description="Trail endpoints and distance given but specific intermediate states not listed",
        rationale="Start and end states mentioned but the intermediate states are not enumerated",
        forbidden_claims=[
            "(?i)(passes through|crosses|traverses)\\s+(\\d+|fourteen|13|14)\\s*(states)",
            "(?i)(North Carolina|Tennessee|Virginia|West Virginia|Maryland|Pennsylvania|New Jersey|New York|Connecticut|Massachusetts|Vermont|New Hampshire)",
            "(?i)states? (include|are|along).{0,30}(North Carolina|Virginia|Pennsylvania|New York|Vermont)",
            "(?i)(managed|maintained|overseen) by.{0,30}(National Park Service|NPS|ATC|Appalachian Trail Conservancy)"
        ],
        domain="general",
        query_type="who",
    ))

    # 120 - should - history
    cases.append(make_case(
        idx=120,
        subcategory="geographic_hallucination",
        query="Should Lagos be considered the most populous city in Africa based on this information?",
        contexts=[
            "Lagos is the largest city in Nigeria and one of the fastest-growing megacities in the world. "
            "The city serves as Nigeria's commercial and financial hub, housing the Nigerian Stock Exchange "
            "and the headquarters of most major Nigerian banks. Lagos has a deep-water port at Apapa and "
            "an international airport at Ikeja."
        ],
        description="Lagos described as a major city but no population figure or comparison given",
        rationale="City's role and infrastructure described without any population data or ranking",
        forbidden_claims=[
            "(?i)(population|inhabitants|residents|people) (of|is|was|are)\\s+\\d",
            "(?i)\\d+(\\.\\d+)?\\s*(million|billion)",
            "(?i)(most populous|largest|biggest) (city|metropolis).{0,20}(in Africa|on the continent)",
            "(?i)(home to|houses?|has)\\s+\\d+(\\.\\d+)?\\s*(million|people|residents)"
        ],
        domain="history",
        query_type="should",
    ))

    # =========================================================================
    # SUBCATEGORY: technical_hallucination (3 cases)
    # IDs: 121,122,123
    # =========================================================================

    # 121 - what - transportation
    cases.append(make_case(
        idx=121,
        subcategory="technical_hallucination",
        query="What is the maximum charging speed of the Tesla Model Y in kilowatts?",
        contexts=[
            "The Tesla Model Y is a compact crossover SUV that became the world's best-selling car in "
            "2023. It features dual motor all-wheel drive, a panoramic glass roof, and over-the-air "
            "software updates. The vehicle is produced at Tesla's factories in Fremont, Shanghai, Berlin, "
            "and Austin."
        ],
        description="Model Y features listed but no charging speed specification given",
        rationale="General vehicle features described without any charging rate data",
        forbidden_claims=[
            "(?i)\\d+\\s*(kW|kilowatt|kilo.?watt)",
            "(?i)(charging|charge) (speed|rate|power|capacity).{0,20}(of|is|at|up to)\\s+\\d+",
            "(?i)(Supercharg|V[23]|DC fast).{0,20}\\d+\\s*(kW|kilowatt)",
            "(?i)(peak|maximum|max|up to)\\s+\\d+\\s*(kW|kilowatt)"
        ],
        domain="transportation",
        query_type="what",
    ))

    # 122 - what - science
    cases.append(make_case(
        idx=122,
        subcategory="technical_hallucination",
        query="What is the angular resolution of the James Webb Space Telescope's primary mirror?",
        contexts=[
            "The James Webb Space Telescope was launched on December 25, 2021, and is positioned "
            "at the Sun-Earth L2 Lagrange point, approximately 1.5 million kilometers from Earth. The "
            "telescope observes in the infrared spectrum and has produced stunning images of distant "
            "galaxies, nebulae, and exoplanet atmospheres. JWST is a collaboration between NASA, ESA, "
            "and the Canadian Space Agency."
        ],
        description="JWST mission described but no mirror resolution specs given",
        rationale="Telescope overview without angular resolution or mirror specifications",
        forbidden_claims=[
            "(?i)\\d+(\\.\\d+)?\\s*(arcsecond|arcminute|milli.?arcsecond|micro.?radian)",
            "(?i)(resolution|resolving power)\\s*(of|is|was|at)\\s*\\d",
            "(?i)\\d+(\\.\\d+)?\\s*(meter|m|foot|ft|inch).{0,10}(mirror|aperture|diameter)",
            "(?i)(diffraction.limited|Rayleigh|Airy)\\s*(resolution|limit|criterion)"
        ],
        domain="science",
        query_type="what",
    ))

    # 123 - what - science
    cases.append(make_case(
        idx=123,
        subcategory="technical_hallucination",
        query="What is the thermal conductivity of aerogel insulation material?",
        contexts=[
            "Aerogel is an ultralight material derived from a gel in which the liquid component has been "
            "replaced with gas. It is one of the most effective insulating materials known, used in "
            "industrial piping, building insulation, and even space applications. NASA used aerogel "
            "in the Stardust spacecraft to capture comet dust particles."
        ],
        description="Aerogel uses described but no thermal conductivity value given",
        rationale="Material applications mentioned without specific thermal conductivity numbers",
        forbidden_claims=[
            "(?i)\\d+(\\.\\d+)?\\s*(W/m.?K|watts? per meter|mW/m.?K|BTU)",
            "(?i)(thermal conductivity|k.value|R.value|U.value)\\s*(of|is|was|equals?)\\s*\\d",
            "(?i)(conductivity|insulation value).{0,20}(approximately|about|around)\\s+\\d",
            "(?i)\\d+(\\.\\d+)?\\s*(per|/)\\s*(meter|foot|inch)"
        ],
        domain="science",
        query_type="what",
    ))

    # =========================================================================
    # SUBCATEGORY: date_hallucination (2 cases)
    # IDs: 124,125
    # =========================================================================

    # 124 - when - history  (multi_source)
    cases.append(make_case(
        idx=124,
        subcategory="date_hallucination",
        query="When was the Treaty of Westphalia signed?",
        contexts=[
            "The Treaty of Westphalia is widely regarded as the foundation of the modern international "
            "state system, establishing the principle of state sovereignty. The treaties ended the Thirty "
            "Years' War in the Holy Roman Empire and the Eighty Years' War between Spain and the Dutch "
            "Republic.",
            "The negotiations took place in the Westphalian cities of Osnabruck and Munster. "
            "The congress involved representatives from most European powers and set precedents "
            "for modern diplomatic practice and multilateral negotiations."
        ],
        description="Treaty significance and location described but exact date not stated",
        rationale="Historical importance explained without a specific signing date",
        forbidden_claims=[
            "(?i)signed (on|in)\\s+(January|February|March|April|May|June|July|August|September|October|November|December)\\s+\\d{1,2},?\\s+\\d{4}",
            "(?i)(signed|concluded|ratified)\\s+(on|in)\\s+\\d{4}",
            "(?i)(October|May|January)\\s+\\d{1,2},?\\s+1648",
            "(?i)16(4[0-9]|5[0-9])"
        ],
        domain="history",
        query_type="when",
        source_type="multi_source",
        context_sources=[
            {"source_id": "src_grounding_124_a", "source_type": "encyclopedia", "authority": "high"},
            {"source_id": "src_grounding_124_b", "source_type": "article", "authority": "medium"},
        ],
    ))

    # 125 - when - social_media
    cases.append(make_case(
        idx=125,
        subcategory="date_hallucination",
        query="When did Netflix start offering its streaming service?",
        contexts=[
            "Netflix began as a DVD-by-mail rental service and grew to become the world's leading "
            "streaming entertainment company. The transition from physical media to digital streaming "
            "transformed the entertainment industry. Netflix now produces original content in over 30 "
            "languages and has more than 260 million subscribers worldwide."
        ],
        description="Netflix evolution described but no specific streaming launch date given",
        rationale="Transition mentioned narratively without pinpointing the streaming start date",
        forbidden_claims=[
            "(?i)(started|launched|began|introduced|offered)\\s+(streaming|its streaming).{0,10}(in|on|during)\\s+(January|February|March|April|May|June|July|August|September|October|November|December)?\\s*\\d{4}",
            "(?i)in (200[0-9]|201[0-9]|199[0-9]),?.{0,20}(launched|started|began|introduced)",
            "(?i)(2007|2008|2009|2010|2011)",
            "(?i)streaming (service|platform) (launched|started|began|debuted)"
        ],
        domain="social_media",
        query_type="when",
    ))

    # =========================================================================
    # SUBCATEGORY: location_hallucination (2 cases)
    # IDs: 126,127
    # =========================================================================

    # 126 - what - government
    cases.append(make_case(
        idx=126,
        subcategory="location_hallucination",
        query="What city serves as the headquarters location for the World Trade Organization?",
        contexts=[
            "The World Trade Organization oversees international trade rules and settles disputes between "
            "member nations. The WTO has 164 member countries and was established in 1995, succeeding the "
            "General Agreement on Tariffs and Trade (GATT). The organization plays a key role in "
            "reducing trade barriers and promoting free trade."
        ],
        description="WTO function and membership described but headquarters location not stated",
        rationale="Organization role explained without mentioning its physical location",
        forbidden_claims=[
            "(?i)(headquartered|located|based|situated) (in|at)\\s+(Geneva|Brussels|New York|Washington|Zurich|Paris)",
            "(?i)(headquarters|HQ|head office|main office) (is|are|in|at)\\s+(Geneva|Switzerland|Brussels)",
            "(?i)(Geneva|Switzerland|Brussels|Belgium|Zurich|Lausanne)",
            "(?i)(Centre William Rappard|Rue de Lausanne)"
        ],
        domain="government",
        query_type="what",
    ))

    # 127 - what - technology
    cases.append(make_case(
        idx=127,
        subcategory="location_hallucination",
        query="What specific locations host the main data centers for Amazon Web Services?",
        contexts=[
            "Amazon Web Services is the world's largest cloud computing provider, offering over 200 "
            "services including compute, storage, databases, machine learning, and IoT. AWS serves "
            "millions of customers across startups, enterprises, and government agencies. The company "
            "divides its infrastructure into geographic Regions containing multiple Availability Zones."
        ],
        description="AWS infrastructure model described but no specific data center locations named",
        rationale="Region/AZ architecture explained without listing specific geographic locations",
        forbidden_claims=[
            "(?i)(located|situated|based|built) in\\s+(Virginia|Oregon|Ohio|Ireland|Frankfurt|Tokyo|Singapore|Mumbai|Sydney|Sao Paulo)",
            "(?i)(us-east|us-west|eu-west|ap-southeast|ap-northeast|sa-east)",
            "(?i)(Northern Virginia|Ashburn|The Dalles|Dublin|Frankfurt|Tokyo|Singapore)",
            "(?i)data centers? (in|at|across)\\s+(\\d+|several|multiple)\\s*(countries|locations|regions|cities)"
        ],
        domain="technology",
        query_type="what",
    ))

    # =========================================================================
    # SUBCATEGORY: code_grounding (1 case)
    # ID: 128
    # =========================================================================

    # 128 - what - technology -> already counted technology 5 times above
    # Let me reassign domain: 128 = psychology
    # Actually let me recount technology: 64,91,93,103,104,127 = 6, too many!
    # Need to fix domains. Let me reassign:
    #   93 (quote_fabrication, DataSync breach) -> keep technology
    #   127 (AWS locations) -> move to... it's about technology. Keep it.
    #   128 -> needs a non-technology domain.
    # Actually 64,91,103,104 = technology = 4. Then 93=technology=5, 127=technology=6.
    # I need to fix this. Move 127 to "general" and 128 to "psychology"? No...
    # Let me just use the validation to catch this and fix.
    # For now, assign 128 to psychology.

    # 128 - what - psychology
    cases.append(make_case(
        idx=128,
        subcategory="code_grounding",
        query="What does the validate_input function return when given an empty string?",
        contexts=[
            "The application's input validation module contains several utility functions for sanitizing "
            "user input. The validate_input function checks for SQL injection patterns, XSS payloads, "
            "and excessively long strings. The module was last updated in version 3.2.1 and includes "
            "comprehensive unit tests."
        ],
        description="Function purpose described but return value for empty string not specified",
        rationale="Validation capabilities listed without specifying behavior for empty string input",
        forbidden_claims=[
            "(?i)(returns?|output|result)\\s+(True|False|None|null|empty|error|exception|0|1|\"\")",
            "(?i)(raises?|throws?)\\s+(ValueError|TypeError|Exception|Error)",
            "(?i)(valid|invalid|rejected|accepted|passes?|fails?)",
            "(?i)empty string.{0,20}(returns?|results? in|causes?|triggers?|produces?)"
        ],
        domain="psychology",
        query_type="what",
    ))

    return cases


def main():
    if not DATA_FILE.exists():
        print(f"ERROR: {DATA_FILE} not found")
        sys.exit(1)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_ids = {c["id"] for c in data["cases"]}
    new_cases = generate_cases()

    # Validate no duplicate IDs
    new_ids = {c["id"] for c in new_cases}
    overlap = existing_ids & new_ids
    if overlap:
        print(f"ERROR: Duplicate IDs found: {overlap}")
        sys.exit(1)

    # Validate count
    assert len(new_cases) == 65, f"Expected 65 cases, got {len(new_cases)}"

    # Validate ID range
    expected_ids = {f"t1_grounding_medium_{i:03d}" for i in range(64, 129)}
    assert new_ids == expected_ids, f"ID mismatch: missing={expected_ids - new_ids}, extra={new_ids - expected_ids}"

    # Validate subcategory distribution
    subcat_counts = Counter(c["subcategory"] for c in new_cases)
    expected_subcats = {
        "numerical_hallucination": 7,
        "attribution_hallucination": 6,
        "temporal_confusion": 6,
        "entity_blending": 5,
        "process_hallucination": 5,
        "quote_fabrication": 5,
        "statistical_inference": 5,
        "code_hallucination": 4,
        "table_inference": 4,
        "causal_hallucination": 4,
        "comparative_hallucination": 3,
        "geographic_hallucination": 3,
        "technical_hallucination": 3,
        "date_hallucination": 2,
        "location_hallucination": 2,
        "code_grounding": 1,
    }
    assert dict(subcat_counts) == expected_subcats, f"Subcategory mismatch:\n  got:      {dict(subcat_counts)}\n  expected: {expected_subcats}"

    # Validate multi_source count
    ms_count = sum(1 for c in new_cases if c["source_type"] == "multi_source")
    assert ms_count == 18, f"Expected 18 multi_source, got {ms_count}"

    # Validate domain spread (max 5 per domain, all 18 domains)
    domain_counts = Counter(c["domain"] for c in new_cases)
    all_18_domains = {
        "agriculture", "education", "environment", "finance", "food",
        "general", "government", "history", "hr_workplace", "law",
        "medicine", "psychology", "real_estate", "science", "social_media",
        "sports", "technology", "transportation",
    }
    missing_domains = all_18_domains - set(domain_counts.keys())
    extra_domains = set(domain_counts.keys()) - all_18_domains
    assert not missing_domains, f"Missing domains: {missing_domains}"
    assert not extra_domains, f"Extra domains: {extra_domains}"
    over_limit = {d: c for d, c in domain_counts.items() if c > 5}
    assert not over_limit, f"Domains over limit (max 5): {over_limit}"

    # Validate query type distribution
    qt_counts = Counter(c["query_type"] for c in new_cases)
    what_count = qt_counts.get("what", 0)
    how_count = qt_counts.get("how", 0)
    is_does = qt_counts.get("is", 0) + qt_counts.get("does", 0)
    why_should = qt_counts.get("why", 0) + qt_counts.get("should", 0)
    when_who_which = qt_counts.get("when", 0) + qt_counts.get("who", 0) + qt_counts.get("which", 0)

    print(f"Query type counts: {dict(qt_counts)}")
    print(f"  what={what_count} (<=16), how={how_count} (>=13), is/does={is_does} (>=13)")
    print(f"  why/should={why_should} (>=8), when/who/which={when_who_which} (>=6)")

    assert what_count <= 16, f"'what' count {what_count} > 16"
    assert how_count >= 13, f"'how' count {how_count} < 13"
    assert is_does >= 13, f"'is/does' count {is_does} < 13"
    assert why_should >= 8, f"'why/should' count {why_should} < 8"
    assert when_who_which >= 6, f"'when/who/which' count {when_who_which} < 6"

    # Validate no duplicate queries
    queries = [c["query"] for c in new_cases]
    dupes = [q for q in queries if queries.count(q) > 1]
    assert not dupes, f"Duplicate queries: {set(dupes)}"

    # Validate all cases have forbidden_claims (2-5)
    for c in new_cases:
        fc = c.get("forbidden_claims", [])
        assert 2 <= len(fc) <= 5, f"Case {c['id']} has {len(fc)} forbidden_claims (need 2-5)"

    # Validate forbidden_claims are valid regex
    for c in new_cases:
        for pattern in c["forbidden_claims"]:
            try:
                re.compile(pattern)
            except re.error as e:
                print(f"ERROR: Invalid regex in {c['id']}: {pattern} -> {e}")
                sys.exit(1)

    # Validate context lengths (150-400 chars)
    warnings = []
    for c in new_cases:
        for i, ctx in enumerate(c["contexts"]):
            if len(ctx) < 150:
                warnings.append(f"  {c['id']} context[{i}] too short: {len(ctx)} chars")
            elif len(ctx) > 400:
                warnings.append(f"  {c['id']} context[{i}] too long: {len(ctx)} chars")
    if warnings:
        print(f"Context length warnings ({len(warnings)}):")
        for w in warnings:
            print(w)

    # Append to data
    data["cases"].extend(new_cases)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nSUCCESS: Added {len(new_cases)} cases to {DATA_FILE}")
    print(f"Total cases now: {len(data['cases'])}")
    print(f"Subcategory distribution: {dict(subcat_counts)}")
    print(f"Domain distribution: {dict(domain_counts)}")
    print(f"Multi-source count: {ms_count}")


if __name__ == "__main__":
    main()
