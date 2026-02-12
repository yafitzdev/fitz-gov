"""
Generate 30 multi-source trustworthy test cases for fitz-gov benchmark.

15 trustworthy_direct (cross_source_agreement): Multiple independent sources agree.
15 trustworthy_hedged (cross_source_partial): Multiple sources provide partial/complementary info.

Output: scripts/new_trustworthy_multisource.json
"""

import json
import os


def build_direct_cases():
    """15 trustworthy_direct cases with cross_source_agreement subcategory."""
    cases = []

    # --- SCIENCE (3 cases) ---

    cases.append({
        "id": "t1_confident_hard_901",
        "difficulty": "hard",
        "subcategory": "cross_source_agreement",
        "query": "What is the speed of light in a vacuum?",
        "contexts": [
            "The speed of light in a vacuum is exactly 299,792,458 meters per second. This value was fixed by the 17th General Conference on Weights and Measures in 1983 as part of the redefinition of the metre.",
            "NIST defines the speed of light c as 299,792,458 m/s exactly, a fundamental physical constant used in the International System of Units to define the metre.",
            "According to the CRC Handbook of Chemistry and Physics (104th edition), the speed of electromagnetic radiation in vacuum is 299,792,458 m/s, consistent with the SI definition."
        ],
        "context_sources": [
            {"source_id": "physics_textbook_2024", "source_type": "academic", "authority": "primary"},
            {"source_id": "nist_constants_db", "source_type": "government", "authority": "official"},
            {"source_id": "crc_handbook_104", "source_type": "reference", "authority": "primary"}
        ],
        "expected_mode": "trustworthy",
        "description": "Fundamental physical constant confirmed by three independent authoritative sources.",
        "rationale": "All three sources -- academic textbook, government standards body, and reference handbook -- independently confirm the exact same value, providing high confidence."
    })

    cases.append({
        "id": "t1_confident_hard_902",
        "difficulty": "hard",
        "subcategory": "cross_source_agreement",
        "query": "What causes ocean tides on Earth?",
        "contexts": [
            "Ocean tides are primarily caused by the gravitational pull of the Moon on Earth's oceans, with a smaller contribution from the Sun. The Moon's gravity creates two tidal bulges: one on the side facing the Moon and one on the opposite side due to inertial effects.",
            "NASA's Ocean Surface Topography mission confirms that lunar gravitational forces account for approximately 68% of tidal forces on Earth, while solar gravitational forces contribute about 32%. The interplay produces spring tides (aligned) and neap tides (perpendicular)."
        ],
        "context_sources": [
            {"source_id": "oceanography_intro_2023", "source_type": "academic", "authority": "primary"},
            {"source_id": "nasa_ocean_topography", "source_type": "government", "authority": "official"}
        ],
        "expected_mode": "trustworthy",
        "description": "Tidal mechanics explained consistently by academic and government sources.",
        "rationale": "Both an oceanography textbook and NASA mission data converge on the same explanation of tidal forces, with consistent percentage contributions from Moon and Sun."
    })

    cases.append({
        "id": "t1_confident_hard_903",
        "difficulty": "hard",
        "subcategory": "cross_source_agreement",
        "query": "What is the half-life of carbon-14?",
        "contexts": [
            "The half-life of carbon-14 is 5,730 plus or minus 40 years, as determined by Godwin (1962). This value, sometimes called the Cambridge half-life, is the internationally accepted standard used in radiocarbon dating calibration.",
            "The International Atomic Energy Agency lists the half-life of C-14 as 5,730 years. This isotope decays via beta emission to nitrogen-14 and is the basis for radiocarbon dating of organic materials up to approximately 50,000 years old.",
            "The NUBASE2020 evaluated nuclear data tables report the carbon-14 half-life as 5,700 plus or minus 30 years, consistent within measurement uncertainty with the Godwin value of 5,730 years used in practice."
        ],
        "context_sources": [
            {"source_id": "radiochemistry_text_2022", "source_type": "academic", "authority": "primary"},
            {"source_id": "iaea_nuclear_data", "source_type": "government", "authority": "official"},
            {"source_id": "nubase2020_tables", "source_type": "reference", "authority": "primary"}
        ],
        "expected_mode": "trustworthy",
        "description": "Carbon-14 half-life confirmed by three independent nuclear science sources.",
        "rationale": "Academic, governmental, and reference sources all agree on the C-14 half-life value within measurement uncertainty, providing strong cross-source confirmation."
    })

    # --- FINANCE (3 cases) ---

    cases.append({
        "id": "t1_confident_hard_904",
        "difficulty": "hard",
        "subcategory": "cross_source_agreement",
        "query": "What is the current federal funds rate target range?",
        "contexts": [
            "The Federal Open Market Committee voted unanimously on January 29, 2025 to maintain the federal funds rate target range at 4.25 to 4.50 percent, citing solid economic activity and an elevated but stabilizing inflation rate.",
            "Bloomberg Terminal data as of February 2025 shows the effective federal funds rate at 4.33%, within the Fed's target range of 4.25-4.50% set at the January 2025 FOMC meeting.",
            "The Wall Street Journal's Fed Tracker reports the current federal funds target range is 4.25%-4.50%, unchanged since the January 2025 meeting, with markets pricing in no change at the March meeting."
        ],
        "context_sources": [
            {"source_id": "fomc_statement_jan2025", "source_type": "government", "authority": "official"},
            {"source_id": "bloomberg_rates_feb2025", "source_type": "industry", "authority": "primary"},
            {"source_id": "wsj_fed_tracker", "source_type": "news", "authority": "secondary"}
        ],
        "expected_mode": "trustworthy",
        "description": "Federal funds rate confirmed by official statement, market data, and financial media.",
        "rationale": "The FOMC's own statement, real-time market data, and financial journalism all report the same target range, with the effective rate falling within that range as expected."
    })

    cases.append({
        "id": "t1_confident_hard_905",
        "difficulty": "hard",
        "subcategory": "cross_source_agreement",
        "query": "What is the standard vesting schedule for employee stock options at US tech companies?",
        "contexts": [
            "According to the NASPP (National Association of Stock Plan Professionals) 2024 Domestic Stock Plan Design Survey, 72% of US technology companies use a four-year vesting schedule with a one-year cliff, where 25% vests after the first year and the remainder vests monthly or quarterly over the following three years.",
            "Carta's 2024 Equity Benchmarking Report, based on data from over 40,000 companies on their platform, confirms the four-year vest with one-year cliff as the dominant structure, used by 69% of technology companies, with the monthly vesting cadence being twice as common as quarterly."
        ],
        "context_sources": [
            {"source_id": "naspp_survey_2024", "source_type": "industry", "authority": "primary"},
            {"source_id": "carta_equity_report_2024", "source_type": "industry", "authority": "primary"}
        ],
        "expected_mode": "trustworthy",
        "description": "Standard vesting schedule confirmed by two independent industry surveys.",
        "rationale": "Two large-scale independent industry surveys agree on the four-year/one-year-cliff structure as dominant, with closely aligned percentages (72% vs 69%)."
    })

    cases.append({
        "id": "t1_confident_hard_906",
        "difficulty": "hard",
        "subcategory": "cross_source_agreement",
        "query": "What are the FDIC deposit insurance limits for individual bank accounts?",
        "contexts": [
            "The FDIC insures deposits at member institutions up to $250,000 per depositor, per insured bank, for each account ownership category. This limit has been in effect since October 2008 when the Emergency Economic Stabilization Act permanently raised it from $100,000.",
            "The Consumer Financial Protection Bureau states that FDIC insurance covers up to $250,000 per person, per bank, per ownership category. Joint accounts are insured up to $250,000 per co-owner, effectively providing $500,000 of coverage for a two-person joint account."
        ],
        "context_sources": [
            {"source_id": "fdic_deposit_insurance_faq", "source_type": "government", "authority": "official"},
            {"source_id": "cfpb_consumer_guide", "source_type": "government", "authority": "official"}
        ],
        "expected_mode": "trustworthy",
        "description": "FDIC insurance limits confirmed by two federal agencies.",
        "rationale": "Both FDIC itself and the CFPB independently state the same $250,000 limit with consistent details about ownership categories, providing authoritative cross-government agreement."
    })

    # --- TECH (3 cases) ---

    cases.append({
        "id": "t1_confident_hard_907",
        "difficulty": "hard",
        "subcategory": "cross_source_agreement",
        "query": "What is the maximum payload size for an AWS Lambda function invocation?",
        "contexts": [
            "AWS Lambda supports synchronous invocation payloads up to 6 MB and asynchronous invocation payloads up to 256 KB. Response payloads for synchronous invocations are also limited to 6 MB. These limits apply to the request and response body after Base64 encoding.",
            "The AWS Well-Architected Framework's serverless lens notes that Lambda's 6 MB synchronous payload limit means architectures handling larger data should use S3 pre-signed URLs or Step Functions with the S3 integration pattern rather than passing data directly through invocations."
        ],
        "context_sources": [
            {"source_id": "aws_lambda_docs_2024", "source_type": "reference", "authority": "official"},
            {"source_id": "aws_well_architected_serverless", "source_type": "reference", "authority": "primary"}
        ],
        "expected_mode": "trustworthy",
        "description": "Lambda payload limits confirmed by official docs and architectural guidance.",
        "rationale": "AWS's own documentation and their architectural best-practices framework both cite the same 6 MB synchronous payload limit, with the latter providing workaround patterns."
    })

    cases.append({
        "id": "t1_confident_hard_908",
        "difficulty": "hard",
        "subcategory": "cross_source_agreement",
        "query": "What hashing algorithm does Git use for object identification?",
        "contexts": [
            "Git identifies all objects (commits, trees, blobs, tags) using SHA-1 hashes, producing a 40-character hexadecimal string. As of Git 2.42, experimental support for SHA-256 has been added through the --object-format=sha256 flag at repository initialization.",
            "The Git internals chapter of Pro Git (2nd edition) explains that Git stores all content in its object database keyed by SHA-1 hashes. Each object is identified by a 160-bit hash computed over a header plus the object content.",
            "GitHub's engineering blog post on hash migration (2023) confirms that Git's default object format remains SHA-1, while the transition to SHA-256 is underway with interoperability support being developed through hash translation tables."
        ],
        "context_sources": [
            {"source_id": "git_scm_docs_v2_42", "source_type": "reference", "authority": "official"},
            {"source_id": "pro_git_2nd_ed", "source_type": "academic", "authority": "primary"},
            {"source_id": "github_eng_blog_2023", "source_type": "blog", "authority": "expert"}
        ],
        "expected_mode": "trustworthy",
        "description": "Git's hashing mechanism confirmed by official docs, reference book, and platform engineering team.",
        "rationale": "Three independent sources -- official Git documentation, the canonical Git reference book, and GitHub's engineering team -- all agree on SHA-1 as the default with SHA-256 transition in progress."
    })

    cases.append({
        "id": "t1_confident_hard_909",
        "difficulty": "hard",
        "subcategory": "cross_source_agreement",
        "query": "What is the default isolation level in PostgreSQL?",
        "contexts": [
            "PostgreSQL uses Read Committed as its default transaction isolation level. In this mode, each statement within a transaction sees a snapshot of the database as of the start of that statement, meaning concurrent committed changes become visible between statements.",
            "The PostgreSQL 16 release notes and documentation confirm Read Committed as the default isolation level. This can be changed per-transaction with SET TRANSACTION ISOLATION LEVEL or globally via the default_transaction_isolation configuration parameter."
        ],
        "context_sources": [
            {"source_id": "pg_docs_isolation_levels", "source_type": "reference", "authority": "official"},
            {"source_id": "pg16_release_docs", "source_type": "reference", "authority": "official"}
        ],
        "expected_mode": "trustworthy",
        "description": "PostgreSQL default isolation level confirmed by core documentation and release notes.",
        "rationale": "Two sections of PostgreSQL's own official documentation independently state Read Committed as the default, with consistent behavioral descriptions."
    })

    # --- HEALTH (3 cases) ---

    cases.append({
        "id": "t1_confident_hard_910",
        "difficulty": "hard",
        "subcategory": "cross_source_agreement",
        "query": "What is the recommended daily sodium intake for adults?",
        "contexts": [
            "The American Heart Association recommends no more than 2,300 milligrams of sodium per day for adults, with an ideal limit of 1,500 mg per day for most adults, especially those with high blood pressure.",
            "The WHO guideline on sodium intake for adults (2023 update) recommends reducing sodium intake to less than 2,000 mg/day (equivalent to less than 5 g/day of salt) for adults to reduce blood pressure and risk of cardiovascular disease.",
            "The Dietary Guidelines for Americans 2020-2025, published jointly by USDA and HHS, state that adults should consume less than 2,300 mg of sodium per day as part of a healthy eating pattern."
        ],
        "context_sources": [
            {"source_id": "aha_sodium_guidelines", "source_type": "industry", "authority": "expert"},
            {"source_id": "who_sodium_guideline_2023", "source_type": "government", "authority": "official"},
            {"source_id": "dga_2020_2025", "source_type": "government", "authority": "official"}
        ],
        "expected_mode": "trustworthy",
        "description": "Sodium intake recommendations confirmed by three major health authorities.",
        "rationale": "The AHA, WHO, and US Dietary Guidelines all converge on roughly 2,000-2,300 mg/day as the upper limit, providing strong multi-authority agreement on the recommendation."
    })

    cases.append({
        "id": "t1_confident_hard_911",
        "difficulty": "hard",
        "subcategory": "cross_source_agreement",
        "query": "How long does immunity from an mRNA COVID-19 booster typically last?",
        "contexts": [
            "A study published in The Lancet Infectious Diseases (2024) found that protection against symptomatic infection from an updated mRNA booster wanes to approximately 50% effectiveness by 4 to 6 months post-vaccination, while protection against severe disease and hospitalization remains above 70% at 6 months.",
            "CDC's MMWR report from October 2024 found that the updated 2024-2025 COVID-19 vaccine provided 54% effectiveness against symptomatic infection at 2 months, declining to approximately 35% at 5 months, with hospitalization protection remaining at 65-75% through 6 months of follow-up."
        ],
        "context_sources": [
            {"source_id": "lancet_id_booster_2024", "source_type": "academic", "authority": "primary"},
            {"source_id": "cdc_mmwr_oct2024", "source_type": "government", "authority": "official"}
        ],
        "expected_mode": "trustworthy",
        "description": "COVID booster duration confirmed by peer-reviewed study and CDC surveillance data.",
        "rationale": "Both a peer-reviewed journal study and CDC surveillance data independently find waning symptomatic protection by 4-6 months but durable hospitalization protection, showing consistent patterns across sources."
    })

    cases.append({
        "id": "t1_confident_hard_912",
        "difficulty": "hard",
        "subcategory": "cross_source_agreement",
        "query": "What is the normal resting heart rate range for adults?",
        "contexts": [
            "The American College of Cardiology defines a normal resting heart rate for adults as between 60 and 100 beats per minute, measured while sitting quietly for at least 5 minutes. Well-trained athletes may have resting rates as low as 40 bpm.",
            "Mayo Clinic's patient reference states that a normal resting heart rate for adults ranges from 60 to 100 beats per minute. A lower resting heart rate generally implies more efficient heart function and better cardiovascular fitness.",
            "Harrison's Principles of Internal Medicine (21st edition) defines normal sinus rhythm at rest as 60-100 bpm in adults, with bradycardia defined as below 60 bpm and tachycardia as above 100 bpm at rest."
        ],
        "context_sources": [
            {"source_id": "acc_clinical_guidelines", "source_type": "industry", "authority": "expert"},
            {"source_id": "mayo_clinic_reference", "source_type": "reference", "authority": "expert"},
            {"source_id": "harrisons_21st_ed", "source_type": "academic", "authority": "primary"}
        ],
        "expected_mode": "trustworthy",
        "description": "Normal resting heart rate confirmed by cardiology guidelines, clinical reference, and medical textbook.",
        "rationale": "Three independent medical sources -- professional cardiology guidelines, a leading clinical reference, and a standard medical textbook -- all agree on the 60-100 bpm range."
    })

    # --- LAW (3 cases) ---

    cases.append({
        "id": "t1_confident_hard_913",
        "difficulty": "hard",
        "subcategory": "cross_source_agreement",
        "query": "What is the statute of limitations for filing a federal employment discrimination claim with the EEOC?",
        "contexts": [
            "Under Title VII of the Civil Rights Act, employees must file a charge of discrimination with the EEOC within 180 days of the alleged discriminatory act. This deadline extends to 300 days if a state or local agency enforces a law prohibiting employment discrimination on the same basis.",
            "The EEOC's own filing guide states: 'You have 180 days from the day the discrimination took place to file a charge. The deadline is extended to 300 days if a state or local agency enforces a state or local law that prohibits employment discrimination on the same basis.'",
            "The ABA's Guide to Workplace Law (2024 edition) confirms the 180/300-day filing window for EEOC charges, noting that the 300-day extension applies in the 46 states that have their own fair employment practices agencies."
        ],
        "context_sources": [
            {"source_id": "title_vii_statute_text", "source_type": "government", "authority": "official"},
            {"source_id": "eeoc_filing_guide", "source_type": "government", "authority": "official"},
            {"source_id": "aba_workplace_law_2024", "source_type": "academic", "authority": "primary"}
        ],
        "expected_mode": "trustworthy",
        "description": "EEOC filing deadline confirmed by statute, agency guidance, and legal reference.",
        "rationale": "The statutory text, the EEOC's own guidance, and a legal reference all agree on the 180/300-day framework, with each providing the same distinction about state agency extensions."
    })

    cases.append({
        "id": "t1_confident_hard_914",
        "difficulty": "hard",
        "subcategory": "cross_source_agreement",
        "query": "What are the Miranda warning requirements during a custodial interrogation?",
        "contexts": [
            "Miranda v. Arizona, 384 U.S. 436 (1966), established that prior to custodial interrogation, law enforcement must inform suspects of their right to remain silent, that anything said can be used against them in court, the right to an attorney, and the right to have an attorney appointed if they cannot afford one.",
            "The Department of Justice Law Enforcement Policy Manual requires agents to administer Miranda warnings before any custodial interrogation, covering four rights: silence, use of statements as evidence, right to counsel, and right to appointed counsel for indigent suspects."
        ],
        "context_sources": [
            {"source_id": "miranda_v_arizona_384us436", "source_type": "government", "authority": "official"},
            {"source_id": "doj_le_policy_manual", "source_type": "government", "authority": "official"}
        ],
        "expected_mode": "trustworthy",
        "description": "Miranda requirements confirmed by Supreme Court ruling and DOJ policy.",
        "rationale": "The original Supreme Court decision and current DOJ enforcement policy both enumerate the same four required warnings, providing authoritative legal agreement."
    })

    cases.append({
        "id": "t1_confident_hard_915",
        "difficulty": "hard",
        "subcategory": "cross_source_agreement",
        "query": "What is the legal blood alcohol concentration limit for driving in the United States?",
        "contexts": [
            "All 50 US states and the District of Columbia have set 0.08% blood alcohol concentration (BAC) as the per se legal limit for driving under the influence for drivers aged 21 and over. Utah was the last state to adopt this limit, lowering it from 0.08% to 0.05% in December 2018, making it the only state with a stricter standard.",
            "The National Highway Traffic Safety Administration reports that the nationwide 0.08% BAC legal limit for adult drivers was effectively established when the final holdout states adopted the standard by 2005, following the federal incentive program under the Department of Transportation Appropriations Act of 2001.",
            "The Insurance Institute for Highway Safety's DUI/DWI laws database confirms that all states use 0.08% BAC as the per se limit for drivers 21 and over, with the exception of Utah at 0.05%. Lower limits of 0.00-0.02% apply to drivers under 21 in all states under zero-tolerance laws."
        ],
        "context_sources": [
            {"source_id": "ncsl_dui_laws_2024", "source_type": "government", "authority": "official"},
            {"source_id": "nhtsa_impaired_driving", "source_type": "government", "authority": "official"},
            {"source_id": "iihs_dui_database", "source_type": "industry", "authority": "primary"}
        ],
        "expected_mode": "trustworthy",
        "description": "BAC legal limit confirmed by legislative tracker, federal highway safety agency, and insurance research institute.",
        "rationale": "Three independent sources -- a state legislative database, a federal safety agency, and an industry research body -- all confirm the 0.08% standard with consistent details about the Utah exception."
    })

    return cases


def build_hedged_cases():
    """15 trustworthy_hedged cases with cross_source_partial subcategory."""
    cases = []

    # --- SCIENCE (3 cases) ---

    cases.append({
        "id": "t1_qualify_hard_915",
        "difficulty": "hard",
        "subcategory": "cross_source_partial",
        "query": "How effective is carbon capture and storage technology at reducing atmospheric CO2?",
        "contexts": [
            "The Global CCS Institute's 2024 status report documents 41 operational carbon capture facilities worldwide with a combined capacity of 49 million tonnes of CO2 per year, representing about 0.1% of global annual emissions of approximately 37 billion tonnes.",
            "A Nature Energy study (2024) found that the energy penalty for post-combustion carbon capture ranges from 15-30% of a power plant's output, meaning a significant portion of generated energy is consumed by the capture process itself.",
            "The IEA's Net Zero by 2050 roadmap projects that CCS must scale to 7.6 billion tonnes per year by 2050 to meet climate targets, a 155-fold increase from current capacity, requiring an estimated $655 billion in cumulative investment."
        ],
        "context_sources": [
            {"source_id": "global_ccs_status_2024", "source_type": "industry", "authority": "primary"},
            {"source_id": "nature_energy_ccs_2024", "source_type": "academic", "authority": "primary"},
            {"source_id": "iea_netzero_2050", "source_type": "government", "authority": "official"}
        ],
        "expected_mode": "trustworthy",
        "description": "CCS effectiveness addressed from capacity, efficiency, and scaling perspectives by different sources.",
        "rationale": "Each source covers a different dimension -- current capacity, energy cost, and future scaling needs -- so the answer should hedge by noting CCS works but faces enormous scaling, efficiency, and investment challenges."
    })

    cases.append({
        "id": "t1_qualify_hard_916",
        "difficulty": "hard",
        "subcategory": "cross_source_partial",
        "query": "Is microplastic contamination in drinking water harmful to human health?",
        "contexts": [
            "A WHO report on microplastics in drinking water (2022) concluded that microplastics larger than 150 micrometers are unlikely to be absorbed by the human body, but acknowledged significant data gaps for particles smaller than 10 micrometers and nanoplastics.",
            "Research published in Environmental Science & Technology (2024) detected microplastic particles in human blood samples from 77% of tested individuals, with PET and polystyrene being the most common polymers found, though the health implications of blood-borne microplastics remain unclear.",
            "A Lancet Planetary Health systematic review (2024) found that occupational exposure to high concentrations of microplastics is associated with respiratory inflammation, but evidence for health effects from typical dietary exposure levels is limited and inconsistent."
        ],
        "context_sources": [
            {"source_id": "who_microplastics_2022", "source_type": "government", "authority": "official"},
            {"source_id": "est_blood_microplastics_2024", "source_type": "academic", "authority": "primary"},
            {"source_id": "lancet_ph_review_2024", "source_type": "academic", "authority": "primary"}
        ],
        "expected_mode": "trustworthy",
        "description": "Microplastic health effects addressed from exposure, bioaccumulation, and epidemiological perspectives.",
        "rationale": "Sources cover different facets -- absorption likelihood, presence in blood, and health outcomes -- but none definitively links typical exposure to harm, requiring hedged synthesis across all three dimensions."
    })

    cases.append({
        "id": "t1_qualify_hard_917",
        "difficulty": "hard",
        "subcategory": "cross_source_partial",
        "query": "Can nuclear fusion become a practical energy source within the next two decades?",
        "contexts": [
            "The National Ignition Facility at Lawrence Livermore achieved fusion ignition in December 2022, producing 3.15 MJ of energy from 2.05 MJ of laser input. However, the total electrical energy consumed by the laser system was approximately 300 MJ, meaning net energy gain relative to wall-plug electricity was not achieved.",
            "The ITER project, the world's largest fusion experiment under construction in France, is now expected to achieve first plasma no earlier than 2034, with full deuterium-tritium operations pushed to 2039, according to the revised timeline approved by the ITER Council in 2024.",
            "Commonwealth Fusion Systems reported in 2024 that their high-temperature superconducting magnet technology achieved a record 20-tesla field strength, enabling a more compact tokamak design. Their SPARC reactor aims to demonstrate net energy by 2028, with a commercial pilot plant (ARC) targeted for the early 2030s."
        ],
        "context_sources": [
            {"source_id": "llnl_nif_results_2023", "source_type": "government", "authority": "official"},
            {"source_id": "iter_council_update_2024", "source_type": "government", "authority": "official"},
            {"source_id": "cfs_progress_report_2024", "source_type": "industry", "authority": "primary"}
        ],
        "expected_mode": "trustworthy",
        "description": "Fusion energy feasibility addressed from proof-of-concept, major project timeline, and private sector perspectives.",
        "rationale": "Each source covers a different aspect -- scientific proof-of-concept, international project delays, and private sector optimism -- requiring a hedged answer acknowledging both progress and substantial remaining challenges."
    })

    # --- HEALTH (3 cases) ---

    cases.append({
        "id": "t1_qualify_hard_918",
        "difficulty": "hard",
        "subcategory": "cross_source_partial",
        "query": "Is intermittent fasting more effective than traditional calorie restriction for weight loss?",
        "contexts": [
            "A New England Journal of Medicine review (2024) of 27 randomized controlled trials found that intermittent fasting (16:8 and 5:2 protocols) produced weight loss comparable to continuous calorie restriction over 12-month periods, with mean differences of less than 1 kg between groups.",
            "An Obesity Reviews meta-analysis (2024) reported that intermittent fasting showed superior adherence rates (71% vs 58%) compared to daily calorie restriction over 6 months, potentially making it more effective in real-world settings despite similar physiological outcomes.",
            "The American College of Endocrinology's 2024 clinical practice guidelines note that intermittent fasting may carry additional risks for patients with diabetes or on certain medications, and that long-term metabolic effects beyond 2 years are poorly studied."
        ],
        "context_sources": [
            {"source_id": "nejm_if_review_2024", "source_type": "academic", "authority": "primary"},
            {"source_id": "obesity_reviews_meta_2024", "source_type": "academic", "authority": "primary"},
            {"source_id": "ace_guidelines_2024", "source_type": "industry", "authority": "expert"}
        ],
        "expected_mode": "trustworthy",
        "description": "Intermittent fasting efficacy addressed from clinical outcomes, adherence, and safety perspectives.",
        "rationale": "Sources provide complementary views -- similar weight loss outcomes, better adherence, but safety concerns -- requiring hedged synthesis that acknowledges all three dimensions."
    })

    cases.append({
        "id": "t1_qualify_hard_919",
        "difficulty": "hard",
        "subcategory": "cross_source_partial",
        "query": "Does regular coffee consumption reduce the risk of type 2 diabetes?",
        "contexts": [
            "A Diabetes Care meta-analysis (2024) pooling 30 prospective cohort studies with over 1.2 million participants found that each additional cup of coffee per day was associated with a 6% lower risk of type 2 diabetes (RR 0.94, 95% CI 0.93-0.96), with effects observed for both caffeinated and decaffeinated coffee.",
            "Research published in Cell Metabolism (2023) identified chlorogenic acid and trigonelline as the coffee compounds most likely responsible for improved glucose metabolism, showing they enhance GLP-1 secretion and improve insulin sensitivity in laboratory models.",
            "The European Food Safety Authority's scientific opinion on caffeine notes that caffeine intake above 400 mg/day (approximately 4-5 cups of coffee) is associated with increased anxiety, sleep disruption, and elevated blood pressure, effects that could indirectly worsen metabolic health."
        ],
        "context_sources": [
            {"source_id": "diabetes_care_meta_2024", "source_type": "academic", "authority": "primary"},
            {"source_id": "cell_metabolism_coffee_2023", "source_type": "academic", "authority": "primary"},
            {"source_id": "efsa_caffeine_opinion", "source_type": "government", "authority": "official"}
        ],
        "expected_mode": "trustworthy",
        "description": "Coffee-diabetes relationship addressed from epidemiology, mechanism, and safety perspectives.",
        "rationale": "Sources cover different facets -- epidemiological association, biological mechanism, and upper intake risks -- requiring a hedged answer that notes the positive association while acknowledging dose-dependent concerns."
    })

    cases.append({
        "id": "t1_qualify_hard_920",
        "difficulty": "hard",
        "subcategory": "cross_source_partial",
        "query": "Are standing desks significantly better for health than sitting desks?",
        "contexts": [
            "A British Journal of Sports Medicine systematic review (2024) found that standing desk users stood an average of 1.2 additional hours per day and reported reduced lower back pain, but found no significant difference in cardiovascular biomarkers or all-cause mortality compared to seated desk users.",
            "Ergonomics research from Cornell University found that prolonged standing (more than 2 hours continuously) increases the risk of varicose veins, lower limb swelling, and musculoskeletal discomfort, recommending a sit-stand ratio of approximately 1:1 to 2:1 sitting-to-standing.",
            "An occupational health survey by the Society for Human Resource Management (2024) found that 67% of standing desk users reported improved energy and alertness, but 41% abandoned regular use within 6 months due to foot pain or fatigue."
        ],
        "context_sources": [
            {"source_id": "bjsm_standing_review_2024", "source_type": "academic", "authority": "primary"},
            {"source_id": "cornell_ergonomics_lab", "source_type": "academic", "authority": "primary"},
            {"source_id": "shrm_workplace_survey_2024", "source_type": "industry", "authority": "secondary"}
        ],
        "expected_mode": "trustworthy",
        "description": "Standing desk health benefits addressed from clinical evidence, ergonomic research, and workplace adoption perspectives.",
        "rationale": "Sources cover different angles -- limited clinical benefit, ergonomic risks of overuse, and mixed real-world adoption -- requiring hedged conclusions about the nuanced trade-offs."
    })

    # --- FINANCE (3 cases) ---

    cases.append({
        "id": "t1_qualify_hard_921",
        "difficulty": "hard",
        "subcategory": "cross_source_partial",
        "query": "Is investing in index funds always better than actively managed funds?",
        "contexts": [
            "The S&P Indices Versus Active (SPIVA) scorecard for 2024 shows that over a 15-year period, 92% of large-cap US actively managed funds underperformed the S&P 500 index after fees, consistent with the long-term trend observed since SPIVA tracking began in 2002.",
            "Morningstar's Active/Passive Barometer (2024) found that in certain niche categories -- emerging market small-cap, high-yield bonds, and real estate -- actively managed funds outperformed their passive benchmarks more than 60% of the time over the past decade.",
            "A Journal of Finance study (2024) found that factor-adjusted returns of the top decile of active managers showed persistent skill, outperforming by an average of 1.2% annually after fees, but that identifying these managers in advance remains statistically difficult for retail investors."
        ],
        "context_sources": [
            {"source_id": "spiva_scorecard_2024", "source_type": "industry", "authority": "primary"},
            {"source_id": "morningstar_barometer_2024", "source_type": "industry", "authority": "primary"},
            {"source_id": "jof_active_mgmt_2024", "source_type": "academic", "authority": "primary"}
        ],
        "expected_mode": "trustworthy",
        "description": "Index vs active investing addressed from broad performance data, niche category exceptions, and manager skill research.",
        "rationale": "Sources reveal different facets: index funds win broadly, but exceptions exist in niche categories, and some skilled managers outperform -- requiring a hedged answer acknowledging the general rule and its exceptions."
    })

    cases.append({
        "id": "t1_qualify_hard_922",
        "difficulty": "hard",
        "subcategory": "cross_source_partial",
        "query": "Is real estate still a good inflation hedge?",
        "contexts": [
            "A National Bureau of Economic Research working paper (2024) analyzed US real estate returns from 1890-2023 and found that residential real estate appreciated at an average real rate of 1.1% annually, outpacing inflation but with significant regional variation -- some markets lost real value over 30-year periods.",
            "The Federal Reserve Bank of Dallas's 2024 housing analysis found that during the 2021-2023 inflation surge, home prices initially outpaced inflation by 15 percentage points but subsequently corrected as mortgage rates rose above 7%, eroding real returns for leveraged buyers.",
            "CBRE's Global Real Estate Outlook (2024) reports that commercial real estate with inflation-linked lease escalations provided a more reliable inflation hedge than residential property, with industrial and logistics assets delivering real returns of 3-5% annually over the past decade."
        ],
        "context_sources": [
            {"source_id": "nber_wp_housing_2024", "source_type": "academic", "authority": "primary"},
            {"source_id": "dallas_fed_housing_2024", "source_type": "government", "authority": "official"},
            {"source_id": "cbre_outlook_2024", "source_type": "industry", "authority": "primary"}
        ],
        "expected_mode": "trustworthy",
        "description": "Real estate as inflation hedge addressed from long-term historical, recent cycle, and commercial segment perspectives.",
        "rationale": "Each source covers a different dimension -- long-term with caveats, recent-cycle dynamics, and sector-specific differences -- requiring hedged conclusions about when and how real estate hedges inflation."
    })

    cases.append({
        "id": "t1_qualify_hard_923",
        "difficulty": "hard",
        "subcategory": "cross_source_partial",
        "query": "Should retirees follow the 4% withdrawal rule for their investment portfolios?",
        "contexts": [
            "The original Trinity Study (updated through 2023 data by Cooley, Hubbard, and Walz) found that a 4% initial withdrawal rate, adjusted annually for inflation, sustained a 60/40 stock/bond portfolio for 30 years in 96% of historical rolling periods since 1926.",
            "A Journal of Financial Planning study (2024) argued that current low bond yields and elevated equity valuations reduce the safe withdrawal rate to 3.3% for new retirees, based on Monte Carlo simulations using forward-looking return assumptions rather than historical averages.",
            "The Stanford Center on Longevity's Sightlines report notes that increasing life expectancies mean many retirees now need portfolios to last 35-40 years rather than 30, which lowers the historically safe withdrawal rate by an estimated 0.5-1.0 percentage points."
        ],
        "context_sources": [
            {"source_id": "trinity_study_update_2023", "source_type": "academic", "authority": "primary"},
            {"source_id": "jfp_withdrawal_2024", "source_type": "academic", "authority": "primary"},
            {"source_id": "stanford_longevity_2024", "source_type": "academic", "authority": "primary"}
        ],
        "expected_mode": "trustworthy",
        "description": "4% rule validity addressed from historical backtesting, current market conditions, and longevity perspectives.",
        "rationale": "Sources provide complementary analyses -- historical success, forward-looking caution, and longevity considerations -- each adjusting the conclusion in different ways, requiring a hedged synthesis."
    })

    # --- TECH (3 cases) ---

    cases.append({
        "id": "t1_qualify_hard_924",
        "difficulty": "hard",
        "subcategory": "cross_source_partial",
        "query": "Is serverless architecture more cost-effective than traditional server-based deployment?",
        "contexts": [
            "An AWS case study compilation (2024) found that organizations migrating event-driven workloads to Lambda reduced infrastructure costs by 40-70% compared to EC2 instances, with the largest savings for applications with variable or bursty traffic patterns.",
            "A Datadog serverless report (2024) analyzing telemetry from 8,000 organizations found that 31% of Lambda functions had average durations exceeding 1 second and that 22% of organizations experienced unexpected cost spikes due to cold starts, retry storms, or recursive invocation bugs.",
            "Research from the IEEE International Conference on Cloud Computing (2024) found that for sustained high-throughput workloads exceeding 60% CPU utilization, reserved EC2 instances were 2-3 times more cost-effective than equivalent Lambda configurations, with the crossover point varying by memory allocation and execution duration."
        ],
        "context_sources": [
            {"source_id": "aws_serverless_cases_2024", "source_type": "industry", "authority": "primary"},
            {"source_id": "datadog_serverless_2024", "source_type": "industry", "authority": "primary"},
            {"source_id": "ieee_cloud_2024", "source_type": "academic", "authority": "primary"}
        ],
        "expected_mode": "trustworthy",
        "description": "Serverless cost-effectiveness addressed from vendor case studies, operational telemetry, and academic benchmarking.",
        "rationale": "Sources present complementary findings -- cost savings for bursty workloads, operational pitfalls, and steady-state cost disadvantages -- requiring hedged conclusions about when serverless is and is not cost-effective."
    })

    cases.append({
        "id": "t1_qualify_hard_925",
        "difficulty": "hard",
        "subcategory": "cross_source_partial",
        "query": "Does adopting microservices architecture improve software delivery speed?",
        "contexts": [
            "The 2024 Accelerate State of DevOps Report found that high-performing teams using microservices deployed 46 times more frequently than low performers, but noted that organizational culture, CI/CD maturity, and team autonomy were stronger predictors of delivery speed than architecture alone.",
            "A study published in Empirical Software Engineering (2024) tracked 15 organizations through monolith-to-microservices migrations and found that delivery speed initially decreased by 20-35% during the 12-18 month transition period due to the complexity of distributed systems, service mesh configuration, and data consistency challenges.",
            "ThoughtWorks Technology Radar (2024) recommends that organizations with fewer than 50 engineers avoid microservices, citing that the operational overhead -- service discovery, distributed tracing, network latency management -- often outweighs benefits for smaller teams."
        ],
        "context_sources": [
            {"source_id": "dora_devops_2024", "source_type": "industry", "authority": "primary"},
            {"source_id": "ese_migration_study_2024", "source_type": "academic", "authority": "primary"},
            {"source_id": "thoughtworks_radar_2024", "source_type": "industry", "authority": "expert"}
        ],
        "expected_mode": "trustworthy",
        "description": "Microservices delivery impact addressed from performance metrics, migration studies, and practitioner guidance.",
        "rationale": "Sources cover different aspects -- correlation with high performance, transition costs, and team-size thresholds -- requiring a heavily hedged answer about context-dependent benefits."
    })

    cases.append({
        "id": "t1_qualify_hard_926",
        "difficulty": "hard",
        "subcategory": "cross_source_partial",
        "query": "Is Rust a good replacement for C++ in systems programming?",
        "contexts": [
            "Microsoft's security team reported that 70% of all CVEs in Microsoft products are memory safety issues, and that adopting Rust for new Windows components has eliminated entire classes of vulnerabilities, including use-after-free, buffer overflow, and double-free bugs in rewritten modules.",
            "A benchmark study published in ACM Computing Surveys (2024) found that Rust programs achieved 95-105% of C++ performance across compute-intensive tasks, with equivalent performance for most algorithms but 5-10% slower compilation times and larger binary sizes for template-heavy equivalents.",
            "The Linux kernel's Rust integration lead noted in a 2024 LWN.net interview that Rust's steep learning curve (median onboarding time of 3-6 months for experienced C++ developers) and limited ecosystem for low-level hardware interfaces remain significant barriers, with only 0.1% of kernel code written in Rust as of kernel 6.8."
        ],
        "context_sources": [
            {"source_id": "msrc_memory_safety_2024", "source_type": "industry", "authority": "expert"},
            {"source_id": "acm_surveys_rust_2024", "source_type": "academic", "authority": "primary"},
            {"source_id": "lwn_rust_kernel_2024", "source_type": "news", "authority": "expert"}
        ],
        "expected_mode": "trustworthy",
        "description": "Rust vs C++ evaluated from security benefits, performance parity, and adoption barriers perspectives.",
        "rationale": "Sources address different dimensions -- security improvements, performance equivalence, and practical adoption challenges -- requiring a hedged answer that weighs compelling safety benefits against real-world adoption friction."
    })

    # --- LAW (3 cases) ---

    cases.append({
        "id": "t1_qualify_hard_927",
        "difficulty": "hard",
        "subcategory": "cross_source_partial",
        "query": "Can employers legally monitor employee communications on company devices?",
        "contexts": [
            "The Electronic Communications Privacy Act (ECPA) of 1986 permits employers to monitor electronic communications on company-owned devices when there is a legitimate business purpose, and also allows monitoring if employees have provided consent, which most employer acceptable-use policies require as a condition of employment.",
            "A National Law Review analysis (2024) notes that several states -- including California, Connecticut, Delaware, and New York -- have enacted notification requirements that go beyond federal law, mandating that employers provide advance written notice before monitoring employee electronic communications, even on company equipment.",
            "The European Court of Human Rights ruled in Barbulescu v. Romania (2017) that even on employer-owned devices, monitoring must be proportionate and employees must have prior notice, a standard now reflected in EU GDPR workplace guidance, relevant for US companies with European employees."
        ],
        "context_sources": [
            {"source_id": "ecpa_legal_analysis", "source_type": "government", "authority": "official"},
            {"source_id": "nlr_state_monitoring_2024", "source_type": "news", "authority": "secondary"},
            {"source_id": "echr_barbulescu_2017", "source_type": "government", "authority": "official"}
        ],
        "expected_mode": "trustworthy",
        "description": "Employee monitoring legality addressed from federal law, state variations, and international obligations.",
        "rationale": "Sources cover different jurisdictional layers -- federal permissiveness, state notification requirements, and EU proportionality standards -- requiring a hedged answer noting that legality depends heavily on jurisdiction and compliance details."
    })

    cases.append({
        "id": "t1_qualify_hard_928",
        "difficulty": "hard",
        "subcategory": "cross_source_partial",
        "query": "Are non-compete agreements enforceable in the United States?",
        "contexts": [
            "The FTC's 2024 final rule attempted to ban most non-compete agreements nationwide, but a federal court in Ryan LLC v. FTC (N.D. Texas, August 2024) issued a nationwide injunction blocking the rule, leaving enforcement to state law for the foreseeable future.",
            "According to the Uniform Law Commission's 2024 survey, California, Minnesota, North Dakota, and Oklahoma effectively ban non-compete agreements for employees, while states like Florida and Texas enforce them when they are reasonable in scope, duration (typically 1-2 years), and geographic limitation.",
            "A Harvard Business Review analysis (2024) found that even in states where non-competes are technically enforceable, litigation outcomes are unpredictable -- courts invalidated 42% of challenged non-competes as overly broad, with enforceability hinging on specific factual circumstances rather than boilerplate contract language."
        ],
        "context_sources": [
            {"source_id": "ftc_noncompete_rule_2024", "source_type": "government", "authority": "official"},
            {"source_id": "ulc_state_survey_2024", "source_type": "academic", "authority": "primary"},
            {"source_id": "hbr_noncompete_analysis_2024", "source_type": "news", "authority": "secondary"}
        ],
        "expected_mode": "trustworthy",
        "description": "Non-compete enforceability addressed from federal regulatory, state law, and litigation outcome perspectives.",
        "rationale": "Sources cover different facets -- blocked federal ban, state-by-state variation, and unpredictable litigation -- requiring heavily hedged answer that the answer depends entirely on jurisdiction and specific contract terms."
    })

    cases.append({
        "id": "t1_qualify_hard_929",
        "difficulty": "hard",
        "subcategory": "cross_source_partial",
        "query": "What are the legal risks of using AI-generated content for commercial purposes?",
        "contexts": [
            "The US Copyright Office's 2023 guidance and subsequent Thaler v. Perlmutter ruling established that purely AI-generated works without human authorship are not copyrightable, but works involving substantial human creative input in the prompting, selection, or arrangement process may receive copyright protection for the human-authored elements.",
            "A Reuters legal analysis (2024) documented 14 pending federal lawsuits against AI companies by content creators alleging that training data constituted copyright infringement, with outcomes that could retroactively affect the legality of AI-generated outputs, creating uncertainty for commercial users.",
            "The EU AI Act (effective August 2025) requires that AI-generated content be clearly labeled as such when used commercially, with penalties of up to 3% of global annual revenue for non-compliance, creating additional compliance obligations for companies operating in European markets."
        ],
        "context_sources": [
            {"source_id": "usco_ai_guidance_2023", "source_type": "government", "authority": "official"},
            {"source_id": "reuters_ai_litigation_2024", "source_type": "news", "authority": "secondary"},
            {"source_id": "eu_ai_act_2024", "source_type": "government", "authority": "official"}
        ],
        "expected_mode": "trustworthy",
        "description": "AI content legal risks addressed from copyright law, pending litigation, and regulatory compliance perspectives.",
        "rationale": "Sources cover different legal dimensions -- copyrightability uncertainty, litigation risk, and emerging regulation -- requiring a heavily hedged answer acknowledging the rapidly evolving and jurisdiction-dependent legal landscape."
    })

    return cases


def main():
    direct_cases = build_direct_cases()
    hedged_cases = build_hedged_cases()

    output = {
        "direct_cases": direct_cases,
        "hedged_cases": hedged_cases
    }

    output_path = os.path.join(os.path.dirname(__file__), "new_trustworthy_multisource.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(direct_cases)} direct cases and {len(hedged_cases)} hedged cases.")
    print(f"Output written to: {output_path}")

    # Validate all cases
    errors = []
    for label, case_list in [("direct", direct_cases), ("hedged", hedged_cases)]:
        for case in case_list:
            cid = case["id"]
            # Check required fields
            for field in ["id", "difficulty", "subcategory", "query", "contexts",
                          "context_sources", "expected_mode", "description", "rationale"]:
                if field not in case:
                    errors.append(f"{cid}: missing field '{field}'")
            # Check context_sources length matches contexts
            if len(case.get("contexts", [])) != len(case.get("context_sources", [])):
                errors.append(
                    f"{cid}: contexts ({len(case['contexts'])}) != "
                    f"context_sources ({len(case['context_sources'])})"
                )
            # Check source_type values
            valid_source_types = {"academic", "news", "government", "industry", "blog", "reference", "report"}
            for src in case.get("context_sources", []):
                if src.get("source_type") not in valid_source_types:
                    errors.append(f"{cid}: invalid source_type '{src.get('source_type')}'")
            # Check authority values
            valid_authorities = {"primary", "secondary", "tertiary", "official", "expert", "community"}
            for src in case.get("context_sources", []):
                if src.get("authority") not in valid_authorities:
                    errors.append(f"{cid}: invalid authority '{src.get('authority')}'")
            # Check expected_mode
            if case.get("expected_mode") != "trustworthy":
                errors.append(f"{cid}: expected_mode should be 'trustworthy'")
            # Check difficulty
            if case.get("difficulty") != "hard":
                errors.append(f"{cid}: difficulty should be 'hard'")

    if errors:
        print(f"\nValidation FAILED with {len(errors)} error(s):")
        for e in errors:
            print(f"  - {e}")
    else:
        print("\nValidation PASSED: all 30 cases are well-formed.")


if __name__ == "__main__":
    main()
