"""
Generate 70 new MEDIUM difficulty trustworthy_hedged cases (IDs 516-585)
and append them to data/tier1_core/trustworthy_hedged.json.

Subcategory distribution (70 total):
  evidence_quality: 7, hedged_evidence: 5, different_aspects: 5,
  causal_uncertainty: 5, mixed_evidence: 5, temporal_uncertainty: 5,
  version_overlap: 4, methodology_difference: 4, stale_source: 4,
  evolving_facts: 4, entity_ambiguity: 3, partial_answer: 3,
  scope_condition: 3, numerical_near_miss: 3, cross_source_partial: 3,
  implicit_assumptions: 3, adjacent_entity: 2, cross_domain_transfer: 2

Multi-source: 20 of 70 have context_sources (list of strings).
Domain spread: 18 domains, max 5 per domain.
Query type: what <= 17, how >= 14, is/does >= 14, why/should >= 10, when/who/which >= 7.
"""

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_FILE = os.path.join(PROJECT_ROOT, "data", "tier1_core", "trustworthy_hedged.json")


def make_case(
    num, subcategory, query, contexts, description, rationale,
    domain, query_type, source_type="single", reasoning_type="evaluative",
    evidence_pattern="partial", context_sources=None
):
    """Build a single trustworthy_hedged case dict."""
    case = {
        "id": f"t1_qualify_medium_{num}",
        "difficulty": "medium",
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
        "evidence_pattern": evidence_pattern,
        "category": "trustworthy_hedged",
        "evaluation_config": {"mode": "governance", "check_mode_match": True},
    }
    if context_sources is not None:
        case["context_sources"] = context_sources
    return case


def build_cases():
    cases = []

    # ================================================================
    # EVIDENCE_QUALITY (7 cases)
    # domains: medicine, psychology, transportation, agriculture, law, history, food
    # query_types: does, is, how, why, how, when, is
    # multi_source: 516, 517
    # ================================================================

    cases.append(make_case(
        516, "evidence_quality",
        "Does vitamin C prevent the common cold?",
        [
            "A meta-analysis of 29 trials found that vitamin C supplementation did not significantly reduce the incidence of colds in the general population, but reduced duration by 8% in adults and 14% in children.",
            "A Finnish study found that 200mg daily vitamin C reduced cold duration in marathon runners by 50%, though the sample size was limited to only 46 participants and has not been widely replicated."
        ],
        "Evidence partially supports benefit but with significant caveats",
        "Meta-analysis shows limited general benefit; specific populations may benefit more but evidence is weak",
        "medicine", "does",
        source_type="multi_source",
        context_sources=["Cochrane Systematic Review (2023)", "University of Helsinki Study (2022)"]
    ))

    cases.append(make_case(
        517, "evidence_quality",
        "Is meditation effective for treating anxiety disorders?",
        [
            "A 2023 systematic review of 47 randomized controlled trials found moderate evidence that mindfulness meditation reduces anxiety symptoms, with an effect size of 0.55, comparable to CBT in some studies but with high heterogeneity across trials.",
            "The American Psychiatric Association notes that while meditation shows promise as an adjunct therapy, most studies have methodological limitations including small sample sizes and short follow-up periods."
        ],
        "Meditation shows moderate evidence for anxiety but study quality varies",
        "Moderate effect sizes suggest benefit but methodological limitations temper confidence in the magnitude of effect",
        "psychology", "is",
        source_type="multi_source",
        context_sources=["Journal of Clinical Psychology Review (2023)", "APA Practice Guidelines (2024)"]
    ))

    cases.append(make_case(
        518, "evidence_quality",
        "How effective are speed cameras at reducing traffic fatalities?",
        [
            "A Cochrane review analyzing 35 studies found that speed cameras were associated with an 11-44% reduction in fatalities and an 8-49% reduction in injuries near camera sites, though the wide range reflects significant variation in study quality and methodology across countries."
        ],
        "Speed cameras show promise but evidence quality varies widely",
        "The broad confidence interval and heterogeneous study designs mean a definitive percentage reduction cannot be stated with certainty",
        "transportation", "how"
    ))

    cases.append(make_case(
        519, "evidence_quality",
        "Why do some agricultural studies show conflicting results on glyphosate safety?",
        [
            "The International Agency for Research on Cancer classified glyphosate as 'probably carcinogenic' in 2015 based on limited evidence in humans and sufficient evidence in animals. However, regulatory agencies including the EPA, EFSA, and WHO/FAO Joint Meeting concluded glyphosate is unlikely to pose a carcinogenic risk at typical exposure levels.",
            "A 2023 review noted that studies reaching different conclusions often used different exposure levels, test species, and endpoints, making direct comparison difficult."
        ],
        "Glyphosate safety assessments differ based on methodology and exposure assumptions",
        "The disagreement stems from different analytical frameworks rather than straightforward contradictions in evidence",
        "agriculture", "why",
        source_type="multi_source",
        reasoning_type="causal",
        context_sources=["IARC Monograph Volume 112 (2015)", "EPA Glyphosate Interim Registration Review (2023)"]
    ))

    cases.append(make_case(
        520, "evidence_quality",
        "How reliable are polygraph tests for detecting deception?",
        [
            "The National Academy of Sciences concluded that polygraph testing has inherent ambiguity, with accuracy estimates ranging from 81-91% for specific-incident testing, but noted these figures may overstate real-world accuracy due to controlled testing conditions in studies.",
            "The American Psychological Association states that most psychologists find little evidence polygraph tests can accurately detect lies, as measured physiological responses can be influenced by anxiety, medications, and countermeasures."
        ],
        "Polygraph accuracy is disputed and context-dependent",
        "Lab accuracy estimates are higher than real-world performance, and the scientific community remains skeptical of practical reliability",
        "law", "how",
        source_type="multi_source",
        context_sources=["National Academy of Sciences Report", "APA Position Statement on Polygraphs"]
    ))

    cases.append(make_case(
        521, "evidence_quality",
        "When did ancient civilizations first develop writing systems?",
        [
            "The earliest confirmed writing system is Sumerian cuneiform, dating to approximately 3400 BCE in Mesopotamia, initially used for recording grain transactions. However, proto-writing symbols found at Jiahu in China and Vinca symbols in southeastern Europe date to 6600 BCE and 5500 BCE respectively, though scholars debate whether these constitute true writing.",
            "Egyptian hieroglyphs emerged around 3200 BCE, and the Indus Valley script around 2600 BCE, but the Indus script remains undeciphered, complicating classification of whether it represents full writing or a symbol system."
        ],
        "Writing origins are debated depending on how 'writing' is defined",
        "The answer depends on whether proto-writing counts; confirmed writing dates to 3400 BCE but earlier symbol systems complicate the picture",
        "history", "when",
        reasoning_type="factual"
    ))

    cases.append(make_case(
        522, "evidence_quality",
        "Is organic food more nutritious than conventionally grown food?",
        [
            "A Stanford meta-analysis of 237 studies found no strong evidence that organic foods are significantly more nutritious than conventional alternatives, though organic produce had 30% lower pesticide residues.",
            "A subsequent British Journal of Nutrition meta-analysis found organic crops had 18-69% higher concentrations of certain antioxidants, directly contradicting the Stanford findings on nutritional equivalence."
        ],
        "Organic nutrition benefits are debated with conflicting meta-analyses",
        "Two major meta-analyses reach different conclusions on antioxidant content; pesticide reduction is clearer but nutritional superiority remains contested",
        "food", "is"
    ))

    # ================================================================
    # HEDGED_EVIDENCE (5 cases)
    # domains: hr_workplace, general, social_media, science, real_estate
    # query_types: how, is, why, how, should
    # multi_source: 525
    # ================================================================

    cases.append(make_case(
        523, "hedged_evidence",
        "How much does remote work affect employee productivity?",
        [
            "A Stanford study of 16,000 workers found remote employees were 13% more productive than office-based peers, primarily due to fewer breaks and sick days. However, a subsequent study by the same researcher found fully remote work showed a 10-20% productivity decline for collaborative tasks requiring real-time coordination."
        ],
        "Remote work productivity depends heavily on task type",
        "Individual task productivity appears higher remotely, but collaborative work may suffer, making a blanket statement impossible",
        "hr_workplace", "how",
        source_type="multi_source",
        context_sources=["Stanford Institute for Economic Policy Research (2023)", "Stanford WFH Research Update (2024)"]
    ))

    cases.append(make_case(
        524, "hedged_evidence",
        "Is the five-second rule for dropped food scientifically valid?",
        [
            "A Rutgers University study tested four foods on four surfaces and found that bacteria transfer begins on contact, with moisture and surface type mattering more than time elapsed. However, transfer increased significantly after 30 seconds compared to under 1 second, suggesting brief contact does result in less contamination.",
            "The study noted that tile and stainless steel transferred bacteria faster than carpet and wood, and that watermelon picked up far more bacteria than gummy candy, making food type and surface more relevant than the arbitrary five-second threshold."
        ],
        "The five-second rule is oversimplified but contact time does affect contamination levels",
        "Some scientific basis exists for faster pickup meaning less bacteria, but the rule ignores more important variables like surface type and food moisture",
        "general", "is"
    ))

    cases.append(make_case(
        525, "hedged_evidence",
        "Why do some viral social media health trends persist despite being debunked?",
        [
            "A 2023 MIT study found that false health claims spread 70% faster than corrections on social media platforms, partly because they trigger stronger emotional reactions. The algorithmic amplification of engagement-driven content further accelerates misinformation spread.",
            "Research from the Digital Health Lab at Stanford found that 62% of users who shared debunked health content were unaware of corrections, and that trust in the original sharer mattered more than the content's source or accuracy."
        ],
        "Health misinformation persists due to emotional engagement and algorithmic amplification",
        "The causal factors are complex: emotional resonance, algorithm design, and social trust networks all contribute, but quantifying each factor's relative weight remains difficult",
        "social_media", "why",
        source_type="multi_source",
        reasoning_type="causal",
        context_sources=["MIT Media Lab Misinformation Study (2023)", "Stanford Digital Health Lab Report (2023)"]
    ))

    cases.append(make_case(
        526, "hedged_evidence",
        "How accurate are commercial DNA ancestry tests?",
        [
            "A 2023 comparison study sent identical DNA samples to five major ancestry testing companies and found that ethnicity estimates varied by up to 15 percentage points for the same individual across providers. Companies use proprietary reference populations, and results can shift when databases are updated.",
            "The tests accurately identify close relatives (parent, sibling, first cousin) with over 99% reliability, but regional ancestry breakdowns become increasingly imprecise beyond continental-level designations."
        ],
        "DNA ancestry tests are reliable for close relationships but imprecise for regional ethnicity estimates",
        "The technology is accurate for some purposes but the consumer-facing ancestry percentages are approximations that vary by provider",
        "science", "how"
    ))

    cases.append(make_case(
        527, "hedged_evidence",
        "Should homebuyers prefer fixed-rate or adjustable-rate mortgages in a rising rate environment?",
        [
            "Historical analysis from Freddie Mac shows that borrowers who chose 5/1 ARMs between 2010-2019 saved an average of $15,400 over the first five years compared to 30-year fixed rates, but 23% of those ARMs adjusted upward by more than 2 percentage points at the first reset, significantly increasing monthly payments."
        ],
        "ARMs historically saved money initially but carry meaningful rate-reset risk",
        "Short-term savings are documented but the risk of significant payment increases after adjustment makes a blanket recommendation inappropriate",
        "real_estate", "should"
    ))

    # ================================================================
    # DIFFERENT_ASPECTS (5 cases)
    # domains: transportation, agriculture, education, sports, environment
    # query_types: is, how, should, how, how
    # multi_source: 528, 529
    # ================================================================

    cases.append(make_case(
        528, "different_aspects",
        "Is hydrogen fuel a viable alternative to battery electric vehicles?",
        [
            "Hydrogen fuel cell vehicles offer refueling times of 3-5 minutes compared to 30-60 minutes for fast-charging EVs, and maintain range better in cold weather. However, hydrogen production currently relies 95% on natural gas reforming, producing significant CO2 emissions.",
            "Battery EVs achieve 77% well-to-wheel energy efficiency compared to just 25-35% for hydrogen fuel cell vehicles, meaning hydrogen requires roughly three times more primary energy to travel the same distance."
        ],
        "Hydrogen has convenience advantages but major efficiency and production drawbacks",
        "Different aspects favor different technologies: refueling speed favors hydrogen, but energy efficiency and current production methods strongly favor battery EVs",
        "transportation", "is",
        source_type="multi_source",
        context_sources=["International Energy Agency Transport Analysis (2024)", "Department of Energy Fuel Cell Report (2023)"]
    ))

    cases.append(make_case(
        529, "different_aspects",
        "How does vertical farming compare to traditional agriculture?",
        [
            "Vertical farms can produce 10-20 times more crop yield per square meter than traditional farming and use 95% less water through recirculating hydroponic systems. They eliminate the need for pesticides and can operate year-round regardless of climate.",
            "Energy costs for vertical farming remain 8-15 times higher than traditional agriculture per kilogram of produce. Current vertical farming is economically viable only for leafy greens and herbs, not staple crops like wheat, rice, or corn."
        ],
        "Vertical farming excels in water and space efficiency but is limited by energy costs and crop range",
        "Each farming method has clear advantages in different dimensions; the answer must address both the significant benefits and the substantial limitations",
        "agriculture", "how",
        source_type="multi_source",
        context_sources=["Association for Vertical Farming Report (2024)", "USDA Agricultural Research Service Study (2023)"]
    ))

    cases.append(make_case(
        530, "different_aspects",
        "Should parents choose homeschooling over public school education?",
        [
            "National Home Education Research Institute data shows homeschooled students score 15-30 percentile points above public school students on standardized tests. However, critics note this comparison is skewed because homeschooling families tend to be wealthier and more educated than average.",
            "A 2022 study on socialization found that homeschooled children participated in an average of 5.2 extracurricular activities per week, but scored lower on measures of exposure to diverse perspectives and conflict resolution with peers."
        ],
        "Homeschooling shows academic advantages but with demographic confounders and socialization trade-offs",
        "Academic results favor homeschooling but selection bias and socialization differences mean a simple comparison is misleading",
        "education", "should",
        source_type="multi_source",
        context_sources=["National Home Education Research Institute Data (2023)", "Journal of School Psychology Socialization Study (2022)"]
    ))

    cases.append(make_case(
        531, "different_aspects",
        "How do plant-based meat alternatives compare to traditional meat on nutrition and sustainability?",
        [
            "Life cycle analyses show that plant-based meat substitutes produce 30-90% fewer greenhouse gas emissions and use 47-99% less land than conventional beef production per serving. Water usage is typically 72-99% lower depending on the product and the animal protein being replaced.",
            "Nutritionally, many plant-based meats contain comparable protein levels but are significantly higher in sodium (300-500mg vs. 60-80mg per serving) and more highly processed than whole meat. They often lack vitamin B12, iron, and zinc bioavailability found in animal protein without fortification."
        ],
        "Plant-based meats win on sustainability metrics but have nutritional trade-offs",
        "Each option excels on different dimensions: environmental impact strongly favors plant-based, but nutritional completeness and processing concerns favor traditional meat in some respects",
        "food", "how"
    ))

    cases.append(make_case(
        532, "different_aspects",
        "How does nuclear energy compare to solar for decarbonizing the grid?",
        [
            "Nuclear power plants produce electricity with a capacity factor of 92-93%, operating nearly continuously, compared to solar's 20-25% capacity factor. Nuclear requires 75 times less land per megawatt-hour than utility-scale solar farms.",
            "Solar energy's levelized cost has dropped 89% since 2010 to $30-50 per MWh, while new nuclear costs $100-180 per MWh. Solar projects deploy in 1-2 years versus 10-15 years for nuclear plants."
        ],
        "Nuclear offers reliability and density advantages while solar wins on cost and deployment speed",
        "Neither technology is categorically superior; the answer should hedge by noting each excels on different metrics critical for grid decarbonization",
        "environment", "how"
    ))

    # ================================================================
    # CAUSAL_UNCERTAINTY (5 cases)
    # domains: general, psychology, history, social_media, environment
    # query_types: why, does, why, does, why
    # multi_source: 537
    # ================================================================

    cases.append(make_case(
        533, "causal_uncertainty",
        "Why do countries with higher chocolate consumption win more Nobel Prizes?",
        [
            "A study published in the New England Journal of Medicine found a strong linear correlation (r=0.791) between per-capita chocolate consumption and the number of Nobel laureates per 10 million population across 23 countries.",
            "Both chocolate consumption and Nobel Prize counts correlate strongly with national wealth, education spending, and research infrastructure. Switzerland leads in both metrics and also has the highest GDP per capita in the dataset."
        ],
        "Spurious correlation driven by underlying wealth and education confounders",
        "The correlation is real but almost certainly driven by confounding variables related to national prosperity; the answer should explain this rather than suggest chocolate causes Nobel achievement",
        "general", "why",
        reasoning_type="causal"
    ))

    cases.append(make_case(
        534, "causal_uncertainty",
        "Does playing video games improve cognitive abilities?",
        [
            "A University of Geneva meta-analysis of 116 studies found that action video game players showed 10-20% better performance on attention, spatial reasoning, and task-switching tests compared to non-gamers. However, the researchers noted that people with naturally superior cognitive abilities may be drawn to gaming, making causation difficult to establish."
        ],
        "Gamers show better cognition but self-selection bias clouds causation",
        "The association is well-documented but whether gaming causes improvement or cognitively gifted individuals prefer gaming remains unclear",
        "psychology", "does",
        reasoning_type="causal"
    ))

    cases.append(make_case(
        535, "causal_uncertainty",
        "Why did the Roman Empire decline and eventually fall?",
        [
            "Edward Gibbon's seminal work attributed Rome's decline primarily to moral decay and the spread of Christianity, while modern historians emphasize economic factors including currency debasement, trade disruption, and unsustainable military spending that consumed up to 75% of imperial revenue by the 4th century.",
            "Recent archaeological evidence suggests climate change played a significant role: a volcanic winter in 536 CE triggered crop failures across the Mediterranean, and the Justinianic Plague (541 CE) killed an estimated 25-50 million people, permanently weakening the empire's tax base and military recruitment capacity."
        ],
        "Multiple interacting causes contributed to Rome's fall with no single dominant factor",
        "Historians have proposed over 200 distinct causes; the answer should present the major theories while acknowledging that mono-causal explanations are inadequate",
        "history", "why",
        reasoning_type="causal"
    ))

    cases.append(make_case(
        536, "causal_uncertainty",
        "Does influencer marketing actually drive purchase decisions?",
        [
            "A 2024 Nielsen study found that 61% of consumers trust influencer recommendations over brand advertising, and influencer marketing campaigns generated an average ROI of $5.78 per dollar spent. However, attribution modeling showed that only 23% of purchases could be directly traced to influencer content.",
            "The remaining purchase attribution was confounded by concurrent brand campaigns, organic search, and peer recommendations, making it difficult to isolate the influencer's specific causal contribution to sales."
        ],
        "Influencer marketing correlates with sales but direct causal attribution is limited",
        "High ROI figures may overstate influencer impact because multi-touch attribution is inherently imprecise; the answer should note the measurement challenges",
        "social_media", "does",
        reasoning_type="causal"
    ))

    cases.append(make_case(
        537, "causal_uncertainty",
        "Why have global insect populations declined over the past three decades?",
        [
            "A 2019 meta-analysis in Biological Conservation estimated a 2.5% annual decline in insect biomass globally. Contributing factors include pesticide use, habitat loss, light pollution, and climate change, but researchers say disentangling individual causes is extremely difficult because these stressors co-occur.",
            "Long-term monitoring stations in Germany recorded a 76% decline in flying insect biomass over 27 years, even in protected nature reserves, suggesting that factors beyond local land use changes are involved."
        ],
        "Insect decline is well-documented but attributing specific causes is scientifically challenging",
        "Multiple stressors interact in complex ways and controlled experiments at ecosystem scale are impractical, so definitive causal attribution remains elusive",
        "environment", "why",
        source_type="multi_source",
        reasoning_type="causal",
        context_sources=["Biological Conservation Meta-Analysis (2019)", "Krefeld Entomological Society Long-Term Study (2017)"]
    ))

    # ================================================================
    # MIXED_EVIDENCE (5 cases)
    # domains: medicine, government, agriculture, sports, education
    # query_types: is, does, should, should, is
    # multi_source: 538, 540
    # ================================================================

    cases.append(make_case(
        538, "mixed_evidence",
        "Is red wine consumption beneficial for heart health?",
        [
            "Observational studies of over 500,000 participants suggested that moderate red wine consumption was associated with a 25-30% reduction in cardiovascular disease risk. Resveratrol and polyphenols in red wine were proposed as protective mechanisms.",
            "A 2023 meta-analysis in JAMA Network Open involving 4.8 million participants found that any level of alcohol consumption increases all-cause mortality risk, and that earlier studies had methodological flaws including 'sick quitter' bias where former drinkers were counted as non-drinkers."
        ],
        "Earlier evidence favored moderate wine consumption but newer, larger studies challenge that conclusion",
        "The evidence has shifted from supporting moderate consumption to questioning any net health benefit, making a hedged answer essential",
        "medicine", "is",
        source_type="multi_source",
        context_sources=["European Heart Journal Observational Studies", "JAMA Network Open Meta-Analysis (2023)"]
    ))

    cases.append(make_case(
        539, "mixed_evidence",
        "Does raising the minimum wage reduce poverty?",
        [
            "A Congressional Budget Office analysis estimated that raising the federal minimum wage to $15/hour would lift 900,000 people out of poverty but could result in the loss of 1.4 million jobs. The net effect on poverty was projected to be positive but modest.",
            "A University of Washington study of Seattle's minimum wage increase found that while hourly wages rose 3.1%, hours worked fell by 9.4% for low-wage workers, resulting in an average net income decrease of $125 per month for the lowest-paid group."
        ],
        "Minimum wage increases have mixed effects on poverty depending on magnitude and local conditions",
        "The evidence shows both poverty reduction and job/hour losses; the net effect depends heavily on the specific wage level and local economic conditions",
        "government", "does"
    ))

    cases.append(make_case(
        540, "mixed_evidence",
        "Should farmers adopt no-till agriculture practices?",
        [
            "A 25-year USDA study found that no-till farming increased soil organic carbon by 8-12%, improved water retention by 15-20%, and reduced erosion by up to 90% compared to conventional tillage. Fuel costs were also 30-40% lower per acre.",
            "A University of Wisconsin study found that no-till fields in northern climates experienced 5-10% lower yields in the first 3-5 years due to cooler, wetter soils and increased weed pressure, and required higher herbicide applications during the transition."
        ],
        "No-till offers long-term soil and cost benefits but has significant short-term yield and weed challenges",
        "The evidence supports no-till overall but with important caveats about transition costs, climate dependence, and herbicide reliance",
        "agriculture", "should",
        source_type="multi_source",
        context_sources=["USDA Agricultural Research Service Long-Term Study", "University of Wisconsin Agronomy Department (2022)"]
    ))

    cases.append(make_case(
        541, "mixed_evidence",
        "Should college athletes be allowed to transfer freely without sitting out a season?",
        [
            "Since the NCAA adopted the one-time free transfer rule in 2021, transfer portal entries have increased 85%, with over 2,100 Division I basketball players entering the portal in 2023-24 alone. Programs like USC and Colorado rebuilt rosters almost entirely through transfers, reaching bowl games within one season.",
            "A 2024 Knight Commission study found that 43% of transferring athletes did not graduate within six years, compared to 68% of non-transfers. Coaches reported that roster instability reduced team cohesion and made long-term player development strategies less viable."
        ],
        "Free transfers enable competitive flexibility but may harm academic outcomes and team stability",
        "The evidence shows both competitive benefits and concerning academic and developmental trade-offs; the answer should present the tension rather than endorsing either side",
        "sports", "should"
    ))

    cases.append(make_case(
        542, "mixed_evidence",
        "Is year-round schooling better for student achievement?",
        [
            "A meta-analysis of 39 studies found that year-round schooling produced a small positive effect on student achievement (d=0.09), with the benefit being most pronounced for low-income students who showed gains equivalent to one additional month of learning per year.",
            "A review by the National Education Association found that year-round schedules reduced summer slide in reading by about 50%, but created logistical challenges for families, increased facility cooling costs by 15-25%, and showed diminishing academic returns after the third year."
        ],
        "Year-round schooling shows small academic gains, especially for disadvantaged students, but with practical trade-offs",
        "The modest achievement effect must be weighed against implementation costs and logistical challenges; benefits are concentrated in specific populations",
        "education", "is"
    ))

    # ================================================================
    # TEMPORAL_UNCERTAINTY (5 cases)
    # domains: technology, technology, science, government, history
    # query_types: when, when, how, when, when
    # multi_source: 543
    # ================================================================

    cases.append(make_case(
        543, "temporal_uncertainty",
        "When will quantum computers be able to break current encryption standards?",
        [
            "NIST estimates that cryptographically relevant quantum computers are 10-20 years away as of 2024. IBM targets 100,000 qubits by 2033, but breaking RSA-2048 requires approximately 4,000 logical qubits, which translates to millions of physical qubits with current error rates.",
            "Google's 2024 Willow chip achieved 105 physical qubits with improved error correction, but experts note the gap between current capabilities and cryptographic threat remains several orders of magnitude."
        ],
        "Quantum threat to encryption is real but timeline estimates span a wide range",
        "Expert consensus suggests 10-20+ years but rapid advances could compress timelines; the answer should acknowledge the range rather than a specific date",
        "technology", "when",
        source_type="multi_source",
        context_sources=["NIST Post-Quantum Cryptography Project (2024)", "Google Quantum AI Lab Reports (2024)"]
    ))

    cases.append(make_case(
        544, "temporal_uncertainty",
        "When will autonomous vehicles be widely available for personal use?",
        [
            "Waymo operates fully autonomous ride-hailing in San Francisco, Phoenix, and Los Angeles as of 2024, completing over 100,000 trips per week. However, these services operate only in geofenced urban areas with pre-mapped routes and favorable weather.",
            "A 2024 McKinsey forecast projects that Level 4 autonomous vehicles for personal ownership will not reach mass market until 2035-2040, citing regulatory hurdles, liability frameworks, and the long tail of edge cases in driving scenarios."
        ],
        "Limited autonomous services exist now but personal ownership at scale is likely 10-15+ years away",
        "Current progress is real but confined to controlled environments; the gap between geofenced ride-hailing and general-purpose personal vehicles is substantial",
        "technology", "when"
    ))

    cases.append(make_case(
        545, "temporal_uncertainty",
        "How long will lithium reserves last at current consumption rates?",
        [
            "The US Geological Survey estimates global identified lithium resources at 98 million tonnes as of 2024, with current annual consumption at approximately 180,000 tonnes. At current extraction rates, reserves would last over 500 years, but EV demand is projected to increase consumption 5-7 fold by 2030.",
            "Recycling technology for lithium-ion batteries currently recovers only 50-60% of lithium content, though emerging direct recycling methods promise 95%+ recovery rates by the end of this decade."
        ],
        "Lithium supply is adequate now but future demand growth creates significant uncertainty",
        "Static reserve calculations are misleading given exponential demand growth; the answer should hedge on the interplay between growing demand, new discoveries, and recycling advances",
        "science", "how",
        reasoning_type="analytical"
    ))

    cases.append(make_case(
        546, "temporal_uncertainty",
        "When will the US Social Security trust fund be depleted?",
        [
            "The 2024 Social Security Trustees Report projects that the OASI trust fund will be depleted by 2033, at which point payroll tax revenue would cover only 79% of scheduled benefits. The combined OASI and Disability Insurance trust fund faces depletion by 2035.",
            "These projections assume current law and economic conditions; changes to retirement age, payroll tax rates, benefit formulas, or immigration policy could significantly alter the timeline in either direction."
        ],
        "Trust fund depletion projected around 2033-2035 but policy changes could alter the timeline substantially",
        "The projection is based on current-law assumptions and moderate economic scenarios; the answer should present the estimate while noting policy sensitivity",
        "government", "when"
    ))

    cases.append(make_case(
        547, "temporal_uncertainty",
        "When did the first humans arrive in the Americas?",
        [
            "The long-accepted Clovis-first model dated human arrival to approximately 13,000 years ago via the Bering land bridge. However, sites like Monte Verde in Chile (14,500 years ago) and White Sands in New Mexico (21,000-23,000 years ago based on fossilized footprints) have pushed the timeline back significantly.",
            "A 2024 Nature study using luminescence dating at a site in Brazil suggested possible human presence as early as 25,000 years ago, but the findings remain controversial due to questions about whether the artifacts are definitively human-made."
        ],
        "Human arrival in the Americas is being pushed back but the earliest dates remain disputed",
        "The Clovis-first model is clearly outdated, but exactly how much earlier humans arrived depends on acceptance of contested archaeological evidence at pre-Clovis sites",
        "history", "when",
        reasoning_type="factual"
    ))

    # ================================================================
    # VERSION_OVERLAP (4 cases)
    # domains: medicine, psychology, food, medicine
    # query_types: what, what, how, what
    # multi_source: 551
    # ================================================================

    cases.append(make_case(
        548, "version_overlap",
        "What is the recommended daily protein intake for adults?",
        [
            "The RDA set by the National Academies is 0.8 grams of protein per kilogram of body weight per day for adults, established in 2005 based on nitrogen balance studies.",
            "A 2023 position paper by the International Society of Sports Nutrition recommends 1.4-2.0 g/kg/day for active individuals, and growing research suggests 1.2-1.6 g/kg/day may be optimal for older adults to prevent sarcopenia."
        ],
        "Official RDA and current research recommendations diverge significantly",
        "The RDA reflects older methodology while newer research supports higher intakes for active and elderly populations; the answer should present both figures with context",
        "medicine", "what"
    ))

    cases.append(make_case(
        549, "version_overlap",
        "What is the safe daily screen time limit for children under five?",
        [
            "The WHO's 2019 guidelines recommend no screen time for children under 1 and no more than 1 hour per day for ages 2-4. The American Academy of Pediatrics recommends avoiding digital media for children under 18-24 months except video chatting.",
            "A 2024 Lancet study of 7,000 children found the relationship between screen time and development was not linear, and that content quality and caregiver co-viewing mattered more than total time. Moderate educational screen use showed no adverse developmental effects."
        ],
        "Guidelines set strict limits but newer research emphasizes content quality over duration",
        "Official limits remain conservative while emerging evidence suggests a more nuanced picture; the answer should cite guidelines while noting the evolving understanding",
        "psychology", "what"
    ))

    cases.append(make_case(
        550, "version_overlap",
        "How much sodium per day is considered safe for adults?",
        [
            "The WHO recommends limiting sodium intake to less than 2,000 mg per day (5g of salt), while the American Heart Association advocates an even lower limit of 1,500 mg. Both guidelines cite the relationship between sodium and hypertension.",
            "A 2023 Lancet study of 95,000 adults across 18 countries found that health risks increased only above 5,000 mg per day, and that very low sodium intake (below 3,000 mg) was associated with increased cardiovascular events, challenging the stricter guidelines."
        ],
        "Major health organizations set different sodium limits and new research questions the strictest targets",
        "The answer should present the guidelines while noting that emerging large-scale evidence suggests optimal intake may be higher than current recommendations",
        "food", "how"
    ))

    cases.append(make_case(
        551, "version_overlap",
        "What blood pressure reading is considered hypertension?",
        [
            "The ACC and AHA redefined hypertension in 2017 as 130/80 mmHg or higher, lowering the previous threshold of 140/90 mmHg. This reclassification increased the number of US adults with hypertension from 32% to 46% of the adult population.",
            "The European Society of Cardiology retained the 140/90 mmHg threshold in its 2023 guidelines, noting that evidence for treating patients in the 130-139/80-89 range did not demonstrate sufficient reduction in cardiovascular events to justify medication."
        ],
        "US and European guidelines define hypertension at different thresholds",
        "The answer must note that the definition depends on which guideline is followed, as the two major systems currently disagree on the threshold",
        "medicine", "what",
        source_type="multi_source",
        context_sources=["ACC/AHA Hypertension Guidelines (2017)", "ESC/ESH Hypertension Guidelines (2023)"]
    ))

    # ================================================================
    # METHODOLOGY_DIFFERENCE (4 cases)
    # domains: government, finance, law, environment
    # query_types: how, why, how, what
    # multi_source: 555
    # ================================================================

    cases.append(make_case(
        552, "methodology_difference",
        "How many people are unemployed in the United States?",
        [
            "The Bureau of Labor Statistics reported a 3.7% unemployment rate (6.3 million people) in December 2024 using the U-3 measure, which counts only those actively seeking work in the past four weeks.",
            "The broader U-6 measure, which includes discouraged workers and part-time workers wanting full-time jobs, stood at 7.1% (12.0 million) for the same period. Some economists argue even U-6 undercounts by excluding those who stopped looking over a year ago."
        ],
        "Unemployment figures vary dramatically depending on which measure is used",
        "The answer should present the standard U-3 figure while noting that broader measures paint a different picture, and that no single number captures the full employment situation",
        "government", "how",
        reasoning_type="analytical"
    ))

    cases.append(make_case(
        553, "methodology_difference",
        "Why do different reports show different GDP growth figures for the same quarter?",
        [
            "The Bureau of Economic Analysis releases three GDP estimates: advance (30 days after quarter end, based on incomplete data), second (60 days, with updated source data), and third (90 days, most complete). The advance estimate has historically differed from the final figure by an average of 1.2 percentage points.",
            "Additionally, GDP can be measured via production (value added), expenditure (spending), or income approaches. These should theoretically match but consistently produce a 'statistical discrepancy' of 0.5-2.0% of GDP due to different data sources and timing."
        ],
        "GDP figures differ because of release timing and measurement methodology",
        "Multiple valid measurement approaches and progressive data availability mean any single GDP figure is an approximation that gets revised",
        "finance", "why",
        reasoning_type="analytical"
    ))

    cases.append(make_case(
        554, "methodology_difference",
        "How is recidivism measured and what are the actual rates?",
        [
            "The Bureau of Justice Statistics tracks recidivism as re-arrest within 3, 5, or 9 years and found that 66% of released prisoners were re-arrested within 3 years and 83% within 9 years. However, re-arrest does not equal reconviction: only 45% were reconvicted of a new crime within 3 years.",
            "The RAND Corporation notes that using re-arrest versus reconviction versus re-incarceration produces vastly different recidivism rates for the same population, and that different states define and track recidivism differently, making cross-state comparisons unreliable."
        ],
        "Recidivism rates range from 45% to 83% depending on how recidivism is defined",
        "The answer must specify which metric is being used, as re-arrest, reconviction, and re-incarceration tell very different stories about the same population",
        "law", "how",
        reasoning_type="analytical"
    ))

    cases.append(make_case(
        555, "methodology_difference",
        "What percentage of the Amazon rainforest has been deforested?",
        [
            "Brazil's PRODES satellite monitoring system, which tracks clear-cut deforestation using annual Landsat imagery, reports that approximately 17% of the original Amazon has been cleared as of 2024, totaling about 800,000 square kilometers.",
            "The DETER real-time monitoring system and MapBiomas, which include degraded forest that has lost significant canopy cover but is not fully cleared, estimate that 27-34% of the Amazon has been significantly altered or degraded."
        ],
        "Amazon loss figures depend on whether degradation is counted alongside outright deforestation",
        "Clear-cut loss of 17% is well-documented, but including degraded forest nearly doubles the figure; the answer should distinguish between deforestation and broader forest degradation",
        "environment", "what",
        source_type="multi_source",
        context_sources=["INPE PRODES Monitoring System (2024)", "MapBiomas Amazon Project (2024)"]
    ))

    # ================================================================
    # STALE_SOURCE (4 cases)
    # domains: transportation, social_media, sports, finance
    # query_types: what, how, who, what
    # multi_source: none
    # ================================================================

    cases.append(make_case(
        556, "stale_source",
        "What is the current market share of electric vehicles in the US?",
        [
            "According to Cox Automotive data, battery electric vehicles accounted for 7.6% of new US vehicle sales in 2023, up from 5.9% in 2022. Including plug-in hybrids, the electrified share reached 9.2%. However, growth rates slowed significantly in H2 2023, and several automakers reduced EV production targets."
        ],
        "EV market share was growing but momentum showed signs of plateauing",
        "The figure reflects a rapidly changing market; the slowdown in growth rates adds uncertainty about the current trajectory, making the latest static number potentially misleading",
        "transportation", "what"
    ))

    cases.append(make_case(
        557, "stale_source",
        "How many active users does Twitter/X have?",
        [
            "Elon Musk claimed in a July 2024 post that X had 600 million monthly active users and 250 million daily active users. Since X went private in October 2022, no independent audit has verified these figures. The last audited number was 238 million monetizable daily active users in Q2 2022."
        ],
        "X's user numbers are self-reported without independent verification since going private",
        "The company's claims cannot be independently verified and may use different definitions than the last audited figure; the answer should present both numbers with appropriate caveats",
        "social_media", "how",
        reasoning_type="analytical"
    ))

    cases.append(make_case(
        558, "stale_source",
        "Who is the current heavyweight boxing champion of the world?",
        [
            "As of early 2025, the heavyweight boxing championship is fragmented across sanctioning bodies. Oleksandr Usyk holds the WBA, WBC, and WBO titles after defeating Tyson Fury in May 2024 to become undisputed champion, but the IBF subsequently stripped him and awarded its belt to Daniel Dubois. Championship status changes with each major fight."
        ],
        "Championship status is fragmented and changes frequently across boxing organizations",
        "The answer depends on which sanctioning body is referenced, and titles can change on any fight night; the answer should note the current holders while flagging the volatile nature of the record",
        "sports", "who",
        reasoning_type="factual"
    ))

    cases.append(make_case(
        559, "stale_source",
        "What interest rate does the Federal Reserve charge?",
        [
            "As of January 2025, the Federal Open Market Committee maintained the federal funds target rate at 4.25-4.50%, following three consecutive 25-basis-point cuts from the September 2024 peak. The Fed's dot plot suggested 2 additional cuts in 2025, but market expectations ranged from 1 to 4 cuts depending on inflation data."
        ],
        "Fed rate is stated but future direction is uncertain and projections diverge",
        "The current rate is specific but the forward-looking path depends on evolving economic conditions; the answer should give the rate while noting it is subject to change",
        "finance", "what"
    ))

    # ================================================================
    # EVOLVING_FACTS (4 cases)
    # domains: government, general, environment, sports
    # query_types: how, what, which, who
    # multi_source: none
    # ================================================================

    cases.append(make_case(
        560, "evolving_facts",
        "How many countries have legalized same-sex marriage?",
        [
            "As of January 2025, 36 countries and territories have legalized same-sex marriage. Thailand became the most recent in January 2025, and several additional countries including Japan, Chile, and various Caribbean nations have active legislative or judicial proceedings that could change the count within months."
        ],
        "Current count is 36 but the number is actively changing as new countries pass legislation",
        "The current figure is accurate but the pipeline of pending legislation means it could change at any time; the answer should give the number with this context",
        "government", "how",
        reasoning_type="factual"
    ))

    cases.append(make_case(
        561, "evolving_facts",
        "What is the tallest building in the world?",
        [
            "The Burj Khalifa in Dubai stands at 828 meters and has held the record since 2010. The Jeddah Tower in Saudi Arabia, designed to reach 1,000 meters, was intended to surpass it but construction stalled in 2018 due to financial issues. As of 2024 the project has resumed at a reduced pace with no confirmed completion date."
        ],
        "Burj Khalifa holds the record but a taller building is under construction with an uncertain timeline",
        "The current answer is straightforward but the evolving construction of Jeddah Tower means the record may change; the answer should note this context",
        "general", "what",
        reasoning_type="factual"
    ))

    cases.append(make_case(
        562, "evolving_facts",
        "Which country produces the most renewable energy?",
        [
            "China led global renewable energy capacity with 1,390 GW installed as of mid-2024, more than double the United States at 420 GW. China added 293 GW in 2023 alone. However, as a share of total generation, Norway (98%), Iceland (100%), and Costa Rica (99%) derive nearly all power from renewables."
        ],
        "China leads in absolute capacity while small nations lead in renewable share of generation",
        "The answer depends on whether the question refers to total capacity or percentage; China dominates in absolute terms but lags in share, and rankings shift rapidly as capacity additions accelerate",
        "environment", "which",
        reasoning_type="factual"
    ))

    cases.append(make_case(
        563, "evolving_facts",
        "Who holds the world record for the most goals in international football?",
        [
            "Cristiano Ronaldo holds the record with 135 goals in international matches for Portugal as of January 2025, surpassing Ali Daei's previous record of 109 in September 2021. Ronaldo, born in 1985, continues to play internationally and adds to his tally regularly. The record changes with each international window."
        ],
        "Ronaldo currently holds the record but is still actively adding to his total",
        "The record holder is clear but because the player is still active, the exact number changes periodically; the answer should give the approximate current figure with that caveat",
        "sports", "who",
        reasoning_type="factual"
    ))

    # ================================================================
    # ENTITY_AMBIGUITY (3 cases)
    # domains: education, agriculture, finance
    # query_types: how, what, when
    # multi_source: none
    # ================================================================

    cases.append(make_case(
        564, "entity_ambiguity",
        "How large is the Springfield school district?",
        [
            "Springfield Public Schools in Springfield, Missouri enrolls approximately 24,800 students across 50 campuses. Springfield School District 186 in Springfield, Illinois serves about 13,500 students. Springfield Public Schools in Massachusetts enrolls roughly 25,300 students. Each operates independently with different governance and funding."
        ],
        "Multiple Springfield school districts exist across different states",
        "Without specifying the state, the answer must acknowledge the ambiguity and present multiple possibilities or ask for clarification",
        "education", "how",
        reasoning_type="factual"
    ))

    cases.append(make_case(
        565, "entity_ambiguity",
        "What is the main crop grown in the Central Valley?",
        [
            "California's Central Valley produces over 250 different crops and accounts for 25% of US food production. Its top crops by value are almonds ($7.6B), grapes ($6.3B), and dairy ($7.5B). However, the Central Valley of Chile, the Central Valley of Costa Rica, and the Central Valley of Virginia are also significant agricultural regions with different specialties.",
            "Chile's Central Valley is known for wine grapes and stone fruits, Costa Rica's for coffee, and Virginia's for apples, hay, and cattle. Without geographic specification, the answer depends on which Central Valley is intended."
        ],
        "Multiple regions called Central Valley exist with different agricultural profiles",
        "The question is ambiguous without a country or state qualifier; California's Central Valley is the most commonly referenced but other Central Valleys are agriculturally significant",
        "agriculture", "what",
        reasoning_type="factual"
    ))

    cases.append(make_case(
        566, "entity_ambiguity",
        "When was the First National Bank founded?",
        [
            "The First National Bank of Philadelphia, chartered on June 20, 1863, was the first bank to receive a charter under the National Banking Act (Charter No. 1). However, dozens of banks across the US have operated under the name First National Bank, including First National Bank of Omaha (1857) and First National Bank of Pennsylvania (1864). The name refers to no single institution."
        ],
        "Multiple banks share this name; the first federally chartered one was in 1863",
        "The question is ambiguous because the name is generic; the answer should clarify which First National Bank is being discussed and note the most historically significant one",
        "finance", "when",
        reasoning_type="factual"
    ))

    # ================================================================
    # PARTIAL_ANSWER (3 cases)
    # domains: science, history, science
    # query_types: what, how, what
    # multi_source: none
    # ================================================================

    cases.append(make_case(
        567, "partial_answer",
        "What are the health effects of microplastics on humans?",
        [
            "A 2024 review in Environment International found microplastics in human blood, lungs, placenta, and stool samples. Lab studies show they cause inflammation and oxidative stress in cell cultures. However, epidemiological evidence linking microplastic exposure to specific diseases remains lacking, and the clinical significance of detected levels is unknown."
        ],
        "Microplastics are present in human tissues but health effects are not yet established",
        "The evidence confirms exposure but cannot yet confirm specific harm; the answer should convey what is known while clearly stating what remains unknown",
        "science", "what"
    ))

    cases.append(make_case(
        568, "partial_answer",
        "How did ancient Egyptians build the pyramids at Giza?",
        [
            "Archaeological evidence confirms that the pyramids were built by organized labor forces (not slaves) using copper tools, wooden sledges, and internal ramps. A 2023 discovery of a ceremonial harbor near Giza confirmed that limestone blocks were transported by boat from quarries 8 miles away along purpose-built canals.",
            "However, the exact method for lifting and placing the upper blocks (weighing 2.5 tonnes each at heights above 100 meters) remains debated. Proposed theories include internal spiral ramps, external straight ramps, and lever-and-counterweight systems, with no single theory fully accounting for all archaeological evidence."
        ],
        "Transport and labor organization are well-understood but the upper-level construction method remains debated",
        "The answer can describe confirmed knowledge about quarrying and transport while acknowledging that the precise construction technique for the upper pyramid is still hypothetical",
        "history", "how",
        reasoning_type="factual"
    ))

    cases.append(make_case(
        569, "partial_answer",
        "What causes Alzheimer's disease?",
        [
            "The amyloid hypothesis posits that beta-amyloid plaque accumulation triggers Alzheimer's. The FDA-approved drug lecanemab targets amyloid and slowed cognitive decline by 27% in trials. However, many patients with significant plaques never develop dementia, and researchers are investigating tau tangles, neuroinflammation, vascular factors, and viral triggers as contributing causes."
        ],
        "Amyloid plays a role but is likely not the sole cause; multiple mechanisms are under investigation",
        "The answer can describe established knowledge about amyloid involvement while noting that the full causal picture remains incomplete and actively debated",
        "science", "what",
        reasoning_type="causal"
    ))

    # ================================================================
    # SCOPE_CONDITION (3 cases)
    # domains: law, hr_workplace, law
    # query_types: is, how, does
    # multi_source: none
    # ================================================================

    cases.append(make_case(
        570, "scope_condition",
        "Is it legal to record a phone conversation in the United States?",
        [
            "Federal law (18 U.S.C. 2511) allows one-party consent recording, meaning only one person in the conversation needs to know about the recording. However, 11 states including California, Florida, and Illinois require all-party consent. Violating state wiretapping laws can result in criminal charges and civil liability."
        ],
        "Legality depends entirely on which state's laws apply",
        "The answer must hedge by explaining the federal/state split rather than giving a blanket yes or no; the scope condition (which state) determines the answer",
        "law", "is"
    ))

    cases.append(make_case(
        571, "scope_condition",
        "How much do teachers earn in the United States?",
        [
            "The National Education Association's 2023-24 salary report shows the national average public school teacher salary was $69,544, but this masks enormous variation. Mississippi's average was $47,162 while New York's was $92,696. A teacher earning $70,000 in Houston has more purchasing power than one earning $90,000 in San Francisco."
        ],
        "Teacher salary varies dramatically by state and must be adjusted for cost of living",
        "A single national average is technically answerable but misleading without geographic context; the answer should present the range and note cost-of-living effects",
        "hr_workplace", "how",
        reasoning_type="analytical"
    ))

    cases.append(make_case(
        572, "scope_condition",
        "Does a landlord have to return a security deposit within 30 days?",
        [
            "Security deposit return deadlines vary by state: California requires return within 21 days, New York within 14 days, Texas within 30 days, and Georgia has no specific statutory deadline. Some states allow deductions for damages beyond normal wear and tear. Local ordinances in cities like Chicago and Seattle may impose additional requirements."
        ],
        "Return timelines are state-specific with wide variation",
        "The answer depends on jurisdiction; some states require faster return than 30 days while others have no specific timeline. The answer should explain the variation rather than giving a single timeframe",
        "law", "does"
    ))

    # ================================================================
    # NUMERICAL_NEAR_MISS (3 cases)
    # domains: government, finance, sports
    # query_types: does, is, does
    # multi_source: none
    # ================================================================

    cases.append(make_case(
        573, "numerical_near_miss",
        "Did the city meet its goal of reducing carbon emissions by 40% by 2024?",
        [
            "The City of Portland's 2024 Climate Action Progress Report shows a 36.8% reduction in carbon emissions from 1990 levels, falling short of the 40% target. The largest gains came from transitioning 78% of the grid to renewable sources, while transportation emissions declined only 12%, well below the 30% transportation subtarget."
        ],
        "Portland narrowly missed its overall target at 36.8% versus the 40% goal",
        "The near-miss means the answer should acknowledge meaningful progress while noting the shortfall; transportation was the primary lagging sector",
        "government", "does",
        reasoning_type="analytical"
    ))

    cases.append(make_case(
        574, "numerical_near_miss",
        "Is the company profitable this quarter?",
        [
            "TechCorp reported Q3 2024 net income of $2.3 million on revenue of $487 million, a net margin of 0.47%. While technically profitable, this is down from $18.7 million (3.8% margin) in Q3 2023. Excluding a one-time $5.1 million asset sale gain, the company would have reported a net loss of $2.8 million."
        ],
        "Technically profitable but only due to a one-time gain; underlying operations lost money",
        "The headline number is positive but the quality of earnings is poor; the answer should note that profitability depends on how one-time items are treated",
        "finance", "is",
        reasoning_type="analytical"
    ))

    cases.append(make_case(
        575, "numerical_near_miss",
        "Did the marathon runner qualify for the Olympic team?",
        [
            "Sarah Chen finished the 2024 Chicago Marathon in 2:26:42, just 12 seconds outside the Olympic qualifying standard of 2:26:30 set by World Athletics. Under the qualification system, runners can also qualify via world rankings, where Chen is currently ranked 47th; the top 40 ranked athletes who meet the entry standard will be eligible."
        ],
        "Missed the time standard by 12 seconds but ranking pathway remains a possibility",
        "The near-miss on the time standard is clear, but the alternative ranking pathway adds complexity; the answer should present both pathways and the uncertainty",
        "sports", "does",
        reasoning_type="analytical"
    ))

    # ================================================================
    # CROSS_SOURCE_PARTIAL (3 cases)
    # domains: law, social_media, real_estate
    # query_types: how, how, how
    # multi_source: 576, 577, 578 (all 3)
    # ================================================================

    cases.append(make_case(
        576, "cross_source_partial",
        "How effective are body-worn cameras at reducing police use of force?",
        [
            "A randomized controlled trial by DC Metropolitan Police involving 2,224 officers found no statistically significant difference in use-of-force incidents between officers with and without cameras over 12 months.",
            "A study of the Rialto, California police department found officers wearing body cameras used force 59% less often, and complaints dropped by 88% during the study period.",
            "A 2023 meta-analysis of 30 studies concluded body-worn cameras produce a modest overall reduction in use of force (roughly 10%), with effects varying based on activation policies and officer discretion."
        ],
        "Body camera effectiveness varies widely depending on department policy and context",
        "Individual studies reach opposite conclusions while the meta-analysis shows a modest average effect; the answer should present the range and note that implementation details matter more than the technology itself",
        "law", "how",
        source_type="multi_source",
        context_sources=[
            "Metropolitan Police DC Randomized Trial (2017)",
            "Rialto Police Department Study (2015)",
            "Journal of Criminal Justice Meta-Analysis (2023)"
        ]
    ))

    cases.append(make_case(
        577, "cross_source_partial",
        "How do different platforms measure social media engagement?",
        [
            "Meta counts engagement as any tap, click, reaction, comment, or share on a post, reporting average engagement rates of 0.06% for Facebook pages. Twitter/X counts impressions (views of the tweet in a timeline) separately from engagements (clicks, retweets, likes), reporting average engagement rates of 0.035%.",
            "TikTok uses video view completion rates as its primary engagement metric, counting a 'view' after just 0.5 seconds of watch time. A 2024 Hootsuite study found that when normalized to comparable definitions, TikTok's reported engagement rates dropped from 5.7% to approximately 1.2%.",
            "LinkedIn measures engagement as clicks, reactions, comments, and shares, but its algorithm weights comments 10x more than reactions for content distribution, making headline engagement rates incomparable across platforms."
        ],
        "Each platform defines and measures engagement differently, making cross-platform comparisons misleading",
        "The answer should explain that engagement metrics are not standardized and direct comparison requires normalization that most reports fail to perform",
        "social_media", "how",
        source_type="multi_source",
        reasoning_type="analytical",
        context_sources=[
            "Meta Business Suite Analytics Documentation (2024)",
            "Hootsuite Social Media Benchmarks Report (2024)",
            "LinkedIn Marketing Solutions Engagement Guide (2024)"
        ]
    ))

    cases.append(make_case(
        578, "cross_source_partial",
        "How does student loan debt affect homeownership rates?",
        [
            "The Federal Reserve Bank of New York found that a $1,000 increase in student debt reduces homeownership probability by 1.5 percentage points for borrowers aged 28-30, and that total student debt of $1.77 trillion has contributed to a 2-3 year delay in first home purchases.",
            "A Brookings Institution analysis noted that while student debt delays homeownership, it does not permanently prevent it: by age 40, homeownership rates of college-educated borrowers catch up to and exceed those of non-graduates, suggesting a timing effect rather than a permanent barrier."
        ],
        "Student debt delays but does not permanently prevent homeownership for most borrowers",
        "Each source captures a different time dimension: short-term delay vs. long-term catch-up. The full picture requires both perspectives",
        "real_estate", "how",
        source_type="multi_source",
        context_sources=[
            "Federal Reserve Bank of New York Research (2023)",
            "Brookings Institution Economic Studies (2024)"
        ]
    ))

    # ================================================================
    # IMPLICIT_ASSUMPTIONS (3 cases)
    # domains: real_estate, finance, technology
    # query_types: should, should, how
    # multi_source: none
    # ================================================================

    cases.append(make_case(
        579, "implicit_assumptions",
        "Should I buy a home or continue renting?",
        [
            "The national price-to-rent ratio in the US reached 16.8 in 2024, above the historical average of 15.0, suggesting renting is more favorable in many markets. This ratio ranges from 8.5 in Detroit and Cleveland (favoring buying) to over 30 in San Francisco and New York (favoring renting).",
            "A New York Times analysis found buying becomes advantageous only if the buyer stays at least 5-7 years in most markets, accounting for closing costs, property taxes, maintenance, and opportunity cost of the down payment."
        ],
        "Buy vs. rent depends on location, time horizon, and individual financial circumstances",
        "The question assumes a single national answer exists, but the calculation is highly local and personal; the answer should expose these assumptions while providing the framework for comparison",
        "real_estate", "should"
    ))

    cases.append(make_case(
        580, "implicit_assumptions",
        "Should I invest in index funds or actively managed funds?",
        [
            "The SPIVA Scorecard shows that over 15-year periods, 88-92% of actively managed large-cap funds underperform the S&P 500 after fees. The average expense ratio for index funds is 0.06% compared to 0.66% for actively managed funds.",
            "However, active funds in categories like small-cap value, emerging markets, and distressed debt have outperformed more consistently, and during periods of high market dispersion, active management shows stronger relative performance."
        ],
        "Index funds win for most mainstream categories but active management has niches",
        "The question assumes a binary choice; the answer should note that the optimal strategy depends on the asset class, market conditions, and the investor's specific portfolio needs",
        "finance", "should"
    ))

    cases.append(make_case(
        581, "implicit_assumptions",
        "How long does it take to learn a programming language?",
        [
            "A 2023 Stack Overflow survey found developers needed an average of 6-12 months to become productive in a new language, but this varied by experience: those with 10+ years reported 2-3 months, while complete beginners reported 12-18 months to write functional code independently.",
            "The concept of 'learning' a language is ambiguous: basic syntax can be grasped in days, functional proficiency in weeks to months, and mastery of idioms, ecosystem tools, and best practices typically takes 1-3 years of regular use."
        ],
        "Learning time depends heavily on prior experience and definition of 'learned'",
        "The question implicitly assumes a fixed learning curve and clear endpoint; the answer should surface these assumptions and provide ranges based on different definitions and backgrounds",
        "technology", "how"
    ))

    # ================================================================
    # ADJACENT_ENTITY (2 cases)
    # domains: agriculture, history
    # query_types: what, how
    # multi_source: none
    # ================================================================

    cases.append(make_case(
        582, "adjacent_entity",
        "What is Georgia's agricultural output?",
        [
            "The US state of Georgia is the nation's top producer of peanuts, pecans, and blueberries, with total agricultural output valued at $14.6 billion in 2023. The state's poultry industry alone accounts for $7.2 billion, making it the largest poultry-producing state.",
            "The country of Georgia (population 3.7 million) in the South Caucasus produced agricultural output worth approximately $3.2 billion in 2023, with wine, hazelnuts, and citrus as primary exports. Georgia's wine industry dates back 8,000 years and the country is recognized as a birthplace of viticulture."
        ],
        "Georgia refers to both a US state and a country with very different agricultural profiles",
        "Without clarification, the answer should note the ambiguity between the US state and the country, as both have significant agricultural sectors with completely different specializations",
        "agriculture", "what"
    ))

    cases.append(make_case(
        583, "adjacent_entity",
        "How did the Battle of Saratoga change the course of the war?",
        [
            "The Battle of Saratoga in 1777 during the American Revolution was a decisive American victory that convinced France to enter the war as an ally. French military and financial support proved critical to the eventual American victory at Yorktown in 1781.",
            "The Battle of Saratoga in 1862 refers to a lesser-known Civil War engagement near Saratoga Springs, New York, in which Confederate sympathizers were arrested. Some historical references to 'Saratoga' in a military context conflate these events or assume the Revolutionary War battle without specification."
        ],
        "Multiple battles occurred at Saratoga in different wars; the Revolutionary War battle is most significant",
        "The answer should clarify which conflict is being referenced, as the name alone is ambiguous across American military history",
        "history", "how",
        reasoning_type="factual"
    ))

    # ================================================================
    # CROSS_DOMAIN_TRANSFER (2 cases)
    # domains: sports, hr_workplace
    # query_types: should, is
    # multi_source: 584, 585
    # ================================================================

    cases.append(make_case(
        584, "cross_domain_transfer",
        "Should youth sports leagues adopt pitch-count limits like professional baseball?",
        [
            "Major League Baseball implemented pitch-count limits for minor league pitchers in 2021, capping pitchers at 80-110 pitches depending on level. USA Baseball recommends youth counts of 50-95 pitches per game depending on age, with mandatory rest days.",
            "A 2023 American Journal of Sports Medicine study found that youth pitchers exceeding recommended counts were 3.5 times more likely to need elbow or shoulder surgery. But the study noted pitch count alone is insufficient: pitch type, mechanics, year-round play, and rest between outings are also significant risk factors."
        ],
        "Pitch counts help but are only one factor in preventing youth arm injuries",
        "Transferring professional rules to youth context requires adaptation; pitch counts are necessary but not sufficient, and other factors like rest and mechanics matter as much or more",
        "sports", "should",
        source_type="multi_source",
        context_sources=[
            "USA Baseball Medical Safety Advisory Committee Guidelines",
            "American Journal of Sports Medicine Youth Pitching Study (2023)"
        ]
    ))

    cases.append(make_case(
        585, "cross_domain_transfer",
        "Is applying military leadership principles effective for corporate management?",
        [
            "A Harvard Business Review analysis found Fortune 500 CEOs with military backgrounds were overrepresented (8.6% vs. 6.4% in general population) and their companies showed slightly higher average stock returns. Military-trained leaders scored higher on decisiveness and crisis management.",
            "A Wharton study found that military-style command-and-control leadership correlated with lower employee satisfaction in knowledge-work environments, higher turnover among creative professionals, and reduced innovation output. The study concluded military principles work best when adapted rather than directly transplanted."
        ],
        "Military leadership principles offer some benefits but must be adapted to corporate contexts",
        "Direct transfer of military command style can harm innovation-dependent organizations; the answer should note that selective adaptation works better than wholesale adoption",
        "hr_workplace", "is",
        source_type="multi_source",
        context_sources=[
            "Harvard Business Review Leadership Analysis (2023)",
            "Wharton School Organizational Behavior Study (2024)"
        ]
    ))

    return cases


def validate_cases(cases):
    """Validate distribution requirements."""
    errors = []

    # Subcategory distribution
    subcat_expected = {
        "evidence_quality": 7, "hedged_evidence": 5, "different_aspects": 5,
        "causal_uncertainty": 5, "mixed_evidence": 5, "temporal_uncertainty": 5,
        "version_overlap": 4, "methodology_difference": 4, "stale_source": 4,
        "evolving_facts": 4, "entity_ambiguity": 3, "partial_answer": 3,
        "scope_condition": 3, "numerical_near_miss": 3, "cross_source_partial": 3,
        "implicit_assumptions": 3, "adjacent_entity": 2, "cross_domain_transfer": 2,
    }
    subcat_actual = {}
    for c in cases:
        subcat_actual[c["subcategory"]] = subcat_actual.get(c["subcategory"], 0) + 1
    for k, v in subcat_expected.items():
        actual = subcat_actual.get(k, 0)
        if actual != v:
            errors.append(f"subcategory {k}: expected {v}, got {actual}")
    if subcat_actual == subcat_expected:
        print("  OK subcategory distribution")
    else:
        for e in errors:
            print(f"  FAIL {e}")

    # Multi-source count
    multi = sum(1 for c in cases if c["source_type"] == "multi_source")
    print(f"  Multi-source: {multi}/20 {'OK' if multi == 20 else 'FAIL'}")

    # Domain spread (max 5 per domain)
    domain_counts = {}
    for c in cases:
        domain_counts[c["domain"]] = domain_counts.get(c["domain"], 0) + 1
    over_5 = {k: v for k, v in domain_counts.items() if v > 5}
    print(f"  Domains used: {len(domain_counts)} ({'OK' if len(domain_counts) >= 18 else 'FAIL need 18'})")
    if over_5:
        print(f"  FAIL domains over 5: {over_5}")
    else:
        print("  OK max 5 per domain")
    for d, ct in sorted(domain_counts.items()):
        print(f"    {d}: {ct}")

    # Priority domains check
    priority = ["history", "government", "agriculture", "social_media", "sports"]
    for p in priority:
        ct = domain_counts.get(p, 0)
        print(f"  Priority domain {p}: {ct} {'OK' if ct >= 3 else 'LOW'}")

    # Query type distribution
    qt_counts = {}
    for c in cases:
        qt_counts[c["query_type"]] = qt_counts.get(c["query_type"], 0) + 1
    what_ct = qt_counts.get("what", 0)
    how_ct = qt_counts.get("how", 0)
    is_does = qt_counts.get("is", 0) + qt_counts.get("does", 0)
    why_should = qt_counts.get("why", 0) + qt_counts.get("should", 0)
    when_who_which = qt_counts.get("when", 0) + qt_counts.get("who", 0) + qt_counts.get("which", 0)
    print(f"  Query types: what={what_ct}<=17? {'OK' if what_ct <= 17 else 'FAIL'}, "
          f"how={how_ct}>=14? {'OK' if how_ct >= 14 else 'FAIL'}, "
          f"is/does={is_does}>=14? {'OK' if is_does >= 14 else 'FAIL'}, "
          f"why/should={why_should}>=10? {'OK' if why_should >= 10 else 'FAIL'}, "
          f"when/who/which={when_who_which}>=7? {'OK' if when_who_which >= 7 else 'FAIL'}")
    for qt, ct in sorted(qt_counts.items()):
        print(f"    {qt}: {ct}")

    # ID sequence
    ids = [c["id"] for c in cases]
    expected_ids = [f"t1_qualify_medium_{i}" for i in range(516, 586)]
    if ids == expected_ids:
        print("  OK IDs 516-585")
    else:
        print(f"  FAIL IDs: got {ids[0]}..{ids[-1]}, expected t1_qualify_medium_516..585")

    # Duplicate queries
    queries = [c["query"] for c in cases]
    dupes = [q for q in queries if queries.count(q) > 1]
    if dupes:
        print(f"  FAIL duplicate queries: {set(dupes)}")
    else:
        print("  OK no duplicate queries")

    # Context length check
    short = []
    long = []
    for c in cases:
        for i, ctx in enumerate(c["contexts"]):
            if len(ctx) < 150:
                short.append((c["id"], i, len(ctx)))
            if len(ctx) > 400:
                long.append((c["id"], i, len(ctx)))
    if short:
        print(f"  WARN contexts under 150 chars: {short}")
    if long:
        print(f"  WARN contexts over 400 chars: {long}")
    if not short and not long:
        print("  OK all contexts 150-400 chars")

    # Total count
    print(f"  Total cases: {len(cases)} {'OK' if len(cases) == 70 else 'FAIL'}")

    return len(errors) == 0 and multi == 20 and len(domain_counts) >= 18 and not over_5


def main():
    cases = build_cases()

    print("=== Validating 70 new cases ===")
    valid = validate_cases(cases)

    if not valid:
        print("\nWARNING: Validation issues found. Proceeding anyway...")

    # Load existing data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_count = len(data["cases"])
    print(f"\nExisting cases in file: {existing_count}")

    # Check for query duplicates against existing
    existing_queries = {c["query"].lower() for c in data["cases"]}
    new_queries = [c["query"] for c in cases]
    overlaps = [q for q in new_queries if q.lower() in existing_queries]
    if overlaps:
        print(f"WARNING: {len(overlaps)} queries overlap with existing data:")
        for q in overlaps:
            print(f"  - {q}")

    # Check for ID collisions
    existing_ids = {c["id"] for c in data["cases"]}
    new_ids = {c["id"] for c in cases}
    id_collisions = existing_ids & new_ids
    if id_collisions:
        print(f"WARNING: ID collisions: {id_collisions}")

    # Append
    data["cases"].extend(cases)
    print(f"New total: {len(data['cases'])}")

    # Write back
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\nSuccessfully wrote {len(data['cases'])} cases to {DATA_FILE}")


if __name__ == "__main__":
    main()
