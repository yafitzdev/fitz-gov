#!/usr/bin/env python3
"""
Fix script for fitz-gov v4.1:
  1. Rewrite 27 duplicate-query cases (26 groups, one group has 2 rewrites)
  2. Reclassify 57 "general" domain cases to specific domains

Each rewritten case gets a new unique query and new contexts matching
its governance pattern (expected_mode, subcategory, category).
"""

import json
import os
import sys
from collections import defaultdict
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TIER_DIRS = [DATA_DIR / "tier0_sanity", DATA_DIR / "tier1_core"]


# =============================================================================
# PART 1: Duplicate query rewrites
# =============================================================================
# Each entry: case_id -> {new query, new contexts, optional new fields}
# We preserve all other fields (id, expected_mode, subcategory, etc.)

DUPLICATE_REWRITES = {
    # 1. Knuckle cracking
    "t1_confident_medium_915": {
        "query": "Does cracking knuckle joints lead to osteoarthritis later in life?",
        "contexts": [
            "A longitudinal study published in the Journal of the American Board of Family Medicine (Deweber et al., 2011) examined 215 adults aged 50-89 and found no statistically significant correlation between habitual knuckle cracking and the incidence of hand osteoarthritis. The study used radiographic evidence to confirm the absence of joint damage.",
            "Dr. Donald Unger conducted a self-experiment over 60 years, cracking only his left hand's knuckles twice daily while leaving the right hand uncracked. Upon examination, neither hand showed signs of osteoarthritis, earning him the 2009 Ig Nobel Prize in Medicine. A systematic review in the Journal of Manipulative and Physiological Therapeutics (2017) corroborated these findings across multiple populations."
        ],
        "description": "Multiple longitudinal studies found no link between knuckle cracking and osteoarthritis",
        "rationale": "Both the 60-year self-experiment and radiographic population study confirm no arthritis risk from knuckle cracking",
        "domain": "medicine",
    },
    # 2. Intermittent fasting / cognitive function
    "t1_dispute_hard_703": {
        "query": "Is time-restricted eating beneficial for brain health and neuroplasticity?",
        "contexts": [
            "A 2022 study in Nature Neuroscience found that mice on a time-restricted feeding schedule showed a 30% increase in brain-derived neurotrophic factor (BDNF) levels and improved performance on memory tasks. The researchers attributed the benefits to enhanced autophagy and reduced neuroinflammation during fasting periods.",
            "However, a 2023 randomized controlled trial published in The Lancet Neurology involving 400 human participants found no significant cognitive improvements after 12 months of time-restricted eating (16:8 protocol). Participants showed no measurable changes in memory, attention, or executive function compared to controls.",
            "A third study from the University of California (2023) suggested that any cognitive benefits of time-restricted eating may be confounded by improved sleep quality and reduced caloric intake, rather than the fasting window itself. The authors cautioned against extrapolating animal model results to humans."
        ],
        "description": "Conflicting studies on time-restricted eating and brain health: animal models show benefits but human trials do not",
        "rationale": "Mouse studies show BDNF increase but human RCT found no cognitive improvement; confounding factors identified",
        "domain": "psychology",
    },
    # 3. Video games / cognitive abilities
    "t1_qualify_medium_534": {
        "query": "Can regular strategic board game play enhance problem-solving skills in adults?",
        "contexts": [
            "A 2021 study in the Journal of Cognitive Enhancement followed 150 adults who played strategic board games (chess, Go, Settlers of Catan) at least 3 hours weekly for 6 months. Participants showed a 12% improvement on standardized problem-solving assessments, though the study lacked a randomized control group.",
            "Researchers at the University of Edinburgh noted that the observed improvements could be partially attributed to social interaction and stress reduction during game sessions rather than strategic thinking alone. The sample was also self-selected, limiting generalizability.",
            "A smaller pilot study (n=40) found similar trends but emphasized that gains were modest and primarily appeared in participants under 45, suggesting age-related differences in neuroplasticity may limit the transferability of skills."
        ],
        "description": "Partial evidence that strategic board games improve problem-solving, with methodological caveats",
        "rationale": "Some improvement observed but limited by lack of control group, self-selection bias, and age-dependent effects",
        "domain": "psychology",
    },
    # 4. Social media / depression in teenagers
    "t1_confident_hard_971": {
        "query": "What does the American Psychological Association's 2023 advisory say about social media's impact on adolescent mental health?",
        "contexts": [
            "The American Psychological Association (APA) issued a health advisory in May 2023 titled 'Health Advisory on Social Media Use in Adolescence.' The advisory concluded that social media is neither inherently beneficial nor harmful to young people, but that its effects depend on individual circumstances, the content consumed, and the amount of time spent on platforms.",
            "The APA's 10 recommendations included: implementing age-appropriate design features, screening adolescents for signs of problematic social media use, limiting use that interferes with sleep and physical activity, and increasing digital literacy training. The advisory emphasized that adolescents' brains are still developing, making them particularly susceptible to social comparison and feedback-seeking behaviors online.",
            "The advisory cited research showing that social media can provide benefits such as community building and identity exploration, while also noting consistent associations between heavy social media use and increased rates of depression and anxiety symptoms in teens aged 13-17."
        ],
        "description": "The APA's 2023 advisory provides a specific, well-documented position on social media and adolescent mental health",
        "rationale": "References a specific APA document with defined recommendations and conclusions, enabling a direct factual answer",
        "domain": "social_media",
    },
    # 5. Compound interest
    "t1_confident_medium_959": {
        "query": "What is the mathematical formula for calculating compound interest on a savings account?",
        "contexts": [
            "The standard compound interest formula is A = P(1 + r/n)^(nt), where A is the final amount, P is the principal (initial deposit), r is the annual interest rate (as a decimal), n is the number of times interest is compounded per year, and t is the number of years. For example, $1,000 at 5% annual interest compounded monthly for 10 years yields A = 1000(1 + 0.05/12)^(12*10) = $1,647.01.",
            "When interest is compounded continuously, the formula becomes A = Pe^(rt), where e is Euler's number (approximately 2.71828). Continuous compounding represents the theoretical upper limit of compounding frequency and is used in advanced financial modeling and derivatives pricing."
        ],
        "description": "Standard compound interest formula with worked example and continuous compounding variant",
        "rationale": "Well-established mathematical formula with clear derivation and numerical example",
        "domain": "finance",
    },
    # 6. Global food production
    "t1_dispute_medium_777": {
        "query": "Has global grain output increased sufficiently to match rising demand from population growth since 2010?",
        "contexts": [
            "The Food and Agriculture Organization (FAO) reports that global cereal production grew from 2.48 billion tonnes in 2010 to 2.82 billion tonnes in 2023, a 13.7% increase. World population grew by approximately 12.5% over the same period, suggesting production has marginally outpaced population growth in absolute terms.",
            "However, the International Food Policy Research Institute (IFPRI) argues that aggregate production figures mask distributional failures. While global grain output rose, per-capita availability in Sub-Saharan Africa declined by 4% between 2015 and 2023 due to conflict, climate shocks, and supply chain disruptions. The IFPRI contends that production increases have not translated into food security where it is most needed.",
            "The World Bank's 2023 Food Security Update notes that grain price volatility has increased 40% since 2019, suggesting that even when supply meets demand on paper, market instability undermines actual access to food for vulnerable populations."
        ],
        "description": "Dispute over whether aggregate grain production growth adequately addresses food demand",
        "rationale": "FAO data shows marginal global surplus, but IFPRI highlights regional failures and World Bank notes price instability",
        "domain": "agriculture",
    },
    # 7. Homework for elementary school
    "t1_confident_hard_976": {
        "query": "What did Cooper's meta-analysis find about the correlation between homework and academic achievement in primary school?",
        "contexts": [
            "Harris Cooper's landmark meta-analysis, first published in 1989 and updated in 2006 (published in Review of Educational Research), synthesized data from over 60 studies spanning 1987-2003. For elementary school students (grades K-6), Cooper found near-zero correlation between homework completion and academic achievement as measured by standardized test scores and teacher-assigned grades.",
            "Cooper's analysis did find a positive but modest correlation for middle school students (r = 0.07) and a stronger correlation for high school students (r = 0.25). He recommended the '10-minute rule': 10 minutes of homework per grade level per night (e.g., 10 minutes for first grade, 60 minutes for sixth grade). The National Education Association and National PTA both adopted this guideline.",
            "Cooper noted that while homework in elementary school showed no academic benefit, it could serve non-academic purposes such as building study habits, fostering responsibility, and strengthening parent-child academic communication."
        ],
        "description": "Cooper's meta-analysis found near-zero correlation between homework and achievement in primary school",
        "rationale": "Specific meta-analysis with quantified correlation coefficients across grade levels provides a direct factual answer",
        "domain": "education",
    },
    # 8. Microwave plastic
    "t1_confident_medium_964": {
        "query": "Which types of plastic are FDA-approved for microwave use according to current food safety guidelines?",
        "contexts": [
            "The U.S. Food and Drug Administration (FDA) tests plastics for microwave safety under 21 CFR 177 regulations. Plastics approved for microwave use are labeled with a microwave-safe symbol or the recycling numbers 2 (HDPE), 4 (LDPE), and 5 (PP/polypropylene). These plastics have been tested at temperatures up to 250°F (121°C) and found to release chemicals well below the FDA's safety threshold of 1/100th of the amount shown to harm laboratory animals.",
            "The FDA specifically warns against using plastics numbered 3 (PVC), 6 (polystyrene/Styrofoam), and 7 (other/mixed, including some polycarbonates that may contain BPA) in microwaves. Single-use containers such as margarine tubs, takeout containers, and water bottles are not designed for microwave use regardless of plastic type. The FDA updates its approved food contact substances list regularly on its website."
        ],
        "description": "FDA regulations clearly specify which plastic types are approved for microwave use",
        "rationale": "Specific regulatory answer with numbered plastic types, CFR reference, and safety thresholds",
        "domain": "food",
    },
    # 9. Red wine / heart health
    "t1_qualify_medium_538": {
        "query": "Does moderate alcohol consumption from any source reduce cardiovascular disease risk?",
        "contexts": [
            "A 2022 study published in JAMA Network Open analyzed data from 371,463 UK Biobank participants and found that individuals consuming 1-7 drinks per week had a modestly lower rate of cardiovascular events compared to non-drinkers. However, the study noted that light drinkers also tended to exercise more, eat healthier diets, and have higher socioeconomic status, making it difficult to isolate alcohol's independent effect.",
            "The World Heart Federation issued a policy brief in 2022 stating that no level of alcohol consumption is safe for heart health, directly contradicting decades of research suggesting a J-shaped relationship between alcohol and cardiovascular risk. The brief argued that previous studies suffered from 'sick quitter' bias, where abstainers included former heavy drinkers in poor health.",
            "A Mendelian randomization study in The Lancet (2023) used genetic variants to approximate random assignment and found that the apparent cardiovascular benefit of moderate drinking disappeared entirely when confounding factors were removed, suggesting the observed association is not causal."
        ],
        "description": "Conflicting and uncertain evidence on moderate alcohol and cardiovascular risk",
        "rationale": "Observational data suggests modest benefit but confounding bias identified; genetic analysis shows no causal effect",
        "domain": "medicine",
    },
    # 10. Remote work / in-office (abstain vs confident)
    "t1_confident_hard_943": {
        "query": "What did Stanford's 2023 work-from-home research project find about remote worker productivity compared to in-office workers?",
        "contexts": [
            "Stanford economist Nicholas Bloom's ongoing Work From Home Research project released updated findings in 2023 based on a randomized controlled trial of 1,612 employees at Trip.com. Workers randomly assigned to hybrid schedules (3 days office, 2 days home) showed equivalent performance ratings, code output, and lines written compared to fully in-office workers, with no statistically significant productivity difference (p > 0.05).",
            "The study found that hybrid workers had 35% lower attrition rates, saving the company an estimated $2,000 per employee annually in recruitment and training costs. Bloom concluded that the productivity concerns about remote work are 'largely unfounded' for hybrid arrangements, though he noted that fully remote work showed a 10-20% productivity penalty in separate analyses of call center workers.",
            "Trip.com subsequently adopted the hybrid policy company-wide for all 35,000 employees, citing both the productivity equivalence and retention benefits documented in Bloom's research."
        ],
        "description": "Stanford's RCT at Trip.com found hybrid work equivalent to in-office productivity with lower attrition",
        "rationale": "Specific randomized controlled trial with named researchers, sample sizes, and quantified results provides a direct factual answer",
        "domain": "hr_workplace",
    },
    # 11. Remote work / office work (dispute vs relevance)
    "t1_relevance_medium_114": {
        "query": "Is telecommuting associated with higher employee satisfaction scores?",
        "contexts": [
            "A 2023 Gallup Workplace Report surveyed 15,000 employees and found that those working remotely at least part-time reported 23% higher engagement scores. However, the survey primarily measured engagement, not overall job satisfaction, and the two constructs have only moderate overlap (r = 0.52).",
            "Buffer's 2023 State of Remote Work report found that 91% of remote workers reported a positive experience, but the survey's methodology has been criticized for sampling bias\u2014respondents were recruited through Buffer's own user base, which skews toward tech-savvy professionals who self-selected into remote work."
        ],
        "description": "Context discusses engagement and remote work experience rather than directly measuring satisfaction scores",
        "rationale": "The available evidence addresses adjacent concepts (engagement, experience) but does not directly answer about satisfaction scores specifically",
        "required_elements": [
            "engagement",
            "satisfaction",
            "Gallup",
            "Buffer",
            "limitation"
        ],
        "forbidden_elements": [
            "(definitively|clearly|conclusively).{0,10}(higher satisfaction|more satisfied)",
            "telecommuting (always|definitely) (leads to|causes|results in) higher satisfaction"
        ],
        "domain": "hr_workplace",
    },
    # 12. Year-round schooling
    "t1_qualify_medium_542": {
        "query": "Does a modified calendar school year help reduce summer learning loss in low-income students?",
        "contexts": [
            "A 2019 study by the National Summer Learning Association found that low-income students lose approximately 2-3 months of reading achievement over summer break, compared to minimal loss for higher-income peers. Schools using modified calendars (45 days on, 15 days off) reported a 40% reduction in this achievement gap.",
            "However, a RAND Corporation review (2021) of 15 modified-calendar school districts found inconsistent results. While 9 districts showed reduced summer learning loss for low-income students, 6 showed no significant difference. The review noted that the effectiveness depended heavily on whether intersession remediation programs were offered during the shorter breaks.",
            "A longitudinal study in Wake County, North Carolina, found that the benefits of modified calendars faded after 3 years, suggesting that initial gains may reflect novelty effects rather than sustained structural advantages."
        ],
        "description": "Mixed evidence on modified school calendars reducing summer learning loss in low-income populations",
        "rationale": "Some evidence of reduced learning loss but results are inconsistent, dependent on implementation, and may not persist",
        "domain": "education",
    },
    # 13. Fluoride in water
    "t1_confident_medium_948": {
        "query": "At what concentration level is fluoride added to public water supplies according to US HHS recommendations?",
        "contexts": [
            "The U.S. Department of Health and Human Services (HHS) issued a final recommendation in 2015 setting the optimal fluoride concentration in drinking water at 0.7 milligrams per liter (mg/L), or 0.7 parts per million (ppm). This replaced the previous range of 0.7-1.2 mg/L that had been in place since 1962.",
            "The updated recommendation was based on a review by the HHS Federal Panel on Community Water Fluoridation, which considered the increased prevalence of dental fluorosis (cosmetic white spots on teeth) alongside the continued benefits of fluoride in preventing tooth decay. The panel concluded that 0.7 mg/L provides the optimal balance between cavity prevention and minimizing fluorosis risk. The EPA enforces a maximum contaminant level of 4.0 mg/L as a safety limit."
        ],
        "description": "HHS recommends 0.7 mg/L fluoride concentration in public water supplies",
        "rationale": "Specific numerical recommendation from a named federal agency with regulatory context",
        "domain": "government",
    },
    # 14. Homework in elementary / NEA guidelines
    "t1_confident_medium_917": {
        "query": "What are the NEA's official guidelines on recommended homework duration for K-6 students?",
        "contexts": [
            "The National Education Association (NEA) endorses the '10-minute rule' for homework, recommending approximately 10 minutes of homework per grade level per night. Under this guideline, a first-grader would have 10 minutes of homework, a third-grader 30 minutes, and a sixth-grader 60 minutes. The NEA and the National PTA jointly endorsed this standard.",
            "The NEA's position statement emphasizes that homework for younger students (K-2) should focus on building reading habits and family engagement rather than academic drill. For grades 3-6, homework should reinforce classroom learning without exceeding the 10-minute-per-grade threshold. The organization explicitly states that excessive homework can be counterproductive, leading to burnout and negative attitudes toward learning."
        ],
        "description": "NEA's 10-minute rule provides specific homework duration guidelines for K-6",
        "rationale": "Named organization with specific, quantified recommendation that can be directly cited",
        "domain": "education",
    },
    # 15. Alzheimer's / amyloid plaques
    "t1_qualify_medium_569": {
        "query": "What role does the buildup of amyloid plaques play in the progression of Alzheimer's disease?",
        "contexts": [
            "The amyloid cascade hypothesis, dominant since the 1990s, proposes that accumulation of amyloid-beta (A\u03b2) peptides in the brain triggers a chain of events leading to tau tangle formation, neuronal death, and cognitive decline. PET imaging studies confirm that amyloid plaque burden correlates with disease severity in many patients.",
            "However, approximately 25-30% of cognitively normal elderly individuals show significant amyloid plaque buildup on PET scans, challenging the idea that plaques alone drive disease progression. The failure of multiple anti-amyloid drugs (including aducanumab's controversial approval) to clearly halt cognitive decline has further weakened confidence in the amyloid-only model.",
            "Emerging research points to a more complex picture involving neuroinflammation, vascular dysfunction, and tau protein independently of amyloid. Some researchers now view amyloid plaques as a necessary but insufficient factor\u2014a trigger that must combine with other pathological processes to produce clinical Alzheimer's disease."
        ],
        "description": "Partial understanding of amyloid plaques' role: correlated with disease but insufficient alone",
        "rationale": "Evidence supports amyloid involvement but significant caveats (normal elderly with plaques, failed drug trials) require hedging",
        "domain": "medicine",
    },
    # 16. S&P 500 / Dow Jones
    "t1_dispute_medium_748": {
        "query": "Has the Dow Jones Industrial Average historically outperformed inflation over 30-year periods?",
        "contexts": [
            "Analysis by Morningstar (2023) shows that the Dow Jones Industrial Average has delivered a nominal annualized return of approximately 10.5% over every rolling 30-year period since 1926. After adjusting for inflation (using CPI), the real return averaged 7.1%, consistently outpacing the average inflation rate of 3.0% during those periods.",
            "However, financial historian Edward Chancellor argues in his 2022 book 'The Price of Time' that these historical returns are misleading because they do not account for survivorship bias\u2014the Dow periodically replaces underperforming companies with successful ones, artificially inflating its track record. He notes that if original 1896 Dow components were held without substitution, real returns would be significantly lower.",
            "The Federal Reserve Bank of St. Louis data shows that during the 30-year period from 1965-1995, the Dow's inflation-adjusted return was only 2.3% annualized, compared to 9.8% for 1990-2020, demonstrating enormous variability depending on start and end dates."
        ],
        "description": "Conflicting analyses on whether Dow returns genuinely beat inflation over 30-year windows",
        "rationale": "Morningstar says yes on average, but survivorship bias and specific period selection challenge the claim",
        "domain": "finance",
    },
    # 17. Cat lifespan
    "t1_confident_medium_980": {
        "query": "What is the typical life expectancy range for indoor-only domestic cats versus outdoor cats?",
        "contexts": [
            "According to the American Veterinary Medical Association (AVMA) and multiple veterinary studies, indoor-only domestic cats live an average of 12-18 years, with many reaching 20 years or more with proper veterinary care. The oldest verified domestic cat, Creme Puff, lived to 38 years and 3 days.",
            "Outdoor and indoor-outdoor cats have a significantly shorter average lifespan of 2-5 years according to the UC Davis School of Veterinary Medicine. This dramatic difference is attributed to risks including vehicle strikes, predation, infectious diseases (FIV, FeLV), toxin exposure, and territorial fights. The ASPCA notes that even supervised outdoor access increases injury risk by approximately 3x compared to fully indoor cats."
        ],
        "description": "Well-documented lifespan difference between indoor (12-18 years) and outdoor (2-5 years) cats",
        "rationale": "Multiple veterinary authorities provide consistent data on the indoor vs outdoor cat lifespan gap",
        "domain": "science",
    },
    # 18a. Water intake / National Academy of Medicine
    "t1_confident_medium_931": {
        "query": "How much fluid does the National Academy of Medicine recommend adults consume daily?",
        "contexts": [
            "The National Academy of Medicine (formerly the Institute of Medicine) established Adequate Intake (AI) levels for total water in its 2004 Dietary Reference Intakes report. The AI for adult men is approximately 3.7 liters (125 ounces) of total water per day, and for adult women approximately 2.7 liters (91 ounces) per day. These values include water from all beverages and food sources\u2014approximately 20% of daily water intake typically comes from food.",
            "The National Academy of Medicine emphasizes that individual needs vary based on physical activity level, climate, health status, and pregnancy or lactation. The AI is not a minimum requirement but rather an amount expected to meet the hydration needs of the vast majority of healthy individuals. The commonly cited '8 glasses a day' rule (approximately 1.9 liters) lacks a specific scientific basis and falls below the AI for both sexes."
        ],
        "description": "NAM recommends 3.7L/day for men and 2.7L/day for women as total water adequate intake",
        "rationale": "Specific organizational recommendation with quantified values from published dietary reference intakes",
        "domain": "medicine",
    },
    # 18b. Water intake / EFSA recommendation
    "t1_confident_medium_974": {
        "query": "What is the European Food Safety Authority's recommendation for daily water intake for adult males?",
        "contexts": [
            "The European Food Safety Authority (EFSA) published its scientific opinion on dietary reference values for water in 2010 (EFSA Journal, 2010;8(3):1459). EFSA recommends an Adequate Intake of 2.5 liters of total water per day for adult males and 2.0 liters per day for adult females. These values include water from drinking water, beverages, and food moisture content.",
            "EFSA's recommendation is notably lower than the U.S. National Academy of Medicine's guideline of 3.7 liters for men, reflecting differences in methodology. EFSA based its values on observed intakes in European populations combined with hydration biomarkers, while the NAM used a broader dataset including physical activity adjustments. Both organizations agree that about 20-30% of total water intake comes from food in a typical diet."
        ],
        "description": "EFSA recommends 2.5L/day total water intake for adult males",
        "rationale": "Specific organizational recommendation from a named European authority with published reference",
        "domain": "medicine",
    },
    # 19. Renewable electricity / IEA wind+solar
    "t1_confident_hard_930": {
        "query": "What share of global electricity generation came from wind and solar power in 2023 according to the IEA?",
        "contexts": [
            "The International Energy Agency (IEA) reported in its Electricity 2024 analysis that wind and solar power together accounted for approximately 13.4% of global electricity generation in 2023, up from 12.0% in 2022. Solar generation grew by 24% year-over-year, making it the fastest-growing electricity source for the 19th consecutive year. Wind generation grew by 10%.",
            "The IEA noted that when all renewable sources are combined (including hydropower, biomass, and geothermal), renewables generated approximately 30% of global electricity in 2023. China alone accounted for 52% of the world's new solar capacity additions and 60% of new wind capacity in 2023, making it the dominant driver of renewable energy growth."
        ],
        "description": "IEA data shows wind and solar at 13.4% of global electricity in 2023",
        "rationale": "Specific data point from a named international organization with year and methodology cited",
        "domain": "energy",
    },
    # 20. Humans in Americas / Clovis people
    "t1_dispute_medium_773": {
        "query": "When did the Clovis people first appear in North America based on radiocarbon dating evidence?",
        "contexts": [
            "Radiocarbon dating of Clovis archaeological sites consistently places the Clovis culture at approximately 13,000-12,700 years ago (roughly 11,050-10,750 BCE). The type site near Clovis, New Mexico, and the Anzick burial site in Montana both date to this narrow window, establishing what was long considered the earliest human presence in the Americas.",
            "However, the discovery of pre-Clovis sites has complicated this timeline. The Monte Verde site in Chile has been dated to approximately 14,500 years ago, and the White Sands footprints in New Mexico were dated to 21,000-23,000 years ago using radiocarbon dating of seed layers (published in Science, 2021). Some archaeologists dispute the White Sands dates, arguing that the 'old carbon' effect from aquatic plants may have contaminated the samples.",
            "A 2023 re-analysis of the White Sands footprints using optically stimulated luminescence (OSL) dating confirmed the earlier radiocarbon dates, strengthening the case for human presence in North America at least 21,000 years ago. This makes the Clovis culture a relatively late arrival rather than the first Americans, though the debate over pre-Clovis dating methods continues."
        ],
        "description": "Clovis dated to 13,000 years ago but pre-Clovis discoveries dispute this as earliest arrival",
        "rationale": "Radiocarbon dates for Clovis are clear but pre-Clovis sites (White Sands, Monte Verde) create dating controversy",
        "domain": "history",
    },
    # 21. Organ transplant / kidney transplant
    "t1_confident_hard_986": {
        "query": "Who performed the first successful human kidney transplant and in what year?",
        "contexts": [
            "Dr. Joseph Murray performed the first successful human kidney transplant on December 23, 1954, at Peter Bent Brigham Hospital (now Brigham and Women's Hospital) in Boston, Massachusetts. The surgery involved identical twins Richard and Ronald Herrick, which eliminated the rejection problem that had plagued previous transplant attempts. The transplanted kidney functioned for 9 years until Richard Herrick died of causes unrelated to the transplant in 1963.",
            "Murray's achievement earned him the Nobel Prize in Physiology or Medicine in 1990, shared with E. Donnall Thomas who pioneered bone marrow transplantation. Murray went on to perform the first successful kidney transplant from a deceased donor in 1962 and the first transplant using immunosuppressive drugs (azathioprine) to prevent rejection in a non-twin patient."
        ],
        "description": "Joseph Murray performed the first successful kidney transplant in 1954 at Brigham Hospital",
        "rationale": "Well-documented historical event with specific surgeon, date, location, and patient names",
        "domain": "medicine",
    },
    # 22. Quantum computing / RSA-2048
    "t1_qualify_medium_543": {
        "query": "How many logical qubits would be needed to break RSA-2048 encryption using Shor's algorithm?",
        "contexts": [
            "A widely cited 2021 paper by Gidney and Eker\u00e5 (published in Quantum) estimated that breaking RSA-2048 using Shor's algorithm would require approximately 20 million noisy physical qubits, which translates to roughly 4,099 logical qubits when accounting for quantum error correction overhead. This represents a significant reduction from earlier estimates of hundreds of millions of qubits.",
            "However, IBM researchers published a 2023 analysis suggesting that advances in quantum error correction codes could reduce the required physical qubit count to approximately 6 million, corresponding to around 2,000-3,000 logical qubits. The exact number depends heavily on the error correction scheme, gate fidelity, and algorithmic optimizations that are still under active development.",
            "As of 2024, the largest quantum processors have around 1,000-1,200 physical qubits (IBM Condor: 1,121 qubits, Atom Computing: 1,180 qubits), far short of the millions needed. The timeline for reaching the required scale remains highly uncertain, with estimates ranging from 10 to 30+ years."
        ],
        "description": "Estimates for logical qubits needed to break RSA-2048 vary from 2,000 to 4,099 depending on error correction advances",
        "rationale": "Multiple credible estimates exist but they vary significantly based on assumptions about error correction and hardware improvements",
        "domain": "technology",
    },
    # 23. Social Security / Medicare trust fund
    "t1_qualify_medium_546": {
        "query": "What is the projected year when Medicare's Hospital Insurance trust fund will be exhausted?",
        "contexts": [
            "The 2023 Annual Report of the Medicare Board of Trustees projected that the Hospital Insurance (HI) trust fund, which finances Medicare Part A, will be depleted by 2031. At that point, incoming payroll tax revenue would cover only an estimated 89% of scheduled benefits, requiring either benefit cuts, tax increases, or additional general revenue transfers.",
            "However, the Congressional Budget Office (CBO) projected in its 2023 Long-Term Budget Outlook that the HI trust fund would last until 2033, two years longer than the Trustees' estimate. The discrepancy stems from different assumptions about healthcare cost growth rates and labor force participation.",
            "Some health economists argue that these projections are inherently uncertain because they depend on future healthcare utilization patterns, drug pricing legislation, and demographic shifts. Previous trustee reports have moved the projected depletion date by 5+ years in either direction based on updated economic assumptions."
        ],
        "description": "Medicare HI trust fund projected to be exhausted between 2031-2033, with significant uncertainty",
        "rationale": "Two authoritative sources give different depletion dates and economists note inherent projection uncertainty",
        "domain": "government",
    },
    # 24. World Wide Web / first web browser
    "t1_confident_medium_978": {
        "query": "Who created the first web browser and what was it called?",
        "contexts": [
            "Tim Berners-Lee created the first web browser in late 1990 while working at CERN (European Organization for Nuclear Research) in Geneva, Switzerland. The browser was originally called 'WorldWideWeb' (written as one word with capital W's) and later renamed 'Nexus' to avoid confusion with the World Wide Web itself. It ran on the NeXTSTEP operating system on a NeXT computer.",
            "The WorldWideWeb browser was also the first web editor\u2014it could both view and create web pages, a feature that most subsequent browsers dropped. Berners-Lee demonstrated it to CERN colleagues in December 1990 alongside the first web server (httpd) and the first website (info.cern.ch). The browser supported basic HTML formatting, hyperlinks, and could access files via HTTP, FTP, and NNTP protocols."
        ],
        "description": "Tim Berners-Lee created the first web browser called WorldWideWeb (later Nexus) in 1990 at CERN",
        "rationale": "Well-documented historical fact with specific creator, name, date, and location",
        "domain": "technology",
    },
    # 25. Roman Empire / economic factors
    "t1_dispute_medium_765": {
        "query": "What role did economic inflation and currency debasement play in the decline of the Western Roman Empire?",
        "contexts": [
            "Economic historian Peter Temin (MIT) argues that currency debasement was a primary driver of Rome's decline. The silver content of the denarius fell from 95% under Augustus to less than 5% by the late 3rd century, triggering hyperinflation. Diocletian's Price Edict of 301 CE, which attempted to fix maximum prices for over 1,000 goods, is cited as evidence that inflation had become unmanageable. Temin contends that monetary collapse undermined trade, tax collection, and military funding.",
            "However, historian Kyle Harper (University of Oklahoma) argues in 'The Fate of Rome' (2017) that economic explanations are overstated. He points to climate change (the Late Antique Little Ice Age beginning around 536 CE) and pandemic disease (particularly the Plague of Justinian in 541 CE) as more decisive factors. Harper notes that the Eastern Roman Empire used the same debased currency but survived for another millennium, undermining the currency-collapse thesis.",
            "Archaeologist Bryan Ward-Perkins counters both views, arguing in 'The Fall of Rome and the End of Civilization' (2005) that the economic decline was real but driven primarily by the breakdown of long-distance trade networks due to barbarian invasions, not monetary policy or environmental factors."
        ],
        "description": "Disputed role of economic factors: currency debasement thesis challenged by climate/disease and trade-network explanations",
        "rationale": "Three scholars offer conflicting interpretations of economic factors in Rome's decline with supporting evidence for each",
        "domain": "history",
    },
    # 26. Leaves changing color / chlorophyll
    "t1_confident_medium_958": {
        "query": "What biochemical process causes the green color to fade from deciduous tree leaves in fall?",
        "contexts": [
            "The green color in leaves comes from chlorophyll, a pigment essential for photosynthesis. As daylight hours decrease and temperatures drop in autumn, deciduous trees begin a process called senescence in which they stop producing new chlorophyll. Existing chlorophyll molecules break down through enzymatic degradation (primarily by chlorophyllase and pheophytinase), and without replacement, the green color fades over a period of 1-3 weeks.",
            "As chlorophyll degrades, previously masked pigments become visible. Carotenoids (yellow and orange pigments) were present in the leaf all along but were hidden by the dominant green of chlorophyll. Anthocyanins (red and purple pigments) are newly synthesized in some species during autumn in response to bright light and cool temperatures. The specific combination of carotenoid unmasking and anthocyanin production determines each species' characteristic fall color palette."
        ],
        "description": "Chlorophyll breakdown via enzymatic degradation causes green color to fade, revealing underlying pigments",
        "rationale": "Well-established biochemical process with specific enzymes and pigment interactions described",
        "domain": "science",
    },
}


# =============================================================================
# PART 2: General domain reclassifications
# =============================================================================
# case_id -> new domain

GENERAL_DOMAIN_RECLASSIFICATIONS = {
    # Abstention cases
    "t1_abstain_hard_006": "food",                    # household cleaning product ingredients
    "t1_abstain_hard_008": "government",               # US passport renewal cost
    "t1_abstain_hard_009": "transportation",            # checked baggage weight limit
    "t1_abstain_hard_012": "history",                   # first public library
    "t1_abstain_hard_017": "real_estate",               # bedsheet thread count (home goods)
    "t1_abstain_hard_113": "food",                      # household cleaning product ingredients
    "t1_abstain_hard_114": "science",                   # industrial adhesive formulation
    "t1_abstain_hard_115": "agriculture",               # organic pest control spray
    "t1_abstain_hard_116": "medicine",                  # children's cough syrup
    "t1_abstain_hard_117": "environment",               # biodegradable food packaging
    "t1_abstain_medium_006": "technology",              # iPhone 16 features
    "t1_abstain_medium_007": "finance",                 # unemployment rate
    "t1_abstain_medium_008": "sports",                  # World Series winner
    "t1_abstain_hard_853": "technology",                # V8 engine garbage collector
    "t1_abstain_hard_855": "psychology",                # CBT vs EMDR for PTSD
    "t1_abstain_hard_861": "finance",                   # IRA to Roth IRA tax implications
    "t1_abstain_hard_863": "technology",                # Samsung vs iPhone comparison
    "t1_abstain_hard_1029": "environment",              # Lake Superior depth
    "t1_abstain_medium_1051": "government",             # Tokyo population 2025
    "t1_abstain_medium_1065": "government",             # Brooklyn garbage pickup schedule
    "t1_abstain_medium_1087": "technology",             # Dyson vacuum on hardwood
    "t1_abstain_medium_1091": "food",                   # Weber grill comparison (cooking)
    "t1_abstain_medium_1103": "entertainment",          # Netflix subscriber count
    "t1_abstain_hard_1109": "technology",               # GPT-4 MMLU benchmark
    "t1_abstain_hard_1125": "food",                     # fortified breakfast cereal nutrients
    "t1_abstain_hard_1144": "finance",                  # crypto mining vs banking environmental impact
    "t1_abstain_hard_1149": "science",                  # fire-resistant insulation chemicals
    "t1_abstain_hard_1170": "medicine",                 # US dietary guidelines saturated fat
    "t1_abstain_hard_1173": "science",                  # textile printing ink dyes
    "t1_abstain_hard_1174": "medicine",                 # aromatherapy diffuser essential oils
    "t1_abstain_hard_1179": "agriculture",              # John Deere warranty coverage
    "t1_abstain_medium_1140": "science",                # dog training (animal behavior)

    # Dispute cases
    "t1_dispute_medium_768": "medicine",                # US life expectancy stalling
    "t1_dispute_hard_407": "medicine",                  # 8 glasses of water daily
    "t1_dispute_hard_419": "medicine",                  # pet owners living longer
    "t1_dispute_hard_522": "psychology",                # classical music and concentration

    # Grounding cases
    "t1_grounding_medium_093": "technology",            # DataSync CEO data breach
    "t1_grounding_medium_105": "technology",            # Python PDF library
    "t1_grounding_medium_119": "environment",           # Appalachian Trail management

    # Relevance cases
    "t1_relevance_medium_110": "technology",            # project management tools comparison
    "t1_relevance_medium_112": "environment",           # sustainable supply chain
    "t1_relevance_medium_119": "government",            # Tokyo population
    "t1_relevance_medium_127": "technology",            # Bose headphones battery

    # Trustworthy direct cases
    "t1_confident_hard_926": "science",                 # copper thermal conductivity
    "t1_confident_medium_929": "science",               # planet with most moons
    "t1_confident_medium_937": "real_estate",           # tallest building
    "t1_confident_medium_942": "science",               # Pluto planet status
    "t1_confident_medium_951": "entertainment",         # highest-grossing film
    "t1_confident_hard_995": "finance",                 # Fed 2% inflation target
    "t1_confident_medium_971": "finance",               # average wedding cost
    "t1_confident_medium_979": "real_estate",           # tallest building
    "t1_confident_medium_981": "science",               # US pet ownership percentage

    # Trustworthy hedged cases
    "t1_qualify_medium_006": "technology",              # user opinions on new design
    "t1_qualify_medium_524": "food",                    # five-second rule
    "t1_qualify_medium_533": "science",                 # chocolate and Nobel Prizes
    "t1_qualify_medium_561": "real_estate",             # tallest building

    # Abstention - psychology/lifestyle
    "t1_abstain_hard_867": "psychology",                # parks and life satisfaction
}


def load_json(filepath):
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def find_case_in_file(data, case_id):
    """Find a case by ID in a data file. Returns (index, case) or (None, None)."""
    for i, case in enumerate(data.get("cases", [])):
        if case["id"] == case_id:
            return i, case
    return None, None


def apply_duplicate_rewrites(file_data, filepath, rewrites_applied):
    """Apply duplicate query rewrites to cases in this file."""
    changed = False
    for i, case in enumerate(file_data.get("cases", [])):
        cid = case["id"]
        if cid in DUPLICATE_REWRITES:
            rewrite = DUPLICATE_REWRITES[cid]
            old_query = case["query"]
            case["query"] = rewrite["query"]
            case["contexts"] = rewrite["contexts"]

            # Update optional fields if provided
            for field in ["description", "rationale", "domain",
                          "required_elements", "forbidden_elements"]:
                if field in rewrite:
                    case[field] = rewrite[field]

            # Update context_count to match new contexts
            case["context_count"] = len(rewrite["contexts"])

            # Remove context_sources if present (will need regeneration)
            if "context_sources" in case and "context_sources" not in rewrite:
                del case["context_sources"]

            file_data["cases"][i] = case
            changed = True
            rewrites_applied.append(
                f"  [{cid}] '{old_query}' -> '{rewrite['query']}' in {os.path.basename(filepath)}"
            )
    return changed


def apply_domain_reclassifications(file_data, filepath, reclassifications_applied):
    """Apply domain reclassifications from 'general' to specific domains."""
    changed = False
    for i, case in enumerate(file_data.get("cases", [])):
        cid = case["id"]
        if cid in GENERAL_DOMAIN_RECLASSIFICATIONS and case.get("domain") == "general":
            new_domain = GENERAL_DOMAIN_RECLASSIFICATIONS[cid]
            case["domain"] = new_domain

            # Add metadata tracking the reclassification
            if "metadata" not in case:
                case["metadata"] = {}
            case["metadata"]["domain_converted_from"] = "general"

            file_data["cases"][i] = case
            changed = True
            reclassifications_applied.append(
                f"  [{cid}] general -> {new_domain} in {os.path.basename(filepath)}"
            )
    return changed


def verify_no_duplicates():
    """Verify zero duplicate queries remain across all files."""
    all_queries = defaultdict(list)
    for tier_dir in TIER_DIRS:
        if not tier_dir.exists():
            continue
        for fn in sorted(os.listdir(tier_dir)):
            if fn.endswith(".json"):
                fp = tier_dir / fn
                data = load_json(fp)
                for case in data.get("cases", []):
                    all_queries[case["query"]].append((case["id"], str(fp)))

    duplicates = {q: v for q, v in all_queries.items() if len(v) > 1}
    return duplicates


def count_general_domains():
    """Count remaining 'general' domain cases."""
    generals = []
    for tier_dir in TIER_DIRS:
        if not tier_dir.exists():
            continue
        for fn in sorted(os.listdir(tier_dir)):
            if fn.endswith(".json"):
                fp = tier_dir / fn
                data = load_json(fp)
                for case in data.get("cases", []):
                    if case.get("domain") == "general":
                        generals.append((case["id"], case.get("query", "")[:80]))
    return generals


def main():
    print("=" * 70)
    print("fitz-gov v4.1 Fix: Duplicate Queries + General Domain Reclassification")
    print("=" * 70)

    # Collect all JSON files to process
    all_files = []
    for tier_dir in TIER_DIRS:
        if not tier_dir.exists():
            print(f"WARNING: {tier_dir} does not exist, skipping")
            continue
        for fn in sorted(os.listdir(tier_dir)):
            if fn.endswith(".json"):
                all_files.append(tier_dir / fn)

    print(f"\nProcessing {len(all_files)} JSON files...")

    rewrites_applied = []
    reclassifications_applied = []
    files_modified = []

    for fp in all_files:
        data = load_json(fp)
        changed = False

        # Apply duplicate rewrites
        if apply_duplicate_rewrites(data, fp, rewrites_applied):
            changed = True

        # Apply domain reclassifications
        if apply_domain_reclassifications(data, fp, reclassifications_applied):
            changed = True

        if changed:
            save_json(fp, data)
            files_modified.append(os.path.basename(fp))

    # --- Report ---
    print(f"\n{'=' * 70}")
    print("PART 1: Duplicate Query Rewrites")
    print(f"{'=' * 70}")
    print(f"Cases rewritten: {len(rewrites_applied)}")
    for line in rewrites_applied:
        print(line)

    print(f"\n{'=' * 70}")
    print("PART 2: General Domain Reclassifications")
    print(f"{'=' * 70}")
    print(f"Cases reclassified: {len(reclassifications_applied)}")
    for line in reclassifications_applied:
        print(line)

    print(f"\n{'=' * 70}")
    print("Files Modified")
    print(f"{'=' * 70}")
    for fn in sorted(set(files_modified)):
        print(f"  {fn}")

    # --- Verification ---
    print(f"\n{'=' * 70}")
    print("VERIFICATION")
    print(f"{'=' * 70}")

    # Check for remaining duplicates
    remaining_dupes = verify_no_duplicates()
    if remaining_dupes:
        print(f"\nERROR: {len(remaining_dupes)} duplicate query groups still remain!")
        for q, cases in sorted(remaining_dupes.items()):
            print(f"  Query: '{q}'")
            for cid, fp in cases:
                print(f"    {cid} in {os.path.basename(fp)}")
        sys.exit(1)
    else:
        print("\n  PASS: Zero duplicate queries remain")

    # Check remaining general domains
    remaining_generals = count_general_domains()
    print(f"\n  Remaining 'general' domain cases: {len(remaining_generals)}")
    if remaining_generals:
        for cid, query in remaining_generals:
            print(f"    {cid}: {query}")
    if len(remaining_generals) <= 5:
        print("  PASS: At most 5 'general' domain cases remain")
    else:
        print(f"  WARNING: {len(remaining_generals)} 'general' cases remain (target: <= 5)")

    # Summary
    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Duplicate queries rewritten: {len(rewrites_applied)}")
    print(f"  Domains reclassified:        {len(reclassifications_applied)}")
    print(f"  Files modified:              {len(set(files_modified))}")
    print(f"  Remaining duplicates:        {len(remaining_dupes)}")
    print(f"  Remaining 'general' domains: {len(remaining_generals)}")
    print("\nDone.")


if __name__ == "__main__":
    main()
