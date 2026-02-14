#!/usr/bin/env python3
"""Add 53 new medium-difficulty grounding test cases (t1_grounding_medium_011 through _063)."""

import json
import re
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "tier1_core" / "grounding.json"

NEW_CASES = [
    # =========================================================================
    # NUMERICAL_HALLUCINATION (6 cases: 011-016)
    # =========================================================================
    {
        "id": "t1_grounding_medium_011",
        "difficulty": "medium",
        "subcategory": "numerical_hallucination",
        "query": "How many employees does Meridian Systems have?",
        "contexts": [
            "Meridian Systems is a mid-sized software company headquartered in Austin, Texas. Founded in 2012, the company specializes in supply chain management solutions for the manufacturing sector. Meridian operates offices in three countries and has been recognized as a Top Workplace by the Austin Business Journal for four consecutive years. The company reported $87 million in revenue for fiscal year 2024 and recently opened a new engineering center in Dublin, Ireland. Meridian's client list includes several Fortune 500 manufacturers, and the company has partnerships with SAP and Oracle for enterprise integration services."
        ],
        "expected_mode": "trustworthy",
        "description": "Context describes the company but never states employee count",
        "rationale": "A model might estimate employee count from revenue or 'mid-sized' descriptor, but the context never gives a number",
        "forbidden_claims": [
            "\\d{2,}\\s*employees",
            "workforce of \\d",
            "staff of \\d",
            "employs \\d",
            "team of \\d{2,}",
            "headcount of \\d"
        ],
        "domain": "technology",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_012",
        "difficulty": "medium",
        "subcategory": "numerical_hallucination",
        "query": "How much interest does Crestfield Bank's savings account earn?",
        "contexts": [
            "Crestfield Bank launched its new high-yield savings account in March 2025. The account requires no minimum balance and allows unlimited withdrawals. Crestfield has described the rate as 'highly competitive' compared to national averages. The bank, which operates 42 branches across the Midwest, has seen a 30% increase in new account openings since the launch. FDIC insurance covers all deposits up to $250,000. Crestfield was founded in 1987 in Des Moines, Iowa, and manages over $8 billion in total assets across personal and commercial banking divisions."
        ],
        "expected_mode": "trustworthy",
        "description": "Context discusses a savings product but never states the actual interest rate",
        "rationale": "The phrase 'highly competitive' might tempt a model to invent a specific APY, but no rate is given",
        "forbidden_claims": [
            "\\d+\\.\\d+\\s*%",
            "\\d+\\s*%\\s*(APY|apy|interest|annual)",
            "rate (of|is|at) \\d",
            "earns? \\d+\\.?\\d*\\s*%",
            "yields? \\d"
        ],
        "domain": "finance",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_013",
        "difficulty": "medium",
        "subcategory": "numerical_hallucination",
        "query": "How many patients were enrolled in the Veridex Phase III trial?",
        "contexts": [
            "Veridex Therapeutics announced positive results from its Phase III clinical trial of VDX-401 for treatment-resistant depression. The multi-center trial was conducted at hospitals across North America and Europe over 18 months. Primary endpoints were met with statistical significance, and the safety profile was consistent with earlier Phase II data. Veridex plans to submit a New Drug Application to the FDA in the first half of 2026. The company's stock rose 14% following the announcement, and analysts at JPMorgan projected peak annual sales of $2 billion for VDX-401 if approved."
        ],
        "expected_mode": "trustworthy",
        "description": "Context reports trial results but never specifies enrollment numbers",
        "rationale": "A model might guess a typical Phase III enrollment number, but the context provides none",
        "forbidden_claims": [
            "\\d{2,}\\s*(patients|participants|subjects|people)",
            "enrolled \\d",
            "enrollment of \\d",
            "sample (size|of) \\d",
            "recruited \\d",
            "included \\d{2,}\\s*(patients|participants)"
        ],
        "domain": "medicine",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_014",
        "difficulty": "medium",
        "subcategory": "numerical_hallucination",
        "query": "How many students are in the average class at Thornwood Academy?",
        "contexts": [
            "Thornwood Academy is a private K-12 school in Fairfield, Connecticut, known for its rigorous academic program and individualized instruction. The school prides itself on maintaining small class sizes to ensure personalized attention for every student. Thornwood employs 85 full-time teachers and offers over 20 Advanced Placement courses. The school's college acceptance rate consistently exceeds 98%, with many graduates attending Ivy League and top-tier universities. Tuition for the 2024-2025 academic year includes access to state-of-the-art science labs, a performing arts center, and two athletic fields."
        ],
        "expected_mode": "trustworthy",
        "description": "Context mentions small class sizes but never gives the actual average number",
        "rationale": "Knowing the teacher count and the emphasis on small classes may tempt a model to estimate, but no class size figure is stated",
        "forbidden_claims": [
            "\\d{1,2}\\s*students (per|in)",
            "class(es)? of \\d",
            "average (of |class size (of |is )?)\\d",
            "ratio of \\d",
            "\\d+:\\d+ (ratio|student)"
        ],
        "domain": "education",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_015",
        "difficulty": "medium",
        "subcategory": "numerical_hallucination",
        "query": "How many acres does the Larkfield Solar Farm cover?",
        "contexts": [
            "The Larkfield Solar Farm, located in central Nevada, is one of the largest solar installations in the western United States. Completed in 2023, the facility generates enough electricity to power approximately 45,000 homes annually. The project was developed by Solaris Energy Corp and received $180 million in federal tax credits. Larkfield uses bifacial solar panels with single-axis tracking systems to maximize energy capture throughout the day. The facility created over 500 construction jobs during its two-year build phase and now employs 35 permanent operations and maintenance staff."
        ],
        "expected_mode": "trustworthy",
        "description": "Context describes the solar farm's output and cost but not its physical acreage",
        "rationale": "A model might estimate acreage from the number of homes powered, but the context never states it",
        "forbidden_claims": [
            "\\d{2,}\\s*acres?",
            "covers? \\d",
            "spans? \\d",
            "\\d+\\s*square (miles?|kilometers?|feet|metres?|meters?)",
            "area of \\d",
            "across \\d{2,}\\s*acres?"
        ],
        "domain": "environment",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_016",
        "difficulty": "medium",
        "subcategory": "numerical_hallucination",
        "query": "How fast is the top speed of the Varex R7 electric motorcycle?",
        "contexts": [
            "The Varex R7 is an all-electric sport motorcycle released by Varex Motors in January 2025. It features a liquid-cooled permanent magnet motor and a 15.5 kWh battery pack providing smooth and powerful acceleration. The R7 can accelerate from 0 to 60 mph in under 3 seconds and has a claimed range of 160 miles on a single charge. The motorcycle weighs 485 pounds and uses regenerative braking. Varex has positioned the R7 as a competitor to premium sport bikes from established manufacturers like Ducati and Yamaha. Pricing starts at $24,990 for the base model."
        ],
        "expected_mode": "trustworthy",
        "description": "Context gives 0-60 time and range but not top speed",
        "rationale": "With detailed performance specs provided, a model might extrapolate top speed, but it is never stated",
        "forbidden_claims": [
            "top speed (of|is|at|reaches?) \\d",
            "\\d{2,}\\s*(mph|km/h|kmh|kph)",
            "reaches? \\d{2,}",
            "maxes? out at \\d",
            "maximum speed of \\d"
        ],
        "domain": "transportation",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },

    # =========================================================================
    # ATTRIBUTION_HALLUCINATION (6 cases: 017-022)
    # =========================================================================
    {
        "id": "t1_grounding_medium_017",
        "difficulty": "medium",
        "subcategory": "attribution_hallucination",
        "query": "Which university conducted the research on coral reef bleaching?",
        "contexts": [
            "A new study published in Nature Climate Change found that coral reef bleaching events have increased by 40% over the past decade across tropical ocean regions worldwide. The research team used satellite imaging and underwater sensors deployed across 12 reef sites in the Indo-Pacific region. The study tracked bleaching patterns over a five-year period from 2019 to 2024 and linked rising sea surface temperatures to mass bleaching events. The findings have implications for marine conservation policy worldwide, and several international organizations have cited the study in calls for stricter carbon emission targets."
        ],
        "expected_mode": "trustworthy",
        "description": "Context describes the study but never names the institution that conducted it",
        "rationale": "A model might attribute the study to a well-known marine science university, but no institution is named",
        "forbidden_claims": [
            "(University|Institute|College) of \\w+",
            "conducted by \\w+",
            "researchers (from|at) \\w+",
            "team (from|at) (the )?\\w+ (University|Institute)",
            "led by (Dr\\.?|Professor|Prof\\.?) \\w+"
        ],
        "domain": "science",
        "query_type": "which",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_018",
        "difficulty": "medium",
        "subcategory": "attribution_hallucination",
        "query": "Who authored the report on remote work productivity?",
        "contexts": [
            "A comprehensive report released in September 2024 analyzed remote work productivity across 500 companies in the technology sector. The report found that hybrid workers were 12% more productive than fully remote employees but 5% less productive than in-office workers. The analysis controlled for role type, seniority, and company size to ensure valid comparisons. It recommended that companies adopt flexible scheduling rather than mandating full return-to-office policies. The report was widely covered by business media outlets and sparked debate among HR professionals about optimal workplace arrangements for knowledge workers."
        ],
        "expected_mode": "trustworthy",
        "description": "Context describes the report's findings but never identifies the author or publishing organization",
        "rationale": "A model might attribute it to McKinsey, Gallup, or another known firm, but no author is named",
        "forbidden_claims": [
            "(authored|written|published|released) by \\w+",
            "(McKinsey|Gallup|Deloitte|Gartner|Forrester|BCG|Bain|PwC|KPMG)",
            "(Dr\\.?|Professor|Prof\\.?) \\w+ \\w+",
            "according to (\\w+ ){1,3}(who|at)"
        ],
        "domain": "hr_workplace",
        "query_type": "who",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_019",
        "difficulty": "medium",
        "subcategory": "attribution_hallucination",
        "query": "Which law firm represented Orion Health in the patent dispute?",
        "contexts": [
            "Orion Health Inc. won a significant patent infringement case in the Eastern District of Texas in November 2024. The court ruled that HealthSync Technologies had violated two of Orion's patents related to interoperability protocols for electronic health records. Orion was awarded $34 million in damages after a three-week jury trial. The case had been ongoing for three years and is expected to set a precedent for health-tech IP disputes nationwide. HealthSync has indicated it will appeal the ruling, and legal experts say the case could eventually reach the Federal Circuit Court of Appeals."
        ],
        "expected_mode": "trustworthy",
        "description": "Context covers the patent case outcome but never names the law firm",
        "rationale": "A model might invent a plausible law firm name, but none is mentioned in the context",
        "forbidden_claims": [
            "represented by \\w+",
            "(law firm|firm|attorneys?) (of |from |at )?(\\w+ )+(&|and) \\w+",
            "counsel (was|were|from|at) \\w+",
            "hired \\w+ (LLP|LLC|& \\w+)",
            "legal team (from|at|led by) \\w+"
        ],
        "domain": "law",
        "query_type": "which",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_020",
        "difficulty": "medium",
        "subcategory": "attribution_hallucination",
        "query": "Who funded the affordable housing initiative in Portland?",
        "contexts": [
            "Portland, Oregon launched a major affordable housing initiative in early 2025 aimed at constructing 3,000 new units over five years. The initiative targets families earning below 60% of the area median income and prioritizes developments near public transit corridors. Construction will incorporate green building standards including energy-efficient HVAC systems and rooftop solar panels. The city council approved the plan unanimously after months of community input, and the first phase of construction is scheduled to break ground in the fall of 2025 at two sites in the Lents neighborhood."
        ],
        "expected_mode": "trustworthy",
        "description": "Context describes the housing initiative but never identifies the funding source",
        "rationale": "A model might attribute funding to HUD, a state bond, or a philanthropic organization, but no funding source is named",
        "forbidden_claims": [
            "funded by \\w+",
            "financed (by|through) \\w+",
            "\\$\\d+\\s*(million|billion)\\s*(from|by|in) (federal|state|grant)",
            "(HUD|Department of Housing)",
            "(grant|bond|levy|tax) (from|by|through) \\w+"
        ],
        "domain": "government",
        "query_type": "who",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_021",
        "difficulty": "medium",
        "subcategory": "attribution_hallucination",
        "query": "Which regulatory body approved the new food labeling standard?",
        "contexts": [
            "A new food labeling standard requiring clearer allergen warnings went into effect across the European Union in January 2025. The standard mandates that all packaged foods display allergen information in bold text on the front of the package, not just in the ingredients list. Food manufacturers were given an 18-month transition period to update their packaging. Consumer advocacy groups praised the change as a significant step forward for food safety, noting that allergic reactions from mislabeled products have been rising in recent years. Some manufacturers, however, criticized the compliance costs, estimating expenses of up to 200,000 euros per product line."
        ],
        "expected_mode": "trustworthy",
        "description": "Context describes the labeling standard but never names the specific regulatory body that approved it",
        "rationale": "A model might name EFSA, the European Commission, or another EU body, but none is specified",
        "forbidden_claims": [
            "approved by (the )?(\\w+ ){1,4}(Authority|Agency|Commission|Council|Board)",
            "(EFSA|European Commission|European Council|European Parliament)",
            "issued by \\w+",
            "regulator(y body)? (was|is) (the )?\\w+"
        ],
        "domain": "food",
        "query_type": "which",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_022",
        "difficulty": "medium",
        "subcategory": "attribution_hallucination",
        "query": "Who designed the algorithm used in the Nextera trading platform?",
        "contexts": [
            "The Nextera trading platform uses a proprietary high-frequency trading algorithm that has consistently outperformed market benchmarks since its deployment in 2022. The algorithm processes over 10 million data points per second and executes trades within microseconds. Nextera Financial reported that the algorithm contributed to a 22% return for its flagship fund in 2024, well above the S&P 500 benchmark of 15%. The platform serves institutional clients including pension funds and endowments across North America and has attracted over $12 billion in assets under management since launch."
        ],
        "expected_mode": "trustworthy",
        "description": "Context describes the algorithm's performance but never names its designer or development team",
        "rationale": "A model might invent a CTO name or attribute it to a known quant researcher, but no person is identified",
        "forbidden_claims": [
            "designed by (Dr\\.?|Professor|Prof\\.?)? ?\\w+ \\w+",
            "developed by \\w+ \\w+",
            "created by \\w+",
            "team led by \\w+",
            "(CTO|chief|head|lead) .{0,10}\\w+ \\w+"
        ],
        "domain": "finance",
        "query_type": "who",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },

    # =========================================================================
    # TEMPORAL_CONFUSION (6 cases: 023-028)
    # =========================================================================
    {
        "id": "t1_grounding_medium_023",
        "difficulty": "medium",
        "subcategory": "temporal_confusion",
        "query": "When did BrightPath Education begin offering online courses?",
        "contexts": [
            "BrightPath Education is an accredited online learning platform that currently serves over 200,000 students globally. As of 2024, BrightPath offers 1,500 online courses across 40 subject areas including technology, business, healthcare, and creative arts. The platform partners with 50 universities and uses AI-driven personalized learning paths to adapt course difficulty to each student's progress. BrightPath recently expanded into corporate training with a dedicated business-to-business portal launched in August 2024 that already has 75 enterprise clients signed up for annual subscriptions."
        ],
        "expected_mode": "trustworthy",
        "description": "Context gives current stats but never states when online courses first started",
        "rationale": "A model might infer a founding date from current scale, but the start date for online courses is never mentioned",
        "forbidden_claims": [
            "(started|began|launched|introduced|offered) (online |courses )?(in|since|from) (19|20)\\d{2}",
            "since (19|20)\\d{2}",
            "founded in (19|20)\\d{2}",
            "has been (offering|providing) .{0,20}since (19|20)\\d{2}"
        ],
        "domain": "education",
        "query_type": "when",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "temporal",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_024",
        "difficulty": "medium",
        "subcategory": "temporal_confusion",
        "query": "When was the last time the Cedar Rapids levee system was upgraded?",
        "contexts": [
            "The Cedar Rapids levee system protects approximately 1,300 acres of residential and commercial property along the Cedar River in Iowa. The levee was originally constructed in the 1960s following a series of devastating floods that displaced thousands of residents. In 2008, the system was overwhelmed during record flooding that caused over $5 billion in damages to the city and surrounding communities. The Army Corps of Engineers has classified sections of the levee as needing significant repairs, and city officials have been actively advocating for federal funding for improvements to prevent another catastrophic failure."
        ],
        "expected_mode": "trustworthy",
        "description": "Context gives construction date and a flood event date but never states when the levee was last upgraded",
        "rationale": "A model might conflate the 2008 flood event with an upgrade, or invent a post-2008 upgrade date",
        "forbidden_claims": [
            "(upgraded|improved|renovated|repaired|reinforced) in (19|20)\\d{2}",
            "last (upgraded|improved|renovated) in (19|20)\\d{2}",
            "(20[1-2]\\d).{0,30}(upgrade|improvement|renovation|repair)",
            "completed .{0,20}(upgrade|renovation) in (19|20)\\d{2}"
        ],
        "domain": "government",
        "query_type": "when",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "temporal",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_025",
        "difficulty": "medium",
        "subcategory": "temporal_confusion",
        "query": "When did the Harmon Art Gallery first open to the public?",
        "contexts": [
            "The Harmon Art Gallery in Savannah, Georgia, houses one of the Southeast's largest collections of American Impressionist paintings. The gallery underwent a $12 million renovation completed in 2021, adding 8,000 square feet of exhibition space and a climate-controlled storage facility for delicate works. Its permanent collection includes over 400 works, with notable pieces by Mary Cassatt and Childe Hassam acquired from private estates. The gallery hosts rotating exhibitions quarterly and attracts roughly 150,000 visitors per year, making it one of Savannah's top cultural destinations alongside the Telfair Museums."
        ],
        "expected_mode": "trustworthy",
        "description": "Context gives the renovation date (2021) but never states when the gallery originally opened",
        "rationale": "A model might confuse the renovation completion date with the original opening date or invent a founding year",
        "forbidden_claims": [
            "(opened|established|founded|inaugurated) in (18|19|20)\\d{2}",
            "first opened .{0,20}(18|19|20)\\d{2}",
            "since (18|19|20)\\d{2}",
            "doors (opened|first) in (18|19|20)\\d{2}",
            "has been open since (18|19|20)\\d{2}"
        ],
        "domain": "history",
        "query_type": "when",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "temporal",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_026",
        "difficulty": "medium",
        "subcategory": "temporal_confusion",
        "query": "When did Greenleaf Organics receive its USDA organic certification?",
        "contexts": [
            "Greenleaf Organics is a family-owned farm in Vermont's Champlain Valley that grows over 30 varieties of vegetables and herbs using sustainable methods. The farm practices regenerative agriculture and holds USDA organic certification for all its produce. Greenleaf sells through farmers' markets, a community-supported agriculture program with 250 members, and wholesale to regional restaurants. The farm was started in 2005 by siblings Marta and Paul Lindgren and spans 120 acres of fertile valley bottomland. In 2023, Greenleaf added a 6,000 square foot greenhouse to extend its growing season by three months."
        ],
        "expected_mode": "trustworthy",
        "description": "Context confirms the farm has organic certification but never states when it was obtained",
        "rationale": "A model might assume certification coincided with founding in 2005 or invent a date, but it is never specified",
        "forbidden_claims": [
            "(certified|received|obtained|granted|awarded) .{0,15}(in|since) (19|20)\\d{2}",
            "certification (in|since|from|was granted in) (19|20)\\d{2}",
            "became (certified|organic) in (19|20)\\d{2}",
            "organic since (19|20)\\d{2}"
        ],
        "domain": "agriculture",
        "query_type": "when",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "temporal",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_027",
        "difficulty": "medium",
        "subcategory": "temporal_confusion",
        "query": "When was the last time Tidewater Insurance raised its premiums?",
        "contexts": [
            "Tidewater Insurance, a regional carrier based in Norfolk, Virginia, provides homeowners and flood insurance to coastal communities throughout the mid-Atlantic and Southeast. The company covers properties in five southeastern states and has paid out over $400 million in claims since 2018 due to increasing hurricane frequency and severity. Tidewater's current premiums reflect risk modeling that accounts for rising storm severity and sea-level rise projections. The company reported a combined ratio of 98.2% for fiscal year 2024, indicating near-breakeven underwriting performance that analysts say is unsustainable long-term."
        ],
        "expected_mode": "trustworthy",
        "description": "Context discusses premiums generally but never states when they were last raised",
        "rationale": "A model might infer a premium increase from the claims data or risk modeling mention, but no date is given",
        "forbidden_claims": [
            "(raised|increased|hiked|adjusted) .{0,20}(in|during|for) (19|20)\\d{2}",
            "premiums? (went up|rose|increased) (in|by) (19|20)?\\d",
            "last (raised|increased|adjusted) in (19|20)\\d{2}",
            "\\d+\\s*% (increase|hike|raise) in (19|20)\\d{2}"
        ],
        "domain": "finance",
        "query_type": "when",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "temporal",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_028",
        "difficulty": "medium",
        "subcategory": "temporal_confusion",
        "query": "When did Dr. Elena Vasquez join the Stanford psychology department?",
        "contexts": [
            "Dr. Elena Vasquez is a cognitive psychologist at Stanford University whose research focuses on decision-making under uncertainty and cognitive bias in professional settings. She has published over 60 peer-reviewed papers and received the American Psychological Association's Distinguished Scientific Award in 2022. Dr. Vasquez directs the Behavioral Decision Lab, which has secured $4.5 million in NIH funding over the past five years for studies on risk perception. She earned her PhD from the University of Michigan and completed a postdoctoral fellowship at Princeton before moving to the West Coast."
        ],
        "expected_mode": "trustworthy",
        "description": "Context describes her career but never states when she joined Stanford",
        "rationale": "A model might try to calculate a start date from career milestones, but the joining date is never stated",
        "forbidden_claims": [
            "(joined|started|began|arrived|appointed) .{0,15}(in|since) (19|20)\\d{2}",
            "at Stanford since (19|20)\\d{2}",
            "has been at Stanford (since|for) \\d",
            "faculty (member |position )?(since|in|from) (19|20)\\d{2}"
        ],
        "domain": "psychology",
        "query_type": "when",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "temporal",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },

    # =========================================================================
    # ENTITY_BLENDING (6 cases: 029-034)
    # =========================================================================
    {
        "id": "t1_grounding_medium_029",
        "difficulty": "medium",
        "subcategory": "entity_blending",
        "query": "Does Pinnacle Health or Summit Medical have a higher patient satisfaction rating?",
        "contexts": [
            "Pinnacle Health Center is a 350-bed hospital in Columbus, Ohio, specializing in cardiac care and orthopedic surgery. It was ranked among the top 50 hospitals nationally by U.S. News & World Report for cardiac procedures. Summit Medical Group operates 12 outpatient clinics across central Ohio and provides primary care, urgent care, and diagnostic imaging services to the community. Summit treated approximately 180,000 patients in 2024 and recently opened a new clinic in Dublin, Ohio, its largest facility to date with 40 exam rooms and a walk-in urgent care wing."
        ],
        "expected_mode": "trustworthy",
        "description": "Context describes both healthcare organizations but gives patient satisfaction ratings for neither",
        "rationale": "A model might infer Pinnacle has higher satisfaction from its U.S. News ranking, but no satisfaction scores are given for either entity",
        "forbidden_claims": [
            "\\d+\\s*%\\s*(satisfaction|approval|rating)",
            "satisfaction (score|rating|rate) (of|is|was) \\d",
            "(Pinnacle|Summit) (has|had|scored|rated|achieved) (a )?(higher|lower|\\d)",
            "(higher|lower) (satisfaction|rating|score) (than|compared)",
            "rated \\d+(\\.\\d+)? out of"
        ],
        "domain": "medicine",
        "query_type": "does",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "comparative",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_030",
        "difficulty": "medium",
        "subcategory": "entity_blending",
        "query": "Which company has more revenue, Axon Dynamics or Prism Technologies?",
        "contexts": [
            "Axon Dynamics is an aerospace components manufacturer based in Wichita, Kansas, that supplies landing gear assemblies and hydraulic systems to major aircraft makers including Boeing and Airbus. Axon employs 2,800 workers across two production facilities and has been operating since 1994. Prism Technologies is a defense electronics firm headquartered in Huntsville, Alabama, specializing in radar systems and electronic warfare equipment. Prism holds contracts with the U.S. Department of Defense valued at over $500 million and recently won a competitive bid to supply next-generation electronic countermeasure systems to the Navy."
        ],
        "expected_mode": "trustworthy",
        "description": "Context describes both companies but only mentions contract values for Prism, not revenue for either",
        "rationale": "A model might confuse Prism's contract value with revenue or estimate Axon's revenue from employee count",
        "forbidden_claims": [
            "(Axon|Prism) (has|had|reported|generated|earned) .{0,10}\\$\\d+\\s*(million|billion) (in )?revenue",
            "revenue (of|is|was) \\$\\d",
            "(higher|lower|more|greater) revenue",
            "\\$\\d+\\s*(million|billion)\\s*(in )?(annual )?revenue"
        ],
        "domain": "science",
        "query_type": "which",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "comparative",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_031",
        "difficulty": "medium",
        "subcategory": "entity_blending",
        "query": "Is the Ridgeway Trail or the Cascade Loop longer in total distance?",
        "contexts": [
            "The Ridgeway Trail is a popular hiking route in the Blue Ridge Mountains of North Carolina that passes through old-growth forest and features several stunning waterfalls and scenic overlooks. The trail is rated as moderately difficult and is well-maintained by a local volunteer conservation organization that performs annual upkeep. The Cascade Loop is a backcountry trek in Washington State's North Cascades that traverses alpine meadows, glacier-fed valleys, and high mountain passes above 7,000 feet elevation. The Cascade Loop is considered one of the most scenic multi-day hikes in the Pacific Northwest and requires a backcountry permit obtained through the National Park Service."
        ],
        "expected_mode": "trustworthy",
        "description": "Context describes both trails but never states the distance of either one",
        "rationale": "A model might invent mileage for these trails based on typical hiking trail lengths",
        "forbidden_claims": [
            "\\d+\\s*(miles?|kilometers?|km)",
            "(Ridgeway|Cascade) (is|spans?|covers?|stretches?) \\d",
            "(longer|shorter) (at|by) \\d",
            "total (distance|length) (of|is) \\d",
            "approximately \\d+\\s*(miles?|km)"
        ],
        "domain": "environment",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "comparative",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_032",
        "difficulty": "medium",
        "subcategory": "entity_blending",
        "query": "Which platform has a larger user base, Chatly or Voxal?",
        "contexts": [
            "Chatly is a messaging application popular among Gen Z users that features disappearing messages, group audio rooms, and AI-powered sticker generation based on conversation context. The app was launched in 2021 and is available on iOS and Android in over 40 countries worldwide. Voxal is a voice-first social network that lets users share short audio clips, host live conversations, and follow topic-based channels curated by moderators. Voxal has been growing rapidly in markets across Southeast Asia and Latin America since its 2022 launch, and the company recently raised $90 million in Series C funding led by Sequoia Capital."
        ],
        "expected_mode": "trustworthy",
        "description": "Context describes both platforms but gives no user count for either",
        "rationale": "A model might invent user numbers or declare one larger based on descriptions like 'growing rapidly'",
        "forbidden_claims": [
            "\\d+\\s*(million|billion|thousand)\\s*(users?|accounts?|downloads?|installs?)",
            "(Chatly|Voxal) (has|had|boasts?|claims?|reached) .{0,15}\\d+\\s*(million|users)",
            "(larger|bigger|more) user (base|count)",
            "(more|over|approximately) \\d+\\s*(million|users)"
        ],
        "domain": "social_media",
        "query_type": "which",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "comparative",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_033",
        "difficulty": "medium",
        "subcategory": "entity_blending",
        "query": "Does Eastgate University or Westfield College have more parking spaces at their main campus?",
        "contexts": [
            "Eastgate University is a public research institution in eastern Pennsylvania with an enrollment of 18,000 undergraduate and graduate students. The main campus covers 200 acres and includes a Division I athletics complex with a 15,000-seat football stadium. Westfield College is a private liberal arts school in western Massachusetts with 3,500 students on its intimate 85-acre campus. Westfield is known for its historic Gothic architecture and was designated a National Historic Landmark in 1998. Both institutions have invested heavily in new dormitory construction in recent years to accommodate growing housing demand."
        ],
        "expected_mode": "trustworthy",
        "description": "Context describes both campuses but never mentions parking capacity for either",
        "rationale": "A model might estimate parking spaces from enrollment or campus size, but no parking data is given",
        "forbidden_claims": [
            "\\d{2,}\\s*parking (spaces?|spots?|stalls?)",
            "(Eastgate|Westfield) has (more|fewer|\\d)",
            "parking (capacity|lot|garage) (of|with|holds?) \\d",
            "(more|fewer) parking",
            "accommodates? \\d+\\s*(cars?|vehicles?)"
        ],
        "domain": "education",
        "query_type": "does",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "comparative",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_034",
        "difficulty": "medium",
        "subcategory": "entity_blending",
        "query": "Which restaurant received a higher health inspection score, Bella Cucina or Sakura Garden?",
        "contexts": [
            "Bella Cucina is an Italian restaurant in downtown Nashville that has been operating since 2016 in a restored 1920s brick building. The restaurant seats 120 guests and is known for its house-made pasta and wood-fired pizzas using imported Italian flour. Bella Cucina was named Nashville's Best Italian Restaurant by the Tennessean in 2023. Sakura Garden is a Japanese restaurant across the street, offering omakase-style dining and an extensive sake list with over 40 selections. Sakura Garden opened in 2019 and has earned a loyal following for its fresh fish flown in daily from Tokyo's Tsukiji market."
        ],
        "expected_mode": "trustworthy",
        "description": "Context describes both restaurants but gives no health inspection scores for either",
        "rationale": "A model might invent scores or assume the award-winning restaurant scored higher",
        "forbidden_claims": [
            "(score|rating|grade) (of|is|was) \\d",
            "scored \\d",
            "\\d+\\s*(out of|/\\s*\\d)",
            "grade (of |is |was )?[A-F]",
            "(Bella|Sakura) (received|scored|earned|got) (a )?(higher|lower|\\d)"
        ],
        "domain": "food",
        "query_type": "which",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "comparative",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },

    # =========================================================================
    # PROCESS_HALLUCINATION (6 cases: 035-040)
    # =========================================================================
    {
        "id": "t1_grounding_medium_035",
        "difficulty": "medium",
        "subcategory": "process_hallucination",
        "query": "How does Solvent Bank process international wire transfers?",
        "contexts": [
            "Solvent Bank offers international wire transfer services to both personal and business customers across its network of retail branches and digital channels. Transfers can be initiated online, by phone, or at any branch location during regular business hours. Solvent supports transfers to over 120 countries and offers competitive exchange rates compared to other regional banks. The bank charges a flat fee for outgoing international wires and provides real-time tracking through its mobile app. Customers must have an active checking account in good standing to use the wire transfer service."
        ],
        "expected_mode": "trustworthy",
        "description": "Context describes the wire transfer service but never explains the internal processing steps",
        "rationale": "A model might invent SWIFT processing steps or intermediary bank procedures that are not described",
        "forbidden_claims": [
            "step \\d",
            "first.{0,30}(submit|enter|provide|verify)",
            "SWIFT (code|network|message|system) (is used|routes|sends)",
            "intermediary bank",
            "correspondent bank",
            "within \\d+\\s*(hours?|days?|business days?)"
        ],
        "domain": "finance",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "procedural",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_036",
        "difficulty": "medium",
        "subcategory": "process_hallucination",
        "query": "How does the Arcturus satellite collect atmospheric data?",
        "contexts": [
            "The Arcturus satellite was launched by the National Oceanic and Atmospheric Administration in October 2024 as part of its next-generation weather monitoring program. Orbiting at an altitude of 35,786 kilometers in geostationary orbit, Arcturus provides continuous coverage of the Western Hemisphere for meteorological observations. The satellite is equipped with advanced atmospheric sensing instruments and a high-bandwidth communications array for rapid data transmission. NOAA has called Arcturus a significant upgrade over its predecessor, which had been in service for 11 years and was operating beyond its designed lifespan with degraded sensors."
        ],
        "expected_mode": "trustworthy",
        "description": "Context describes the satellite and its purpose but not the specific data collection process",
        "rationale": "A model might fabricate specific instrument operations or data collection methods not mentioned",
        "forbidden_claims": [
            "step \\d",
            "(infrared|microwave|lidar|radar) (sensor|scanner|sounder|imager) (scans?|measures?|detects?)",
            "(measures?|collects?|captures?) .{0,20}(wavelength|frequency|spectrum)",
            "scans? (the )?(atmosphere|surface|cloud) (every|at|in) \\d",
            "resolution of \\d"
        ],
        "domain": "science",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "procedural",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_037",
        "difficulty": "medium",
        "subcategory": "process_hallucination",
        "query": "How does MapleGrid determine electricity pricing for industrial customers?",
        "contexts": [
            "MapleGrid Energy is a regulated utility serving industrial and commercial customers in Ontario, Canada, providing reliable electricity to critical infrastructure. The company supplies power to over 4,000 industrial facilities including auto plants, steel mills, and data centers across the province. MapleGrid's pricing for industrial customers is subject to approval by the Ontario Energy Board through a formal regulatory process. In 2024, industrial electricity rates in Ontario were among the most competitive in North America, which MapleGrid credits to a diversified generation portfolio including nuclear, hydro, and natural gas assets that balance cost and reliability."
        ],
        "expected_mode": "trustworthy",
        "description": "Context discusses industrial pricing generally and mentions regulatory oversight but never explains the pricing methodology",
        "rationale": "A model might invent demand charges, time-of-use tiers, or rate formulas not described in context",
        "forbidden_claims": [
            "demand charge of \\$?\\d",
            "\\$\\d+(\\.\\d+)?\\s*per (kWh|MWh|kilowatt)",
            "(time-of-use|peak|off-peak) rat(e|ing) (of|is|at) \\$?\\d",
            "step \\d",
            "calculated (by|using|based on) .{0,30}(formula|factor|multiplier)"
        ],
        "domain": "environment",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "procedural",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_038",
        "difficulty": "medium",
        "subcategory": "process_hallucination",
        "query": "How does the city of Ashford handle zoning variance requests?",
        "contexts": [
            "The city of Ashford, Oregon, has a zoning ordinance that divides land into residential, commercial, industrial, and mixed-use zones with specific permitted uses in each category. Property owners who wish to use their land in ways not permitted by current zoning may apply for a variance through the planning department. The Ashford Planning Department receives approximately 80 variance applications per year, and the approval rate has hovered around 45% over the past three years according to the department's annual report. Variance decisions can be appealed to the city council within 30 days of the initial determination being issued."
        ],
        "expected_mode": "trustworthy",
        "description": "Context mentions variance applications and approval rates but never describes the handling process",
        "rationale": "A model might invent specific procedural steps like public hearings, review committees, or fee amounts",
        "forbidden_claims": [
            "step \\d",
            "first.{0,30}(submit|file|complete|fill)",
            "public (hearing|meeting|notice) (is |must be )?(held|required|scheduled)",
            "committee (reviews?|meets?|votes?|decides?)",
            "(fee|cost|charge) (of|is) \\$?\\d"
        ],
        "domain": "government",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "procedural",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_039",
        "difficulty": "medium",
        "subcategory": "process_hallucination",
        "query": "How does NovaMed screen blood donations for pathogens?",
        "contexts": [
            "NovaMed Blood Services is a nonprofit blood bank operating in the southeastern United States that relies entirely on volunteer donors for its supply. The organization collects approximately 300,000 units of blood annually from mobile blood drives and fixed donation centers in seven states. NovaMed follows FDA guidelines for blood safety and screens all donations for a comprehensive panel of infectious diseases before releasing any product. In 2024, the organization achieved a contamination rate below 0.001%, one of the lowest in the industry. NovaMed supplies blood products including red blood cells, platelets, and plasma to over 200 hospitals."
        ],
        "expected_mode": "trustworthy",
        "description": "Context mentions that screening occurs but never describes the specific screening methods",
        "rationale": "A model might fabricate specific test names like NAT, ELISA, or PCR protocols not mentioned in context",
        "forbidden_claims": [
            "(NAT|ELISA|PCR|nucleic acid|antibody|antigen) test",
            "step \\d",
            "tested for .{0,30}(HIV|hepatitis|syphilis|Zika|West Nile)",
            "using .{0,20}(method|technique|assay|panel)",
            "within \\d+\\s*(hours?|minutes?) (of|after) (collection|donation)"
        ],
        "domain": "medicine",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "procedural",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_040",
        "difficulty": "medium",
        "subcategory": "process_hallucination",
        "query": "How does Terravault encrypt data at rest in its cloud storage service?",
        "contexts": [
            "Terravault Cloud Storage is an enterprise-grade storage platform used by Fortune 500 companies for managing sensitive corporate data and compliance archives. The service provides encryption at rest and in transit, role-based access control, and comprehensive audit logging for regulatory compliance. Terravault is SOC 2 Type II and ISO 27001 certified and undergoes quarterly security reviews by independent assessors. The platform supports multi-region replication across three geographic zones and offers 99.999% durability for stored objects. Terravault's security practices undergo annual third-party penetration testing, and the results are shared with enterprise customers under NDA."
        ],
        "expected_mode": "trustworthy",
        "description": "Context confirms encryption at rest exists but never explains the specific encryption method",
        "rationale": "A model might invent specific algorithms like AES-256, key management details, or envelope encryption schemes",
        "forbidden_claims": [
            "AES[- ]?(128|256|512)",
            "(RSA|Blowfish|Twofish|ChaCha|Serpent)",
            "\\d+-bit (encryption|key)",
            "(KMS|key management|envelope encryption|HSM)",
            "keys? (are |is )?(stored|managed|rotated|generated) (in|by|every|using)"
        ],
        "domain": "law",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "procedural",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },

    # =========================================================================
    # QUOTE_FABRICATION (6 cases: 041-046)
    # =========================================================================
    {
        "id": "t1_grounding_medium_041",
        "difficulty": "medium",
        "subcategory": "quote_fabrication",
        "query": "What did the head coach say after the team's playoff loss?",
        "contexts": [
            "The Riverside Raptors were eliminated from the NASL playoffs on Saturday after a 3-1 loss to the Portland Timbers at Riverside Stadium in front of 22,000 fans. The Raptors had held a 1-0 lead at halftime before Portland scored three unanswered goals in a dominant second-half performance. Head coach Marcus Oyelaran addressed the media briefly after the match before leaving the press room visibly frustrated. The loss ends Riverside's best season in franchise history, having won 19 regular-season games and reaching the conference semifinals for the first time since the club's founding in 2018."
        ],
        "expected_mode": "trustworthy",
        "description": "Context mentions the coach addressed media but does not include any quotes",
        "rationale": "A model might fabricate a typical post-loss statement, but no actual words are quoted",
        "forbidden_claims": [
            "(he|coach|Oyelaran) (said|stated|told|remarked|commented)[,:]? ['\"]",
            "['\"][A-Z][^'\"]{10,}['\"]",
            "in his words",
            "he (expressed|conveyed|noted) that"
        ],
        "domain": "sports",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_042",
        "difficulty": "medium",
        "subcategory": "quote_fabrication",
        "query": "What did the mayor say about the proposed transit expansion?",
        "contexts": [
            "Mayor Diana Kowalski of Cincinnati held a press conference on Tuesday to discuss the proposed $2.3 billion transit expansion plan that has divided residents and council members. The plan would add 28 miles of light rail connecting the city center to northern suburbs along the I-75 corridor. City officials have been debating the proposal for over a year, with council members split along party lines on funding mechanisms. Environmental groups support the project while small business owners along the route have raised concerns about years of construction disruption. A public comment period will remain open through March 2025 at city hall and online."
        ],
        "expected_mode": "trustworthy",
        "description": "Context mentions the mayor held a press conference but never quotes her",
        "rationale": "A model might invent a supportive or diplomatic quote for the mayor, but none is provided",
        "forbidden_claims": [
            "(she|mayor|Kowalski) (said|stated|told|declared|announced)[,:]? ['\"]",
            "['\"][A-Z][^'\"]{10,}['\"]",
            "in her words",
            "she (expressed|noted|remarked) that"
        ],
        "domain": "government",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_043",
        "difficulty": "medium",
        "subcategory": "quote_fabrication",
        "query": "What did the lead researcher describe about the cancer vaccine trial results?",
        "contexts": [
            "A research team at Mount Sinai Hospital published results from an early-stage trial of a personalized mRNA cancer vaccine targeting advanced melanoma. The trial enrolled 48 patients with stage III or IV melanoma, and 36 showed measurable tumor reduction after 12 weeks of treatment with the experimental vaccine. Lead researcher Dr. Amina Chowdhury presented the findings at the American Society of Clinical Oncology conference in June 2025 to a packed auditorium. The results have generated significant excitement in the oncology community, with several pharmaceutical companies including Merck and Roche expressing interest in licensing the technology for further development."
        ],
        "expected_mode": "trustworthy",
        "description": "Context names the researcher and says she presented findings, but never quotes her",
        "rationale": "A model might fabricate an optimistic or cautious quote about the results, but none appears in the context",
        "forbidden_claims": [
            "(she|Dr\\.? Chowdhury|researcher) (said|stated|told|noted|commented)[,:]? ['\"]",
            "['\"][A-Z][^'\"]{10,}['\"]",
            "in her words",
            "she (described|called|characterized) .{0,20}as ['\"]"
        ],
        "domain": "medicine",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_044",
        "difficulty": "medium",
        "subcategory": "quote_fabrication",
        "query": "What did the CEO of TerraFirm say about the data breach?",
        "contexts": [
            "TerraFirm Inc., a real estate technology company based in San Francisco, disclosed a data breach affecting approximately 2.1 million user accounts in December 2024. The breach exposed names, email addresses, and hashed passwords, though financial data was not compromised according to the company's filing with the SEC. TerraFirm CEO Ryan Gallagher issued a public statement and the company began notifying affected users within 48 hours of discovering the breach. The company has engaged a leading cybersecurity firm to investigate the incident and has offered one year of free credit monitoring to affected users. TerraFirm's stock dropped 8% following the disclosure."
        ],
        "expected_mode": "trustworthy",
        "description": "Context says the CEO issued a statement but never includes the actual statement text",
        "rationale": "A model might invent an apology or reassurance quote, but no actual words from the CEO are provided",
        "forbidden_claims": [
            "(he|CEO|Gallagher) (said|stated|told|wrote|apologized)[,:]? ['\"]",
            "['\"][A-Z][^'\"]{10,}['\"]",
            "in his (words|statement)",
            "he (expressed|conveyed|assured) that"
        ],
        "domain": "real_estate",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_045",
        "difficulty": "medium",
        "subcategory": "quote_fabrication",
        "query": "What did the union leader say about the proposed contract changes?",
        "contexts": [
            "Negotiations between the United Steelworkers Local 1142 and Allegheny Steel Corp reached a critical phase this week as the current three-year collective bargaining agreement expires on February 28, 2025. Union president Teresa Dominguez met with company negotiators for eight hours on Monday at the company's headquarters in Pittsburgh. Key sticking points include healthcare premium sharing, overtime pay rates for weekend shifts, and safety staffing minimums in the rolling mill. The previous contract was ratified three years ago after a two-week strike that cost the company an estimated $15 million in lost production and damaged its relationship with several automaker customers."
        ],
        "expected_mode": "trustworthy",
        "description": "Context describes the negotiations and names the union president but never quotes her",
        "rationale": "A model might fabricate a defiant or conciliatory statement from the union leader, but none is given",
        "forbidden_claims": [
            "(she|Dominguez|president|leader) (said|stated|told|declared|vowed)[,:]? ['\"]",
            "['\"][A-Z][^'\"]{10,}['\"]",
            "in her words",
            "she (expressed|insisted|demanded|pledged) that"
        ],
        "domain": "hr_workplace",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_046",
        "difficulty": "medium",
        "subcategory": "quote_fabrication",
        "query": "What did the defense attorney argue during closing arguments?",
        "contexts": [
            "The trial of former Apex Financial CFO Martin Dreyfuss concluded this week after three weeks of testimony in the Southern District of New York. Dreyfuss faces charges of securities fraud and wire fraud related to an alleged scheme to inflate quarterly earnings over a period of two years. The prosecution presented evidence including internal emails and testimony from five former employees who described being pressured to misstate revenue figures. Defense attorney Patricia Nakamura delivered closing arguments on Thursday afternoon to the twelve-person jury. The jury is expected to begin deliberations on Monday, and if convicted, Dreyfuss faces up to 20 years in federal prison."
        ],
        "expected_mode": "trustworthy",
        "description": "Context mentions the defense attorney delivered closing arguments but does not quote them",
        "rationale": "A model might fabricate legal arguments or dramatic courtroom quotes, but none are provided",
        "forbidden_claims": [
            "(she|Nakamura|attorney|counsel) (said|stated|told|argued|declared)[,:]? ['\"]",
            "['\"][A-Z][^'\"]{10,}['\"]",
            "in her (words|argument|closing)",
            "she (argued|maintained|asserted|insisted) that .{10,}"
        ],
        "domain": "law",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },

    # =========================================================================
    # STATISTICAL_INFERENCE (6 cases: 047-052)
    # =========================================================================
    {
        "id": "t1_grounding_medium_047",
        "difficulty": "medium",
        "subcategory": "statistical_inference",
        "query": "Does Ironclad Fitness have a high membership renewal rate?",
        "contexts": [
            "Ironclad Fitness is a gym chain with 45 locations across the southeastern United States offering modern equipment and a variety of training programs. The company reported total revenue of $62 million in 2024, up from $54 million in 2023, driven by both new member acquisition and expansion. Ironclad offers monthly and annual membership options, personal training packages, and group fitness classes led by certified instructors. The chain has been expanding aggressively, opening 8 new locations in 2024 alone. Member satisfaction surveys consistently rate Ironclad above regional competitors on equipment quality, cleanliness, and staff friendliness."
        ],
        "expected_mode": "trustworthy",
        "description": "Context gives revenue growth and satisfaction data but no renewal rate",
        "rationale": "A model might extrapolate a renewal rate from revenue growth or satisfaction scores, but none is stated",
        "forbidden_claims": [
            "\\d+\\s*% (of )?(members?|customers?|subscribers?) (renew|retain|keep|continue)",
            "renewal rate (of|is|was|at) \\d",
            "retention rate (of|is|was|at) \\d",
            "\\d+\\s*% renewal",
            "renew(s|ed|al)? .{0,10}\\d+\\s*%"
        ],
        "domain": "sports",
        "query_type": "does",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_048",
        "difficulty": "medium",
        "subcategory": "statistical_inference",
        "query": "Is the dropout rate high for the CyberGuard bootcamp program?",
        "contexts": [
            "CyberGuard Academy is an online cybersecurity bootcamp that offers an intensive 16-week program designed for career changers. The curriculum covers network security, penetration testing, incident response, and cloud security through hands-on labs and capstone projects. CyberGuard accepts approximately 200 students per cohort and runs four cohorts per year starting in January, April, July, and October. Graduates have been hired by companies including Google, Deloitte, and CrowdStrike for entry-level security roles. The program costs $14,500, with income-share agreements available for students who qualify based on financial need. CyberGuard reports that 89% of graduates receive job offers within 90 days of completing the program."
        ],
        "expected_mode": "trustworthy",
        "description": "Context gives graduate job placement rate but never mentions the dropout rate",
        "rationale": "A model might try to infer the dropout rate from other statistics, but it is never provided",
        "forbidden_claims": [
            "\\d+\\s*% (drop out|dropout|attrition|leave|quit|fail to complete)",
            "(dropout|attrition|completion) rate (of|is|was) \\d",
            "\\d+\\s*% (of )?(students?|enrollees?|participants?) (drop|leave|quit|fail)",
            "\\d+\\s*(out of|/) \\d+\\s*(drop|leave|fail)"
        ],
        "domain": "education",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_049",
        "difficulty": "medium",
        "subcategory": "statistical_inference",
        "query": "How many bushels per acre does Heartland Grain Cooperative's wheat yield on average?",
        "contexts": [
            "Heartland Grain Cooperative is a farmer-owned cooperative in central Kansas with 340 member farms spanning over 200,000 acres of productive cropland. The cooperative handles storage, marketing, and export of wheat, corn, and sorghum grown by its member farms. In 2024, Heartland processed 12 million bushels of grain across all crop types and generated $180 million in total sales to domestic and international buyers. The cooperative recently invested $25 million in new grain storage elevators and high-efficiency drying facilities to reduce post-harvest losses. Heartland's wheat is exported primarily to Japan, Mexico, and Nigeria through Gulf Coast shipping terminals."
        ],
        "expected_mode": "trustworthy",
        "description": "Context gives total acreage and bushels processed but never specifies yield per acre for wheat specifically",
        "rationale": "A model might divide total bushels by total acres, but the total bushels include multiple crops, not just wheat",
        "forbidden_claims": [
            "\\d+\\s*bushels? per acre",
            "yield (of|is|was|averaging?) \\d",
            "\\d+\\s*(bu|bushels?)/acre",
            "averag(e|ing) \\d+\\s*bushels?",
            "produces? \\d+\\s*bushels? per"
        ],
        "domain": "agriculture",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_050",
        "difficulty": "medium",
        "subcategory": "statistical_inference",
        "query": "Does NovaTech derive most of its revenue from international markets?",
        "contexts": [
            "NovaTech Solutions is a cybersecurity company based in Tel Aviv, Israel, with additional offices in New York, London, and Singapore supporting regional sales teams. The company reported $420 million in total revenue for 2024, up 18% from the prior year. NovaTech serves clients in 35 countries and has been expanding its presence in the Asia-Pacific region with a new sales office in Tokyo opened in September 2024. The company derives revenue from software subscriptions, professional services, and managed security operations centers. Its largest contract in 2024 was a $28 million multi-year deal with a European bank for comprehensive threat monitoring services."
        ],
        "expected_mode": "trustworthy",
        "description": "Context mentions international presence and total revenue but never breaks down the percentage from international vs domestic markets",
        "rationale": "A model might estimate international revenue share from office locations and client count, but no percentage is stated",
        "forbidden_claims": [
            "\\d+\\s*% (of )?(revenue|sales|income) (from|comes? from|is from) (international|overseas|foreign)",
            "international (revenue|sales) (of|is|was|accounts? for) \\d",
            "\\d+\\s*% (international|global|overseas)",
            "\\$\\d+\\s*(million|billion) (from|in) international"
        ],
        "domain": "technology",
        "query_type": "does",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_051",
        "difficulty": "medium",
        "subcategory": "statistical_inference",
        "query": "How quickly does the Clearview County fire department typically respond to calls?",
        "contexts": [
            "Clearview County Fire Department serves a population of 185,000 across 420 square miles of rural and suburban Virginia. The department operates 12 fire stations staffed by 210 career firefighters and 150 volunteers who respond to emergencies around the clock. In 2024, the department responded to 8,400 calls including structure fires, medical emergencies, hazardous materials incidents, and vehicle accidents on rural highways. The department recently acquired three new pumper trucks and upgraded its dispatch system to GPS-enabled routing for faster unit deployment. Chief Angela Moretti has prioritized recruiting in underserved areas of the county where volunteer numbers have declined."
        ],
        "expected_mode": "trustworthy",
        "description": "Context describes the department's resources and call volume but never states response times",
        "rationale": "A model might estimate response time from geographic area and station count, but no time is given",
        "forbidden_claims": [
            "\\d+\\s*(minutes?|mins?|seconds?|secs?) (response|arrival)",
            "(response|arrival) time (of|is|was|averag) \\d",
            "(respond|arrive)(s|d|ing)? (within|in|under) \\d+\\s*(minutes?|mins?)",
            "averag(e|ing) \\d+\\s*(minutes?|mins?)"
        ],
        "domain": "government",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_052",
        "difficulty": "medium",
        "subcategory": "statistical_inference",
        "query": "Is it common for appeals to succeed at the state labor board?",
        "contexts": [
            "The state labor board received 4,200 appeals from workers in 2024 regarding workplace disputes including wrongful termination, wage theft, and workplace discrimination claims. The board employs 35 administrative law judges who hear cases at courthouses across the state through a rotating schedule. Average case resolution time is 14 months, which the board acknowledges is significantly longer than its internal target of 9 months due to rising caseloads. The board's annual budget of $18 million has remained flat for five years despite increasing case volumes. Worker advocacy groups have called for additional funding and staffing to reduce the backlog."
        ],
        "expected_mode": "trustworthy",
        "description": "Context gives case volume and resolution time but not the success rate for appellants",
        "rationale": "A model might estimate a success percentage from contextual clues, but none is provided",
        "forbidden_claims": [
            "\\d+\\s*% (of )?(appeals?|cases?|claims?) (are |were )?(successful|upheld|granted|won)",
            "success rate (of|is|was) \\d",
            "(win|success|favorable) rate (of|is|was) \\d",
            "\\d+\\s*(out of|/) \\d+\\s*(appeals?|cases?) (are |were )?(successful|upheld)"
        ],
        "domain": "law",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },

    # =========================================================================
    # CODE_HALLUCINATION (6 cases: 053-058)
    # =========================================================================
    {
        "id": "t1_grounding_medium_053",
        "difficulty": "medium",
        "subcategory": "code_hallucination",
        "query": "Which authentication method does the Forge API use?",
        "contexts": [
            "The Forge API is a RESTful service that provides programmatic access to project management data for teams of all sizes. It supports CRUD operations on projects, tasks, team members, and milestones through well-documented endpoints. The API uses JSON for request and response payloads and follows semantic versioning with backward-compatible minor releases. Rate limiting is applied at 1,000 requests per minute per API key to ensure fair usage across all clients. The Forge API documentation includes interactive examples and a sandbox environment for testing integrations before deploying to production."
        ],
        "expected_mode": "trustworthy",
        "description": "Context says authentication is required but never specifies the method",
        "rationale": "A model might guess OAuth2, API keys, or JWT, but the specific auth method is not stated",
        "forbidden_claims": [
            "(OAuth|OAuth2|OAuth 2\\.0|JWT|JSON Web Token|Bearer|Basic Auth)",
            "Authorization: (Bearer|Basic|Token)",
            "authenticate(s|d)? (using|via|with|through) \\w+",
            "(HMAC|SAML|OpenID|mTLS|certificate)"
        ],
        "domain": "technology",
        "query_type": "which",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_054",
        "difficulty": "medium",
        "subcategory": "code_hallucination",
        "query": "Which programming languages does the DataBridge SDK support?",
        "contexts": [
            "DataBridge is a data integration platform that enables companies to sync data between their SaaS applications and data warehouses in real time. The platform offers an official SDK that simplifies connecting to the DataBridge API and handles common integration patterns automatically. The SDK manages connection pooling, retry logic with exponential backoff, and automatic schema detection for source databases. DataBridge processes over 2 billion records per day for its enterprise customers across multiple industries. The company released version 3.0 of the SDK in November 2024 with improved error handling, batch processing capabilities, and support for streaming data sources."
        ],
        "expected_mode": "trustworthy",
        "description": "Context describes the SDK features but never lists supported programming languages",
        "rationale": "A model might list common languages like Python, Java, or JavaScript, but none are mentioned",
        "forbidden_claims": [
            "(Python|Java|JavaScript|TypeScript|Go|Ruby|C#|Rust|PHP|Swift|Kotlin|\\.NET|Node\\.?js)",
            "supports? (\\w+, )*(and )?\\w+ (languages?|SDKs?)",
            "available (in|for) (\\w+, )*(and )?\\w+",
            "(pip|npm|maven|nuget|gem|cargo) install"
        ],
        "domain": "technology",
        "query_type": "which",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_055",
        "difficulty": "medium",
        "subcategory": "code_hallucination",
        "query": "Which database does the Luminos analytics platform use for its backend?",
        "contexts": [
            "Luminos Analytics is a business intelligence platform designed for mid-market companies that need powerful analytics without enterprise-level complexity or cost. It ingests data from over 150 source connectors including popular CRM, ERP, and marketing automation tools. The platform provides real-time dashboards, scheduled reports, and AI-powered anomaly detection that alerts users to unusual patterns. Luminos can handle datasets up to 500 million rows with sub-second query performance thanks to its optimized data engine. The company was founded in 2019 and serves 800 customers across North America and Europe. Luminos raised $45 million in Series B funding in 2024 led by Accel Partners."
        ],
        "expected_mode": "trustworthy",
        "description": "Context describes the platform's capabilities but never names the underlying database technology",
        "rationale": "A model might guess PostgreSQL, ClickHouse, Snowflake, or another database, but none is specified",
        "forbidden_claims": [
            "(PostgreSQL|MySQL|MongoDB|Cassandra|DynamoDB|ClickHouse|Snowflake|BigQuery|Redshift|Elasticsearch)",
            "(built on|uses?|powered by|backed by|runs? on) \\w+(SQL|DB|Base|Store)",
            "database (is|backend) \\w+",
            "(columnar|document|graph|key-value|relational) (database|store)"
        ],
        "domain": "technology",
        "query_type": "which",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_056",
        "difficulty": "medium",
        "subcategory": "code_hallucination",
        "query": "Which parameters does the search endpoint accept in the Catalog API?",
        "contexts": [
            "The Catalog API provides programmatic access to a product inventory of over 3 million items across hundreds of categories for retail and wholesale partners. The API includes endpoints for browsing categories, retrieving product details, checking real-time availability across warehouses, and searching the entire catalog. Search results are paginated and can be sorted by relevance, price, or customer rating according to the caller's preference. The API returns results in JSON format and supports both GET and POST requests for search operations. Full documentation with code examples and rate limit details is available on the developer portal at docs.catalogapi.example.com."
        ],
        "expected_mode": "trustworthy",
        "description": "Context describes search behavior but never lists the specific query parameters",
        "rationale": "A model might fabricate parameter names like 'q', 'category_id', 'min_price', but none are specified",
        "forbidden_claims": [
            "(parameter|param|field|key) (name[ds]? )?['\"]\\w+['\"]",
            "\\?\\w+=",
            "(q|query|keyword|search|term|category|filter|sort|page|limit|offset)=",
            "accepts? (the )?(following )?parameters?:? (\\w+, )*\\w+"
        ],
        "domain": "technology",
        "query_type": "which",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_057",
        "difficulty": "medium",
        "subcategory": "code_hallucination",
        "query": "Which error codes does the PayStream payment API return for failed transactions?",
        "contexts": [
            "PayStream is a payment processing API used by e-commerce platforms for handling credit card transactions, refunds, and recurring subscription billing across multiple currencies. The API processes over $2 billion in monthly transaction volume and supports 25 currencies with automatic exchange rate conversion. PayStream provides detailed error responses with descriptive messages to help developers diagnose issues with failed transactions quickly. The API uses standard HTTP status codes along with custom error codes specific to payment processing scenarios. PayStream's uptime has exceeded 99.99% for the past three years, and the company maintains redundant processing centers in Virginia and Oregon."
        ],
        "expected_mode": "trustworthy",
        "description": "Context mentions the API has custom error codes but never lists any of them",
        "rationale": "A model might invent specific error codes like 'CARD_DECLINED' or numeric codes, but none are given",
        "forbidden_claims": [
            "(error |status )?(code|codes?) ['\"]?\\w+[_-]\\w+['\"]?",
            "(CARD_DECLINED|INSUFFICIENT_FUNDS|INVALID_CVV|EXPIRED_CARD|AUTHENTICATION_FAILED)",
            "returns? ['\"]?\\w+[_-]\\w+['\"]? (when|if|for)",
            "(E|ERR)[_-]?\\d{3,}"
        ],
        "domain": "finance",
        "query_type": "which",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_058",
        "difficulty": "medium",
        "subcategory": "code_hallucination",
        "query": "Is there a maximum file size limit for uploads in the CloudVault API?",
        "contexts": [
            "CloudVault is a cloud file storage and collaboration API designed for enterprise applications that need secure, reliable document management at scale. The API supports file uploads, downloads, versioning, and sharing with granular permission controls for teams and external collaborators. CloudVault integrates with major identity providers for single sign-on and supports webhooks for real-time event notifications when files are modified or shared. The platform stores over 500 petabytes of data for its customers across Fortune 500 companies and provides geographic redundancy across three data center regions in the US, EU, and Asia-Pacific. CloudVault's free tier allows developers to test all API features with generous usage limits."
        ],
        "expected_mode": "trustworthy",
        "description": "Context describes the file storage API but never states the upload size limit",
        "rationale": "A model might guess a common limit like 5 GB or 100 MB, but no size limit is mentioned",
        "forbidden_claims": [
            "\\d+\\s*(MB|GB|TB|megabytes?|gigabytes?|terabytes?)",
            "(limit|maximum|max) (of|is|at) \\d",
            "up to \\d+\\s*(MB|GB)",
            "cannot exceed \\d"
        ],
        "domain": "technology",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },

    # =========================================================================
    # TABLE_INFERENCE (5 cases: 059-063)
    # =========================================================================
    {
        "id": "t1_grounding_medium_059",
        "difficulty": "medium",
        "subcategory": "table_inference",
        "query": "How much revenue did Helios Corporation earn in Q3 of 2024?",
        "contexts": [
            "Helios Corporation reported the following quarterly revenues for fiscal year 2024: Q1 was $142 million, Q2 was $158 million, and Q4 was $189 million. The company attributed its strong fourth-quarter finish to the holiday season and new product launches in the consumer electronics division that exceeded sales projections. Full-year revenue reached $651 million, representing 14% growth over 2023 and marking the company's fifth consecutive year of double-digit revenue growth. CEO Margaret Liu expressed optimism about continued momentum heading into 2025 as the company prepares to enter new international markets."
        ],
        "expected_mode": "trustworthy",
        "description": "Context gives Q1, Q2, Q4, and full-year revenue but omits Q3 specifically",
        "rationale": "A model might calculate Q3 by subtracting (Q1+Q2+Q4) from the annual total, which is a valid inference but constitutes inventing a number not explicitly stated",
        "forbidden_claims": [
            "Q3 (revenue|was|is|of) \\$?\\d",
            "\\$\\d+\\s*million (in|for|during) Q3",
            "third quarter (revenue|was|is) \\$?\\d",
            "Q3.{0,20}\\$\\d+\\s*million"
        ],
        "domain": "finance",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_060",
        "difficulty": "medium",
        "subcategory": "table_inference",
        "query": "How many units of the Seraph phone were sold in Europe?",
        "contexts": [
            "Global sales data for the Seraph X1 smartphone in calendar year 2024: North America accounted for 3.2 million units, Asia-Pacific for 5.8 million units, and the rest of the world for 1.1 million units sold through authorized retail and online channels. Total global sales reached 12.4 million units, making the Seraph X1 the fifth best-selling smartphone of the year according to IDC data. The phone was praised by reviewers for its advanced camera system featuring a 200-megapixel sensor and its two-day battery life. Seraph Technologies plans to release the successor X2 model in June 2025 with an upgraded processor and satellite connectivity."
        ],
        "expected_mode": "trustworthy",
        "description": "Context gives regional sales for NA, APAC, and 'rest of world' plus total, but Europe is not broken out separately",
        "rationale": "A model might subtract known regions from the total to get Europe, but Europe could be embedded within any of the stated regions or 'rest of world'",
        "forbidden_claims": [
            "\\d+(\\.\\d+)?\\s*million (units? )?(in|for|across) Europe",
            "Europe(an)? (sales?|market|region) (of|was|were|accounted) .{0,10}\\d",
            "sold \\d+(\\.\\d+)?\\s*million (units? )?in Europe",
            "European (sales|units) (of|were|was|totaled?) \\d"
        ],
        "domain": "technology",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_061",
        "difficulty": "medium",
        "subcategory": "table_inference",
        "query": "What was the unemployment rate in Millfield County in March 2024?",
        "contexts": [
            "Millfield County labor statistics for 2024 show a steady improvement in employment conditions throughout the first half of the year. The unemployment rate was 4.2% in January, 4.0% in February, 3.6% in April, and 3.4% in May. The county's economy benefited significantly from the opening of two advanced manufacturing facilities in the spring that together brought over 600 new jobs to the area. The total labor force was approximately 52,000 workers as of the most recent census estimate. County labor commissioner David Park noted that the positive trend reflected broader state-level improvements in the manufacturing sector."
        ],
        "expected_mode": "trustworthy",
        "description": "Context gives unemployment rates for Jan, Feb, April, and May but skips March",
        "rationale": "A model might interpolate March between February (4.0%) and April (3.6%), but the March figure is never stated",
        "forbidden_claims": [
            "(March|Mar\\.?) .{0,15}\\d+\\.\\d+\\s*%",
            "\\d+\\.\\d+\\s*% in (March|Mar)",
            "(March|Mar\\.?) (unemployment|rate|was) .{0,10}\\d+\\.\\d+",
            "unemployment .{0,15}(March|Mar\\.?) .{0,10}\\d"
        ],
        "domain": "government",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_062",
        "difficulty": "medium",
        "subcategory": "table_inference",
        "query": "How many calories are in the grilled chicken wrap at FreshBite?",
        "contexts": [
            "FreshBite restaurant's published menu nutrition information shows calorie counts per standard serving: Caesar Salad 380 cal, Turkey Club Sandwich 520 cal, Veggie Burger 440 cal, Grilled Salmon Bowl 490 cal, and Chicken Noodle Soup 220 cal. The grilled chicken wrap is one of FreshBite's most popular menu items and is available with a choice of ranch or chipotle sauce on the side. All calorie counts listed on the menu are based on standard preparation without modifications, sauces, or additional toppings. FreshBite also offers a kids' menu with smaller portion sizes and reduced-calorie options for families dining with children."
        ],
        "expected_mode": "trustworthy",
        "description": "Context lists calories for five menu items but not for the grilled chicken wrap despite mentioning it",
        "rationale": "A model might estimate calories based on similar items or typical wrap nutrition, but the exact count is missing from the data",
        "forbidden_claims": [
            "\\d{2,}\\s*(cal(ories)?|kcal)",
            "(wrap|chicken wrap) (is|has|contains?) \\d",
            "\\d{2,}\\s*(cal(ories)?|kcal) (for|in) the (grilled )?chicken wrap",
            "approximately \\d{2,}\\s*cal"
        ],
        "domain": "food",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
    {
        "id": "t1_grounding_medium_063",
        "difficulty": "medium",
        "subcategory": "table_inference",
        "query": "How much is the median home price in the Willowbrook neighborhood?",
        "contexts": [
            "Quarterly real estate report for the city of Maplewood, 2024 Q4: Oakdale neighborhood median home price $425,000, Pinehurst $387,000, Riverside $512,000, and Cedarwood $298,000 based on closed transactions during the quarter. The Willowbrook neighborhood saw strong buyer interest this quarter due to the new elementary school completed in September and improved walkability scores from recent sidewalk construction. City-wide, the median home price rose 6% year-over-year to $402,000, driven by limited inventory and sustained demand from first-time buyers. Inventory levels remain tight across all neighborhoods with an average of 1.8 months of supply, well below the six-month threshold that indicates a balanced market."
        ],
        "expected_mode": "trustworthy",
        "description": "Context gives median prices for four neighborhoods and city-wide average but not for Willowbrook specifically",
        "rationale": "A model might estimate from the city median or surrounding neighborhoods, but the Willowbrook figure is missing",
        "forbidden_claims": [
            "\\$\\d{3,}(,\\d{3})*",
            "Willowbrook .{0,20}\\$\\d",
            "median (home )?(price|value) (in|for|of) (the )?Willowbrook .{0,10}\\$?\\d",
            "priced at \\$\\d"
        ],
        "domain": "real_estate",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
        "category": "grounding",
        "evaluation_config": {
            "mode": "answer_quality",
            "use_regex": True,
            "case_insensitive": True,
            "allowed_phrases": []
        }
    },
]


def validate_cases(cases):
    """Validate all cases before inserting."""
    errors = []
    ids_seen = set()
    required_fields = [
        "id", "difficulty", "subcategory", "query", "contexts",
        "expected_mode", "description", "rationale", "forbidden_claims",
        "domain", "query_type", "source_type", "context_count",
        "reasoning_type", "evidence_pattern", "category", "evaluation_config"
    ]

    # Distribution tracking
    domains = {}
    query_types = {}
    subcategories = {}

    for i, case in enumerate(cases):
        cid = case.get("id", f"MISSING_ID_{i}")

        # Check duplicate IDs
        if cid in ids_seen:
            errors.append(f"{cid}: Duplicate ID")
        ids_seen.add(cid)

        # Check all required fields
        for field in required_fields:
            if field not in case:
                errors.append(f"{cid}: Missing field '{field}'")

        # Check forbidden_claims count
        fc = case.get("forbidden_claims", [])
        if len(fc) < 3:
            errors.append(f"{cid}: Only {len(fc)} forbidden_claims (need >= 3)")
        if len(fc) > 6:
            errors.append(f"{cid}: {len(fc)} forbidden_claims (max 6)")

        # Check context word count
        for j, ctx in enumerate(case.get("contexts", [])):
            words = len(ctx.split())
            if words < 80:
                errors.append(f"{cid}: Context {j} has only {words} words (need >= 80)")
            if words > 150:
                errors.append(f"{cid}: Context {j} has {words} words (max 150)")

        # Check evaluation_config
        ec = case.get("evaluation_config", {})
        if ec.get("mode") != "answer_quality":
            errors.append(f"{cid}: evaluation_config.mode should be 'answer_quality'")

        # Track distributions
        domain = case.get("domain", "unknown")
        domains[domain] = domains.get(domain, 0) + 1
        qt = case.get("query_type", "unknown")
        query_types[qt] = query_types.get(qt, 0) + 1
        sc = case.get("subcategory", "unknown")
        subcategories[sc] = subcategories.get(sc, 0) + 1

    # Check domain distribution (no domain > 15% = ~8 cases)
    for domain, count in domains.items():
        pct = count / len(cases) * 100
        if pct > 16:
            errors.append(f"Domain '{domain}' has {count} cases ({pct:.1f}%) - exceeds 15%")

    # Check query_type distribution (what <= 30% = ~16 cases)
    what_count = query_types.get("what", 0)
    what_pct = what_count / len(cases) * 100
    if what_pct > 31:
        errors.append(f"'what' queries: {what_count} ({what_pct:.1f}%) - exceeds 30%")

    # Validate regex patterns compile
    for case in cases:
        for j, pattern in enumerate(case.get("forbidden_claims", [])):
            try:
                re.compile(pattern, re.IGNORECASE)
            except re.error as e:
                errors.append(f"{case['id']}: Invalid regex in forbidden_claims[{j}]: {e}")

    print(f"\n=== Validation Results ===")
    print(f"Total new cases: {len(cases)}")
    print(f"\nSubcategory distribution: {dict(sorted(subcategories.items()))}")
    print(f"Domain distribution: {dict(sorted(domains.items()))}")
    print(f"Query type distribution: {dict(sorted(query_types.items()))}")

    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print(f"\nAll validations passed!")
        return True


def main():
    # Validate new cases first
    if not validate_cases(NEW_CASES):
        print("\nAborting - fix validation errors first.")
        return

    # Load existing data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Check for ID conflicts with existing data
    existing_ids = {c["id"] for c in data["cases"]}
    new_ids = {c["id"] for c in NEW_CASES}
    conflicts = existing_ids & new_ids
    if conflicts:
        print(f"\nERROR: ID conflicts with existing data: {conflicts}")
        return

    # Find insertion point: after existing medium cases, before hard cases
    insert_idx = 0
    for i, case in enumerate(data["cases"]):
        if case["difficulty"] == "medium":
            insert_idx = i + 1

    # Insert new cases after existing medium cases
    for i, case in enumerate(NEW_CASES):
        data["cases"].insert(insert_idx + i, case)

    # Write back
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nInserted {len(NEW_CASES)} cases at index {insert_idx}")
    print(f"Total cases now: {len(data['cases'])}")

    # Final verification
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        verify = json.load(f)
    all_ids = [c["id"] for c in verify["cases"]]
    assert len(all_ids) == len(set(all_ids)), "Duplicate IDs found!"
    medium_count = sum(1 for c in verify["cases"] if c["difficulty"] == "medium")
    print(f"Medium cases: {medium_count}")
    print(f"Hard cases: {sum(1 for c in verify['cases'] if c['difficulty'] == 'hard')}")


if __name__ == "__main__":
    main()
