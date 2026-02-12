#!/usr/bin/env python3
"""
Generate 50 new dispute test cases (batch 1) for fitz-gov benchmark.

IDs: t1_dispute_hard_618 through t1_dispute_hard_667
Subcategories:
  - cross_source_contradiction (20 cases, 618-637) -- multi-source
  - source_authority_conflict  (10 cases, 638-647) -- multi-source
  - numerical_conflict         (10 cases, 648-657) -- single source
  - implicit_contradiction     (10 cases, 658-667) -- single source

Output: scripts/new_dispute_batch1.json
"""

import json
import os

cases = []

# ===========================================================================
# SUBCATEGORY 1: cross_source_contradiction (20 cases, IDs 618-637)
# Multi-source: different sources report different facts about the same topic.
# Domain spread: 4 science, 4 law/policy, 3 history, 3 sports, 3 finance, 3 technology
# ===========================================================================

cases.append({
    "id": "t1_dispute_hard_618",
    "difficulty": "hard",
    "subcategory": "cross_source_contradiction",
    "query": "What percentage of the Amazon rainforest has been deforested since 1970?",
    "contexts": [
        "According to the Brazilian National Institute for Space Research (INPE) satellite analysis published in March 2024, approximately 17% of the original Amazon rainforest has been lost since 1970, with deforestation accelerating significantly between 2019 and 2022 before declining in 2023.",
        "The World Wildlife Fund's 2024 Living Amazon Report estimates that roughly 20% of the Amazon biome has been converted to other land uses since the early 1970s, based on combined satellite imagery and ground-truth surveys across all nine Amazonian countries.",
        "A peer-reviewed study in Nature Ecology & Evolution (January 2024) reports that 26% of the Amazon has been either deforested or severely degraded, noting that degradation from selective logging and fire damage is often missed by standard deforestation metrics."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "inpe_satellite_2024", "source_type": "government", "authority": "primary"},
        {"source_id": "wwf_living_amazon_2024", "source_type": "report", "authority": "secondary"},
        {"source_id": "nature_eco_evo_2024", "source_type": "academic", "authority": "primary"}
    ],
    "description": "Three credible sources provide different estimates of Amazon deforestation due to differing methodologies and scope definitions",
    "rationale": "INPE reports 17% (pure deforestation, Brazil only), WWF reports 20% (all Amazon countries, land-use conversion), and the Nature study reports 26% (including degradation). The disagreement stems from whether degradation counts and which geographic scope is used."
})

cases.append({
    "id": "t1_dispute_hard_619",
    "difficulty": "hard",
    "subcategory": "cross_source_contradiction",
    "query": "How much does the ocean absorb of human CO2 emissions annually?",
    "contexts": [
        "The Global Carbon Budget 2024 report by the Global Carbon Project estimates that the ocean absorbs approximately 2.8 gigatons of carbon (GtC) per year, accounting for roughly 26% of total anthropogenic CO2 emissions.",
        "A 2024 study published in Science using updated ocean circulation models and direct measurements found the ocean carbon sink to be closer to 3.6 GtC per year, suggesting previous estimates systematically undercount absorption in the Southern Ocean."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "global_carbon_budget_2024", "source_type": "report", "authority": "primary"},
        {"source_id": "science_ocean_sink_2024", "source_type": "academic", "authority": "primary"}
    ],
    "description": "Two primary scientific sources disagree on the magnitude of annual ocean CO2 absorption by nearly 30%",
    "rationale": "The Global Carbon Budget uses one methodology (atmospheric inversion models) yielding 2.8 GtC/yr while the Science study uses updated ocean models yielding 3.6 GtC/yr. Both are peer-reviewed and credible, but they disagree materially on a key climate metric."
})

cases.append({
    "id": "t1_dispute_hard_620",
    "difficulty": "hard",
    "subcategory": "cross_source_contradiction",
    "query": "What is the half-life of PFAS chemicals in the human body?",
    "contexts": [
        "The U.S. CDC Agency for Toxic Substances and Disease Registry states that PFOS has a serum elimination half-life of approximately 5.4 years in humans, based on occupational exposure cohort studies conducted between 2000 and 2015.",
        "A 2023 meta-analysis in Environmental Health Perspectives pooling data from 12 population studies across six countries estimated the PFOS half-life at 3.4 years (95% CI: 2.9-4.0), noting that earlier estimates were biased upward by ongoing low-level environmental exposure during the elimination period.",
        "The European Food Safety Authority (EFSA) 2024 risk assessment uses a PFOS half-life of 4.8 years, derived from Nordic population studies where environmental exposure dropped sharply after regulatory bans."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "cdc_atsdr_pfas_profile", "source_type": "government", "authority": "official"},
        {"source_id": "ehp_pfas_metaanalysis_2023", "source_type": "academic", "authority": "primary"},
        {"source_id": "efsa_pfas_risk_2024", "source_type": "government", "authority": "official"}
    ],
    "description": "Three authoritative sources report different half-life values for PFOS in humans: 5.4, 3.4, and 4.8 years",
    "rationale": "CDC cites 5.4 years from occupational studies, a meta-analysis finds 3.4 years after correcting for ongoing exposure bias, and EFSA uses 4.8 years from post-ban Nordic data. All are credible but the estimates differ by up to 60%, reflecting genuine scientific uncertainty about PFAS pharmacokinetics."
})

cases.append({
    "id": "t1_dispute_hard_621",
    "difficulty": "hard",
    "subcategory": "cross_source_contradiction",
    "query": "What is the current rate of sea level rise per year?",
    "contexts": [
        "NASA's Sea Level Change Portal reports that global mean sea level is currently rising at 3.7 millimeters per year, based on satellite altimetry data from the Jason-3 and Sentinel-6 missions, averaged over the 2013-2023 decade.",
        "The IPCC Sixth Assessment Report (AR6, 2021) states the rate of global mean sea level rise was 3.1 mm/yr over the 1993-2010 period, with acceleration detected but not yet fully quantified for the most recent decade.",
        "A 2024 study in Nature Climate Change using recalibrated tide gauge records combined with satellite data estimates the current rate at 4.4 mm/yr, arguing that previous satellite-only estimates miss coastal subsidence effects."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "nasa_sea_level_portal_2024", "source_type": "government", "authority": "official"},
        {"source_id": "ipcc_ar6_wg1_2021", "source_type": "report", "authority": "primary"},
        {"source_id": "nature_cc_sealevel_2024", "source_type": "academic", "authority": "primary"}
    ],
    "description": "Three sources report different current rates of sea level rise: 3.1, 3.7, and 4.4 mm/yr",
    "rationale": "The sources disagree because they use different time windows, measurement techniques, and definitions of 'sea level rise.' NASA's satellite altimetry gives 3.7 mm/yr, the IPCC's older period gives 3.1 mm/yr, and a newer study incorporating coastal subsidence gives 4.4 mm/yr."
})

# Law/policy (4 cases)
cases.append({
    "id": "t1_dispute_hard_622",
    "difficulty": "hard",
    "subcategory": "cross_source_contradiction",
    "query": "Is employer monitoring of employee emails legal in the European Union?",
    "contexts": [
        "The European Court of Human Rights ruled in Barbulescu v. Romania (2017, Grand Chamber) that employers may not monitor employee communications without prior notice and a legitimate purpose, and that employees have a reasonable expectation of privacy even when using work devices.",
        "A 2024 European Data Protection Board guidance document states that employers may process employee email metadata for security purposes under GDPR Article 6(1)(f) (legitimate interest), provided they conduct a data protection impact assessment and implement proportionality safeguards.",
        "The French CNIL issued a decision in November 2023 fining a Paris-based company EUR 300,000 for systematically monitoring employee emails, ruling that even with prior notice, comprehensive email surveillance is disproportionate under French implementation of the GDPR."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "echr_barbulescu_2017", "source_type": "government", "authority": "official"},
        {"source_id": "edpb_guidance_2024", "source_type": "government", "authority": "official"},
        {"source_id": "cnil_decision_2023", "source_type": "government", "authority": "official"}
    ],
    "description": "EU-level court precedent, EDPB guidance, and a national regulator decision give different answers about the legality of employee email monitoring",
    "rationale": "The ECHR allows monitoring with notice and legitimate purpose, the EDPB permits metadata processing under legitimate interest with safeguards, but the French CNIL ruled that even notified comprehensive monitoring is disproportionate. The legal landscape is genuinely fragmented."
})

cases.append({
    "id": "t1_dispute_hard_623",
    "difficulty": "hard",
    "subcategory": "cross_source_contradiction",
    "query": "Does the First Amendment protect hate speech in the United States?",
    "contexts": [
        "The Congressional Research Service report 'The First Amendment: Categories of Unprotected Speech' (updated 2024) notes that the Supreme Court has never recognized 'hate speech' as a categorical exception to the First Amendment, and that content-based restrictions are subject to strict scrutiny.",
        "A 2023 Harvard Law Review article argues that while hate speech lacks a formal exception, the Court's decisions in cases like Virginia v. Black (2003) and Wisconsin v. Mitchell (1993) demonstrate that speech motivated by bias receives less protection when it constitutes true threats, incitement, or enhances criminal sentencing.",
        "The ACLU's current legal position statement holds that hate speech is fully protected under the First Amendment unless it falls into an independently recognized exception such as incitement to imminent lawless action or true threats, and that there is no hate speech exception."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "crs_first_amendment_2024", "source_type": "government", "authority": "official"},
        {"source_id": "harvard_law_review_2023", "source_type": "academic", "authority": "primary"},
        {"source_id": "aclu_free_speech_position", "source_type": "reference", "authority": "expert"}
    ],
    "description": "Legal sources agree there is no categorical hate speech exception but disagree on the practical level of protection such speech receives",
    "rationale": "The CRS and ACLU say hate speech is protected (no exception exists), while the Harvard Law Review argues the practical reality is more nuanced since bias-motivated expression often overlaps with less-protected categories like true threats. The formal legal answer and the practical legal landscape diverge."
})

cases.append({
    "id": "t1_dispute_hard_624",
    "difficulty": "hard",
    "subcategory": "cross_source_contradiction",
    "query": "Can an employer require employees to sign a non-compete agreement in California?",
    "contexts": [
        "California Business and Professions Code Section 16600, as amended by AB 1076 (effective January 2024), declares that every contract restraining anyone from engaging in a lawful profession, trade, or business is void, with narrow exceptions for the sale of a business or dissolution of a partnership.",
        "A January 2024 advisory from the law firm Littler Mendelson notes that despite California's strong prohibition, employers can still protect their interests through narrowly tailored non-solicitation agreements targeting specific clients, provided the agreements do not effectively function as non-competes.",
        "The FTC's proposed federal non-compete ban rule (published January 2023, stayed by court order August 2024) would have preempted state law and banned most non-compete agreements nationwide, but its legal status remains uncertain after the Ryan LLC v. FTC ruling in the Northern District of Texas."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "ca_bpc_16600_2024", "source_type": "government", "authority": "official"},
        {"source_id": "littler_advisory_2024", "source_type": "industry", "authority": "expert"},
        {"source_id": "ftc_noncompete_rule_2023", "source_type": "government", "authority": "official"}
    ],
    "description": "California law bans non-competes but sources disagree on scope of permissible alternatives and interaction with potential federal preemption",
    "rationale": "State law clearly voids non-competes, but a law firm advisory suggests non-solicitation agreements remain viable, and the FTC's stayed federal rule creates uncertainty about the future landscape. The answer to whether an employer 'can require' such an agreement depends on exact agreement type and evolving federal law."
})

cases.append({
    "id": "t1_dispute_hard_625",
    "difficulty": "hard",
    "subcategory": "cross_source_contradiction",
    "query": "Is it legal to record a phone call without the other party's consent in Australia?",
    "contexts": [
        "The Telecommunications (Interception and Access) Act 1979 (Cth) Section 7 prohibits the interception of communications passing over a telecommunications system, but Section 7(2)(a) allows a party to the communication to record it without the other party's consent at the federal level.",
        "The Victorian Surveillance Devices Act 1999 Section 6 makes it an offence to knowingly use a listening device to record a private conversation to which you are a party without the consent of all parties, with penalties up to 2 years imprisonment.",
        "The Queensland Invasion of Privacy Act 1971 Section 43 similarly requires all-party consent for recording telephone conversations, while New South Wales permits single-party consent under the Surveillance Devices Act 2007 Section 7(3)(b)."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "aus_tia_act_1979", "source_type": "government", "authority": "official"},
        {"source_id": "vic_surveillance_act_1999", "source_type": "government", "authority": "official"},
        {"source_id": "qld_nsw_privacy_acts", "source_type": "government", "authority": "official"}
    ],
    "description": "Federal Australian law permits single-party recording but several state laws require all-party consent, creating genuine legal conflict",
    "rationale": "Federal law allows recording by a party to the call, but Victoria and Queensland require all-party consent while NSW follows the federal approach. The answer depends entirely on which state the recorder is in and which law takes precedence in a conflict."
})

# History (3 cases)
cases.append({
    "id": "t1_dispute_hard_626",
    "difficulty": "hard",
    "subcategory": "cross_source_contradiction",
    "query": "How many people died during the Great Leap Forward famine in China (1959-1961)?",
    "contexts": [
        "Demographer Judith Banister's landmark 1987 study 'China's Changing Population' estimated 30 million excess deaths during the Great Leap Forward, a figure widely cited in Western scholarship and based on reconstructed census data.",
        "Yang Jisheng, a Chinese journalist and historian, estimated 36 million deaths in his 2008 book 'Tombstone' (Mubei), drawing on provincial archives, internal Communist Party documents, and county-level mortality records that were declassified in the 1990s.",
        "A 2017 demographic study by Cormac O Grada published in the Journal of Economic Literature reviewed all major estimates and concluded the likely range is 15-55 million, with a central estimate of approximately 22 million, arguing that earlier figures were inflated by double-counting and faulty population baseline assumptions."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "banister_china_pop_1987", "source_type": "academic", "authority": "primary"},
        {"source_id": "yang_tombstone_2008", "source_type": "reference", "authority": "primary"},
        {"source_id": "ograda_jel_2017", "source_type": "academic", "authority": "primary"}
    ],
    "description": "Scholarly estimates of Great Leap Forward deaths range from 22 million to 36 million, with no consensus achievable due to data limitations",
    "rationale": "Three respected sources give materially different death tolls: Banister (30M), Yang (36M), and O Grada (22M). The disagreement persists because Chinese demographic data from the period is incomplete and politically contested, making a definitive count impossible."
})

cases.append({
    "id": "t1_dispute_hard_627",
    "difficulty": "hard",
    "subcategory": "cross_source_contradiction",
    "query": "Who was the first person to reach the North Pole?",
    "contexts": [
        "The National Geographic Society officially recognized Robert Peary's claim to have reached the North Pole on April 6, 1909, awarding him a gold medal and defending his priority for over a century.",
        "A 1988 re-analysis of Peary's navigation logs by astronomer Dennis Rawlins, published in the journal Polar Record, concluded that Peary likely fell 30-60 miles short of the pole, based on inconsistencies in his sun sighting records and an implausibly fast return speed of 135 miles in 56 hours.",
        "Historian Robert Bryce's 1997 book 'Cook & Peary: The Polar Controversy, Resolved' argues that neither Peary nor rival claimant Frederick Cook reached the pole, and that the first verified surface attainment was Ralph Plaisted's snowmobile expedition in April 1968, confirmed by Air Force satellite navigation."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "natgeo_peary_recognition", "source_type": "reference", "authority": "primary"},
        {"source_id": "rawlins_polar_record_1988", "source_type": "academic", "authority": "primary"},
        {"source_id": "bryce_cook_peary_1997", "source_type": "reference", "authority": "primary"}
    ],
    "description": "Historical sources disagree on whether Peary actually reached the North Pole in 1909 or whether the first verified attainment was decades later",
    "rationale": "National Geographic upholds Peary's 1909 claim, but a navigation re-analysis suggests he fell short, and a comprehensive historical study argues neither early claimant succeeded. The first verified attainment may actually have been Plaisted in 1968."
})

cases.append({
    "id": "t1_dispute_hard_628",
    "difficulty": "hard",
    "subcategory": "cross_source_contradiction",
    "query": "When was the printing press invented?",
    "contexts": [
        "The Encyclopaedia Britannica states that Johannes Gutenberg invented the movable-type printing press in Mainz, Germany, around 1440, with the first major printed work being the Gutenberg Bible completed by 1455.",
        "A 2001 study by Korean historian Park Byeng-Sen and UNESCO scholarship established that Jikji, a Korean Buddhist text printed with movable metal type, was produced at Heungdeok-sa temple in Cheongju in 1377, predating Gutenberg by roughly 60 years. The UNESCO Memory of the World Register lists it as the world's oldest extant book printed with movable metal type."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "britannica_gutenberg", "source_type": "reference", "authority": "primary"},
        {"source_id": "unesco_jikji_2001", "source_type": "government", "authority": "official"}
    ],
    "description": "Western and East Asian sources attribute movable-type printing to different inventors separated by 60 years",
    "rationale": "Britannica credits Gutenberg (c. 1440) while UNESCO recognizes a Korean movable metal type print from 1377. The answer depends on whether 'invention of the printing press' means the European mechanized press or the earlier East Asian movable metal type technology."
})

# Sports (3 cases)
cases.append({
    "id": "t1_dispute_hard_629",
    "difficulty": "hard",
    "subcategory": "cross_source_contradiction",
    "query": "What is the fastest recorded tennis serve in professional history?",
    "contexts": [
        "The ATP official records list John Isner's serve of 157.2 mph (253.0 km/h) at the 2016 Davis Cup as the fastest recorded serve in professional men's tennis, measured by Hawk-Eye electronic line-calling technology.",
        "The Guinness World Records recognizes Sam Groth's serve of 163.7 mph (263.4 km/h), hit during a 2012 Challenger event in Busan, South Korea, as the fastest tennis serve ever recorded, though this was measured by a Doppler radar gun rather than Hawk-Eye."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "atp_official_records_2024", "source_type": "reference", "authority": "official"},
        {"source_id": "guinness_tennis_serve", "source_type": "reference", "authority": "official"}
    ],
    "description": "ATP and Guinness World Records recognize different serves as the fastest due to different measurement technologies",
    "rationale": "The ATP uses Hawk-Eye (camera-based) measuring 157.2 mph for Isner, while Guinness accepts a Doppler radar measurement of 163.7 mph for Groth. The discrepancy stems from different measurement standards and the ATP does not recognize radar gun readings for its official records."
})

cases.append({
    "id": "t1_dispute_hard_630",
    "difficulty": "hard",
    "subcategory": "cross_source_contradiction",
    "query": "How many career goals did Pele score?",
    "contexts": [
        "FIFA's official website states that Pele scored 757 goals in 831 official matches during his career with Santos FC, the New York Cosmos, and the Brazilian national team.",
        "The Pele Foundation and the Santos FC museum count 1,283 goals when including friendly matches, exhibition games, and unofficial international tours, a figure that Pele himself frequently cited during his lifetime.",
        "The Rec.Sport.Soccer Statistics Foundation (RSSSF), an independent football statistics organization, has documented 767 goals in official competitive matches after reviewing match reports and club records, noting that some of FIFA's early match classifications contain errors."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "fifa_pele_profile", "source_type": "reference", "authority": "official"},
        {"source_id": "pele_foundation_records", "source_type": "reference", "authority": "primary"},
        {"source_id": "rsssf_pele_goals", "source_type": "reference", "authority": "expert"}
    ],
    "description": "FIFA, the Pele Foundation, and independent statisticians all cite different career goal totals for Pele",
    "rationale": "The dispute centers on which matches count as 'official': FIFA says 757 in official matches, the Pele Foundation counts 1,283 including friendlies, and the RSSSF independently verified 767 in competitive play. There is no consensus even among credible sources on the correct number."
})

cases.append({
    "id": "t1_dispute_hard_631",
    "difficulty": "hard",
    "subcategory": "cross_source_contradiction",
    "query": "What is the correct length of a marathon in miles?",
    "contexts": [
        "World Athletics (formerly IAAF) defines the official marathon distance as 42.195 kilometers, which it states equals 26 miles 385 yards (26.2188 miles), the standard used for all sanctioned races worldwide since 1921.",
        "The Boston Athletic Association's course measurement documentation states the Boston Marathon course is certified at 26 miles and 385 yards via calibrated Jones Counter measurements, but notes that due to point-to-point course topology with a net elevation drop of 459 feet, times run on the course are not eligible for world records under World Athletics Rule 260.28(c).",
        "A 2019 analysis in the Journal of Sports Sciences measured GPS data from 37,000 runners across six World Marathon Majors and found that the average distance actually run by participants was 26.4-26.7 miles due to tangent deviation, weaving, and course crowding effects."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "world_athletics_rules_2024", "source_type": "reference", "authority": "official"},
        {"source_id": "baa_course_certification", "source_type": "reference", "authority": "official"},
        {"source_id": "jss_marathon_gps_2019", "source_type": "academic", "authority": "primary"}
    ],
    "description": "The official marathon distance is defined but sources disagree on whether commonly run marathon courses actually match that distance in practice",
    "rationale": "While the official distance is 26.2188 miles, the Boston course has elevation issues affecting record eligibility, and GPS data shows runners actually cover 26.4-26.7 miles. The 'correct length' depends on whether you mean the defined distance, certified course distance, or distance actually run."
})

# Finance (3 cases)
cases.append({
    "id": "t1_dispute_hard_632",
    "difficulty": "hard",
    "subcategory": "cross_source_contradiction",
    "query": "What is the average annual return of the S&P 500?",
    "contexts": [
        "According to data from NYU Stern School of Business (Aswath Damodaran's dataset), the arithmetic average annual return of the S&P 500 from 1928 to 2023 was 11.66%, including dividends.",
        "Vanguard's 2024 Market Perspectives report states that the S&P 500 has returned an average of 10.3% annually over the past 30 years (1994-2023), a figure frequently cited in retirement planning materials.",
        "When adjusted for inflation using CPI data from the Bureau of Labor Statistics, the real (inflation-adjusted) average annual return of the S&P 500 from 1928 to 2023 was approximately 8.0%, as calculated by the Federal Reserve Bank of St. Louis FRED database."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "nyu_stern_damodaran_2024", "source_type": "academic", "authority": "primary"},
        {"source_id": "vanguard_market_perspectives_2024", "source_type": "industry", "authority": "expert"},
        {"source_id": "fred_sp500_real_returns", "source_type": "government", "authority": "official"}
    ],
    "description": "Three financial sources cite different average annual S&P 500 returns: 11.66%, 10.3%, and 8.0%",
    "rationale": "The disagreement stems from different time periods (1928-2023 vs 30-year), nominal vs real returns, and arithmetic vs geometric averaging. All three numbers are factually correct in their own terms but give very different impressions of stock market performance."
})

cases.append({
    "id": "t1_dispute_hard_633",
    "difficulty": "hard",
    "subcategory": "cross_source_contradiction",
    "query": "What is the current U.S. national debt?",
    "contexts": [
        "The U.S. Treasury's Daily Treasury Statement for January 31, 2025 shows the total public debt outstanding at $36.22 trillion, which includes both debt held by the public ($28.91 trillion) and intragovernmental holdings ($7.31 trillion).",
        "The Congressional Budget Office's February 2025 budget outlook reports federal debt held by the public at $28.9 trillion (approximately 99% of GDP), which it notes is the economically relevant measure because intragovernmental debt represents money the government owes to itself.",
        "USDebtClock.org, a widely cited real-time tracker, displayed $36.4 trillion on February 1, 2025, and projects total unfunded liabilities including Social Security and Medicare obligations at over $200 trillion."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "treasury_daily_statement_2025", "source_type": "government", "authority": "official"},
        {"source_id": "cbo_budget_outlook_2025", "source_type": "government", "authority": "official"},
        {"source_id": "usdebtclock_2025", "source_type": "reference", "authority": "secondary"}
    ],
    "description": "Sources cite U.S. national debt as $28.9T, $36.2T, or $200T+ depending on what obligations are included",
    "rationale": "The Treasury reports total public debt ($36.2T), the CBO focuses on debt held by public ($28.9T) as the economically meaningful figure, and USDebtClock includes unfunded liabilities ($200T+). The 'national debt' depends entirely on which definition is used."
})

cases.append({
    "id": "t1_dispute_hard_634",
    "difficulty": "hard",
    "subcategory": "cross_source_contradiction",
    "query": "What is the global inflation rate as of 2024?",
    "contexts": [
        "The International Monetary Fund's World Economic Outlook (October 2024) projects global headline inflation at 5.8% for 2024, down from 6.8% in 2023, using a GDP-weighted average across 196 countries.",
        "The World Bank's Global Economic Prospects (January 2025) reports 2024 global inflation at 4.2%, calculated as a median across all countries rather than a GDP-weighted average, which reduces the influence of large emerging economies with high inflation."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "imf_weo_oct_2024", "source_type": "government", "authority": "official"},
        {"source_id": "world_bank_gep_jan_2025", "source_type": "government", "authority": "official"}
    ],
    "description": "IMF and World Bank report different global inflation rates for 2024 (5.8% vs 4.2%) due to different aggregation methods",
    "rationale": "The IMF uses GDP-weighted averaging (giving more weight to large high-inflation economies) yielding 5.8%, while the World Bank uses median-country inflation yielding 4.2%. Both are official international financial institutions using the same underlying country data but different statistical approaches."
})

# Technology (3 cases)
cases.append({
    "id": "t1_dispute_hard_635",
    "difficulty": "hard",
    "subcategory": "cross_source_contradiction",
    "query": "How much energy does Bitcoin mining consume annually?",
    "contexts": [
        "The Cambridge Centre for Alternative Finance Bitcoin Electricity Consumption Index estimates Bitcoin's annualized electricity consumption at 95.5 TWh as of January 2025, based on an economic model that accounts for miner profitability and hardware efficiency.",
        "A 2024 report by the International Energy Agency (IEA) estimates Bitcoin mining consumed approximately 130 TWh in 2024, comparable to the electricity consumption of Argentina, using top-down analysis of global hashrate and assumed power usage effectiveness.",
        "Greenpeace's 'Change the Code, Not the Climate' campaign cites Bitcoin energy consumption at 173 TWh per year, referencing Digiconomist's index which includes estimates of embodied energy in hardware manufacturing and cooling infrastructure."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "cambridge_cbeci_2025", "source_type": "academic", "authority": "primary"},
        {"source_id": "iea_crypto_energy_2024", "source_type": "government", "authority": "official"},
        {"source_id": "greenpeace_bitcoin_campaign", "source_type": "report", "authority": "secondary"}
    ],
    "description": "Three sources estimate Bitcoin energy consumption at 95.5, 130, and 173 TWh/year using different methodologies and scope definitions",
    "rationale": "Cambridge uses economic modeling (95.5 TWh), IEA uses top-down hashrate analysis (130 TWh), and Digiconomist includes hardware lifecycle energy (173 TWh). The estimates differ by nearly 2x because they define 'energy consumption' differently and use different modeling approaches."
})

cases.append({
    "id": "t1_dispute_hard_636",
    "difficulty": "hard",
    "subcategory": "cross_source_contradiction",
    "query": "What percentage of internet traffic is generated by bots?",
    "contexts": [
        "Imperva's 2024 Bad Bot Report (analyzing data from the Imperva global network) states that 49.6% of all internet traffic in 2023 was generated by bots, with bad bots accounting for 32% and good bots (search crawlers, monitoring services) accounting for 17.6%.",
        "Cloudflare's 2024 Radar Year-in-Review report, based on traffic across its network serving approximately 20% of all websites, estimates bot traffic at 38% of total internet traffic, with automated API calls and AI training crawlers growing 40% year-over-year.",
        "Akamai's State of the Internet Report (Q4 2024) measured bot traffic at 42% of web requests across its content delivery network, noting significant variation by industry: financial services saw 65% bot traffic while media sites averaged 35%."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "imperva_bot_report_2024", "source_type": "industry", "authority": "expert"},
        {"source_id": "cloudflare_radar_2024", "source_type": "industry", "authority": "expert"},
        {"source_id": "akamai_soti_q4_2024", "source_type": "industry", "authority": "expert"}
    ],
    "description": "Three major CDN/security companies report bot traffic as 38%, 42%, and 49.6% of internet traffic",
    "rationale": "Each company measures bot traffic through its own network, which has different customer composition and detection capabilities. Imperva reports 49.6%, Cloudflare 38%, and Akamai 42%. The true figure is unknowable because each vendor sees only a portion of the internet."
})

cases.append({
    "id": "t1_dispute_hard_637",
    "difficulty": "hard",
    "subcategory": "cross_source_contradiction",
    "query": "How many software developers are there worldwide?",
    "contexts": [
        "Evans Data Corporation's Global Developer Population and Demographics Study (2024 edition) estimates 28.7 million professional software developers worldwide, based on surveys of companies, job posting analysis, and government labor statistics across 40 countries.",
        "GitHub's 2024 Octoverse report states that GitHub now has over 100 million developer accounts, with 31 million accounts active in the past year, though this includes hobbyists, students, and contributors who are not professional developers.",
        "SlashData's Developer Nation survey (Q1 2025) estimates 43.1 million active software developers globally, using a broader definition that includes part-time developers, DevOps engineers, data scientists who code, and technical managers who write code regularly."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "evans_data_2024", "source_type": "industry", "authority": "primary"},
        {"source_id": "github_octoverse_2024", "source_type": "industry", "authority": "primary"},
        {"source_id": "slashdata_devnation_2025", "source_type": "industry", "authority": "primary"}
    ],
    "description": "Industry sources estimate the global developer population at 28.7M, 31M active on GitHub, or 43.1M depending on definition",
    "rationale": "Evans Data counts only professional developers (28.7M), GitHub reports active accounts (31M, mixing professional and hobbyist), and SlashData uses a broad definition including part-time coders (43.1M). The count depends entirely on who qualifies as a 'software developer.'"
})

# ===========================================================================
# SUBCATEGORY 2: source_authority_conflict (10 cases, IDs 638-647)
# Multi-source: authoritative source vs weaker source disagree.
# Domain spread: 2 science, 2 law, 2 finance, 2 health, 2 technology
# ===========================================================================

# Science (2)
cases.append({
    "id": "t1_dispute_hard_638",
    "difficulty": "hard",
    "subcategory": "source_authority_conflict",
    "query": "Is microwave radiation from cell phones linked to cancer?",
    "contexts": [
        "The World Health Organization's International Agency for Research on Cancer (IARC) classified radiofrequency electromagnetic fields as 'possibly carcinogenic to humans' (Group 2B) in 2011, based on limited evidence of increased glioma risk among heavy cell phone users from the Interphone study and Hardell group studies.",
        "The U.S. National Toxicology Program (NTP) 2018 study, a 10-year, $30 million investigation exposing rats to cell phone radiation, found 'clear evidence' of heart tumors (schwannomas) and 'some evidence' of brain tumors (malignant gliomas) in male rats at high exposure levels.",
        "A widely cited 2020 blog post by physicist Dr. Sabine Hossenfelder argues that the NTP study is irrelevant because the radiation levels used were far higher than typical human exposure, and that basic physics shows non-ionizing radiation at cell phone frequencies cannot break DNA bonds or cause mutations."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "who_iarc_rf_2011", "source_type": "government", "authority": "official"},
        {"source_id": "ntp_cellphone_study_2018", "source_type": "government", "authority": "official"},
        {"source_id": "hossenfelder_blog_2020", "source_type": "blog", "authority": "community"}
    ],
    "description": "Two major government agencies found possible cancer links from cell phone radiation while a popular science blog dismisses the findings on physics grounds",
    "rationale": "WHO/IARC (official, primary) classifies RF as possibly carcinogenic, the NTP (official) found clear evidence in rodents, but a physics blogger (community) argues the mechanism is physically impossible. The authoritative sources suggest concern while the weaker source provides a plausible physics-based counterargument."
})

cases.append({
    "id": "t1_dispute_hard_639",
    "difficulty": "hard",
    "subcategory": "source_authority_conflict",
    "query": "Are neonicotinoid pesticides the primary cause of bee colony collapse?",
    "contexts": [
        "The European Food Safety Authority (EFSA) 2018 scientific assessment concluded that three neonicotinoid pesticides (clothianidin, imidacloprid, and thiamethoxam) pose unacceptable risks to wild and managed bees, leading to the EU's outdoor use ban. The assessment was based on over 1,500 studies and found both acute and chronic effects on bee survival, reproduction, and behavior.",
        "A 2023 position paper published by CropLife International, the global trade association representing pesticide manufacturers including Bayer and Syngenta, argues that bee population declines are primarily driven by the Varroa destructor mite, habitat loss, and climate stress, and that laboratory studies showing neonicotinoid harm use unrealistically high exposure levels that do not reflect field conditions."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "efsa_neonicotinoid_2018", "source_type": "government", "authority": "official"},
        {"source_id": "croplife_bee_health_2023", "source_type": "industry", "authority": "secondary"}
    ],
    "description": "EU food safety authority implicates neonicotinoids as a major bee threat while the pesticide industry trade group attributes decline primarily to mites and habitat loss",
    "rationale": "EFSA (official, government) conducted a comprehensive review finding unacceptable risk, while CropLife (industry, secondary) argues the real drivers are parasites and habitat. The industry source has a clear financial interest but raises scientifically valid points about field vs lab exposure levels."
})

# Law (2)
cases.append({
    "id": "t1_dispute_hard_640",
    "difficulty": "hard",
    "subcategory": "source_authority_conflict",
    "query": "Are tip pools that include managers legal under U.S. federal law?",
    "contexts": [
        "The U.S. Department of Labor's final rule implementing the Consolidated Appropriations Act of 2018, effective December 2021, states that employers who do not take a tip credit may include supervisors and managers in tip pools, provided those managers do not have hiring/firing authority and their 'managerial' duties constitute less than 20% of their work time in the tipped role.",
        "A 2024 article on the restaurant industry blog 'Toast Restaurant Management' advises that 'managers can never participate in tip pools under federal law' and recommends restaurants establish separate service charge systems to supplement manager compensation, citing the Fair Labor Standards Act Section 3(m) as the controlling statute."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "dol_tip_pool_rule_2021", "source_type": "government", "authority": "official"},
        {"source_id": "toast_blog_tip_pools_2024", "source_type": "blog", "authority": "community"}
    ],
    "description": "DOL official rule allows managers in tip pools under specific conditions while an industry blog states it is categorically illegal",
    "rationale": "The DOL's official rule (the authoritative source) permits managers in tip pools when the employer does not take a tip credit and the manager's duties meet specific thresholds. The restaurant blog (community source) states a flat prohibition that reflects the older pre-2018 rule. The blog is factually wrong but widely read in the industry, creating real-world confusion."
})

cases.append({
    "id": "t1_dispute_hard_641",
    "difficulty": "hard",
    "subcategory": "source_authority_conflict",
    "query": "Does the GDPR apply to companies outside the European Union?",
    "contexts": [
        "Article 3(2) of the General Data Protection Regulation (EU) 2016/679 explicitly states that the GDPR applies to organizations not established in the EU when they process personal data of individuals who are in the EU, if the processing relates to offering goods or services to such individuals or monitoring their behavior within the EU. The European Data Protection Board's Guidelines 3/2018 further clarify that merely having a website accessible from the EU is insufficient to trigger GDPR applicability.",
        "A 2024 analysis published on the Forbes Technology Council contributor platform argues that the GDPR's extraterritorial reach is 'largely theoretical' for small and medium businesses outside the EU, noting that no enforcement action has been successfully executed against a non-EU company with no EU establishment, no EU bank accounts, and no EU assets, and that the estimated cost of cross-border enforcement makes pursuing small violators economically impractical for data protection authorities."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "gdpr_regulation_2016_679", "source_type": "government", "authority": "official"},
        {"source_id": "forbes_tech_council_gdpr_2024", "source_type": "news", "authority": "secondary"}
    ],
    "description": "The GDPR text clearly applies extraterritorially but a business publication argues the practical enforceability is minimal for non-EU companies",
    "rationale": "The GDPR (official) explicitly claims extraterritorial jurisdiction over non-EU companies processing EU personal data. The Forbes contributor (secondary) argues this is de facto unenforceable for small foreign companies. The legal text and practical reality genuinely diverge, creating a dispute about what 'applies' means."
})

# Finance (2)
cases.append({
    "id": "t1_dispute_hard_642",
    "difficulty": "hard",
    "subcategory": "source_authority_conflict",
    "query": "Is passive index investing causing a stock market bubble?",
    "contexts": [
        "A 2024 working paper by researchers at the Federal Reserve Board of Governors, published in the FEDS Notes series, examined whether passive fund flows distort stock prices and concluded that 'the evidence does not support the hypothesis that passive investing has created a broad market bubble,' noting that arbitrage mechanisms in the market continue to function and that passive fund inflows track economic fundamentals rather than drive them.",
        "Michael Burry, the hedge fund manager featured in 'The Big Short' for predicting the 2008 financial crisis, told Bloomberg in a September 2024 interview that passive investing has created 'the next market bubble' because index funds buy stocks based on market cap rather than fundamentals, causing overvaluation of the largest companies and reducing price discovery. Burry compared it to the CDO crisis where 'capital allocation was divorced from analysis.'"
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "fed_feds_notes_passive_2024", "source_type": "government", "authority": "official"},
        {"source_id": "bloomberg_burry_interview_2024", "source_type": "news", "authority": "expert"}
    ],
    "description": "Federal Reserve researchers find no evidence of a passive investing bubble while a prominent investor who predicted the 2008 crisis warns one is forming",
    "rationale": "The Fed's research (official, methodical) finds no bubble evidence, while Michael Burry (expert with track record but individual opinion) warns of one. Both have credibility: the Fed has analytical rigor, Burry has a proven record of identifying bubbles others missed."
})

cases.append({
    "id": "t1_dispute_hard_643",
    "difficulty": "hard",
    "subcategory": "source_authority_conflict",
    "query": "Is cryptocurrency a good hedge against inflation?",
    "contexts": [
        "The Bank for International Settlements (BIS) Quarterly Review (March 2024) analyzed Bitcoin and Ethereum price behavior during the 2021-2023 global inflation surge and found that cryptocurrencies behaved as 'risk-on speculative assets rather than inflation hedges,' with correlation to NASDAQ exceeding 0.75 during high-inflation periods and significant drawdowns during monetary tightening.",
        "ARK Invest's 'Big Ideas 2025' research report, authored by Cathie Wood's team, argues that Bitcoin is 'digital gold' and the superior inflation hedge for the 21st century, citing its fixed supply cap of 21 million coins, increasing institutional adoption, and the historical 230% annualized return from 2011-2024 which vastly outpaced inflation in any measurement period."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "bis_quarterly_mar_2024", "source_type": "government", "authority": "official"},
        {"source_id": "ark_invest_big_ideas_2025", "source_type": "industry", "authority": "secondary"}
    ],
    "description": "The Bank for International Settlements found crypto behaves as a speculative asset during inflation while ARK Invest argues it is a superior inflation hedge",
    "rationale": "The BIS (official, neutral) presents empirical evidence that crypto correlated with risk assets during actual inflation, while ARK Invest (industry, pro-crypto) argues theoretical properties make it an inflation hedge. The dispute is between empirical historical performance and theoretical supply-side arguments."
})

# Health (2)
cases.append({
    "id": "t1_dispute_hard_644",
    "difficulty": "hard",
    "subcategory": "source_authority_conflict",
    "query": "Is intermittent fasting effective for long-term weight loss?",
    "contexts": [
        "A 2023 systematic review and meta-analysis published in the New England Journal of Medicine, analyzing 27 randomized controlled trials with a total of 3,912 participants followed for 12+ months, found that intermittent fasting produced weight loss statistically indistinguishable from continuous caloric restriction at the 12-month mark (mean difference: 0.4 kg, 95% CI: -0.8 to 1.6), and that dropout rates were higher in fasting groups (34% vs 26%).",
        "A viral 2024 YouTube video by Dr. Jason Fung (6.2 million views), a nephrologist and bestselling author of 'The Obesity Code,' presents intermittent fasting as 'the most powerful weight loss tool ever discovered,' citing insulin reduction as the key mechanism and referencing individual patient case studies showing 30-50 kg weight loss maintained over 2-3 years."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "nejm_if_metaanalysis_2023", "source_type": "academic", "authority": "primary"},
        {"source_id": "fung_youtube_if_2024", "source_type": "blog", "authority": "community"}
    ],
    "description": "A major meta-analysis finds intermittent fasting no better than caloric restriction while a popular physician influencer promotes it as uniquely powerful",
    "rationale": "The NEJM meta-analysis (primary, academic) found IF equivalent to caloric restriction with higher dropout, while Dr. Fung (community, popular) presents dramatic individual cases and a mechanistic argument. The authoritative evidence shows no special advantage but the popular source is more persuasive to the public."
})

cases.append({
    "id": "t1_dispute_hard_645",
    "difficulty": "hard",
    "subcategory": "source_authority_conflict",
    "query": "Should adults take a daily multivitamin supplement?",
    "contexts": [
        "The U.S. Preventive Services Task Force (USPSTF) 2022 recommendation statement, based on a systematic review of 84 studies with over 700,000 participants, concluded with a Grade I statement (insufficient evidence) that 'the current evidence is insufficient to assess the balance of benefits and harms of multivitamin supplementation for the prevention of cardiovascular disease, cancer, or mortality in the general adult population.'",
        "The supplement brand Nature Made's website and marketing materials state that 'taking a daily multivitamin helps fill nutritional gaps in your diet' and that their products are 'the #1 pharmacist recommended vitamin and supplement brand,' citing a Pharmacy Times survey of pharmacist recommendations.",
        "A 2024 post on the wellness blog MindBodyGreen, authored by a naturopathic doctor, recommends that 'every adult should take a high-quality multivitamin daily' because 'modern soil depletion has reduced nutrient density in food by up to 40% since the 1950s.'"
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "uspstf_multivitamin_2022", "source_type": "government", "authority": "official"},
        {"source_id": "nature_made_website", "source_type": "industry", "authority": "secondary"},
        {"source_id": "mindbodygreen_vitamins_2024", "source_type": "blog", "authority": "community"}
    ],
    "description": "USPSTF finds insufficient evidence for daily multivitamins while supplement manufacturers and wellness blogs promote them",
    "rationale": "The USPSTF (official, systematic review) found insufficient evidence to recommend for or against multivitamins. Nature Made (industry, financial interest) markets their necessity, and a wellness blog (community) recommends them based on soil depletion claims. The authoritative source is agnostic while lower-authority sources make strong positive claims."
})

# Technology (2)
cases.append({
    "id": "t1_dispute_hard_646",
    "difficulty": "hard",
    "subcategory": "source_authority_conflict",
    "query": "Will artificial general intelligence (AGI) be achieved by 2030?",
    "contexts": [
        "A 2024 survey of 2,778 AI researchers published in the journal AI & Society, conducted by Katja Grace et al., found the median estimate for a 50% probability of human-level machine intelligence (HLMI) was 2047, with only 10% of respondents placing the date before 2030. The survey noted significant disagreement among experts, with estimates ranging from 2025 to never.",
        "OpenAI CEO Sam Altman stated in a January 2025 blog post titled 'The Intelligence Age' that 'we are now confident that we know how to build AGI as we have traditionally understood it' and predicted that 'superintelligence could be achieved within a few thousand days,' implying AGI by approximately 2027-2028. He cited scaling laws, improved training techniques, and internal benchmark results not yet publicly disclosed."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "grace_ai_survey_2024", "source_type": "academic", "authority": "primary"},
        {"source_id": "altman_blog_jan_2025", "source_type": "blog", "authority": "expert"}
    ],
    "description": "A large survey of AI researchers puts the median AGI date at 2047 while the CEO of a leading AI lab predicts it by ~2028",
    "rationale": "The expert survey (primary, academic, large sample) gives a median of 2047 with wide uncertainty, while Sam Altman (expert individual, interested party) predicts ~2028 based on proprietary data. The broad expert consensus is far more conservative than the leading AI company CEO's prediction."
})

cases.append({
    "id": "t1_dispute_hard_647",
    "difficulty": "hard",
    "subcategory": "source_authority_conflict",
    "query": "Is quantum computing a threat to current encryption standards?",
    "contexts": [
        "The National Institute of Standards and Technology (NIST) Post-Quantum Cryptography Standardization project, which published its first finalized post-quantum standards (FIPS 203, 204, 205) in August 2024, states that 'a cryptanalytically relevant quantum computer (CRQC) capable of breaking RSA-2048 or AES-256 is unlikely to exist before 2035' but that the transition to quantum-resistant algorithms should begin immediately due to 'harvest now, decrypt later' threats and the multi-year migration timeline.",
        "A 2024 Medium article by a cybersecurity consultant titled 'Quantum Computing Will Break All Encryption Within 5 Years' claims that recent advances in quantum error correction, particularly Google's Willow chip achieving below-threshold error rates, mean that 'every major encryption standard is on the verge of being cracked' and recommends businesses immediately abandon RSA and ECC in favor of lattice-based cryptography."
    ],
    "expected_mode": "disputed",
    "context_sources": [
        {"source_id": "nist_pqc_standards_2024", "source_type": "government", "authority": "official"},
        {"source_id": "medium_quantum_threat_2024", "source_type": "blog", "authority": "community"}
    ],
    "description": "NIST says quantum computers won't break current encryption before 2035 while a consultant blog claims it will happen within 5 years",
    "rationale": "NIST (official, authoritative) assesses the timeline as pre-2035 while recommending proactive migration. The Medium blog (community, alarmist) claims encryption will be broken within 5 years based on extrapolation from recent hardware demos. The authoritative source is measured while the weaker source is sensationalist, but both agree migration is needed."
})

# ===========================================================================
# SUBCATEGORY 3: numerical_conflict (10 cases, IDs 648-657)
# Single source style: different numbers cited for the same metric.
# Domain spread: 2 science, 2 finance, 2 sports, 2 technology, 2 history
# ===========================================================================

# Science (2)
cases.append({
    "id": "t1_dispute_hard_648",
    "difficulty": "hard",
    "subcategory": "numerical_conflict",
    "query": "How many neurons are in the human brain?",
    "contexts": [
        "For decades, neuroscience textbooks and reference materials have stated that the human brain contains approximately 100 billion neurons, a figure attributed to a 1988 review article and widely repeated in medical education.",
        "Brazilian neuroscientist Suzana Herculano-Houzel's 2009 study using the isotropic fractionator method, published in the Journal of Comparative Neurology, counted approximately 86 billion neurons in the human brain, roughly 14% fewer than the commonly cited figure.",
        "A 2024 update from Herculano-Houzel's lab incorporating samples from 15 additional brains revised the estimate to 88 billion neurons with significant individual variation (standard deviation of 8 billion), noting that neuron count decreases by approximately 10% between ages 20 and 80."
    ],
    "expected_mode": "disputed",
    "description": "The commonly cited 100 billion neuron figure differs significantly from empirical counts of 86-88 billion",
    "rationale": "Textbooks cite 100 billion neurons (a round number without clear empirical basis), while direct counting studies find 86-88 billion with substantial individual variation. The 14% discrepancy matters for quantitative neuroscience, and even the empirical studies disagree slightly between 2009 and 2024."
})

cases.append({
    "id": "t1_dispute_hard_649",
    "difficulty": "hard",
    "subcategory": "numerical_conflict",
    "query": "What is the speed of gravity?",
    "contexts": [
        "Einstein's general theory of relativity predicts that gravitational waves propagate at exactly the speed of light: 299,792,458 meters per second (c). This is a fundamental prediction of the theory, not an approximation.",
        "The LIGO and Virgo collaborations' measurement from the binary neutron star merger GW170817 in August 2017, combined with the simultaneous gamma-ray burst GRB 170817A detected 1.7 seconds later by the Fermi satellite, constrained the speed of gravity to be within -3 x 10^-15 to +7 x 10^-16 of the speed of light.",
        "A 2023 preprint posted on arXiv by physicist Atsushi Nishizawa argues that modified gravity theories allowing massive gravitons predict a gravitational wave speed slightly below c, with the deviation proportional to the graviton mass. If the graviton mass is at the upper bound currently permitted by LIGO data (m_g < 1.27 x 10^-23 eV/c^2), gravity could be as much as 10^-19 slower than light."
    ],
    "expected_mode": "disputed",
    "description": "Theory predicts gravity travels at exactly the speed of light, measurement confirms it to extreme precision, but a theoretical possibility of deviation remains",
    "rationale": "General relativity predicts c exactly, LIGO confirmed it to 15 decimal places, but a preprint argues massive graviton theories permit an unmeasurably small deviation. Whether the speed of gravity is 'exactly c' or 'indistinguishable from c within current measurement precision' is a genuine scientific nuance."
})

# Finance (2)
cases.append({
    "id": "t1_dispute_hard_650",
    "difficulty": "hard",
    "subcategory": "numerical_conflict",
    "query": "What was the peak unemployment rate during the 2008 financial crisis in the United States?",
    "contexts": [
        "The Bureau of Labor Statistics (BLS) official U-3 unemployment rate reached a peak of 10.0% in October 2009, representing 15.4 million unemployed Americans who were actively seeking work.",
        "The BLS's broader U-6 unemployment measure, which includes discouraged workers who stopped looking for jobs and those working part-time for economic reasons, peaked at 17.1% in late 2009 and remained above 15% through most of 2010.",
        "A 2012 study by economists at the Federal Reserve Bank of Atlanta estimated that when including workers who left the labor force entirely and were not captured even by U-6, the effective unemployment rate peaked at approximately 23% in early 2010."
    ],
    "expected_mode": "disputed",
    "description": "The peak unemployment rate during the 2008 crisis is reported as 10%, 17.1%, or 23% depending on which definition of unemployment is used",
    "rationale": "The headline U-3 rate was 10.0%, the broader U-6 was 17.1%, and including all labor force dropouts gives roughly 23%. All three are factually defensible measurements of 'unemployment' but differ by more than 2x, giving drastically different impressions of crisis severity."
})

cases.append({
    "id": "t1_dispute_hard_651",
    "difficulty": "hard",
    "subcategory": "numerical_conflict",
    "query": "How much student loan debt is outstanding in the United States?",
    "contexts": [
        "The Federal Reserve Bank of New York's Quarterly Report on Household Debt and Credit (Q4 2024) reports total student loan balances at $1.74 trillion, based on data from Equifax consumer credit reports covering approximately 97% of the U.S. adult population with a credit file.",
        "The U.S. Department of Education's Federal Student Aid data center reports the federal student loan portfolio at $1.61 trillion as of September 30, 2024, across 43.2 million borrowers, noting this excludes approximately $140 billion in private student loans not held or guaranteed by the federal government.",
        "The College Board's 'Trends in Student Aid 2024' report cites total outstanding student debt at $1.77 trillion, combining Department of Education federal loan data with estimates of private student loan balances from MeasureOne and the Consumer Financial Protection Bureau."
    ],
    "expected_mode": "disputed",
    "description": "Three sources report U.S. student loan debt as $1.61T, $1.74T, or $1.77T depending on scope and data source",
    "rationale": "The Department of Education counts only federal loans ($1.61T), the NY Fed uses credit reports ($1.74T), and the College Board combines sources ($1.77T). The $160 billion spread reflects genuine disagreement about scope (federal only vs all student debt) and measurement methodology (administrative records vs credit reports)."
})

# Sports (2)
cases.append({
    "id": "t1_dispute_hard_652",
    "difficulty": "hard",
    "subcategory": "numerical_conflict",
    "query": "What is the fastest a human has ever run in miles per hour?",
    "contexts": [
        "Usain Bolt reached a peak speed of 27.78 mph (44.72 km/h) during his 100m world record run of 9.58 seconds at the 2009 World Championships in Berlin, as measured by laser velocity tracking between the 60m and 80m marks.",
        "The International Association of Athletics Federations (now World Athletics) recorded Bolt's top instantaneous speed at 27.44 mph (44.16 km/h) using their own split timing system, which measures 10-meter segment speeds rather than continuous laser tracking.",
        "A 2017 biomechanical analysis published in the Journal of Sports Sciences, using high-speed camera footage at 200 frames per second, estimated Bolt's peak speed at 28.0 mph (45.07 km/h) during a specific stride between 65m and 67m, arguing that both timing systems underestimate peak velocity because they average over multi-meter segments."
    ],
    "expected_mode": "disputed",
    "description": "Three different measurement methods report Usain Bolt's top speed as 27.44, 27.78, or 28.0 mph",
    "rationale": "Laser tracking gives 27.78 mph, official split timing gives 27.44 mph, and high-speed camera analysis gives 28.0 mph. The discrepancy arises because finer temporal resolution captures higher instantaneous peaks, and no two measurement systems agree on the 'fastest' a human has run."
})

cases.append({
    "id": "t1_dispute_hard_653",
    "difficulty": "hard",
    "subcategory": "numerical_conflict",
    "query": "How many people watched the 2024 Super Bowl?",
    "contexts": [
        "Nielsen's official ratings report for Super Bowl LVIII (Kansas City Chiefs vs. San Francisco 49ers, February 11, 2024) measured an average audience of 123.4 million viewers across CBS television broadcast and Paramount+ streaming, making it the most-watched telecast in U.S. history.",
        "CBS parent company Paramount Global reported a total audience of 200 million viewers when including all viewing platforms and any amount of viewing time (as opposed to the Nielsen average-minute audience), along with pre-game and post-game coverage.",
        "The NFL's own post-event release cited 'more than 130 million' viewers, a figure that includes Univision's Spanish-language simulcast and Nickelodeon's family-oriented alternate broadcast, which Nielsen tracked separately from the primary CBS measurement."
    ],
    "expected_mode": "disputed",
    "description": "Super Bowl LVIII viewership is reported as 123.4M, 130M+, or 200M depending on measurement methodology",
    "rationale": "Nielsen's standard average-minute audience was 123.4M, adding alternate broadcasts gives 130M+, and counting any amount of viewing across all platforms yields 200M. The 'correct' viewership depends entirely on whether you mean sustained viewership or any-touch reach."
})

# Technology (2)
cases.append({
    "id": "t1_dispute_hard_654",
    "difficulty": "hard",
    "subcategory": "numerical_conflict",
    "query": "How much data does the world generate per day?",
    "contexts": [
        "IDC's Global DataSphere Forecast (2024 update) estimates that the world generates approximately 402 exabytes of data per day (147 zettabytes per year), counting all data created, captured, copied, and consumed across enterprise and consumer segments.",
        "Statista's Digital Economy Compass 2024 cites daily data creation at 328 exabytes (120 zettabytes per year), using a methodology that counts only newly created and captured data while excluding copies, replicas, and ephemeral data that is immediately discarded.",
        "A 2024 IEEE Spectrum article estimates daily data generation at approximately 220 exabytes, noting that many commonly cited figures are inflated by counting transient data like RAM contents, network packet headers, and sensor readings that are never stored or analyzed."
    ],
    "expected_mode": "disputed",
    "description": "Estimates of daily global data generation range from 220 to 402 exabytes depending on what counts as 'data'",
    "rationale": "IDC counts all data including copies (402 EB/day), Statista excludes duplicates (328 EB/day), and IEEE Spectrum excludes ephemeral/transient data (220 EB/day). The nearly 2x spread stems from definitional differences about whether copies, duplicates, and transient data should be counted."
})

cases.append({
    "id": "t1_dispute_hard_655",
    "difficulty": "hard",
    "subcategory": "numerical_conflict",
    "query": "What percentage of emails sent globally are spam?",
    "contexts": [
        "Cisco's Talos Intelligence 2024 Annual Report, based on analysis of approximately 600 billion emails per day passing through Cisco's email security infrastructure, reports that 85.6% of all email traffic is spam, with the remainder split between legitimate email (12.2%) and phishing/malware (2.2%).",
        "Statista's 2024 data, sourced from Kaspersky Lab's anti-spam research, places the global spam rate at 45.6% of all email traffic for the year, noting a steady decline from over 70% in the early 2010s due to improved filtering and anti-bot enforcement by ISPs.",
        "Google reported in its 2024 Transparency Report that Gmail blocks more than 99.9% of spam, phishing, and malware from reaching user inboxes, and estimates that approximately 50% of emails it receives are spam, based on its classification algorithms processing 1.8 billion Gmail accounts."
    ],
    "expected_mode": "disputed",
    "description": "Sources report global spam rates as 45.6%, 50%, or 85.6% of all email traffic",
    "rationale": "Cisco sees 85.6% spam at the network infrastructure level, Google sees about 50% at the consumer email level, and Kaspersky reports 45.6%. The discrepancy reflects different vantage points: network-level scanning catches spam before it reaches mailboxes, while user-facing services see a pre-filtered subset."
})

# History (2)
cases.append({
    "id": "t1_dispute_hard_656",
    "difficulty": "hard",
    "subcategory": "numerical_conflict",
    "query": "How many people died in the Bengal famine of 1943?",
    "contexts": [
        "The official Famine Inquiry Commission report (1945), chaired by Sir John Woodhead and commissioned by the British colonial government, estimated 1.5 million deaths directly attributable to the famine in Bengal province.",
        "Amartya Sen, the Nobel Prize-winning economist, in his seminal 1981 work 'Poverty and Famines: An Essay on Entitlement and Deprivation,' estimated approximately 3 million deaths, incorporating excess mortality from famine-related disease epidemics (malaria, cholera, smallpox) that persisted through 1944.",
        "A 2019 demographic study published in the Indian Economic & Social History Review by historians Mukherjee and Vaidyanathan, using newly available provincial census records and parish burial registers, estimated total excess mortality at 3.8 million, arguing that both previous estimates undercounted rural deaths due to poor registration in remote areas."
    ],
    "expected_mode": "disputed",
    "description": "Death toll estimates for the 1943 Bengal famine range from 1.5 to 3.8 million across official and academic sources",
    "rationale": "The colonial government estimated 1.5M (narrow definition, political interest in minimizing), Sen estimated 3M (including disease sequelae), and a 2019 study found 3.8M using better data. The 2.5x range reflects both definitional disputes about what counts as a famine death and genuine data gaps in colonial-era record keeping."
})

cases.append({
    "id": "t1_dispute_hard_657",
    "difficulty": "hard",
    "subcategory": "numerical_conflict",
    "query": "What was the population of the Americas before European contact?",
    "contexts": [
        "Alfred Kroeber's 1939 estimate, which dominated scholarship for decades, placed the pre-contact population of the Western Hemisphere at approximately 8.4 million, based on extrapolation from early colonial census records and ethnographic observations.",
        "Henry Dobyns's 1966 study in the journal Current Anthropology estimated a pre-contact population of 90 to 112 million for the entire hemisphere, using disease-mortality ratios applied backward from known post-contact population nadirs and arguing that European diseases killed 90-95% of indigenous populations.",
        "A 2019 study published in Quaternary Science Reviews by Koch et al. estimated a pre-contact population of approximately 60 million, based on combining archaeological site density analysis, agricultural land-use modeling, and the measurable atmospheric CO2 decline following mass depopulation (the 'Orbis spike' of 1610)."
    ],
    "expected_mode": "disputed",
    "description": "Scholarly estimates of pre-Columbian population range from 8.4 million to 112 million, a 13x spread",
    "rationale": "Kroeber estimated 8.4M (colonial extrapolation), Dobyns estimated 90-112M (disease modeling), and Koch et al. estimated 60M (atmospheric/archaeological evidence). The estimates span more than an order of magnitude because pre-contact census data does not exist and each methodology makes very different assumptions."
})

# ===========================================================================
# SUBCATEGORY 4: implicit_contradiction (10 cases, IDs 658-667)
# Single source: contexts don't directly contradict but imply incompatible conclusions.
# Domain spread: 2 science, 2 law, 2 finance, 2 health, 2 education
# ===========================================================================

# Science (2)
cases.append({
    "id": "t1_dispute_hard_658",
    "difficulty": "hard",
    "subcategory": "implicit_contradiction",
    "query": "Is this new drug candidate ready for Phase III clinical trials?",
    "contexts": [
        "The Phase II trial of compound BRX-4120 demonstrated a statistically significant reduction in tumor volume (38% shrinkage, p=0.003) compared to placebo in 240 patients with advanced non-small cell lung cancer over a 24-week treatment period.",
        "The trial's Data Safety Monitoring Board flagged that 12% of patients in the treatment arm developed Grade 3 or 4 hepatotoxicity (severe liver damage), compared to 1% in the placebo arm, with two treatment-related deaths during the study.",
        "The FDA's 2024 guidance on oncology drug development states that compounds advancing to Phase III should demonstrate 'an acceptable benefit-risk profile in the target population' and that 'serious hepatotoxicity occurring in more than 5% of patients typically requires additional dose-finding or formulation work before pivotal trial initiation.'"
    ],
    "expected_mode": "disputed",
    "description": "Strong efficacy data supports Phase III readiness but hepatotoxicity rates exceed FDA's stated threshold for advancement",
    "rationale": "The drug showed strong efficacy (38% tumor shrinkage, p=0.003), but 12% Grade 3-4 liver toxicity exceeds the FDA's 5% guidance threshold. The contexts don't directly say 'yes' or 'no' to Phase III, but the efficacy data implies readiness while the safety data implies more work is needed."
})

cases.append({
    "id": "t1_dispute_hard_659",
    "difficulty": "hard",
    "subcategory": "implicit_contradiction",
    "query": "Should this coastal city invest in building new seawalls?",
    "contexts": [
        "The city's engineering assessment estimates that a new seawall system would protect 15,000 homes and $4.2 billion in property from storm surge damage over a 50-year design life, with construction costs of $800 million and annual maintenance of $12 million.",
        "The latest NOAA regional sea level rise projection for this section of coastline forecasts 3.5 feet of rise by 2070 under the intermediate scenario, which would overtop the proposed seawall design height of 3 feet above current high tide levels.",
        "A University of Miami study on managed retreat economics found that relocating coastal residents before catastrophic flooding costs 40-60% less than post-disaster rebuilding and that seawall investments create 'moral hazard' by encouraging continued development in high-risk zones.",
        "Local property tax records show that waterfront homes within the seawall's protection zone generate $180 million per year in municipal tax revenue, representing 35% of the city's total property tax base."
    ],
    "expected_mode": "disputed",
    "description": "Engineering analysis supports seawall construction but climate projections suggest it will be insufficient within its design life, and economic analysis favors retreat",
    "rationale": "The engineering case (protect $4.2B in property for $800M) implies building is worthwhile. But the NOAA projection implies the seawall will be overtopped before its 50-year design life ends. The retreat study implies building is counterproductive. And the tax revenue data implies abandoning the area would devastate city finances. Each context points in a different direction."
})

# Law (2)
cases.append({
    "id": "t1_dispute_hard_660",
    "difficulty": "hard",
    "subcategory": "implicit_contradiction",
    "query": "Can the employer terminate this employee?",
    "contexts": [
        "The employee's annual performance review, completed on January 15, 2025, rated them 'Exceeds Expectations' with a score of 4.2 out of 5.0, including specific praise from their direct manager for 'exceptional client relationship management and consistent delivery of high-quality work product.'",
        "The company announced a reduction in force (RIF) on February 1, 2025, eliminating 15% of positions company-wide. The RIF selection criteria, documented in the HR policy manual, prioritize eliminating positions based on business need rather than individual performance.",
        "The employee signed an employment agreement on their hire date that includes a clause stating: 'Employee may be terminated at any time, with or without cause, subject to 30 days written notice and applicable severance as defined in Section 8.'",
        "The employee filed a formal complaint with the company's ethics hotline on January 28, 2025, alleging that their department head was falsifying quarterly revenue reports submitted to investors."
    ],
    "expected_mode": "disputed",
    "description": "At-will employment allows termination but strong performance, whistleblower timing, and RIF context create legal risk",
    "rationale": "The at-will agreement permits termination. The RIF provides business justification. But the employee has excellent performance (undermining 'cause'), and terminating them 3 days after they filed a whistleblower complaint creates potential retaliation liability. No context directly contradicts another, but together they imply an extremely risky termination."
})

cases.append({
    "id": "t1_dispute_hard_661",
    "difficulty": "hard",
    "subcategory": "implicit_contradiction",
    "query": "Is this contract enforceable?",
    "contexts": [
        "The services agreement between Apex Consulting LLC and DataStream Corp., executed on March 1, 2024, contains all required elements of a valid contract under New York law: offer, acceptance, consideration ($450,000 for 12 months of consulting services), mutual assent, and signatures of authorized representatives of both parties.",
        "Section 14.2 of the agreement states: 'This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to its conflict of laws principles.'",
        "DataStream Corp. is incorporated in Delaware but operates exclusively from offices in California. Apex Consulting LLC is a New York limited liability company. Neither party has any operations, employees, or registered agents in Delaware.",
        "California Civil Code Section 1717 and California Business and Professions Code Section 16600 contain mandatory provisions that cannot be waived by choice-of-law clauses, including limits on non-compete enforcement and mandatory fee-shifting in contract disputes."
    ],
    "expected_mode": "disputed",
    "description": "Contract has all formal validity elements but choice-of-law clause selecting Delaware may be overridden by California mandatory law",
    "rationale": "The contract appears facially valid with all required elements. But the Delaware choice-of-law clause may be unenforceable because neither party operates in Delaware, and California's mandatory statutes could override the chosen law for a company operating exclusively in California. The contexts don't say the contract is invalid but together imply serious enforceability questions."
})

# Finance (2)
cases.append({
    "id": "t1_dispute_hard_662",
    "difficulty": "hard",
    "subcategory": "implicit_contradiction",
    "query": "Is this company a good investment at its current valuation?",
    "contexts": [
        "NovaTech Inc. reported revenue growth of 42% year-over-year in its Q4 2024 earnings, reaching $2.1 billion in annual recurring revenue, with net revenue retention of 135% indicating strong expansion within existing customers.",
        "The company's current market capitalization of $85 billion implies a price-to-sales ratio of 40x, compared to the SaaS industry median of 12x and the top-quartile of 22x.",
        "NovaTech's CEO disclosed in the earnings call that the company expects to achieve GAAP profitability by Q3 2026, after burning through $340 million in cash during 2024, with $1.2 billion in cash reserves remaining.",
        "Three of NovaTech's five board members sold a combined $28 million in stock through 10b5-1 plans during Q4 2024, representing approximately 60% of their vested holdings."
    ],
    "expected_mode": "disputed",
    "description": "Strong growth metrics suggest upside but extreme valuation, cash burn, and insider selling imply downside risk",
    "rationale": "Revenue growth (42%) and retention (135%) signal a strong business. But 40x P/S (vs 12x median) implies the stock is extremely expensive. Cash burn of $340M/year with $1.2B remaining creates a 3.5-year runway. And heavy insider selling (60% of holdings) suggests those closest to the company are reducing exposure. The bullish and bearish signals are both strong but point in opposite directions."
})

cases.append({
    "id": "t1_dispute_hard_663",
    "difficulty": "hard",
    "subcategory": "implicit_contradiction",
    "query": "Should this pension fund increase its allocation to private equity?",
    "contexts": [
        "The pension fund's private equity portfolio has generated a net internal rate of return (IRR) of 14.2% over the past decade, compared to 10.8% for its public equity portfolio and 4.1% for fixed income, making it the top-performing asset class.",
        "An analysis by pension consultant Callan Associates notes that private equity returns are typically reported using IRR, which can be inflated by early capital distributions and leverage. When measured on a public market equivalent (PME) basis, the fund's PE portfolio outperformed public equities by only 1.1% annually, before accounting for management fees of 1.5% and carried interest of 20%.",
        "The fund currently has 22% of its $45 billion portfolio allocated to private equity, with $3.8 billion in unfunded commitments that could be called over the next 3-5 years. Its actuarial liability requires maintaining a 7.5% annual return on assets to remain fully funded.",
        "The fund's board fiduciary counsel advised that increasing illiquid holdings above 25% of total assets may impair the fund's ability to meet monthly benefit payments of $320 million without selling assets at a discount during market downturns."
    ],
    "expected_mode": "disputed",
    "description": "Private equity appears to outperform other assets but adjusted returns are marginal, and liquidity constraints limit further allocation",
    "rationale": "The IRR data (14.2%) implies PE is the best performer and should be increased. But on a fee-adjusted PME basis, the outperformance shrinks to near zero. The unfunded commitments create future liquidity demands. And fiduciary counsel warns that exceeding 25% illiquid assets risks benefit payment disruption. Each fact is consistent but they imply incompatible conclusions about the investment decision."
})

# Health (2)
cases.append({
    "id": "t1_dispute_hard_664",
    "difficulty": "hard",
    "subcategory": "implicit_contradiction",
    "query": "Should this hospital implement AI-assisted radiology diagnosis?",
    "contexts": [
        "A 2024 randomized controlled trial at Johns Hopkins, published in The Lancet Digital Health, found that AI-assisted chest X-ray interpretation reduced diagnostic errors by 28% compared to radiologist-only reads, with the greatest improvement in detecting early-stage lung nodules under 6mm.",
        "The hospital's radiology department currently has 12 radiologists reading an average of 45,000 studies per month, with an average turnaround time of 2.8 hours. Three radiologists are within 5 years of retirement and the department has been unable to fill two open positions for over 18 months.",
        "The FDA-cleared AI system under consideration (Vendor: RadAssist Pro) carries an annual license fee of $1.2 million and requires integration with the existing PACS infrastructure at an estimated implementation cost of $800,000, plus ongoing IT support estimated at $200,000 per year.",
        "The hospital's malpractice insurer notified all clients in January 2025 that AI-assisted diagnoses create 'novel liability questions' and that premiums for institutions using AI diagnostic tools will increase by 15-25% pending development of case law around AI liability allocation."
    ],
    "expected_mode": "disputed",
    "description": "AI radiology reduces errors and addresses staffing gaps but creates significant costs and unresolved liability exposure",
    "rationale": "Better accuracy (28% fewer errors) and a worsening staffing crisis both argue for AI adoption. But $2.2M first-year costs and 15-25% malpractice premium increases argue against it. The staffing context implies urgency while the liability context implies caution. No source directly contradicts another but they lead to incompatible recommendations."
})

cases.append({
    "id": "t1_dispute_hard_665",
    "difficulty": "hard",
    "subcategory": "implicit_contradiction",
    "query": "Is this patient's lab result clinically significant?",
    "contexts": [
        "The patient's fasting blood glucose test returned a result of 118 mg/dL. The laboratory's reference range for normal fasting glucose is 70-100 mg/dL, and the American Diabetes Association defines prediabetes as fasting glucose of 100-125 mg/dL.",
        "The patient's previous three fasting glucose tests over the past 18 months were 95, 102, and 108 mg/dL respectively, showing a consistent upward trend of approximately 8 mg/dL every six months.",
        "The patient's HbA1c test, drawn on the same day, was 5.4%, which falls within the normal range (below 5.7%) and reflects average blood glucose control over the preceding 2-3 months.",
        "The patient reports having consumed a small amount of juice approximately 3 hours before the 'fasting' blood draw due to a miscommunication about fasting requirements."
    ],
    "expected_mode": "disputed",
    "description": "The glucose result is elevated into prediabetic range but may be invalidated by non-fasting status, and the HbA1c is normal",
    "rationale": "The glucose of 118 mg/dL is in the prediabetic range, and the upward trend (95->102->108->118) is concerning. But the patient wasn't truly fasting, which could explain the elevation. And the HbA1c of 5.4% (normal) suggests long-term glucose control is fine. The contexts imply both 'yes, this is prediabetes progressing' and 'no, this is a testing artifact.'"
})

# Education (2)
cases.append({
    "id": "t1_dispute_hard_666",
    "difficulty": "hard",
    "subcategory": "implicit_contradiction",
    "query": "Should this university eliminate its standardized test requirement for admissions?",
    "contexts": [
        "A 2024 study by the National Bureau of Economic Research found that SAT/ACT scores are the single strongest predictor of first-year college GPA (r=0.54) and four-year graduation rates (r=0.48) among commonly used admissions criteria, outperforming high school GPA (r=0.42 and r=0.39 respectively).",
        "The university's own internal analysis of its three-year test-optional pilot (2021-2024) found that students admitted without test scores had a first-year GPA only 0.08 points lower (3.24 vs 3.32) than those who submitted scores, and that six-year graduation rates were not yet available.",
        "During the test-optional period, applications from underrepresented minority students increased 34% and first-generation college student enrollment increased 22%, while the overall acceptance rate decreased from 32% to 24% due to the larger applicant pool.",
        "The university's U.S. News & World Report ranking dropped from #42 to #58 during the test-optional period, partially because the methodology penalizes institutions that cannot report median test scores for the full incoming class."
    ],
    "expected_mode": "disputed",
    "description": "Test scores predict success and rankings reward them, but removing the requirement boosted diversity with minimal academic impact",
    "rationale": "The NBER study implies tests are valuable predictors and should be kept. The university's own data shows minimal GPA difference without them. Diversity increased substantially during the test-optional period. But the ranking dropped 16 places. Each context supports a different conclusion and the tradeoffs between prediction, equity, and institutional reputation point in different directions."
})

cases.append({
    "id": "t1_dispute_hard_667",
    "difficulty": "hard",
    "subcategory": "implicit_contradiction",
    "query": "Is this school district's teacher retention strategy working?",
    "contexts": [
        "The district implemented a $5,000 annual retention bonus for teachers with 5+ years of experience in January 2023. Since implementation, the resignation rate for eligible teachers dropped from 18% to 11% year-over-year.",
        "An exit survey of the 47 teachers who still resigned despite the bonus found that 78% cited 'lack of administrative support' and 'excessive non-teaching duties' as their primary reasons for leaving, with only 6% mentioning compensation.",
        "The district's total spending on retention bonuses was $3.2 million in the 2023-2024 school year, paid from a federal ESSER grant that expires in September 2025. The district's general fund budget has a projected deficit of $4.8 million for 2025-2026.",
        "Neighboring districts have begun offering $7,000-$8,000 retention bonuses and signing bonuses of up to $10,000 for experienced teachers in shortage subjects (math, science, special education), funded by permanent local bond measures."
    ],
    "expected_mode": "disputed",
    "description": "Retention improved after the bonus but the root causes are non-financial, funding is temporary, and competitors are outbidding the district",
    "rationale": "The resignation rate dropped from 18% to 11%, implying the strategy works. But exit surveys show the real issues are administrative, not financial, suggesting the bonus masks the problem. The funding expires in 2025 with no replacement budget. And neighboring districts are offering more, creating a future retention arms race. Success by one metric, failure by underlying analysis."
})

# ===========================================================================
# Output
# ===========================================================================

output = {"cases": cases}

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "new_dispute_batch1.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Generated {len(cases)} dispute cases")
print(f"Output: {output_path}")

# Validate counts
subcategory_counts = {}
for case in cases:
    sub = case["subcategory"]
    subcategory_counts[sub] = subcategory_counts.get(sub, 0) + 1

print("\nSubcategory distribution:")
for sub, count in sorted(subcategory_counts.items()):
    print(f"  {sub}: {count}")

# Validate IDs are sequential
ids = [c["id"] for c in cases]
expected_ids = [f"t1_dispute_hard_{i}" for i in range(618, 668)]
assert ids == expected_ids, f"ID mismatch! Got {len(ids)} IDs, expected {len(expected_ids)}"
print(f"\nIDs verified: {ids[0]} through {ids[-1]}")

# Validate multi-source cases have context_sources
multi_source_subs = {"cross_source_contradiction", "source_authority_conflict"}
for case in cases:
    if case["subcategory"] in multi_source_subs:
        assert "context_sources" in case, f"{case['id']} missing context_sources"
        assert len(case["context_sources"]) == len(case["contexts"]), \
            f"{case['id']} context_sources length mismatch"
        for i, src in enumerate(case["context_sources"]):
            assert "source_id" in src, f"{case['id']} context_sources[{i}] missing source_id"
            assert "source_type" in src, f"{case['id']} context_sources[{i}] missing source_type"
            assert "authority" in src, f"{case['id']} context_sources[{i}] missing authority"
            valid_source_types = {"academic", "news", "government", "industry", "blog", "reference", "report"}
            valid_authorities = {"primary", "secondary", "tertiary", "official", "expert", "community"}
            assert src["source_type"] in valid_source_types, \
                f"{case['id']} context_sources[{i}] invalid source_type: {src['source_type']}"
            assert src["authority"] in valid_authorities, \
                f"{case['id']} context_sources[{i}] invalid authority: {src['authority']}"

print("Multi-source context_sources validated successfully")

# Validate single-source cases do NOT have context_sources
single_source_subs = {"numerical_conflict", "implicit_contradiction"}
for case in cases:
    if case["subcategory"] in single_source_subs:
        assert "context_sources" not in case, \
            f"{case['id']} should not have context_sources (single-source subcategory)"

print("Single-source cases verified (no context_sources)")
print("\nAll validations passed!")
