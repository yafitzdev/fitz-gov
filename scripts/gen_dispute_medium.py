#!/usr/bin/env python3
"""
Generate 50 new MEDIUM difficulty dispute cases for fitz-gov benchmark.

IDs: t1_dispute_medium_746 through t1_dispute_medium_795

Subcategory distribution:
  - numerical_conflict: 7
  - implicit_contradiction: 6
  - binary_conflict: 6
  - opposing_conclusions: 6
  - temporal_conflict: 5
  - statistical_direction_conflict: 4
  - source_authority_conflict: 4
  - methodology_conflict: 4
  - interpretation_conflict: 3
  - competing_theories: 3
  - scientific_replication: 2

Multi-source: 15 of 50 have source_type="multi_source" with context_sources
Domain spread: all 18 domains, max 4 per domain, prioritize history/government/agriculture/social_media/hr_workplace
Query type: what<=12, how>=10, is/does>=10, why/should>=7, when/who/which>=5
"""

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_FILE = os.path.join(PROJECT_ROOT, "data", "tier1_core", "dispute.json")

cases = []

# ============================================================================
# Helper to build a case dict
# ============================================================================
def make_case(
    idx,
    subcategory,
    query,
    contexts,
    description,
    rationale,
    domain,
    query_type,
    source_type="single",
    reasoning_type="factual",
    evidence_pattern="conflicting",
    context_sources=None,
):
    case = {
        "id": f"t1_dispute_medium_{746 + idx}",
        "difficulty": "medium",
        "subcategory": subcategory,
        "query": query,
        "contexts": contexts,
        "expected_mode": "disputed",
        "description": description,
        "rationale": rationale,
        "domain": domain,
        "query_type": query_type,
        "source_type": source_type,
        "context_count": len(contexts),
        "reasoning_type": reasoning_type,
        "evidence_pattern": evidence_pattern,
        "category": "dispute",
        "evaluation_config": {"mode": "governance", "check_mode_match": True},
    }
    if context_sources:
        case["context_sources"] = context_sources
    return case


# ============================================================================
# SUBCATEGORY: numerical_conflict (7 cases, idx 0-6)
# ============================================================================

# idx 0 -- history, what, multi_source
cases.append(make_case(
    idx=0,
    subcategory="numerical_conflict",
    query="How many people died during the Irish Potato Famine?",
    contexts=[
        "The Irish Central Statistics Office estimates that approximately 1 million people died directly from starvation and disease during the Great Famine of 1845-1852, based on census comparisons from 1841 and 1851.",
        "Historian Cormac O Grada's 2024 analysis argues the death toll was closer to 1.5 million when accounting for under-registration of rural deaths and workhouse mortality records that were lost or destroyed."
    ],
    description="Two credible sources disagree on Irish Famine death toll by 500,000",
    rationale="Government census data yields 1 million while academic analysis of under-counted deaths yields 1.5 million, a 50% discrepancy.",
    domain="history",
    query_type="how",
    source_type="multi_source",
    context_sources=["Irish Central Statistics Office Census Analysis", "Cormac O Grada, Historical Demographics (2024)"],
))

# idx 1 -- agriculture, what, single
cases.append(make_case(
    idx=1,
    subcategory="numerical_conflict",
    query="What percentage of global freshwater is used for agriculture?",
    contexts=[
        "The UN Food and Agriculture Organization reports that agriculture accounts for approximately 70% of global freshwater withdrawals, making it the single largest consumer of water resources worldwide.",
        "A 2024 World Resources Institute study using satellite-based evapotranspiration data found that agriculture actually consumes about 92% of humanity's freshwater footprint when including rainfed crop water use."
    ],
    description="Two organizations report very different figures for agricultural water use depending on methodology",
    rationale="FAO reports 70% based on withdrawal data while WRI reports 92% when including rainfed consumption, a significant methodological divergence.",
    domain="agriculture",
    query_type="what",
))

# idx 2 -- finance, what, single
cases.append(make_case(
    idx=2,
    subcategory="numerical_conflict",
    query="What is the average annual return of the S&P 500?",
    contexts=[
        "According to Vanguard's 2024 market analysis, the S&P 500 has returned an average of 10.3% per year since its inception in 1957, based on total return including dividends.",
        "Morningstar's 2024 data shows the S&P 500's inflation-adjusted real return averages approximately 7.1% annually over the same period, which they argue is the more meaningful figure for investors."
    ],
    description="Two financial authorities cite different average S&P 500 returns due to inflation adjustment",
    rationale="Vanguard reports 10.3% nominal return while Morningstar reports 7.1% real return. Both are correct within their framework but give contradictory impressions.",
    domain="finance",
    query_type="what",
))

# idx 3 -- government, how, multi_source
cases.append(make_case(
    idx=3,
    subcategory="numerical_conflict",
    query="How much does the US spend on foreign aid annually?",
    contexts=[
        "The Congressional Research Service reports that total US foreign assistance obligations were $63.4 billion in fiscal year 2023, encompassing both economic and security assistance programs across 140 countries.",
        "The OECD Development Assistance Committee records US official development assistance at $42.3 billion for 2023, using a narrower definition that excludes military aid, refugee processing costs, and administrative expenses."
    ],
    description="US government and international organization report different foreign aid totals",
    rationale="CRS uses a broad definition ($63.4B) including security aid while OECD uses a narrower definition ($42.3B) of development-only aid, creating a $21B gap.",
    domain="government",
    query_type="how",
    source_type="multi_source",
    context_sources=["Congressional Research Service Report (FY2023)", "OECD Development Assistance Committee (2023)"],
))

# idx 4 -- education, how, single
cases.append(make_case(
    idx=4,
    subcategory="numerical_conflict",
    query="How much student loan debt does the average US graduate carry?",
    contexts=[
        "The Federal Reserve Bank of New York reports the median student loan balance for borrowers who completed a bachelor's degree is $28,950, based on its Consumer Credit Panel from Q4 2024.",
        "The Education Data Initiative calculates the average student loan debt for bachelor's degree holders at $37,650, noting that the mean is significantly pulled higher by borrowers with graduate school debt included in their totals."
    ],
    description="Two data sources report different student debt figures due to mean vs median and population definitions",
    rationale="The Fed reports a $28,950 median while EDI reports a $37,650 mean. Different central tendency measures and inclusion criteria yield a $9K difference.",
    domain="education",
    query_type="how",
))

# idx 5 -- sports, what, single
cases.append(make_case(
    idx=5,
    subcategory="numerical_conflict",
    query="What is the concussion rate in professional football per season?",
    contexts=[
        "The NFL's official injury surveillance data for the 2023 season reported 219 diagnosed concussions across all teams, translating to approximately 0.41 concussions per game across the league.",
        "An independent study published in the British Journal of Sports Medicine estimated 340 concussions occurred in the 2023 NFL season, arguing that sideline assessment protocols miss approximately 36% of concussive events."
    ],
    description="NFL official data and independent research disagree on concussion rates by over 50%",
    rationale="NFL reports 219 concussions while independent researchers estimate 340, suggesting systematic underdiagnosis on game day.",
    domain="sports",
    query_type="what",
))

# idx 6 -- technology, what, multi_source
cases.append(make_case(
    idx=6,
    subcategory="numerical_conflict",
    query="What percentage of internet traffic comes from bots?",
    contexts=[
        "Imperva's 2024 Bad Bot Report found that automated bot traffic accounted for 49.6% of all internet traffic in 2023, the highest proportion ever recorded, with malicious bots comprising 32% of all traffic.",
        "Cloudflare's 2024 Radar Report estimated bot traffic at approximately 30% of global requests processed through its network, noting that definitions of what constitutes a bot vary significantly across the industry."
    ],
    description="Two major cybersecurity firms report very different bot traffic percentages",
    rationale="Imperva says nearly 50% while Cloudflare says 30%. Measurement methodology, network sample, and bot definition differences drive a 20-point gap.",
    domain="technology",
    query_type="what",
    source_type="multi_source",
    context_sources=["Imperva Bad Bot Report (2024)", "Cloudflare Radar Annual Report (2024)"],
))

# ============================================================================
# SUBCATEGORY: implicit_contradiction (6 cases, idx 7-12)
# ============================================================================

# idx 7 -- social_media, is, single
cases.append(make_case(
    idx=7,
    subcategory="implicit_contradiction",
    query="Is social media effective for small business marketing?",
    contexts=[
        "A Hootsuite survey of 18,000 marketers found that 83% of small business owners consider social media their most effective marketing channel, citing low cost and direct customer engagement as key advantages.",
        "Research from the Harvard Business Review found that fewer than 5% of social media followers ever engage with branded content, and organic reach on major platforms has declined to under 2% for business pages."
    ],
    description="Marketers report high effectiveness but engagement metrics tell a contradictory story",
    rationale="Marketers perceive social media as effective (83% satisfaction) while actual engagement data shows minimal interaction (under 2% organic reach), creating an implicit contradiction.",
    domain="social_media",
    query_type="is",
    reasoning_type="evaluative",
))

# idx 8 -- hr_workplace, does, single
cases.append(make_case(
    idx=8,
    subcategory="implicit_contradiction",
    query="Does offering unlimited PTO increase employee time off?",
    contexts=[
        "Namely's 2024 HR benchmark data shows employees at companies with unlimited PTO policies took an average of 13 days off per year, compared to 15 days at companies with traditional fixed PTO allocations.",
        "A Glassdoor employer survey found that 72% of companies offering unlimited PTO reported improved employee satisfaction and reduced burnout complaints compared to their previous fixed-day policies."
    ],
    description="Unlimited PTO reduces actual days taken while reportedly improving satisfaction",
    rationale="Employees take fewer days with unlimited PTO (13 vs 15) yet report higher satisfaction, implying the policy works differently than intended.",
    domain="hr_workplace",
    query_type="does",
    source_type="multi_source",
    reasoning_type="evaluative",
    context_sources=["Namely HR Benchmark Report (2024)", "Glassdoor Employer Survey (2024)"],
))

# idx 9 -- government, is, multi_source
cases.append(make_case(
    idx=9,
    subcategory="implicit_contradiction",
    query="Is the US power grid reliable enough for increasing electricity demand?",
    contexts=[
        "The Department of Energy's 2024 Grid Reliability Report states that the US grid maintained 99.97% average uptime across all regions, with fewer major outage events than any five-year period in the previous two decades.",
        "The North American Electric Reliability Corporation warned in its 2024 reliability assessment that two-thirds of North America faces elevated risk of electricity shortfalls during extreme weather, with reserve margins shrinking in most planning regions."
    ],
    description="DOE highlights high uptime while NERC warns of growing reliability risks",
    rationale="The grid currently runs at 99.97% uptime, but future projections show shrinking reserves and elevated shortfall risk, creating an implicit contradiction between present reliability and future outlook.",
    domain="government",
    query_type="is",
    source_type="multi_source",
    reasoning_type="evaluative",
    context_sources=["US Department of Energy Grid Reliability Report (2024)", "NERC Long-Term Reliability Assessment (2024)"],
))

# idx 10 -- food, does, single
cases.append(make_case(
    idx=10,
    subcategory="implicit_contradiction",
    query="Does organic farming produce enough food to feed the world?",
    contexts=[
        "A Nature Plants study found that organic farms produce 19-25% lower yields per acre than conventional farms on average, with the gap widening for cereal grains that form the basis of global food supply.",
        "The Rodale Institute's 40-year side-by-side farming trial showed organic plots matched conventional yields after a three-year transition period and outperformed conventional plots during drought years by up to 31%."
    ],
    description="Large-scale meta-analysis shows organic yield gap while a long-term trial shows yield parity",
    rationale="Nature Plants documents a 19-25% yield deficit for organic farming globally, but Rodale's controlled trial shows organic can match or exceed conventional yields, creating contradictory evidence.",
    domain="food",
    query_type="does",
    reasoning_type="evaluative",
))

# idx 11 -- psychology, is, single
cases.append(make_case(
    idx=11,
    subcategory="implicit_contradiction",
    query="Is positive reinforcement more effective than punishment for behavior change?",
    contexts=[
        "A meta-analysis in Psychological Bulletin covering 128 studies found that positive reinforcement produced more lasting behavior changes with 73% effectiveness across diverse populations and settings.",
        "Research published in the Journal of Applied Behavior Analysis found that in cases of dangerous or self-injurious behavior, punishment-based interventions achieved compliance within an average of 3 sessions compared to 12 sessions for reinforcement-only approaches."
    ],
    description="General research favors reinforcement but specific clinical contexts show punishment works faster",
    rationale="Positive reinforcement is broadly more effective (73% across studies) but punishment achieves faster results for urgent behavioral issues, creating a context-dependent contradiction.",
    domain="psychology",
    query_type="is",
    source_type="multi_source",
    reasoning_type="evaluative",
    context_sources=["Psychological Bulletin Meta-Analysis (2024)", "Journal of Applied Behavior Analysis (2024)"],
))

# idx 12 -- environment, how, single
cases.append(make_case(
    idx=12,
    subcategory="implicit_contradiction",
    query="How effective are carbon offset programs at reducing emissions?",
    contexts=[
        "The Gold Standard Foundation certifies that its portfolio of carbon offset projects has prevented 300 million tonnes of CO2 equivalent emissions since inception, with each credit verified through independent third-party auditing.",
        "A 2024 investigation by The Guardian and academic researchers found that over 90% of rainforest carbon offsets analyzed were likely phantom credits that did not represent genuine carbon reductions, based on satellite analysis of actual deforestation rates."
    ],
    description="Offset certifier claims verified reductions while independent analysis finds most credits are phantom",
    rationale="Gold Standard claims 300M tonnes prevented with third-party verification while investigative research finds 90% of similar credits are phantom, implicitly contradicting the effectiveness claim.",
    domain="environment",
    query_type="how",
    reasoning_type="evaluative",
))

# ============================================================================
# SUBCATEGORY: binary_conflict (6 cases, idx 13-18)
# ============================================================================

# idx 13 -- law, is, single
cases.append(make_case(
    idx=13,
    subcategory="binary_conflict",
    query="Is it legal to record phone calls without the other party's consent in the US?",
    contexts=[
        "Under federal law (18 U.S.C. 2511), recording a phone call requires only one party's consent, meaning you can legally record your own conversations without informing the other party.",
        "Twelve US states including California, Florida, and Illinois require all-party consent for recording phone calls, making it a criminal offense to record without everyone's knowledge and agreement."
    ],
    description="Federal law and state laws directly contradict on phone recording consent requirements",
    rationale="Federal law permits one-party consent recording while 12 states require all-party consent, creating a binary legal conflict depending on jurisdiction.",
    domain="law",
    query_type="is",
))

# idx 14 -- agriculture, should, single
cases.append(make_case(
    idx=14,
    subcategory="binary_conflict",
    query="Should farmers use neonicotinoid pesticides on flowering crops?",
    contexts=[
        "The USDA Integrated Pest Management guidelines state that neonicotinoids remain an effective and approved tool for protecting crops from destructive insect pests, with proper application reducing crop losses by 10-20% on average.",
        "The European Food Safety Authority concluded that neonicotinoids pose an unacceptable risk to wild bees and honeybees, leading to a complete outdoor ban across the European Union since 2018."
    ],
    description="USDA approves neonicotinoid use while EFSA banned them as unacceptable risk",
    rationale="USDA endorses neonicotinoids as effective pest management while EFSA banned them entirely due to bee toxicity, a direct binary conflict between regulatory bodies.",
    domain="agriculture",
    query_type="should",
    reasoning_type="evaluative",
))

# idx 15 -- medicine, is, multi_source
cases.append(make_case(
    idx=15,
    subcategory="binary_conflict",
    query="Is routine PSA screening recommended for prostate cancer?",
    contexts=[
        "The American Urological Association recommends routine PSA screening for men aged 55-69, stating that early detection through PSA testing reduces prostate cancer mortality by approximately 20-30% over 13 years of follow-up.",
        "The US Preventive Services Task Force advises against routine PSA screening for men 70 and older and recommends individual decision-making for ages 55-69, citing high rates of overdiagnosis and overtreatment that cause more harm than benefit."
    ],
    description="Two major medical bodies give opposing screening recommendations for the same test",
    rationale="AUA recommends routine PSA screening citing mortality reduction while USPSTF advises against it citing overdiagnosis harms, a direct binary conflict between medical authorities.",
    domain="medicine",
    query_type="is",
    source_type="multi_source",
    reasoning_type="evaluative",
    context_sources=["American Urological Association Guidelines (2024)", "US Preventive Services Task Force Recommendation (2024)"],
))

# idx 16 -- transportation, should, single
cases.append(make_case(
    idx=16,
    subcategory="binary_conflict",
    query="Should cities invest in expanding highway capacity to reduce traffic congestion?",
    contexts=[
        "The American Society of Civil Engineers' 2024 infrastructure report recommends significant highway expansion investment, noting that congestion costs US drivers $87 billion annually in wasted time and fuel, and that targeted capacity additions reduce delay by up to 20%.",
        "Research from the Transportation Research Board demonstrates that highway expansions consistently fail to reduce long-term congestion due to induced demand, where new capacity attracts additional drivers until congestion returns to pre-expansion levels within 5-10 years."
    ],
    description="Engineering body recommends highway expansion while transportation research shows it fails",
    rationale="ASCE advocates expanding highways to reduce congestion while TRB research shows induced demand negates expansion benefits, a binary conflict on the same policy question.",
    domain="transportation",
    query_type="should",
    reasoning_type="evaluative",
))

# idx 17 -- real_estate, is, single
cases.append(make_case(
    idx=17,
    subcategory="binary_conflict",
    query="Is rent control effective at keeping housing affordable?",
    contexts=[
        "A Stanford study of San Francisco's rent control policy found it reduced tenant displacement by 15% and saved long-term tenants an average of $394 per month compared to market rates in the same neighborhoods.",
        "An analysis published in the Journal of Political Economy found that rent control reduced the rental housing supply by 15% as landlords converted units to condos or let buildings deteriorate, ultimately increasing market rents for non-controlled units."
    ],
    description="One study shows rent control protects tenants while another shows it reduces housing supply",
    rationale="Rent control demonstrably helps current tenants ($394/month savings) but simultaneously reduces overall housing supply by 15%, creating contradictory evidence on net effectiveness.",
    domain="real_estate",
    query_type="is",
    reasoning_type="evaluative",
))

# idx 18 -- social_media, does, single
cases.append(make_case(
    idx=18,
    subcategory="binary_conflict",
    query="Does content moderation on social platforms reduce harmful speech?",
    contexts=[
        "Meta's 2024 Community Standards Enforcement Report shows that proactive detection removed 97.8% of hate speech before users reported it, with overall hate speech prevalence declining by 53% over three years on Facebook.",
        "A Stanford Internet Observatory study found that banned users simply migrated to alternative platforms where hate speech volume increased by 70%, and that 38% of removed content was reshared on the original platform within 48 hours through slightly altered versions."
    ],
    description="Platform data shows moderation works while independent research shows it merely displaces speech",
    rationale="Meta reports 97.8% proactive removal and declining prevalence while researchers find displacement to other platforms and rapid resharing, a binary conflict on actual effectiveness.",
    domain="social_media",
    query_type="does",
))

# ============================================================================
# SUBCATEGORY: opposing_conclusions (6 cases, idx 19-24)
# ============================================================================

# idx 19 -- history, why, multi_source
cases.append(make_case(
    idx=19,
    subcategory="opposing_conclusions",
    query="Why did the Roman Empire fall?",
    contexts=[
        "Historian Peter Heather's 2024 revised analysis argues that the Western Roman Empire collapsed primarily due to external barbarian pressure, particularly the Hunnic migrations that pushed Germanic tribes into Roman territory, overwhelming military defenses that had been adequate for centuries.",
        "Historian Bryan Ward-Perkins contends that Rome fell due to internal economic decay, including currency debasement, overtaxation, and the collapse of long-distance trade networks that made the empire ungovernable well before the barbarian invasions became decisive."
    ],
    description="Two prominent historians reach opposing conclusions on the primary cause of Rome's fall",
    rationale="Heather attributes the fall to external military pressure while Ward-Perkins blames internal economic collapse, each presenting compelling evidence for mutually exclusive primary causes.",
    domain="history",
    query_type="why",
    source_type="multi_source",
    reasoning_type="evaluative",
    context_sources=["Peter Heather, The Fall of the Roman Empire, Revised Edition (2024)", "Bryan Ward-Perkins, The Fall of Rome and the End of Civilization (2024 reprint)"],
))

# idx 20 -- science, why, single
cases.append(make_case(
    idx=20,
    subcategory="opposing_conclusions",
    query="Why are insect populations declining globally?",
    contexts=[
        "A comprehensive review in Science attributes the primary driver of insect decline to agricultural intensification, specifically the expansion of monoculture farming and widespread pesticide use, which have destroyed habitat and directly poisoned insect populations across every continent.",
        "A competing analysis published in Annual Review of Entomology argues that climate change is the dominant factor, showing that temperature shifts have disrupted breeding cycles, altered migration patterns, and created phenological mismatches between insects and their food plants."
    ],
    description="Two major reviews reach opposing conclusions on the primary driver of insect decline",
    rationale="One review identifies agriculture as the main cause while the other identifies climate change, both using substantial evidence to support mutually exclusive primary explanations.",
    domain="science",
    query_type="why",
    reasoning_type="evaluative",
))

# idx 21 -- hr_workplace, how, multi_source
cases.append(make_case(
    idx=21,
    subcategory="opposing_conclusions",
    query="How should companies structure return-to-office mandates?",
    contexts=[
        "McKinsey's 2024 workplace survey of 800 executives concluded that structured hybrid models with 3 mandatory office days per week optimize both productivity and collaboration, with companies reporting 12% higher team output compared to fully remote arrangements.",
        "Gallup's 2024 State of the Workplace report found that employees given full flexibility over their work location reported 41% higher engagement and 23% lower turnover, concluding that autonomy-based policies outperform mandated schedules regardless of the number of required days."
    ],
    description="Two major consulting firms reach opposing conclusions on mandatory vs flexible office policies",
    rationale="McKinsey favors structured 3-day mandates for productivity while Gallup finds full flexibility drives better engagement and retention, reaching opposite recommendations from different data.",
    domain="hr_workplace",
    query_type="how",
    source_type="multi_source",
    reasoning_type="evaluative",
    context_sources=["McKinsey Workplace Survey (2024)", "Gallup State of the Workplace Report (2024)"],
))

# idx 22 -- general, why, single
cases.append(make_case(
    idx=22,
    subcategory="opposing_conclusions",
    query="Why has life expectancy in the US stalled compared to other developed nations?",
    contexts=[
        "A Commonwealth Fund analysis attributes the US life expectancy gap primarily to the fragmented healthcare system, showing that Americans have lower rates of primary care access, higher rates of uninsurance, and worse chronic disease management than peer countries.",
        "Princeton economists Anne Case and Angus Deaton argue the stagnation is driven by social factors rather than healthcare, pointing to deaths of despair from opioids, alcohol, and suicide concentrated among working-class Americans without college degrees."
    ],
    description="Healthcare system analysis and social factors research reach opposing conclusions on the same trend",
    rationale="One analysis blames the healthcare system while the other blames socioeconomic despair, each presenting evidence that the other's factor is secondary.",
    domain="general",
    query_type="why",
    reasoning_type="evaluative",
))

# idx 23 -- food, should, single
cases.append(make_case(
    idx=23,
    subcategory="opposing_conclusions",
    query="Should governments tax sugary beverages to reduce obesity?",
    contexts=[
        "A WHO-commissioned systematic review found that sugar taxes in Mexico, the UK, and Philadelphia reduced sugary drink purchases by 10-35%, concluding that fiscal policies are among the most effective population-level interventions for reducing sugar consumption and obesity rates.",
        "An analysis by the Tax Foundation found that sugar taxes are highly regressive, falling disproportionately on low-income households, and that consumers largely substitute to other high-calorie alternatives, concluding the taxes fail to meaningfully reduce obesity while increasing economic burden on the poor."
    ],
    description="Health organization review favors sugar taxes while economic analysis concludes they are ineffective and regressive",
    rationale="WHO evidence shows sugar taxes reduce purchases by 10-35% while economic analysis shows regressive impacts and substitution effects that negate health benefits, opposing conclusions on the same policy.",
    domain="food",
    query_type="should",
    reasoning_type="evaluative",
))

# idx 24 -- technology, how, single
cases.append(make_case(
    idx=24,
    subcategory="opposing_conclusions",
    query="How will AI affect employment in the next decade?",
    contexts=[
        "A Goldman Sachs analysis projects that generative AI could automate 25% of current work tasks globally, potentially displacing 300 million full-time jobs, with legal, administrative, and financial roles facing the highest exposure.",
        "MIT's Work of the Future task force concludes that AI will primarily augment rather than replace workers, creating more new job categories than it eliminates, as every prior wave of automation has ultimately increased total employment and wages."
    ],
    description="Investment bank predicts massive job displacement while academic research predicts job augmentation",
    rationale="Goldman Sachs predicts 300 million job displacements while MIT concludes AI will augment workers and increase total employment, directly opposing conclusions about the same technology's impact.",
    domain="technology",
    query_type="how",
    reasoning_type="evaluative",
))

# ============================================================================
# SUBCATEGORY: temporal_conflict (5 cases, idx 25-29)
# ============================================================================

# idx 25 -- government, when, single
cases.append(make_case(
    idx=25,
    subcategory="temporal_conflict",
    query="When will the US Social Security trust fund be depleted?",
    contexts=[
        "The 2024 Social Security Trustees Report projects the combined Old-Age and Survivors Insurance trust fund will be depleted by 2033, at which point incoming payroll taxes would cover only 79% of scheduled benefits.",
        "The Congressional Budget Office's 2024 long-term projection estimates depletion by 2033 under baseline assumptions but notes that under alternative economic scenarios with higher immigration and productivity growth, solvency could extend to 2039."
    ],
    description="Two government bodies project different potential depletion dates based on economic assumptions",
    rationale="Trustees project 2033 depletion while CBO's alternative scenario extends it to 2039, a six-year gap depending on economic assumptions about immigration and productivity.",
    domain="government",
    query_type="when",
))

# idx 26 -- science, when, multi_source
cases.append(make_case(
    idx=26,
    subcategory="temporal_conflict",
    query="When will the Arctic Ocean experience its first ice-free summer?",
    contexts=[
        "A 2024 Nature Communications study using updated climate models predicts the Arctic could see its first ice-free September as early as the 2030s, even under moderate emissions scenarios, roughly a decade earlier than previous IPCC estimates.",
        "The IPCC Sixth Assessment Report states that the Arctic is not projected to be practically ice-free in September until mid-century (2040s-2050s) under high-emissions scenarios, based on the ensemble mean of CMIP6 climate models."
    ],
    description="Recent modeling predicts ice-free Arctic a decade earlier than IPCC projections",
    rationale="New research says ice-free Arctic by 2030s while IPCC says 2040s-2050s, a 10-20 year divergence driven by different model generations and emissions assumptions.",
    domain="science",
    query_type="when",
    source_type="multi_source",
    context_sources=["Nature Communications Arctic Ice Study (2024)", "IPCC Sixth Assessment Report (2021-2023)"],
))

# idx 27 -- history, when, single
cases.append(make_case(
    idx=27,
    subcategory="temporal_conflict",
    query="When did humans first arrive in the Americas?",
    contexts=[
        "The long-established Clovis-first model, supported by extensive archaeological evidence, places the first human migration to the Americas at approximately 13,500 years ago via the Bering land bridge during the last Ice Age.",
        "Recent discoveries at the White Sands site in New Mexico yielded footprints radiocarbon-dated to 21,000-23,000 years ago, suggesting humans arrived in the Americas roughly 10,000 years earlier than the Clovis model predicted."
    ],
    description="Traditional archaeology and recent discoveries disagree on first human arrival by 10,000 years",
    rationale="Clovis model says 13,500 years ago while White Sands evidence suggests 21,000-23,000 years ago, a fundamental temporal conflict that rewrites migration history.",
    domain="history",
    query_type="when",
))

# idx 28 -- technology, when, single
cases.append(make_case(
    idx=28,
    subcategory="temporal_conflict",
    query="When will solid-state batteries be commercially viable for electric vehicles?",
    contexts=[
        "Toyota announced in 2024 that it expects to begin mass production of solid-state batteries for its electric vehicles by 2027-2028, having achieved breakthroughs in sulfide-based electrolyte manufacturing that resolved previous durability issues.",
        "Battery researchers at the Argonne National Laboratory published a 2024 assessment concluding that commercial solid-state batteries remain at least 10-15 years away due to unresolved challenges in electrode-electrolyte interface stability at scale."
    ],
    description="Automaker promises commercial solid-state batteries by 2028 while researchers say 2035 at earliest",
    rationale="Toyota claims 2027-2028 commercialization while Argonne Lab says 10-15 years away, a conflict between corporate timelines and academic assessment.",
    domain="technology",
    query_type="when",
))

# idx 29 -- environment, when, single
cases.append(make_case(
    idx=29,
    subcategory="temporal_conflict",
    query="When will global CO2 emissions peak?",
    contexts=[
        "The International Energy Agency's 2024 World Energy Outlook states that global CO2 emissions from energy are expected to peak before 2025, driven by rapid solar deployment, EV adoption, and China's slowing economic growth reducing coal demand.",
        "Climate Analytics' 2024 assessment argues emissions will not peak until 2030 at the earliest, noting that developing nations' industrialization, continued fossil fuel subsidies, and insufficient renewable deployment in Africa and Southeast Asia will sustain growth."
    ],
    description="IEA predicts imminent emissions peak while Climate Analytics says it is years away",
    rationale="IEA says peak before 2025 based on renewable growth while Climate Analytics says not until 2030 due to developing world industrialization, a five-year disagreement.",
    domain="environment",
    query_type="when",
))

# ============================================================================
# SUBCATEGORY: statistical_direction_conflict (4 cases, idx 30-33)
# ============================================================================

# idx 30 -- social_media, does, multi_source
cases.append(make_case(
    idx=30,
    subcategory="statistical_direction_conflict",
    query="Does social media use increase political polarization?",
    contexts=[
        "A large-scale experiment published in Science where participants deactivated Facebook for four weeks showed reduced political polarization, less exposure to partisan news, and lower political knowledge, concluding that social media causally increases ideological division.",
        "Research from Stanford's Internet Observatory found that political polarization has increased most among demographics least likely to use social media, particularly older Americans with low internet usage, suggesting social media is not the primary driver of polarization."
    ],
    description="Experimental evidence shows social media increases polarization while demographic data suggests it does not",
    rationale="A controlled experiment shows deactivating Facebook reduces polarization while demographic analysis shows polarization rising most among non-users, statistical findings pointing in opposite directions.",
    domain="social_media",
    query_type="does",
    source_type="multi_source",
    context_sources=["Science Magazine Deactivation Experiment (2024)", "Stanford Internet Observatory Report (2024)"],
))

# idx 31 -- agriculture, is, single
cases.append(make_case(
    idx=31,
    subcategory="statistical_direction_conflict",
    query="Is global food production keeping pace with population growth?",
    contexts=[
        "The FAO's 2024 State of Food Security report shows that global food production has increased by 2.4% annually over the past decade, consistently outpacing the 1.1% annual population growth rate, with per-capita calorie availability reaching record highs.",
        "The World Food Programme's 2024 hunger assessment reports that the number of acutely food-insecure people rose from 135 million in 2019 to 345 million in 2024, with famine conditions expanding despite aggregate production increases."
    ],
    description="FAO data shows production outpacing population while WFP data shows hunger increasing",
    rationale="Aggregate production grows faster than population (2.4% vs 1.1%) yet acute hunger has more than doubled, with the statistics pointing in opposite directions on whether food supply is adequate.",
    domain="agriculture",
    query_type="is",
))

# idx 32 -- finance, how, single
cases.append(make_case(
    idx=32,
    subcategory="statistical_direction_conflict",
    query="How has income inequality changed in the US over the past decade?",
    contexts=[
        "Census Bureau data shows the Gini coefficient for US household income fell from 0.489 in 2013 to 0.471 in 2023, representing a statistically significant decline in income inequality, with the largest gains among the lowest quintile.",
        "Federal Reserve Survey of Consumer Finances data shows wealth inequality increased dramatically over the same period, with the top 1% of households increasing their share of total wealth from 32% to 38% while the bottom 50% saw their share remain flat at 2.5%."
    ],
    description="Income inequality measures show decline while wealth inequality measures show increase",
    rationale="Income Gini fell from 0.489 to 0.471 (less inequality) while wealth share of top 1% rose from 32% to 38% (more inequality), statistical trends moving in opposite directions.",
    domain="finance",
    query_type="how",
))

# idx 33 -- hr_workplace, is, single
cases.append(make_case(
    idx=33,
    subcategory="statistical_direction_conflict",
    query="Is the gender pay gap in the US narrowing?",
    contexts=[
        "Bureau of Labor Statistics data shows women's median weekly earnings rose from 82.3% of men's in 2014 to 84.0% in 2024, representing a statistically significant narrowing of the raw gender pay gap over the decade.",
        "A PayScale analysis controlling for job title, experience, and industry found the controlled gender pay gap has actually widened from $0.98 to $0.97 on the dollar between 2019 and 2024, with the gap growing most in technology and finance sectors."
    ],
    description="Raw pay gap is narrowing while controlled pay gap is widening",
    rationale="Raw BLS data shows gap narrowing (82.3% to 84.0%) while controlled PayScale analysis shows gap widening ($0.98 to $0.97), statistical trends moving in opposite directions depending on methodology.",
    domain="hr_workplace",
    query_type="is",
))

# ============================================================================
# SUBCATEGORY: source_authority_conflict (4 cases, idx 34-37)
# ============================================================================

# idx 34 -- history, who, multi_source
cases.append(make_case(
    idx=34,
    subcategory="source_authority_conflict",
    query="Who was primarily responsible for breaking the Enigma code in World War II?",
    contexts=[
        "The British Government Communications Headquarters' official history credits Alan Turing and the Bletchley Park team as the primary codebreakers, citing Turing's development of the Bombe machine that mechanized decryption of daily Enigma settings.",
        "Polish intelligence historians argue that Polish mathematicians Marian Rejewski, Jerzy Rozycki, and Henryk Zygalski broke Enigma first in 1932 and shared their methods with the British in 1939, providing the essential foundation without which Bletchley Park could not have succeeded."
    ],
    description="British and Polish authorities each claim primary credit for breaking Enigma",
    rationale="GCHQ credits Turing and Bletchley Park while Polish historians argue their mathematicians broke Enigma seven years earlier and enabled the British effort, a source authority conflict between national historical narratives.",
    domain="history",
    query_type="who",
    source_type="multi_source",
    reasoning_type="evaluative",
    context_sources=["GCHQ Official History of Signals Intelligence", "Polish Institute of National Remembrance (2024)"],
))

# idx 35 -- medicine, which, single
cases.append(make_case(
    idx=35,
    subcategory="source_authority_conflict",
    query="Which diet is most effective for long-term weight loss?",
    contexts=[
        "The American Heart Association's 2024 dietary guidelines recommend a Mediterranean-style diet as the most effective approach for sustained weight management, citing meta-analyses showing 4.5 kg greater weight loss maintained at two years compared to low-fat diets.",
        "The National Academy of Sciences published a 2024 consensus report concluding that ketogenic diets produce superior long-term weight loss outcomes, with patients maintaining 6.2 kg greater loss at 18 months compared to calorie-restricted approaches including Mediterranean patterns."
    ],
    description="Two authoritative medical bodies recommend different diets as most effective for weight loss",
    rationale="AHA recommends Mediterranean diet while NAS favors ketogenic diet, both citing large-scale evidence, a direct conflict between equally authoritative sources.",
    domain="medicine",
    query_type="which",
    reasoning_type="evaluative",
))

# idx 36 -- law, who, single
cases.append(make_case(
    idx=36,
    subcategory="source_authority_conflict",
    query="Who has the legal authority to regulate cryptocurrency in the United States?",
    contexts=[
        "SEC Chairman's 2024 testimony before Congress asserted that most cryptocurrencies qualify as securities under the Howey test and fall under SEC jurisdiction, citing enforcement actions against major exchanges as establishing regulatory precedent.",
        "The CFTC Commissioner's 2024 position paper argued that major cryptocurrencies like Bitcoin and Ethereum are commodities under the Commodity Exchange Act and fall under CFTC jurisdiction, noting that Congress has not explicitly granted the SEC authority over digital assets."
    ],
    description="SEC and CFTC both claim primary regulatory authority over cryptocurrency",
    rationale="SEC classifies crypto as securities under its jurisdiction while CFTC classifies them as commodities under its jurisdiction, a direct authority conflict between federal regulators.",
    domain="law",
    query_type="who",
    reasoning_type="evaluative",
))

# idx 37 -- agriculture, which, multi_source
cases.append(make_case(
    idx=37,
    subcategory="source_authority_conflict",
    query="Which farming method is more sustainable: regenerative agriculture or precision agriculture?",
    contexts=[
        "The USDA Natural Resources Conservation Service's 2024 sustainability assessment ranked regenerative agriculture practices as the most sustainable approach, citing soil carbon sequestration rates of 0.5-1.0 tonnes per hectare annually and 40% improvement in water retention.",
        "The International Food Policy Research Institute concluded in its 2024 report that precision agriculture using AI-guided inputs delivers superior sustainability outcomes, reducing fertilizer use by 30%, water consumption by 25%, and greenhouse gas emissions by 20% per unit of food produced."
    ],
    description="USDA favors regenerative agriculture while IFPRI favors precision agriculture for sustainability",
    rationale="USDA prioritizes soil health metrics favoring regenerative practices while IFPRI prioritizes per-unit efficiency metrics favoring precision agriculture, an authority conflict rooted in different sustainability definitions.",
    domain="agriculture",
    query_type="which",
    source_type="multi_source",
    reasoning_type="evaluative",
    context_sources=["USDA NRCS Sustainability Assessment (2024)", "IFPRI Global Sustainability Report (2024)"],
))

# ============================================================================
# SUBCATEGORY: methodology_conflict (4 cases, idx 38-41)
# ============================================================================

# idx 38 -- psychology, how, single
cases.append(make_case(
    idx=38,
    subcategory="methodology_conflict",
    query="How prevalent is clinical depression among US teenagers?",
    contexts=[
        "The CDC's Youth Risk Behavior Survey, based on anonymous school-administered questionnaires, found that 42% of high school students reported persistent feelings of sadness or hopelessness in 2023, suggesting widespread depressive symptoms among adolescents.",
        "The National Comorbidity Survey Replication using structured diagnostic interviews conducted by trained clinicians found that 12.8% of adolescents met criteria for major depressive disorder, indicating the true clinical prevalence is significantly lower than self-report surveys suggest."
    ],
    description="Self-report surveys show 42% depression symptoms while clinical interviews show 12.8% diagnosis rate",
    rationale="Anonymous self-report questionnaires yield 42% while structured clinical interviews yield 12.8%, a methodological conflict where the measurement approach drives a 3x difference in reported prevalence.",
    domain="psychology",
    query_type="how",
))

# idx 39 -- real_estate, how, single
cases.append(make_case(
    idx=39,
    subcategory="methodology_conflict",
    query="How much have US home prices increased in the past year?",
    contexts=[
        "The Case-Shiller National Home Price Index, which tracks repeat sales of the same properties to control for housing quality changes, showed a 6.2% annual increase in home prices through Q3 2024.",
        "The National Association of Realtors' existing home sales report showed the median sale price increased only 3.7% year-over-year, based on all closed transactions regardless of whether the same property was previously sold."
    ],
    description="Two standard housing indices show different price appreciation due to methodological differences",
    rationale="Case-Shiller's repeat-sale methodology shows 6.2% growth while NAR's median-price methodology shows 3.7%, a 2.5-point gap driven purely by how prices are measured.",
    domain="real_estate",
    query_type="how",
))

# idx 40 -- sports, how, multi_source
cases.append(make_case(
    idx=40,
    subcategory="methodology_conflict",
    query="How effective is high-intensity interval training compared to steady-state cardio?",
    contexts=[
        "A meta-analysis in the British Journal of Sports Medicine analyzing 36 randomized controlled trials found HIIT produced 28.5% greater improvements in maximal oxygen uptake (VO2max) compared to moderate continuous training over equivalent study durations.",
        "A competing meta-analysis in Sports Medicine examining 55 studies with longer follow-up periods found no significant difference in VO2max improvements between HIIT and continuous training at 12 months, noting that HIIT's early advantages diminish with training adaptation."
    ],
    description="Two meta-analyses reach different conclusions based on study selection and follow-up duration",
    rationale="Shorter-term meta-analysis shows HIIT 28.5% better while longer-term meta-analysis shows no significant difference, a methodology conflict in study selection criteria.",
    domain="sports",
    query_type="how",
    source_type="multi_source",
    context_sources=["British Journal of Sports Medicine Meta-Analysis (2024)", "Sports Medicine Journal Meta-Analysis (2024)"],
))

# idx 41 -- education, how, single
cases.append(make_case(
    idx=41,
    subcategory="methodology_conflict",
    query="How effective are charter schools compared to traditional public schools?",
    contexts=[
        "Stanford University's Center for Research on Education Outcomes, using matched-comparison methodology pairing charter students with demographically similar traditional school peers, found charter school students gained 16 additional days of learning in reading and 6 in math per year.",
        "A study published in the Journal of Policy Analysis and Management using school-level average test scores rather than student-level matching found no statistically significant difference in performance between charter and traditional public schools after controlling for demographics."
    ],
    description="Student-level matching shows charter school advantage while school-level analysis shows no difference",
    rationale="Student-level matched comparison finds charter advantage of 16 days in reading while school-level analysis finds no significant difference, demonstrating how unit of analysis changes the conclusion.",
    domain="education",
    query_type="how",
))

# ============================================================================
# SUBCATEGORY: interpretation_conflict (3 cases, idx 42-44)
# ============================================================================

# idx 42 -- finance, how, single
cases.append(make_case(
    idx=42,
    subcategory="interpretation_conflict",
    query="How should investors interpret an inverted yield curve?",
    contexts=[
        "Federal Reserve Bank of New York research shows that an inverted yield curve has preceded every US recession since 1960 with no false positives, with the 10-year minus 3-month Treasury spread remaining the most reliable recession predictor, currently signaling a 71% probability of recession within 12 months.",
        "Analysis by JP Morgan's chief economist argues that the current yield curve inversion is a false signal driven by unusual monetary policy rather than economic fundamentals, noting that strong labor markets, resilient consumer spending, and healthy corporate balance sheets are inconsistent with imminent recession."
    ],
    description="Central bank research interprets inverted curve as recession signal while Wall Street interprets it as false alarm",
    rationale="The Fed sees the inverted curve as a reliable recession signal (100% historical accuracy) while JP Morgan interprets the same data as distorted by monetary policy, an interpretation conflict over identical financial data.",
    domain="finance",
    query_type="how",
    reasoning_type="evaluative",
))

# idx 43 -- science, how, single
cases.append(make_case(
    idx=43,
    subcategory="interpretation_conflict",
    query="How should the discovery of phosphine in Venus's atmosphere be interpreted?",
    contexts=[
        "A study led by Cardiff University researchers published in Nature Astronomy detected 20 parts per billion of phosphine gas in Venus's cloud layer, arguing that no known abiotic chemical process can explain this concentration, making it a potential biosignature of microbial life.",
        "A reanalysis by NASA's Jet Propulsion Laboratory using the same spectral data found the phosphine signal was likely a misidentification of sulfur dioxide, a common volcanic gas on Venus, and that the original study's data processing introduced artifacts that mimicked a phosphine signature."
    ],
    description="Same spectral data interpreted as biosignature by one team and as instrument artifact by another",
    rationale="Cardiff team interprets spectral data as phosphine biosignature while NASA JPL interprets the same data as sulfur dioxide misidentification, a direct interpretation conflict over identical observations.",
    domain="science",
    query_type="how",
    reasoning_type="evaluative",
))

# idx 44 -- transportation, is, single
cases.append(make_case(
    idx=44,
    subcategory="interpretation_conflict",
    query="Is autonomous vehicle technology safer than human drivers?",
    contexts=[
        "Waymo's 2024 safety report covering 7.1 million autonomous miles in San Francisco showed their vehicles had 85% fewer injury-causing crashes per million miles compared to the human driver baseline, interpreting this as clear evidence that autonomous technology surpasses human safety.",
        "The National Highway Traffic Safety Administration's analysis of the same period notes that autonomous vehicles disengage and hand control to safety drivers in complex situations, meaning the human baseline comparison is not apples-to-apples since AVs avoid the hardest driving scenarios."
    ],
    description="Company interprets safety data as proving AV superiority while regulator questions the comparison methodology",
    rationale="Waymo interprets crash data as showing 85% safety improvement while NHTSA argues the comparison is flawed because AVs disengage in difficult situations, an interpretation conflict over what the data actually proves.",
    domain="transportation",
    query_type="is",
    reasoning_type="evaluative",
))

# ============================================================================
# SUBCATEGORY: competing_theories (3 cases, idx 45-47)
# ============================================================================

# idx 45 -- psychology, why, single
cases.append(make_case(
    idx=45,
    subcategory="competing_theories",
    query="Why do humans dream?",
    contexts=[
        "Harvard psychiatrist J. Allan Hobson's activation-synthesis theory proposes that dreams are the brain's attempt to make sense of random neural firing during REM sleep, with the cortex generating narratives from essentially meaningless signals originating in the brainstem.",
        "Cognitive neuroscientist Antti Revonsuo's threat simulation theory argues that dreaming evolved as a biological defense mechanism, where the brain rehearses threatening scenarios during sleep to improve real-world survival responses, evidenced by the disproportionate frequency of threatening content in dreams."
    ],
    description="Two competing neuroscience theories offer contradictory explanations for why humans dream",
    rationale="Hobson says dreams are random neural noise given narrative structure while Revonsuo says dreams are evolutionarily purposeful threat rehearsals, fundamentally incompatible theories about the same phenomenon.",
    domain="psychology",
    query_type="why",
    reasoning_type="evaluative",
))

# idx 46 -- environment, why, single
cases.append(make_case(
    idx=46,
    subcategory="competing_theories",
    query="Why did megafauna like mammoths and giant sloths go extinct?",
    contexts=[
        "The overkill hypothesis, championed by paleoecologist Paul Martin, argues that the arrival of human hunters to new continents directly caused megafauna extinctions, supported by the consistent timing of extinctions coinciding with first human arrival on every continent and major island.",
        "Climate-driven extinction theory, supported by researchers at the University of Adelaide, argues that rapid climate shifts at the end of the Pleistocene destroyed megafauna habitats, noting that many species declined before human arrival and that small human populations lacked the capacity for continental-scale extinction."
    ],
    description="Two competing theories attribute megafauna extinction to human hunting versus climate change",
    rationale="Overkill hypothesis blames human hunting (timing correlation) while climate theory blames habitat loss (evidence of pre-human decline), competing explanations for the same extinction event.",
    domain="environment",
    query_type="why",
    reasoning_type="evaluative",
))

# idx 47 -- medicine, why, single
cases.append(make_case(
    idx=47,
    subcategory="competing_theories",
    query="Why does general anesthesia cause loss of consciousness?",
    contexts=[
        "The integrated information theory of anesthesia, supported by research at the University of Wisconsin, proposes that anesthetics work by disrupting the brain's ability to integrate information across cortical networks, effectively fragmenting consciousness into disconnected modules that cannot combine into unified experience.",
        "The thalamocortical loop theory, advanced by researchers at MIT, argues that anesthetics primarily block communication between the thalamus and cortex, preventing sensory information from reaching higher brain areas, which they demonstrated by showing that restoring thalamic function can reverse unconsciousness even while anesthetic concentrations remain high."
    ],
    description="Two neuroscience theories explain anesthetic unconsciousness through different brain mechanisms",
    rationale="Information integration theory says anesthetics fragment cortical integration while thalamocortical theory says they block thalamus-cortex communication, competing mechanisms for the same clinical phenomenon.",
    domain="medicine",
    query_type="why",
    reasoning_type="evaluative",
))

# ============================================================================
# SUBCATEGORY: scientific_replication (2 cases, idx 48-49)
# ============================================================================

# idx 48 -- food, is, multi_source
cases.append(make_case(
    idx=48,
    subcategory="scientific_replication",
    query="Is red meat consumption linked to increased cancer risk?",
    contexts=[
        "The International Agency for Research on Cancer classified processed red meat as a Group 1 carcinogen in 2015, with a 2024 updated meta-analysis confirming an 18% increased risk of colorectal cancer per 50g daily serving, based on pooled data from 800 epidemiological studies.",
        "A 2024 replication effort published in the Annals of Internal Medicine reanalyzed the underlying studies using stricter inclusion criteria and found the association was weak and inconsistent, with a risk ratio of only 1.04 when limited to studies controlling for confounders like smoking, alcohol, and obesity."
    ],
    description="IARC classification confirmed by meta-analysis but challenged by stricter reanalysis showing weak effect",
    rationale="Original meta-analysis shows 18% increased cancer risk while rigorous reanalysis controlling for confounders finds only a 4% increase (barely significant), a replication conflict casting doubt on the strength of the association.",
    domain="food",
    query_type="is",
    source_type="multi_source",
    context_sources=["IARC/WHO Updated Meta-Analysis (2024)", "Annals of Internal Medicine Replication Study (2024)"],
))

# idx 49 -- real_estate, does, single
cases.append(make_case(
    idx=49,
    subcategory="scientific_replication",
    query="Does building more housing actually reduce rents in expensive cities?",
    contexts=[
        "A widely cited 2023 study from the Upjohn Institute found that each new market-rate apartment built in a low-vacancy area reduced nearby rents by 5-7% within two years through filtering effects and increased competition among landlords.",
        "A 2024 replication study by urban economists at UCLA using the same methodology in Los Angeles found no statistically significant rent reduction near new construction, noting that luxury developments attracted higher-income migrants who bid up rents in surrounding neighborhoods, offsetting any supply-side benefit."
    ],
    description="Original study shows new housing reduces rents but replication in different city finds no effect",
    rationale="Upjohn study finds 5-7% rent reduction from new construction while UCLA replication finds no significant effect due to migration-induced demand, a failed replication casting doubt on the generalizability of supply-side housing theory.",
    domain="real_estate",
    query_type="does",
))

# ============================================================================
# Validation and output
# ============================================================================

def validate_cases(cases):
    """Validate all constraints are met."""
    errors = []

    # Check count
    if len(cases) != 50:
        errors.append(f"Expected 50 cases, got {len(cases)}")

    # Check IDs
    expected_ids = [f"t1_dispute_medium_{i}" for i in range(746, 796)]
    actual_ids = [c["id"] for c in cases]
    if actual_ids != expected_ids:
        errors.append(f"ID mismatch. Expected {expected_ids[0]}-{expected_ids[-1]}, got {actual_ids[0]}-{actual_ids[-1]}")
        for i, (e, a) in enumerate(zip(expected_ids, actual_ids)):
            if e != a:
                errors.append(f"  idx {i}: expected {e}, got {a}")

    # Check duplicate queries
    queries = [c["query"] for c in cases]
    dupes = [q for q in queries if queries.count(q) > 1]
    if dupes:
        errors.append(f"Duplicate queries: {set(dupes)}")

    # Subcategory distribution
    from collections import Counter
    sub_counts = Counter(c["subcategory"] for c in cases)
    expected_subs = {
        "numerical_conflict": 7,
        "implicit_contradiction": 6,
        "binary_conflict": 6,
        "opposing_conclusions": 6,
        "temporal_conflict": 5,
        "statistical_direction_conflict": 4,
        "source_authority_conflict": 4,
        "methodology_conflict": 4,
        "interpretation_conflict": 3,
        "competing_theories": 3,
        "scientific_replication": 2,
    }
    if dict(sub_counts) != expected_subs:
        errors.append(f"Subcategory mismatch:\n  Expected: {expected_subs}\n  Got:      {dict(sub_counts)}")

    # Multi-source count
    ms_count = sum(1 for c in cases if c["source_type"] == "multi_source")
    if ms_count != 15:
        errors.append(f"Expected 15 multi_source cases, got {ms_count}")

    # Multi-source must have context_sources
    for c in cases:
        if c["source_type"] == "multi_source" and "context_sources" not in c:
            errors.append(f"{c['id']}: multi_source but missing context_sources")

    # Domain spread - max 4 per domain, all 18 domains
    dom_counts = Counter(c["domain"] for c in cases)
    all_18 = {
        "agriculture", "education", "environment", "finance", "food", "general",
        "government", "history", "hr_workplace", "law", "medicine", "psychology",
        "real_estate", "science", "social_media", "sports", "technology", "transportation",
    }
    missing_domains = all_18 - set(dom_counts.keys())
    if missing_domains:
        errors.append(f"Missing domains: {missing_domains}")
    over_4 = {d: n for d, n in dom_counts.items() if n > 4}
    if over_4:
        errors.append(f"Domains with >4 cases: {over_4}")

    # Priority domains should be well-represented
    priority = {"history", "government", "agriculture", "social_media", "hr_workplace"}
    for d in priority:
        if dom_counts.get(d, 0) < 3:
            errors.append(f"Priority domain '{d}' has only {dom_counts.get(d, 0)} cases (expected >=3)")

    # Query type constraints
    qt_counts = Counter(c["query_type"] for c in cases)
    what_count = qt_counts.get("what", 0)
    how_count = qt_counts.get("how", 0)
    is_does_count = qt_counts.get("is", 0) + qt_counts.get("does", 0)
    why_should_count = qt_counts.get("why", 0) + qt_counts.get("should", 0)
    when_who_which_count = qt_counts.get("when", 0) + qt_counts.get("who", 0) + qt_counts.get("which", 0)

    if what_count > 12:
        errors.append(f"what query count {what_count} > 12")
    if how_count < 10:
        errors.append(f"how query count {how_count} < 10")
    if is_does_count < 10:
        errors.append(f"is/does query count {is_does_count} < 10")
    if why_should_count < 7:
        errors.append(f"why/should query count {why_should_count} < 7")
    if when_who_which_count < 5:
        errors.append(f"when/who/which query count {when_who_which_count} < 5")

    # Context length check (150-400 chars)
    for c in cases:
        for i, ctx in enumerate(c["contexts"]):
            if len(ctx) < 150:
                errors.append(f"{c['id']} context[{i}] too short: {len(ctx)} chars")
            if len(ctx) > 400:
                errors.append(f"{c['id']} context[{i}] too long: {len(ctx)} chars (<= 400)")

    # Required fields
    required_fields = [
        "id", "difficulty", "subcategory", "query", "contexts", "expected_mode",
        "description", "rationale", "domain", "query_type", "source_type",
        "context_count", "reasoning_type", "evidence_pattern", "category",
        "evaluation_config",
    ]
    for c in cases:
        for f in required_fields:
            if f not in c:
                errors.append(f"{c['id']}: missing field '{f}'")

    # All difficulty = medium
    for c in cases:
        if c["difficulty"] != "medium":
            errors.append(f"{c['id']}: difficulty is '{c['difficulty']}', expected 'medium'")

    # All expected_mode = disputed
    for c in cases:
        if c["expected_mode"] != "disputed":
            errors.append(f"{c['id']}: expected_mode is '{c['expected_mode']}', expected 'disputed'")

    # Print results
    print(f"\nValidation: {len(cases)} cases checked")
    print(f"  Subcategories: {dict(sub_counts)}")
    print(f"  Domains ({len(dom_counts)}): {dict(dom_counts)}")
    print(f"  Query types: {dict(qt_counts)}")
    print(f"  Multi-source: {ms_count}")
    print(f"  what={what_count}, how={how_count}, is/does={is_does_count}, why/should={why_should_count}, when/who/which={when_who_which_count}")

    if errors:
        print(f"\n  ERRORS ({len(errors)}):")
        for e in errors:
            print(f"    - {e}")
        return False
    else:
        print("\n  All constraints passed!")
        return True


def main():
    # Validate before writing
    valid = validate_cases(cases)
    if not valid:
        print("\nFix validation errors before writing.")
        return

    # Read existing data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_count = len(data["cases"])
    print(f"\nExisting cases: {existing_count}")

    # Check for ID collisions
    existing_ids = {c["id"] for c in data["cases"]}
    new_ids = {c["id"] for c in cases}
    collisions = existing_ids & new_ids
    if collisions:
        print(f"ERROR: ID collisions: {collisions}")
        return

    # Append new cases
    data["cases"].extend(cases)
    new_count = len(data["cases"])
    print(f"New total: {new_count} (+{new_count - existing_count})")

    # Write back
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Written to {DATA_FILE}")


if __name__ == "__main__":
    main()
