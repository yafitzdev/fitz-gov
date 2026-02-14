"""Apply within-category duplicate rewrites that were overwritten by path normalization bug."""

import json
import os

BASE = os.path.join(os.path.dirname(__file__), "..")

ABSTENTION_REWRITES = {
    "t1_abstain_hard_114": {
        "query": "What specific compounds are used in the new industrial adhesive formulation?",
        "contexts": ["GripBond Industries announced a new industrial adhesive line in Q3 2024. The product targets automotive and aerospace applications requiring high-temperature resistance up to 400\u00b0F. Initial orders from three major manufacturers exceeded projections by 60%, with full production scaling expected in early 2025."],
    },
    "t1_abstain_hard_115": {
        "query": "What are the active ingredients in the new organic pest control spray?",
        "contexts": ["GreenShield Organics received EPA registration for their new pest control spray targeting home garden use. The product was developed over 18 months at their Portland research facility. Field trials across six climate zones showed 89% effectiveness against common aphids and whiteflies."],
    },
    "t1_abstain_hard_116": {
        "query": "What preservatives are used in the reformulated children's cough syrup?",
        "contexts": ["PediCare Pharmaceuticals reformulated their children's cough syrup in response to parent concerns about artificial additives. The new version launched in 2,400 pharmacies nationwide. Clinical trials with 350 pediatric patients showed comparable efficacy to the previous formulation with improved taste ratings."],
    },
    "t1_abstain_hard_117": {
        "query": "What materials compose the new biodegradable food packaging?",
        "contexts": ["EcoPack Solutions unveiled their biodegradable food packaging at the 2024 Sustainable Packaging Conference. The packaging decomposes within 90 days in commercial composting facilities. Three major restaurant chains have signed pilot agreements to test the product in their takeout operations."],
    },
    "t1_abstain_hard_1125": {
        "query": "What specific nutrients are in the new fortified breakfast cereal?",
        "contexts": ["NutriStart Foods launched a fortified breakfast cereal aimed at children ages 4-12. The product was developed in partnership with the Children's Nutrition Research Center. Market research indicated strong parent interest in healthier breakfast options, with 78% of surveyed parents willing to pay a premium."],
    },
    "t1_abstain_hard_1149": {
        "query": "What chemical additives are in the new fire-resistant building insulation?",
        "contexts": ["SafeHome Materials introduced a fire-resistant insulation product at the International Building Materials Expo. The insulation achieved a Class A fire rating in independent testing by Underwriters Laboratories. Several state building codes are being updated to require enhanced fire resistance in residential construction."],
    },
    "t1_abstain_hard_1173": {
        "query": "What dyes and colorants are used in the new textile printing ink?",
        "contexts": ["ChromaPrint launched a new textile ink system compatible with major industrial printers. The company claims the inks produce 40% more vibrant colors than competing products. Fashion brands including two luxury houses have begun sampling the inks for their Spring 2025 collections."],
    },
    "t1_abstain_hard_1174": {
        "query": "What essential oils are blended in the new aromatherapy diffuser product?",
        "contexts": ["WellnessAir released a premium aromatherapy diffuser system with proprietary scent cartridges. The product was endorsed by the International Aromatherapy Association and has sold over 50,000 units since launch. Customer reviews cite improved sleep quality and reduced stress levels."],
    },
    "t1_abstain_hard_123": {
        "query": "What were the specific articles of the Edict of Nantes in 1598?",
        "contexts": ["The Edict of Nantes, issued by Henry IV of France, is widely regarded as a landmark in religious tolerance. It ended the French Wars of Religion, which had devastated the country for over three decades. Henry IV's conversion to Catholicism in 1593 was a prerequisite for his acceptance as king by the Catholic majority."],
    },
    "t1_abstain_hard_125": {
        "query": "What were the precise boundary provisions of the Treaty of Zaragoza in 1529?",
        "contexts": ["The Treaty of Zaragoza was signed between Spain and Portugal as a companion agreement to earlier colonial treaties. It resolved competing claims in the Pacific region. Spain received a payment of 350,000 ducats as part of the arrangement, which was a substantial sum at the time."],
    },
    "t1_abstain_hard_126": {
        "query": "What were the detailed surrender conditions in the Treaty of Ghent in 1814?",
        "contexts": ["The Treaty of Ghent ended the War of 1812 between the United States and Great Britain. Negotiations took place in the city of Ghent in modern-day Belgium. Both American and British delegations included prominent political figures of the era."],
    },
    "t1_abstain_hard_127": {
        "query": "What were the specific reparation amounts stipulated in the Treaty of Frankfurt in 1871?",
        "contexts": ["The Treaty of Frankfurt ended the Franco-Prussian War and led to the creation of the German Empire. The treaty was negotiated primarily by Otto von Bismarck. France lost the provinces of Alsace and most of Lorraine, a loss that would fuel resentment for decades."],
    },
    "t1_abstain_hard_1176": {
        "query": "What were the territorial concessions defined in the Treaty of Brest-Litovsk in 1918?",
        "contexts": ["The Treaty of Brest-Litovsk was signed between Soviet Russia and the Central Powers. It allowed Russia to exit World War I, fulfilling one of the Bolsheviks' key promises. The treaty was later annulled following Germany's defeat in November 1918."],
    },
    "t1_abstain_hard_130": {
        "query": "What is the average mortgage origination fee for commercial real estate loans?",
        "contexts": ["Commercial real estate lending saw record volumes in 2024, driven by strong demand for industrial and logistics properties. Major banks expanded their commercial lending divisions, hiring over 2,000 loan officers nationally. The sector benefited from declining vacancy rates in prime industrial corridors."],
    },
    "t1_abstain_hard_131": {
        "query": "What is the typical escrow deposit percentage for luxury home purchases?",
        "contexts": ["The luxury home market above $5 million saw a 12% increase in transactions in 2024. International buyers accounted for 23% of luxury purchases in major metros. Miami, Los Angeles, and New York remained the top three markets by transaction volume."],
    },
    "t1_abstain_hard_132": {
        "query": "What is the average title insurance premium for a $500,000 home purchase?",
        "contexts": ["Title insurance protects buyers and lenders against potential ownership disputes. The industry processes over 1.5 million policies annually in the United States. Digital transformation has reduced the average closing timeline from 45 to 32 days for residential transactions."],
    },
    "t1_abstain_hard_133": {
        "query": "What is the standard inspection contingency period for residential sales in Texas?",
        "contexts": ["Texas residential real estate transactions are governed by the Texas Real Estate Commission (TREC). Standard forms are updated annually to reflect legislative changes. Licensed inspectors must complete 194 hours of qualifying education and pass the state examination."],
    },
    "t1_abstain_hard_134": {
        "query": "What is the average property tax rate for single-family homes in Cook County, Illinois?",
        "contexts": ["Cook County, Illinois, underwent a comprehensive property reassessment in 2024. The county assessor's office processes valuations for over 1.8 million parcels. Appeals of assessed values can be filed with the Cook County Board of Review within 30 days of receiving the assessment notice."],
    },
    "t1_abstain_hard_140": {
        "query": "How many delegates does New Hampshire send to the national party conventions?",
        "contexts": ["New Hampshire holds the first-in-the-nation primary election, a tradition dating back to 1920. The state's small size allows candidates to engage in retail politics, meeting voters at diners and town halls. The primary's predictive value has been debated by political scientists, with mixed results over the past five decades."],
    },
    "t1_abstain_hard_143": {
        "query": "How many Senate-confirmed positions exist in the federal executive branch?",
        "contexts": ["The Senate confirmation process has become increasingly contentious in recent decades. The average confirmation time for presidential nominees has tripled since the 1980s. Recess appointments have been used by multiple administrations to bypass lengthy confirmation delays."],
    },
    "t1_abstain_hard_144": {
        "query": "How many federal judicial vacancies currently exist in the circuit courts?",
        "contexts": ["The federal judiciary comprises 13 circuit courts of appeals and 94 district courts. Judicial appointments are lifetime positions under Article III of the Constitution. The Judicial Conference of the United States periodically recommends the creation of new judgeships to manage growing caseloads."],
    },
    "t1_abstain_hard_145": {
        "query": "How many lobbying firms are registered to operate in Washington, D.C.?",
        "contexts": ["Washington, D.C. is home to a vast lobbying industry that influences federal legislation. The Lobbying Disclosure Act of 1995 established registration requirements for lobbyists. K Street has become synonymous with the lobbying industry, though many firms have relocated to other areas of the capital."],
    },
    "t1_abstain_hard_146": {
        "query": "How many executive orders has the current administration issued in its first year?",
        "contexts": ["Executive orders are directives issued by the President to manage operations of the federal government. Their use has varied significantly across administrations. The legal authority for executive orders derives from Article II of the Constitution and specific statutory delegations."],
    },
    "t1_abstain_hard_149": {
        "query": "What is the safe minimum cooking temperature for wild game meats?",
        "contexts": ["Wild game hunting is regulated by state wildlife agencies across the United States. The processing of game meat must follow USDA guidelines for sanitation. Hunter education courses cover field dressing techniques and proper meat handling to prevent contamination during transport."],
    },
    "t1_abstain_hard_201": {
        "query": "What is the recommended internal temperature for reheating leftover casseroles?",
        "contexts": ["Food safety in leftovers management is a growing concern for public health agencies. The CDC estimates 48 million Americans experience foodborne illness annually. Proper refrigeration within two hours of cooking is emphasized in food safety education programs."],
    },
    "t1_abstain_hard_204": {
        "query": "What temperature should smoked salmon reach during the hot-smoking process?",
        "contexts": ["Salmon smoking is both a culinary tradition and a food preservation method dating back centuries. Pacific Northwest tribes developed sophisticated smoking techniques long before European contact. Modern commercial smoking operations use computerized kilns to ensure consistent flavor profiles."],
    },
    "t1_abstain_hard_209": {
        "query": "What is the safe holding temperature for buffet-style food service?",
        "contexts": ["Buffet-style food service is popular in hotels, conferences, and catering operations. The National Restaurant Association provides guidelines for food presentation and service flow. Customer satisfaction surveys indicate that food variety is the most valued aspect of buffet dining."],
    },
    "t1_abstain_hard_211": {
        "query": "What is the cap on punitive damages in product liability cases in Ohio?",
        "contexts": ["Ohio's tort reform legislation has been updated multiple times since the early 2000s. Product liability claims in Ohio must establish that the product was defective when it left the manufacturer's control. The state follows a modified comparative fault standard for determining damages."],
    },
    "t1_abstain_hard_212": {
        "query": "What is the filing deadline for workers' compensation claims in New York?",
        "contexts": ["New York's workers' compensation system covers most private-sector employees. The Workers' Compensation Board adjudicates disputes between injured workers and employers. Medical providers must be authorized by the Board to treat workers' compensation patients."],
    },
    "t1_abstain_hard_214": {
        "query": "What is the mandatory waiting period for divorce proceedings in Illinois?",
        "contexts": ["Illinois family law underwent significant reform with the Marriage and Dissolution of Marriage Act. The state adopted no-fault divorce provisions, eliminating the need to prove specific grounds. Mediation is increasingly encouraged as an alternative to contested litigation in custody disputes."],
    },
    "t1_abstain_hard_215": {
        "query": "What is the maximum penalty for first-offense DUI in Pennsylvania?",
        "contexts": ["Pennsylvania's DUI enforcement program includes sobriety checkpoints authorized under state law. The state operates an Accelerated Rehabilitative Disposition program for first-time offenders. Ignition interlock requirements have expanded under recent legislative amendments."],
    },
    "t1_abstain_hard_218": {
        "query": "What was the attendance figure for the 2024 Paris Olympics opening ceremony?",
        "contexts": ["The 2024 Paris Olympics featured a groundbreaking opening ceremony along the Seine River. Security operations involved over 45,000 police and military personnel. The ceremony showcased French cultural heritage through elaborate artistic performances."],
    },
    "t1_abstain_hard_219": {
        "query": "What was the TV viewership for the 2024 Super Bowl halftime show?",
        "contexts": ["The Super Bowl remains the most-watched annual television event in the United States. Advertising rates have increased consistently over the past two decades. The halftime show has evolved from simple marching band performances to elaborate productions featuring global music stars."],
    },
    "t1_abstain_hard_220": {
        "query": "What was the prize money distribution at the 2024 Wimbledon Championships?",
        "contexts": ["Wimbledon, the oldest tennis tournament in the world, has been held at the All England Club since 1877. The tournament maintains its tradition of grass courts and all-white dress codes. The 2024 event saw record attendance across the fortnight of play."],
    },
    "t1_abstain_hard_255": {
        "query": "What is the passenger capacity of the Airbus A380 in standard configuration?",
        "contexts": ["The Airbus A380, the world's largest passenger aircraft, entered service in 2007. Production ceased in 2021 after 251 deliveries. Emirates remains the largest operator of the type, using it extensively on high-density routes between Dubai and major global hubs."],
    },
    "t1_abstain_hard_256": {
        "query": "What is the cruising speed of the Maersk Triple-E class container ships?",
        "contexts": ["The Triple-E class represents Maersk's commitment to efficient large-scale container shipping. These vessels can carry over 18,000 twenty-foot equivalent units. The class was designed with a twin-skeg hull form that reduces fuel consumption compared to previous generations."],
    },
    "t1_abstain_hard_258": {
        "query": "What is the top speed of the Hennessey Venom F5 hypercar?",
        "contexts": ["The Hennessey Venom F5 is an American hypercar designed to challenge established European manufacturers. The vehicle features a twin-turbocharged V8 engine developed entirely in-house. Only 24 units were planned for production, each customized to the buyer's specifications."],
    },
    "t1_abstain_hard_604": {
        "query": "What is the remission rate for exposure therapy in treating specific phobias?",
        "contexts": ["Specific phobias affect approximately 12% of the adult population at some point in their lives. The development of virtual reality technology has opened new avenues for therapeutic intervention. Research institutions across Europe and North America have established dedicated anxiety treatment centers."],
    },
    "t1_abstain_hard_606": {
        "query": "What is the efficacy rate of dialectical behavior therapy for borderline personality disorder?",
        "contexts": ["Borderline personality disorder presents significant treatment challenges for mental health professionals. The disorder is characterized by emotional dysregulation, unstable relationships, and identity disturbance. Training programs for therapists specializing in personality disorders have expanded in recent years."],
    },
    "t1_abstain_hard_608": {
        "query": "What content moderation policy changes did TikTok implement in 2024?",
        "contexts": ["TikTok's global user base surpassed 1.5 billion monthly active users in 2024. The platform has invested heavily in creator monetization tools and e-commerce features. Regulatory scrutiny of TikTok's data practices has intensified in multiple countries."],
    },
    "t1_abstain_hard_609": {
        "query": "What changes to its news feed ranking algorithm did Facebook announce in 2024?",
        "contexts": ["Meta's Facebook platform continues to evolve its approach to content distribution. The company has shifted significant engineering resources toward AI-powered content recommendations. User engagement patterns have changed substantially with the rise of short-form video content."],
    },
    "t1_abstain_hard_704": {
        "query": "What is the average time-to-hire for senior engineering positions at Fortune 500 companies?",
        "contexts": ["Fortune 500 companies have significantly expanded their technical hiring operations in recent years. Many have established dedicated engineering campuses and innovation labs. Competition for senior engineering talent has led to creative benefits packages including remote work options and sabbatical programs."],
    },
    "t1_abstain_hard_705": {
        "query": "What is the median tenure of C-suite executives in the healthcare industry?",
        "contexts": ["Healthcare executive leadership has faced unprecedented challenges in recent years. Hospital systems have consolidated rapidly, creating larger organizational structures. Executive coaching and leadership development programs have become standard investments for major healthcare systems."],
    },
    "t1_abstain_hard_802": {
        "query": "What fraction of microplastics in drinking water comes from tire wear particles?",
        "contexts": ["Microplastics research has expanded rapidly as detection methods have improved. Studies have identified plastic particles in water sources across all seven continents. International cooperation on plastic pollution has increased through various UN-sponsored initiatives."],
    },
    "t1_abstain_hard_805": {
        "query": "What percentage of marine biodiversity loss is attributed to deep-sea trawling?",
        "contexts": ["Marine biodiversity conservation has become a priority for international environmental organizations. The establishment of marine protected areas has accelerated in the past decade. Advances in underwater monitoring technology have improved our understanding of deep-ocean ecosystems."],
    },
    "t1_abstain_medium_917": {
        "query": "What is the recommended daily intake of omega-3 fatty acids for pregnant women?",
        "contexts": ["Prenatal nutrition research has expanded significantly in the past decade. The American College of Obstetricians and Gynecologists publishes guidelines for nutrition during pregnancy. Fish consumption during pregnancy has been a topic of debate due to concerns about mercury exposure."],
    },
    "t1_abstain_hard_809": {
        "query": "What is the ideal nitrogen application rate for commercial strawberry cultivation?",
        "contexts": ["Commercial strawberry production in the United States is concentrated in California and Florida. Sustainable farming practices have gained traction among strawberry growers seeking organic certification. Drip irrigation systems have improved water use efficiency in strawberry fields by up to 30%."],
    },
    "t1_abstain_medium_916": {
        "query": "What is the exact wavelength of the hydrogen alpha spectral line?",
        "contexts": ["Spectroscopy is a foundational tool in astrophysics, enabling the identification of chemical elements in distant stars. The hydrogen spectrum was first systematically described by Johann Balmer in 1885. Modern spectrographs can resolve spectral features with extraordinary precision."],
    },
    "t1_abstain_medium_004": {
        "query": "What is the population density of Monaco?",
        "contexts": ["Monaco is the second-smallest country in the world by area, covering approximately 2.02 square kilometers. It is located on the French Riviera and is famous for the Monte Carlo Casino and the annual Formula 1 Grand Prix. The principality has no income tax, attracting wealthy residents from around the world."],
    },
    "t1_abstain_hard_1087": {
        "query": "How many gallons of water are needed to produce one pound of almonds?",
        "contexts": ["California's Central Valley is the largest almond-producing region in the world, accounting for over 80% of global supply. Almond orchards require irrigation in the Mediterranean climate of the valley. Recent droughts have prompted growers to adopt more efficient micro-drip irrigation systems."],
    },
    "t1_abstain_hard_1089": {
        "query": "What is the decay rate of potassium-40 in volcanic rock samples?",
        "contexts": ["Potassium-argon dating is widely used in geochronology for dating volcanic rocks and minerals. The technique has been instrumental in establishing the geological time scale. Volcanic eruptions in the East African Rift Valley have been dated using this method, contributing to our understanding of early human evolution."],
    },
}

DISPUTE_REWRITES = {
    "t1_dispute_hard_734": {
        "query": "Does eating organic food significantly reduce cancer risk?",
        "contexts": [
            "A 2023 longitudinal study published in the British Journal of Nutrition tracked 68,946 participants over 7 years and found that frequent organic food consumers had a 25% lower overall cancer risk, with particularly strong reductions in non-Hodgkin lymphoma and postmenopausal breast cancer.",
            "A comprehensive 2024 meta-analysis in the Annals of Internal Medicine reviewing 240 studies concluded that organic foods show no clinically meaningful difference in health outcomes compared to conventional foods, noting that the cancer risk reduction in observational studies disappears when controlling for lifestyle factors."
        ],
    },
    "t1_dispute_medium_608": {
        "query": "Does screen time before bed impair sleep quality in school-age children?",
        "contexts": [
            "A controlled study at the University of Colorado involving 234 children ages 8-12 found that one hour of tablet use before bedtime reduced total sleep duration by 28 minutes and delayed sleep onset by 37 minutes compared to book reading, with measurable decreases in REM sleep duration.",
            "A 2024 systematic review in the Journal of Sleep Research, analyzing 18 randomized controlled trials, found no consistent evidence that moderate screen use (under 90 minutes) before bed affects objective sleep measures in children, suggesting that content type and arousal level matter more than screen exposure itself."
        ],
    },
}

DIRECT_REWRITES = {
    "t1_confident_hard_867": {
        "query": "How does mRNA vaccine technology produce an immune response?",
        "contexts": [
            "mRNA vaccines work by delivering synthetic messenger RNA into cells, which instructs cellular ribosomes to produce a specific protein antigen\u2014in the case of COVID-19 vaccines, the spike protein of SARS-CoV-2. The immune system recognizes this protein as foreign and mounts both an antibody response and a T-cell response. The mRNA does not enter the cell nucleus or interact with DNA, and is degraded by normal cellular processes within 48-72 hours. Lipid nanoparticles serve as the delivery mechanism, protecting the fragile mRNA molecule during injection and facilitating cellular uptake.",
            "According to the National Institute of Allergy and Infectious Diseases, the mRNA platform enables rapid vaccine development because only the genetic sequence of the target antigen is needed, not the actual pathogen. Clinical trials by Pfizer-BioNTech and Moderna demonstrated 94-95% efficacy in preventing symptomatic COVID-19 infection. The technology has been in development since the 1990s, with foundational work by Katalin Karik\u00f3 and Drew Weissman on modified nucleosides proving critical to overcoming early inflammatory responses."
        ],
    },
}


def main():
    # Fix abstention
    path = os.path.join(BASE, "data", "tier1_core", "abstention.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    case_idx = {c["id"]: i for i, c in enumerate(data["cases"])}
    fixed = 0
    for case_id, rewrite in ABSTENTION_REWRITES.items():
        if case_id in case_idx:
            idx = case_idx[case_id]
            data["cases"][idx]["query"] = rewrite["query"]
            data["cases"][idx]["contexts"] = rewrite["contexts"]
            data["cases"][idx]["context_count"] = len(rewrite["contexts"])
            fixed += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Fixed {fixed} abstention cases")

    # Fix dispute
    path = os.path.join(BASE, "data", "tier1_core", "dispute.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    case_idx = {c["id"]: i for i, c in enumerate(data["cases"])}
    fixed = 0
    for case_id, rewrite in DISPUTE_REWRITES.items():
        if case_id in case_idx:
            idx = case_idx[case_id]
            data["cases"][idx]["query"] = rewrite["query"]
            data["cases"][idx]["contexts"] = rewrite["contexts"]
            data["cases"][idx]["context_count"] = len(rewrite["contexts"])
            fixed += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Fixed {fixed} dispute cases")

    # Fix trustworthy_direct
    path = os.path.join(BASE, "data", "tier1_core", "trustworthy_direct.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    case_idx = {c["id"]: i for i, c in enumerate(data["cases"])}
    fixed = 0
    for case_id, rewrite in DIRECT_REWRITES.items():
        if case_id in case_idx:
            idx = case_idx[case_id]
            data["cases"][idx]["query"] = rewrite["query"]
            data["cases"][idx]["contexts"] = rewrite["contexts"]
            data["cases"][idx]["context_count"] = len(rewrite["contexts"])
            fixed += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Fixed {fixed} trustworthy_direct cases")


if __name__ == "__main__":
    main()
