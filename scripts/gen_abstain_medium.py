#!/usr/bin/env python3
"""Generate 60 new MEDIUM difficulty abstention cases (t1_abstain_medium_1111 through _1170).

Distribution constraints:
  Subcategories: wrong_entity(8), wrong_specificity(7), temporal_mismatch(7),
    missing_data(7), off_topic_contradiction(5), wrong_domain(5), wrong_jurisdiction(4),
    outdated_context(4), wrong_product(3), cross_domain_insufficient(3), decoy_keywords(3),
    wrong_granularity(2), implicit_only(2)
  Multi-source: 15 of 60 cases
  Domains: 18 domains, max 5 each, prioritize history/psychology/social_media/agriculture
  Query types: what<=15, how>=12, is/does>=12, why/should>=8, when/who/which>=6
"""

import json
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "tier1_core" / "abstention.json"

NEW_CASES = [
    # =========================================================================
    # WRONG_ENTITY (8 cases: 1111-1118)
    # =========================================================================
    {
        "id": "t1_abstain_medium_1111",
        "difficulty": "medium",
        "subcategory": "wrong_entity",
        "query": "How does Samsung's Galaxy S25 camera compare to previous models?",
        "contexts": [
            "Google released the Pixel 9 Pro in August 2024 with an upgraded 50MP main sensor and a new 48MP ultrawide lens. Google's Tensor G4 chip brings improved computational photography and better night mode processing."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about Samsung Galaxy S25 but context covers Google Pixel 9",
        "rationale": "Google Pixel camera specs say nothing about Samsung Galaxy camera performance",
        "domain": "technology",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1112",
        "difficulty": "medium",
        "subcategory": "wrong_entity",
        "query": "What role did Genghis Khan play in the fall of the Song Dynasty?",
        "contexts": [
            "Genghis Khan united the Mongol tribes and established the Mongol Empire in 1206. His military campaigns conquered vast territories across Central Asia, Persia, and parts of Eastern Europe. The Mongol army was known for its cavalry tactics, composite bows, and psychological warfare against fortified cities.",
            "The Jin Dynasty of northern China fell to the Mongols in 1234, over a decade after Genghis Khan's campaigns weakened their defenses. The Jin had ruled northern China since 1115 and maintained a complex relationship with neighboring states."
        ],
        "context_sources": [
            {"source_id": "mongol_empire_history_2023", "source_type": "academic_text", "authority": "primary"},
            {"source_id": "jin_dynasty_fall_review", "source_type": "journal_article", "authority": "secondary"}
        ],
        "expected_mode": "abstain",
        "description": "Query asks about Genghis Khan and the Song Dynasty but contexts only cover his general campaigns and the fall of the Jin Dynasty",
        "rationale": "The Song Dynasty fell to Kublai Khan decades later; Genghis Khan's campaigns against the Jin cannot answer questions about the Song",
        "domain": "history",
        "query_type": "what",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1113",
        "difficulty": "medium",
        "subcategory": "wrong_entity",
        "query": "Is the University of Tokyo ranked in the top 10 globally?",
        "contexts": [
            "Peking University in Beijing is consistently ranked among Asia's top universities. In the 2024 QS World Rankings, Peking University placed 17th globally, with particular strength in engineering and natural sciences programs."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about University of Tokyo ranking but context covers Peking University",
        "rationale": "Peking University's ranking does not inform University of Tokyo's standing",
        "domain": "education",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1114",
        "difficulty": "medium",
        "subcategory": "wrong_entity",
        "query": "How did Napoleon perform at the Battle of Austerlitz?",
        "contexts": [
            "The Duke of Wellington commanded British and allied forces at the Battle of Waterloo in 1815. Wellington's defensive strategy on the ridge of Mont-Saint-Jean, combined with the timely arrival of Prussian reinforcements, led to a decisive Allied victory over the French army."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about Napoleon at Austerlitz but context covers Wellington at Waterloo",
        "rationale": "Wellington's tactics at Waterloo cannot describe Napoleon's performance at Austerlitz",
        "domain": "history",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1115",
        "difficulty": "medium",
        "subcategory": "wrong_entity",
        "query": "Does Spotify offer lossless audio streaming?",
        "contexts": [
            "Apple Music launched its Lossless Audio tier in June 2021, offering ALAC encoding up to 24-bit/192kHz at no additional cost. Apple Music also supports Dolby Atmos spatial audio on compatible devices, with a growing library of spatially mixed tracks."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about Spotify's lossless audio but context covers Apple Music's lossless feature",
        "rationale": "Apple Music's lossless offering says nothing about whether Spotify has a similar feature",
        "domain": "technology",
        "query_type": "does",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1116",
        "difficulty": "medium",
        "subcategory": "wrong_entity",
        "query": "Why did the Roman Republic transition to an Empire?",
        "contexts": [
            "The Greek city-state of Athens transitioned from oligarchy to democracy under the reforms of Cleisthenes around 508 BCE. The Athenian democratic system allowed male citizens to vote directly on legislation and executive decisions, creating a model that influenced later political thought."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about Rome's political transition but context covers Athens's democratic reforms",
        "rationale": "Athenian democracy reforms cannot explain the Roman Republic-to-Empire transition",
        "domain": "history",
        "query_type": "why",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "causal",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1117",
        "difficulty": "medium",
        "subcategory": "wrong_entity",
        "query": "How does TikTok's algorithm determine content recommendations?",
        "contexts": [
            "YouTube's recommendation system uses a deep neural network to suggest videos. It considers watch history, search queries, user demographics, and video metadata. YouTube's algorithm prioritizes watch time and session duration as key engagement metrics.",
            "Instagram's Explore page uses machine learning to surface posts based on user interactions, hashtag following, and content similarity. The platform prioritizes content from accounts users have previously engaged with, and uses image recognition to categorize visual content into topic clusters."
        ],
        "context_sources": [
            {"source_id": "youtube_eng_blog_2024", "source_type": "tech_blog", "authority": "primary"},
            {"source_id": "instagram_creators_guide", "source_type": "platform_docs", "authority": "secondary"}
        ],
        "expected_mode": "abstain",
        "description": "Query asks about TikTok's algorithm but contexts cover YouTube and Instagram algorithms",
        "rationale": "YouTube and Instagram recommendation systems differ fundamentally from TikTok's approach",
        "domain": "social_media",
        "query_type": "how",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1118",
        "difficulty": "medium",
        "subcategory": "wrong_entity",
        "query": "What side effects does ibuprofen have on the stomach?",
        "contexts": [
            "Acetaminophen (Tylenol) is metabolized primarily by the liver. Chronic overuse of acetaminophen can lead to hepatotoxicity and liver failure. The maximum recommended daily dose for adults is 3,000 mg, and it should be avoided in patients with pre-existing liver disease."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about ibuprofen's gastrointestinal effects but context covers acetaminophen's liver effects",
        "rationale": "Acetaminophen liver toxicity data cannot answer questions about ibuprofen stomach effects",
        "domain": "medicine",
        "query_type": "what",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    # =========================================================================
    # WRONG_SPECIFICITY (7 cases: 1119-1125)
    # =========================================================================
    {
        "id": "t1_abstain_medium_1119",
        "difficulty": "medium",
        "subcategory": "wrong_specificity",
        "query": "What is the yield strength of Grade 5 titanium alloy?",
        "contexts": [
            "Titanium alloys are widely used in aerospace, medical implants, and marine engineering due to their high strength-to-weight ratio and excellent corrosion resistance. Titanium is about 45% lighter than steel while offering comparable strength."
        ],
        "expected_mode": "abstain",
        "description": "Query asks for specific yield strength of Grade 5 titanium but context gives only general titanium properties",
        "rationale": "General statements about titanium do not provide the specific yield strength of Grade 5 alloy",
        "domain": "science",
        "query_type": "what",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1120",
        "difficulty": "medium",
        "subcategory": "wrong_specificity",
        "query": "How many calories are in a Starbucks Grande Caramel Macchiato?",
        "contexts": [
            "Starbucks offers a wide range of beverages including espresso drinks, blended beverages, teas, and refreshers. The company sources arabica coffee beans from over 30 countries and roasts them at facilities in Kent, Washington and other global locations."
        ],
        "expected_mode": "abstain",
        "description": "Query asks for specific calorie count but context only describes Starbucks product range",
        "rationale": "General company and sourcing information cannot provide specific nutritional data for a particular drink",
        "domain": "food",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1121",
        "difficulty": "medium",
        "subcategory": "wrong_specificity",
        "query": "When does the New York City subway stop running on weeknights?",
        "contexts": [
            "The New York City subway system is one of the largest mass transit systems in the world, operating 472 stations across 36 lines. The MTA serves approximately 3.5 million riders on an average weekday. Major hub stations include Times Square, Grand Central, and Penn Station."
        ],
        "expected_mode": "abstain",
        "description": "Query asks for specific operating hours but context only covers general subway statistics",
        "rationale": "Ridership statistics and station counts do not indicate late-night operating schedules",
        "domain": "transportation",
        "query_type": "when",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1122",
        "difficulty": "medium",
        "subcategory": "wrong_specificity",
        "query": "What is the interest rate on a 30-year fixed mortgage from Wells Fargo?",
        "contexts": [
            "Wells Fargo is one of the four largest banks in the United States by total assets. The company offers various financial services including banking, investments, and mortgage products. Wells Fargo employs approximately 230,000 people and operates over 4,700 retail banking branches.",
            "The U.S. housing market saw significant activity in 2024 with mortgage applications rising as the Federal Reserve signaled rate adjustments. Existing home sales reached 4.15 million units on an annualized basis, while median days on market fell to 22 days in competitive metro areas."
        ],
        "context_sources": [
            {"source_id": "wells_fargo_annual_2024", "source_type": "corporate_report", "authority": "primary"},
            {"source_id": "fed_housing_summary_2024", "source_type": "government_report", "authority": "secondary"}
        ],
        "expected_mode": "abstain",
        "description": "Query asks for a specific mortgage rate but contexts describe company overview and market trends",
        "rationale": "Corporate profile and housing market trends do not contain a specific mortgage interest rate",
        "domain": "finance",
        "query_type": "what",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1123",
        "difficulty": "medium",
        "subcategory": "wrong_specificity",
        "query": "How much RAM does the MacBook Pro M4 Max configuration include?",
        "contexts": [
            "Apple announced the M4 chip family in late 2024, featuring improved power efficiency and enhanced machine learning cores. The M4 lineup includes standard M4, M4 Pro, and M4 Max variants. Apple's marketing emphasized that the M4 Max delivers the fastest performance ever in a Mac notebook."
        ],
        "expected_mode": "abstain",
        "description": "Query asks for specific RAM configuration but context only covers chip announcements and marketing claims",
        "rationale": "Marketing language about fastest performance does not specify actual RAM configurations",
        "domain": "technology",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1124",
        "difficulty": "medium",
        "subcategory": "wrong_specificity",
        "query": "What is the germination time for Roma tomato seeds?",
        "contexts": [
            "Roma tomatoes are a popular paste tomato variety known for their oblong shape and meaty texture. They are commonly used in sauces, canning, and drying. Roma plants are determinate, meaning they grow to a fixed size and produce fruit over a concentrated period."
        ],
        "expected_mode": "abstain",
        "description": "Query asks for specific germination time but context covers general Roma tomato characteristics",
        "rationale": "Plant growth habit and culinary uses do not specify seed germination duration",
        "domain": "agriculture",
        "query_type": "what",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1125",
        "difficulty": "medium",
        "subcategory": "wrong_specificity",
        "query": "Should patients with type 2 diabetes take metformin before or after meals?",
        "contexts": [
            "Metformin is the most commonly prescribed medication for type 2 diabetes worldwide. It works by reducing hepatic glucose production and improving insulin sensitivity. Metformin belongs to the biguanide class of drugs and was first approved for use in the United States in 1995."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about meal timing for metformin but context covers mechanism and drug class",
        "rationale": "Drug mechanism and classification do not address dosage timing relative to meals",
        "domain": "medicine",
        "query_type": "should",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    # =========================================================================
    # TEMPORAL_MISMATCH (7 cases: 1126-1132)
    # =========================================================================
    {
        "id": "t1_abstain_medium_1126",
        "difficulty": "medium",
        "subcategory": "temporal_mismatch",
        "query": "Who won the 2026 FIFA World Cup?",
        "contexts": [
            "Argentina won the 2022 FIFA World Cup held in Qatar, defeating France in a penalty shootout in the final. Lionel Messi was awarded the Golden Ball as the tournament's best player, cementing his legacy as one of the greatest footballers of all time."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about 2026 World Cup but context covers the 2022 tournament",
        "rationale": "Results from the 2022 World Cup cannot answer who won the 2026 edition",
        "domain": "sports",
        "query_type": "who",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1127",
        "difficulty": "medium",
        "subcategory": "temporal_mismatch",
        "query": "Is the Ottoman Empire still a major political power in the Middle East?",
        "contexts": [
            "The Ottoman Empire reached its peak under Suleiman the Magnificent in the 16th century, controlling vast territories across southeastern Europe, western Asia, and northern Africa. The empire's administrative system organized provinces under governors appointed by the Sultan in Constantinople.",
            "Ottoman architecture flourished during the classical period, producing masterworks like the Suleymaniye Mosque designed by architect Mimar Sinan. The empire maintained a sophisticated court culture blending Turkish, Persian, and Arabic traditions."
        ],
        "context_sources": [
            {"source_id": "ottoman_history_textbook_2023", "source_type": "academic_text", "authority": "primary"},
            {"source_id": "islamic_art_architecture_review", "source_type": "reference_book", "authority": "secondary"}
        ],
        "expected_mode": "abstain",
        "description": "Query asks about current political status but context only covers the Ottoman Empire at its 16th-century peak",
        "rationale": "Historical descriptions of the empire's zenith cannot address its current existence or dissolution in 1922",
        "domain": "history",
        "query_type": "is",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1128",
        "difficulty": "medium",
        "subcategory": "temporal_mismatch",
        "query": "How did ancient Egyptian farming techniques work before the Nile dams?",
        "contexts": [
            "Modern Egyptian agriculture relies heavily on the Aswan High Dam, completed in 1970, which controls the Nile's flooding and provides year-round irrigation. Egypt's agricultural sector now focuses on cotton, rice, and sugarcane production using controlled irrigation systems and modern fertilizers."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about ancient pre-dam farming but context only covers modern post-dam agriculture",
        "rationale": "Modern dam-controlled agriculture cannot describe ancient flood-based farming practices",
        "domain": "agriculture",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1129",
        "difficulty": "medium",
        "subcategory": "temporal_mismatch",
        "query": "When did the first social media platform launch?",
        "contexts": [
            "Facebook launched in February 2004 from a Harvard University dorm room. By 2024, Meta Platforms (Facebook's parent company) reported over 3 billion monthly active users across Facebook and Instagram. The company's revenue in 2023 exceeded $134 billion, primarily from advertising.",
            "Twitter was launched in July 2006 as a microblogging platform allowing users to post 140-character messages. It was rebranded to X in 2023 after acquisition by Elon Musk, who subsequently removed the character limit for premium subscribers."
        ],
        "context_sources": [
            {"source_id": "meta_annual_report_2023", "source_type": "corporate_filing", "authority": "primary"},
            {"source_id": "social_media_timeline_2024", "source_type": "reference_article", "authority": "secondary"}
        ],
        "expected_mode": "abstain",
        "description": "Query asks about the first social media platform but contexts only cover Facebook (2004) and Twitter (2006)",
        "rationale": "Earlier platforms like SixDegrees (1997) and Friendster (2002) preceded Facebook; these sources cannot identify the first",
        "domain": "social_media",
        "query_type": "when",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1130",
        "difficulty": "medium",
        "subcategory": "temporal_mismatch",
        "query": "What psychological treatments were used for PTSD in the 1950s?",
        "contexts": [
            "PTSD was officially recognized as a diagnosis in the DSM-III in 1980. Modern evidence-based treatments include Cognitive Processing Therapy (CPT), developed in the 1990s, and Eye Movement Desensitization and Reprocessing (EMDR), introduced by Francine Shapiro in 1987."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about 1950s PTSD treatment but context covers post-1980 era treatments",
        "rationale": "Treatments developed after 1980 cannot describe what was used in the 1950s before PTSD was even defined",
        "domain": "psychology",
        "query_type": "what",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1131",
        "difficulty": "medium",
        "subcategory": "temporal_mismatch",
        "query": "Is the Space Shuttle program still active at NASA?",
        "contexts": [
            "The Space Shuttle program launched its first mission, STS-1, on April 12, 1981, with the orbiter Columbia. Over its 30-year history, the program completed 135 missions and carried 355 individual astronauts to space. The fleet included Columbia, Challenger, Discovery, Atlantis, and Endeavour."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about current status but context only covers historical missions without mentioning retirement",
        "rationale": "Historical mission counts and orbiter names do not indicate the program's current operational status",
        "domain": "science",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1132",
        "difficulty": "medium",
        "subcategory": "temporal_mismatch",
        "query": "Which teams played in the 2030 Super Bowl?",
        "contexts": [
            "Super Bowl LVIII was held on February 11, 2024, at Allegiant Stadium in Las Vegas, Nevada. The Kansas City Chiefs defeated the San Francisco 49ers 25-22 in overtime. Patrick Mahomes was named Super Bowl MVP for the third time in his career."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about the 2030 Super Bowl but context only covers the 2024 game",
        "rationale": "The 2024 Super Bowl result cannot predict or determine which teams play in 2030",
        "domain": "sports",
        "query_type": "which",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    # =========================================================================
    # MISSING_DATA (7 cases: 1133-1139)
    # =========================================================================
    {
        "id": "t1_abstain_medium_1133",
        "difficulty": "medium",
        "subcategory": "missing_data",
        "query": "How much does a plumber charge per hour in Denver, Colorado?",
        "contexts": [
            "Denver, Colorado has a population of approximately 713,000 and is the largest city in the state. The city's economy is driven by government, telecommunications, and energy sectors. Denver's cost of living is about 12% above the national average."
        ],
        "expected_mode": "abstain",
        "description": "Query asks for plumber hourly rates but context gives general Denver economic data",
        "rationale": "General cost of living index does not provide specific plumber service rates",
        "domain": "real_estate",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1134",
        "difficulty": "medium",
        "subcategory": "missing_data",
        "query": "What is the employee turnover rate at Amazon warehouses?",
        "contexts": [
            "Amazon operates over 1,500 fulfillment and distribution centers worldwide. The company uses advanced robotics, including Sparrow and Proteus robots, for sorting and picking tasks. Amazon employs over 1.5 million people globally, making it one of the largest private employers in the world.",
            "Amazon warehouse workers are classified as hourly employees and work shifts ranging from 8 to 12 hours. The company offers a starting wage of at least $15 per hour and benefits including health insurance after 90 days of employment."
        ],
        "context_sources": [
            {"source_id": "amazon_operations_overview_2024", "source_type": "corporate_report", "authority": "primary"},
            {"source_id": "amazon_careers_page_2024", "source_type": "company_website", "authority": "secondary"}
        ],
        "expected_mode": "abstain",
        "description": "Query asks for warehouse turnover rates but contexts describe operations, workforce size, and compensation",
        "rationale": "Employee headcount, facility count, and compensation details do not indicate turnover rate percentages",
        "domain": "hr_workplace",
        "query_type": "what",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1135",
        "difficulty": "medium",
        "subcategory": "missing_data",
        "query": "Does exposure to blue light from screens cause permanent eye damage?",
        "contexts": [
            "Blue light has a wavelength between 380 and 500 nanometers, making it one of the highest-energy visible light spectrums. Blue light is emitted naturally by the sun and artificially by LED screens, fluorescent lighting, and digital displays. The human eye's cornea and lens are not very effective at blocking blue light."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about permanent eye damage but context only covers blue light physics and sources",
        "rationale": "Physical properties of blue light do not establish whether screen exposure causes permanent damage",
        "domain": "science",
        "query_type": "does",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "causal",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1136",
        "difficulty": "medium",
        "subcategory": "missing_data",
        "query": "Why do some people develop seasonal affective disorder while others do not?",
        "contexts": [
            "Seasonal affective disorder (SAD) is a form of depression that follows a seasonal pattern, most commonly beginning in autumn and continuing through winter. Symptoms include persistent low mood, loss of interest in activities, irritability, and changes in sleep and appetite patterns. SAD affects approximately 5% of the U.S. population.",
            "Light therapy using a 10,000 lux lamp for 20-30 minutes each morning is a common first-line treatment for SAD. Antidepressant medications such as bupropion are sometimes prescribed preventively before the onset of winter symptoms in patients with recurrent episodes."
        ],
        "context_sources": [
            {"source_id": "nimh_sad_factsheet_2024", "source_type": "government_report", "authority": "primary"},
            {"source_id": "mayo_clinic_sad_2024", "source_type": "medical_reference", "authority": "secondary"}
        ],
        "expected_mode": "abstain",
        "description": "Query asks about individual susceptibility factors but contexts describe symptoms and treatment",
        "rationale": "Symptom descriptions and treatment methods do not explain why some individuals develop SAD and others do not",
        "domain": "psychology",
        "query_type": "why",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "causal",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1137",
        "difficulty": "medium",
        "subcategory": "missing_data",
        "query": "How many followers does the average Instagram influencer need to get brand deals?",
        "contexts": [
            "Instagram influencer marketing has become a multi-billion dollar industry. Brands use influencers to promote products through sponsored posts, stories, and reels. The platform's shopping features allow influencers to tag products directly in their content for seamless purchasing."
        ],
        "expected_mode": "abstain",
        "description": "Query asks for specific follower threshold for brand deals but context describes the industry in general",
        "rationale": "Industry overview does not provide specific follower count thresholds for brand partnerships",
        "domain": "social_media",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1138",
        "difficulty": "medium",
        "subcategory": "missing_data",
        "query": "Does the Silk Road archaeological evidence reveal what goods were traded most frequently?",
        "contexts": [
            "The Silk Road was a network of trade routes connecting China to the Mediterranean from roughly the 2nd century BCE to the 15th century CE. Caravansaries provided rest stops for merchants traveling across Central Asian deserts and mountain passes. The routes facilitated not only trade but also cultural, religious, and technological exchange between civilizations.",
            "Archaeological excavations at sites along the Silk Road have uncovered pottery shards, textile fragments, and coin hoards. However, organic materials like spices, silk, and food have rarely survived in the archaeological record due to decomposition over centuries."
        ],
        "context_sources": [
            {"source_id": "silk_road_history_2024", "source_type": "academic_text", "authority": "primary"},
            {"source_id": "central_asia_archaeology_review", "source_type": "journal_article", "authority": "secondary"}
        ],
        "expected_mode": "abstain",
        "description": "Query asks about most frequently traded goods but archaeological evidence is limited by organic decay",
        "rationale": "The context explicitly states that key trade goods like silk and spices rarely survive archaeologically, making frequency determination impossible",
        "domain": "history",
        "query_type": "does",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1139",
        "difficulty": "medium",
        "subcategory": "missing_data",
        "query": "Is remote work more productive than in-office work?",
        "contexts": [
            "Many companies adopted remote work policies during the COVID-19 pandemic. As of 2024, approximately 27% of US employees work remotely at least part-time. Major tech companies including Google, Apple, and Amazon have implemented hybrid return-to-office policies requiring 2-3 days per week in the office."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about productivity comparison but context only covers adoption rates and policies",
        "rationale": "Remote work adoption statistics do not provide evidence on productivity differences",
        "domain": "hr_workplace",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "comparative",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    # =========================================================================
    # OFF_TOPIC_CONTRADICTION (5 cases: 1140-1144)
    # =========================================================================
    {
        "id": "t1_abstain_medium_1140",
        "difficulty": "medium",
        "subcategory": "off_topic_contradiction",
        "query": "How do you train a dog to stop barking at strangers?",
        "contexts": [
            "Goldfish require a properly maintained aquarium with filtration, water temperature between 65-75 degrees Fahrenheit, and regular water changes. Common goldfish diseases include ich, fin rot, and swim bladder disorder. Goldfish can live 10-15 years with proper care."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about dog training but context is entirely about goldfish care",
        "rationale": "Goldfish husbandry has no relevance to canine behavior modification",
        "domain": "general",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "procedural",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1141",
        "difficulty": "medium",
        "subcategory": "off_topic_contradiction",
        "query": "What are the environmental impacts of lithium mining?",
        "contexts": [
            "Renaissance painting techniques evolved significantly during the 15th and 16th centuries. Artists such as Leonardo da Vinci and Raphael developed sfumato and chiaroscuro techniques to create lifelike depth and dimensionality. Oil painting on canvas gradually replaced tempera on wood panels during this period."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about lithium mining impacts but context covers Renaissance art techniques",
        "rationale": "Art history content is completely irrelevant to mining and environmental science",
        "domain": "environment",
        "query_type": "what",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1142",
        "difficulty": "medium",
        "subcategory": "off_topic_contradiction",
        "query": "Should I invest in index funds or individual stocks?",
        "contexts": [
            "The Mediterranean diet emphasizes whole grains, fruits, vegetables, legumes, nuts, and olive oil. Research published in the New England Journal of Medicine has shown the diet reduces cardiovascular disease risk by approximately 30% compared to standard Western diets.",
            "Fermented foods such as yogurt, kimchi, and kefir contain probiotics that support gut microbiome health. Regular consumption of fermented foods has been associated with reduced inflammation markers and improved immune response in several observational studies."
        ],
        "context_sources": [
            {"source_id": "nejm_diet_study_2023", "source_type": "journal_article", "authority": "primary"},
            {"source_id": "nutrition_review_2024", "source_type": "review_article", "authority": "secondary"}
        ],
        "expected_mode": "abstain",
        "description": "Query asks about investment strategy but contexts cover diet and nutrition",
        "rationale": "Dietary health research cannot inform investment decisions",
        "domain": "finance",
        "query_type": "should",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "comparative",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1143",
        "difficulty": "medium",
        "subcategory": "off_topic_contradiction",
        "query": "Why do tectonic plates move?",
        "contexts": [
            "Professional basketball courts measure 94 feet by 50 feet, with a 10-foot-high rim. The NBA uses a 24-second shot clock and four 12-minute quarters. The three-point line is set at 23 feet 9 inches from the center of the basket."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about geological plate tectonics but context covers basketball court dimensions",
        "rationale": "Basketball court specifications have no connection to geological processes",
        "domain": "sports",
        "query_type": "why",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "causal",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1144",
        "difficulty": "medium",
        "subcategory": "off_topic_contradiction",
        "query": "How does dialectical behavior therapy help patients with borderline personality disorder?",
        "contexts": [
            "The Panama Canal is a 50-mile waterway connecting the Atlantic and Pacific oceans through Panama. The canal uses a system of locks to raise ships 85 feet above sea level. Approximately 14,000 vessels transit the canal annually, carrying about 5% of world trade."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about DBT for borderline personality disorder but context covers Panama Canal engineering",
        "rationale": "Canal infrastructure has no relevance to psychological treatment methods",
        "domain": "psychology",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "procedural",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    # =========================================================================
    # WRONG_DOMAIN (5 cases: 1145-1149)
    # =========================================================================
    {
        "id": "t1_abstain_medium_1145",
        "difficulty": "medium",
        "subcategory": "wrong_domain",
        "query": "What are the legal requirements for building a backyard fence in California?",
        "contexts": [
            "California is known for its diverse cuisine, with notable food scenes in Los Angeles and San Francisco. The state produces over 400 different commodities including almonds, grapes, and strawberries, making it the leading agricultural state in the US."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about California fence building regulations but context covers California agriculture and food",
        "rationale": "Agricultural production and food culture cannot inform building code requirements",
        "domain": "law",
        "query_type": "what",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1146",
        "difficulty": "medium",
        "subcategory": "wrong_domain",
        "query": "How does photosynthesis convert sunlight into chemical energy?",
        "contexts": [
            "Solar panel technology has advanced rapidly, with modern photovoltaic cells achieving efficiency rates above 22%. Residential solar installations typically cost between $15,000 and $25,000 before tax credits. The US solar industry employed over 260,000 workers in 2024."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about biological photosynthesis but context covers commercial solar panel technology",
        "rationale": "Solar panel engineering is distinct from the biological process of photosynthesis in plants",
        "domain": "science",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "causal",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1147",
        "difficulty": "medium",
        "subcategory": "wrong_domain",
        "query": "Why do some students perform better in morning classes than afternoon classes?",
        "contexts": [
            "Morning routines in corporate offices typically include stand-up meetings, email triage, and priority-setting exercises. Research in organizational behavior shows that employees who arrive early tend to be perceived as more conscientious by managers, potentially influencing performance reviews."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about student academic performance patterns but context covers corporate workplace habits",
        "rationale": "Corporate morning routines and employee perception do not explain student learning patterns",
        "domain": "education",
        "query_type": "why",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "causal",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1148",
        "difficulty": "medium",
        "subcategory": "wrong_domain",
        "query": "Does intermittent fasting improve cognitive function?",
        "contexts": [
            "Intermittent fasting has been studied for its effects on body weight and metabolic markers. A 2023 meta-analysis found that time-restricted eating led to average weight loss of 3-5% over 12 weeks. Fasting protocols also showed improvements in fasting insulin levels and blood lipid profiles.",
            "The 16:8 fasting protocol is the most commonly practiced form, involving 16 hours of fasting and an 8-hour eating window. Other popular variations include the 5:2 diet, which involves eating normally for five days and restricting calories to 500-600 on two non-consecutive days."
        ],
        "context_sources": [
            {"source_id": "if_meta_analysis_2023", "source_type": "journal_article", "authority": "primary"},
            {"source_id": "nutrition_guide_2024", "source_type": "reference_book", "authority": "secondary"}
        ],
        "expected_mode": "abstain",
        "description": "Query asks about cognitive effects but contexts only cover metabolic and weight outcomes",
        "rationale": "Weight loss and metabolic marker data cannot answer questions about cognitive function",
        "domain": "medicine",
        "query_type": "does",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "causal",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1149",
        "difficulty": "medium",
        "subcategory": "wrong_domain",
        "query": "How do electric vehicle batteries impact soil contamination when improperly disposed?",
        "contexts": [
            "Electric vehicles have seen rapid adoption globally, with over 14 million EVs sold in 2023. Major manufacturers including Tesla, BYD, and Volkswagen are expanding production capacity. EV batteries primarily use lithium-ion chemistry, with a typical lifespan of 8-15 years before requiring replacement."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about environmental contamination from battery disposal but context covers EV market and battery lifespan",
        "rationale": "Sales figures and battery lifespan data do not address soil contamination mechanisms",
        "domain": "environment",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "causal",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    # =========================================================================
    # WRONG_JURISDICTION (4 cases: 1150-1153)
    # =========================================================================
    {
        "id": "t1_abstain_medium_1150",
        "difficulty": "medium",
        "subcategory": "wrong_jurisdiction",
        "query": "What is the minimum wage in Germany?",
        "contexts": [
            "France's minimum wage (SMIC) was increased to 11.65 euros per hour in January 2024. The French government adjusts the SMIC annually based on inflation and wage growth indicators. France has one of the highest minimum wages in the European Union."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about Germany's minimum wage but context covers France's SMIC",
        "rationale": "French minimum wage data cannot determine Germany's minimum wage rate",
        "domain": "government",
        "query_type": "what",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1151",
        "difficulty": "medium",
        "subcategory": "wrong_jurisdiction",
        "query": "Is marijuana legal for recreational use in Texas?",
        "contexts": [
            "Colorado became one of the first US states to legalize recreational marijuana in 2012. The state has generated over $15 billion in marijuana sales since legalization. Colorado's regulatory framework includes licensing requirements, age restrictions (21+), and THC potency limits for edibles."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about Texas marijuana laws but context covers Colorado's legalization",
        "rationale": "Colorado's marijuana laws are independent of Texas's legal status for marijuana",
        "domain": "law",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1152",
        "difficulty": "medium",
        "subcategory": "wrong_jurisdiction",
        "query": "How does the UK healthcare system handle prescription drug costs?",
        "contexts": [
            "Canada's universal healthcare system provides coverage for hospital and physician services under the Canada Health Act. However, prescription drug coverage varies by province. Ontario's OHIP+ program covers all prescription medications for residents under 25, while British Columbia uses a fair pharmacare plan based on household income."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about UK prescription costs but context describes Canadian provincial drug coverage",
        "rationale": "Canadian provincial healthcare policies do not describe UK NHS prescription practices",
        "domain": "government",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "procedural",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1153",
        "difficulty": "medium",
        "subcategory": "wrong_jurisdiction",
        "query": "What are the speed limits on highways in Japan?",
        "contexts": [
            "Germany's Autobahn is famous for sections without speed limits, known as 'unrestricted zones.' However, approximately 30% of the Autobahn network has posted speed limits. The recommended advisory speed is 130 km/h even on unrestricted sections.",
            "In South Korea, expressway speed limits typically range from 100-120 km/h, with automatic speed enforcement cameras placed at regular intervals. The country's KTX high-speed rail system offers an alternative for inter-city travel at speeds up to 305 km/h."
        ],
        "context_sources": [
            {"source_id": "european_road_safety_2024", "source_type": "government_report", "authority": "primary"},
            {"source_id": "asian_transport_review_2024", "source_type": "industry_journal", "authority": "secondary"}
        ],
        "expected_mode": "abstain",
        "description": "Query asks about Japanese highway speed limits but contexts cover Germany and South Korea",
        "rationale": "German Autobahn and South Korean expressway rules cannot determine Japanese highway limits",
        "domain": "transportation",
        "query_type": "what",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    # =========================================================================
    # OUTDATED_CONTEXT (4 cases: 1154-1157)
    # =========================================================================
    {
        "id": "t1_abstain_medium_1154",
        "difficulty": "medium",
        "subcategory": "outdated_context",
        "query": "What is Twitter's current monthly active user count?",
        "contexts": [
            "Twitter reported 368 million monthly active users in Q2 2022. The platform's advertising revenue was $1.18 billion for the quarter. Twitter's user growth was strongest in Japan and India outside of North America."
        ],
        "expected_mode": "abstain",
        "description": "Query asks for current user count but context has 2022 data before the platform was rebranded to X",
        "rationale": "Pre-acquisition 2022 figures cannot reflect current user counts after platform transformation",
        "domain": "social_media",
        "query_type": "what",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1155",
        "difficulty": "medium",
        "subcategory": "outdated_context",
        "query": "Does the UK still follow EU food safety regulations?",
        "contexts": [
            "The European Union's food safety regulations require all member states to comply with maximum residue levels for pesticides, labeling standards, and traceability requirements. The UK participated in shaping these standards as a member state through the Food Standards Agency's collaboration with EFSA."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about current UK-EU regulatory alignment but context describes UK as an EU member state",
        "rationale": "Pre-Brexit regulatory participation does not indicate current post-Brexit status",
        "domain": "government",
        "query_type": "does",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1156",
        "difficulty": "medium",
        "subcategory": "outdated_context",
        "query": "Which streaming service has the most subscribers right now?",
        "contexts": [
            "As of Q4 2019, Netflix led the streaming market with approximately 167 million global subscribers. Disney+ had just launched in November 2019, reaching 10 million subscribers on its first day. Amazon Prime Video and Hulu rounded out the top four streaming platforms."
        ],
        "expected_mode": "abstain",
        "description": "Query asks for current subscriber leader but context is from late 2019",
        "rationale": "The 2019 streaming landscape has changed dramatically and cannot reflect current standings",
        "domain": "technology",
        "query_type": "which",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1157",
        "difficulty": "medium",
        "subcategory": "outdated_context",
        "query": "How much does a gallon of gas cost in the United States today?",
        "contexts": [
            "The average price of regular unleaded gasoline in the United States was $2.17 per gallon in April 2020. This represented the lowest gas prices in over a decade, driven by a collapse in global oil demand during the early stages of the COVID-19 pandemic."
        ],
        "expected_mode": "abstain",
        "description": "Query asks for today's gas prices but context provides April 2020 pandemic-era data",
        "rationale": "Pandemic-era gas prices from 2020 bear no relation to current fuel costs",
        "domain": "finance",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    # =========================================================================
    # WRONG_PRODUCT (3 cases: 1158-1160)
    # =========================================================================
    {
        "id": "t1_abstain_medium_1158",
        "difficulty": "medium",
        "subcategory": "wrong_product",
        "query": "What are the nutrition facts for Coca-Cola Zero Sugar?",
        "contexts": [
            "Pepsi Max is a zero-calorie cola beverage produced by PepsiCo. It contains aspartame and acesulfame potassium as artificial sweeteners. A 12-ounce can of Pepsi Max contains 69mg of caffeine, which is higher than regular Pepsi's 38mg."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about Coca-Cola Zero Sugar but context provides Pepsi Max nutritional information",
        "rationale": "Pepsi Max's formulation and nutrition data cannot answer questions about a competing product",
        "domain": "food",
        "query_type": "what",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1159",
        "difficulty": "medium",
        "subcategory": "wrong_product",
        "query": "How long does the Toyota Camry hybrid battery warranty last?",
        "contexts": [
            "The Honda Accord Hybrid features a 2.0-liter four-cylinder engine paired with two electric motors, producing 204 horsepower. Honda provides a battery warranty of 10 years or 150,000 miles for the Accord Hybrid's lithium-ion battery pack. The vehicle achieves an EPA-estimated 48 mpg combined."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about Toyota Camry battery warranty but context covers Honda Accord Hybrid",
        "rationale": "Honda Accord warranty terms do not apply to or predict Toyota Camry warranty coverage",
        "domain": "transportation",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1160",
        "difficulty": "medium",
        "subcategory": "wrong_product",
        "query": "Is the PlayStation 5 backward compatible with PS3 games?",
        "contexts": [
            "The Xbox Series X supports backward compatibility with a large library of Xbox One, Xbox 360, and original Xbox games. Microsoft's backward compatibility program uses emulation technology to run older titles, with some games receiving enhanced resolution and frame rate improvements on the newer hardware."
        ],
        "expected_mode": "abstain",
        "description": "Query asks about PlayStation 5 backward compatibility but context covers Xbox backward compatibility",
        "rationale": "Xbox backward compatibility features cannot determine PlayStation 5's compatibility with PS3 titles",
        "domain": "technology",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    # =========================================================================
    # CROSS_DOMAIN_INSUFFICIENT (3 cases: 1161-1163)
    # =========================================================================
    {
        "id": "t1_abstain_medium_1161",
        "difficulty": "medium",
        "subcategory": "cross_domain_insufficient",
        "query": "Should schools teach financial literacy as a required course?",
        "contexts": [
            "A 2024 survey found that 56% of American adults could not cover an unexpected $1,000 expense from savings. The average credit card debt per household reached $7,951, and student loan debt surpassed $1.77 trillion nationally.",
            "Finland's education system ranks among the best globally, with high scores in PISA assessments for reading, science, and mathematics. Finnish schools emphasize student well-being, small class sizes, and teacher autonomy."
        ],
        "context_sources": [
            {"source_id": "fed_reserve_survey_2024", "source_type": "government_report", "authority": "primary"},
            {"source_id": "oecd_education_review_2024", "source_type": "international_org", "authority": "secondary"}
        ],
        "expected_mode": "abstain",
        "description": "Query asks about financial literacy in schools but contexts cover separate financial and educational data",
        "rationale": "Household debt statistics and Finnish education rankings do not evaluate whether financial literacy should be required",
        "domain": "education",
        "query_type": "should",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "evaluative",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1162",
        "difficulty": "medium",
        "subcategory": "cross_domain_insufficient",
        "query": "How does urban farming address food desert problems?",
        "contexts": [
            "Urban farming initiatives have grown in cities like Detroit, Chicago, and Philadelphia. These projects convert vacant lots into productive growing spaces, using raised beds, hydroponics, and vertical farming techniques.",
            "Food deserts are defined by the USDA as census tracts where at least one-third of the population lives more than one mile from a supermarket in urban areas. Over 23 million Americans live in food deserts."
        ],
        "context_sources": [
            {"source_id": "urban_ag_report_2024", "source_type": "research_report", "authority": "secondary"},
            {"source_id": "usda_food_access_atlas", "source_type": "government_data", "authority": "primary"}
        ],
        "expected_mode": "abstain",
        "description": "Query asks how urban farming solves food deserts but contexts describe each independently without linking them",
        "rationale": "Separate descriptions of urban farming and food desert definitions do not demonstrate the causal connection",
        "domain": "agriculture",
        "query_type": "how",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "causal",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1163",
        "difficulty": "medium",
        "subcategory": "cross_domain_insufficient",
        "query": "Does social media use by teenagers increase rates of clinical depression?",
        "contexts": [
            "Teenagers aged 13-17 spend an average of 4.8 hours per day on social media platforms. TikTok is the most popular platform among teens, followed by Snapchat and Instagram.",
            "The prevalence of major depressive episodes among adolescents aged 12-17 increased from 8.7% in 2005 to 15.7% in 2022 according to SAMHSA data. Female adolescents were disproportionately affected, with rates nearly three times higher than their male peers."
        ],
        "context_sources": [
            {"source_id": "pew_teen_survey_2024", "source_type": "research_survey", "authority": "primary"},
            {"source_id": "samhsa_nsduh_2022", "source_type": "government_data", "authority": "primary"}
        ],
        "expected_mode": "abstain",
        "description": "Query asks about causal link but contexts provide usage stats and depression rates independently",
        "rationale": "Correlation between rising screen time and depression rates does not establish the causal relationship the query asks about",
        "domain": "psychology",
        "query_type": "does",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "causal",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    # =========================================================================
    # DECOY_KEYWORDS (3 cases: 1164-1166)
    # =========================================================================
    {
        "id": "t1_abstain_medium_1164",
        "difficulty": "medium",
        "subcategory": "decoy_keywords",
        "query": "What is the current interest rate on Apple's corporate bonds?",
        "contexts": [
            "Apple Inc. reported record-breaking revenue of $394 billion in fiscal year 2024. The company holds approximately $162 billion in cash and marketable securities. Apple's stock price reached an all-time high, and the company continued its share buyback program worth over $90 billion."
        ],
        "expected_mode": "abstain",
        "description": "Context mentions Apple and financial figures but not corporate bond interest rates",
        "rationale": "Revenue, cash reserves, and stock buybacks are not bond interest rate data",
        "domain": "finance",
        "query_type": "what",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1165",
        "difficulty": "medium",
        "subcategory": "decoy_keywords",
        "query": "How effective is crop rotation for controlling corn rootworm?",
        "contexts": [
            "Crop rotation is a fundamental agricultural practice where different crops are planted in the same field in sequential seasons. Common rotation patterns include corn-soybean in the Midwest and wheat-canola in the Northern Plains. Rotation helps maintain soil nitrogen levels and reduces erosion."
        ],
        "expected_mode": "abstain",
        "description": "Context discusses crop rotation generally but not its effectiveness against corn rootworm specifically",
        "rationale": "General soil health benefits of rotation do not address pest control effectiveness against corn rootworm",
        "domain": "agriculture",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "causal",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1166",
        "difficulty": "medium",
        "subcategory": "decoy_keywords",
        "query": "Who founded the social media platform Mastodon?",
        "contexts": [
            "The mastodon was a large prehistoric mammal related to modern elephants that lived during the Pleistocene epoch. American mastodons stood up to 10 feet tall and weighed around 6 tons. Their fossils have been found extensively across North America, with notable discoveries in New York, Indiana, and Michigan."
        ],
        "expected_mode": "abstain",
        "description": "Context discusses the prehistoric animal mastodon rather than the social media platform Mastodon",
        "rationale": "Paleontological information about the animal cannot answer who founded the software platform",
        "domain": "social_media",
        "query_type": "who",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    # =========================================================================
    # WRONG_GRANULARITY (2 cases: 1167-1168)
    # =========================================================================
    {
        "id": "t1_abstain_medium_1167",
        "difficulty": "medium",
        "subcategory": "wrong_granularity",
        "query": "What was the GDP growth rate of Vietnam in Q2 2024?",
        "contexts": [
            "Southeast Asia's combined GDP exceeded $3.6 trillion in 2024. The region's economic growth was driven by strong manufacturing exports, tourism recovery, and digital economy expansion. ASEAN economies collectively grew at an average rate of 4.7% in 2024, with Indonesia, Vietnam, and the Philippines as the fastest-growing members."
        ],
        "expected_mode": "abstain",
        "description": "Query asks for Vietnam's Q2 2024 GDP growth but context gives regional annual aggregates",
        "rationale": "ASEAN regional averages do not provide Vietnam's specific quarterly growth rate",
        "domain": "finance",
        "query_type": "what",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1168",
        "difficulty": "medium",
        "subcategory": "wrong_granularity",
        "query": "How many murders occurred in Chicago in December 2024?",
        "contexts": [
            "The United States recorded approximately 21,000 homicides in 2023, according to FBI Uniform Crime Report data. Violent crime declined nationally by approximately 6% compared to 2022. Major cities saw varied trends, with some experiencing decreases while others reported increases."
        ],
        "expected_mode": "abstain",
        "description": "Query asks for Chicago-specific December 2024 murders but context provides national 2023 annual totals",
        "rationale": "National homicide totals for a different year cannot give city-specific monthly counts",
        "domain": "law",
        "query_type": "how",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    # =========================================================================
    # IMPLICIT_ONLY (2 cases: 1169-1170)
    # =========================================================================
    {
        "id": "t1_abstain_medium_1169",
        "difficulty": "medium",
        "subcategory": "implicit_only",
        "query": "Is it safe to swim in the Ganges River?",
        "contexts": [
            "The Ganges River stretches over 1,560 miles from the Himalayas to the Bay of Bengal. Over 400 million people live in the Ganges basin. The river is considered sacred in Hinduism, and millions participate in ritual bathing during festivals. Industrial effluent from over 700 factories is discharged into the river, along with untreated sewage from major cities."
        ],
        "expected_mode": "abstain",
        "description": "Context implies pollution but never directly states whether swimming is safe or unsafe",
        "rationale": "Industrial discharge and sewage facts suggest hazards but do not explicitly evaluate swimming safety",
        "domain": "environment",
        "query_type": "is",
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "evaluative",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
    {
        "id": "t1_abstain_medium_1170",
        "difficulty": "medium",
        "subcategory": "implicit_only",
        "query": "Should I buy a house in this current real estate market?",
        "contexts": [
            "Median home prices in the United States reached $420,000 in mid-2024, up 4% year-over-year. Mortgage rates for a 30-year fixed loan hovered around 6.8%. Housing inventory remained tight at 3.7 months of supply, well below the 6-month threshold that typically indicates a balanced market. First-time homebuyers accounted for only 26% of purchases, near historic lows.",
            "Home builders started approximately 1.35 million new housing units in 2024, slightly below the pace needed to meet demand according to the National Association of Home Builders."
        ],
        "context_sources": [
            {"source_id": "nar_housing_report_2024", "source_type": "industry_report", "authority": "primary"},
            {"source_id": "nahb_construction_data_2024", "source_type": "industry_data", "authority": "secondary"}
        ],
        "expected_mode": "abstain",
        "description": "Context provides market data but never gives an explicit buy or wait recommendation",
        "rationale": "Market statistics alone do not constitute a personalized buy recommendation",
        "domain": "real_estate",
        "query_type": "should",
        "source_type": "multi_source",
        "context_count": 2,
        "reasoning_type": "evaluative",
        "evidence_pattern": "absent",
        "category": "abstention",
        "evaluation_config": {"mode": "governance", "check_mode_match": True}
    },
]


def main():
    # Load existing data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_cases = data["cases"]
    existing_ids = {c["id"] for c in existing_cases}
    existing_queries = {c["query"].lower().strip() for c in existing_cases}

    # Validate new cases
    print(f"Existing cases: {len(existing_cases)}")
    print(f"New cases to add: {len(NEW_CASES)}")

    # Check for ID collisions
    new_ids = {c["id"] for c in NEW_CASES}
    id_collisions = new_ids & existing_ids
    if id_collisions:
        raise ValueError(f"ID collisions: {id_collisions}")

    # Check for query duplicates
    new_queries = {c["query"].lower().strip() for c in NEW_CASES}
    query_dupes = new_queries & existing_queries
    if query_dupes:
        raise ValueError(f"Duplicate queries: {query_dupes}")

    # Validate ID range
    for c in NEW_CASES:
        num = int(c["id"].split("_")[-1])
        assert 1111 <= num <= 1170, f"ID {c['id']} out of range"

    # Validate all required fields
    required_fields = [
        "id", "difficulty", "subcategory", "query", "contexts",
        "expected_mode", "description", "rationale", "domain",
        "query_type", "source_type", "context_count", "reasoning_type",
        "evidence_pattern", "category", "evaluation_config",
    ]
    for c in NEW_CASES:
        for field in required_fields:
            assert field in c, f"Missing field '{field}' in case {c['id']}"
        assert c["difficulty"] == "medium", f"Wrong difficulty in {c['id']}"
        assert c["expected_mode"] == "abstain", f"Wrong mode in {c['id']}"
        assert c["category"] == "abstention", f"Wrong category in {c['id']}"

    # Validate multi_source cases have context_sources
    ms_cases = [c for c in NEW_CASES if c["source_type"] == "multi_source"]
    for c in ms_cases:
        assert "context_sources" in c, f"Multi-source case {c['id']} missing context_sources"

    # Print distribution stats
    from collections import Counter

    subcats = Counter(c["subcategory"] for c in NEW_CASES)
    print("\nSubcategory distribution:")
    for s, cnt in sorted(subcats.items(), key=lambda x: -x[1]):
        print(f"  {s}: {cnt}")

    domains = Counter(c["domain"] for c in NEW_CASES)
    print(f"\nDomain distribution ({len(domains)} domains):")
    for d, cnt in sorted(domains.items(), key=lambda x: -x[1]):
        flag = " *** OVER LIMIT" if cnt > 5 else ""
        print(f"  {d}: {cnt}{flag}")

    query_types = Counter(c["query_type"] for c in NEW_CASES)
    print("\nQuery type distribution:")
    for q, cnt in sorted(query_types.items(), key=lambda x: -x[1]):
        print(f"  {q}: {cnt}")

    print(f"\nMulti-source cases: {len(ms_cases)}")

    # Context length validation
    for c in NEW_CASES:
        for i, ctx in enumerate(c["contexts"]):
            length = len(ctx)
            if length < 150 or length > 400:
                print(f"  WARNING: {c['id']} context[{i}] length={length} (target: 150-400)")

    # Append and write
    data["cases"].extend(NEW_CASES)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nDone. Total cases now: {len(data['cases'])}")


if __name__ == "__main__":
    main()
