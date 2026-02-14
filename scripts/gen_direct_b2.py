"""
Generate 91 new trustworthy_direct cases (batch 2) and append to trustworthy_direct.json.

Batch 2 IDs:
  - t1_confident_hard_962 through t1_confident_hard_1007 (46 hard)
  - t1_confident_medium_955 through t1_confident_medium_999 (45 medium)

Constraints:
  - 14 subcategories, counts sum to 91
  - 18 domains, max 7 per domain
  - Query type: what<=23, how>=18, is/does>=18, why/should>=10, when/who/which>=8
  - 20+ multi_source cases (all multi_source_convergence + others)
  - Contexts 150-400 chars each (use 2 contexts to split content)
"""

import json
import os

DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data", "tier1_core", "trustworthy_direct.json"
)


def base(id_, difficulty, subcategory, query, contexts, description, rationale,
         domain, query_type, source_type, reasoning_type,
         context_sources=None):
    """Build a single case dict."""
    case = {
        "id": id_,
        "difficulty": difficulty,
        "subcategory": subcategory,
        "query": query,
        "contexts": contexts,
        "expected_mode": "trustworthy",
        "description": description,
        "rationale": rationale,
        "domain": domain,
        "query_type": query_type,
        "source_type": source_type,
        "context_count": len(contexts),
        "reasoning_type": reasoning_type,
        "evidence_pattern": "direct",
        "category": "trustworthy_direct",
        "evaluation_config": {"mode": "governance", "check_mode_match": True},
    }
    if source_type == "multi_source" and context_sources:
        case["context_sources"] = context_sources
    return case


def build_cases():
    cases = []
    h = 962

    # ==== HARD CASES (46 total) ====

    # --- technical_documented: 4 hard ---
    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "technical_documented",
        "How does the Linux CFS scheduler allocate CPU time among processes?",
        ["CFS uses a red-black tree to track each task's virtual runtime. Tasks with the smallest vruntime run next, distributing CPU proportionally to task weight from nice values.",
         "CFS replaced the O(1) scheduler in Linux 2.6.23 and achieves O(log N) decisions. Proportional sharing ensures fairness without starvation."],
        "CFS scheduling algorithm with data structure details",
        "Both contexts detail vruntime mechanism, data structure, and complexity",
        "technology", "how", "single", "factual"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "technical_documented",
        "How does galvanic corrosion occur between dissimilar metals in contact?",
        ["When two dissimilar metals connect in an electrolyte, the more negative metal (anode) oxidizes, releasing electrons to the nobler metal (cathode).",
         "Corrosion rate depends on galvanic series potential difference, cathode-to-anode area ratio, and electrolyte conductivity. Large cathode area with small anode accelerates attack dramatically."],
        "Galvanic corrosion electrochemistry with rate factors",
        "Contexts describe anode-cathode mechanism and three rate variables",
        "science", "how", "single", "causal"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "technical_documented",
        "How does HTTPS certificate pinning protect mobile apps from man-in-the-middle attacks?",
        ["Certificate pinning embeds the expected server cert hash in the app. During TLS handshake, the app compares the server cert against the pinned value instead of using the device trust store.",
         "Attackers with compromised CAs or rogue root certificates cannot intercept traffic because the pinned hash won't match. Android uses network_security_config.xml for implementation."],
        "Certificate pinning mechanism in mobile apps",
        "Contexts detail pinning verification and how it defeats rogue CA attacks",
        "technology", "how", "single", "factual"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "technical_documented",
        "Is single-mode fiber at 1310 nm capable of reaching 40 km without regeneration?",
        ["Yes. Single-mode OS2 fiber at 1310 nm has 0.35 dB/km attenuation, enabling about 40 km. At 1550 nm attenuation drops to 0.2 dB/km, reaching roughly 80 km.",
         "These assume ITU-T G.652 fiber. Practical deployments add 3-5 dB overhead for connectors, splices, and bends, reducing effective reach somewhat."],
        "Fiber optic transmission specs at specific wavelengths",
        "Contexts provide attenuation figures, distances, and practical overhead",
        "technology", "is", "single", "factual"
    )); h += 1

    # --- clear_explanation: 4 hard ---
    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "clear_explanation",
        "Why do farmers rotate crops between legumes and cereals?",
        ["Legumes host Rhizobium bacteria in root nodules that fix atmospheric N2, enriching soil with 40-200 kg nitrogen per hectare depending on species.",
         "The following cereal crop benefits from residual nitrogen, cutting fertilizer needs 30-50%. Rotation also breaks pest and disease cycles specific to each crop family."],
        "Nitrogen fixation explanation for legume-cereal rotation",
        "Contexts explain Rhizobium symbiosis, quantify nitrogen, and identify pest benefits",
        "agriculture", "why", "single", "causal"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "clear_explanation",
        "How does CBT-I treat insomnia compared to medication?",
        ["CBT-I uses sleep restriction to limit bed time, stimulus control to re-associate bed with sleep, and cognitive restructuring to challenge catastrophic beliefs about sleep loss.",
         "Meta-analyses show CBT-I improvements last 12+ months after treatment. Medication benefits cease on discontinuation and carry tolerance and dependence risks."],
        "CBT-I mechanisms versus pharmacological approaches",
        "Contexts detail three components and contrast durability with medication",
        "psychology", "how", "single", "comparative"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "clear_explanation",
        "Why does the Electoral College sometimes produce a popular-vote loser as president?",
        ["Small states get proportionally more electors per capita. Forty-eight states use winner-take-all, giving all electors to the narrow winner of each state.",
         "A candidate can pile up huge margins in some states while narrowly winning enough others to reach 270. This occurred in 2000 (Bush) and 2016 (Trump)."],
        "Structural explanation of Electoral College popular-vote splits",
        "Contexts identify overrepresentation and winner-take-all as key factors",
        "government", "why", "single", "causal"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "clear_explanation",
        "How does an appraisal contingency protect homebuyers?",
        ["It lets buyers renegotiate or exit without losing earnest money if the appraised value falls below the purchase price. The lender orders an independent appraisal of comparable sales and condition.",
         "If low, the buyer can request a price cut or walk away. Without the clause, the buyer must cover the gap in cash because lenders won't finance above appraised value."],
        "Appraisal contingency mechanics in real estate",
        "Contexts explain the process flow and financial risk mitigation",
        "real_estate", "how", "single", "factual"
    )); h += 1

    # --- contradiction_resolved: 4 hard ---
    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "contradiction_resolved",
        "Is saturated fat directly linked to heart disease despite recent contrary studies?",
        ["Keys' Seven Countries Study found strong saturated fat-CVD correlation, but 2010-2020 meta-analyses found weak associations when controlling for replacement nutrients.",
         "The 2023 AHA Presidential Advisory resolved it: replacing saturated fat with polyunsaturated fat cuts CVD risk by 25%, but replacing it with refined carbs shows no benefit. Both sets of findings are correct for different dietary substitution patterns."],
        "Saturated fat debate resolved via substitution analysis",
        "Both historical observational data and AHA advisory converge on substitution-dependent effects",
        "medicine", "is", "multi_source", "evaluative",
        [{"source_id": "keys_seven_countries", "source_type": "academic", "authority": "primary"},
         {"source_id": "aha_advisory_2023", "source_type": "industry", "authority": "expert"}]
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "contradiction_resolved",
        "Does social media cause depression in teenagers?",
        ["Cross-sectional studies correlated heavy use with depressive symptoms, but screen-time experiments showed inconsistent effects.",
         "JCPP 2024 longitudinal data resolved it: passive scrolling predicts depression (OR 1.33) while active engagement is slightly protective (OR 0.91). The pathway is usage-pattern-specific, not blanket."],
        "Social media depression debate resolved via usage patterns",
        "Contexts explain passive vs active distinction that resolves conflicting findings",
        "social_media", "does", "single", "causal"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "contradiction_resolved",
        "Does raising the minimum wage cause job losses given some studies show employment gains?",
        ["Classical economics predicted wage floors above equilibrium reduce jobs. But Card and Krueger's 1994 study of New Jersey fast food workers found no negative employment effects after a state minimum wage increase.",
         "Monopsony models resolved the contradiction: where few employers set wages, moderate increases can boost employment. CBO 2024 estimates a $15 federal minimum raises pay for 17M workers while reducing 1.4M jobs -- effects are real but context-dependent."],
        "Minimum wage debate resolved via monopsony theory",
        "Contexts show how monopsony models reconcile theory with empirics",
        "government", "does", "single", "causal"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "contradiction_resolved",
        "Is organic food more nutritious than conventional despite conflicting studies?",
        ["Stanford (2012) found no nutritional advantage. BJN (2014) found 18-69% higher antioxidant polyphenols in organic crops.",
         "Resolution: Stanford measured macronutrients (minimal differences). BJN measured secondary metabolites that organic plants overproduce as pest defenses. Both correct for different nutrient categories."],
        "Organic nutrition debate resolved via nutrient category distinction",
        "Contexts explain how measurement targets produced contradictory conclusions",
        "food", "is", "single", "comparative"
    )); h += 1

    # --- opposing_with_consensus: 4 hard ---
    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "opposing_with_consensus",
        "Is nuclear power safe despite high-profile accidents like Chernobyl and Fukushima?",
        ["Per TWh, nuclear causes 0.03 deaths vs coal 24.6 and gas 2.8, according to Our World in Data's analysis of historical energy mortality. WHO and UNSCEAR conclude Fukushima's cancer impact will be statistically undetectable.",
         "The World Nuclear Association's 2024 safety review confirms Gen III+ reactor designs use passive safety systems making Chernobyl-type events physically impossible via laws of physics rather than operator intervention."],
        "Nuclear safety confirmed by mortality data and industry assessment",
        "Both energy mortality analysis and nuclear industry review confirm safety record",
        "science", "is", "multi_source", "evaluative",
        [{"source_id": "owid_energy_mortality", "source_type": "academic", "authority": "primary"},
         {"source_id": "wna_safety_review_2024", "source_type": "industry", "authority": "expert"}]
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "opposing_with_consensus",
        "Should employers use Myers-Briggs (MBTI) for hiring decisions?",
        ["MBTI has test-retest reliability of only 50% over five weeks. APA and SIOP both recommend against using it for personnel selection.",
         "The Big Five model shows predictive validity for job performance (r=0.22-0.27) and is the validated alternative for personality assessment in hiring."],
        "Professional consensus against MBTI for hiring",
        "Contexts present reliability problems and the validated alternative",
        "hr_workplace", "should", "single", "evaluative"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "opposing_with_consensus",
        "Is homework beneficial for elementary school students?",
        ["Cooper's meta-analysis (updated 2023) found near-zero correlation between homework and achievement for grades K-5. Effects emerge in middle school, strengthen in high school.",
         "NEA and PTA recommend the '10-minute rule' per grade level. Excessive elementary homework can reduce motivation without measurable academic benefit."],
        "Research consensus on homework effectiveness by grade",
        "Contexts quantify the near-zero elementary effect and cite guidelines",
        "education", "is", "single", "evaluative"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "opposing_with_consensus",
        "Does fluoride in drinking water pose health risks despite dental benefits?",
        ["USPHS recommends 0.7 mg/L; CDC, ADA, and WHO endorse this. Community fluoridation at this level reduces tooth decay by approximately 25%.",
         "NAS (2020) found no adverse effects at 0.7 mg/L. Dental fluorosis begins above 2.0 mg/L; skeletal fluorosis above 4.0 mg/L -- nearly six times the recommended concentration."],
        "Fluoride safety consensus at recommended levels",
        "Contexts distinguish safe vs harmful concentrations with authority citations",
        "environment", "does", "single", "evaluative"
    )); h += 1

    # --- different_framing: 4 hard ---
    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "different_framing",
        "How does property tax assessment differ from a home's market value?",
        ["Assessors use mass appraisal: lot size, square footage, materials, age, comparable sales. But caps like CA Prop 13 (2%/year increase limit) create divergence from market value.",
         "Assessment cycles lag markets 1-5 years, and standardized depreciation ignores renovations. Assessed values average 80-90% of market value nationally."],
        "Property tax assessment vs market value distinction",
        "Contexts identify assessment methods and three divergence reasons",
        "real_estate", "how", "single", "factual"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "different_framing",
        "How do clinicians distinguish normal grief from clinical depression?",
        ["DSM-5-TR (2022) removed the bereavement exclusion. Grief has waves of sadness with positive memories, preserved self-esteem, and gradual symptom reduction.",
         "Depression shows persistent depressed mood, worthlessness, inability to feel pleasure, and lasting impairment. Clinicians may diagnose both concurrently when grief meets full MDD criteria."],
        "Grief vs depression clinical distinction",
        "Contexts contrast symptom patterns using current diagnostic criteria",
        "psychology", "how", "single", "comparative"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "different_framing",
        "How does a traditional 401(k) differ from a Roth 401(k)?",
        ["Traditional: pre-tax contributions reduce current income; all withdrawals taxed as income. Roth: after-tax with no current deduction; qualified withdrawals entirely tax-free.",
         "Both share the 2024 $23,000 limit ($30,500 if 50+). Employer matches always go pre-tax. Choose based on whether your tax rate will be higher (Roth) or lower (traditional) in retirement."],
        "Traditional vs Roth 401(k) tax treatment comparison",
        "Contexts detail contribution mechanics and decision framework",
        "finance", "how", "single", "comparative"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "different_framing",
        "Which New Deal programs were temporary relief versus permanent institutional reforms?",
        ["Temporary: CCC (1933-42, 3M workers), WPA (1935-43, 8.5M employed), FERA (1933-35, $3.1B in direct aid). These ended when the crisis passed.",
         "Permanent (still operating): Social Security (1935), SEC (1934), FDIC (1933), NLRB (1935), Fair Labor Standards Act (1938). This distinction explains why some say the New Deal 'ended' while its institutions persist."],
        "New Deal programs classified as temporary vs permanent",
        "Contexts categorize specific programs by type with dates and scale",
        "history", "which", "single", "factual"
    )); h += 1

    # --- quantitative_answer: 3 hard ---
    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "quantitative_answer",
        "How much water does producing one pound of beef require compared to chicken?",
        ["Per the Water Footprint Network, one pound of beef needs about 1,847 gallons (feed irrigation + drinking + processing). One pound of chicken needs about 518 gallons.",
         "The 3.6:1 ratio reflects cattle's 18-24 month growth cycle vs 6-8 weeks for broilers, lower feed conversion (6-8 lbs/lb vs 1.8-2.0), and water-intensive feed crops like alfalfa."],
        "Water footprint comparison: beef vs chicken",
        "Contexts provide gallon figures and explain the ratio via biological factors",
        "agriculture", "how", "single", "comparative"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "quantitative_answer",
        "Is most of Earth's fresh water actually accessible for human use?",
        ["No. Of 1.386 billion km3 total water, only 2.5% is fresh. Of that, 68.7% is glaciers, 30.1% is deep groundwater, and just 1.2% is surface or atmospheric water -- roughly 0.03% of total water is readily accessible.",
         "USGS estimates accessible renewable fresh water at 42,700 km3/year. Humanity currently withdraws about 4,000 km3 annually, or 9.4% of the renewable supply, though this is unevenly distributed geographically."],
        "Global fresh water accessibility breakdown",
        "Contexts layer percentages from total to accessible with withdrawal rates",
        "environment", "is", "single", "factual"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "quantitative_answer",
        "How many calories does a person burn during eight hours of sleep?",
        ["Adults burn 50-70 calories/hour during sleep, or 400-560 over eight hours. This supports respiration, circulation, cell repair, and thermoregulation.",
         "A 150-lb person burns roughly 440 calories overnight, a 200-lb person about 580. Sleep metabolic rate is 5-10% below waking basal rate due to lower muscle tone and temperature."],
        "Sleep calorie expenditure with weight-based estimates",
        "Contexts provide ranges, weight-specific examples, and physiological basis",
        "sports", "how", "single", "factual"
    )); h += 1

    # --- cross_source_agreement: 3 hard, multi_source ---
    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "cross_source_agreement",
        "What is the average time to hire for US software engineering roles?",
        ["LinkedIn 2024 Talent Insights (800K+ postings) found average time to hire of 44 days from posting to accepted offer, up 6 days from 2022.",
         "Greenhouse 2024 Benchmark (4,000+ companies) reports median 41 days for software roles, with 4.2 interview rounds on average."],
        "Software hiring timeline from two data sources",
        "Both converge on 41-44 days for software engineering roles",
        "hr_workplace", "what", "multi_source", "factual",
        [{"source_id": "linkedin_talent_2024", "source_type": "industry", "authority": "primary"},
         {"source_id": "greenhouse_benchmark_2024", "source_type": "industry", "authority": "primary"}]
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "cross_source_agreement",
        "When was the first successful organ transplant performed?",
        ["December 23, 1954: Dr. Joseph Murray performed a kidney transplant at Peter Bent Brigham Hospital in Boston between identical twins Ronald and Richard Herrick, avoiding rejection.",
         "The Nobel committee's 1990 citation confirms the December 23, 1954 date and notes the recipient survived eight years with normal kidney function."],
        "First organ transplant confirmed by medical history and Nobel records",
        "Both confirm same date, surgeon, and patient details",
        "history", "when", "multi_source", "factual",
        [{"source_id": "brigham_medical_history", "source_type": "academic", "authority": "primary"},
         {"source_id": "nobel_prize_1990", "source_type": "reference", "authority": "official"}]
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "cross_source_agreement",
        "What is the recommended winter wheat seeding rate for the US Great Plains?",
        ["Kansas State Extension recommends 900K-1.2M seeds/acre (60-80 lbs) for dryland Great Plains wheat, higher for late planting, lower for early planting.",
         "USDA-ARS Bushland, TX guidelines say 60-75 lbs/acre, noting rates above 90 lbs showed no yield benefit and added $8-12/acre in seed costs in 2023 trials."],
        "Seeding rates confirmed by two agricultural sources",
        "University extension and USDA research converge on 60-80 lbs/acre",
        "agriculture", "what", "multi_source", "factual",
        [{"source_id": "ksu_extension_wheat_2024", "source_type": "academic", "authority": "primary"},
         {"source_id": "usda_ars_bushland_2023", "source_type": "government", "authority": "official"}]
    )); h += 1

    # --- direct_factual: 3 hard ---
    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "direct_factual",
        "Who was the first woman to serve as Speaker of the US House?",
        ["Nancy Pelosi became the first female Speaker on January 4, 2007, from California's 8th District. She served 2007-2011 and 2019-2023.",
         "The Speaker is second in presidential line of succession after the VP. Pelosi's election was confirmed by a 233-202 House vote."],
        "First female House Speaker with service dates",
        "Contexts directly identify Pelosi with dates and role significance",
        "government", "who", "single", "factual"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "direct_factual",
        "When did the ADA become law, and what does Title I require?",
        ["Signed July 26, 1990. Title I bars employers with 15+ employees from disability discrimination in hiring, promotion, compensation, and training.",
         "Employers must provide reasonable accommodations unless imposing undue hardship. EEOC enforces Title I; it took effect July 1992 for 25+ employers, July 1994 for 15-24."],
        "ADA enactment date and Title I requirements",
        "Contexts provide exact date, threshold, accommodation mandate, and phased timeline",
        "law", "when", "single", "factual"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "direct_factual",
        "What is the boiling point of ethanol at standard pressure?",
        ["Ethanol boils at 78.37 C (173.07 F) at 1 atm. This is below water's 100 C due to ethanol's weaker hydrogen bonding and lower molecular weight (46.07 g/mol).",
         "The low boiling point makes ethanol useful as a solvent in extraction processes and explains its rapid evaporation at room temperature."],
        "Ethanol boiling point with scientific context",
        "Contexts give exact temperature in both scales with molecular explanation",
        "science", "what", "single", "factual"
    )); h += 1

    # --- multi_source_convergence: 3 hard, all multi_source ---
    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "multi_source_convergence",
        "What is the S&P 500's average annual total return over the past 30 years?",
        ["Vanguard 2024 reports the S&P 500 Total Return Index averaged 10.5% annually (1994-2024) including dividends. Real return (CPI-adjusted) was approximately 7.6%.",
         "NYU Stern's Damodaran dataset shows 10.3% annualized total return for 1994-2024, with dividends contributing about 1.8 percentage points."],
        "S&P 500 30-year return confirmed by two sources",
        "Both converge on approximately 10.3-10.5% annualized total return",
        "finance", "what", "multi_source", "factual",
        [{"source_id": "vanguard_analysis_2024", "source_type": "industry", "authority": "primary"},
         {"source_id": "nyu_stern_damodaran", "source_type": "academic", "authority": "primary"}]
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "multi_source_convergence",
        "How many people voted in the 2020 US presidential election?",
        ["The Federal Election Commission certified a total of 158,383,403 votes cast for president across all states and territories, representing a turnout rate of 66.8% of the voting-eligible population.",
         "The US Elections Project (Prof. McDonald) recorded 159,633,396 ballots (including late provisionals), with 66.9% turnout. The slight difference reflects counting timing."],
        "2020 voter turnout confirmed by official and academic sources",
        "Both converge on 158-159 million voters at 66.8-66.9% turnout",
        "history", "how", "multi_source", "factual",
        [{"source_id": "fec_2020_report", "source_type": "government", "authority": "official"},
         {"source_id": "us_elections_project", "source_type": "academic", "authority": "primary"}]
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "multi_source_convergence",
        "What does it cost to raise a child to age 18 in the United States?",
        ["Brookings (2024) estimates $310,605 for a middle-income child born in 2023: housing 29%, food 18%, childcare/education 16%, transportation 15%.",
         "USDA's last official report (2017, adjusted to 2024 dollars) estimated $286K-$324K depending on income, centered at $307K. Figures exclude college costs."],
        "Child-rearing costs from two independent estimates",
        "Brookings and USDA converge on approximately $307-311K for middle-income families",
        "finance", "what", "multi_source", "factual",
        [{"source_id": "brookings_child_cost_2024", "source_type": "academic", "authority": "primary"},
         {"source_id": "usda_child_expenditure", "source_type": "government", "authority": "official"}]
    )); h += 1

    # --- authoritative_source: 3 hard ---
    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "authoritative_source",
        "Which USDA hardiness zones support citrus trees in the continental US?",
        ["Per USDA 2023 map: citrus needs zones 9-11 (min 20 F). Sweet oranges 9b-11 (25 F), lemons 9a-11 (20 F), cold-hardy Satsumas survive zone 8b (15 F).",
         "The 2023 revision shifted 49% of the country to a warmer half-zone versus 2012, slightly expanding potential citrus-growing regions."],
        "USDA citrus hardiness zones with species requirements",
        "Contexts cite the official map with zones and temperatures by species",
        "agriculture", "which", "single", "factual"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "authoritative_source",
        "Why does the Federal Reserve target 2% inflation rather than 0%?",
        ["The FOMC adopted a formal 2% PCE inflation target in 2012. A moderate positive target provides a buffer against deflation, which is harder to reverse, and gives the Fed room to cut real interest rates during recessions since nominal rates cannot go far below zero.",
         "Research by the Brookings Institution and former Fed Chair Bernanke confirmed that 2% balances price stability with labor market flexibility. The December 2024 projections show the Fed estimates a natural unemployment rate of 4.0-4.4% alongside this target."],
        "Fed inflation target rationale from authoritative economic sources",
        "Contexts explain the anti-deflation buffer rationale and current target parameters",
        "general", "why", "single", "causal"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "authoritative_source",
        "How does the FDA approve a new prescription drug?",
        ["Five stages: (1) preclinical tests, (2) IND application, (3) clinical trials: Phase I 20-100 volunteers, Phase II 100-300 patients, Phase III 1,000-3,000 in RCTs.",
         "(4) NDA filed with all data. (5) FDA reviews within 10-month standard or 6-month priority timeline. Median development: 8-12 years, costing $1.3-2.6 billion per Tufts Center."],
        "FDA drug approval stages with timelines",
        "Contexts detail all five stages with numbers and cost estimates",
        "medicine", "how", "single", "procedural"
    )); h += 1

    # --- near_complete_evidence: 3 hard ---
    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "near_complete_evidence",
        "Why did the Great Depression become so severe and prolonged?",
        ["Five reinforcing causes: (1) 1929 crash destroyed $25B in wealth. (2) 9,000+ banks failed 1930-33, wiping out savings. (3) The Fed tightened money during the downturn (documented by Friedman/Schwartz). (4) Smoot-Hawley raised tariffs on 20K goods, cutting global trade 66%.",
         "(5) Dust Bowl devastated agriculture 1930-36. These causes interacted in a deflationary spiral that reduced US GDP by 30% from 1929 to 1933, making the downturn far worse than a typical recession."],
        "Comprehensive Great Depression causes enumeration",
        "Contexts identify five reinforcing causes with specific data for each",
        "history", "why", "single", "causal"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "near_complete_evidence",
        "How does ranked-choice voting work in US elections?",
        ["Voters rank candidates by preference. If no one gets 50%+ first-choice votes, the last-place candidate is eliminated and their voters' ballots go to second choices. This repeats until someone passes 50%.",
         "Alaska and Maine use RCV statewide; 50+ cities (NYC, Minneapolis) use it locally. FairVote studies show winners average 52.8% of final-round votes."],
        "RCV mechanics with current adoption status",
        "Contexts cover voting process, elimination rounds, and jurisdictions",
        "government", "how", "single", "procedural"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "near_complete_evidence",
        "Does long-term shift work cause measurable health problems for employees?",
        ["Yes. IARC classifies night shifts as 'probably carcinogenic' (Group 2A) with 5-15% increased breast cancer risk. Cardiovascular risk rises 17% for rotating shift workers, and type 2 diabetes risk increases 9% compared to day workers.",
         "Mental health impacts include 28% higher depression and anxiety rates among permanent night workers. Gastrointestinal disorders, especially peptic ulcers, occur at 2-5x the day-worker rate due to disrupted meal timing and altered gut motility."],
        "Shift work health effects across five body systems",
        "Contexts cover cancer, CV, metabolic, mental health, and GI risks with percentages",
        "hr_workplace", "does", "single", "factual"
    )); h += 1

    # --- conditional_confidence: 3 hard ---
    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "conditional_confidence",
        "Is it safe to exercise during pregnancy, and when should women avoid it?",
        ["ACOG recommends 150 min/week moderate aerobic activity for uncomplicated pregnancies. Safe: walking, swimming, cycling, modified yoga.",
         "Avoid with placenta previa after 26 weeks, preeclampsia, cervical insufficiency, preterm labor risk, severe anemia, or restrictive heart/lung disease. No contact sports, hot yoga, or scuba."],
        "Conditional pregnancy exercise guidance",
        "Contexts provide ACOG recommendation and six contraindications",
        "medicine", "is", "single", "evaluative"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "conditional_confidence",
        "Should small businesses use accrual or cash basis accounting?",
        ["IRS allows cash basis under $29M gross receipts (2024). Cash is simpler. But accrual is required for inventory businesses, those above $29M, and certain C corporations.",
         "Decision factors: (1) regulatory requirements, (2) whether investors need GAAP financials (which require accrual), (3) whether to defer tax by controlling income recognition timing."],
        "Conditional accounting method guidance",
        "Contexts identify the threshold, mandatory situations, and three decision factors",
        "finance", "should", "single", "evaluative"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "conditional_confidence",
        "Is recording a phone conversation legal in the United States?",
        ["Federal law (18 USC 2511) allows recording if one party consents. But 11 states require all-party consent: CA, CT, FL, IL, MD, MA, MI, MT, NH, PA, WA.",
         "Violations bring criminal and civil liability. For interstate calls, the stricter state's law applies. Businesses use automated disclosures at call start to satisfy all-party consent."],
        "Phone recording legality by state consent type",
        "Contexts distinguish federal from state rules with consequences and compliance",
        "law", "is", "single", "factual"
    )); h += 1

    # --- step_by_step: 3 hard ---
    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "step_by_step",
        "How do you calibrate a drip irrigation system for vegetables?",
        ["(1) Cup-test 10 emitters for 15 min, measure ml. (2) Calculate GPH: avg ml x 0.0159. (3) Get crop water need from local ET data x crop coefficient (Kc 0.8-1.2 for vegetables).",
         "(4) Runtime = daily water need / (emitter GPH x emitters per plant). (5) Check distribution uniformity (DU): lowest-quartile avg / overall avg. Above 90% is excellent. (6) Actual runtime = calculated / DU."],
        "Six-step drip irrigation calibration",
        "Contexts provide measurement steps and formulas with quality thresholds",
        "agriculture", "how", "single", "procedural"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "step_by_step",
        "How does a forensic accountant trace hidden assets in divorce proceedings?",
        ["(1) Analyze 3-5 years of tax returns vs bank deposits. (2) Lifestyle analysis: compare income to spending via credit cards and loan applications. (3) Trace transfers, cash withdrawals over $5K, payments to unknowns.",
         "(4) Subpoena brokerages, insurance cash values, offshore records. (5) Examine business financials for fictitious vendors or no-work family payroll. (6) Prepare marital balance sheet as expert testimony under FRE 702."],
        "Six-step forensic asset tracing procedure",
        "Contexts detail investigative techniques and legal framework",
        "law", "how", "single", "procedural"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "step_by_step",
        "How should HR conduct a workplace harassment investigation?",
        ["(1) Document complaint within 24-48 hrs with conflict-free investigator. (2) Separate parties without retaliating against complainant. (3) Interview complainant on specifics: dates, witnesses, evidence. (4) Interview accused, document verbatim.",
         "(5) Interview witnesses individually, instruct confidentiality. (6) Collect emails, footage, prior complaints. (7) Evaluate on preponderance-of-evidence standard. (8) Communicate findings and implement corrective action."],
        "Eight-step harassment investigation procedure",
        "Contexts provide sequential steps with timelines and evidence standards",
        "hr_workplace", "how", "single", "procedural"
    )); h += 1

    # --- definitional: 2 hard ---
    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "definitional",
        "When can the government take private property through eminent domain?",
        ["Eminent domain allows government to take private property when two Fifth Amendment requirements are met: the taking must serve a 'public use' (broadly interpreted since Kelo v. New London, 2005 to include economic development), and the owner must receive just compensation.",
         "Just compensation equals fair market value at the time of taking. The formal legal process is called condemnation proceedings. Property owners have the right to challenge both the public use designation and the offered compensation amount in court."],
        "Eminent domain conditions and constitutional requirements",
        "Contexts provide Fifth Amendment basis, two requirements, and key case law",
        "law", "when", "single", "factual"
    )); h += 1

    cases.append(base(
        f"t1_confident_hard_{h}", "hard", "definitional",
        "Why does the herd immunity threshold differ so dramatically between measles and influenza?",
        ["Herd immunity threshold = 1 - 1/R0, where R0 is the basic reproduction number (average secondary infections from one case in a susceptible population). Measles (R0=12-18) requires 92-95% population immunity, while influenza (R0=1.5-2) needs only 33-50%.",
         "The difference is driven entirely by transmissibility: measles spreads so efficiently that even 5-8% susceptible people sustain outbreaks, while flu's lower R0 means outbreaks die out with modest immunity levels. For SARS-CoV-2 original (R0=2.5-3.5), the threshold was 60-71%."],
        "Herd immunity threshold variation explained via R0 differences",
        "Contexts provide the formula and explain why transmissibility drives threshold differences between diseases",
        "medicine", "why", "single", "factual"
    )); h += 1

    assert h == 1008, f"Expected hard=1008, got {h} ({h-962} hard cases)"

    # ==== MEDIUM CASES (45 total) ====
    m = 955

    # --- technical_documented: 3 medium ---
    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "technical_documented",
        "How does a heat pump both heat and cool a building?",
        ["In heating mode, the outdoor coil absorbs heat from outside air via refrigerant; the indoor coil releases that heat inside. A reversing valve switches flow direction for cooling.",
         "Modern heat pumps achieve COP of 3-4, producing 3-4 units of heat per unit of electricity, far exceeding electric resistance heating efficiency."],
        "Heat pump operation in both modes",
        "Contexts describe refrigerant cycle, reversing valve, and COP",
        "technology", "how", "single", "factual"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "technical_documented",
        "Why is HTTPS considered more secure than HTTP for web browsing?",
        ["HTTP transmits data in plain text, making it vulnerable to interception by anyone on the network path. HTTPS adds TLS encryption (typically AES-256 after an asymmetric key exchange), encrypting all data in transit between browser and server.",
         "HTTPS also requires a valid certificate from a trusted Certificate Authority, authenticating the server's identity. Since 2018, Chrome marks HTTP sites 'Not Secure' and search rankings penalize HTTP-only sites, driving widespread adoption."],
        "HTTPS security advantages over HTTP",
        "Contexts explain encryption mechanism and authentication requirements",
        "technology", "why", "single", "comparative"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "technical_documented",
        "How does GPS determine a device's location?",
        ["GPS uses trilateration from 4+ of 31 satellites orbiting at 20,200 km. Each broadcasts position and a precise timestamp; the receiver calculates signal delay to derive distance.",
         "Three satellites give 3D position; the fourth corrects receiver clock errors. Civilian accuracy is 3-5 meters under open sky."],
        "GPS positioning mechanism",
        "Contexts describe trilateration, timing, and accuracy",
        "technology", "how", "single", "factual"
    )); m += 1

    # --- clear_explanation: 3 medium ---
    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "clear_explanation",
        "Why do leaves change color in autumn?",
        ["Decreasing daylight stops chlorophyll production, unmasking yellow/orange carotenoids. Red/purple anthocyanins are produced when trapped sugars react with sunlight during cool nights.",
         "Browns come from tannin waste products. Best displays occur with sunny days and cool (not freezing) nights; drought and early frost diminish color."],
        "Autumn color change via pigment chemistry",
        "Contexts identify pigment types and environmental factors",
        "science", "why", "single", "causal"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "clear_explanation",
        "How does compound interest differ from simple interest?",
        ["Simple: I = P x r x t (on principal only). Compound: A = P(1+r/n)^(nt), calculated on principal plus all accumulated interest.",
         "$10,000 at 5% for 10 years: $15,000 simple vs $16,470 compound annually vs $16,532 monthly. Most savings accounts use daily compounding."],
        "Simple vs compound interest with example",
        "Contexts provide formulas and a worked numerical comparison",
        "finance", "how", "single", "comparative"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "clear_explanation",
        "Why do only certain foods trigger allergic reactions?",
        ["The immune system produces IgE antibodies against specific food proteins. On re-exposure, IgE triggers mast cells to release histamine, causing hives, swelling, or anaphylaxis.",
         "Only proteins that resist digestion long enough to interact with gut immune cells are allergenic. Eight foods (peanuts, tree nuts, milk, eggs, wheat, soy, fish, shellfish) cause 90% of food allergies."],
        "Food allergy immunological mechanism",
        "Contexts explain IgE pathway and why specific proteins are allergenic",
        "medicine", "why", "single", "causal"
    )); m += 1

    # --- contradiction_resolved: 3 medium ---
    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "contradiction_resolved",
        "Does stretching before exercise prevent injuries or cause harm?",
        ["A British Journal of Sports Medicine review found that static stretching (30+ sec holds) before exercise reduces muscle strength 5-8% and doesn't prevent injuries in most sports.",
         "The American College of Sports Medicine recommends dynamic stretching (leg swings, arm circles) before exercise, which maintains power and reduces injury rates 10-15%. Static stretching should be reserved for post-exercise or separate flexibility sessions."],
        "Stretching debate resolved via type distinction",
        "Both BJSM review and ACSM guidelines agree on dynamic before, static after",
        "sports", "does", "multi_source", "evaluative",
        [{"source_id": "bjsm_stretching_review", "source_type": "academic", "authority": "primary"},
         {"source_id": "acsm_stretching_guide", "source_type": "academic", "authority": "expert"}]
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "contradiction_resolved",
        "Is breakfast truly the most important meal of the day?",
        ["Originated from 1944 cereal marketing. Observational studies showed breakfast eaters were healthier, but RCTs found no weight loss benefit.",
         "Resolution: breakfast eaters had healthier overall lifestyles, confounding results. Breakfast helps children's cognition and blood sugar regulation but isn't universally necessary for adults."],
        "Breakfast myth resolved via confounding analysis",
        "Contexts trace marketing origin and explain the observational confound",
        "food", "is", "single", "evaluative"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "contradiction_resolved",
        "Do violent video games cause violent behavior in youth?",
        ["Lab studies found short-term aggressive thoughts. But juvenile violent crime fell 37% (2006-2019) as gaming surged. APA 2020: 'insufficient evidence' linking games to criminal violence.",
         "Resolution: lab 'aggression' measures (choosing loud noises) don't translate to real violence. Population-level data directly contradicts a causal link."],
        "Video game violence debate resolved via measurement validity",
        "Contexts distinguish lab aggression from real-world violence",
        "social_media", "does", "single", "evaluative"
    )); m += 1

    # --- opposing_with_consensus: 3 medium ---
    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "opposing_with_consensus",
        "Is it safe to microwave food in plastic containers?",
        ["The FDA's food contact materials program certifies 'microwave-safe' plastics (typically polypropylene, recycling code #5) as keeping chemical migration 100-1,000x below harmful levels established in animal studies.",
         "Harvard Health Publishing confirms the safety of microwave-safe labeled containers but warns against microwaving take-out containers, margarine tubs, or polystyrene (#6) and polycarbonate (#7) plastics. Cracked or discolored containers should always be discarded."],
        "Microwave plastic safety from FDA and medical institution",
        "Both FDA certification standards and Harvard Health guidance align on safe container types",
        "food", "is", "multi_source", "evaluative",
        [{"source_id": "fda_food_contact_2024", "source_type": "government", "authority": "official"},
         {"source_id": "harvard_health_plastics", "source_type": "academic", "authority": "expert"}]
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "opposing_with_consensus",
        "Should homeowners always get a home inspection before buying?",
        ["The National Association of Realtors advises buyers to always obtain a home inspection despite competitive market pressures. At $300-500, inspections can identify foundation, roofing, electrical, and plumbing issues costing tens of thousands to repair.",
         "The American Society of Home Inspectors reports that 85% of all inspections uncover at least one material defect requiring attention. Even 36% of new construction inspections find defects that municipal building inspectors missed during the permitting process."],
        "Home inspection recommendation from two professional organizations",
        "Both NAR and ASHI data support always inspecting before purchase",
        "real_estate", "should", "multi_source", "evaluative",
        [{"source_id": "nar_buyer_guide_2024", "source_type": "industry", "authority": "primary"},
         {"source_id": "ashi_inspection_stats_2024", "source_type": "industry", "authority": "primary"}]
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "opposing_with_consensus",
        "Is working from home less productive than office work?",
        ["Stanford economist Bloom's study of 16,000 workers found hybrid (3 office, 2 home) showed no productivity loss; fully remote call-center workers were 13% more productive than in-office counterparts.",
         "Microsoft WorkLab research found fully remote work cut spontaneous collaboration by 25%. SHRM endorses hybrid as optimal: it maintains individual task productivity while preserving in-person collaboration benefits."],
        "Remote work consensus from academic and industry research",
        "Stanford research and Microsoft/SHRM findings converge on hybrid as optimal",
        "hr_workplace", "is", "multi_source", "evaluative",
        [{"source_id": "stanford_bloom_remote_2024", "source_type": "academic", "authority": "primary"},
         {"source_id": "microsoft_worklab_2024", "source_type": "industry", "authority": "primary"}]
    )); m += 1

    # --- different_framing: 3 medium ---
    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "different_framing",
        "Why does a single cold day not disprove global warming?",
        ["Weather is short-term atmospheric conditions at a specific place and time, while climate is the statistical average of weather over 30+ years per the World Meteorological Organization. They operate on entirely different timescales.",
         "People experience weather directly but can only observe climate through long-term data aggregation. A cold day is a weather event; global warming is a climate trend. Just as a single bad mood doesn't change your personality, one cold day doesn't affect the 30-year average."],
        "Weather vs climate distinction explaining common misconception",
        "Contexts provide WMO definition and explain why individual events don't contradict long-term trends",
        "environment", "why", "single", "factual"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "different_framing",
        "How do food expiration dates differ from best-by dates for safety?",
        ["'Sell-by' is for retailers. 'Best-by' indicates quality, not safety. 'Use-by' is safety-relevant for perishables. Except for infant formula, no federal law requires date labels.",
         "FDA's 2023 guidance supports standardizing to 'Best If Used By' (quality) and 'Use By' (safety) to cut the estimated 30% of food waste caused by label confusion."],
        "Date label types and safety implications",
        "Contexts differentiate label types and note food waste impact",
        "food", "how", "single", "factual"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "different_framing",
        "Does an acquittal provide stronger legal protection than a dismissal?",
        ["Yes. Acquittal occurs after a full trial when the jury/judge finds the defendant not guilty. The Fifth Amendment's double jeopardy clause permanently bars retrial for the same offense, providing absolute protection.",
         "A dismissal ends the case before verdict due to insufficient evidence or procedural errors, but it can be 'without prejudice' (prosecution may refile charges later). Only 'with prejudice' dismissals provide the same permanent protection as acquittals."],
        "Acquittal vs dismissal legal protection comparison",
        "Contexts compare the permanence of each outcome and explain prejudice types",
        "law", "does", "single", "comparative"
    )); m += 1

    # --- quantitative_answer: 3 medium ---
    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "quantitative_answer",
        "How long does a plastic bottle take to decompose in a landfill?",
        ["PET bottles: approximately 450 years per NOAA. In oceans, UV breaks bottles into microplastics in 10-20 years, but polymers persist for centuries.",
         "Comparison: glass 1M+ years, aluminum 200-500 years, paper 2-6 weeks. Only 29% of PET bottles are recycled per 2023 EPA data."],
        "Plastic decomposition timeline with comparisons",
        "Contexts provide the 450-year figure and comparative timelines",
        "environment", "how", "single", "factual"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "quantitative_answer",
        "What is the average wedding cost in the United States?",
        ["The Knot's 2024 Real Weddings Study, surveying over 10,000 couples, found the average US wedding cost was $35,000 excluding the honeymoon, up 4% from 2023. Costs range from $55-60K in NY/NJ to $18-22K in KS/AR/MS.",
         "Top categories: venue 31%, catering 23%, photo/video 12%, entertainment 8%, flowers 8%. Median $28K -- average skewed by high-cost outliers."],
        "US wedding cost breakdown",
        "Contexts provide average, median, regional ranges, and budget shares",
        "general", "what", "single", "factual"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "quantitative_answer",
        "How many bird species have been documented worldwide?",
        ["IOU world bird list v14.1 (Jan 2024): 11,017 extant species. About 1,481 (13.4%) IUCN-threatened: 798 vulnerable, 460 endangered, 223 critically endangered.",
         "The 2024 list added 7 newly described species and split 15 previously recognized species into separate classifications. An estimated 150 billion individual birds exist worldwide across all species."],
        "World bird species count with conservation status",
        "Contexts provide IOU count, threat breakdown, and population estimate",
        "science", "how", "single", "factual"
    )); m += 1

    # --- cross_source_agreement: 4 medium, multi_source ---
    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "cross_source_agreement",
        "What is the average US public school teacher salary?",
        ["The National Education Association's 2024 Rankings report states the average US public school teacher salary in 2023-24 was $69,544, ranging from $46,843 in Mississippi to $95,279 in New York.",
         "The Bureau of Labor Statistics Occupational Employment Statistics (May 2024) reports a mean annual wage of $68,830 for elementary teachers and $70,420 for secondary teachers, consistent with the NEA's overall average."],
        "Teacher salary from two independent sources",
        "NEA and BLS converge on approximately $69-70K",
        "education", "what", "multi_source", "factual",
        [{"source_id": "nea_rankings_2024", "source_type": "industry", "authority": "primary"},
         {"source_id": "bls_oes_2024", "source_type": "government", "authority": "official"}]
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "cross_source_agreement",
        "What is the recommended daily water intake for adults?",
        ["The National Academies of Sciences determined that adequate daily fluid intake is approximately 3.7 liters (125 oz) for men and 2.7 liters (91 oz) for women, including all beverages and food (which provides about 20% of total water intake).",
         "Mayo Clinic's nutrition guidelines align with these recommendations: 15.5 cups (3.7L) for men and 11.5 cups (2.7L) for women, with individual needs varying based on exercise level, climate conditions, and overall health status."],
        "Daily water intake from two health authorities",
        "Both provide identical 3.7L/2.7L recommendations",
        "medicine", "what", "multi_source", "factual",
        [{"source_id": "nasem_dietary_ref", "source_type": "government", "authority": "official"},
         {"source_id": "mayo_nutrition", "source_type": "reference", "authority": "expert"}]
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "cross_source_agreement",
        "What percentage of US adults hold a bachelor's degree or higher?",
        ["The US Census Bureau's Current Population Survey (2024 data) reports that 37.7% of US adults aged 25 and older hold a bachelor's degree or higher, a significant increase from 33.1% in 2019.",
         "NCES Condition of Education 2024: 38.0% of adults 25-64, consistent with Census when accounting for the narrower age range."],
        "Degree attainment from two federal sources",
        "Census and NCES converge at 37.7-38.0%",
        "education", "what", "multi_source", "factual",
        [{"source_id": "census_cps_2024", "source_type": "government", "authority": "official"},
         {"source_id": "nces_2024", "source_type": "government", "authority": "official"}]
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "cross_source_agreement",
        "What unemployment rate is considered full employment in the US?",
        ["CBO Feb 2024: NAIRU estimated at 4.4%, meaning unemployment near this level is full employment without excess inflation.",
         "Federal Reserve Chair Jerome Powell's December 2024 press conference referenced the Fed's longer-run unemployment estimate of 4.2%, noting that actual unemployment of 3.7% was 'below most estimates of its natural rate.'"],
        "Full employment rate from CBO and Fed",
        "Both converge on approximately 4.2-4.4%",
        "government", "what", "multi_source", "factual",
        [{"source_id": "cbo_outlook_2024", "source_type": "government", "authority": "official"},
         {"source_id": "fed_presser_dec2024", "source_type": "government", "authority": "official"}]
    )); m += 1

    # --- direct_factual: 3 medium ---
    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "direct_factual",
        "Which planet has the most moons in our solar system?",
        ["Saturn: 146 confirmed moons per IAU 2024, surpassing Jupiter's 95. A 2023 Canada-France-Hawaii Telescope survey discovered 62 new small irregular satellites.",
         "Most new moons are 2-4 km diameter with retrograde orbits, suggesting they are captured objects rather than formed in place."],
        "Most-moons planet identification",
        "Contexts state Saturn at 146 with discovery context",
        "science", "which", "single", "factual"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "direct_factual",
        "Who invented the World Wide Web?",
        ["Tim Berners-Lee at CERN in 1989. He built the first browser (WorldWideWeb), server (httpd), and website (info.cern.ch), which went live December 20, 1990.",
         "He created HTML, URI, and HTTP. He made the Web freely available with no patents or royalties, a decision essential to its universal adoption."],
        "WWW inventor with timeline",
        "Contexts name Berners-Lee with dates and technologies",
        "technology", "who", "single", "factual"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "direct_factual",
        "What is the tallest building in the world as of 2024?",
        ["Burj Khalifa in Dubai: 828 meters (2,717 ft), 163 above-ground floors. Completed 2010, surpassing Taipei 101 (508m) by 320 meters.",
         "Jeddah Tower (planned 1,000m+) stalled at 252m since 2013. Burj Khalifa has a hotel, residences, offices, and observation deck at 555m."],
        "Tallest building identification",
        "Contexts provide exact height, floor count, and competitor status",
        "general", "what", "single", "factual"
    )); m += 1

    # --- multi_source_convergence: 3 medium, all multi_source ---
    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "multi_source_convergence",
        "What is the average lifespan of a domestic cat?",
        ["The American Veterinary Medical Association states that indoor domestic cats live an average of 12-18 years, with some cats reaching their early 20s with proper veterinary care and nutrition.",
         "JFMS 2024 (584,000 cats): median 14.0 years indoor, 11.7 outdoor. Mixed breeds live 1.5 years longer than purebreds on average."],
        "Cat lifespan from vet association and large study",
        "Both place indoor lifespan at 12-18 years, median about 14",
        "science", "what", "multi_source", "factual",
        [{"source_id": "avma_pet_care", "source_type": "industry", "authority": "expert"},
         {"source_id": "jfms_lifespan_2024", "source_type": "academic", "authority": "primary"}]
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "multi_source_convergence",
        "What percentage of US households own a pet?",
        ["The American Pet Products Association's 2024 National Pet Owners Survey found that 67% of US households (approximately 86.9 million homes) own at least one pet, with dogs most common at 54.4M households followed by cats at 42.7M.",
         "The American Veterinary Medical Association's 2024 Pet Demographics Sourcebook, based on a nationally representative survey of 80,000 households, reports 66.3% pet ownership, with dog ownership at 44.5% and cat ownership at 29.0% of households."],
        "Pet ownership from two industry surveys",
        "APPA and AVMA converge on 66-67%",
        "general", "what", "multi_source", "factual",
        [{"source_id": "appa_survey_2024", "source_type": "industry", "authority": "primary"},
         {"source_id": "avma_demographics", "source_type": "industry", "authority": "primary"}]
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "multi_source_convergence",
        "How fast can the average person run a mile?",
        ["Running USA's 2024 annual report, based on chip-timed results from 12 million race participants, found the average mile time was 9 minutes 48 seconds across all age groups (male 8:54, female 10:41).",
         "The American College of Sports Medicine fitness assessment guidelines list an 'average' mile time as 9-12 minutes for healthy adults aged 20-50, with below 8 minutes classified as 'good' and below 6 minutes as 'excellent' fitness."],
        "Average mile time from race data and fitness standards",
        "Both place average at approximately 9-10 minutes",
        "sports", "how", "multi_source", "factual",
        [{"source_id": "running_usa_2024", "source_type": "industry", "authority": "primary"},
         {"source_id": "acsm_guidelines", "source_type": "academic", "authority": "expert"}]
    )); m += 1

    # --- authoritative_source: 3 medium ---
    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "authoritative_source",
        "What are the official dimensions of an NBA basketball court?",
        ["NBA Rule Book Rule 1: 94 ft (28.65m) x 50 ft (15.24m). Three-point line 23'9\" (7.24m) from basket center, 22 ft (6.71m) at corners.",
         "Free throw line 15 ft from backboard. Rim at exactly 10 ft (3.05m). The three-point distance was moved back from 22 ft to 23'9\" in 1997."],
        "NBA court dimensions from official rules",
        "Contexts provide exact measurements in feet and meters",
        "sports", "what", "single", "factual"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "authoritative_source",
        "What is the current US federal minimum wage?",
        ["$7.25/hour since July 24, 2009 (Fair Minimum Wage Act of 2007). Tipped minimum $2.13/hour provided tips bring total to $7.25+.",
         "Thirty states plus DC exceed the federal rate; Washington is highest at $16.28/hour (Jan 2024). CBO estimates $15 federal would raise pay for 17M workers."],
        "Federal minimum wage with state context",
        "Contexts provide exact rate, date, tipped rate, and state variation",
        "government", "what", "single", "factual"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "authoritative_source",
        "What is the typical school zone speed limit in US states?",
        ["According to the Governors Highway Safety Association's 2024 state law compilation, the most common school zone speed limit is 20 mph, used by 31 states. Nine states set 15 mph (including CA and NY) and 10 states set 25 mph.",
         "Enforced during school hours or when lights flash. Penalties generally double the normal fine. Automated cameras authorized in 17 states."],
        "School zone speed limits from GHSA",
        "Contexts identify the common limit with state distribution",
        "transportation", "what", "single", "factual"
    )); m += 1

    # --- near_complete_evidence: 3 medium ---
    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "near_complete_evidence",
        "What are the main causes of urban traffic congestion?",
        ["(1) Peak-hour demand (45-55% of traffic in 4 hours). (2) Incidents: 25% of congestion per FHWA. (3) Work zones: 10%. (4) Poor signal timing wastes 295K daily hours nationwide.",
         "(5) Induced demand absorbs 20-50% of new road capacity in 5-10 years. (6) Lack of transit alternatives forces car dependency. A single lane closure during peak can cut throughput 50%."],
        "Six congestion causes with contributions",
        "Contexts enumerate causes with quantified shares",
        "transportation", "what", "single", "factual"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "near_complete_evidence",
        "Does payment history matter more than credit utilization for your credit score?",
        ["Yes, in FICO scoring (used in 90% of lending decisions). Payment history carries 35% weight -- a single 30-day late payment can drop scores 60-110 points. Credit utilization is 30% -- keeping balances below 30% of limits is recommended, below 10% is optimal.",
         "The remaining factors: credit history length 15% (7+ years helps), credit mix 10% (revolving + installment loans), and new inquiries 10% (each hard pull drops 5-10 points for 12 months). VantageScore uses similar weights but doesn't penalize paid collections."],
        "Credit score factor hierarchy with FICO weights",
        "Contexts establish the payment history > utilization ranking and cover all five factors",
        "finance", "does", "single", "factual"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "near_complete_evidence",
        "How does US presidential succession work beyond the VP?",
        ["1947 Succession Act: (1) Speaker of the House, (2) President pro tempore of Senate, (3) Secretary of State, then Cabinet by department creation date.",
         "25th Amendment: Section 3 for voluntary transfer, Section 4 for involuntary (VP + Cabinet majority). VP vacancies filled by nomination + congressional confirmation, as with Ford 1973 and Rockefeller 1974."],
        "Presidential succession framework",
        "Contexts cover statutory order and constitutional mechanisms",
        "government", "how", "single", "factual"
    )); m += 1

    # --- conditional_confidence: 3 medium ---
    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "conditional_confidence",
        "Is it safe to eat sushi during pregnancy?",
        ["FDA/ACOG: avoid raw fish (Listeria, parasite risk). But cooked sushi is safe -- California rolls, shrimp tempura, cooked eel provide good protein.",
         "Avoid all high-mercury fish (shark, swordfish, king mackerel). Eat low-mercury options (salmon, shrimp, pollock) 2-3 servings/week for fetal brain omega-3 benefits."],
        "Conditional sushi guidance during pregnancy",
        "Contexts distinguish raw (avoid) from cooked (safe) with mercury tiers",
        "food", "is", "single", "evaluative"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "conditional_confidence",
        "Should you tip on takeout orders?",
        ["Emily Post 2024: appreciated but not required. 10% standard, 15-20% for large/complex orders. Post-pandemic 43% of consumers now tip takeout (up from 24%).",
         "Counter-service prompts: 0-15%. Higher tips warranted for phone orders, catering, curbside delivery, and special modifications."],
        "Conditional takeout tipping guidance",
        "Contexts provide tier-based recommendations by context",
        "food", "should", "single", "evaluative"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "conditional_confidence",
        "Is refinancing a mortgage worth it, and when does it make sense?",
        ["Refinancing makes financial sense when the rate drops 0.75-1.0+ percentage points. Calculate break-even by dividing total closing costs (typically $6,000-$10,000 on a $200,000 loan) by monthly payment savings.",
         "Don't refinance if: moving before break-even, <10 years remain, credit dropped (worse rate), or equity below 20% (triggers PMI)."],
        "Conditional refinancing guidance",
        "Contexts provide rate threshold, formula, and disqualifying conditions",
        "real_estate", "is", "single", "evaluative"
    )); m += 1

    # --- step_by_step: 3 medium ---
    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "step_by_step",
        "How do you change a flat tire?",
        ["(1) Flat surface, hazards on, parking brake, wheel wedges. (2) Loosen lugs half-turn while on ground. (3) Jack at designated point until tire is 6 inches up.",
         "(4) Remove lugs, swap tire, hand-tighten in star pattern. (5) Lower partially, fully tighten (80-100 ft-lbs). (6) Lower fully. Drive <50 mph, <50 miles on temp spare."],
        "Flat tire change procedure",
        "Contexts provide six steps with measurements and limits",
        "transportation", "how", "single", "procedural"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "step_by_step",
        "How do you cite sources in APA 7th edition?",
        ["In-text: (Smith, 2023) or Smith (2023). Two authors: &. Three+: et al. References: hanging indent, double-spaced, DOIs as links.",
         "Journal: Author. (Year). Title. Journal Italics, Vol(Issue), Pages. DOI. Book: Author. (Year). Title italics. Publisher. Website: Author. (Date). Title. Site. URL."],
        "APA 7th citation steps",
        "Contexts cover in-text rules and source templates",
        "education", "how", "single", "procedural"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "step_by_step",
        "How do you perform CPR on a collapsed adult?",
        ["(1) Tap and shout. (2) Call 911, request AED. (3) Check breathing max 10 sec (gasping is not normal). (4) Compressions: center of chest, 2+ inches deep, 100-120/min.",
         "(5) Full recoil between compressions. (6) If trained: 2 breaths (1 sec each) every 30 compressions. (7) Continue until EMS. Compression-only CPR recommended for untrained bystanders."],
        "Adult CPR procedure from AHA",
        "Contexts provide steps with depth, rate, and ratio specs",
        "medicine", "how", "single", "procedural"
    )); m += 1

    # --- definitional: 6 medium ---
    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "definitional",
        "Who was responsible for the term gerrymandering and how is it used today?",
        ["The term originated in 1812 when Massachusetts Governor Elbridge Gerry approved a state senate district shaped like a salamander to favor his party. Today, gerrymandering means drawing electoral boundaries to advantage a political party.",
         "Two techniques are used: 'packing' concentrates opponents into few districts, and 'cracking' splits them across many. In Rucho v. Common Cause (2019), SCOTUS ruled partisan gerrymandering non-justiciable, though racial gerrymandering remains reviewable under the Voting Rights Act."],
        "Gerrymandering origin and current legal status",
        "Contexts trace the etymology, define techniques, and state judicial enforceability",
        "history", "who", "single", "factual"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "definitional",
        "Why is GDP considered an incomplete measure of a country's well-being?",
        ["GDP measures total monetary value of finished goods and services within a country's borders, calculated via expenditure (C+I+G+NX), income, or production (value added at each stage). It tracks economic activity accurately.",
         "But GDP ignores income inequality, environmental degradation, unpaid household work (~$10.9T/yr in the US), the underground economy, and quality of life factors. Nobel laureate Stiglitz argues GDP was designed to measure activity, not well-being, and should not serve as a proxy for societal progress."],
        "GDP limitations as a well-being measure",
        "Contexts define GDP's purpose and enumerate six critical blind spots",
        "finance", "why", "single", "factual"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "definitional",
        "Why does confirmation bias make people resist changing their minds even when shown contrary evidence?",
        ["Confirmation bias, first described by Peter Wason in 1960, is the tendency to search for, interpret, and recall information that supports existing beliefs while giving disproportionately less attention to contradictory evidence.",
         "Three reinforcing mechanisms make it resistant: selective exposure (seeking aligned sources), biased interpretation (reading ambiguous data as confirming), and selective recall (better memory for confirming info). These affect medical diagnosis, criminal investigations, and financial investing."],
        "Confirmation bias mechanisms explaining resistance to belief change",
        "Contexts define the bias and explain three reinforcing mechanisms",
        "psychology", "why", "single", "factual"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "definitional",
        "What is the gig economy?",
        ["A labor market of short-term, freelance work via platforms (Uber, DoorDash, Fiverr). BLS: 57.3M Americans participate, 16% as primary income.",
         "Workers lack employer benefits and unemployment protections. DOL 2024 rule uses multi-factor economic reality test for contractor vs employee classification."],
        "Gig economy definition with statistics",
        "Contexts define the concept, provide BLS data, and note legal issues",
        "hr_workplace", "what", "single", "factual"
    )); m += 1

    cases.append(base(
        f"t1_confident_medium_{m}", "medium", "definitional",
        "What is the average US commute time?",
        ["The US Census Bureau's American Community Survey (2023) reports the average one-way commute time for US workers at 27.6 minutes, with 76.3% driving alone, 9.0% carpooling, and 5.2% using public transit.",
         "The Bureau of Transportation Statistics' 2024 National Household Travel Survey found an average commute of 28.1 minutes one-way with a median of 24 minutes, right-skewed by metros like New York (37.7 min) and Los Angeles (32.1 min)."],
        "US commute time from two federal surveys",
        "Census and BTS converge on 27.6-28.1 minutes",
        "transportation", "what", "multi_source", "factual",
        [{"source_id": "census_acs_2023", "source_type": "government", "authority": "official"},
         {"source_id": "bts_nhts_2024", "source_type": "government", "authority": "official"}]
    )); m += 1

    assert m == 1000, f"Expected medium=1000, got {m} ({m-955} medium cases)"
    return cases


def validate_cases(cases):
    errors = []
    seen_ids = set()
    seen_queries = set()
    from collections import Counter
    subcats = Counter()
    domains = Counter()
    query_types = Counter()
    difficulties = Counter()
    multi_source_count = 0

    for c in cases:
        cid = c["id"]
        if cid in seen_ids:
            errors.append(f"Duplicate ID: {cid}")
        seen_ids.add(cid)
        q = c["query"].lower().strip()
        if q in seen_queries:
            errors.append(f"Dup query {cid}: {c['query'][:60]}")
        seen_queries.add(q)

        for field in ["id", "difficulty", "subcategory", "query", "contexts",
                      "expected_mode", "description", "rationale", "domain",
                      "query_type", "source_type", "context_count",
                      "reasoning_type", "evidence_pattern", "category",
                      "evaluation_config"]:
            if field not in c:
                errors.append(f"{cid}: missing '{field}'")

        if c.get("expected_mode") != "trustworthy":
            errors.append(f"{cid}: expected_mode != trustworthy")
        if c.get("category") != "trustworthy_direct":
            errors.append(f"{cid}: category != trustworthy_direct")
        if c.get("evidence_pattern") != "direct":
            errors.append(f"{cid}: evidence_pattern != direct")
        if c.get("context_count") != len(c.get("contexts", [])):
            errors.append(f"{cid}: context_count mismatch")

        for i, ctx in enumerate(c.get("contexts", [])):
            if len(ctx) < 120:
                errors.append(f"{cid}: ctx[{i}] short ({len(ctx)})")
            if len(ctx) > 450:
                errors.append(f"{cid}: ctx[{i}] long ({len(ctx)})")

        if c.get("source_type") == "multi_source":
            multi_source_count += 1
            if "context_sources" not in c:
                errors.append(f"{cid}: multi_source no context_sources")
            elif len(c["context_sources"]) != len(c.get("contexts", [])):
                errors.append(f"{cid}: context_sources len mismatch")

        subcats[c.get("subcategory")] += 1
        domains[c.get("domain")] += 1
        query_types[c.get("query_type")] += 1
        difficulties[c.get("difficulty")] += 1

    print(f"\n=== Distribution ===\nTotal: {len(cases)}")
    print(f"Difficulties: {dict(difficulties)}")
    print(f"\nSubcategories ({len(subcats)}):")
    for s, n in sorted(subcats.items()): print(f"  {s}: {n}")
    print(f"\nDomains ({len(domains)}):")
    for d, n in sorted(domains.items()): print(f"  {d}: {n}")
    print(f"\nQuery types:")
    for q, n in sorted(query_types.items()): print(f"  {q}: {n}")
    print(f"\nMulti-source: {multi_source_count}")

    if len(cases) != 91: errors.append(f"Need 91, got {len(cases)}")
    if difficulties.get("hard", 0) != 46: errors.append(f"Need 46 hard")
    if difficulties.get("medium", 0) != 45: errors.append(f"Need 45 medium")
    if multi_source_count < 20: errors.append(f"Multi-source {multi_source_count} < 20")
    for d, n in domains.items():
        if n > 7: errors.append(f"Domain '{d}' = {n} > 7")

    w = query_types.get("what", 0)
    h = query_types.get("how", 0)
    id_ = query_types.get("is", 0) + query_types.get("does", 0)
    ws = query_types.get("why", 0) + query_types.get("should", 0)
    wwk = query_types.get("when", 0) + query_types.get("who", 0) + query_types.get("which", 0)

    if w > 23: errors.append(f"what={w} > 23")
    if h < 18: errors.append(f"how={h} < 18")
    if id_ < 18: errors.append(f"is/does={id_} < 18")
    if ws < 10: errors.append(f"why/should={ws} < 10")
    if wwk < 8: errors.append(f"when/who/which={wwk} < 8")

    return errors


def main():
    cases = build_cases()
    errors = validate_cases(cases)
    if errors:
        print(f"\n*** FAILED ({len(errors)}): ***")
        for e in errors: print(f"  - {e}")
        return

    print("\n*** PASSED ***")
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    overlap = {c["id"] for c in data["cases"]} & {c["id"] for c in cases}
    if overlap:
        print(f"*** OVERLAP: {sorted(overlap)[:5]} ***")
        return
    data["cases"].extend(cases)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nAppended {len(cases)}. Total: {len(data['cases'])}")


if __name__ == "__main__":
    main()
