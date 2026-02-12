#!/usr/bin/env python3
"""Generate 50 new dispute cases (batch 2) for fitz-gov benchmark.

IDs: t1_dispute_hard_668 through t1_dispute_hard_717

Subcategory distribution:
  - temporal_source_conflict (10, IDs 668-677) - MULTI-SOURCE with context_sources
  - implicit_contradiction (5, IDs 678-682) - SINGLE SOURCE
  - binary_conflict (10, IDs 683-692) - SINGLE SOURCE
  - interpretation_conflict (10, IDs 693-702) - NEW subcategory, SINGLE SOURCE
  - scientific_replication (10, IDs 703-712) - NEW subcategory, SINGLE SOURCE
  - numerical_conflict (5, IDs 713-717) - SINGLE SOURCE
"""

import json
import os

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "new_dispute_batch2.json")


def build_cases() -> list[dict]:
    cases = []

    # =========================================================================
    # 1. temporal_source_conflict (10 cases, IDs 668-677) -- MULTI-SOURCE
    #    Domain spread: 2 science, 2 law, 2 health, 2 tech, 2 finance
    # =========================================================================

    # 668 - science
    cases.append({
        "id": "t1_dispute_hard_668",
        "difficulty": "hard",
        "subcategory": "temporal_source_conflict",
        "query": "What is the recommended treatment for mild depression?",
        "contexts": [
            "A 2019 clinical practice guideline from the American Psychiatric Association states that SSRIs remain the first-line treatment for mild to moderate depression, citing response rates of 60-70% across multiple randomized trials.",
            "A 2024 meta-analysis published in The Lancet Psychiatry, covering 47 trials and 12,000 patients, concludes that psychotherapy alone is as effective as SSRIs for mild depression, with significantly fewer side effects and lower relapse rates at 12-month follow-up."
        ],
        "expected_mode": "disputed",
        "description": "Newer meta-analysis challenges the established guideline on first-line treatment for mild depression.",
        "rationale": "The 2019 guideline recommends SSRIs as first-line, but the 2024 meta-analysis of 47 trials argues psychotherapy alone is equally effective with fewer side effects, creating a temporal conflict between authoritative sources.",
        "context_sources": [
            {"source_id": "apa_guideline_2019", "source_type": "clinical_guideline", "authority": "primary"},
            {"source_id": "lancet_meta_analysis_2024", "source_type": "academic", "authority": "primary"}
        ]
    })

    # 669 - science
    cases.append({
        "id": "t1_dispute_hard_669",
        "difficulty": "hard",
        "subcategory": "temporal_source_conflict",
        "query": "How old is the universe?",
        "contexts": [
            "NASA's 2020 measurement using the Planck satellite's cosmic microwave background data places the age of the universe at 13.77 billion years, with a margin of error of just 40 million years.",
            "A 2023 study led by Dr. Rajendra Gupta at the University of Ottawa, published in Monthly Notices of the Royal Astronomical Society, proposes that the universe may be 26.7 billion years old, nearly double the accepted estimate, based on a model incorporating tired light theory and evolving coupling constants."
        ],
        "expected_mode": "disputed",
        "description": "A 2023 cosmological model challenges the widely accepted Planck satellite age estimate of the universe.",
        "rationale": "The established 13.77-billion-year estimate from Planck data directly conflicts with a newer 26.7-billion-year proposal, representing a fundamental disagreement about cosmological models and measurement interpretation.",
        "context_sources": [
            {"source_id": "nasa_planck_2020", "source_type": "government_agency", "authority": "primary"},
            {"source_id": "gupta_mnras_2023", "source_type": "academic", "authority": "primary"}
        ]
    })

    # 670 - law
    cases.append({
        "id": "t1_dispute_hard_670",
        "difficulty": "hard",
        "subcategory": "temporal_source_conflict",
        "query": "Can employers monitor employees' personal devices used for work?",
        "contexts": [
            "The 2018 EU General Data Protection Regulation (GDPR) Article 6 permits employers to process employee data, including device monitoring, when there is a legitimate business interest, provided employees are informed and the monitoring is proportionate.",
            "A January 2024 ruling by the European Court of Human Rights in Lopez Ribalda v. Spain established that covert monitoring of employees, even on work devices, violates Article 8 of the European Convention on Human Rights unless strictly necessary and pre-authorized by a judicial body.",
            "The French CNIL issued updated guidance in March 2024 stating that any employer monitoring of personal devices used in BYOD arrangements requires explicit, freely given consent that cannot be a condition of employment."
        ],
        "expected_mode": "disputed",
        "description": "Recent court rulings and regulatory guidance restrict the employer monitoring latitude previously allowed under GDPR.",
        "rationale": "GDPR's 2018 framework allowed monitoring under legitimate interest, but the 2024 ECHR ruling and CNIL guidance impose stricter consent and necessity requirements, creating a temporal conflict in the legal landscape.",
        "context_sources": [
            {"source_id": "gdpr_2018_article6", "source_type": "legislation", "authority": "primary"},
            {"source_id": "echr_lopez_ribalda_2024", "source_type": "court_ruling", "authority": "primary"},
            {"source_id": "cnil_byod_guidance_2024", "source_type": "regulatory_guidance", "authority": "secondary"}
        ]
    })

    # 671 - law
    cases.append({
        "id": "t1_dispute_hard_671",
        "difficulty": "hard",
        "subcategory": "temporal_source_conflict",
        "query": "Is non-compete enforcement legal for low-wage workers in the United States?",
        "contexts": [
            "Under common law principles reaffirmed by many state courts through 2020, non-compete agreements are generally enforceable if they are reasonable in scope, duration, and geographic area, regardless of the worker's wage level.",
            "The FTC's April 2024 final rule bans virtually all non-compete clauses nationwide, with limited exceptions for senior executives earning above $151,164 annually, effectively making non-competes illegal for low-wage workers."
        ],
        "expected_mode": "disputed",
        "description": "FTC's 2024 non-compete ban conflicts with longstanding common law enforcement tradition.",
        "rationale": "State courts have historically enforced reasonable non-competes at all wage levels, but the FTC's 2024 rule effectively bans them for low-wage workers, creating a direct temporal conflict between established precedent and new federal regulation.",
        "context_sources": [
            {"source_id": "state_common_law_2020", "source_type": "legal_precedent", "authority": "primary"},
            {"source_id": "ftc_noncompete_rule_2024", "source_type": "federal_regulation", "authority": "primary"}
        ]
    })

    # 672 - health
    cases.append({
        "id": "t1_dispute_hard_672",
        "difficulty": "hard",
        "subcategory": "temporal_source_conflict",
        "query": "Should healthy adults take a daily aspirin to prevent heart attacks?",
        "contexts": [
            "The 2016 U.S. Preventive Services Task Force recommendation stated that low-dose aspirin (81 mg) is beneficial for adults aged 50-59 with a 10% or greater 10-year cardiovascular risk, receiving a B-grade recommendation.",
            "The USPSTF's updated 2022 recommendation reversed its position, stating that the evidence no longer supports routine aspirin use for primary prevention in adults over 60, and that the decision for adults 40-59 should be individual, downgrading to a C-grade recommendation due to bleeding risks."
        ],
        "expected_mode": "disputed",
        "description": "USPSTF reversed its own aspirin recommendation within six years based on new bleeding risk evidence.",
        "rationale": "The same authoritative body (USPSTF) gave a B-grade recommendation for aspirin in 2016 but then effectively reversed it in 2022, with the updated guidance citing bleeding risks that outweigh cardiovascular benefits for most healthy adults.",
        "context_sources": [
            {"source_id": "uspstf_aspirin_2016", "source_type": "clinical_guideline", "authority": "primary"},
            {"source_id": "uspstf_aspirin_2022", "source_type": "clinical_guideline", "authority": "primary"}
        ]
    })

    # 673 - health
    cases.append({
        "id": "t1_dispute_hard_673",
        "difficulty": "hard",
        "subcategory": "temporal_source_conflict",
        "query": "Is vaping a safe alternative to cigarettes for smoking cessation?",
        "contexts": [
            "Public Health England's 2018 evidence review concluded that e-cigarettes are approximately 95% less harmful than combustible cigarettes and should be promoted as a cessation tool, recommending that NHS stop-smoking services offer vaping support.",
            "A 2024 WHO technical report found that e-cigarettes contain at least 2,000 chemicals, including known carcinogens like formaldehyde and acrolein, and stated there is insufficient evidence that they aid cessation, recommending that countries ban or strictly regulate them."
        ],
        "expected_mode": "disputed",
        "description": "WHO's 2024 position on e-cigarette safety directly contradicts Public Health England's 2018 endorsement.",
        "rationale": "PHE's 2018 report endorsed vaping as 95% safer and a cessation aid, while WHO's 2024 report highlights thousands of harmful chemicals and insufficient cessation evidence, representing a stark temporal disagreement between major health authorities.",
        "context_sources": [
            {"source_id": "phe_vaping_review_2018", "source_type": "government_report", "authority": "primary"},
            {"source_id": "who_ecig_report_2024", "source_type": "international_organization", "authority": "primary"}
        ]
    })

    # 674 - tech
    cases.append({
        "id": "t1_dispute_hard_674",
        "difficulty": "hard",
        "subcategory": "temporal_source_conflict",
        "query": "Is blockchain technology suitable for enterprise supply chain management?",
        "contexts": [
            "Gartner's 2019 Hype Cycle report predicted that blockchain would reach mainstream enterprise adoption within 5-10 years, citing pilot programs at Walmart, Maersk, and De Beers as evidence that supply chain transparency use cases were near production-ready.",
            "Gartner's 2024 updated analysis found that 80% of enterprise blockchain supply chain projects launched between 2018 and 2022 were abandoned or mothballed, with most organizations reverting to centralized databases, citing scalability limitations, interoperability failures, and governance complexities."
        ],
        "expected_mode": "disputed",
        "description": "Gartner's own enterprise blockchain predictions from 2019 were contradicted by their 2024 adoption data.",
        "rationale": "The same analyst firm predicted mainstream blockchain adoption for supply chains in 2019, but their 2024 data shows 80% of those projects failed, creating a temporal conflict about blockchain's enterprise viability.",
        "context_sources": [
            {"source_id": "gartner_hype_cycle_2019", "source_type": "industry_report", "authority": "primary"},
            {"source_id": "gartner_blockchain_review_2024", "source_type": "industry_report", "authority": "primary"}
        ]
    })

    # 675 - tech
    cases.append({
        "id": "t1_dispute_hard_675",
        "difficulty": "hard",
        "subcategory": "temporal_source_conflict",
        "query": "Is quantum computing a near-term threat to current encryption standards?",
        "contexts": [
            "The National Security Agency's 2021 cybersecurity advisory stated that quantum computers capable of breaking RSA-2048 encryption were at least 20-30 years away, and recommended organizations begin planning for post-quantum migration on a gradual timeline.",
            "IBM's December 2023 Quantum Development Roadmap announced achieving a 1,121-qubit processor and projected reaching 100,000 logical qubits by 2033, with cryptographically relevant quantum computing potentially achievable within 10 years, prompting NIST to accelerate its post-quantum cryptography standardization to 2024."
        ],
        "expected_mode": "disputed",
        "description": "IBM's 2023 quantum roadmap challenges NSA's 2021 assessment of the timeline for encryption-breaking quantum computers.",
        "rationale": "The NSA estimated 20-30 years in 2021, but IBM's 2023 hardware advances and NIST's accelerated standardization suggest the threat may materialize within 10 years, creating a significant temporal conflict on quantum computing timelines.",
        "context_sources": [
            {"source_id": "nsa_quantum_advisory_2021", "source_type": "government_advisory", "authority": "primary"},
            {"source_id": "ibm_quantum_roadmap_2023", "source_type": "industry_report", "authority": "primary"}
        ]
    })

    # 676 - finance
    cases.append({
        "id": "t1_dispute_hard_676",
        "difficulty": "hard",
        "subcategory": "temporal_source_conflict",
        "query": "Are index funds always the best investment strategy for retail investors?",
        "contexts": [
            "The 2019 S&P SPIVA Scorecard showed that over 15 years, 92.2% of large-cap active fund managers underperformed the S&P 500 after fees, strongly supporting passive index investing as the optimal strategy for most retail investors.",
            "A 2024 Morningstar analysis found that during the 2022-2023 period of rising interest rates and sector rotation, 55% of active large-cap managers outperformed their benchmark index, and that index concentration risk (the top 7 stocks representing 30% of the S&P 500) introduced systematic risk that active managers could avoid."
        ],
        "expected_mode": "disputed",
        "description": "Recent active management outperformance challenges the long-standing dominance of passive index funds.",
        "rationale": "The 2019 SPIVA data overwhelmingly favored index funds over 15 years, but the 2024 Morningstar analysis shows active managers outperformed during recent market stress and highlights concentration risk in indices, creating a temporal conflict about optimal investment strategy.",
        "context_sources": [
            {"source_id": "sp_spiva_2019", "source_type": "financial_report", "authority": "primary"},
            {"source_id": "morningstar_active_2024", "source_type": "financial_report", "authority": "primary"}
        ]
    })

    # 677 - finance
    cases.append({
        "id": "t1_dispute_hard_677",
        "difficulty": "hard",
        "subcategory": "temporal_source_conflict",
        "query": "Is cryptocurrency a viable store of value?",
        "contexts": [
            "A 2021 Goldman Sachs research note argued that Bitcoin's extreme volatility (annualized at 80%), lack of intrinsic yield, and correlation with risk assets during market stress made it unsuitable as a store of value, recommending clients avoid allocation.",
            "BlackRock's January 2024 Bitcoin ETF filing and subsequent SEC approval argued that Bitcoin had matured as a store of value, citing declining volatility (annualized at 45% in 2023), institutional custody solutions, and its 15-year track record of outperforming gold and equities on a risk-adjusted basis over rolling 4-year periods."
        ],
        "expected_mode": "disputed",
        "description": "BlackRock's 2024 Bitcoin ETF thesis contradicts Goldman Sachs' 2021 rejection of Bitcoin as a store of value.",
        "rationale": "Goldman Sachs dismissed Bitcoin's store-of-value potential in 2021 citing 80% volatility, while BlackRock's 2024 ETF filing argues Bitcoin has matured with lower volatility at 45% and superior risk-adjusted returns, representing conflicting assessments from major financial institutions across time.",
        "context_sources": [
            {"source_id": "goldman_crypto_note_2021", "source_type": "financial_report", "authority": "primary"},
            {"source_id": "blackrock_btc_etf_2024", "source_type": "regulatory_filing", "authority": "primary"}
        ]
    })

    # =========================================================================
    # 2. implicit_contradiction (5 cases, IDs 678-682) -- SINGLE SOURCE
    #    Domain spread: 1 science, 1 law, 1 finance, 1 health, 1 education
    # =========================================================================

    # 678 - science
    cases.append({
        "id": "t1_dispute_hard_678",
        "difficulty": "hard",
        "subcategory": "implicit_contradiction",
        "query": "Can the Mars rover complete its extended mission objectives?",
        "contexts": [
            "NASA's Perseverance rover has been operating on Mars for over 1,200 sols and its nuclear power source (MMRTG) is designed to provide at least 110 watts for 14 Earth years.",
            "The extended mission plan requires the rover to traverse 28 kilometers of terrain with elevation changes exceeding 600 meters to reach the Jezero crater rim sampling sites.",
            "Engineering telemetry shows the rover's left front wheel has sustained 62% tread degradation after covering only 18 kilometers on relatively flat terrain.",
            "Mission scientists estimate the remaining sampling campaign requires a minimum of 45 operational wheel-kilometers."
        ],
        "expected_mode": "disputed",
        "description": "Power supply is sufficient but wheel degradation rate implies mechanical failure before mission completion.",
        "rationale": "The power source supports 14 years of operation, but the wheel has lost 62% tread in 18 km, while the mission needs 45 more km on harder terrain -- implying the rover may not physically survive to use its ample power supply."
    })

    # 679 - law
    cases.append({
        "id": "t1_dispute_hard_679",
        "difficulty": "hard",
        "subcategory": "implicit_contradiction",
        "query": "Can the defendant's confession be used as evidence at trial?",
        "contexts": [
            "The defendant signed a written confession at the police station at 3:47 AM on October 12, admitting to the robbery in detail.",
            "Police body camera footage shows officers arrived at the defendant's home at 11:15 PM on October 11 and immediately placed him in handcuffs.",
            "The booking record indicates the defendant was formally read his Miranda rights at 3:30 AM on October 12, seventeen minutes before signing the confession.",
            "The defendant has no prior criminal record and speaks English as a second language with limited proficiency."
        ],
        "expected_mode": "disputed",
        "description": "Confession was signed after Miranda rights were read, but defendant was restrained for over four hours before that.",
        "rationale": "While Miranda rights were technically administered before the confession, the 4+ hour custodial detention without rights notification, combined with the suspect's limited English proficiency, implicitly contradicts the voluntariness of the confession."
    })

    # 680 - finance
    cases.append({
        "id": "t1_dispute_hard_680",
        "difficulty": "hard",
        "subcategory": "implicit_contradiction",
        "query": "Is TechVenture Inc. a good investment based on its latest earnings report?",
        "contexts": [
            "TechVenture Inc. reported Q4 revenue of $2.3 billion, beating analyst estimates of $2.1 billion by 9.5%, marking the eighth consecutive quarter of revenue beats.",
            "The company announced a $500 million stock buyback program and raised its 2025 revenue guidance by 12% to $10.5 billion.",
            "The CFO sold 85% of her vested stock options, totaling $14.2 million, during a pre-announced 10b5-1 trading window that opened three days after the earnings release.",
            "Three independent board members also filed Form 4 disclosures showing combined sales of $8.7 million in the same window."
        ],
        "expected_mode": "disputed",
        "description": "Strong earnings and raised guidance conflict with massive insider selling by the CFO and board members.",
        "rationale": "The company beat estimates and raised guidance, which signals confidence, but the CFO selling 85% of her options and board members unloading $8.7M implicitly contradicts the bullish narrative -- insiders are acting as if the stock is overvalued despite publicly optimistic signals."
    })

    # 681 - health
    cases.append({
        "id": "t1_dispute_hard_681",
        "difficulty": "hard",
        "subcategory": "implicit_contradiction",
        "query": "Is the hospital's new patient safety initiative working?",
        "contexts": [
            "Memorial Regional Hospital's 2024 annual report states that reported medication errors decreased by 34% following the implementation of their AI-assisted prescribing system in January 2024.",
            "The same report notes that the hospital increased its nursing staff-to-patient ratio from 1:6 to 1:4 during the same period as part of a broader hiring initiative.",
            "A CMS audit found that the hospital's voluntary error reporting rate dropped by 28% in 2024, with staff citing 'alert fatigue' from the new AI system as a barrier to completing incident reports.",
            "Patient readmission rates for medication-related complications remained unchanged at 4.7% year-over-year."
        ],
        "expected_mode": "disputed",
        "description": "Reported medication errors dropped, but so did the reporting rate, and patient outcomes did not improve.",
        "rationale": "The 34% decrease in reported errors looks positive, but the 28% drop in reporting rates suggests errors are being underreported rather than prevented, and unchanged readmission rates implicitly contradict any real safety improvement."
    })

    # 682 - education
    cases.append({
        "id": "t1_dispute_hard_682",
        "difficulty": "hard",
        "subcategory": "implicit_contradiction",
        "query": "Has the school district's new literacy program improved reading outcomes?",
        "contexts": [
            "The Greenfield School District reported that average 3rd-grade reading scores on the state standardized test increased from 62% to 71% proficiency after one year of implementing the Foundations First phonics curriculum.",
            "The district also reported that 15% of students were reclassified from special education reading services to general education during the same year.",
            "State records show the district's 3rd-grade enrollment dropped from 2,400 to 1,950 students between the two testing years, with the superintendent citing 'families relocating due to housing costs.'",
            "The neighboring district, which absorbed many of Greenfield's transferring families, saw its 3rd-grade reading proficiency drop from 68% to 59% in the same period."
        ],
        "expected_mode": "disputed",
        "description": "Reading scores improved but enrollment dropped significantly, and the receiving district's scores declined.",
        "rationale": "The 9-point proficiency gain and special education reclassifications look positive, but losing 450 students (19%) while the receiving district's scores dropped by 9 points implicitly suggests the improvement came from lower-performing students leaving rather than from the new curriculum."
    })

    # =========================================================================
    # 3. binary_conflict (10 cases, IDs 683-692) -- SINGLE SOURCE
    #    Domain spread: 2 science, 2 law, 2 health, 2 sports, 2 tech
    # =========================================================================

    # 683 - science
    cases.append({
        "id": "t1_dispute_hard_683",
        "difficulty": "hard",
        "subcategory": "binary_conflict",
        "query": "Is Pluto a planet?",
        "contexts": [
            "The International Astronomical Union's 2006 Resolution 5A formally reclassified Pluto as a 'dwarf planet' because it has not cleared its orbital neighborhood of other debris, failing one of three criteria for full planet status.",
            "NASA administrator Jim Bridenstine stated in 2019: 'I am here to tell you, as the NASA administrator, I believe Pluto is a planet,' arguing that the IAU definition is arbitrary and that geological complexity should be the primary criterion.",
            "A 2022 petition signed by over 300 planetary scientists called for reinstating Pluto's planet status, citing that the 'clearing the neighborhood' criterion would also disqualify Earth and Jupiter."
        ],
        "expected_mode": "disputed",
        "description": "The IAU says Pluto is not a planet, but NASA's administrator and hundreds of scientists disagree.",
        "rationale": "The IAU formally declassified Pluto in 2006, but NASA's own administrator and 300+ scientists dispute the definition itself, creating a binary yes/no conflict backed by credible authorities on both sides."
    })

    # 684 - science
    cases.append({
        "id": "t1_dispute_hard_684",
        "difficulty": "hard",
        "subcategory": "binary_conflict",
        "query": "Do humans have a fixed number of brain cells that cannot regenerate?",
        "contexts": [
            "A landmark 2018 study published in Nature by Sorrells et al. examined post-mortem hippocampal tissue from 59 subjects and found no evidence of new neuron formation in the adult human hippocampus, concluding that neurogenesis ceases in childhood.",
            "A competing 2019 study in Nature Medicine by Moreno-Jimenez et al. used improved tissue preservation techniques on 13 deceased adults and detected thousands of immature neurons in the hippocampus, arguing that adult neurogenesis persists throughout life but is methodologically difficult to detect."
        ],
        "expected_mode": "disputed",
        "description": "Two Nature-published studies reach opposite conclusions about whether adult human brains generate new neurons.",
        "rationale": "Sorrells et al. (2018) found zero new neurons in adults, while Moreno-Jimenez et al. (2019) found thousands using different methods -- a direct binary conflict about whether adult neurogenesis occurs at all."
    })

    # 685 - law
    cases.append({
        "id": "t1_dispute_hard_685",
        "difficulty": "hard",
        "subcategory": "binary_conflict",
        "query": "Can an employer fire an employee for off-duty marijuana use in a legal state?",
        "contexts": [
            "Under federal law, marijuana remains a Schedule I controlled substance, and the Drug-Free Workplace Act of 1988 permits employers receiving federal contracts to terminate employees who test positive for THC regardless of state legalization.",
            "California's AB 2188, effective January 2024, prohibits employers from discriminating against employees for off-duty cannabis use and bars the use of THC metabolite tests (which detect past use) in employment decisions, with exceptions only for federal contractors and safety-sensitive positions."
        ],
        "expected_mode": "disputed",
        "description": "Federal law permits termination for marijuana use while California state law prohibits it.",
        "rationale": "Federal law explicitly allows firing for THC-positive tests, while California AB 2188 explicitly prohibits discrimination for off-duty use -- a direct binary conflict between federal and state law for non-federal-contractor employers."
    })

    # 686 - law
    cases.append({
        "id": "t1_dispute_hard_686",
        "difficulty": "hard",
        "subcategory": "binary_conflict",
        "query": "Is it legal to record a phone conversation without the other party's consent?",
        "contexts": [
            "Under federal law (18 U.S.C. 2511), the United States follows a one-party consent rule: recording a phone call is legal as long as one participant (including the person recording) consents, and no court order is required.",
            "California Penal Code Section 632 requires all-party consent for recording confidential communications, making it a criminal offense punishable by a fine of up to $2,500 and up to one year in jail to record a call without the other party's knowledge."
        ],
        "expected_mode": "disputed",
        "description": "Federal law allows one-party consent recording while California law criminalizes it.",
        "rationale": "Federal statute says yes (one-party consent is sufficient), California statute says no (all parties must consent) -- a direct binary legal conflict depending on which jurisdiction's law applies."
    })

    # 687 - health
    cases.append({
        "id": "t1_dispute_hard_687",
        "difficulty": "hard",
        "subcategory": "binary_conflict",
        "query": "Should you feed a cold and starve a fever?",
        "contexts": [
            "A 2002 study by Dutch researchers at the Academic Medical Center in Amsterdam found that eating stimulated the immune response needed to fight viral infections (colds), while fasting activated the immune response needed to fight bacterial infections (fevers), providing scientific support for the adage.",
            "The American College of Physicians and Harvard Medical School's 2023 patient guidance states that adequate nutrition and hydration are essential during any illness, that caloric restriction during fever can impair immune function and delay recovery, and that there is no clinical evidence supporting dietary restriction based on symptom type."
        ],
        "expected_mode": "disputed",
        "description": "A peer-reviewed study supports the folk wisdom while major medical institutions reject it entirely.",
        "rationale": "The 2002 Amsterdam study found scientific support for differentiated eating based on illness type, but the ACP and Harvard 2023 guidance directly rejects caloric restriction during fever as harmful -- a binary conflict between a research finding and clinical consensus."
    })

    # 688 - health
    cases.append({
        "id": "t1_dispute_hard_688",
        "difficulty": "hard",
        "subcategory": "binary_conflict",
        "query": "Is sitting for long periods as dangerous as smoking?",
        "contexts": [
            "A 2014 meta-analysis published in the Journal of the National Cancer Institute, analyzing 43 studies covering 4 million participants, found that prolonged sitting increased cancer risk by 24%, heart disease mortality by 18%, and all-cause mortality by 24%, leading lead author Dr. Daniela Schmid to call sitting 'the new smoking.'",
            "A 2024 rebuttal published in the British Journal of Sports Medicine by Professor Terry Boyle of the University of South Australia argues that the comparison is 'scientifically inaccurate and harmful,' noting that smoking causes 7 million deaths annually versus an estimated 400,000 attributable to sedentary behavior, and that the risks are not comparable in magnitude, mechanism, or dose-response relationship."
        ],
        "expected_mode": "disputed",
        "description": "One major study equates sitting risks to smoking while another rejects the comparison as grossly misleading.",
        "rationale": "The 2014 meta-analysis found sitting increased mortality by 24% and called it 'the new smoking,' but the 2024 rebuttal argues the comparison is inaccurate since smoking kills 17x more people -- a binary conflict about whether the equivalence is valid."
    })

    # 689 - sports
    cases.append({
        "id": "t1_dispute_hard_689",
        "difficulty": "hard",
        "subcategory": "binary_conflict",
        "query": "Does static stretching before exercise prevent injuries?",
        "contexts": [
            "The American College of Sports Medicine's 2018 guidelines recommend pre-exercise static stretching as part of a comprehensive warm-up routine, citing evidence that it improves range of motion and may reduce the incidence of muscle strains and joint injuries.",
            "A 2021 systematic review in the British Medical Journal covering 12 randomized controlled trials with 8,806 participants concluded that pre-exercise static stretching does not reduce overall injury risk, and may actually impair performance by reducing muscle force production by 5-8% and decreasing vertical jump height."
        ],
        "expected_mode": "disputed",
        "description": "ACSM recommends pre-exercise static stretching while a BMJ systematic review says it does not prevent injuries.",
        "rationale": "ACSM guidelines endorse static stretching for injury prevention, but a BMJ systematic review of 12 RCTs finds no injury reduction and 5-8% performance impairment -- directly opposite conclusions on whether the practice is beneficial."
    })

    # 690 - sports
    cases.append({
        "id": "t1_dispute_hard_690",
        "difficulty": "hard",
        "subcategory": "binary_conflict",
        "query": "Should youth athletes specialize in a single sport early?",
        "contexts": [
            "USA Hockey's long-term athlete development model recommends early sport specialization beginning at age 10-12 for competitive-track athletes, arguing that the 10,000-hour rule requires early focused training to develop elite-level skills before physical maturation windows close.",
            "The American Academy of Pediatrics' 2023 clinical report on youth sports recommends against single-sport specialization before age 15-16, citing evidence that early specializers have 81% higher overuse injury rates, 36% higher burnout rates, and are no more likely to reach elite levels than multi-sport athletes."
        ],
        "expected_mode": "disputed",
        "description": "A major sports federation recommends early specialization while the AAP advises against it.",
        "rationale": "USA Hockey says specialize by age 10-12 citing skill development windows, while the AAP says wait until 15-16 citing 81% higher injury rates and no elite advantage -- a direct binary conflict between sports development and medical organizations."
    })

    # 691 - tech
    cases.append({
        "id": "t1_dispute_hard_691",
        "difficulty": "hard",
        "subcategory": "binary_conflict",
        "query": "Is dark mode better for your eyes?",
        "contexts": [
            "A 2023 study by the University of Tubingen's Institute for Ophthalmic Research found that reading in dark mode reduced eye strain markers by 22% in a controlled trial of 120 participants who used screens for 6+ hours daily, with participants reporting less visual fatigue and fewer headaches.",
            "Researchers at the University of British Columbia published a 2024 study in the Journal of Experimental Psychology showing that dark mode actually reduces reading comprehension by 11% and increases error rates by 14%, and found no measurable difference in eye strain biomarkers between light and dark modes using objective pupillometry."
        ],
        "expected_mode": "disputed",
        "description": "One study shows dark mode reduces eye strain while another finds no objective benefit and reduced comprehension.",
        "rationale": "The Tubingen study found 22% less eye strain with dark mode, while the UBC study found no objective strain difference and 11% worse reading comprehension -- directly conflicting findings on whether dark mode helps or hinders."
    })

    # 692 - tech
    cases.append({
        "id": "t1_dispute_hard_692",
        "difficulty": "hard",
        "subcategory": "binary_conflict",
        "query": "Does using a VPN make you anonymous online?",
        "contexts": [
            "ExpressVPN's independent audit conducted by PricewaterhouseCoopers in 2023 confirmed that its TrustedServer technology stores no user logs, runs entirely in RAM, and that even a government subpoena cannot retrieve user browsing data, supporting its claim that VPN users are effectively anonymous.",
            "The Electronic Frontier Foundation's 2024 technical analysis states that VPNs do not provide anonymity because browser fingerprinting, DNS leaks, WebRTC leaks, and traffic correlation attacks can identify users even through a VPN connection, and that at least 26 VPN providers claiming 'no-log' policies were found to retain identifiable user data when subpoenaed."
        ],
        "expected_mode": "disputed",
        "description": "A VPN provider's audit claims effective anonymity while the EFF says VPNs fundamentally cannot provide it.",
        "rationale": "ExpressVPN's PwC audit confirms no-log anonymity, while the EFF argues VPNs cannot provide anonymity due to fingerprinting, leak vectors, and documented cases of 'no-log' providers retaining data -- a binary conflict about whether VPN anonymity is real."
    })

    # =========================================================================
    # 4. interpretation_conflict (10 cases, IDs 693-702) -- NEW subcategory
    #    Same facts, different interpretations/conclusions
    #    Domain spread: 2 science, 2 finance, 2 health, 2 education, 2 politics
    # =========================================================================

    # 693 - science
    cases.append({
        "id": "t1_dispute_hard_693",
        "difficulty": "hard",
        "subcategory": "interpretation_conflict",
        "query": "Is the decline of insect populations a crisis?",
        "contexts": [
            "A 2019 global meta-analysis in Biological Conservation found that 40% of insect species are declining, with total insect biomass decreasing by 2.5% per year, and warned of a potential 'insect apocalypse' within decades that could collapse pollination networks and food webs.",
            "A 2023 reanalysis of the same underlying datasets published in Nature Ecology & Evolution found that while certain insect groups (butterflies, beetles) are declining, freshwater insects have increased by 11% since 1990, and that the '40% declining' figure was inflated by geographic bias toward Western European studies, calling the apocalypse framing 'not supported by the totality of evidence.'"
        ],
        "expected_mode": "disputed",
        "description": "Same insect data interpreted as either an impending ecological apocalypse or a geographically biased exaggeration.",
        "rationale": "Both analyses reference overlapping datasets but draw opposite conclusions: one sees a 2.5% annual decline as catastrophic, the other identifies geographic bias and rising freshwater insect populations as evidence against the crisis narrative."
    })

    # 694 - science
    cases.append({
        "id": "t1_dispute_hard_694",
        "difficulty": "hard",
        "subcategory": "interpretation_conflict",
        "query": "Does the discovery of phosphine on Venus indicate extraterrestrial life?",
        "contexts": [
            "A 2020 paper in Nature Astronomy by Greaves et al. reported detecting 20 parts per billion of phosphine in Venus's atmosphere using the James Clerk Maxwell Telescope, arguing that no known abiotic chemical process can account for the observed concentration and that a biological source is the most plausible explanation.",
            "A 2022 reanalysis by Villanueva et al. using the same spectral data but different calibration techniques estimated the phosphine concentration at less than 1 part per billion, well within the range explainable by volcanic activity and photochemistry, and concluded that the detection does not require a biological explanation."
        ],
        "expected_mode": "disputed",
        "description": "Same spectral data from Venus interpreted as either evidence for life or an artifact of calibration error.",
        "rationale": "Greaves et al. interpret the spectral signal as 20 ppb phosphine requiring biological origin, while Villanueva et al. reanalyze the same data and find less than 1 ppb explainable by geology -- same data, opposite interpretations about extraterrestrial life."
    })

    # 695 - finance
    cases.append({
        "id": "t1_dispute_hard_695",
        "difficulty": "hard",
        "subcategory": "interpretation_conflict",
        "query": "Is the economy recovering?",
        "contexts": [
            "The Bureau of Economic Analysis reported that U.S. GDP grew 2.1% in Q3 2024, unemployment fell to 3.8%, consumer spending rose 1.5%, and the economy added 254,000 jobs in September, marking the 33rd consecutive month of job gains.",
            "Analysis by the Economic Policy Institute using the same government data notes that real wages declined 0.4% year-over-year when adjusted for housing costs, household debt reached a record $17.7 trillion, the growth was driven primarily by a 4.6% increase in government spending, and the labor force participation rate remained 0.8 points below pre-pandemic levels."
        ],
        "expected_mode": "disputed",
        "description": "Same economic data interpreted as either a strong recovery or a fragile expansion masking structural weakness.",
        "rationale": "The headline numbers (GDP up, unemployment down, jobs added) suggest recovery, but the same data reframed (declining real wages, record debt, government-driven growth, low participation) suggests underlying weakness -- identical facts supporting opposite conclusions."
    })

    # 696 - finance
    cases.append({
        "id": "t1_dispute_hard_696",
        "difficulty": "hard",
        "subcategory": "interpretation_conflict",
        "query": "Is the housing market overvalued?",
        "contexts": [
            "The National Association of Realtors' 2024 Q3 report highlights that median home prices rose 4.2% year-over-year to $412,300, existing home inventory reached its highest level in 3 years at 4.2 months of supply, and mortgage rates at 6.8% are stabilizing, characterizing the market as 'normalizing toward sustainable growth.'",
            "An analysis by the Federal Reserve Bank of Dallas using the same price and income data calculates that the price-to-income ratio reached 7.1x in Q3 2024, exceeding the 2006 pre-crisis peak of 6.8x, that the 4.2 months of inventory represents a 58% increase from the prior year signaling weakening demand, and that affordability for first-time buyers has reached its lowest point since 1984."
        ],
        "expected_mode": "disputed",
        "description": "Same housing data interpreted as healthy normalization by one source and pre-crisis overvaluation by another.",
        "rationale": "NAR interprets rising prices and increased inventory as normalization, while the Dallas Fed interprets the same metrics as price-to-income exceeding 2006 levels and historic unaffordability -- identical data framed as either stability or a bubble."
    })

    # 697 - health
    cases.append({
        "id": "t1_dispute_hard_697",
        "difficulty": "hard",
        "subcategory": "interpretation_conflict",
        "query": "Are ultra-processed foods responsible for the obesity epidemic?",
        "contexts": [
            "A 2024 Lancet study analyzing dietary data from 197 countries found that ultra-processed food consumption increased by 48% globally between 2000 and 2020, correlating with a 65% increase in obesity rates, and concluded that ultra-processed foods are 'the primary dietary driver of the global obesity epidemic.'",
            "Nutrition researchers at the University of Cambridge published a 2024 rebuttal in the BMJ arguing that the correlation is confounded by sedentary lifestyles, increased portion sizes, and urbanization occurring over the same period, and that controlled metabolic ward studies show calorie-matched diets of processed and unprocessed foods produce identical weight outcomes when total calories are controlled."
        ],
        "expected_mode": "disputed",
        "description": "Same global trend data interpreted as proof of ultra-processed food harm or as a confounded correlation.",
        "rationale": "The Lancet study interprets the parallel rise in processed food consumption and obesity as causal, while Cambridge researchers argue the correlation is confounded and that calorie-controlled studies show processing itself does not cause weight gain -- same data, conflicting causal interpretations."
    })

    # 698 - health
    cases.append({
        "id": "t1_dispute_hard_698",
        "difficulty": "hard",
        "subcategory": "interpretation_conflict",
        "query": "Does moderate alcohol consumption have health benefits?",
        "contexts": [
            "A 2022 observational study in JAMA Network Open analyzing 371,463 UK Biobank participants found that moderate drinkers (7-14 drinks/week) had 14% lower all-cause mortality than non-drinkers, with the strongest protective association for cardiovascular death, consistent with decades of J-curve epidemiological findings.",
            "A 2023 meta-analysis in JAMA by Dr. Tim Stockwell re-examined 107 studies including the UK Biobank data and found that after correcting for 'abstainer bias' (former drinkers and ill people in the non-drinker reference group), the apparent protective effect disappeared entirely, with even light drinking associated with slightly increased mortality."
        ],
        "expected_mode": "disputed",
        "description": "Same cohort data shows either protective effects of moderate drinking or an artifact of flawed reference groups.",
        "rationale": "The 2022 study finds a 14% mortality benefit for moderate drinkers, but the 2023 meta-analysis reanalyzes overlapping data and argues the benefit vanishes when the non-drinker control group is corrected for abstainer bias -- same data, opposite health conclusions."
    })

    # 699 - education
    cases.append({
        "id": "t1_dispute_hard_699",
        "difficulty": "hard",
        "subcategory": "interpretation_conflict",
        "query": "Has No Child Left Behind improved American education?",
        "contexts": [
            "NAEP data from 2002 to 2013 shows that 4th-grade math scores increased by 11 points and 8th-grade math scores by 9 points nationally, with Black and Hispanic students showing gains of 14 and 16 points respectively, narrowing the achievement gap by 8-10 points during the NCLB era.",
            "Analysis by the Brookings Institution of the same NAEP data notes that the rate of improvement actually slowed during NCLB compared to the pre-NCLB period of 1996-2002, that reading scores showed no significant gains, that gains were concentrated in low-stakes 4th-grade assessments, and that 12th-grade scores remained flat, suggesting the improvements reflected test preparation rather than genuine learning."
        ],
        "expected_mode": "disputed",
        "description": "Same NAEP test data interpreted as evidence that NCLB narrowed gaps or merely produced test-prep artifacts.",
        "rationale": "The raw NAEP data shows 11-point math gains and gap narrowing, but reanalysis of the same data shows gains slowed relative to pre-NCLB trends, were absent in reading, and did not reach 12th grade -- identical data supporting opposite conclusions about policy effectiveness."
    })

    # 700 - education
    cases.append({
        "id": "t1_dispute_hard_700",
        "difficulty": "hard",
        "subcategory": "interpretation_conflict",
        "query": "Do charter schools outperform traditional public schools?",
        "contexts": [
            "Stanford University's CREDO 2023 national study of 2.7 million charter school students found they gained the equivalent of 16 additional days of learning in reading and 6 days in math per year compared to matched peers in traditional public schools, with urban charter students gaining 40 additional reading days.",
            "The National Education Policy Center at the University of Colorado reviewed the same CREDO data and argued that 16 extra days (4% of the school year) is educationally negligible, that the matching methodology fails to account for selection bias from motivated families, that 37% of charters performed worse than traditional schools, and that the urban gains are driven by a handful of high-performing networks like KIPP and Success Academy that serve only 3% of charter students."
        ],
        "expected_mode": "disputed",
        "description": "Same CREDO dataset interpreted as demonstrating charter school superiority or as showing negligible, uneven results.",
        "rationale": "CREDO's data shows 16 extra learning days for charter students, but reinterpretation of the same data frames this as a trivial 4% difference driven by selection bias and a few elite networks, with 37% of charters actually underperforming -- identical data, opposite policy conclusions."
    })

    # 701 - politics
    cases.append({
        "id": "t1_dispute_hard_701",
        "difficulty": "hard",
        "subcategory": "interpretation_conflict",
        "query": "Did immigration increase or decrease crime rates in the United States in the 2010s?",
        "contexts": [
            "FBI Uniform Crime Report data shows that between 2010 and 2020, the foreign-born population in the United States increased by 4.3 million while violent crime rates fell 15% and property crime rates fell 25%, consistent with peer-reviewed studies finding immigrants commit crimes at lower rates than native-born citizens.",
            "The Federation for American Immigration Reform analyzed the same FBI crime data alongside ICE enforcement records and found that non-citizen arrests for drug offenses increased 42%, that border counties experienced a 17% increase in aggravated assaults, and that the decline in national crime rates was driven by demographic and policing changes unrelated to immigration patterns."
        ],
        "expected_mode": "disputed",
        "description": "Same FBI crime data interpreted as showing immigration reduces crime or as masking localized crime increases.",
        "rationale": "National FBI data shows crime falling as immigration rose, but disaggregated analysis of the same data highlights rising drug arrests and border county assaults, with the national decline attributed to other factors -- identical datasets supporting opposite conclusions about immigration's effect on crime."
    })

    # 702 - politics
    cases.append({
        "id": "t1_dispute_hard_702",
        "difficulty": "hard",
        "subcategory": "interpretation_conflict",
        "query": "Has remote voting (vote-by-mail) increased election fraud?",
        "contexts": [
            "The Heritage Foundation's election fraud database documents 1,465 proven cases of voter fraud across the United States since 2000, with mail-in ballot fraud comprising 24% of all cases, and argues this represents a 'significant and growing threat' to election integrity as mail voting expanded after 2020.",
            "The Brennan Center for Justice analyzed the same Heritage database and noted that 1,465 cases across 24 years and billions of ballots cast represents a fraud rate of 0.00006%, that mail ballot fraud declined from 0.00004% to 0.00003% even as mail voting doubled between 2016 and 2022, and characterized the fraud threat as 'infinitesimally rare and declining.'"
        ],
        "expected_mode": "disputed",
        "description": "Same Heritage fraud database interpreted as showing a growing threat or as proof that fraud is vanishingly rare.",
        "rationale": "Heritage presents 1,465 cases and 24% mail-ballot share as a significant threat, while Brennan Center takes the same 1,465 cases and divides by billions of ballots to get 0.00006%, framing it as negligible -- identical data, opposite conclusions about the severity of mail voting fraud."
    })

    # =========================================================================
    # 5. scientific_replication (10 cases, IDs 703-712) -- NEW subcategory
    #    Studies with conflicting results on the same research question
    #    Domain spread: 3 health/medicine, 3 psychology, 2 nutrition, 2 environmental science
    # =========================================================================

    # 703 - health/medicine
    cases.append({
        "id": "t1_dispute_hard_703",
        "difficulty": "hard",
        "subcategory": "scientific_replication",
        "query": "Does intermittent fasting improve cognitive function?",
        "contexts": [
            "A 2022 randomized controlled trial at Johns Hopkins University enrolled 200 adults aged 55-75 in a 16:8 intermittent fasting protocol and found that working memory scores improved by 15% and executive function by 11% over 12 weeks compared to controls eating regular meals.",
            "A 2024 pre-registered replication study at the University of Sydney with 500 participants aged 55-75 using the identical 16:8 protocol and cognitive battery found no significant difference in working memory (p=0.71) or executive function (p=0.43) between fasting and control groups over 16 weeks."
        ],
        "expected_mode": "disputed",
        "description": "A well-powered replication study failed to reproduce cognitive benefits of intermittent fasting found in the original trial.",
        "rationale": "The Johns Hopkins trial found 15% working memory improvement with intermittent fasting, but the larger Sydney replication with identical protocol found no effect (p=0.71) -- a direct replication failure on the same research question."
    })

    # 704 - health/medicine
    cases.append({
        "id": "t1_dispute_hard_704",
        "difficulty": "hard",
        "subcategory": "scientific_replication",
        "query": "Does vitamin D supplementation reduce the risk of respiratory infections?",
        "contexts": [
            "A 2017 meta-analysis in the BMJ pooling 25 randomized controlled trials with 11,321 participants found that vitamin D supplementation reduced the risk of acute respiratory infections by 12% overall and by 70% in participants with severe deficiency (serum levels below 25 nmol/L).",
            "The VITAL randomized trial published in the BMJ in 2022, enrolling 25,871 participants over 5 years, found no significant reduction in respiratory infections with 2,000 IU daily vitamin D supplementation (HR 0.97, 95% CI 0.93-1.01), including in the subgroup with baseline deficiency."
        ],
        "expected_mode": "disputed",
        "description": "The largest-ever vitamin D respiratory trial contradicted the meta-analytic finding of protective benefit.",
        "rationale": "The 2017 meta-analysis of 25 trials found a 12% infection reduction (70% in deficient individuals), but the much larger 2022 VITAL trial of 25,871 people found no benefit even in deficient subgroups -- conflicting results from rigorous studies on the same question."
    })

    # 705 - health/medicine
    cases.append({
        "id": "t1_dispute_hard_705",
        "difficulty": "hard",
        "subcategory": "scientific_replication",
        "query": "Do statins reduce mortality in elderly patients without prior heart disease?",
        "contexts": [
            "The PROSPER trial (2002) enrolled 5,804 patients aged 70-82 with cardiovascular risk factors but no prior heart events and found that pravastatin reduced cardiac events by 19% but showed no reduction in all-cause mortality (HR 0.97, p=0.74) over 3.2 years.",
            "A 2020 Australian study (STAREE pilot data) of 1,800 patients aged 70+ without prior cardiovascular disease found that statin use was associated with a 25% reduction in all-cause mortality and a 35% reduction in cardiovascular events over 4.5 years, leading researchers to conclude that statins provide meaningful survival benefit in healthy elderly populations."
        ],
        "expected_mode": "disputed",
        "description": "One trial finds statins reduce cardiac events but not mortality in the elderly, while another finds a significant mortality benefit.",
        "rationale": "PROSPER found no mortality benefit (HR 0.97) for statins in the elderly, while the STAREE pilot data found a 25% mortality reduction in a similar population -- directly conflicting results on whether statins extend life in healthy older adults."
    })

    # 706 - psychology
    cases.append({
        "id": "t1_dispute_hard_706",
        "difficulty": "hard",
        "subcategory": "scientific_replication",
        "query": "Does power posing increase confidence and testosterone levels?",
        "contexts": [
            "The original 2010 study by Amy Cuddy and colleagues at Harvard, published in Psychological Science, found that holding expansive 'power poses' for two minutes increased testosterone by 20%, decreased cortisol by 25%, and increased self-reported feelings of power and willingness to take risks in a sample of 42 participants.",
            "A 2017 pre-registered replication by Ranehill et al. published in Psychological Science with 200 participants found no significant effect of power posing on testosterone (p=0.49), cortisol (p=0.35), or risk-taking behavior, and a 2018 P-curve analysis by Simmons and Simonsohn concluded the original study's results were likely false positives driven by researcher degrees of freedom."
        ],
        "expected_mode": "disputed",
        "description": "The famous power posing study's hormonal findings failed to replicate in a larger pre-registered study.",
        "rationale": "Cuddy's 2010 study found 20% testosterone increase from power posing, but the 2017 replication with 5x the sample found no hormonal effects (p=0.49) and a P-curve analysis suggested the original was a false positive -- a high-profile replication failure."
    })

    # 707 - psychology
    cases.append({
        "id": "t1_dispute_hard_707",
        "difficulty": "hard",
        "subcategory": "scientific_replication",
        "query": "Does the marshmallow test predict long-term life outcomes?",
        "contexts": [
            "Walter Mischel's original 1972 marshmallow test and subsequent follow-ups through 2011 found that children who delayed gratification at age 4 had SAT scores 210 points higher, lower BMI, lower divorce rates, and higher educational attainment decades later, suggesting that early self-control is a powerful predictor of life success.",
            "A 2018 conceptual replication by Watts, Duncan, and Quan published in Psychological Science tested 918 children (10x the original sample) and found that the marshmallow test's predictive power dropped by over 50% when controlling for the child's family socioeconomic status and home environment, and became statistically insignificant for most outcomes when maternal education was included as a covariate."
        ],
        "expected_mode": "disputed",
        "description": "The iconic marshmallow test's predictive power was substantially diminished when a larger study controlled for socioeconomic factors.",
        "rationale": "Mischel's studies found a strong link between childhood delay of gratification and life success, but Watts et al. showed the effect dropped 50%+ and became non-significant when controlling for SES -- conflicting conclusions about whether self-control or socioeconomic background drives outcomes."
    })

    # 708 - psychology
    cases.append({
        "id": "t1_dispute_hard_708",
        "difficulty": "hard",
        "subcategory": "scientific_replication",
        "query": "Does unconscious priming influence complex behavior?",
        "contexts": [
            "John Bargh's famous 1996 experiment published in the Journal of Personality and Social Psychology found that participants primed with elderly-related words (Florida, bingo, wrinkle) walked significantly more slowly down a hallway afterward, demonstrating that unconscious semantic priming can influence complex motor behavior.",
            "Doyen et al.'s 2012 direct replication published in PLOS ONE with 120 participants found no effect of elderly priming on walking speed when experimenter expectations were controlled using a double-blind protocol, suggesting the original result was driven by experimenter expectancy effects rather than unconscious priming."
        ],
        "expected_mode": "disputed",
        "description": "The landmark elderly priming study failed to replicate when experimenter expectancy effects were controlled.",
        "rationale": "Bargh's 1996 study found elderly-word priming slowed walking speed, but Doyen et al.'s double-blind replication found no effect, attributing the original finding to unblinded experimenters unconsciously influencing participant behavior -- conflicting results on unconscious behavioral priming."
    })

    # 709 - nutrition
    cases.append({
        "id": "t1_dispute_hard_709",
        "difficulty": "hard",
        "subcategory": "scientific_replication",
        "query": "Do artificial sweeteners cause weight gain?",
        "contexts": [
            "A 2023 WHO-commissioned systematic review of 56 studies found that long-term use of non-sugar sweeteners was associated with a 76% increased risk of type 2 diabetes, increased BMI, and higher cardiovascular mortality, leading the WHO to recommend against their use for weight control.",
            "A 2024 randomized controlled trial published in the New England Journal of Medicine, following 1,548 overweight adults for 2 years, found that replacing sugary drinks with artificially sweetened alternatives resulted in 5.3 kg average weight loss, improved insulin sensitivity, and no increase in metabolic disease markers, and criticized the WHO review for relying heavily on observational data subject to reverse causation."
        ],
        "expected_mode": "disputed",
        "description": "A WHO review links artificial sweeteners to weight gain and diabetes while a large RCT shows they aid weight loss.",
        "rationale": "The WHO review of 56 studies finds 76% increased diabetes risk with artificial sweeteners, but a 2-year RCT of 1,548 adults finds 5.3 kg weight loss and improved insulin sensitivity -- conflicting evidence likely due to the difference between observational and experimental study designs."
    })

    # 710 - nutrition
    cases.append({
        "id": "t1_dispute_hard_710",
        "difficulty": "hard",
        "subcategory": "scientific_replication",
        "query": "Does eating red meat increase cancer risk?",
        "contexts": [
            "The International Agency for Research on Cancer (IARC), part of the WHO, classified processed meat as a Group 1 carcinogen and red meat as a Group 2A probable carcinogen in 2015, based on a review of 800 epidemiological studies finding that 50g of processed meat daily increases colorectal cancer risk by 18%.",
            "The NutriRECS consortium published a 2019 systematic review in the Annals of Internal Medicine covering 61 studies with 4 million participants and concluded that the evidence linking red and processed meat to cancer is 'low-certainty,' that the absolute risk increase is 'very small' (7 fewer cancer cases per 1,000 people with reduced consumption), and recommended that adults continue current meat consumption levels."
        ],
        "expected_mode": "disputed",
        "description": "IARC classifies red meat as a probable carcinogen while NutriRECS says the evidence is low-certainty and the risk is trivial.",
        "rationale": "IARC reviewed 800 studies and classified processed meat as a definite carcinogen, but NutriRECS reviewed 61 studies with 4M participants and called the evidence 'low-certainty' with negligible absolute risk -- same research question, opposing conclusions and dietary recommendations."
    })

    # 711 - environmental science
    cases.append({
        "id": "t1_dispute_hard_711",
        "difficulty": "hard",
        "subcategory": "scientific_replication",
        "query": "Are microplastics in drinking water harmful to human health?",
        "contexts": [
            "A 2024 study published in the New England Journal of Medicine analyzed carotid artery plaques from 312 patients and found that patients with detectable microplastics in their plaques had a 4.5-fold increased risk of heart attack, stroke, or death over 34 months, providing the first direct evidence linking microplastics to cardiovascular disease in humans.",
            "The WHO's 2023 systematic review of microplastics in drinking water concluded that current levels of microplastic exposure through drinking water 'do not appear to pose a health risk' based on available toxicological evidence, that the concentrations found in tap water are orders of magnitude below levels shown to cause harm in animal studies, and that there is 'no evidence of human health concern' at current exposure levels."
        ],
        "expected_mode": "disputed",
        "description": "A NEJM study links microplastics to cardiovascular death while a WHO review says current exposures pose no health risk.",
        "rationale": "The NEJM study found 4.5x increased cardiovascular mortality in patients with microplastics in arterial plaques, but the WHO concluded microplastics in drinking water pose no health risk at current levels -- directly conflicting assessments of microplastic danger to humans."
    })

    # 712 - environmental science
    cases.append({
        "id": "t1_dispute_hard_712",
        "difficulty": "hard",
        "subcategory": "scientific_replication",
        "query": "Is ocean acidification killing coral reefs?",
        "contexts": [
            "A 2020 study in Nature Climate Change measuring carbonate chemistry across 22 reef systems found that ocean pH has decreased by 0.1 units since pre-industrial times, causing a 30% reduction in coral calcification rates, and projected that 70% of tropical reefs would experience net dissolution by 2050 under current emission trends.",
            "A 2023 field study published in Science examined coral communities near natural CO2 seeps in Papua New Guinea where pH levels already match 2100 projections, and found thriving coral communities with 85% cover, diverse species composition, and normal calcification rates, suggesting that many reef species can adapt to acidified conditions over generational timescales."
        ],
        "expected_mode": "disputed",
        "description": "One study predicts acidification will dissolve 70% of reefs by 2050 while field observations show reefs thriving at projected pH levels.",
        "rationale": "The 2020 Nature study projects catastrophic reef dissolution from acidification, but the 2023 Science field study finds thriving reefs at even lower pH levels near CO2 seeps -- directly conflicting predictions about coral survival under ocean acidification."
    })

    # =========================================================================
    # 6. numerical_conflict (5 cases, IDs 713-717) -- SINGLE SOURCE
    #    Domain spread: 1 science, 1 finance, 1 sports, 1 tech, 1 history
    # =========================================================================

    # 713 - science
    cases.append({
        "id": "t1_dispute_hard_713",
        "difficulty": "hard",
        "subcategory": "numerical_conflict",
        "query": "How much has global sea level risen since 1900?",
        "contexts": [
            "The IPCC Sixth Assessment Report (2021) states that global mean sea level rose approximately 20 centimeters (0.20 meters) between 1901 and 2018, based on tide gauge records and satellite altimetry data.",
            "A 2023 study by researchers at the University of Siegen published in Nature Communications, using revised satellite calibrations and updated tide gauge corrections, estimates that global sea level rise since 1900 was approximately 28 centimeters (0.28 meters), noting that the IPCC figure underestimates acceleration in recent decades."
        ],
        "expected_mode": "disputed",
        "description": "Two authoritative sources disagree on total sea level rise since 1900 by a 40% margin.",
        "rationale": "The IPCC reports 20 cm of sea level rise since 1900, while the 2023 Nature Communications study estimates 28 cm using revised calibrations -- a 40% discrepancy on the same physical measurement, with significant implications for projections."
    })

    # 714 - finance
    cases.append({
        "id": "t1_dispute_hard_714",
        "difficulty": "hard",
        "subcategory": "numerical_conflict",
        "query": "What is the average annual return of the S&P 500?",
        "contexts": [
            "Vanguard's 2024 investor education materials state that the S&P 500 has delivered an average annual return of 10.3% since its inception in 1957, using arithmetic mean total returns including dividends.",
            "Professor Robert Shiller's dataset at Yale, widely used in academic research, reports the S&P 500's compound annual growth rate (CAGR) as 7.0% in real terms (inflation-adjusted) since 1957, or approximately 10.1% nominal, but notes that the geometric mean (actual investor experience) is 9.4% nominal due to the difference between arithmetic and geometric averaging."
        ],
        "expected_mode": "disputed",
        "description": "Reported S&P 500 average returns range from 7.0% to 10.3% depending on methodology and inflation adjustment.",
        "rationale": "Vanguard reports 10.3% using arithmetic mean nominal returns, Shiller reports 7.0% real or 9.4% geometric nominal -- the 'average return' differs by up to 47% depending on whether you use arithmetic vs. geometric mean and nominal vs. real values."
    })

    # 715 - sports
    cases.append({
        "id": "t1_dispute_hard_715",
        "difficulty": "hard",
        "subcategory": "numerical_conflict",
        "query": "How many concussions occur in the NFL each season?",
        "contexts": [
            "The NFL's official 2023 injury report stated that there were 174 diagnosed concussions during the regular season and postseason combined, representing a 10% decline from the previous year, attributing the improvement to enhanced helmet safety standards and updated tackling protocols.",
            "A 2024 independent analysis by Boston University's CTE Center, using sideline video review, undiagnosed symptom data from player surveys, and post-career neurological assessments, estimated that the actual concussion count for the same 2023 season was between 450 and 600, noting that approximately 60% of concussions go unreported due to player reluctance, inadequate sideline screening, and the league's Return to Play protocol incentivizing underreporting."
        ],
        "expected_mode": "disputed",
        "description": "The NFL reports 174 concussions while an independent analysis estimates 450-600 for the same season.",
        "rationale": "The NFL's official count of 174 concussions is 2.5-3.5x lower than Boston University's estimate of 450-600, representing a fundamental disagreement about the true injury rate with significant player safety implications."
    })

    # 716 - tech
    cases.append({
        "id": "t1_dispute_hard_716",
        "difficulty": "hard",
        "subcategory": "numerical_conflict",
        "query": "How much energy does Bitcoin mining consume annually?",
        "contexts": [
            "The Cambridge Centre for Alternative Finance's Bitcoin Electricity Consumption Index estimated Bitcoin's annual energy consumption at 95.5 terawatt-hours (TWh) as of December 2023, roughly equivalent to the energy consumption of the Philippines.",
            "The Bitcoin Mining Council's Q4 2023 survey of its members, who represent 48% of the global Bitcoin mining network, extrapolated total network consumption at 63.5 TWh annually, noting that 58.9% of mining energy comes from sustainable sources and that the Cambridge model overestimates consumption by using outdated hardware efficiency assumptions."
        ],
        "expected_mode": "disputed",
        "description": "Two tracking organizations report Bitcoin energy consumption figures differing by 50%.",
        "rationale": "Cambridge estimates Bitcoin uses 95.5 TWh annually while the Bitcoin Mining Council estimates 63.5 TWh -- a 50% disagreement on the same metric, driven by different hardware efficiency assumptions and methodological approaches."
    })

    # 717 - history
    cases.append({
        "id": "t1_dispute_hard_717",
        "difficulty": "hard",
        "subcategory": "numerical_conflict",
        "query": "How many people died in the Bengal famine of 1943?",
        "contexts": [
            "The official Famine Inquiry Commission report published in 1945 by the British colonial government estimated that 1.5 million people died in the Bengal famine of 1943, attributing the cause primarily to natural crop failure from a cyclone and flooding, with wartime disruptions as a secondary factor.",
            "Nobel laureate economist Amartya Sen's research, published in his 1981 book 'Poverty and Famines,' estimated the death toll at approximately 3 million people, based on demographic analysis of excess mortality data, and attributed the famine primarily to wartime policy failures including rice exports, military requisitioning, and denial of food imports by the British War Cabinet."
        ],
        "expected_mode": "disputed",
        "description": "The official colonial report and Nobel laureate research disagree on the Bengal famine death toll by a factor of two.",
        "rationale": "The British commission reported 1.5 million deaths blaming natural causes, while Sen estimated 3 million using demographic data and blamed colonial policy -- a 2x discrepancy in death toll with fundamentally different causal attributions."
    })

    return cases


def main():
    cases = build_cases()
    assert len(cases) == 50, f"Expected 50 cases, got {len(cases)}"

    # Validate IDs are sequential 668-717
    expected_ids = [f"t1_dispute_hard_{i}" for i in range(668, 718)]
    actual_ids = [c["id"] for c in cases]
    assert actual_ids == expected_ids, f"ID mismatch: expected {expected_ids[0]}..{expected_ids[-1]}, got {actual_ids[0]}..{actual_ids[-1]}"

    # Validate all cases have required fields
    required_fields = {"id", "difficulty", "subcategory", "query", "contexts", "expected_mode", "description", "rationale"}
    for case in cases:
        missing = required_fields - set(case.keys())
        assert not missing, f"Case {case['id']} missing fields: {missing}"
        assert case["difficulty"] == "hard"
        assert case["expected_mode"] == "disputed"
        assert len(case["contexts"]) >= 2
        # Multi-source cases must have context_sources matching contexts length
        if "context_sources" in case:
            assert len(case["context_sources"]) == len(case["contexts"]), (
                f"Case {case['id']}: context_sources length {len(case['context_sources'])} "
                f"does not match contexts length {len(case['contexts'])}"
            )

    # Validate subcategory distribution
    from collections import Counter
    subcats = Counter(c["subcategory"] for c in cases)
    assert subcats["temporal_source_conflict"] == 10, f"temporal_source_conflict: {subcats['temporal_source_conflict']}"
    assert subcats["implicit_contradiction"] == 5, f"implicit_contradiction: {subcats['implicit_contradiction']}"
    assert subcats["binary_conflict"] == 10, f"binary_conflict: {subcats['binary_conflict']}"
    assert subcats["interpretation_conflict"] == 10, f"interpretation_conflict: {subcats['interpretation_conflict']}"
    assert subcats["scientific_replication"] == 10, f"scientific_replication: {subcats['scientific_replication']}"
    assert subcats["numerical_conflict"] == 5, f"numerical_conflict: {subcats['numerical_conflict']}"

    # Validate all temporal_source_conflict cases have context_sources
    for case in cases:
        if case["subcategory"] == "temporal_source_conflict":
            assert "context_sources" in case, f"Case {case['id']} is temporal_source_conflict but missing context_sources"

    output = {"cases": cases}

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(cases)} cases")
    print(f"Output: {OUTPUT_PATH}")
    print(f"Subcategory distribution: {dict(subcats)}")
    print("All validations passed.")


if __name__ == "__main__":
    main()
