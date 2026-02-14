"""
Final comprehensive dedup: rewrite all duplicate queries into unique new cases.

Strategy:
- For within-category dupes: keep the first, rewrite the rest with new queries
- For cross-category dupes: keep the one in the "primary" category, rewrite in "secondary"
- All rewrites maintain same subcategory, difficulty, expected_mode, domain, evaluation_config
- Only the query and contexts are rewritten to be genuinely new

Categories of fixes:
1. 47 excess within abstention (14 dupe groups)
2. 2 excess within dispute (2 dupe groups)
3. 1 excess within trustworthy_direct (1 dupe group)
4. 23 cross-category dupe groups (rewrite the "secondary" in each pair)
"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# ── WITHIN-CATEGORY REWRITES ──
# For each group, the first ID is kept; the rest get new queries.
# Each rewrite: (case_id, new_query, new_contexts)

ABSTENTION_REWRITES = {
    # Group 1: "How are the specific ingredients in the new household cleaning product?" (9x, keep 113)
    "t1_abstain_hard_114": {
        "query": "What specific compounds are used in the new industrial adhesive formulation?",
        "contexts": [
            "GripBond Industries announced a new industrial adhesive line in Q3 2024. The product targets automotive and aerospace applications requiring high-temperature resistance up to 400°F. Initial orders from three major manufacturers exceeded projections by 60%, with full production scaling expected in early 2025."
        ],
    },
    "t1_abstain_hard_115": {
        "query": "What are the active ingredients in the new organic pest control spray?",
        "contexts": [
            "GreenShield Organics received EPA registration for their new pest control spray targeting home garden use. The product was developed over 18 months at their Portland research facility. Field trials across six climate zones showed 89% effectiveness against common aphids and whiteflies."
        ],
    },
    "t1_abstain_hard_116": {
        "query": "What preservatives are used in the reformulated children's cough syrup?",
        "contexts": [
            "PediCare Pharmaceuticals reformulated their children's cough syrup in response to parent concerns about artificial additives. The new version launched in 2,400 pharmacies nationwide. Clinical trials with 350 pediatric patients showed comparable efficacy to the previous formulation with improved taste ratings."
        ],
    },
    "t1_abstain_hard_117": {
        "query": "What materials compose the new biodegradable food packaging?",
        "contexts": [
            "EcoPack Solutions unveiled their biodegradable food packaging at the 2024 Sustainable Packaging Conference. The packaging decomposes within 90 days in commercial composting facilities. Three major restaurant chains have signed pilot agreements to test the product in their takeout operations."
        ],
    },
    "t1_abstain_hard_1125": {
        "query": "What specific nutrients are in the new fortified breakfast cereal?",
        "contexts": [
            "NutriStart Foods launched a fortified breakfast cereal aimed at children ages 4-12. The product was developed in partnership with the Children's Nutrition Research Center. Market research indicated strong parent interest in healthier breakfast options, with 78% of surveyed parents willing to pay a premium."
        ],
    },
    "t1_abstain_hard_1149": {
        "query": "What chemical additives are in the new fire-resistant building insulation?",
        "contexts": [
            "SafeHome Materials introduced a fire-resistant insulation product at the International Building Materials Expo. The insulation achieved a Class A fire rating in independent testing by Underwriters Laboratories. Several state building codes are being updated to require enhanced fire resistance in residential construction."
        ],
    },
    "t1_abstain_hard_1173": {
        "query": "What dyes and colorants are used in the new textile printing ink?",
        "contexts": [
            "ChromaPrint launched a new textile ink system compatible with major industrial printers. The company claims the inks produce 40% more vibrant colors than competing products. Fashion brands including two luxury houses have begun sampling the inks for their Spring 2025 collections."
        ],
    },
    "t1_abstain_hard_1174": {
        "query": "What essential oils are blended in the new aromatherapy diffuser product?",
        "contexts": [
            "WellnessAir released a premium aromatherapy diffuser system with proprietary scent cartridges. The product was endorsed by the International Aromatherapy Association and has sold over 50,000 units since launch. Customer reviews cite improved sleep quality and reduced stress levels."
        ],
    },

    # Group 2: "How were the specific terms of the Treaty of Tordesillas in 1494?" (6x, keep 118)
    "t1_abstain_hard_123": {
        "query": "What were the specific articles of the Edict of Nantes in 1598?",
        "contexts": [
            "The Edict of Nantes, issued by Henry IV of France, is widely regarded as a landmark in religious tolerance. It ended the French Wars of Religion, which had devastated the country for over three decades. Henry IV's conversion to Catholicism in 1593 was a prerequisite for his acceptance as king by the Catholic majority."
        ],
    },
    "t1_abstain_hard_125": {
        "query": "What were the precise boundary provisions of the Treaty of Zaragoza in 1529?",
        "contexts": [
            "The Treaty of Zaragoza was signed between Spain and Portugal as a companion agreement to earlier colonial treaties. It resolved competing claims in the Pacific region. Spain received a payment of 350,000 ducats as part of the arrangement, which was a substantial sum at the time."
        ],
    },
    "t1_abstain_hard_126": {
        "query": "What were the detailed surrender conditions in the Treaty of Ghent in 1814?",
        "contexts": [
            "The Treaty of Ghent ended the War of 1812 between the United States and Great Britain. Negotiations took place in the city of Ghent in modern-day Belgium. Both American and British delegations included prominent political figures of the era."
        ],
    },
    "t1_abstain_hard_127": {
        "query": "What were the specific reparation amounts stipulated in the Treaty of Frankfurt in 1871?",
        "contexts": [
            "The Treaty of Frankfurt ended the Franco-Prussian War and led to the creation of the German Empire. The treaty was negotiated primarily by Otto von Bismarck. France lost the provinces of Alsace and most of Lorraine, a loss that would fuel resentment for decades."
        ],
    },
    "t1_abstain_hard_1176": {
        "query": "What were the territorial concessions defined in the Treaty of Brest-Litovsk in 1918?",
        "contexts": [
            "The Treaty of Brest-Litovsk was signed between Soviet Russia and the Central Powers. It allowed Russia to exit World War I, fulfilling one of the Bolsheviks' key promises. The treaty was later annulled following Germany's defeat in November 1918."
        ],
    },

    # Group 3: "How is the average closing cost percentage for US homebuyers?" (6x, keep 129)
    "t1_abstain_hard_130": {
        "query": "What is the average mortgage origination fee for commercial real estate loans?",
        "contexts": [
            "Commercial real estate lending saw record volumes in 2024, driven by strong demand for industrial and logistics properties. Major banks expanded their commercial lending divisions, hiring over 2,000 loan officers nationally. The sector benefited from declining vacancy rates in prime industrial corridors."
        ],
    },
    "t1_abstain_hard_131": {
        "query": "What is the typical escrow deposit percentage for luxury home purchases?",
        "contexts": [
            "The luxury home market above $5 million saw a 12% increase in transactions in 2024. International buyers accounted for 23% of luxury purchases in major metros. Miami, Los Angeles, and New York remained the top three markets by transaction volume."
        ],
    },
    "t1_abstain_hard_132": {
        "query": "What is the average title insurance premium for a $500,000 home purchase?",
        "contexts": [
            "Title insurance protects buyers and lenders against potential ownership disputes. The industry processes over 1.5 million policies annually in the United States. Digital transformation has reduced the average closing timeline from 45 to 32 days for residential transactions."
        ],
    },
    "t1_abstain_hard_133": {
        "query": "What is the standard inspection contingency period for residential sales in Texas?",
        "contexts": [
            "Texas residential real estate transactions are governed by the Texas Real Estate Commission (TREC). Standard forms are updated annually to reflect legislative changes. Licensed inspectors must complete 194 hours of qualifying education and pass the state examination."
        ],
    },
    "t1_abstain_hard_134": {
        "query": "What is the average property tax rate for single-family homes in Cook County, Illinois?",
        "contexts": [
            "Cook County, Illinois, underwent a comprehensive property reassessment in 2024. The county assessor's office processes valuations for over 1.8 million parcels. Appeals of assessed values can be filed with the Cook County Board of Review within 30 days of receiving the assessment notice."
        ],
    },

    # Group 4: "Why many electoral votes does California have?" (6x, keep 138)
    "t1_abstain_hard_140": {
        "query": "How many delegates does New Hampshire send to the national party conventions?",
        "contexts": [
            "New Hampshire holds the first-in-the-nation primary election, a tradition dating back to 1920. The state's small size allows candidates to engage in retail politics, meeting voters at diners and town halls. The primary's predictive value has been debated by political scientists, with mixed results over the past five decades."
        ],
    },
    "t1_abstain_hard_143": {
        "query": "How many Senate-confirmed positions exist in the federal executive branch?",
        "contexts": [
            "The Senate confirmation process has become increasingly contentious in recent decades. The average confirmation time for presidential nominees has tripled since the 1980s. Recess appointments have been used by multiple administrations to bypass lengthy confirmation delays."
        ],
    },
    "t1_abstain_hard_144": {
        "query": "How many federal judicial vacancies currently exist in the circuit courts?",
        "contexts": [
            "The federal judiciary comprises 13 circuit courts of appeals and 94 district courts. Judicial appointments are lifetime positions under Article III of the Constitution. The Judicial Conference of the United States periodically recommends the creation of new judgeships to manage growing caseloads."
        ],
    },
    "t1_abstain_hard_145": {
        "query": "How many lobbying firms are registered to operate in Washington, D.C.?",
        "contexts": [
            "Washington, D.C. is home to a vast lobbying industry that influences federal legislation. The Lobbying Disclosure Act of 1995 established registration requirements for lobbyists. K Street has become synonymous with the lobbying industry, though many firms have relocated to other areas of the capital."
        ],
    },
    "t1_abstain_hard_146": {
        "query": "How many executive orders has the current administration issued in its first year?",
        "contexts": [
            "Executive orders are directives issued by the President to manage operations of the federal government. Their use has varied significantly across administrations. The legal authority for executive orders derives from Article II of the Constitution and specific statutory delegations."
        ],
    },

    # Group 5: "How temperature should chicken be cooked to for safe consumption?" (5x, keep 148)
    "t1_abstain_hard_149": {
        "query": "What is the safe minimum cooking temperature for wild game meats?",
        "contexts": [
            "Wild game hunting is regulated by state wildlife agencies across the United States. The processing of game meat must follow USDA guidelines for sanitation. Hunter education courses cover field dressing techniques and proper meat handling to prevent contamination during transport."
        ],
    },
    "t1_abstain_hard_201": {
        "query": "What is the recommended internal temperature for reheating leftover casseroles?",
        "contexts": [
            "Food safety in leftovers management is a growing concern for public health agencies. The CDC estimates 48 million Americans experience foodborne illness annually. Proper refrigeration within two hours of cooking is emphasized in food safety education programs."
        ],
    },
    "t1_abstain_hard_204": {
        "query": "What temperature should smoked salmon reach during the hot-smoking process?",
        "contexts": [
            "Salmon smoking is both a culinary tradition and a food preservation method dating back centuries. Pacific Northwest tribes developed sophisticated smoking techniques long before European contact. Modern commercial smoking operations use computerized kilns to ensure consistent flavor profiles."
        ],
    },
    "t1_abstain_hard_209": {
        "query": "What is the safe holding temperature for buffet-style food service?",
        "contexts": [
            "Buffet-style food service is popular in hotels, conferences, and catering operations. The National Restaurant Association provides guidelines for food presentation and service flow. Customer satisfaction surveys indicate that food variety is the most valued aspect of buffet dining."
        ],
    },

    # Group 6: "How is the statute of limitations for medical malpractice in California?" (5x, keep 210)
    "t1_abstain_hard_211": {
        "query": "What is the cap on punitive damages in product liability cases in Ohio?",
        "contexts": [
            "Ohio's tort reform legislation has been updated multiple times since the early 2000s. Product liability claims in Ohio must establish that the product was defective when it left the manufacturer's control. The state follows a modified comparative fault standard for determining damages."
        ],
    },
    "t1_abstain_hard_212": {
        "query": "What is the filing deadline for workers' compensation claims in New York?",
        "contexts": [
            "New York's workers' compensation system covers most private-sector employees. The Workers' Compensation Board adjudicates disputes between injured workers and employers. Medical providers must be authorized by the Board to treat workers' compensation patients."
        ],
    },
    "t1_abstain_hard_214": {
        "query": "What is the mandatory waiting period for divorce proceedings in Illinois?",
        "contexts": [
            "Illinois family law underwent significant reform with the Marriage and Dissolution of Marriage Act. The state adopted no-fault divorce provisions, eliminating the need to prove specific grounds. Mediation is increasingly encouraged as an alternative to contested litigation in custody disputes."
        ],
    },
    "t1_abstain_hard_215": {
        "query": "What is the maximum penalty for first-offense DUI in Pennsylvania?",
        "contexts": [
            "Pennsylvania's DUI enforcement program includes sobriety checkpoints authorized under state law. The state operates an Accelerated Rehabilitative Disposition program for first-time offenders. Ignition interlock requirements have expanded under recent legislative amendments."
        ],
    },

    # Group 7: "How was the final score of the 2022 World Cup final?" (4x, keep 216)
    "t1_abstain_hard_218": {
        "query": "What was the attendance figure for the 2024 Paris Olympics opening ceremony?",
        "contexts": [
            "The 2024 Paris Olympics featured a groundbreaking opening ceremony along the Seine River. Security operations involved over 45,000 police and military personnel. The ceremony showcased French cultural heritage through elaborate artistic performances."
        ],
    },
    "t1_abstain_hard_219": {
        "query": "What was the TV viewership for the 2024 Super Bowl halftime show?",
        "contexts": [
            "The Super Bowl remains the most-watched annual television event in the United States. Advertising rates have increased consistently over the past two decades. The halftime show has evolved from simple marching band performances to elaborate productions featuring global music stars."
        ],
    },
    "t1_abstain_hard_220": {
        "query": "What was the prize money distribution at the 2024 Wimbledon Championships?",
        "contexts": [
            "Wimbledon, the oldest tennis tournament in the world, has been held at the All England Club since 1877. The tournament maintains its tradition of grass courts and all-white dress codes. The 2024 event saw record attendance across the fortnight of play."
        ],
    },

    # Group 8: "How is the maximum speed of the Shinkansen bullet train?" (4x, keep 250)
    "t1_abstain_hard_255": {
        "query": "What is the passenger capacity of the Airbus A380 in standard configuration?",
        "contexts": [
            "The Airbus A380, the world's largest passenger aircraft, entered service in 2007. Production ceased in 2021 after 251 deliveries. Emirates remains the largest operator of the type, using it extensively on high-density routes between Dubai and major global hubs."
        ],
    },
    "t1_abstain_hard_256": {
        "query": "What is the cruising speed of the Maersk Triple-E class container ships?",
        "contexts": [
            "The Triple-E class represents Maersk's commitment to efficient large-scale container shipping. These vessels can carry over 18,000 twenty-foot equivalent units. The class was designed with a twin-skeg hull form that reduces fuel consumption compared to previous generations."
        ],
    },
    "t1_abstain_hard_258": {
        "query": "What is the top speed of the Hennessey Venom F5 hypercar?",
        "contexts": [
            "The Hennessey Venom F5 is an American hypercar designed to challenge established European manufacturers. The vehicle features a twin-turbocharged V8 engine developed entirely in-house. Only 24 units were planned for production, each customized to the buyer's specifications."
        ],
    },

    # Group 9: "How is the success rate of CBT for treating PTSD?" (3x, keep 259)
    "t1_abstain_hard_604": {
        "query": "What is the remission rate for exposure therapy in treating specific phobias?",
        "contexts": [
            "Specific phobias affect approximately 12% of the adult population at some point in their lives. The development of virtual reality technology has opened new avenues for therapeutic intervention. Research institutions across Europe and North America have established dedicated anxiety treatment centers."
        ],
    },
    "t1_abstain_hard_606": {
        "query": "What is the efficacy rate of dialectical behavior therapy for borderline personality disorder?",
        "contexts": [
            "Borderline personality disorder presents significant treatment challenges for mental health professionals. The disorder is characterized by emotional dysregulation, unstable relationships, and identity disturbance. Training programs for therapists specializing in personality disorders have expanded in recent years."
        ],
    },

    # Group 10: "How algorithm changes did YouTube make in 2023?" (3x, keep 607)
    "t1_abstain_hard_608": {
        "query": "What content moderation policy changes did TikTok implement in 2024?",
        "contexts": [
            "TikTok's global user base surpassed 1.5 billion monthly active users in 2024. The platform has invested heavily in creator monetization tools and e-commerce features. Regulatory scrutiny of TikTok's data practices has intensified in multiple countries."
        ],
    },
    "t1_abstain_hard_609": {
        "query": "What changes to its news feed ranking algorithm did Facebook announce in 2024?",
        "contexts": [
            "Meta's Facebook platform continues to evolve its approach to content distribution. The company has shifted significant engineering resources toward AI-powered content recommendations. User engagement patterns have changed substantially with the rise of short-form video content."
        ],
    },

    # Group 11: "How is the average employee turnover rate in tech?" (3x, keep 610)
    "t1_abstain_hard_704": {
        "query": "What is the average time-to-hire for senior engineering positions at Fortune 500 companies?",
        "contexts": [
            "Fortune 500 companies have significantly expanded their technical hiring operations in recent years. Many have established dedicated engineering campuses and innovation labs. Competition for senior engineering talent has led to creative benefits packages including remote work options and sabbatical programs."
        ],
    },
    "t1_abstain_hard_705": {
        "query": "What is the median tenure of C-suite executives in the healthcare industry?",
        "contexts": [
            "Healthcare executive leadership has faced unprecedented challenges in recent years. Hospital systems have consolidated rapidly, creating larger organizational structures. Executive coaching and leadership development programs have become standard investments for major healthcare systems."
        ],
    },

    # Group 12: "How percentage of ocean plastic comes from fishing equipment?" (3x, keep 706)
    "t1_abstain_hard_802": {
        "query": "What fraction of microplastics in drinking water comes from tire wear particles?",
        "contexts": [
            "Microplastics research has expanded rapidly as detection methods have improved. Studies have identified plastic particles in water sources across all seven continents. International cooperation on plastic pollution has increased through various UN-sponsored initiatives."
        ],
    },
    "t1_abstain_hard_805": {
        "query": "What percentage of marine biodiversity loss is attributed to deep-sea trawling?",
        "contexts": [
            "Marine biodiversity conservation has become a priority for international environmental organizations. The establishment of marine protected areas has accelerated in the past decade. Advances in underwater monitoring technology have improved our understanding of deep-ocean ecosystems."
        ],
    },

    # Group 13: "What is the recommended daily intake of vitamin D for adults?" (2x, keep 112)
    "t1_abstain_medium_917": {
        "query": "What is the recommended daily intake of omega-3 fatty acids for pregnant women?",
        "contexts": [
            "Prenatal nutrition research has expanded significantly in the past decade. The American College of Obstetricians and Gynecologists publishes guidelines for nutrition during pregnancy. Fish consumption during pregnancy has been a topic of debate due to concerns about mercury exposure."
        ],
    },

    # Group 14: "How is the optimal soil pH for growing blueberries?" (2x, keep 806)
    "t1_abstain_hard_809": {
        "query": "What is the ideal nitrogen application rate for commercial strawberry cultivation?",
        "contexts": [
            "Commercial strawberry production in the United States is concentrated in California and Florida. Sustainable farming practices have gained traction among strawberry growers seeking organic certification. Drip irrigation systems have improved water use efficiency in strawberry fields by up to 30%."
        ],
    },
}

# Within-dispute rewrites
DISPUTE_REWRITES = {
    # "Is breakfast the most important meal of the day?" (keep 025, rewrite 734)
    "t1_dispute_hard_734": {
        "query": "Does eating organic food significantly reduce cancer risk?",
        "contexts": [
            "A 2023 longitudinal study published in the British Journal of Nutrition tracked 68,946 participants over 7 years and found that frequent organic food consumers had a 25% lower overall cancer risk, with particularly strong reductions in non-Hodgkin lymphoma and postmenopausal breast cancer.",
            "A comprehensive 2024 meta-analysis in the Annals of Internal Medicine reviewing 240 studies concluded that organic foods show no clinically meaningful difference in health outcomes compared to conventional foods, noting that the cancer risk reduction in observational studies disappears when controlling for lifestyle factors."
        ],
    },
    # "Does social media use cause depression in teenagers?" (keep hard_208, rewrite medium_608)
    "t1_dispute_medium_608": {
        "query": "Does screen time before bed impair sleep quality in school-age children?",
        "contexts": [
            "A controlled study at the University of Colorado involving 234 children ages 8-12 found that one hour of tablet use before bedtime reduced total sleep duration by 28 minutes and delayed sleep onset by 37 minutes compared to book reading, with measurable decreases in REM sleep duration.",
            "A 2024 systematic review in the Journal of Sleep Research, analyzing 18 randomized controlled trials, found no consistent evidence that moderate screen use (under 90 minutes) before bed affects objective sleep measures in children, suggesting that content type and arousal level matter more than screen exposure itself."
        ],
    },
}

# Within-trustworthy_direct rewrites
DIRECT_REWRITES = {
    # "How does CRISPR-Cas9 gene editing work?" (keep 753, rewrite 867)
    "t1_confident_hard_867": {
        "query": "How does mRNA vaccine technology produce an immune response?",
        "contexts": [
            "mRNA vaccines work by delivering synthetic messenger RNA into cells, which instructs cellular ribosomes to produce a specific protein antigen—in the case of COVID-19 vaccines, the spike protein of SARS-CoV-2. The immune system recognizes this protein as foreign and mounts both an antibody response and a T-cell response. The mRNA does not enter the cell nucleus or interact with DNA, and is degraded by normal cellular processes within 48-72 hours. Lipid nanoparticles serve as the delivery mechanism, protecting the fragile mRNA molecule during injection and facilitating cellular uptake.",
            "According to the National Institute of Allergy and Infectious Diseases, the mRNA platform enables rapid vaccine development because only the genetic sequence of the target antigen is needed, not the actual pathogen. Clinical trials by Pfizer-BioNTech and Moderna demonstrated 94-95% efficacy in preventing symptomatic COVID-19 infection. The technology has been in development since the 1990s, with foundational work by Katalin Karikó and Drew Weissman on modified nucleosides proving critical to overcoming early inflammatory responses."
        ],
    },
}

# ── CROSS-CATEGORY REWRITES ──
# For each pair, keep the "primary" category's version, rewrite the "secondary"
# Primary priority: trustworthy_direct > dispute > trustworthy_hedged > abstention > grounding > relevance

CROSS_CATEGORY_REWRITES = {
    # "What is the speed of light in a vacuum?" — keep direct_107, rewrite abstention + grounding
    ("data/tier1_core/abstention.json", "t1_abstain_medium_916"): {
        "query": "What is the exact wavelength of the hydrogen alpha spectral line?",
        "contexts": [
            "Spectroscopy is a foundational tool in astrophysics, enabling the identification of chemical elements in distant stars. The hydrogen spectrum was first systematically described by Johann Balmer in 1885. Modern spectrographs can resolve spectral features with extraordinary precision."
        ],
    },
    ("data/tier1_core/grounding.json", "t1_grounding_hard_144"): {
        "query": "What is the gravitational constant G in SI units?",
        "contexts": [
            "The gravitational constant was first measured by Henry Cavendish in 1798 using a torsion balance. The accepted value is approximately 6.674 × 10⁻¹¹ N⋅m²/kg². Despite being one of the first constants measured, G remains the least precisely known fundamental constant due to the weakness of gravitational interactions at laboratory scales."
        ],
        "forbidden_claims": ["6\\.67[0-9]*\\s*×\\s*10⁻¹⁰", "6\\.67[0-9]*e-10", "Newton discovered"],
    },

    # "What programming languages does the API support?" — keep relevance_008, rewrite grounding_004
    ("data/tier0_sanity/grounding.json", "t0_grounding_easy_004"): {
        "query": "How many concurrent users can the platform handle?",
        "contexts": [
            "Our platform uses a microservices architecture deployed on AWS with auto-scaling enabled. Load balancing distributes traffic across multiple availability zones. The system has a 99.95% uptime SLA and supports both REST and GraphQL endpoints."
        ],
        "forbidden_claims": ["\\d{3,}\\s*(concurrent|simultaneous)", "handles?\\s+\\d+\\s*(million|thousand|K)\\s*(users|connections)", "up to \\d+"],
    },

    # "How many employees does the company have?" — keep direct_004, rewrite grounding_006
    ("data/tier0_sanity/grounding.json", "t0_grounding_easy_006"): {
        "query": "What is the company's annual revenue?",
        "contexts": [
            "The company was founded in 2015 and has grown to operate in 12 countries. It serves over 500 enterprise clients across the healthcare and financial services sectors. The company completed a Series D funding round of $150 million in 2023."
        ],
        "forbidden_claims": ["\\$\\d+\\s*(million|billion)\\s*(in\\s+)?revenue", "revenue (of|is|was) \\$", "annual revenue"],
    },

    # "What is the recommended dosage?" — keep relevance_005, rewrite grounding_005
    ("data/tier1_core/grounding.json", "t1_grounding_medium_005"): {
        "query": "What are the contraindications for this medication?",
        "contexts": [
            "PharmaCo's new medication received FDA approval in January 2024 for treating chronic migraines. The drug works by blocking CGRP receptors, reducing the frequency of migraine episodes by an average of 50% in clinical trials. It is administered as a monthly injection and is available through specialty pharmacies."
        ],
        "forbidden_claims": ["contraindicated in", "should not (be used|take)", "do not (use|take) if", "avoid if (you have|pregnant)"],
    },

    # "When was the company founded?" — keep direct_002, rewrite grounding_006
    ("data/tier1_core/grounding.json", "t1_grounding_medium_006"): {
        "query": "Who is the current CEO of the company?",
        "contexts": [
            "TechVision Inc. reported record quarterly earnings of $3.2 billion in Q3 2024, driven by strong demand for its AI-powered analytics platform. The company expanded its partnership with three Fortune 100 clients and opened a new research campus in Austin, Texas. Its stock price has appreciated 85% year-to-date."
        ],
        "forbidden_claims": ["CEO (is|was)\\s+\\w+", "led by\\s+\\w+", "founded by\\s+\\w+", "\\w+\\s+(serves?|is)\\s+(as\\s+)?CEO"],
    },

    # "Who invented the telephone?" — keep direct_006, rewrite dispute_633
    ("data/tier1_core/dispute.json", "t1_dispute_medium_633"): {
        "query": "Who first discovered the New World — the Vikings or Columbus?",
        "contexts": [
            "Archaeological evidence at L'Anse aux Meadows in Newfoundland conclusively demonstrates Norse presence in North America around 1000 CE, approximately 500 years before Columbus's 1492 voyage. The site, excavated by Helge and Anne Stine Ingstad in the 1960s, contained Norse artifacts including a bronze ring-headed pin.",
            "While the Vikings may have briefly visited North America, Columbus's 1492 voyage established the first permanent and sustained contact between Europe and the Americas. His expeditions led to the Columbian Exchange and fundamentally transformed both hemispheres, making his the truly significant discovery."
        ],
    },

    # "What is the population of Tokyo?" — keep direct_845, rewrite abstention_004
    ("data/tier1_core/abstention.json", "t1_abstain_medium_004"): {
        "query": "What is the population density of Monaco?",
        "contexts": [
            "Monaco is the second-smallest country in the world by area, covering approximately 2.02 square kilometers. It is located on the French Riviera and is famous for the Monte Carlo Casino and the annual Formula 1 Grand Prix. The principality has no income tax, attracting wealthy residents from around the world."
        ],
    },

    # "How much water does it take to produce one pound of beef?" — keep dispute_568, rewrite abstention_1087
    ("data/tier1_core/abstention.json", "t1_abstain_hard_1087"): {
        "query": "How many gallons of water are needed to produce one pound of almonds?",
        "contexts": [
            "California's Central Valley is the largest almond-producing region in the world, accounting for over 80% of global supply. Almond orchards require irrigation in the Mediterranean climate of the valley. Recent droughts have prompted growers to adopt more efficient micro-drip irrigation systems."
        ],
    },

    # "What is the half-life of carbon-14?" — keep direct_106, rewrite abstention_1089
    ("data/tier1_core/abstention.json", "t1_abstain_hard_1089"): {
        "query": "What is the decay rate of potassium-40 in volcanic rock samples?",
        "contexts": [
            "Potassium-argon dating is widely used in geochronology for dating volcanic rocks and minerals. The technique has been instrumental in establishing the geological time scale. Volcanic eruptions in the East African Rift Valley have been dated using this method, contributing to our understanding of early human evolution."
        ],
    },

    # "What is the deforestation rate in the Brazilian Amazon?" — keep dispute_552, rewrite hedged_334
    ("data/tier1_core/trustworthy_hedged.json", "t1_qualify_hard_334"): {
        "query": "What is the rate of coral reef degradation in the Great Barrier Reef?",
        "contexts": [
            "The Australian Institute of Marine Science reported that coral cover on surveyed reefs reached a 36-year high in 2022, with recovery driven by fast-growing Acropora corals. However, the institute cautioned that Acropora corals are highly susceptible to bleaching, cyclones, and crown-of-thorns starfish outbreaks.",
            "A 2024 study in Nature Climate Change found that marine heatwaves have caused five mass bleaching events on the Great Barrier Reef since 2016, with the 2024 event being the most geographically widespread. Approximately 73% of surveyed reefs showed some level of bleaching."
        ],
    },

    # "What percentage of global electricity comes from renewable sources?" — keep dispute_584, rewrite hedged_137
    ("data/tier1_core/trustworthy_hedged.json", "t1_qualify_medium_137"): {
        "query": "What share of new vehicle sales are electric vehicles globally?",
        "contexts": [
            "The International Energy Agency reported that electric vehicle sales reached 14 million units in 2023, representing approximately 18% of all new car sales globally. China accounted for 60% of global EV sales, followed by Europe at 25%.",
            "However, EV adoption rates vary dramatically by region. While Norway exceeded 80% EV share of new sales, markets like India, Southeast Asia, and Africa remained below 2%. The IEA noted that without further policy support, global EV market share could plateau at around 25% by 2030."
        ],
    },

    # "Does creatine supplementation improve athletic performance?" — keep dispute_595, rewrite hedged_131
    ("data/tier1_core/trustworthy_hedged.json", "t1_qualify_medium_131"): {
        "query": "Does beta-alanine supplementation enhance endurance exercise capacity?",
        "contexts": [
            "A meta-analysis of 40 studies in the Journal of the International Society of Sports Nutrition found that beta-alanine supplementation improved exercise capacity in activities lasting 1-4 minutes, with a median effect size of 2.85%. The effect was most pronounced in high-intensity cycling and running tests.",
            "However, for exercises lasting longer than 4 minutes, the evidence is less clear. A 2024 systematic review noted that individual responses vary considerably, and the benefits may be limited to specific exercise modalities. The characteristic paresthesia (tingling) side effect also limits tolerability for some athletes."
        ],
    },

    # "Does moderate alcohol consumption have health benefits?" — keep dispute_698, rewrite hedged_607
    ("data/tier1_core/trustworthy_hedged.json", "t1_qualify_hard_607"): {
        "query": "Does moderate coffee consumption provide cardiovascular health benefits?",
        "contexts": [
            "A large-scale prospective study published in the European Heart Journal, following 468,629 participants over 12.5 years, found that consuming 2-3 cups of coffee daily was associated with a 10-15% lower risk of cardiovascular disease mortality and a lower incidence of arrhythmias compared to non-drinkers.",
            "However, the study authors cautioned that residual confounding may explain part of the association, as coffee drinkers in the cohort also tended to have higher physical activity levels and lower smoking rates. Additionally, individuals with certain genetic variants in CYP1A2 metabolize caffeine slowly and may experience elevated blood pressure from the same intake levels."
        ],
    },

    # "Do charter schools outperform traditional public schools?" — keep dispute_700, rewrite hedged_109
    ("data/tier1_core/trustworthy_hedged.json", "t1_qualify_hard_109"): {
        "query": "Do year-round schooling calendars improve student academic outcomes?",
        "contexts": [
            "A 2023 study by the National Education Policy Center analyzed 15 school districts that adopted year-round calendars and found modest improvements in math scores (0.08 standard deviations) and reading scores (0.05 standard deviations), with larger gains for students from low-income backgrounds.",
            "Critics note that the academic gains are small and inconsistent across studies. A meta-analysis in the Review of Educational Research found that the benefits of year-round schooling are often indistinguishable from zero when controlling for school-level factors like teacher quality and funding levels."
        ],
    },

    # "Does intermittent fasting improve cognitive function?" — keep dispute_703, rewrite hedged_016
    ("data/tier1_core/trustworthy_hedged.json", "t1_qualify_hard_016"): {
        "query": "Does regular meditation practice improve working memory capacity?",
        "contexts": [
            "A randomized controlled trial published in Psychological Science found that an 8-week mindfulness meditation program improved working memory capacity by an average of 16% on the operation span task, compared to a waitlist control group. Neuroimaging showed increased activation in the dorsolateral prefrontal cortex.",
            "A 2024 meta-analysis in Neuroscience & Biobehavioral Reviews, analyzing 45 RCTs, found that meditation effects on working memory are small (Hedges' g = 0.22) and often disappear at follow-up. The analysis noted significant publication bias and heterogeneity across study designs."
        ],
    },

    # "What is the average salary for a data scientist in the US?" — keep dispute_571, rewrite hedged_162
    ("data/tier1_core/trustworthy_hedged.json", "t1_qualify_medium_162"): {
        "query": "What is the average starting salary for cybersecurity analysts in the United States?",
        "contexts": [
            "The Bureau of Labor Statistics reported a median annual wage of $112,000 for information security analysts in 2024, with entry-level positions starting around $70,000-$85,000 depending on location and certification status. The field is projected to grow 32% from 2022 to 2032.",
            "However, salary surveys from different sources show significant variation. CompTIA's workforce report estimated entry-level cybersecurity salaries at $55,000-$75,000, while CyberSeek data suggested higher ranges in metropolitan areas. Geographic cost-of-living differences and varying definitions of 'entry-level' contribute to the discrepancy."
        ],
    },

    # "Who built the Great Zimbabwe ruins?" — keep dispute_679, rewrite hedged_313
    ("data/tier1_core/trustworthy_hedged.json", "t1_qualify_hard_313"): {
        "query": "Who constructed the Nazca Lines in Peru and for what purpose?",
        "contexts": [
            "Archaeological consensus attributes the Nazca Lines to the Nazca culture, which flourished from approximately 200 BCE to 600 CE. Radiocarbon dating of wooden stakes at line endpoints supports this timeframe. The most widely accepted theory is that the lines served a ritualistic purpose related to water and fertility.",
            "However, competing theories persist. Some researchers propose the lines served as astronomical calendars, while others suggest they marked underground water sources. A 2023 study using AI-assisted analysis identified previously unknown smaller geoglyphs, complicating earlier interpretations focused solely on the larger figures."
        ],
    },

    # "How many people are affected by food insecurity in the US?" — keep dispute_722, rewrite hedged_806
    ("data/tier1_core/trustworthy_hedged.json", "t1_qualify_hard_806"): {
        "query": "How many Americans experience chronic homelessness?",
        "contexts": [
            "HUD's 2024 Annual Homeless Assessment Report estimated 653,100 people experiencing homelessness on a single night in January 2024, a 12% increase from the previous year. Approximately 35% were classified as chronically homeless, meaning they had experienced homelessness for at least a year.",
            "However, advocates argue that point-in-time counts significantly underestimate the true scope. The National Alliance to End Homelessness noted that counts miss people in unstable housing situations, doubled-up households, and those who avoid shelters and encampments. Some estimates suggest the annual number of people experiencing any form of homelessness exceeds 1.5 million."
        ],
    },

    # "Is intermittent fasting effective for long-term weight management?" — keep dispute_725, rewrite hedged_244
    ("data/tier1_core/trustworthy_hedged.json", "t1_qualify_hard_244"): {
        "query": "Is a plant-based diet effective for long-term cardiovascular risk reduction?",
        "contexts": [
            "A 2024 prospective cohort study in JAMA Internal Medicine following 210,000 participants over 30 years found that adherence to a plant-based diet was associated with a 16% lower risk of cardiovascular disease. The strongest associations were observed for diets emphasizing whole grains, legumes, and nuts.",
            "However, not all plant-based diets are equal. The same study found that 'unhealthy' plant-based diets heavy in refined grains, sugary beverages, and processed foods were associated with a 32% higher cardiovascular risk. Additionally, some cardiologists caution that B12 deficiency and inadequate omega-3 intake in strict vegan diets may counteract cardiovascular benefits."
        ],
    },

    # "What is the recommended daily sodium intake?" — keep dispute_752, rewrite hedged_330
    ("data/tier1_core/trustworthy_hedged.json", "t1_qualify_hard_330"): {
        "query": "What is the recommended daily potassium intake for adults?",
        "contexts": [
            "The National Academies of Sciences set the adequate intake for potassium at 2,600 mg/day for women and 3,400 mg/day for men. Potassium-rich diets have been associated with lower blood pressure and reduced stroke risk in multiple observational studies.",
            "However, the WHO uses a different recommendation of at least 3,510 mg/day for all adults, and some researchers argue that the optimal intake may be higher. A 2023 Cochrane review found that while increased potassium intake lowers blood pressure, the evidence for effects on cardiovascular mortality is less consistent, particularly for people with impaired kidney function."
        ],
    },

    # "What is the poverty rate in the US?" — keep dispute_775, rewrite hedged_230
    ("data/tier1_core/trustworthy_hedged.json", "t1_qualify_hard_230"): {
        "query": "What is the child poverty rate in the United Kingdom?",
        "contexts": [
            "The Department for Work and Pensions reported that 29% of children in the UK were living in relative poverty (below 60% of median income) in 2023/24, equating to approximately 4.3 million children. The rate has remained stubbornly high despite various policy interventions over the past decade.",
            "However, the Institute for Fiscal Studies noted that different poverty measures yield different pictures. Using an anchored poverty threshold, child poverty fell from 27% to 24% between 2010 and 2024 due to real income growth. Material deprivation indicators also showed improvement, with fewer families reporting inability to afford basic necessities."
        ],
    },

    # "What is the average home price in Austin, Texas?" — keep grounding_012, rewrite hedged_814
    ("data/tier1_core/trustworthy_hedged.json", "t1_qualify_hard_814"): {
        "query": "What is the average rent for a one-bedroom apartment in Denver, Colorado?",
        "contexts": [
            "Zillow's 2024 rental market report indicated that the median rent for a one-bedroom apartment in Denver was $1,580 per month as of September 2024, representing a 3.2% year-over-year decrease. New apartment construction has increased supply, moderating rent growth.",
            "Apartments.com data for the same period showed median one-bedroom rents of $1,425, a larger decline of 7.1%. The discrepancy may reflect differences in data collection methodology — Zillow tracks listing prices while Apartments.com reports signed lease amounts, which are often negotiated below asking price in a softening market."
        ],
    },

    # "Is intermittent fasting effective for weight loss?" — keep direct_859, rewrite hedged_603
    ("data/tier1_core/trustworthy_hedged.json", "t1_qualify_hard_603"): {
        "query": "Is the Mediterranean diet effective for reducing type 2 diabetes risk?",
        "contexts": [
            "The landmark PREDIMED trial, involving 7,447 participants at high cardiovascular risk, found that a Mediterranean diet supplemented with extra-virgin olive oil or nuts reduced type 2 diabetes incidence by 52% compared to a low-fat control diet over a median follow-up of 4.1 years.",
            "A 2024 reanalysis published in the BMJ raised concerns about randomization irregularities at several PREDIMED trial sites, leading to a retraction and republication of the original results. The updated analysis still showed a risk reduction, but the effect size was smaller (30%) and the confidence intervals wider, leaving some uncertainty about the true magnitude of benefit."
        ],
    },
}


def apply_rewrites():
    """Apply all rewrites to the data files."""
    # Track which files need updating
    file_updates = {}

    # Process within-category abstention rewrites
    abs_path = os.path.join(DATA_DIR, "tier1_core", "abstention.json")
    with open(abs_path, encoding="utf-8") as f:
        abs_data = json.load(f)

    case_idx = {c["id"]: i for i, c in enumerate(abs_data["cases"])}
    for case_id, rewrite in ABSTENTION_REWRITES.items():
        if case_id in case_idx:
            idx = case_idx[case_id]
            abs_data["cases"][idx]["query"] = rewrite["query"]
            abs_data["cases"][idx]["contexts"] = rewrite["contexts"]
            # Update context_count
            abs_data["cases"][idx]["context_count"] = len(rewrite["contexts"])
            print(f"  Rewrote {case_id}: {rewrite['query'][:60]}...")
        else:
            print(f"  WARNING: {case_id} not found in abstention.json")

    file_updates[abs_path] = abs_data

    # Process within-category dispute rewrites
    disp_path = os.path.join(DATA_DIR, "tier1_core", "dispute.json")
    with open(disp_path, encoding="utf-8") as f:
        disp_data = json.load(f)

    case_idx = {c["id"]: i for i, c in enumerate(disp_data["cases"])}
    for case_id, rewrite in DISPUTE_REWRITES.items():
        if case_id in case_idx:
            idx = case_idx[case_id]
            disp_data["cases"][idx]["query"] = rewrite["query"]
            disp_data["cases"][idx]["contexts"] = rewrite["contexts"]
            disp_data["cases"][idx]["context_count"] = len(rewrite["contexts"])
            print(f"  Rewrote {case_id}: {rewrite['query'][:60]}...")
        else:
            print(f"  WARNING: {case_id} not found in dispute.json")

    file_updates[disp_path] = disp_data

    # Process within-category trustworthy_direct rewrites
    dir_path = os.path.join(DATA_DIR, "tier1_core", "trustworthy_direct.json")
    with open(dir_path, encoding="utf-8") as f:
        dir_data = json.load(f)

    case_idx = {c["id"]: i for i, c in enumerate(dir_data["cases"])}
    for case_id, rewrite in DIRECT_REWRITES.items():
        if case_id in case_idx:
            idx = case_idx[case_id]
            dir_data["cases"][idx]["query"] = rewrite["query"]
            dir_data["cases"][idx]["contexts"] = rewrite["contexts"]
            dir_data["cases"][idx]["context_count"] = len(rewrite["contexts"])
            print(f"  Rewrote {case_id}: {rewrite['query'][:60]}...")
        else:
            print(f"  WARNING: {case_id} not found in trustworthy_direct.json")

    file_updates[dir_path] = dir_data

    # Process cross-category rewrites
    for (file_path, case_id), rewrite in CROSS_CATEGORY_REWRITES.items():
        full_path = os.path.join(DATA_DIR, "..", file_path) if not os.path.isabs(file_path) else file_path
        # Normalize the path
        full_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", file_path))

        if full_path not in file_updates:
            with open(full_path, encoding="utf-8") as f:
                file_updates[full_path] = json.load(f)

        data = file_updates[full_path]
        case_idx_map = {c["id"]: i for i, c in enumerate(data["cases"])}

        if case_id in case_idx_map:
            idx = case_idx_map[case_id]
            data["cases"][idx]["query"] = rewrite["query"]
            data["cases"][idx]["contexts"] = rewrite["contexts"]
            data["cases"][idx]["context_count"] = len(rewrite["contexts"])
            if "forbidden_claims" in rewrite:
                data["cases"][idx]["forbidden_claims"] = rewrite["forbidden_claims"]
            print(f"  Rewrote {case_id} in {os.path.basename(full_path)}: {rewrite['query'][:60]}...")
        else:
            print(f"  WARNING: {case_id} not found in {full_path}")

    # Write all updated files
    for path, data in file_updates.items():
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"  Wrote {path}")

    print(f"\nDone. Applied {len(ABSTENTION_REWRITES)} abstention + {len(DISPUTE_REWRITES)} dispute + {len(DIRECT_REWRITES)} direct + {len(CROSS_CATEGORY_REWRITES)} cross-category rewrites.")


if __name__ == "__main__":
    apply_rewrites()
