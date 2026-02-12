#!/usr/bin/env python3
"""Convert ~120 cases from over-represented domains to under-represented ones.

Maintains the same governance pattern (subcategory, difficulty, expected_mode)
while rewriting query + contexts to new domain content.
"""

import json
from pathlib import Path

# Each conversion: (case_id, target_domain, new_query_type,
#   new_query, new_contexts, new_description, new_rationale)

TRUSTWORTHY_DIRECT_CONVERSIONS = [
    # === social_media (6) ===
    ("t1_confident_hard_002", "social_media", "why",
     "Why did the brand's TikTok engagement drop after the algorithm change?",
     ["Exit surveys of brand partners identified three primary reasons for engagement decline: 45% cited the algorithm shift that deprioritized long-form content, 30% switched to Instagram Reels which offered better monetization, and 25% reported that the removal of duet features led creators to leave.",
      "Analytics showed that brands whose engagement dropped had 40% lower posting frequency in the 60 days before the algorithm update, suggesting early warning signs were present."],
     "Causal question with data-backed reasons about social media engagement decline",
     "Three causes stated with specific percentages from partner surveys"),

    ("t1_confident_hard_003", "social_media", "how",
     "How does Instagram's content recommendation algorithm work?",
     ["Instagram's recommendation algorithm uses a hybrid approach combining engagement signals and content-based analysis. First, it builds a user-interest graph from viewing, liking, and sharing history. Collaborative filtering identifies users with similar interaction patterns using cosine similarity. Content-based filtering analyzes post attributes (hashtags, visual features, caption text) using embedding vectors. The final rank combines both: 0.6 * engagement_score + 0.4 * content_score, with a recency boost of 1.3x for posts from the last 24 hours."],
     "Complex algorithm question with full methodology for social media recommendation",
     "Complete algorithm description with specific weights and ranking methods"),

    ("t1_confident_hard_007", "social_media", "what",
     "What is the total cost of running a large-scale influencer campaign?",
     ["Influencer Campaign Total Cost Breakdown (6-month projection): Talent fees: $280,000 (micro and macro influencers across 3 platforms). Content production: $95,000 (professional photo/video shoots). Platform ad spend: $150,000 ($25,000/month boosted posts). Management tools: $18,000 (scheduling, analytics, CRM). Legal/contracts: $12,000 (FTC compliance review). Total 6-month cost: $555,000, or approximately $92,500 per month."],
     "Complex financial question about influencer marketing with detailed breakdown",
     "Complete cost breakdown with all campaign components and total"),

    ("t1_confident_hard_008", "social_media", "is",
     "Is YouTube Shorts outperforming TikTok in creator monetization?",
     ["The YouTube Shorts Fund distributed $100 million to creators in 2024, averaging $200-$600 per eligible creator monthly. Revenue sharing from ads launched at 45% creator split. TikTok's Creator Fund pays approximately $0.02-$0.04 per 1,000 views, with top creators earning $2,000-$4,000 monthly. YouTube Shorts creators with similar view counts report 3x higher earnings due to the ad revenue model.",
      "However, TikTok's LIVE gifting generates $500-$2,000 per stream for mid-tier creators, a revenue stream YouTube Shorts lacks. Brand deals on TikTok average 20% higher rates due to its younger demographic."],
     "Monetization comparison with clear data favoring YouTube Shorts overall but TikTok in specific areas",
     "Clear data showing YouTube Shorts earns more from ads while TikTok leads in live gifting"),

    ("t1_confident_hard_009", "social_media", "how",
     "How should a brand respond to a viral negative review?",
     ["For your situation (500K+ view negative review, verified customer, product defect claim), a direct public response within 4 hours is the recommended approach. Social media crisis data shows: brands that respond publicly within 4 hours see 67% sentiment recovery vs 23% for delayed responses. Offering a replacement publicly converts 78% of detractors to promoters. Brands that delete or ignore viral complaints see 3x amplification of negative sentiment."],
     "Crisis management question with clear data-backed recommendation for social media",
     "Clear recommendation with specific comparative data on response timing"),

    ("t1_confident_hard_110", "social_media", "what",
     "What metrics indicate a podcast is ready for monetization?",
     ["A podcast is generally ready for monetization when it meets these documented thresholds: minimum 5,000 downloads per episode within the first 30 days, a listener retention rate above 60% through the full episode, at least 100 episodes published, and a consistent weekly release schedule maintained for 6+ months. Industry data from IAB shows podcasts meeting these criteria generate $18-$25 CPM from mid-roll ads, with annual revenue potential of $50,000-$150,000 depending on niche."],
     "Documented thresholds and metrics for podcast monetization readiness",
     "Specific documented thresholds backed by industry data from IAB"),

    # === history (5) ===
    ("t1_confident_hard_022", "history", "why",
     "Why did the Roman Empire decline in the 5th century?",
     ["Historical analysis identifies five key factors in Rome's decline: First, the empire's tax base shrank by 40% between 400-450 CE as provinces were lost to Germanic tribes. Second, military spending consumed 75% of remaining imperial revenue. Third, the population of Rome itself fell from 800,000 to 100,000 between 400-500 CE. Fourth, the division into Eastern and Western empires in 395 CE fragmented military coordination.",
      "Archaeological evidence confirms that trade routes contracted significantly, with pottery distribution patterns showing a 60% reduction in long-distance commerce by 450 CE."],
     "Causal question about Roman decline with multiple documented factors",
     "Five specific causes enumerated with quantified impacts"),

    ("t1_confident_hard_023", "history", "when",
     "When were the major milestones in the development of writing systems?",
     ["Writing system development timeline: Sumerian cuneiform emerged around 3400 BCE in Mesopotamia for record-keeping. Egyptian hieroglyphs appeared independently around 3200 BCE. The Phoenician alphabet, developed around 1050 BCE, introduced the first purely phonetic system with 22 consonant letters. The Greek alphabet adapted Phoenician script around 800 BCE, adding vowels for the first time. Chinese oracle bone script dates to approximately 1200 BCE during the Shang Dynasty."],
     "Timeline question with specific dates for writing system milestones",
     "Clear chronological sequence with specific dates for each major development"),

    ("t1_confident_hard_031", "history", "what",
     "What was the economic impact of the Black Death on medieval Europe?",
     ["The Black Death of 1347-1351 killed an estimated 30-60% of Europe's population, roughly 25 million people. Labor shortages caused wages to rise 40-100% within a decade. Land values fell by 30-40% as there were fewer tenants.",
      "The long-term effects included the decline of feudalism, as surviving peasants gained bargaining power. Per capita wealth approximately doubled by 1400 due to inheritance concentration."],
     "Economic impact question with quantified data about the Black Death",
     "Specific percentages documenting the Black Death's economic effects"),

    ("t1_confident_hard_032", "history", "who",
     "Who were the key figures in the Treaty of Westphalia negotiations?",
     ["The Treaty of Westphalia (1648) was negotiated by several principal figures: Count Maximilian von Trauttmansdorff represented the Holy Roman Emperor Ferdinand III. Cardinal Jules Mazarin directed French negotiations through his envoys. Swedish interests were represented by Johan Oxenstierna. Papal Nuncio Fabio Chigi attended but opposed the settlement. The negotiations involved 109 delegations meeting simultaneously in Osnabruck and Munster over four years."],
     "Documented key participants in the Westphalia negotiations with roles",
     "Specific named individuals with their roles and affiliations"),

    ("t1_confident_hard_033", "history", "how",
     "How did the Silk Road facilitate cultural exchange between East and West?",
     ["The Silk Road facilitated cultural exchange through three primary mechanisms: First, merchant caravans carried religious texts, with Buddhism spreading from India to China via the Kushan Empire between 100 BCE and 200 CE. Second, diplomatic exchanges like Zhang Qian's mission in 138 BCE established formal communication between Han China and Central Asian kingdoms. Third, technological transfer occurred naturally, with papermaking reaching Samarkand by 751 CE.",
      "Archaeological evidence from Dunhuang cave manuscripts confirms the mixing of Greek, Indian, Chinese, and Persian artistic styles along the route."],
     "Complex cultural exchange question with specific mechanisms and evidence",
     "Three documented mechanisms with dates and archaeological evidence"),

    # === psychology (4) ===
    ("t1_confident_hard_034", "psychology", "what",
     "What are the documented stages of grief according to the Kubler-Ross model?",
     ["The Kubler-Ross model identifies five stages of grief: Denial (initial shock, lasting days to weeks), Anger (frustration directed at self or others), Bargaining (hypothetical 'what if' thinking), Depression (deep sadness as reality settles), and Acceptance (coming to terms). Research by Maciejewski et al. (2007) in JAMA validated the sequence with 233 bereaved individuals, finding acceptance was most frequently endorsed at all time points, while disbelief peaked at 1 month and depression peaked at 6 months."],
     "Documented psychological model with research validation",
     "Five specific stages with research validation including sample size and timeline"),

    ("t1_confident_hard_035", "psychology", "how",
     "How does cognitive behavioral therapy treat anxiety disorders?",
     ["CBT for anxiety follows a structured protocol: Sessions 1-3 focus on psychoeducation about the anxiety cycle. Sessions 4-8 introduce cognitive restructuring using thought records. Sessions 9-12 implement graded exposure hierarchies. Sessions 13-16 focus on relapse prevention.",
      "Meta-analysis by Hofmann and Smits (2008) across 27 RCTs found CBT produces a large effect size (Hedges' g = 0.73) for anxiety disorders, with 60% of patients achieving remission by session 12."],
     "Structured protocol question with session breakdown and meta-analytic evidence",
     "Complete treatment protocol with session numbers and validated effect sizes"),

    ("t1_confident_hard_036", "psychology", "is",
     "Is the Stanford Prison Experiment considered valid by modern psychology?",
     ["The Stanford Prison Experiment (1971) is now widely criticized: Researcher demand characteristics — Zimbardo served as prison superintendent, directly influencing guard behavior. Sample bias — only 24 male Stanford students participated. Replication failure — Reicher and Haslam's 2006 BBC Prison Study found guards did NOT automatically become abusive. The APA's 2018 review noted it would not pass modern ethical standards.",
      "Recordings released in 2018 showed Zimbardo's research assistant explicitly coached guards to be tougher."],
     "Validity assessment with documented criticisms and evidence",
     "Multiple documented methodological flaws with specific sources"),

    ("t1_confident_medium_815", "psychology", "what",
     "What is the current scientific consensus on IQ heritability?",
     ["Twin studies consistently show IQ heritability increases with age: approximately 20% in infancy, 40% in childhood, and 60-80% in adulthood. The largest meta-analysis (Polderman et al., 2015) analyzing 14.5 million twin pairs found cognitive ability heritability at 0.54. The Flynn Effect demonstrates average IQ scores rose 3 points per decade throughout the 20th century.",
      "Both the APA (1996) and Plomin et al. (2016) agree that IQ reflects both genetic and environmental factors."],
     "Scientific consensus question with clear agreement across authoritative sources",
     "Multiple authoritative sources converge on heritability estimates"),

    # === government (4) ===
    ("t1_confident_hard_816", "government", "how",
     "How does the US Census affect congressional seat apportionment?",
     ["Congressional reapportionment follows a precise mathematical process: After each decennial census, the 435 House seats are redistributed using the method of equal proportions (Hill-Huntington method). Each state first receives its constitutionally guaranteed one seat. Remaining 385 seats are allocated by computing priority values. After the 2020 Census, Texas gained 2 seats, while California, Illinois, Michigan, New York, Ohio, Pennsylvania, and West Virginia each lost 1 seat."],
     "Precise mathematical process documented for congressional reapportionment",
     "Complete formula and 2020 Census results with specific state changes"),

    ("t1_confident_hard_818", "government", "what",
     "What is the breakdown of the federal budget for fiscal year 2024?",
     ["Federal Budget FY2024 Breakdown: Mandatory spending: $3.9 trillion (62%), including Social Security ($1.4T), Medicare ($1.0T), Medicaid ($616B). Discretionary spending: $1.7 trillion (27%), with defense at $886B and non-defense at $814B. Net interest: $659 billion (11%). Total budget: $6.3 trillion. Revenue: $4.9 trillion, creating a deficit of approximately $1.4 trillion."],
     "Detailed federal budget breakdown with complete spending categories",
     "Complete budget breakdown with all major categories and totals"),

    ("t1_confident_hard_820", "government", "why",
     "Why do voter turnout rates differ between midterm and presidential elections?",
     ["Political science research identifies four factors: media coverage of presidential races is 3-5x greater. Presidential candidates invest $2-3 billion in voter mobilization vs $500M-$800M in midterms. Down-ballot races lack the simplicity of a single national choice. Younger voters (18-29) show the largest gap: 50% turnout in presidential years vs 20% in midterms.",
      "Presidential elections average 55-60% turnout vs 35-40% for midterms since 1974."],
     "Data-backed causal question about voting behavior differences",
     "Four documented factors with specific data"),

    ("t1_confident_medium_821", "government", "which",
     "Which government agencies oversee food safety in the United States?",
     ["The FDA regulates approximately 80% of the food supply including produce, seafood, and dairy. The USDA's FSIS oversees meat, poultry, and processed egg products. The EPA sets pesticide residue limits. The CDC tracks foodborne illness outbreaks. State and local health departments conduct restaurant inspections. The GAO has noted the fragmented system involves 15 agencies administering at least 30 food-related laws."],
     "Documented multi-agency oversight structure with clear jurisdictional boundaries",
     "Specific agencies named with their jurisdictions"),

    # === agriculture (4) ===
    ("t1_confident_hard_111", "agriculture", "what",
     "What are the optimal soil conditions for growing winter wheat?",
     ["Winter wheat thrives in well-drained loam soils: pH 6.0-7.0, organic matter above 2%, phosphorus 25-50 ppm, potassium 150-200 ppm. Planting depth of 1-1.5 inches with row spacing of 6-8 inches. Soil temperature at planting should be 50-65 degrees F, typically 4-6 weeks before the first hard freeze. Nitrogen requirements are 1.2-1.5 lbs per bushel of expected yield."],
     "Documented soil and planting parameters for winter wheat",
     "Specific numerical thresholds from USDA guidelines"),

    ("t1_confident_hard_112", "agriculture", "how",
     "How does precision agriculture use GPS technology to optimize crop yields?",
     ["Precision agriculture employs GPS through three stages: First, GPS-equipped soil samplers create field maps at 2.5-acre grid resolution. Second, variable-rate application adjusts fertilizer in real-time, reducing costs by 15-25%. Third, GPS-guided harvesting logs yield data per square meter for next-season planning.",
      "Purdue University trials demonstrated GPS-guided nitrogen application increased corn yields by 8-12 bushels per acre while reducing total nitrogen use by 20%."],
     "Technology application question with three stages and trial data",
     "Three-stage process with cost savings and yield data"),

    ("t1_confident_hard_113", "agriculture", "is",
     "Is no-till farming more profitable than conventional tillage?",
     ["USDA data shows no-till reduces fuel costs by $15-$25 per acre and equipment wear by $8-$12 per acre. Labor savings average 30-50%. Herbicide costs increase $10-$15 per acre. Net profitability advantage is $5-$20 per acre after a 3-5 year transition.",
      "Kansas State University's 20-year study found no-till yields matched conventional after year 5, while soil organic matter increased 12% and water infiltration improved 25%."],
     "Profitability comparison with detailed cost-benefit data",
     "Clear cost breakdown showing no-till advantage with per-acre economics"),

    ("t1_confident_hard_114", "agriculture", "when",
     "When should farmers apply pre-emergent herbicides for corn?",
     ["Application should occur after planting but before emergence, typically within 0-3 days. Soil temperature must be below 77 degrees F at 2-inch depth. Rainfall of 0.5-1.0 inches within 7-10 days is needed for activation. University of Illinois research shows applications more than 5 days after planting lose 15-30% efficacy."],
     "Timing question with specific research-based application windows",
     "Precise timing window with temperature and moisture data"),

    # === hr_workplace (4) ===
    ("t1_confident_hard_115", "hr_workplace", "what",
     "What are the documented benefits of structured interviews over unstructured ones?",
     ["Meta-analysis by Schmidt and Hunter (1998) established structured interviews have predictive validity of 0.51 vs 0.38 for unstructured. A Google People Analytics study found structured interviews reduced bias by 40% and improved diverse candidate selection by 25%. EEOC data shows unstructured interviews are 3x more likely to result in discrimination claims."],
     "Documented comparison with meta-analytic evidence",
     "Specific validity coefficients from multiple data sources"),

    ("t1_confident_hard_116", "hr_workplace", "how",
     "How does the 360-degree feedback process work in practice?",
     ["Phase 1 (2 weeks): select 8-12 raters including direct reports, peers, and supervisors. Phase 2 (2-3 weeks): raters complete standardized questionnaires on 40-60 behavioral items. Phase 3 (1 week): HR aggregates responses ensuring anonymity with minimum 3 raters per category. Phase 4: individual receives report comparing self-ratings to others. Phase 5: facilitated debrief creates action plan.",
      "Atwater and Brett (2005) found 33% improved significantly, 55% moderately improved, 12% showed no change."],
     "Structured process with complete phased implementation",
     "Five-phase process with timelines and research outcomes"),

    ("t1_confident_hard_117", "hr_workplace", "should",
     "Should companies implement a four-day work week?",
     ["The UK 4-Day Week Pilot (2022) with 61 companies found: revenue increased 1.4%, sick days fell 65%, resignations dropped 57%, and 92% chose to continue permanently. Microsoft Japan's 2019 trial saw productivity increase 40%. However, Unilever New Zealand found 15% of clients reported slower response times in customer-facing roles."],
     "Decision question with clear recommendation backed by multiple trials",
     "Clear evidence from UK pilot and Microsoft Japan with specific metrics"),

    ("t1_confident_hard_118", "hr_workplace", "what",
     "What is the average cost-per-hire breakdown for a software engineer?",
     ["SHRM 2024 data: Job boards $2,400. Recruiter time (40 hours at $45/hr): $1,800. Technical assessment tools: $500. Interview panel (6 people x 2 hours x $75/hr): $900. Background check: $200. Onboarding (first 90 days): $8,500. Total: $14,300. Agency recruitment adds $25,000-$35,000 (20-25% of first-year salary). Average time-to-fill: 44 days."],
     "Detailed cost breakdown with industry benchmarking data",
     "Complete cost-per-hire with SHRM benchmarking data"),

    # === sports (4) ===
    ("t1_confident_hard_119", "sports", "what",
     "What factors determine MLB draft pick value according to analytics?",
     ["College players have a 65% rate of reaching the majors vs 45% for high school players. WAR correlates with draft position: picks 1-10 average 15.2 career WAR vs 5.8 for picks 11-30. Pitcher injury risk means college position players provide the highest expected value. Signing bonus slot values: #1 overall receives $9.4 million vs $2.3 million for pick #30 under the current CBA."],
     "Data-driven MLB draft value analysis with WAR and success metrics",
     "Four factors with quantified data from FanGraphs"),

    ("t1_confident_hard_120", "sports", "how",
     "How does altitude affect marathon performance?",
     ["At 5,000 feet, VO2 max decreases approximately 5%, adding 3-5 minutes to marathon times. At 7,000 feet, the decrease is 8-10%, adding 7-12 minutes. The Denver Marathon has average finishing times 6.8% slower than sea-level races. Optimal altitude training follows 'live high, train low': living at 7,000-8,000 feet while training at 4,000 feet for 3-4 weeks increases red blood cell production by 5-8%.",
      "The 1968 Mexico City Olympics (7,349 ft) demonstrated these effects: distance events were 3-8% slower while sprint times were unaffected."],
     "Physiological impact question with altitude-performance data",
     "Specific altitude thresholds with percentage impacts"),

    ("t1_confident_hard_121", "sports", "is",
     "Is the home-field advantage in the NFL statistically significant?",
     ["Home teams won 57.1% of regular-season games from 1966-2019. This dropped to 51.3% during 2020 COVID season with limited fans, then rebounded to 54.8% in 2021 with full stadiums. Average home point margin is +2.5 points. Seattle's Lumen Field averaged 64% home win rate from 2002-2023 with crowd noise exceeding 130 decibels."],
     "Statistical significance question with historical data and natural experiment",
     "Win percentages across eras with COVID natural experiment confirming fan impact"),

    ("t1_confident_hard_122", "sports", "when",
     "When should a basketball team start intentional fouling when trailing?",
     ["Teams trailing by 6+ points should begin fouling with 30-40 seconds remaining. For 3-point deficits, fouling at 24-30 seconds is optimal. Each possession takes approximately 6 seconds when fouling vs 14 seconds normally. Ken Pomeroy's analysis of 10,000+ end-game scenarios shows teams trailing by 7+ with under 60 seconds have 2.1% win probability with normal play vs 5.3% when fouling."],
     "Decision timing question with specific thresholds from analytics",
     "Precise timing thresholds with win probability data"),

    # === food (3) ===
    ("t1_confident_hard_123", "food", "what",
     "What is the nutritional difference between grass-fed and grain-fed beef?",
     ["USDA data per 100g ribeye: Grass-fed has 198 calories vs 271 for grain-fed. Omega-3 fatty acids: 80mg vs 20mg. Total fat: 10.2g vs 18.5g. Similar protein (~26g). Vitamin E is 3x higher in grass-fed.",
      "The American Journal of Clinical Nutrition (2019) noted that while grass-fed has a superior fatty acid profile, the absolute omega-3 differences are minor compared to eating fish 2x weekly."],
     "Nutritional comparison with specific per-100g data",
     "Specific nutrient values from USDA database"),

    ("t1_confident_hard_124", "food", "how",
     "How does fermentation preserve food and enhance nutrition?",
     ["Three preservation mechanisms: lactic acid bacteria drop pH to 3.5-4.5 inhibiting pathogens. Beneficial bacteria competitively exclude harmful organisms. Fermentation byproducts (bacteriocins, hydrogen peroxide) directly kill pathogens.",
      "Nutritional enhancement: B-vitamin content increases 20-100%, phytic acid breaks down 50-70% improving mineral absorption, and bioactive peptides are generated. Fermented dairy has 4x higher folate than unfermented equivalents."],
     "Comprehensive mechanism question with preservation and nutrition enhancement",
     "Three preservation mechanisms and three nutritional benefits with quantified improvements"),

    ("t1_confident_hard_125", "food", "is",
     "Is the Mediterranean diet evidence-based for heart health?",
     ["The PREDIMED trial (7,447 participants, NEJM 2013) found a 30% reduction in major cardiovascular events. A 2023 meta-analysis of 29 studies (1.5 million participants) confirmed 25% lower cardiovascular mortality. The American Heart Association gives it the highest evidence grade (Class I, Level A). Key components: olive oil 4+ tablespoons/day, nuts 30g/day, fish 3+ servings/week."],
     "Evidence-based assessment with RCT data and meta-analytic confirmation",
     "PREDIMED trial data plus meta-analysis with AHA recommendation grade"),

    # === transportation (4) ===
    ("t1_confident_hard_126", "transportation", "what",
     "What are the safety statistics for autonomous vehicles compared to human drivers?",
     ["NHTSA 2024 data: human drivers average one crash per 484,000 miles. Waymo reported one contact event per 3.8 million miles. Tesla Autopilot data shows one crash per 7.6 million miles with Autopilot engaged (primarily highway driving).",
      "IIHS notes autonomous vehicles eliminate the 94% of crashes caused by human error but introduce new failure modes: sensor degradation in weather (17% of AV incidents), software edge cases (23%), and construction zones (31% of disengagements)."],
     "Comparative safety data with per-mile incident rates",
     "Specific per-mile rates from multiple companies with failure mode context"),

    ("t1_confident_hard_127", "transportation", "how",
     "How does fleet electrification affect total maintenance costs?",
     ["NREL study of 400+ fleet vehicles: EVs average $0.06/mile in maintenance vs $0.10/mile for diesel — a 40% reduction. Brake wear decreases 80% due to regenerative braking. No oil changes or transmission fluid needed. Tire replacement increases 10-15% due to higher weight. Battery degradation averages 2.3% capacity loss per year.",
      "Amazon's delivery fleet (10,000+ Rivian vans) showed 43% actual maintenance savings in the first 18 months."],
     "Total cost comparison with per-mile maintenance data",
     "Specific per-mile costs with 40% reduction from NREL and Amazon data"),

    ("t1_confident_hard_128", "transportation", "should",
     "Should a logistics company invest in hydrogen fuel cell trucks for long-haul routes?",
     ["For 500+ mile routes: Nikola Tre FCEV achieves 500-mile range with 20-minute refueling vs battery trucks requiring 4+ hours. TCO analysis projects hydrogen parity with diesel by 2028 at $5/kg hydrogen (currently $8-12/kg). Only 54 public hydrogen stations exist in the US. California's ARCHES hub plans $4/kg by 2030.",
      "For routes under 300 miles with overnight depot charging, battery electric trucks offer lower TCO today at $0.12/kWh vs hydrogen equivalent of $0.35/kWh."],
     "Investment decision with conditional recommendation and TCO data",
     "Clear recommendation for long-haul hydrogen, short-haul BEV, with cost data"),

    ("t1_confident_hard_129", "transportation", "when",
     "When should airlines schedule heavy maintenance checks for Boeing 737 aircraft?",
     ["Boeing 737 maintenance levels: A-Check every 500-800 flight hours (50-70 man-hours). B-Check every 6-8 months (180 man-hours). C-Check every 20-24 months or 6,000 flight hours (6,000 man-hours, aircraft out of service). D-Check every 8-12 years or 48,000-72,000 flight hours (50,000 man-hours, complete structural inspection). Airlines in harsh environments reduce intervals by 10-15%."],
     "Scheduled maintenance timing with specific interval requirements",
     "Four check levels with exact intervals and man-hours"),

    # Remaining to fill quota
    ("t1_confident_hard_130", "social_media", "which",
     "Which social media platform has the highest ROI for B2B marketing?",
     ["LinkedIn dominates B2B: 84% of B2B marketers rate it most effective. LinkedIn Ads average $5.26 cost-per-lead for B2B vs $8.40 on Facebook and $12.50 on Google Ads. Conversion rates from InMail average 10-25% vs 1-3% for cold email.",
      "For technical audiences, Reddit and Stack Overflow show $3.50-$6.00 CPLs with higher intent signals."],
     "Platform comparison with ROI data from multiple benchmarking sources",
     "Specific CPL data across platforms with clear LinkedIn advantage"),

    ("t1_confident_hard_131", "history", "what",
     "What were the terms of the Treaty of Versailles?",
     ["The Treaty of Versailles (1919) imposed: Alsace-Lorraine to France, Eupen-Malmedy to Belgium, Polish Corridor created. Military limited to 100,000 troops, tanks/aircraft/submarines prohibited. Article 231 assigned sole war guilt. Reparations set at 132 billion gold marks ($33 billion). Overseas colonies redistributed as League of Nations mandates."],
     "Comprehensive treaty terms with specific provisions",
     "Specific territorial, military, guilt, and financial terms"),
]


TRUSTWORTHY_HEDGED_CONVERSIONS = [
    # === social_media (5) ===
    ("t1_qualify_hard_005", "social_media", "why",
     "Why do posts with emojis get higher engagement on Instagram?",
     ["Data shows posts with emojis receive 47.7% more interactions across 500,000 analyzed posts.",
      "Both emoji-heavy posts and high engagement correlate with posting during peak hours (11am-1pm), suggesting timing may be confounding.",
      "Accounts with larger followings (100K+) show the strongest correlation but also post more frequently."],
     "Classic confounding variable — emoji use may correlate with habits not cause engagement",
     "Emoji use may be a proxy for post effort or timing"),

    ("t1_qualify_hard_012", "social_media", "does",
     "Does going viral lead to sustained follower growth?",
     ["Analysis of 2,000 viral TikTok videos (1M+ views) found creators gained 15,000 followers within 48 hours.",
      "60-day follow-up showed 70% of new followers became inactive within 30 days.",
      "Creators who posted daily after going viral retained 3x more followers, but the sample was small (n=43)."],
     "Partial evidence with limited sample size for key finding",
     "Viral growth data is clear but retention data has quality issues"),

    ("t1_qualify_hard_019", "social_media", "is",
     "Is TikTok more addictive than other social media platforms?",
     ["TikTok users average 95 minutes daily vs 51 for Instagram and 33 for Twitter.",
      "Self-reported addiction scores were 22% higher for TikTok users, but the study only surveyed 18-24 year olds.",
      "Neuroimaging showed TikTok's reward schedule activates dopamine pathways like slot machines, but with only 30 participants."],
     "Multiple indicators but methodological limitations in each study",
     "Usage data is descriptive; addiction scale limited to young adults; neuroimaging underpowered"),

    ("t1_qualify_hard_021", "social_media", "how",
     "How effective are Instagram collaborations for small business growth?",
     ["Survey of 500 small businesses showed collaboration posts averaged 3.2x higher reach.",
      "Revenue attribution is uncertain: 45% reported sales increases but only 20% could directly attribute sales to the collaboration.",
      "Most successful were between complementary businesses, though 'complementary' varied across respondents."],
     "Evidence quality issue — self-reported data with unclear attribution",
     "Reach data is clear but revenue attribution is self-reported"),

    ("t1_qualify_hard_022", "social_media", "should",
     "Should content creators diversify across multiple platforms?",
     ["Multi-platform creators earn 2.4x more than single-platform creators on average.",
      "Creators on 4+ platforms showed 35% declining engagement compared to 2-platform creators.",
      "23% of TikTok-only creators lost 50%+ reach during the 2024 algorithm update, while multi-platform creators maintained overall audience."],
     "Mixed evidence — diversification helps income but hurts engagement beyond 2-3 platforms",
     "Income benefits but diminishing returns on engagement"),

    # === history (4) ===
    ("t1_qualify_hard_310", "history", "when",
     "When did agriculture first develop independently?",
     ["Archaeological evidence: Fertile Crescent crop cultivation around 9500 BCE. Yangtze River Valley rice paddies around 8000 BCE, though some scholars argue 10,000 BCE.",
      "Mesoamerican maize domestication dated to approximately 7000 BCE based on cob morphology, but genetic analysis suggests possibly 9000 BCE."],
     "Different dating methods yield different timelines",
     "Radiocarbon and genetic dating disagree on exact timelines"),

    ("t1_qualify_hard_312", "history", "what",
     "What was the population of pre-Columbian Americas?",
     ["Conservative estimates (Kroeber, 1934) suggested 8-15 million. Henry Dobyns (1966) argued 90-112 million.",
      "Recent DNA and ecological studies suggest 50-60 million is most likely, but the debate hinges on estimated disease mortality rates of 50-95%, which are poorly documented."],
     "Wide scholarly disagreement — estimates vary by 10x",
     "Estimates range from 8 to 112 million with poor evidence quality"),

    ("t1_qualify_hard_313", "history", "who",
     "Who built the Great Zimbabwe ruins?",
     ["Archaeological consensus attributes Great Zimbabwe to the Shona-speaking peoples, roughly 1100-1450 CE.",
      "The exact political entity is debated: Kingdom of Zimbabwe, Karanga state, or multi-ethnic trading center.",
      "Colonial-era non-African attribution has been thoroughly debunked by stratigraphy and pottery analysis."],
     "General attribution clear but specific political identity debated",
     "Shona attribution solid but exact political structure uncertain"),

    ("t1_qualify_hard_316", "history", "why",
     "Why did the Maya civilization decline?",
     ["Paleoclimate data shows severe droughts between 800-1000 CE correlating with city abandonment.",
      "Some major cities were abandoned before drought periods, and northern Yucatan cities persisted through droughts that devastated southern sites.",
      "LiDAR surveys reveal agricultural intensification suggesting deforestation may have amplified drought, but evidence is preliminary."],
     "Multiple contributing factors with uncertain causal ordering",
     "Drought correlation strong but doesn't explain all cases"),

    # === psychology (3) ===
    ("t1_qualify_hard_317", "psychology", "does",
     "Does playing violent video games increase aggression?",
     ["Meta-analysis of 24 studies found small but significant effect (r = 0.24) linking violent game exposure to aggressive behavior.",
      "Przybylski and Weinstein (2019) with 1,004 teens found no significant relationship using pre-registered methods.",
      "The APA (2020) concluded evidence is 'insufficient' to link games to criminal violence. Lab vs real-world measures diverge."],
     "Laboratory vs real-world measures diverge; effect sizes small and contested",
     "Small lab effects exist but real-world behavioral evidence insufficient"),

    ("t1_qualify_hard_318", "psychology", "how",
     "How reliable is eyewitness testimony?",
     ["Innocence Project reports eyewitness misidentification contributed to 69% of wrongful convictions overturned by DNA.",
      "Memory research showed 25-30% of subjects incorporate suggested false details into recollections.",
      "Initial confidence at identification correlates moderately with accuracy (r = 0.40-0.60) per Wixted et al. (2015), but confidence shifts after investigator feedback."],
     "Moderate initial reliability but highly susceptible to contamination",
     "Initial identification has moderate validity but post-event contamination reduces reliability"),

    ("t1_qualify_hard_023", "psychology", "is",
     "Is mindfulness meditation effective for chronic pain management?",
     ["Cochrane review of 38 RCTs found MBSR produces small to moderate pain reduction (SMD = -0.32).",
      "Placebo-controlled studies (sham meditation) showed only 12% improvement vs 23% in MBSR, suggesting expectation effects account for roughly half the benefit.",
      "Only 4 of 38 studies followed patients beyond 6 months, and effects diminished without continued practice."],
     "Moderate short-term benefit but placebo-controlled effects smaller; long-term evidence weak",
     "Expectation effects account for ~50% and long-term data insufficient"),

    # === government (4) ===
    ("t1_qualify_hard_024", "government", "does",
     "Does increasing police funding reduce crime rates?",
     ["Study of 242 US cities found 10% budget increases correlated with 3-5% decrease in violent crime.",
      "Same dataset showed no effect on property crime, and correlation disappeared when controlling for economic conditions.",
      "Camden, NJ saw crime drop 25% after disbanding and reorganizing police; some cities that defunded police saw temporary increases."],
     "Correlational evidence mixed; confounders make causal claims unreliable",
     "Correlation exists but disappears with economic controls"),

    ("t1_qualify_hard_025", "government", "how",
     "How effective are school voucher programs at improving student outcomes?",
     ["Milwaukee Parental Choice Program: voucher students performed similarly to public school peers after 5 years.",
      "Indiana's evaluation found voucher students initially scored lower, though scores converged by year 4.",
      "Louisiana showed 0.4 standard deviations loss in math in year 1 with partial recovery by year 3. Quality variation across schools was extreme."],
     "Inconsistent results across programs",
     "No consistent positive effect; outcomes vary by program design"),

    ("t1_qualify_hard_034", "government", "should",
     "Should municipalities implement congestion pricing?",
     ["Stockholm's 2006 trial reduced city center traffic 22% and improved air quality 12%.",
      "Public support was only 36% pre-implementation; $200M infrastructure cost with $80M annual revenue making break-even 2.5 years.",
      "NYC's 2024 implementation faced equity criticism that the $15 toll disproportionately affected outer-borough residents."],
     "Effective at reducing traffic but equity concerns vary by context",
     "Benefits documented but equity depends on local transit infrastructure"),

    ("t1_qualify_hard_042", "government", "what",
     "What impact does universal pre-K have on long-term educational outcomes?",
     ["Perry Preschool Study (123 participants): participants earned 20% more as adults, 44% less likely arrested.",
      "Tennessee Pre-K Study (2,990 students, 2019): initial gains faded by third grade; pre-K participants scored slightly lower by sixth grade.",
      "Perry had 1:6 teacher-student ratio while Tennessee reflected typical public school resources."],
     "Mixed evidence — landmark studies disagree due to quality differences",
     "High-quality programs show effects but typical programs show fadeout"),

    # === agriculture (3) ===
    ("t1_qualify_hard_043", "agriculture", "does",
     "Does organic farming produce lower crop yields than conventional farming?",
     ["Meta-analysis (Seufert 2012, Nature): organic yields 25% lower overall but only 5% lower for fruit, 13% for legumes, 34% for cereals.",
      "Rodale Institute 30-year study: organic yields matched conventional after year 5, organic outperformed by 31% in drought years.",
      "Results come from research farms; commercial organic operations may face larger yield gaps."],
     "Yield gap varies hugely by crop type, management quality, and weather",
     "Meta-analysis shows 25% gap but convergence in long-term studies"),

    ("t1_qualify_hard_120", "agriculture", "how",
     "How does cover cropping affect subsequent cash crop yields?",
     ["SARE database: cover crops increase corn yields 3-5% and soybean 2-4%.",
      "Upper Midwest: late cover crop termination can reduce yields 5-10%. Southeast: consistent improvement due to erosion prevention.",
      "Cover crop costs $30-$50/acre; yield benefit translates to $15-$35/acre, making net return marginal before soil health benefits."],
     "Variable results by region; economic case uncertain",
     "Average benefit positive but regional variation extreme"),

    ("t1_qualify_hard_127", "agriculture", "is",
     "Is vertical farming economically viable for staple crops?",
     ["Leafy greens production costs: $2.50-$4.00 per head vs $1.50-$2.50 field-grown.",
      "Staple crops (wheat, rice, corn) would cost $25/kg in vertical farms vs $0.25/kg in fields — 5-20x more expensive.",
      "If electricity reaches $0.02/kWh (vs current $0.12/kWh), viability improves, but no region consistently achieves that price."],
     "Viable for high-value crops but prohibitive for staples under current energy prices",
     "Lettuce works but staples are 5-20x too expensive"),

    # === hr_workplace (3) ===
    ("t1_qualify_hard_128", "hr_workplace", "does",
     "Does unlimited PTO result in employees taking more time off?",
     ["Namely's data from 1,000+ companies: unlimited PTO employees took 13 days vs 15 days for fixed allotment.",
      "Managers took 17 days with unlimited PTO (more than fixed) while junior employees took only 10 days.",
      "Companies requiring minimum 15 days alongside unlimited saw usage normalize to 18 days, but only from 12 companies."],
     "Counter-intuitive — unlimited PTO often reduces time off for junior staff",
     "Less usage overall; seniority gap notable; minimum-PTO fix has limited data"),

    ("t1_qualify_hard_129", "hr_workplace", "how",
     "How effective are employee wellness programs at reducing healthcare costs?",
     ["RAND Study (600,000+ employees): wellness programs generated only $3.80 savings per member per month, below typical $5-10 cost.",
      "Single-company study found 25% cost reduction over 3 years but with high baseline health risks.",
      "Illinois Workplace Wellness Study (first large RCT): no significant effect on spending, behaviors, or productivity after 2 years."],
     "First RCT shows no effect; observational studies likely biased by self-selection",
     "Rigorous evidence shows minimal savings; positive studies have limitations"),

    ("t1_qualify_hard_130", "hr_workplace", "is",
     "Is salary transparency beneficial for reducing pay gaps?",
     ["Denmark's transparency legislation reduced gender pay gap by 7% over 5 years, primarily by slowing male wage growth.",
      "65% of employees discovering they earned below median reported decreased satisfaction (Card et al. 2012).",
      "When differences are linked to performance metrics, transparency increases motivation; when arbitrary, it increases turnover by 15%."],
     "Reduces gaps but can harm morale; depends on pre-existing equity",
     "Gap reduction documented but mechanism is suppressing high earners"),

    # === sports (2) ===
    ("t1_qualify_hard_131", "sports", "does",
     "Does sports specialization in youth improve professional prospects?",
     ["Survey of 1,000 elite athletes: specialized before 12 reached elite levels 2 years earlier.",
      "NCAA study: 88% of Division I athletes played multiple sports. Pro athletes were 2x more likely multi-sport in high school.",
      "Early specializers have 1.5x higher overuse injury rates, and 70% who specialize before 14 quit by age 18 due to burnout."],
     "Faster development but higher injury/dropout; pros trend multi-sport",
     "Earlier specialization speeds development but increases injury and burnout"),

    ("t1_qualify_hard_132", "sports", "how",
     "How accurate are pre-draft scouting evaluations in the NBA?",
     ["Top-5 picks average 8.2 Win Shares/year vs 3.1 for picks 6-14 and 1.4 for 15-30.",
      "22% of top-10 picks fail to complete rookie contracts. 15% of second-round picks outperform by 5+ Win Shares.",
      "Combine physical measurements explain only 12% of career variance. College metrics explain 25-30%, leaving 70% unexplained."],
     "Moderate predictive validity but substantial bust rates",
     "Draft position has moderate correlation but 70%+ variance unexplained"),

    # === food (2) ===
    ("t1_qualify_hard_133", "food", "is",
     "Is intermittent fasting more effective than caloric restriction for weight loss?",
     ["NEJM review of 27 trials: IF and CR produced equivalent 5-7% weight loss over 12 months.",
      "IF showed slightly better insulin sensitivity (HOMA-IR reduced 20% vs 15% CR) but not statistically significant.",
      "Adherence: 82% IF at 6 months vs 75% CR; by 12 months both declined similarly."],
     "Equivalent outcomes; minor metabolic differences not significant",
     "No meaningful weight loss difference"),

    ("t1_qualify_hard_134", "food", "does",
     "Does cooking method affect the nutritional value of vegetables?",
     ["Boiling leaches 25-50% of water-soluble vitamins; steaming retains 80-90%.",
      "Cooking increases bioavailability: lycopene 2.5x more absorbable cooked, beta-carotene absorption from carrots increases 6x with fat.",
      "Net impact is context-dependent: vitamin C best raw, but cooked carrots/spinach/tomatoes have higher antioxidant capacity."],
     "Complex tradeoff — destroys some nutrients while enhancing others",
     "Leaching of water-soluble vitamins clear but fat-soluble bioavailability increases"),

    # === transportation (2) ===
    ("t1_qualify_hard_135", "transportation", "should",
     "Should cities invest in light rail over bus rapid transit?",
     ["Light rail costs $100-250M/mile vs $5-30M for BRT. Light rail attracts 30-50% more riders.",
      "BRT can be implemented in 2-3 years vs 7-10 for light rail, and routes are modifiable.",
      "40% of US BRT systems lose dedicated lanes within 10 years (BRT creep), while light rail infrastructure is permanent."],
     "Light rail attracts more riders but costs 5-50x more; BRT is flexible but vulnerable",
     "Cost-benefit depends on corridor density and timeline"),

    ("t1_qualify_hard_136", "transportation", "how",
     "How effective are speed cameras at reducing traffic fatalities?",
     ["Cochrane review of 35 studies: speed cameras reduce fatal crashes 11-44% within zones.",
      "Most studies use before-after designs without control groups; regression to mean may account for 10-30% of reduction.",
      "Average speeds in camera zones dropped 1-15%, but increased speeds between cameras may shift crash locations."],
     "Likely effective within zones but study quality poor and behavioral displacement may occur",
     "Large range in estimated effect; regression to mean and kangaroo effect may inflate benefits"),
]


ABSTENTION_CONVERSIONS = [
    # === social_media (4) ===
    ("t1_abstain_hard_100", "social_media", "how",
     "How does TikTok's content moderation algorithm detect misinformation?",
     ["TikTok reported removing 113 million videos in Q1 2024 for community guideline violations. The platform employs over 40,000 human moderators across multiple languages.",
      "TikTok's transparency report shows 89% of removed content was identified before any user reports."],
     "Enforcement statistics instead of detection mechanism",
     "Removal stats and moderator counts cannot answer how the algorithm works technically"),

    ("t1_abstain_hard_101", "social_media", "what",
     "What is the demographic breakdown of Reddit's user base in 2025?",
     ["Reddit reported 52 million daily active users in 2023 and saw significant growth after its 2024 IPO.",
      "Popular subreddits like r/AskReddit have over 40 million subscribers. Revenue per user has grown to approximately $3.50 quarterly."],
     "Asks for 2025 demographics but context only has 2023-2024 metrics",
     "Revenue and subscriber data from earlier years cannot answer 2025 demographics"),

    ("t1_abstain_hard_103", "social_media", "who",
     "Who are the top-earning content creators on YouTube in 2025?",
     ["YouTube paid out over $30 billion to creators since inception. Platform ad revenue reached $8.6 billion in Q3 2024.",
      "YouTube Shorts accounts for 70 billion daily views. YouTube Premium subscribers reached 100 million globally."],
     "Aggregate platform revenue and feature data but no individual creator earnings for 2025",
     "Platform-wide stats cannot identify specific top earners"),

    ("t1_abstain_hard_225", "social_media", "when",
     "When will Twitter/X reach profitability under its current business model?",
     ["Twitter/X's workforce was reduced from 7,500 to approximately 1,500. Advertising revenue declined 50% in 2023.",
      "X Premium generated an estimated $120 million annually by mid-2024. Server costs were reduced through AWS to on-premises migration."],
     "Past cost-cutting and revenue changes cannot predict future profitability timeline",
     "Historical data cannot predict when profitability will be achieved"),

    # === history (3) ===
    ("t1_abstain_hard_227", "history", "what",
     "What was the population of ancient Troy during the Trojan War?",
     ["Homer's Iliad describes Troy as a great walled city defended by 50,000 warriors. Archaeological excavations at Hisarlik identified nine settlement layers.",
      "The layer associated with the Trojan War (Troy VIIa, c. 1180 BCE) shows destruction by fire. City walls enclosed approximately 200,000 square meters."],
     "Literary sources are mythological; enclosed area alone cannot determine population",
     "Homer's figures are literary not historical; area cannot determine population"),

    ("t1_abstain_hard_228", "history", "how",
     "How were the Egyptian pyramids at Giza constructed?",
     ["The Great Pyramid consists of 2.3 million limestone blocks averaging 2.5 tons each. Construction took approximately 20 years under Pharaoh Khufu.",
      "A workers' village housed 20,000-30,000 laborers. The base is level to within 2.1 centimeters across 230 meters."],
     "Describes finished structure's properties but not construction methods",
     "Block counts and precision describe WHAT was built, not HOW"),

    ("t1_abstain_hard_229", "history", "why",
     "Why did the Indus Valley Civilization collapse around 1900 BCE?",
     ["The civilization encompassed over 1,500 settlements. Mohenjo-daro had 40,000-80,000 people.",
      "Featured advanced urban planning with grid streets and standardized weights. After 1900 BCE, cities were gradually abandoned."],
     "Describes the civilization at its peak and abandonment pattern but not causes",
     "Achievements and abandonment pattern cannot explain WHY it collapsed"),

    # === psychology (2) ===
    ("t1_abstain_hard_135", "psychology", "what",
     "What specific brain regions are activated during deja vu experiences?",
     ["Deja vu is reported by 60-70% of the population, most commonly ages 15-25.",
      "Temporal lobe epilepsy patients report deja vu more frequently, suggesting a temporal lobe connection.",
      "Psychological theories propose deja vu results from familiarity-recollection mismatch in dual-process memory."],
     "Prevalence and theories but no specific brain region activation data",
     "Prevalence data and theories cannot identify brain activation patterns"),

    ("t1_abstain_hard_136", "psychology", "how",
     "How does lucid dreaming training work at the neurological level?",
     ["Lucid dreaming occurs in 55% of people at least once. Induction techniques include reality testing, MILD, and WBTB.",
      "Lucid dreamers have higher metacognitive awareness. Prefrontal cortex shows increased activity during lucid REM sleep.",
      "Training programs achieve 17-46% success rates within 1-2 weeks."],
     "Behavioral techniques and one brain region finding but not neurological mechanism of training",
     "Technique descriptions and one correlation cannot explain the learning mechanism"),

    # === government (3) ===
    ("t1_abstain_hard_016", "government", "what",
     "What were the specific policy recommendations in the 2024 CBO climate report?",
     ["The CBO publishes annual budget outlooks since 1975. The 2023 report projected $1.4 trillion deficits.",
      "CBO analyses cover healthcare, defense, Social Security, and environmental spending.",
      "The 2022 climate report estimated climate change could reduce US GDP by 1-3% by 2050."],
     "Asks about 2024 climate report but context has 2022-2023 data only",
     "Earlier CBO reports cannot provide 2024 specific recommendations"),

    ("t1_abstain_hard_023", "government", "how",
     "How much federal funding did the CHIPS Act allocate to each recipient company?",
     ["The CHIPS Act authorized $52.7 billion for semiconductor manufacturing. Commerce Department administers the funding.",
      "Preliminary applications exceeded $150 billion against $39 billion available.",
      "Samsung, TSMC, and Intel announced new US fabrication facilities with combined investments exceeding $200 billion."],
     "Total authorization and company plans but no per-company allocation breakdown",
     "Total funding and announcements cannot provide specific allocations"),

    ("t1_abstain_hard_024", "government", "when",
     "When will the Social Security trust fund be fully depleted?",
     ["67 million Americans received benefits totaling $1.4 trillion in 2024. Funded through 12.4% payroll tax.",
      "The 2024 Trustees Report projected reserves would be depleted, requiring benefit reductions. Previous projections shifted significantly.",
      "Congress last amended Social Security in 1983 when retirement age was raised to 67."],
     "Asks for depletion date but context gives vague projection without specific year",
     "Current payment data and vague projections cannot give a specific depletion date"),

    # === agriculture (2) ===
    ("t1_abstain_hard_028", "agriculture", "what",
     "What is the genetic modification process used in Bt corn varieties?",
     ["Bt corn represents 83% of US corn acreage. Crops produce proteins toxic to specific pests, reducing pesticide use 10-12%.",
      "Farmers must maintain 20% non-Bt refuge areas. Bt seed costs $40-$60 more per bag.",
      "European corn borer damage decreased 90% in high-adoption regions, saving $1.7 billion annually."],
     "Adoption rates and outcomes but not the genetic engineering process itself",
     "Market adoption and pest reduction cannot explain the GM process"),

    ("t1_abstain_hard_029", "agriculture", "how",
     "How does hydroponic nutrient film technique maintain optimal pH?",
     ["Hydroponic systems cover 5% of global greenhouse vegetable production. NFT involves thin nutrient solution flowing over roots.",
      "NFT produces lettuce yields 11x higher per square foot. Water usage is 90% lower than field farming."],
     "Market share, yield, and crop types but not pH management mechanism",
     "Statistics and yield data cannot explain pH maintenance"),

    # === food (2) ===
    ("t1_abstain_hard_030", "food", "what",
     "What specific enzymes are involved in sourdough fermentation?",
     ["Sourdough has been made for over 5,000 years. Modern artisan bakeries have revived interest.",
      "Distinctive tangy flavor comes from lactic and acetic acid. Fermentation takes 4-12 hours.",
      "Lower glycemic index (54 vs 72 for white bread) and improved mineral absorption."],
     "History, flavor compounds, and health benefits but not specific enzymes",
     "Historical context and health benefits cannot identify specific enzymes"),

    ("t1_abstain_hard_037", "food", "how",
     "How is high-fructose corn syrup manufactured from corn starch?",
     ["HFCS is the primary US sweetener, replacing sugar since the 1980s. US produces 8 million metric tons annually.",
      "Two formulations: HFCS-42 (cereals, baked goods) and HFCS-55 (soft drinks).",
      "AMA states HFCS is not significantly different from sucrose metabolically."],
     "Market usage and formulations but not manufacturing process",
     "Product types and consumption stats cannot explain manufacturing"),

    # === transportation (2) ===
    ("t1_abstain_hard_031", "transportation", "what",
     "What were the specific technical failures in the Boeing 737 MAX MCAS system?",
     ["The 737 MAX was grounded March 2019 to December 2020 after two crashes killing 346 people.",
      "Congressional investigations found Boeing prioritized cost over safety. FAA delegated certification to Boeing.",
      "Boeing paid $2.5 billion in fines and compensation. MAX returned with software updates."],
     "Crash summary and organizational failures but not technical MCAS details",
     "Timelines and penalties cannot explain the specific MCAS malfunction"),

    ("t1_abstain_hard_032", "transportation", "when",
     "When will fully autonomous Level 5 vehicles be commercially available?",
     ["Waymo operates Level 4 robotaxis in Phoenix, San Francisco, and Los Angeles. 7 million autonomous miles in 2024.",
      "Cruise suspended driverless operations October 2023 after a San Francisco incident.",
      "Tesla's FSD requires constant driver supervision, operating at Level 2+."],
     "Current Level 2-4 deployments cannot predict Level 5 availability",
     "Limited autonomous deployments cannot predict when Level 5 will be available"),

    # === sports (2) ===
    ("t1_abstain_hard_121", "sports", "what",
     "What was the specific contract structure of the NBA's 2025 media rights deal?",
     ["The previous ESPN/Turner deal was $24 billion over 9 years. New deal negotiations included Amazon, NBC, and ESPN.",
      "Reports suggested the new deal could exceed $75 billion over 11 years.",
      "NBA League Pass available in 200+ countries with games broadcast in 50 languages."],
     "Previous deal and pre-negotiation reports but not the final 2025 structure",
     "Previous terms and speculation cannot provide the final agreement structure"),

    ("t1_abstain_hard_122", "sports", "how",
     "How does the NFL's salary cap calculation formula work?",
     ["The 2024 cap was $255.4 million per team, a $30.6 million increase from 2023.",
      "Teams can carry over unused cap space. Cowboys and Saints are most aggressive at cap manipulation.",
      "Salaries can be structured with prorated signing bonuses. Dead money charges occur when players are cut."],
     "Cap amounts and management techniques but not the calculation formula",
     "Cap amounts and strategies cannot explain the mathematical formula"),

    # === hr_workplace (1) ===
    ("t1_abstain_hard_230", "hr_workplace", "what",
     "What is the specific scoring methodology of the Gallup Q12 employee engagement survey?",
     ["The Gallup Q12 survey is used by over 2.7 million work teams worldwide. Companies in the top quartile of engagement have 23% higher profitability.",
      "The survey consists of 12 questions measuring elements of workplace engagement. Gallup has benchmarking data from over 100,000 business units.",
      "Organizations that act on Q12 results see 14% improvement in productivity within one year."],
     "Survey usage and outcomes but not the actual scoring methodology",
     "Usage statistics and outcomes cannot explain how the Q12 is scored"),
]


DISPUTE_CONVERSIONS = [
    # === social_media (3) ===
    ("t1_dispute_hard_012", "social_media", "does",
     "Does social media cause depression in teenagers?",
     ["A 2019 study of 12,000 UK teenagers found 3+ hours daily social media correlated with 2x increase in depression symptoms.",
      "The APA's 2023 advisory stated social media's causal role remains unproven; most evidence is correlational.",
      "A natural experiment where Facebook was temporarily banned in India showed no change in mental health scores among 15,000 teens.",
      "Jonathan Haidt's 2024 analysis argues teen mental health decline timing (2012-2015) perfectly matches smartphone adoption."],
     "Correlational studies suggest harm but experimental studies show no effect",
     "Large correlations exist; APA says causation unproven; natural experiment shows no effect"),

    ("t1_dispute_hard_017", "social_media", "is",
     "Is content moderation effective at reducing hate speech online?",
     ["Meta's report showed 50% reduction in hate speech after AI moderation, with 97% removed before user reports.",
      "ADL found hate speech on Facebook actually increased 25% using different criteria including coded language.",
      "Stanford research found heavy moderation causes migration to unmoderated platforms, net zero reduction.",
      "EU's Digital Services Act reported 40% decrease in regulated markets."],
     "Platform data shows reduction, independent audits show increase, migration may neutralize gains",
     "Platform self-reports vs independent audits contradict; displacement effects may neutralize"),

    ("t1_dispute_hard_018", "social_media", "what",
     "What is the actual click-through rate impact of influencer marketing versus traditional digital ads?",
     ["Nielsen 2024: influencer marketing achieves 5.2% engagement vs 0.9% for display ads, 3.5x higher CTR.",
      "Journal of Marketing (2024) analyzing 50,000 campaigns found no significant purchase conversion difference when controlling for targeting quality.",
      "FTC reported 30% of influencer engagement metrics are inflated by bots and engagement pods."],
     "Conflicting performance data; metric reliability questionable",
     "Industry data shows superiority; academic study shows no difference; FTC questions reliability"),

    # === history (3) ===
    ("t1_dispute_hard_100", "history", "when",
     "When did humans first arrive in the Americas?",
     ["Clovis-first model dates arrival to approximately 13,000 years ago based on fluted stone tools.",
      "Monte Verde in Chile has radiocarbon dates of 14,500 years ago, accepted by most archaeologists.",
      "Cerutti Mastodon site claims suggest 130,000 years ago, though most archaeologists reject this.",
      "Genetic studies suggest divergence 23,000-25,000 years ago, implying arrival during Last Glacial Maximum."],
     "Dates range from 13,000 to 130,000 years depending on evidence type",
     "Archaeological, genetic, and controversial sites give conflicting timelines"),

    ("t1_dispute_hard_101", "history", "what",
     "What caused the Bronze Age Collapse around 1200 BCE?",
     ["47 major cities destroyed or abandoned between 1250-1150 BCE including Troy, Mycenae, and Ugarit.",
      "Egyptian inscriptions attribute collapse to 'Sea Peoples' — unidentified maritime raiders.",
      "Climate analysis suggests a 300-year drought beginning around 1200 BCE caused agricultural failure.",
      "Eric Cline's systems collapse theory argues interconnected trade was so fragile that cascading disruptions caused failure."],
     "Multiple competing theories with evidence supporting each",
     "Sea Peoples, drought, and systems collapse each have supporting evidence"),

    ("t1_dispute_hard_105", "history", "who",
     "Who was primarily responsible for winning World War II in Europe?",
     ["Soviet forces suffered 27 million casualties and destroyed 80% of the Wehrmacht on the Eastern Front.",
      "American Lend-Lease shipped $180 billion (2024 dollars) in supplies including 400,000 trucks to the USSR.",
      "British breaking of Enigma shortened the war by an estimated 2 years.",
      "The Combined Bomber Offensive destroyed 50% of German industrial capacity by 1944."],
     "Each major ally claims decisive contribution with legitimate evidence",
     "Soviet blood, American production, British intelligence all have credible claims"),

    # === psychology (3) ===
    ("t1_dispute_hard_106", "psychology", "is",
     "Is the concept of learning styles scientifically valid?",
     ["Pashler et al. (2009) found no credible evidence that matching teaching to learning styles improves outcomes.",
      "The International Learning Styles Network argues 71 models exist, with Kolb's showing positive effects in professional education.",
      "fMRI shows distinct neural activation for visual vs auditory learners, though whether leveraging this improves learning is unresolved.",
      "89% of educators worldwide believe in learning styles, one of the most widely held 'neuromyths'."],
     "Scientific reviews reject it, practitioners embrace it, neuroscience shows real differences",
     "No evidence matching styles improves learning but cognitive differences exist"),

    ("t1_dispute_hard_108", "psychology", "does",
     "Does birth order affect personality traits?",
     ["Sulloway (1996) argued firstborns are more conscientious, laterborns more creative, based on 6,566 scientists.",
      "Damian and Roberts (2015, PNAS) with 377,000 students found birth order effects were essentially zero after controlling for family size.",
      "Rohrer et al. (2015) with 10,000 adults found firstborns scored slightly higher on intellect but no personality differences.",
      "65% of parents in surveys believe birth order shapes personality despite scientific consensus shifting against it."],
     "Large-scale studies find minimal effects contradicting earlier work",
     "Influential historical analysis vs modern large-sample studies finding near-zero effects"),

    ("t1_dispute_hard_109", "psychology", "what",
     "What is the replication rate of published psychology findings?",
     ["Open Science Collaboration (2015): only 36% of 100 studies replicated successfully.",
      "Gilbert et al. (2018, Harvard) argued flawed replication methodology; 77% fell within original confidence intervals.",
      "Many Labs 2 (2018) replicated 54% of 28 classic findings across 125 labs.",
      "Nosek argues low rates reflect legitimate moderating factors, not false findings."],
     "Replication rates range 36-77% depending on definition of success",
     "Fundamental disagreement on what counts as successful replication"),

    # === government (3) ===
    ("t1_dispute_hard_125", "government", "is",
     "Is universal basic income economically feasible for developed nations?",
     ["Finland's UBI experiment ($685/month): improved well-being, recipients 27% more likely to find employment.",
      "CBO estimates US-wide $12,000/year UBI would cost $3 trillion annually — more than discretionary budget.",
      "Stockton's SEED ($500/month): full-time employment increased from 28% to 40%.",
      "Critics argue revenue-neutral UBI funded by eliminating programs would leave vulnerable populations worse off."],
     "Pilots show positive employment effects but fiscal concerns are serious",
     "Pilots show benefits but full-scale cost is enormous"),

    ("t1_dispute_hard_126", "government", "does",
     "Does ranked-choice voting increase voter participation?",
     ["FairVote: turnout increased 10% in 56 RCV elections vs previous plurality elections.",
      "MIT 2023 study: no significant difference when controlling for election type and competitiveness.",
      "Alaska 2022: 62% found it easy but 30% reported confusion and 15% had ballot errors.",
      "NYC: comprehension was 95%+ in affluent areas but dropped to 72% in lower-income areas."],
     "Conflicting evidence on turnout and equity concerns about comprehension gaps",
     "FairVote shows increase; MIT finds no difference; comprehension gaps raise equity issues"),

    ("t1_dispute_hard_136", "government", "should",
     "Should the Electoral College be abolished?",
     ["Electoral College produced five popular-vote-losing presidents. Wyoming has one elector per 193,000 residents vs California's one per 720,000.",
      "Defenders argue it forces geographically diverse coalitions and protects federalism.",
      "National Popular Vote Compact has 209 of 270 needed electoral votes, but constitutional viability is uncertain.",
      "Both parties' strategies would change radically under popular vote, making predictions unreliable."],
     "Fundamental disagreement about majority rule vs geographic diversity",
     "Disproportionate representation vs coalition-building; constitutional viability uncertain"),

    # === agriculture (2) ===
    ("t1_dispute_hard_027", "agriculture", "is",
     "Is glyphosate (Roundup) safe for human health?",
     ["EPA 2020: 'not likely to be carcinogenic to humans' at environmental exposure levels.",
      "WHO IARC 2015: classified as 'probably carcinogenic' (Group 2A) based on non-Hodgkin lymphoma evidence.",
      "Bayer paid $11 billion settling 100,000 lawsuits without admitting liability.",
      "2023 meta-analysis: 41% increased lymphoma risk for highest-exposed workers, no increased risk in general population."],
     "EPA says safe, WHO says probably carcinogenic, risk appears dose-dependent",
     "EPA and IARC directly contradict; dose-dependent risk complicates the answer"),

    ("t1_dispute_hard_137", "agriculture", "does",
     "Does GMO crop cultivation reduce or increase pesticide use?",
     ["USDA: herbicide-tolerant crops led to 28% increase in herbicide use 1996-2011.",
      "Bt crops reduced insecticide use by 37% over the same period, largest in cotton (77%) and corn (42%).",
      "Benbrook calculated net increase of 404M pounds; PG Economics (industry-funded) calculated 8.6% decrease when weighting by toxicity.",
      "'Superweeds' now found on 60+ million acres of US farmland."],
     "Herbicides up, insecticides down — net depends on measurement method",
     "Bt clearly reduces insecticides; herbicide-tolerant clearly increases herbicides; net is contested"),

    # === transportation (2) ===
    ("t1_dispute_hard_138", "transportation", "is",
     "Is high-speed rail economically justified for the United States?",
     ["China's HSR generates 8% GDP boost in connected corridors, shifted 30% of short-haul air traffic.",
      "California HSR costs ballooned from $33B to $128B, may never compete with $80 flights.",
      "European HSR broke even operationally in 15 years but never recouped construction subsidies.",
      "Including environmental externalities ($200B/year aviation emissions), HSR provides $3 benefit per $1 invested."],
     "Construction costs enormous but benefit calculations vary wildly",
     "Cost overruns real but international comparisons and externalities show different pictures"),

    ("t1_dispute_hard_402", "transportation", "does",
     "Does adding highway lanes reduce traffic congestion?",
     ["Texas Transportation Institute: congestion returns within 3-5 years due to induced demand.",
      "Houston Katy Freeway ($2.8B, 23 lanes): commute times increased from 57 to 65 minutes within two years.",
      "FHWA: 40% of congestion is at specific bottlenecks; targeted fixes yield lasting improvements.",
      "University of Toronto: elasticity of VMT to lane-miles is approximately 1.0 — 10% more lanes = 10% more driving."],
     "General lane additions fail due to induced demand, but bottleneck fixes work",
     "Strong induced demand evidence but targeted fixes are effective"),

    # === hr_workplace (2) ===
    ("t1_dispute_hard_300", "hr_workplace", "is",
     "Is the open-plan office more productive than private offices?",
     ["Harvard (2018): open-plan reduced face-to-face interactions 70% and increased email 56%.",
      "Google: teams in open spaces showed 15% higher idea generation rates.",
      "Meta-analysis of 50 studies: open plans reduced focused work 15% but increased information sharing 20%.",
      "Steelcase: employee satisfaction dropped 20% after conversion while facilities costs decreased 30%."],
     "Increases some collaboration but decreases focus work and satisfaction",
     "Harvard shows less interaction; Google shows more ideas; productivity-sharing tradeoff"),

    ("t1_dispute_hard_301", "hr_workplace", "does",
     "Does offering higher salaries attract better performing employees?",
     ["Mas (2017): 10% above market sees 25% more applicants and 15% lower turnover.",
      "Deci et al. (1999) meta-analysis: extrinsic rewards undermined intrinsic motivation, 20% less engagement on creative tasks.",
      "LinkedIn 2023: top 10% paying companies had 30% higher performance ratings, but correlation disappeared controlling for company reputation.",
      "Dan Pink: beyond ~$85,000, additional salary has minimal performance impact."],
     "Higher pay attracts more applicants but performance link disappears after controlling confounds",
     "More applicants but intrinsic motivation, confounding, and threshold effects complicate"),

    # === food (2) ===
    ("t1_dispute_hard_302", "food", "is",
     "Is raw milk safer or more nutritious than pasteurized milk?",
     ["2018 study: children on raw milk had 30% lower asthma and allergy rates.",
      "CDC: raw milk is 150x more likely to cause foodborne illness, 202 outbreaks and 2,645 illnesses from 2007-2020.",
      "Raw milk has 5-10% more vitamin C and B6, but these are easily obtained elsewhere.",
      "FDA 2024 concluded pasteurization has 'minimal nutritional impact'; allergy benefits may be from farm exposure not milk."],
     "Minor nutritional advantages vs major safety risks; allergy benefit likely confounded",
     "Small nutritional differences but 150x higher illness risk"),

    ("t1_dispute_hard_304", "food", "does",
     "Does eating breakfast improve cognitive performance?",
     ["Systematic review of 54 studies: breakfast associated with improved memory and academic performance in children.",
      "BMJ 2019 meta-analysis of 13 RCTs: no evidence breakfast aids weight loss; eaters consumed 260 more calories.",
      "2024 crossover study: no cognitive difference between breakfast and fasting when well-rested, but breakfast helped when sleep-deprived.",
      "IF research suggests skipping breakfast may improve insulin sensitivity after 2-week adaptation."],
     "Association in children vs no RCT evidence for metabolic benefits",
     "Observational studies show benefits; RCTs show no metabolic benefit"),
]


def apply_conversions(conversions, category_file):
    """Apply domain conversions to cases in a category file."""
    filepath = Path(f"data/tier1_core/{category_file}")
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    cases_by_id = {c["id"]: c for c in data["cases"]}
    converted = 0

    for conv in conversions:
        case_id, target_domain, new_query_type, new_query, new_contexts, new_description, new_rationale = conv
        if case_id not in cases_by_id:
            print(f"  WARNING: {case_id} not found in {category_file}")
            continue

        case = cases_by_id[case_id]
        old_domain = case.get("domain", "unknown")

        # Track original domain
        if "metadata" not in case:
            case["metadata"] = {}
        case["metadata"]["domain_converted_from"] = old_domain

        # Update domain content
        case["query"] = new_query
        case["contexts"] = new_contexts
        case["description"] = new_description
        case["rationale"] = new_rationale

        # Update classification
        case["domain"] = target_domain
        case["query_type"] = new_query_type
        case["context_count"] = len(new_contexts)

        converted += 1

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return converted


def main():
    total = 0

    n = apply_conversions(TRUSTWORTHY_DIRECT_CONVERSIONS, "trustworthy_direct.json")
    print(f"trustworthy_direct: {n} conversions")
    total += n

    n = apply_conversions(TRUSTWORTHY_HEDGED_CONVERSIONS, "trustworthy_hedged.json")
    print(f"trustworthy_hedged: {n} conversions")
    total += n

    n = apply_conversions(ABSTENTION_CONVERSIONS, "abstention.json")
    print(f"abstention: {n} conversions")
    total += n

    n = apply_conversions(DISPUTE_CONVERSIONS, "dispute.json")
    print(f"dispute: {n} conversions")
    total += n

    print(f"\nTotal: {total} domain conversions applied")

    # Verify domain distribution
    from collections import Counter
    domains = Counter()
    for cat in ["trustworthy_direct", "trustworthy_hedged", "abstention", "dispute"]:
        with open(f"data/tier1_core/{cat}.json", encoding="utf-8") as f:
            data = json.load(f)
        for c in data["cases"]:
            domains[c.get("domain", "unknown")] += 1

    total_cases = sum(domains.values())
    print("\nGovernance category domain distribution after conversion:")
    for d, n in domains.most_common():
        print(f"  {d:20s} {n:4d} ({n/total_cases*100:5.1f}%)")


if __name__ == "__main__":
    main()
