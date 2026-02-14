"""
Generate 91 new trustworthy_direct cases and append to data/tier1_core/trustworthy_direct.json.

IDs: t1_confident_hard_916..961 (46 hard), t1_confident_medium_910..954 (45 medium)
"""

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_FILE = os.path.join(PROJECT_ROOT, "data", "tier1_core", "trustworthy_direct.json")


def make_case(
    id_str, difficulty, subcategory, query, contexts, description, rationale,
    domain, query_type, source_type, reasoning_type, evidence_pattern="direct",
    context_sources=None,
):
    c = {
        "id": id_str,
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
        "evidence_pattern": evidence_pattern,
        "category": "trustworthy_direct",
        "evaluation_config": {
            "mode": "governance",
            "check_mode_match": True,
        },
    }
    if context_sources is not None:
        c["context_sources"] = context_sources
    return c


def build_cases():
    cases = []

    # ── hard cases: t1_confident_hard_916 .. t1_confident_hard_961 (46) ──

    cases.append(make_case(
        "t1_confident_hard_916", "hard", "technical_documented",
        "How does the Linux kernel's Completely Fair Scheduler allocate CPU time?",
        [
            "The Completely Fair Scheduler (CFS) in the Linux kernel uses a red-black tree indexed by each task's virtual runtime (vruntime). Tasks that have consumed the least CPU time sit leftmost in the tree and are scheduled next. CFS calculates vruntime as actual_runtime / task_weight, where weight derives from the nice value. This ensures higher-priority tasks accumulate vruntime more slowly and thus receive more CPU time.",
            "CFS targets a configurable scheduling latency (default 6 ms for up to 8 runnable tasks). When the number of runnable tasks exceeds 8, the minimum granularity (0.75 ms) prevents excessive context switching. The scheduler rebalances across CPUs via periodic load balancing every 4 ms on idle CPUs and every 64 ms on busy ones."
        ],
        "Technical OS scheduling question with complete algorithmic detail",
        "Context fully explains CFS data structure, vruntime calculation, weight mapping, latency targets, and load balancing intervals",
        "technology", "how", "single", "procedural",
    ))

    cases.append(make_case(
        "t1_confident_hard_917", "hard", "technical_documented",
        "What are the ACID properties in database transaction management?",
        [
            "ACID stands for Atomicity, Consistency, Isolation, and Durability. Atomicity guarantees that all operations in a transaction either complete fully or roll back entirely, using write-ahead logging (WAL). Consistency ensures the database transitions only between valid states by enforcing constraints such as foreign keys and check constraints.",
            "Isolation controls concurrent access through mechanisms like MVCC or two-phase locking, with levels ranging from Read Uncommitted to Serializable. Durability guarantees committed data survives system failures by flushing WAL records to persistent storage before acknowledging the commit, typically using fsync or O_DIRECT I/O."
        ],
        "Database fundamentals with precise technical mechanisms for each ACID property",
        "Both contexts together provide a complete definition and implementation detail for every ACID property",
        "technology", "what", "single", "factual",
    ))

    cases.append(make_case(
        "t1_confident_hard_918", "hard", "clear_explanation",
        "Why does quantitative easing increase asset prices but not always consumer inflation?",
        [
            "Quantitative easing (QE) involves the central bank purchasing government bonds and other securities, injecting reserves into the banking system. This lowers long-term interest rates and compresses yields, pushing investors toward riskier assets like equities and real estate, directly inflating their prices.",
            "Consumer inflation depends on bank lending transmitting reserves into the real economy. During the 2010-2019 QE era, banks held excess reserves rather than lending aggressively due to stricter capital requirements and weak loan demand. Velocity of money (M2 velocity) fell from 1.7 to 1.4, dampening the pass-through from monetary base expansion to consumer price increases."
        ],
        "Macroeconomic mechanism explaining the asymmetric effects of QE on assets versus consumer prices",
        "Contexts explain both the asset-price channel (portfolio rebalancing) and why consumer inflation lagged (low velocity, weak lending transmission)",
        "finance", "why", "single", "causal",
    ))

    cases.append(make_case(
        "t1_confident_hard_919", "hard", "clear_explanation",
        "How does CRISPR-Cas9 achieve targeted gene editing in eukaryotic cells?",
        [
            "CRISPR-Cas9 gene editing uses a synthetic guide RNA (sgRNA) complementary to a 20-nucleotide target sequence adjacent to a protospacer adjacent motif (PAM, typically NGG for SpCas9). The Cas9 protein forms a ribonucleoprotein complex with the sgRNA, scans genomic DNA for PAM sites, and upon sgRNA-target complementarity, creates a double-strand break (DSB) 3 base pairs upstream of the PAM.",
            "The cell repairs the DSB through either non-homologous end joining (NHEJ), which introduces insertions/deletions disrupting gene function, or homology-directed repair (HDR) when a donor template is co-delivered, enabling precise sequence insertion. HDR efficiency is typically 5-20% in mammalian cells, while NHEJ dominates at 30-70% efficiency."
        ],
        "Molecular biology question with complete CRISPR mechanism from target recognition to DNA repair outcomes",
        "Contexts cover sgRNA design, PAM recognition, DSB creation, and both repair pathways with quantified efficiencies",
        "science", "how", "single", "procedural",
    ))

    cases.append(make_case(
        "t1_confident_hard_920", "hard", "contradiction_resolved",
        "Is coffee consumption linked to increased or decreased cardiovascular risk?",
        [
            "A widely cited 2006 study in the American Journal of Clinical Nutrition found that consuming more than 4 cups of coffee per day was associated with a 20% increase in coronary heart disease risk, particularly among slow caffeine metabolizers with CYP1A2 gene variants.",
            "However, a 2022 meta-analysis published in the European Journal of Preventive Cardiology aggregating 382,535 participants across 21 cohort studies concluded that 3-5 cups of coffee per day is associated with a 15% lower risk of cardiovascular mortality. The discrepancy is explained by the 2006 study's failure to control for smoking and sedentary behavior, confounders that the later meta-analysis adjusted for."
        ],
        "Apparently contradictory findings about coffee and heart health resolved by methodological improvements",
        "Initial context suggests increased risk, but second context explains the earlier study's confounders and presents stronger evidence for decreased risk",
        "food", "is", "single", "evaluative",
    ))

    cases.append(make_case(
        "t1_confident_hard_921", "hard", "contradiction_resolved",
        "Does stretching before exercise prevent injuries or not?",
        [
            "A 2004 systematic review in the British Medical Journal concluded that static stretching before exercise showed no statistically significant reduction in injury risk across 5 randomized controlled trials (pooled RR 0.93, 95% CI 0.78-1.11). Several sports medicine textbooks from that era still recommended pre-exercise stretching.",
            "A 2016 update in the British Journal of Sports Medicine clarified the distinction: static stretching alone is ineffective, but dynamic stretching combined with a progressive warm-up reduces lower-extremity injury rates by 35% (RR 0.65, 95% CI 0.50-0.84). The earlier review conflated static and dynamic modalities, explaining the null result."
        ],
        "Contradictory stretching injury-prevention evidence resolved by distinguishing stretching types",
        "First context shows null effect, second resolves by separating static from dynamic stretching and showing dynamic warm-ups work",
        "sports", "does", "single", "evaluative",
    ))

    cases.append(make_case(
        "t1_confident_hard_922", "hard", "opposing_with_consensus",
        "Should schools adopt later start times for adolescents?",
        [
            "The American Academy of Pediatrics recommends middle and high schools start no earlier than 8:30 AM, citing research that adolescent circadian rhythms shift sleep onset to approximately 11 PM due to delayed melatonin release. A CDC study of 362 schools found districts that adopted 8:30+ start times saw a 16.5% reduction in teen car crashes and a 4.5% improvement in attendance.",
            "Critics argue later start times create logistical problems: 78% of surveyed superintendents cited bus scheduling conflicts, increased childcare costs for working parents, and reduced after-school daylight for sports. The Brookings Institution estimated implementation costs of $150 per student annually."
        ],
        "Policy question where medical consensus clearly favors later starts despite logistical objections",
        "Medical authority (AAP) and empirical crash/attendance data strongly support later starts; opposition is logistical, not scientific",
        "education", "should", "single", "evaluative",
    ))

    cases.append(make_case(
        "t1_confident_hard_923", "hard", "opposing_with_consensus",
        "Is nuclear energy a viable component of climate change mitigation?",
        [
            "The IPCC Sixth Assessment Report (2022) identifies nuclear energy as a proven low-carbon technology, with lifecycle emissions of 5.5 g CO2-eq/kWh, comparable to wind (4.4 g) and well below solar (26 g). All four IPCC mitigation pathways limiting warming to 1.5C include nuclear capacity increases of 90-200% by 2050.",
            "Environmental groups like Greenpeace oppose nuclear expansion, citing Fukushima and Chernobyl disaster risks, unresolved waste storage for 10,000+ year half-lives, and cost overruns at plants like Hinkley Point C (projected at GBP 33 billion versus GBP 18 billion original estimate). They advocate exclusive investment in renewables plus storage."
        ],
        "Climate policy question where IPCC scientific consensus includes nuclear despite advocacy group opposition",
        "IPCC (authoritative body) explicitly includes nuclear in all 1.5C pathways with quantified emissions data; opposition is risk-based advocacy, not emissions-based science",
        "environment", "is", "single", "evaluative",
    ))

    cases.append(make_case(
        "t1_confident_hard_924", "hard", "different_framing",
        "Why does Type 2 diabetes develop at the molecular level?",
        [
            "From a cellular signaling perspective, Type 2 diabetes results from impaired insulin receptor substrate (IRS) phosphorylation. Chronic caloric excess activates serine/threonine kinases (JNK, IKK-beta) that phosphorylate IRS-1 at inhibitory serine residues instead of activating tyrosine residues. This blocks downstream PI3K/Akt signaling, preventing GLUT4 transporter translocation to the cell membrane.",
            "From a metabolic perspective, persistent hyperglycemia causes beta-cell glucotoxicity: elevated glucose generates reactive oxygen species via mitochondrial electron transport chain overload, damaging beta-cell DNA and reducing insulin secretion by 50-80% over 10-15 years. Lipotoxicity from circulating free fatty acids compounds this through ceramide-mediated beta-cell apoptosis."
        ],
        "Molecular diabetes pathology explained through complementary signaling and metabolic framings",
        "One context covers insulin resistance (signaling defect), the other covers beta-cell failure (metabolic damage); together they give the full molecular picture",
        "medicine", "why", "single", "causal",
    ))

    cases.append(make_case(
        "t1_confident_hard_925", "hard", "different_framing",
        "Why did the Ottoman Empire collapse after World War I?",
        [
            "Military historians emphasize that the Ottoman Empire's collapse followed catastrophic wartime losses. The Gallipoli campaign (1915-1916) killed 250,000 Ottoman soldiers, and the Mesopotamian and Palestinian fronts drained remaining manpower. By 1918, the Ottoman army had suffered over 2.8 million casualties from combat, disease, and desertion. The Armistice of Mudros (October 30, 1918) formalized military defeat and Allied occupation of strategic territories.",
            "Political and economic historians point to longer structural decay: the 'Capitulations' system gave European powers trade privileges that undermined Ottoman industry, while nationalist movements (Arab, Armenian, Greek, Balkan) fragmented the multiethnic empire. The Young Turk Revolution (1908) attempted modernization but alienated non-Turkish populations. The Treaty of Sevres (1920) partitioned Ottoman territory, though Ataturk's independence war led to the Treaty of Lausanne (1923)."
        ],
        "Ottoman collapse explained through complementary military defeat and structural decay framings",
        "Both framings converge: military losses in WWI triggered the final collapse of an empire already weakened by economic dependency and nationalist fragmentation",
        "history", "why", "single", "causal",
    ))

    cases.append(make_case(
        "t1_confident_hard_926", "hard", "quantitative_answer",
        "Is copper the most thermally conductive metal at room temperature?",
        [
            "Copper has a thermal conductivity of 401 W/(m*K) at 25 degrees Celsius, making it the second most thermally conductive pure metal after silver (429 W/(m*K)). This high conductivity results from copper's single 4s electron contributing to both electrical and thermal transport via the Wiedemann-Franz law.",
            "NIST Standard Reference Data confirms copper's thermal conductivity at 293 K as 401 +/- 1 W/(m*K) for oxygen-free high-conductivity (OFHC) copper. Alloying reduces conductivity significantly: brass (Cu-Zn) drops to 109 W/(m*K) and bronze (Cu-Sn) to 50 W/(m*K)."
        ],
        "Precise quantitative materials science answer with authoritative measurement data",
        "Both contexts converge on 401 W/(m*K) with NIST confirmation and physical explanation",
        "general", "is", "multi_source",
        "factual", "direct",
        context_sources=[
            {"source_id": "ashm_metals_handbook_v2", "source_type": "reference", "authority": "primary"},
            {"source_id": "nist_srd_thermal_conductivity", "source_type": "government", "authority": "official"},
        ],
    ))

    cases.append(make_case(
        "t1_confident_hard_927", "hard", "quantitative_answer",
        "How much water does it take to produce one kilogram of beef?",
        [
            "The Water Footprint Network calculates that producing 1 kg of beef requires approximately 15,415 liters of water globally averaged. This breaks down to 98.8% green water (rainwater for pasture/feed crops), 0.8% blue water (irrigation), and 0.4% grey water (pollution dilution). Feed production accounts for 99% of the total, with a typical feedlot steer consuming 2,500 kg of grain over its lifetime.",
            "Regional variation is significant: water-efficient operations in the Netherlands use approximately 8,000 liters/kg through intensive grain-fed systems, while extensive pastoral systems in arid regions can exceed 20,000 liters/kg due to lower grass productivity and longer rearing times."
        ],
        "Water footprint of beef with global average, breakdown by water type, and regional range",
        "Contexts provide precise global average (15,415 L/kg), water-type decomposition, and regional variation range",
        "agriculture", "how", "single", "factual",
    ))

    cases.append(make_case(
        "t1_confident_hard_928", "hard", "cross_source_agreement",
        "What is the current federal minimum wage in the United States?",
        [
            "The Fair Labor Standards Act (FLSA) establishes the federal minimum wage at $7.25 per hour, a rate set by the Fair Minimum Wage Act of 2007 and effective since July 24, 2009. Tipped employees may be paid a minimum cash wage of $2.13 per hour provided tips bring total compensation to at least $7.25.",
            "The U.S. Department of Labor Wage and Hour Division confirms the federal minimum wage remains $7.25 per hour as of 2025. Thirty states and the District of Columbia have enacted higher state minimum wages, with Washington state highest at $16.66 per hour."
        ],
        "Federal minimum wage confirmed by statute text and DOL enforcement data",
        "FLSA statute and DOL enforcement arm both confirm $7.25/hr with consistent detail",
        "government", "what", "multi_source",
        "factual", "direct",
        context_sources=[
            {"source_id": "flsa_statute_29usc206", "source_type": "government", "authority": "official"},
            {"source_id": "dol_whd_minimum_wage_2025", "source_type": "government", "authority": "official"},
        ],
    ))

    cases.append(make_case(
        "t1_confident_hard_929", "hard", "cross_source_agreement",
        "Is 78 degrees Celsius the correct boiling point of ethanol at standard pressure?",
        [
            "The CRC Handbook of Chemistry and Physics (105th edition) lists the boiling point of ethanol (C2H5OH) as 78.37 degrees Celsius (173.07 degrees Fahrenheit) at 1 atm (101.325 kPa). Ethanol's relatively low boiling point compared to water (100 C) is due to weaker hydrogen bonding from having only one hydroxyl group versus water's two.",
            "NIST Chemistry WebBook reports ethanol's normal boiling point as 351.44 K (78.29 C) based on thermodynamic measurements. The Antoine equation parameters for ethanol (A=8.20417, B=1642.89, C=230.300) predict 78.3 C at 760 mmHg, consistent with experimental data within 0.1 C."
        ],
        "Ethanol boiling point confirmed by two independent reference sources within 0.1 C agreement",
        "CRC Handbook and NIST WebBook converge on 78.3-78.4 C with supporting thermodynamic data",
        "science", "is", "multi_source",
        "factual", "direct",
        context_sources=[
            {"source_id": "crc_handbook_105th", "source_type": "academic", "authority": "primary"},
            {"source_id": "nist_chemistry_webbook_ethanol", "source_type": "government", "authority": "official"},
        ],
    ))

    cases.append(make_case(
        "t1_confident_hard_930", "hard", "multi_source_convergence",
        "What percentage of global electricity comes from renewable sources?",
        [
            "The International Energy Agency (IEA) World Energy Outlook 2024 reports that renewable energy sources accounted for 30% of global electricity generation in 2023, with hydro contributing 15%, wind 8%, solar 5%, and biomass/geothermal 2%. This represents a 3 percentage point increase from 2022.",
            "The International Renewable Energy Agency (IRENA) Renewable Capacity Statistics 2024 confirms renewables generated approximately 29.9% of global electricity in 2023. IRENA notes that renewable capacity additions reached a record 473 GW in 2023, with solar PV alone accounting for 73% of new capacity.",
            "BloombergNEF's New Energy Outlook 2024 estimates renewables at 30.1% of global electricity, projecting this share will reach 50% by 2030 at current deployment rates and 68% by 2040."
        ],
        "Global renewable electricity share confirmed by three independent international energy bodies",
        "IEA, IRENA, and BloombergNEF all converge on approximately 30% for 2023 with complementary detail on composition and trajectory",
        "environment", "what", "multi_source",
        "factual", "direct",
        context_sources=[
            {"source_id": "iea_weo_2024", "source_type": "government", "authority": "official"},
            {"source_id": "irena_capacity_stats_2024", "source_type": "government", "authority": "official"},
            {"source_id": "bnef_neo_2024", "source_type": "industry", "authority": "primary"},
        ],
    ))

    cases.append(make_case(
        "t1_confident_hard_931", "hard", "multi_source_convergence",
        "How effective are mRNA vaccines against severe COVID-19 outcomes?",
        [
            "A New England Journal of Medicine study (2024) following 1.2 million participants found that two doses of BNT162b2 (Pfizer) reduced hospitalization from COVID-19 by 90% (95% CI: 87-93%) during the first 6 months post-vaccination, declining to 73% after 12 months.",
            "The CDC Morbidity and Mortality Weekly Report analyzing 800,000 hospital admissions confirmed mRNA vaccines (both Pfizer and Moderna) reduced ICU admission by 92% and death by 91% when the primary series was completed within the preceding 6 months. Booster doses restored protection to 94% against hospitalization.",
            "The WHO Weekly Epidemiological Record synthesizing data from 42 countries reported mRNA vaccine effectiveness against severe disease at 88-95% within 6 months of last dose, with waning to 70-80% by 12 months, consistent across Alpha, Delta, and Omicron BA.1 variants."
        ],
        "mRNA vaccine effectiveness against severe COVID confirmed by three independent health authorities",
        "NEJM, CDC, and WHO all converge on 88-95% effectiveness against severe outcomes with consistent waning timeline",
        "medicine", "how", "multi_source",
        "factual", "direct",
        context_sources=[
            {"source_id": "nejm_bnt162b2_followup_2024", "source_type": "academic", "authority": "primary"},
            {"source_id": "cdc_mmwr_mrna_hosp_2024", "source_type": "government", "authority": "official"},
            {"source_id": "who_wer_mrna_2024", "source_type": "government", "authority": "official"},
        ],
    ))

    cases.append(make_case(
        "t1_confident_hard_932", "hard", "authoritative_source",
        "What are the Miranda rights that police must read during an arrest?",
        [
            "Under Miranda v. Arizona (384 U.S. 436, 1966), law enforcement must inform individuals in custodial interrogation of four rights: (1) the right to remain silent, (2) that anything said can and will be used against them in court, (3) the right to an attorney, and (4) that if they cannot afford an attorney, one will be appointed. Failure to provide these warnings renders subsequent statements inadmissible under the exclusionary rule.",
            "The Department of Justice Law Enforcement Policy Manual reiterates these four warnings and adds that officers must obtain an explicit waiver before proceeding with questioning. The DOJ notes that Miranda applies only during custodial interrogation, not during routine traffic stops or voluntary conversations, and that public safety exceptions (New York v. Quarles, 1984) allow limited questioning without warnings when there is an immediate threat."
        ],
        "Miranda rights confirmed by Supreme Court decision and DOJ enforcement policy with scope clarifications",
        "Supreme Court ruling and DOJ policy manual both specify the same four warnings with DOJ adding waiver requirement and custodial scope",
        "law", "what", "multi_source",
        "factual", "direct",
        context_sources=[
            {"source_id": "miranda_v_arizona_384us436", "source_type": "government", "authority": "official"},
            {"source_id": "doj_le_policy_manual_ch5", "source_type": "government", "authority": "official"},
        ],
    ))

    cases.append(make_case(
        "t1_confident_hard_933", "hard", "authoritative_source",
        "What is the recommended daily sodium intake according to health authorities?",
        [
            "The World Health Organization recommends adults consume less than 2,000 mg of sodium per day (equivalent to less than 5 grams of salt), based on a systematic review of 36 cohort studies linking excess sodium to elevated blood pressure and cardiovascular risk.",
            "The American Heart Association recommends an ideal limit of 1,500 mg per day for most adults, particularly those with hypertension. Current average U.S. intake is approximately 3,400 mg per day, exceeding both the WHO and AHA guidelines by 70-127%. The AHA notes that 70% of sodium in American diets comes from processed and restaurant foods, not home cooking."
        ],
        "Sodium intake guidelines confirmed by WHO and AHA with consistent directional guidance",
        "WHO and AHA both recommend sodium reduction with specific thresholds and consistent evidence base",
        "medicine", "what", "multi_source",
        "factual", "direct",
        context_sources=[
            {"source_id": "who_sodium_guideline_2023", "source_type": "government", "authority": "official"},
            {"source_id": "aha_sodium_recommendations_2024", "source_type": "industry", "authority": "expert"},
        ],
    ))

    cases.append(make_case(
        "t1_confident_hard_934", "hard", "near_complete_evidence",
        "What factors determine mortgage interest rates for individual borrowers?",
        [
            "Mortgage interest rates for individual borrowers are determined by a combination of macroeconomic and borrower-specific factors. The Federal Reserve's federal funds rate sets the baseline, with 30-year fixed mortgage rates typically 1.5-2.5 percentage points above the 10-year Treasury yield. Credit score is the primary borrower factor: scores above 760 receive the best rates, with each 20-point decrease below 740 adding 0.125-0.25% to the rate.",
            "Loan-to-value (LTV) ratio significantly affects pricing: LTV above 80% requires private mortgage insurance and adds 0.3-0.5% to effective cost. Debt-to-income ratio above 43% typically disqualifies conventional loans. Loan type (fixed vs. ARM, conforming vs. jumbo), property type (primary vs. investment), and loan term further modify the rate. Points can buy down the rate at approximately 0.25% per point paid."
        ],
        "Comprehensive mortgage rate determinants covering macro, borrower, and loan-level factors",
        "Contexts cover nearly every major rate factor: Fed rate, credit score, LTV, DTI, loan type, and points with specific thresholds",
        "real_estate", "what", "single", "factual",
    ))

    cases.append(make_case(
        "t1_confident_hard_935", "hard", "near_complete_evidence",
        "How does soil pH affect nutrient availability for crops?",
        [
            "Soil pH is the master variable controlling nutrient availability. At pH 6.0-7.0, most macronutrients (nitrogen, phosphorus, potassium) and micronutrients reach peak availability. Below pH 5.5, aluminum and manganese become toxic to roots, phosphorus binds with iron and aluminum into insoluble forms, and calcium/magnesium leach from the root zone.",
            "Above pH 7.5, iron, zinc, manganese, and boron become increasingly unavailable due to formation of insoluble hydroxides. Phosphorus also decreases as it binds with calcium. Lime application raises pH at 1-2 tons per acre per pH unit on loam soils, while sulfur lowers pH at approximately 300 lbs per acre per unit on similar soils. Most crops perform optimally between pH 6.0 and 6.8."
        ],
        "Soil pH-nutrient relationship with specific thresholds, mechanisms, and amendment rates",
        "Contexts cover the full pH spectrum with toxicity thresholds, nutrient lockout mechanisms, and practical amendment rates",
        "agriculture", "how", "single", "causal",
    ))

    cases.append(make_case(
        "t1_confident_hard_936", "hard", "conditional_confidence",
        "Is a ketogenic diet effective for managing Type 2 diabetes?",
        [
            "A 2023 meta-analysis in Diabetes Care analyzing 12 RCTs (n=1,845) found that ketogenic diets (less than 50g carbs/day) reduced HbA1c by an average of 1.07% over 6 months compared to 0.63% for standard low-fat diets (p=0.003). Additionally, 34% of participants on keto reduced or eliminated diabetes medication versus 12% in control groups. Fasting glucose decreased by 1.2 mmol/L on average.",
            "However, effectiveness depends on several conditions: patients with Stage 3+ chronic kidney disease should avoid high-protein keto variants, adherence drops from 85% at 3 months to 45% at 12 months, and LDL cholesterol increased by an average of 10% in 40% of participants. Supervised medical keto programs with regular lipid monitoring showed the best outcomes. The American Diabetes Association recognizes low-carb diets as a viable option but recommends individualized approaches based on kidney function, lipid profile, and medication regimen."
        ],
        "Ketogenic diet for T2D with clear glycemic benefits conditioned on kidney function, lipid monitoring, and adherence",
        "Evidence supports HbA1c improvement but effectiveness depends on kidney status, cholesterol response, long-term adherence, and medical supervision",
        "medicine", "is", "single", "evaluative",
    ))

    cases.append(make_case(
        "t1_confident_hard_937", "hard", "step_by_step",
        "How do you file a provisional patent application with the USPTO?",
        [
            "Step 1: Prepare a detailed written description of your invention including all embodiments and variations. No formal claims are required for a provisional application. Include drawings or diagrams that illustrate the invention. Step 2: Complete USPTO Form SB/16 (Provisional Application for Patent Cover Sheet) with inventor names, title of invention, correspondence address, and entity status (micro, small, or large).",
            "Step 3: File electronically through USPTO's Patent Center (patentcenter.uspto.gov) or by mail to Commissioner for Patents, P.O. Box 1450, Alexandria, VA 22313-1450. Step 4: Pay the filing fee: $160 for micro entities, $320 for small entities, $640 for large entities (2024 rates). Step 5: Receive your provisional application number and filing date, which establishes your priority date. The provisional expires after 12 months; you must file a non-provisional application before expiration to benefit from the priority date."
        ],
        "Complete step-by-step USPTO provisional patent filing procedure with forms, fees, and deadlines",
        "Contexts provide numbered sequential steps covering preparation, forms, filing methods, fee schedule, and critical 12-month deadline",
        "law", "how", "single", "procedural",
    ))

    cases.append(make_case(
        "t1_confident_hard_938", "hard", "step_by_step",
        "How is a bill passed into law by the United States Congress?",
        [
            "Step 1: A bill is introduced by a member of the House or Senate and assigned a number (H.R. for House, S. for Senate). Step 2: The bill is referred to the relevant standing committee (e.g., Judiciary, Finance), which may hold hearings and mark up the bill with amendments. Step 3: If approved by committee, the bill goes to the full chamber floor for debate and vote. The House uses the Rules Committee to set debate terms; the Senate allows unlimited debate unless cloture is invoked (60 votes).",
            "Step 4: If passed by the originating chamber, the bill moves to the other chamber and repeats the committee/floor process. Step 5: If both chambers pass different versions, a conference committee reconciles them into a single text that both chambers must approve. Step 6: The enrolled bill goes to the President, who has 10 days to sign (becomes law), veto (returns to Congress, overridable by two-thirds vote in both chambers), or take no action (becomes law if Congress is in session, pocket veto if Congress adjourns)."
        ],
        "Complete legislative process from bill introduction through presidential action",
        "Six sequential steps cover introduction, committee action, floor vote, bicameral reconciliation, and presidential options with specific procedural details",
        "government", "how", "single", "procedural",
    ))

    cases.append(make_case(
        "t1_confident_hard_939", "hard", "definitional",
        "Is force majeure a valid defense for non-performance in contract law?",
        [
            "Force majeure (French for 'superior force') is a contractual provision that excuses one or both parties from performance when extraordinary events beyond their control prevent fulfillment. Under the Uniform Commercial Code Section 2-615 and common law principles, qualifying events typically include natural disasters, war, government actions, epidemics, and embargoes.",
            "Three elements must be established: (1) the event was unforeseeable at the time of contracting, (2) the event was beyond the affected party's control, and (3) the party took reasonable steps to mitigate the impact. Unlike frustration of purpose, force majeure must be explicitly included in the contract to be invoked. Courts interpret force majeure clauses narrowly, requiring the triggering event to be specifically listed or closely analogous to listed events."
        ],
        "Legal definition of force majeure with statutory basis, required elements, and judicial interpretation standards",
        "Contexts define the term, cite UCC authority, specify three required elements, and distinguish from related doctrines",
        "law", "is", "single", "factual",
    ))

    cases.append(make_case(
        "t1_confident_hard_940", "hard", "definitional",
        "What is the difference between Type I and Type II statistical errors?",
        [
            "A Type I error (false positive, alpha) occurs when a null hypothesis that is actually true is incorrectly rejected. The probability of a Type I error is the significance level (alpha), conventionally set at 0.05. For example, concluding a drug is effective when it actually has no effect. A Type II error (false negative, beta) occurs when a null hypothesis that is actually false fails to be rejected. The probability of a Type II error is beta, and statistical power (1 - beta) is the ability to detect a true effect.",
            "The two errors have an inverse relationship at fixed sample size: reducing alpha (stricter threshold) increases beta, and vice versa. Increasing sample size reduces both simultaneously. In medical testing, Type I errors lead to unnecessary treatments (cost/harm), while Type II errors mean missed diagnoses (undetected disease). The acceptable balance depends on context: criminal trials prioritize avoiding Type I (convicting the innocent), while screening tests prioritize avoiding Type II (missing disease)."
        ],
        "Statistical error types defined with probabilities, relationship, practical examples, and context-dependent tradeoffs",
        "Complete definitions with alpha/beta notation, inverse relationship, sample size effect, and domain-specific consequence analysis",
        "education", "what", "single", "comparative",
    ))

    cases.append(make_case(
        "t1_confident_hard_941", "hard", "technical_documented",
        "How does TLS 1.3 perform a handshake compared to TLS 1.2?",
        [
            "TLS 1.3 reduces the handshake from two round trips (TLS 1.2) to one. In TLS 1.2, the client sends ClientHello, the server responds with ServerHello plus certificate, the client sends key exchange and ChangeCipherSpec, and the server confirms. In TLS 1.3, the client sends ClientHello with key_share extension containing Diffie-Hellman parameters in the first message.",
            "TLS 1.3 eliminates insecure cipher suites: no RSA key exchange (forward secrecy mandatory), no CBC mode (only AEAD ciphers: AES-128-GCM, AES-256-GCM, ChaCha20-Poly1305). Zero-RTT (0-RTT) resumption allows previously connected clients to send encrypted data in the first packet, though this is vulnerable to replay attacks. Measurements show TLS 1.3 handshake completes in 50-100 ms versus 150-300 ms for TLS 1.2."
        ],
        "TLS version comparison with precise protocol differences in handshake rounds, cipher suites, and latency",
        "Contexts detail the exact handshake flow differences, removed features, mandatory requirements, and measured performance improvements",
        "technology", "how", "single", "comparative",
    ))

    cases.append(make_case(
        "t1_confident_hard_942", "hard", "technical_documented",
        "What is the CAP theorem and how does it constrain distributed databases?",
        [
            "The CAP theorem, proved by Gilbert and Lynch in 2002 (based on Brewer's 2000 conjecture), states that a distributed data store can provide at most two of three guarantees simultaneously: Consistency (every read receives the most recent write), Availability (every request receives a non-error response), and Partition tolerance (the system continues operating despite network partitions between nodes).",
            "In practice, partition tolerance is non-negotiable in distributed systems (networks fail), so the real choice is between CP and AP systems. CP systems (e.g., HBase, MongoDB with majority write concern) reject requests during partitions to maintain consistency. AP systems (e.g., Cassandra, DynamoDB) continue serving requests during partitions but may return stale data. Modern systems like CockroachDB and Spanner use synchronized clocks to minimize the consistency-availability tradeoff window."
        ],
        "CAP theorem definition with formal provenance and practical database system classification",
        "Contexts provide the theorem statement, formal proof citation, practical CP/AP classification with real database examples, and modern approaches",
        "technology", "what", "single", "factual",
    ))

    cases.append(make_case(
        "t1_confident_hard_943", "hard", "opposing_with_consensus",
        "Is remote work more productive than in-office work?",
        [
            "Stanford economist Nicholas Bloom's study of 16,000 workers at Ctrip (2015) found remote workers were 13% more productive, worked 9.5% longer hours, and had 50% lower attrition. A 2023 follow-up across 30,000 workers confirmed hybrid (2-3 days remote) maintained productivity while improving satisfaction. Microsoft's analysis of 61,000 employees found no productivity difference between remote and office workers when measured by output rather than hours logged.",
            "However, a 2023 working paper from the Federal Reserve Bank of New York found fully remote workers were 10-20% less productive in collaborative tasks requiring real-time coordination. Several CEOs (JPMorgan's Jamie Dimon, Tesla's Elon Musk) have mandated return-to-office, citing innovation loss and mentorship difficulties, though these claims lack peer-reviewed support."
        ],
        "Remote work productivity evidence where peer-reviewed research favors remote/hybrid over executive opinion",
        "Multiple peer-reviewed studies support remote productivity; opposition comes from executive anecdote and one Fed paper limited to collaborative tasks only",
        "hr_workplace", "is", "single", "evaluative",
    ))

    cases.append(make_case(
        "t1_confident_hard_944", "hard", "opposing_with_consensus",
        "Should governments implement sugar taxes to reduce obesity?",
        [
            "Mexico's peso-per-liter soda tax (2014) reduced sugary drink purchases by 7.6% in the first year and 9.7% by the second year (BMJ, 2016). Berkeley, California's penny-per-ounce tax reduced consumption by 21% in low-income neighborhoods (American Journal of Public Health, 2019). The UK's tiered sugar levy prompted manufacturers to reformulate, reducing average sugar content by 29% before the tax even took effect. The WHO endorses sugar taxes as evidence-based obesity prevention.",
            "The American Beverage Association argues sugar taxes are regressive, disproportionately burdening low-income consumers who spend a higher share of income on food. Industry-funded research from the National Bureau of Economic Research found consumers shifted to untaxed sugary products (juices, flavored milk), suggesting limited net health benefit. The Tax Foundation notes compliance costs for small businesses."
        ],
        "Sugar tax policy question where public health evidence and WHO endorsement outweigh industry-funded counter-evidence",
        "Multiple peer-reviewed studies and WHO endorsement support effectiveness; opposition is largely industry-funded or addresses regressivity (a separate policy concern, not efficacy)",
        "government", "should", "single", "evaluative",
    ))

    cases.append(make_case(
        "t1_confident_hard_945", "hard", "direct_factual",
        "When was the Treaty of Westphalia signed and what did it establish?",
        [
            "The Peace of Westphalia was signed on October 24, 1648, comprising two treaties: the Treaty of Osnabrueck and the Treaty of Muenster. It ended the Thirty Years' War (1618-1648) in the Holy Roman Empire and the Eighty Years' War (1568-1648) between Spain and the Dutch Republic. The treaties established the principle of state sovereignty (cuius regio, eius religio extended to Calvinism), recognized the independence of the Netherlands and Swiss Confederacy, and redrew territorial boundaries across Central Europe."
        ],
        "Precise historical date, component treaties, wars ended, and principles established by Westphalia",
        "Context provides exact date, both treaties, both wars concluded, sovereignty principle, and territorial outcomes",
        "history", "when", "single", "temporal",
    ))

    cases.append(make_case(
        "t1_confident_hard_946", "hard", "direct_factual",
        "Who developed the theory of general relativity and when was it published?",
        [
            "Albert Einstein developed the theory of general relativity, presenting the final field equations to the Prussian Academy of Sciences on November 25, 1915. The theory was published in Annalen der Physik in March 1916 under the title 'Die Grundlage der allgemeinen Relativitaetstheorie' (The Foundation of the General Theory of Relativity). It describes gravity not as a force but as the curvature of spacetime caused by mass and energy, expressed mathematically as G_mu_nu + Lambda*g_mu_nu = (8*pi*G/c^4)*T_mu_nu.",
            "The Nobel Foundation records confirm Einstein received the 1921 Nobel Prize in Physics (awarded in 1922), though notably for the photoelectric effect rather than general relativity, as the latter was still considered insufficiently verified experimentally at that time. Arthur Eddington's 1919 solar eclipse expedition provided the first observational confirmation of general relativity by measuring starlight deflection near the Sun consistent with Einstein's predictions."
        ],
        "General relativity attribution confirmed by Annalen der Physik publication record and Nobel Foundation archives",
        "Primary publication and Nobel Foundation both attribute the theory to Einstein with complementary historical verification detail",
        "history", "who", "multi_source",
        "factual", "direct",
        context_sources=[
            {"source_id": "annalen_der_physik_1916_vol49", "source_type": "academic", "authority": "primary"},
            {"source_id": "nobel_foundation_einstein_1921", "source_type": "academic", "authority": "official"},
        ],
    ))

    cases.append(make_case(
        "t1_confident_hard_947", "hard", "step_by_step",
        "How do you perform CPR on an adult according to the American Heart Association guidelines?",
        [
            "Step 1: Check the scene for safety, then check the person for responsiveness by tapping their shoulders and shouting. Step 2: Call 911 (or direct someone to call) and get an AED if available. Step 3: Check for breathing for no more than 10 seconds; look for chest rise, listen for breath sounds. If no normal breathing, begin CPR.",
            "Step 4: Place the heel of one hand on the center of the chest (lower half of the sternum), place the other hand on top, interlace fingers. Step 5: Compress the chest at least 2 inches (5 cm) deep but no more than 2.4 inches (6 cm) at a rate of 100-120 compressions per minute. Allow full chest recoil between compressions. Step 6: After 30 compressions, give 2 rescue breaths (tilt head, lift chin, pinch nose, seal mouth, deliver 1-second breaths watching for chest rise). Continue 30:2 cycle until EMS arrives or an AED is available."
        ],
        "AHA-compliant adult CPR procedure with six numbered steps including specific depth, rate, and ratio",
        "Sequential steps cover scene safety, activation, assessment, hand placement, compression specs (depth, rate, recoil), and ventilation ratio",
        "medicine", "how", "single", "procedural",
    ))

    cases.append(make_case(
        "t1_confident_hard_948", "hard", "multi_source_convergence",
        "What is the average global temperature increase since pre-industrial times?",
        [
            "NASA's Goddard Institute for Space Studies (GISS) reports that global average surface temperature has increased by approximately 1.2 degrees Celsius (2.2 degrees Fahrenheit) since the late 19th century, with most of the warming occurring in the past 50 years. The 10 warmest years on record have all occurred since 2010.",
            "The IPCC Sixth Assessment Report (2021) states that global surface temperature was 1.09 degrees C higher in 2011-2020 than in 1850-1900, with a likely range of 0.95-1.20 degrees C. Human influence has warmed the climate at a rate unprecedented in at least the last 2,000 years.",
            "The UK Met Office HadCRUT5 dataset shows a warming of 1.19 degrees C in 2023 relative to the 1850-1900 baseline, making 2023 the warmest year on record. Combined with NOAA's independent analysis showing 1.18 degrees C, four independent temperature records agree within 0.1 degrees C."
        ],
        "Global temperature rise confirmed by four independent datasets (NASA, IPCC, Met Office, NOAA) within tight agreement",
        "NASA GISS, IPCC AR6, HadCRUT5, and NOAA all converge on approximately 1.1-1.2 degrees C warming since pre-industrial",
        "environment", "what", "multi_source",
        "factual", "direct",
        context_sources=[
            {"source_id": "nasa_giss_temp_2024", "source_type": "government", "authority": "official"},
            {"source_id": "ipcc_ar6_wg1_ch2", "source_type": "government", "authority": "official"},
            {"source_id": "metoffice_hadcrut5_2024", "source_type": "government", "authority": "official"},
        ],
    ))

    cases.append(make_case(
        "t1_confident_hard_949", "hard", "contradiction_resolved",
        "Does moderate alcohol consumption provide cardiovascular benefits?",
        [
            "For decades, studies including the Framingham Heart Study reported a J-shaped curve where moderate drinkers (1-2 drinks/day) had lower cardiovascular mortality than abstainers. A 2006 meta-analysis of 34 studies in Archives of Internal Medicine found a 25% reduction in heart disease risk for moderate drinkers.",
            "A landmark 2023 study in JAMA Network Open analyzing 371,463 participants revealed that the J-curve was an artifact of reference group bias: former drinkers who quit due to illness were classified as 'abstainers,' inflating that group's mortality. After correcting for this 'sick quitter' bias and adjusting for confounders, no level of alcohol consumption showed cardiovascular benefit. Even moderate drinking increased risk of atrial fibrillation by 16% and cardiomyopathy by 8%."
        ],
        "Decades-old moderate-drinking benefit resolved as statistical artifact by corrected 2023 analysis",
        "Initial context presents the classic J-curve finding; second context resolves it by identifying reference group bias and showing corrected analysis finds no benefit",
        "medicine", "does", "single", "evaluative",
    ))

    cases.append(make_case(
        "t1_confident_hard_950", "hard", "different_framing",
        "Why do housing prices vary so dramatically between cities?",
        [
            "From a supply-side perspective, housing prices are driven by construction constraints. Cities with geographic barriers (San Francisco's peninsula, Manhattan's island) and restrictive zoning (minimum lot sizes, height limits, single-family mandates) have housing supply elasticities below 1.0, meaning a 10% demand increase raises prices by more than 10%. Houston, with minimal zoning and flat terrain, has a supply elasticity of 2.4 and consistently lower prices.",
            "From a demand-side perspective, housing prices reflect local economic productivity. Cities with high-wage industries (tech in San Francisco, finance in New York) attract workers bidding up prices. Glaeser and Gyourko (2018) showed that 60% of inter-city price variation is explained by the interaction of labor market wage premiums with local housing supply elasticity, not demand or supply alone."
        ],
        "Housing price variation explained through supply and demand framings that converge on supply-demand interaction",
        "Supply-side context covers zoning/geography constraints; demand-side covers wage premiums; both converge on the interaction as the key explanatory variable",
        "real_estate", "why", "single", "causal",
    ))

    cases.append(make_case(
        "t1_confident_hard_951", "hard", "technical_documented",
        "How does a lithium-ion battery charge and discharge at the chemical level?",
        [
            "During charging, an external voltage forces lithium ions (Li+) to deintercalate from the cathode (typically LiCoO2, LiFePO4, or NMC) and migrate through the electrolyte to intercalate into the graphite anode layers. Electrons flow through the external circuit from cathode to anode. The anode reaction is: xLi+ + xe- + 6C -> LixC6. The cathode reaction is: LiCoO2 -> Li(1-x)CoO2 + xLi+ + xe-.",
            "During discharge, the process reverses spontaneously: lithium ions migrate from anode to cathode through the electrolyte while electrons flow through the external circuit from anode to cathode, powering the connected device. The solid electrolyte interphase (SEI) layer on the anode is critical for longevity; it forms during the first charge cycle and prevents further electrolyte decomposition while remaining permeable to Li+ ions."
        ],
        "Lithium-ion battery electrochemistry with charge/discharge reactions and SEI layer function",
        "Contexts provide both half-reactions, ion/electron flow directions for both modes, and the SEI layer mechanism for battery longevity",
        "technology", "how", "single", "procedural",
    ))

    cases.append(make_case(
        "t1_confident_hard_952", "hard", "technical_documented",
        "What is the difference between OAuth 2.0 authorization code flow and implicit flow?",
        [
            "In OAuth 2.0 Authorization Code flow, the client receives a short-lived authorization code from the authorization server after user consent, then exchanges this code for an access token via a back-channel (server-to-server) POST request including the client_secret. This two-step process keeps the access token out of the browser's URL/history. Tokens can be long-lived because the client_secret authenticates the exchange.",
            "The Implicit flow was designed for public clients (SPAs) that cannot securely store a client_secret. The access token is returned directly in the URL fragment (#access_token=...) after user consent, skipping the code exchange step. However, this exposes the token to the browser and URL history. RFC 6819 and the OAuth 2.0 Security BCP (RFC 9700) now recommend against Implicit flow, advising public clients use Authorization Code with PKCE (Proof Key for Code Exchange) instead."
        ],
        "OAuth 2.0 flow comparison with security implications and current best practices",
        "Contexts detail both flows step-by-step, explain the security difference (back-channel vs. fragment), and note the deprecation of Implicit in favor of PKCE",
        "social_media", "what", "single", "comparative",
    ))

    cases.append(make_case(
        "t1_confident_hard_953", "hard", "step_by_step",
        "How do you properly conduct a soil test for a farm field?",
        [
            "Step 1: Determine sampling pattern - use a zigzag or grid pattern across the field, taking 15-20 cores per composite sample. Separate areas with different soil types, cropping history, or topography into distinct sampling zones. Step 2: Collect samples at the appropriate depth: 0-6 inches for no-till fields, 0-8 inches for conventional tillage. Use a clean soil probe or auger. Step 3: Mix all cores for each zone thoroughly in a clean plastic bucket, breaking up clumps, and take a 1-pint subsample.",
            "Step 4: Air-dry the subsample at room temperature (not in direct sunlight or oven) or deliver to the lab within 24 hours if testing for nitrogen (nitrate is volatile). Step 5: Submit to a certified laboratory (check state extension service for accredited labs) with field identification, crop history, and planned crop. Step 6: Interpret results against regional guidelines: compare pH, organic matter, P, K, Ca, Mg, and micronutrients to crop-specific sufficiency ranges. Apply amendments based on lab recommendations, typically 60-90 days before planting."
        ],
        "Complete six-step soil testing procedure from sampling design through amendment application",
        "Sequential steps cover sampling pattern, depth, compositing, handling, lab selection, and interpretation with specific quantitative guidance",
        "agriculture", "how", "single", "procedural",
    ))

    cases.append(make_case(
        "t1_confident_hard_954", "hard", "definitional",
        "What is cognitive dissonance in psychology?",
        [
            "Cognitive dissonance, first described by Leon Festinger in 1957, is the psychological discomfort experienced when a person holds two or more contradictory beliefs, values, or attitudes simultaneously, or when behavior conflicts with beliefs. The theory predicts that individuals are motivated to reduce this dissonance through one of three strategies: changing the dissonant belief, adding consonant cognitions to outweigh the dissonance, or trivializing the importance of the conflicting element.",
            "Festinger's classic study involved participants performing a boring task and then being paid $1 or $20 to tell the next participant it was enjoyable. Those paid $1 (insufficient justification) rated the task as more enjoyable than those paid $20, because they needed to change their belief about the task to reduce dissonance. This insufficient justification paradigm remains foundational in social psychology, replicated across cultures with effect sizes of d = 0.5 to 0.8."
        ],
        "Cognitive dissonance definition with original theorist, three reduction strategies, and paradigmatic experiment",
        "Contexts provide the formal definition, Festinger's attribution, reduction mechanisms, and the classic $1/$20 experimental demonstration",
        "psychology", "what", "single", "factual",
    ))

    cases.append(make_case(
        "t1_confident_hard_955", "hard", "multi_source_convergence",
        "What is the gravitational constant G and how is it measured?",
        [
            "NIST's CODATA 2018 recommended value for the gravitational constant is G = 6.67430 x 10^-11 m^3 kg^-1 s^-2, with a relative standard uncertainty of 2.2 x 10^-5 (22 parts per million), making it the least precisely known fundamental constant. This uncertainty is 10,000 times larger than that of Planck's constant.",
            "The Bureau International des Poids et Mesures (BIPM) measured G using two independent methods: a torsion balance (Cavendish-type) and a beam balance, obtaining 6.67559 and 6.67407 x 10^-11 respectively. The discrepancy between methods highlights the experimental difficulty: G requires measuring extremely weak gravitational forces between laboratory masses, with systematics from density inhomogeneities and seismic noise.",
            "The Royal Society's 2014 review of 300 years of G measurements (from Cavendish's 1798 experiment yielding 6.74 x 10^-11 to modern interferometric methods) confirmed that G remains the fundamental constant with the largest measurement uncertainty, with modern values clustering between 6.672 and 6.676 x 10^-11."
        ],
        "Gravitational constant value and measurement challenges confirmed by three metrology sources spanning 300 years of data",
        "NIST CODATA, BIPM independent measurements, and Royal Society historical review all converge on G's value and uniquely large uncertainty among fundamental constants",
        "science", "what", "multi_source",
        "factual", "direct",
        context_sources=[
            {"source_id": "nist_codata_2018_g", "source_type": "government", "authority": "official"},
            {"source_id": "bipm_g_measurement_2014", "source_type": "government", "authority": "official"},
            {"source_id": "royal_society_g_review_2014", "source_type": "academic", "authority": "primary"},
        ],
    ))

    cases.append(make_case(
        "t1_confident_hard_956", "hard", "contradiction_resolved",
        "Is breakfast the most important meal of the day for weight management?",
        [
            "The commonly cited belief that breakfast is essential for weight management stems from observational studies, such as the National Weight Control Registry finding that 78% of successful weight maintainers eat breakfast daily. A 2013 review in the American Journal of Clinical Nutrition argued that breakfast-skipping was associated with higher BMI and weight gain.",
            "However, randomized controlled trials tell a different story. A 2019 BMJ systematic review of 13 RCTs found that breakfast eaters consumed an average of 260 calories more per day than breakfast skippers, with no significant difference in metabolic rate. The earlier observational association was confounded by healthy-user bias: people who eat breakfast also tend to exercise more, smoke less, and drink less alcohol. The evidence does not support breakfast as uniquely important for weight management compared to total daily caloric intake."
        ],
        "Breakfast-weight myth resolved by distinguishing observational confounding from RCT evidence",
        "Observational data seemed supportive but RCTs revealed the association was confounded; second context directly resolves the contradiction",
        "food", "is", "single", "evaluative",
    ))

    cases.append(make_case(
        "t1_confident_hard_957", "hard", "authoritative_source",
        "Who holds the world record for the men's 100-metre sprint?",
        [
            "World Athletics, the governing body for international track and field, records the men's 100-metre world record as 9.58 seconds, set by Usain Bolt (Jamaica) at the 2009 World Championships in Berlin, Germany on August 16, 2009. The previous record of 9.69 seconds was also held by Bolt, set at the 2008 Beijing Olympics.",
            "The International Olympic Committee's official records confirm Bolt's 9.58 seconds as the standing world record. Bolt's 9.58 represents a 1.6% improvement over his already historic Olympic time and is the largest single improvement in the 100m record since electronic timing began in 1977. His reaction time of 0.146 seconds and top speed of 44.72 km/h (12.42 m/s) at the 65-metre mark were captured by Laveg laser speed guns."
        ],
        "100m world record confirmed by World Athletics and IOC with biomechanical measurement detail",
        "Both governing bodies confirm 9.58 seconds with complementary detail on reaction time and peak velocity measurement",
        "sports", "who", "multi_source",
        "factual", "direct",
        context_sources=[
            {"source_id": "world_athletics_records_db", "source_type": "industry", "authority": "official"},
            {"source_id": "ioc_berlin_2009_results", "source_type": "industry", "authority": "official"},
        ],
    ))

    cases.append(make_case(
        "t1_confident_hard_958", "hard", "different_framing",
        "How does social media affect adolescent mental health?",
        [
            "From a clinical psychology perspective, a 2023 meta-analysis in JAMA Pediatrics of 87 studies (n=159,425 adolescents) found that heavy social media use (more than 3 hours daily) was associated with double the risk of depression and anxiety symptoms (OR 2.1, 95% CI 1.7-2.5). The mechanisms include social comparison via curated self-presentation, cyberbullying exposure (experienced by 37% of teens), and sleep displacement from nighttime scrolling disrupting circadian rhythms.",
            "From a developmental neuroscience perspective, the adolescent brain's prefrontal cortex (responsible for impulse control and risk assessment) is not fully developed until age 25, while the reward-sensitive ventral striatum is highly active. Social media's variable-ratio reinforcement schedule (unpredictable likes, comments) exploits this neurological immaturity, triggering dopamine release patterns similar to slot machines. MRI studies show heavy teen social media users have altered activation in the amygdala and anterior cingulate cortex during social feedback."
        ],
        "Social media-teen mental health impacts framed through clinical epidemiology and developmental neuroscience lenses",
        "Both framings converge on harm but from different angles: clinical data quantifies outcomes, neuroscience explains the biological vulnerability mechanisms",
        "psychology", "how", "single", "causal",
    ))

    cases.append(make_case(
        "t1_confident_hard_959", "hard", "conditional_confidence",
        "Is electric vehicle ownership cheaper than gasoline vehicles over a typical ownership period?",
        [
            "The U.S. Department of Energy's Alternative Fuels Data Center calculates that EVs cost an average of $0.04 per mile for electricity versus $0.12 per mile for gasoline (based on national average electricity rate of $0.16/kWh and gasoline at $3.50/gallon with 30 MPG). Over 150,000 miles, this saves approximately $12,000 in fuel costs alone. EV maintenance costs are 40% lower due to fewer moving parts (no oil changes, no transmission fluid, regenerative braking extending brake life to 200,000+ miles).",
            "However, total cost of ownership depends on several conditions: purchase price premium ($5,000-$15,000 for comparable EVs versus ICE), federal tax credit availability ($7,500 for qualifying models as of 2024), insurance premiums (8-12% higher for EVs due to repair costs), battery degradation (average 12% capacity loss over 200,000 miles, replacement cost $8,000-$15,000), and home charging capability (home charger installation $500-$2,500). Breakeven typically occurs at 3-5 years for owners with home charging and available tax credits."
        ],
        "EV cost comparison with clear savings quantified alongside conditional factors that affect breakeven",
        "Fuel and maintenance savings are clearly quantified, but total cost depends on stated conditions (price premium, tax credits, home charging, battery life)",
        "transportation", "is", "single", "evaluative",
    ))

    cases.append(make_case(
        "t1_confident_hard_960", "hard", "quantitative_answer",
        "What is the average depth of the world's oceans?",
        [
            "NOAA's National Centers for Environmental Information, using the ETOPO 2022 global relief model derived from satellite altimetry and ship-based sonar surveys, calculates the average depth of the world's oceans at 3,688 metres (12,100 feet). The Pacific Ocean is the deepest on average at 4,280 m, followed by the Indian Ocean at 3,741 m, the Southern Ocean at 3,270 m, the Atlantic at 3,332 m, and the Arctic at 1,205 m.",
            "The total volume of the oceans is approximately 1.335 billion cubic kilometres, covering 361 million square kilometres (70.8% of Earth's surface). The maximum depth is 10,935 m at the Challenger Deep in the Mariana Trench, measured by the Trieste bathyscaphe in 1960 and confirmed by Victor Vescovo's DSV Limiting Factor expedition in 2019."
        ],
        "Ocean depth statistics from NOAA with per-ocean averages, volume, coverage, and maximum depth",
        "NOAA-sourced data provides precise global average (3,688 m), per-ocean breakdown, total volume, and extreme depth record",
        "environment", "what", "single", "factual",
    ))

    cases.append(make_case(
        "t1_confident_hard_961", "hard", "step_by_step",
        "How do you set up a drip irrigation system for a vegetable garden?",
        [
            "Step 1: Measure your garden layout and create a plan showing bed locations, distances from water source, and plant spacing. Step 2: Install a backflow preventer at the spigot to protect potable water, followed by a filter (150-mesh for drip) and a pressure regulator (typically set to 25 PSI for most drip systems). Step 3: Run 1/2-inch polyethylene mainline tubing from the spigot along the length of the garden, securing with stakes every 3 feet.",
            "Step 4: Punch holes in the mainline at each bed location and attach 1/4-inch drip line or emitter tubing using barbed connectors. Use 0.5 GPH emitters for most vegetables, spaced 12 inches apart for row crops or 18 inches for larger plants like tomatoes. Step 5: Close the end of each line with a figure-8 end clamp or flush cap. Step 6: Test the system by running water for 15 minutes, checking each emitter for flow, and inspecting connections for leaks. Program the timer for 30-45 minutes every other day in summer, adjusting based on soil moisture readings."
        ],
        "Complete drip irrigation setup with six steps covering hardware, assembly, emitter selection, and scheduling",
        "Sequential steps from planning through testing with specific hardware specs (mesh, PSI, GPH, spacing) and operational parameters",
        "agriculture", "how", "single", "procedural",
    ))

    # ── medium cases: t1_confident_medium_910 .. t1_confident_medium_954 (45) ──

    cases.append(make_case(
        "t1_confident_medium_910", "medium", "technical_documented",
        "Does an HTTP 403 status code mean the server denied access?",
        [
            "HTTP status code 403 Forbidden indicates that the server understood the request but refuses to authorize it. Unlike 401 Unauthorized, which means authentication is missing or invalid, 403 means the client's identity is known but they lack sufficient permissions. Re-authenticating will not help. Common causes include IP-based access restrictions, directory listing disabled on web servers, or insufficient file permissions on the server filesystem."
        ],
        "HTTP 403 definition distinguishing it from 401 with common causes",
        "Context precisely defines 403, contrasts with 401, and lists practical causes",
        "technology", "does", "single", "factual",
    ))

    cases.append(make_case(
        "t1_confident_medium_911", "medium", "technical_documented",
        "How does DNS resolution work when you type a URL in a browser?",
        [
            "When you enter a URL, the browser first checks its local DNS cache, then the operating system's resolver cache. If no cached record exists, the OS queries the configured recursive DNS resolver (e.g., ISP's server or 8.8.8.8). The recursive resolver queries root name servers, which direct it to the appropriate TLD server (.com, .org), which in turn directs it to the authoritative name server for the domain. The authoritative server returns the IP address, which propagates back through the chain and gets cached at each level according to the record's TTL value."
        ],
        "DNS resolution chain from browser cache to authoritative server with caching behavior",
        "Context traces the complete resolution path with each tier and caching mechanism explained",
        "technology", "how", "single", "procedural",
    ))

    cases.append(make_case(
        "t1_confident_medium_912", "medium", "clear_explanation",
        "Why do leaves change color in autumn?",
        [
            "During autumn, shorter daylight hours trigger trees to stop producing chlorophyll, the green pigment that masks other pigments present in the leaf. As chlorophyll breaks down, yellow and orange carotenoid pigments (always present but hidden) become visible. Red and purple anthocyanin pigments are newly synthesized from sugars trapped in the leaf after the abscission layer forms at the leaf stem, blocking sugar transport. Cool nights and sunny days maximize anthocyanin production."
        ],
        "Leaf color change explained through pigment chemistry and photoperiod triggers",
        "Context covers chlorophyll breakdown, carotenoid unmasking, anthocyanin synthesis, and environmental conditions",
        "agriculture", "why", "single", "causal",
    ))

    cases.append(make_case(
        "t1_confident_medium_913", "medium", "clear_explanation",
        "How does compound interest differ from simple interest?",
        [
            "Simple interest is calculated only on the original principal: I = P * r * t, where P is principal, r is annual rate, and t is time in years. Compound interest is calculated on the principal plus all accumulated interest: A = P * (1 + r/n)^(n*t), where n is the compounding frequency. For example, $10,000 at 5% for 10 years yields $15,000 with simple interest ($5,000 earned) versus $16,288.95 with annual compounding ($6,288.95 earned). The difference grows dramatically over longer periods and higher rates."
        ],
        "Simple vs compound interest with formulas and concrete dollar-amount example",
        "Context provides both formulas, a worked example showing the difference, and notes the compounding effect growth",
        "finance", "how", "single", "comparative",
    ))

    cases.append(make_case(
        "t1_confident_medium_914", "medium", "contradiction_resolved",
        "Are eggs healthy or unhealthy for heart health?",
        [
            "For decades, eggs were considered harmful for heart health because one large egg contains about 186 mg of dietary cholesterol, and the American Heart Association recommended limiting cholesterol to 300 mg per day. A 1984 Time Magazine cover declared eggs dangerous.",
            "Modern research has largely overturned this view. A 2020 meta-analysis in the BMJ of 17 studies (505,681 participants) found that consuming up to one egg per day was not associated with increased cardiovascular risk (RR 0.98, 95% CI 0.93-1.03). The 2020 Dietary Guidelines for Americans removed the 300 mg cholesterol limit, noting that dietary cholesterol has a minimal effect on blood cholesterol for most people. Eggs are now recognized as a nutrient-dense food providing 6g protein, choline, and vitamins D and B12."
        ],
        "Egg-heart health contradiction resolved by updated dietary science overturning cholesterol fears",
        "Old guidance restricted eggs based on cholesterol; modern meta-analyses and updated dietary guidelines resolved the contradiction",
        "food", "is", "single", "evaluative",
    ))

    cases.append(make_case(
        "t1_confident_medium_915", "medium", "contradiction_resolved",
        "Does cracking your knuckles cause arthritis?",
        [
            "A common belief holds that cracking knuckles causes arthritis. This belief is reinforced by the unpleasant sound and parental warnings. Some early case reports suggested a link between habitual knuckle cracking and joint swelling.",
            "Multiple scientific studies have debunked this claim. Dr. Donald Unger cracked the knuckles of his left hand twice daily for 60 years while leaving the right hand uncracked, finding no arthritis difference (published in Arthritis & Rheumatism, 1998; awarded the 2009 Ig Nobel Prize). A radiographic study of 215 participants (Deweber et al., 2011) found no correlation between knuckle cracking frequency and hand osteoarthritis. The cracking sound is caused by cavitation bubbles forming in synovial fluid during joint separation, not by cartilage damage."
        ],
        "Knuckle-cracking arthritis myth debunked by controlled self-experiment and radiographic study",
        "Belief in harm is stated then directly contradicted by Unger's 60-year experiment and Deweber's radiographic evidence",
        "social_media", "does", "single", "evaluative",
    ))

    cases.append(make_case(
        "t1_confident_medium_916", "medium", "opposing_with_consensus",
        "Is organic food significantly more nutritious than conventional food?",
        [
            "The Stanford University Center for Health Policy conducted a comprehensive meta-analysis of 237 studies (2012, Annals of Internal Medicine) and found no strong evidence that organic foods are significantly more nutritious than conventional alternatives. Nutrient levels (vitamins, minerals, protein) showed no clinically meaningful differences. A 2020 follow-up by the same group confirmed these findings across an additional 150 studies.",
            "Organic industry advocates and some smaller studies claim higher antioxidant levels (20-40% more phenolic compounds in some organic fruits). The Organic Trade Association cites a 2014 British Journal of Nutrition meta-analysis showing higher antioxidant concentrations, though the clinical significance of these differences for health outcomes remains undemonstrated."
        ],
        "Organic vs conventional nutrition where large meta-analyses find no meaningful difference despite industry claims",
        "Stanford's large meta-analysis (237 studies) finds no nutritional advantage; smaller pro-organic studies show antioxidant differences of unclear clinical significance",
        "food", "is", "single", "evaluative",
    ))

    cases.append(make_case(
        "t1_confident_medium_917", "medium", "opposing_with_consensus",
        "Should students be assigned homework in elementary school?",
        [
            "Harris Cooper's meta-analysis of homework research (2006, synthesizing data since 1987) found that homework has near-zero academic benefit for elementary students (grades K-5), with a correlation of r = 0.04 between homework and achievement. The American Psychological Association and National Education Association both recommend no more than 10 minutes per grade level. For high school students, moderate homework (1-2 hours/night) showed positive effects (r = 0.25).",
            "Proponents including the Thomas B. Fordham Institute argue homework builds study habits and responsibility even if academic gains are minimal. Some parents equate homework volume with school quality. However, excess homework in elementary grades is associated with increased anxiety, family conflict, and reduced interest in learning, per a 2015 Stanford study surveying 4,317 families."
        ],
        "Elementary homework debate where research consensus shows near-zero academic benefit despite cultural expectations",
        "Cooper's meta-analysis shows negligible effect for K-5; proponents argue non-academic benefits but evidence links excess homework to negative outcomes",
        "education", "should", "single", "evaluative",
    ))

    cases.append(make_case(
        "t1_confident_medium_918", "medium", "different_framing",
        "Why does inflation occur in an economy?",
        [
            "From the monetarist perspective (Milton Friedman), inflation is 'always and everywhere a monetary phenomenon.' When the money supply grows faster than real output, each unit of currency buys less. The quantity theory (MV = PQ) predicts that if velocity (V) and output (Q) are stable, prices (P) rise proportionally to money supply (M) growth.",
            "From the Keynesian perspective, inflation arises from either demand-pull (aggregate demand exceeding aggregate supply, often from government spending or consumer confidence) or cost-push factors (rising input costs like wages or raw materials being passed to consumers). Supply chain disruptions, wage-price spirals, and expectations also play key roles. In practice, most economists acknowledge both monetary and real-economy factors interact to drive inflation."
        ],
        "Inflation causes presented through monetarist and Keynesian frameworks that complement each other",
        "Both perspectives are mainstream; monetarism emphasizes money supply while Keynesian theory adds demand-pull and cost-push mechanisms. Context notes they interact in practice.",
        "finance", "why", "single", "causal",
    ))

    cases.append(make_case(
        "t1_confident_medium_919", "medium", "quantitative_answer",
        "What is the distance from the Earth to the Moon?",
        [
            "The average distance from Earth to the Moon is 384,400 kilometres (238,855 miles), known as the semi-major axis of the Moon's orbit. Due to the Moon's elliptical orbit, the actual distance varies from 356,500 km at perigee (closest approach) to 406,700 km at apogee (farthest point). Lunar Laser Ranging experiments using retroreflectors placed during Apollo missions measure this distance with precision to within a few millimeters. The Moon is receding from Earth at a rate of 3.8 cm per year due to tidal interactions."
        ],
        "Earth-Moon distance with average, range, measurement method, and recession rate",
        "Context provides exact average (384,400 km), perigee/apogee range, measurement precision, and tidal recession rate",
        "science", "what", "single", "factual",
    ))

    cases.append(make_case(
        "t1_confident_medium_920", "medium", "quantitative_answer",
        "How many bones are in the adult human body?",
        [
            "The adult human body has 206 bones. Babies are born with approximately 270 bones, many of which fuse together during development (for example, the 5 sacral vertebrae fuse into the sacrum, and the skull's fontanelles close). The skeleton is divided into the axial skeleton (80 bones: skull, vertebral column, rib cage) and the appendicular skeleton (126 bones: limbs, pectoral girdle, pelvic girdle). The smallest bone is the stapes in the middle ear (2.5 mm), and the largest is the femur (thigh bone), averaging 48 cm in adults."
        ],
        "Bone count with developmental explanation, axial/appendicular breakdown, and size extremes",
        "Context provides precise adult count (206), infant starting count (270), fusion explanation, and skeletal division",
        "education", "how", "single", "factual",
    ))

    cases.append(make_case(
        "t1_confident_medium_921", "medium", "cross_source_agreement",
        "What are the main greenhouse gases contributing to climate change?",
        [
            "The EPA identifies carbon dioxide (CO2), methane (CH4), nitrous oxide (N2O), and fluorinated gases (HFCs, PFCs, SF6) as the primary greenhouse gases. CO2 accounts for 79% of U.S. greenhouse gas emissions (2021), primarily from fossil fuel combustion. Methane contributes 11%, mainly from agriculture and natural gas systems.",
            "The IPCC AR6 confirms CO2 as the dominant driver of radiative forcing since 1750, contributing 2.16 W/m2, followed by methane at 0.54 W/m2, nitrous oxide at 0.21 W/m2, and halocarbons at 0.41 W/m2. Water vapor is the most abundant greenhouse gas but acts as a feedback amplifier rather than a direct forcing agent."
        ],
        "Greenhouse gas identification confirmed by EPA emissions data and IPCC radiative forcing measurements",
        "EPA (domestic emissions) and IPCC (global radiative forcing) converge on the same gases with complementary quantification approaches",
        "environment", "what", "multi_source",
        "factual", "direct",
        context_sources=[
            {"source_id": "epa_ghg_inventory_2023", "source_type": "government", "authority": "official"},
            {"source_id": "ipcc_ar6_wg1_ch7", "source_type": "government", "authority": "official"},
        ],
    ))

    cases.append(make_case(
        "t1_confident_medium_922", "medium", "cross_source_agreement",
        "Is the Great Wall of China visible from space with the naked eye?",
        [
            "NASA astronaut Chris Hadfield, who served as commander of the International Space Station in 2013, stated that the Great Wall of China is not visible from the ISS with the naked eye, as it is only about 6 metres wide. Wide highways, airports, and greenhouses are more visible due to color contrast and width.",
            "China's first astronaut, Yang Liwei, confirmed after his 2003 Shenzhou 5 mission that he could not see the Great Wall from orbit. The China Manned Space Engineering office corroborated this, noting that at 350 km altitude, resolving a 6-metre-wide structure would require visual acuity 7.7 times better than normal human vision (20/20 or 6/6 Snellen)."
        ],
        "Great Wall visibility myth debunked by astronauts from both NASA and CNSA with optical physics explanation",
        "Two independent space agencies and firsthand astronaut accounts agree the Wall is not visible from space, supported by optical resolution calculations",
        "history", "is", "multi_source",
        "factual", "direct",
        context_sources=[
            {"source_id": "nasa_iss_hadfield_2013", "source_type": "government", "authority": "expert"},
            {"source_id": "cnsa_shenzhou5_debrief", "source_type": "government", "authority": "official"},
        ],
    ))

    cases.append(make_case(
        "t1_confident_medium_923", "medium", "multi_source_convergence",
        "How much sleep do adults need per night according to health guidelines?",
        [
            "The National Sleep Foundation's expert panel (2015, Sleep Health journal) recommends 7-9 hours of sleep per night for adults aged 18-64, and 7-8 hours for adults 65 and older. Consistently sleeping fewer than 6 hours is associated with increased mortality, obesity, and cardiovascular disease risk.",
            "The American Academy of Sleep Medicine and Sleep Research Society joint consensus statement (2015) recommends adults sleep 7 or more hours per night on a regular basis. Sleeping fewer than 7 hours is associated with weight gain, diabetes, hypertension, heart disease, stroke, depression, and impaired immune function.",
            "The CDC classifies fewer than 7 hours of sleep per night as 'short sleep duration,' estimating that 1 in 3 American adults (35.2%) does not get sufficient sleep. Their recommendation aligns with the AASM: at least 7 hours for optimal health."
        ],
        "Adult sleep recommendations converging across three independent health organizations at 7+ hours",
        "National Sleep Foundation, AASM/SRS, and CDC all independently recommend 7+ hours with consistent health outcome data",
        "psychology", "how", "multi_source",
        "factual", "direct",
        context_sources=[
            {"source_id": "nsf_sleep_duration_2015", "source_type": "academic", "authority": "expert"},
            {"source_id": "aasm_srs_consensus_2015", "source_type": "academic", "authority": "expert"},
            {"source_id": "cdc_sleep_data_brief_2022", "source_type": "government", "authority": "official"},
        ],
    ))

    cases.append(make_case(
        "t1_confident_medium_924", "medium", "authoritative_source",
        "Is 21 the legal drinking age across all U.S. states?",
        [
            "The National Minimum Drinking Age Act of 1984 (23 U.S.C. Section 158) requires all states to set a minimum purchase and public possession age of 21 for alcoholic beverages. States that do not comply face a 10% reduction in federal highway funding. All 50 states and the District of Columbia comply with the 21 minimum age. Some states allow exceptions for consumption under parental supervision, religious ceremonies, or medical purposes, but purchase age is uniformly 21."
        ],
        "U.S. legal drinking age from federal statute with enforcement mechanism and universal compliance",
        "Direct statutory citation with USC reference, funding enforcement mechanism, and confirmation of universal state compliance",
        "law", "is", "single", "factual",
    ))

    cases.append(make_case(
        "t1_confident_medium_925", "medium", "authoritative_source",
        "What is the retirement age for Social Security in the United States?",
        [
            "The Social Security Administration states that full retirement age (FRA) depends on birth year: 66 for those born 1943-1954, gradually increasing to 67 for those born in 1960 or later. Early retirement at age 62 is available but permanently reduces benefits by 5/9 of 1% per month for the first 36 months and 5/12 of 1% for each additional month before FRA. Delayed retirement credits of 8% per year accrue for each year benefits are delayed past FRA up to age 70."
        ],
        "Social Security retirement ages from SSA with birth-year schedule and early/delayed benefit calculations",
        "SSA-sourced data provides the exact FRA schedule, early retirement reduction formula, and delayed retirement credit rate",
        "government", "what", "single", "factual",
    ))

    cases.append(make_case(
        "t1_confident_medium_926", "medium", "near_complete_evidence",
        "Why is the Amazon rainforest being deforested?",
        [
            "According to Brazil's National Institute for Space Research (INPE) satellite monitoring, the primary drivers of Amazon deforestation are cattle ranching (responsible for approximately 80% of cleared land), soybean cultivation (5-10%), logging both legal and illegal (10-15%), and infrastructure development including roads and hydroelectric dams. Small-scale subsistence farming accounts for less than 5%.",
            "The World Wildlife Fund notes that deforestation rates correlate with commodity prices: beef and soy price increases of 10% correspond to 2-3% increases in deforestation within 12 months. Between 2019-2022, annual deforestation exceeded 10,000 square kilometres, though 2023 showed a 22% reduction following enforcement policy changes."
        ],
        "Amazon deforestation causes with proportional breakdown and economic correlation data",
        "Satellite data provides driver percentages; economic analysis adds commodity price correlation and recent trend data",
        "environment", "why", "single", "factual",
    ))

    cases.append(make_case(
        "t1_confident_medium_927", "medium", "near_complete_evidence",
        "How does a home appraisal work in the mortgage process?",
        [
            "A home appraisal is an independent assessment of a property's market value required by mortgage lenders before loan approval. A licensed appraiser visits the property, inspects both interior and exterior condition, measures square footage, evaluates improvements, and photographs the home. The appraiser then compares the property to 3-5 recently sold comparable properties ('comps') within a 1-mile radius (or wider in rural areas) that sold within the past 6 months.",
            "The appraiser adjusts comp values for differences (e.g., adding value for an extra bedroom, subtracting for a smaller lot) to arrive at an estimated market value. If the appraisal comes in below the purchase price, the buyer can renegotiate, make up the difference in cash, contest the appraisal, or walk away (if an appraisal contingency exists). Appraisals typically cost $300-$600 and take 7-14 days."
        ],
        "Home appraisal process from inspection through valuation methodology and buyer options if low",
        "Contexts cover appraiser procedures, comparable sales methodology, adjustment process, and remedies for low appraisals with cost/timeline",
        "real_estate", "how", "single", "procedural",
    ))

    cases.append(make_case(
        "t1_confident_medium_928", "medium", "conditional_confidence",
        "Is it safe to exercise during pregnancy?",
        [
            "The American College of Obstetricians and Gynecologists (ACOG) recommends that women with uncomplicated pregnancies engage in at least 150 minutes of moderate-intensity aerobic activity per week. Safe activities include walking, swimming, stationary cycling, and prenatal yoga. Exercise during pregnancy reduces the risk of gestational diabetes by 30%, preeclampsia by 40%, and excessive weight gain.",
            "Contraindications include placenta previa after 26 weeks, cervical insufficiency, preterm labor risk, severe anemia, and uncontrolled cardiac or pulmonary conditions. Contact sports, scuba diving, and activities with fall risk should be avoided. Women should stop exercising and seek medical attention if they experience vaginal bleeding, dizziness, chest pain, or regular painful contractions."
        ],
        "Pregnancy exercise safety with ACOG recommendation, benefits, contraindications, and warning signs",
        "Evidence clearly supports exercise in uncomplicated pregnancies with specific conditions (contraindications) when it should be avoided",
        "medicine", "is", "single", "evaluative",
    ))

    cases.append(make_case(
        "t1_confident_medium_929", "medium", "direct_factual",
        "Which planet in our solar system has the most moons?",
        [
            "As of 2024, Saturn holds the record for the most known moons in our solar system with 146 confirmed natural satellites, surpassing Jupiter's 95 confirmed moons. The discovery of 62 new Saturnian moons was announced in 2023 using the Canada-France-Hawaii Telescope's shift-and-stack technique, which can detect objects as small as 2.5 km in diameter. Saturn's largest moon, Titan, is the only moon in the solar system with a substantial atmosphere."
        ],
        "Moon count record holder with discovery method and current confirmed totals",
        "Context provides Saturn's count (146), Jupiter's count (95), discovery technique, and notable Titan fact",
        "general", "which", "single", "factual",
    ))

    cases.append(make_case(
        "t1_confident_medium_930", "medium", "direct_factual",
        "When did World War II officially end?",
        [
            "The U.S. National Archives holds the original Japanese Instrument of Surrender signed on September 2, 1945, aboard the USS Missouri in Tokyo Bay. The document was signed by Japanese Foreign Minister Mamoru Shigemitsu and General Yoshijiro Umezu, accepted by General Douglas MacArthur for the Allied Powers. This followed the atomic bombings of Hiroshima (August 6) and Nagasaki (August 9).",
            "The Imperial War Museum's timeline confirms that Emperor Hirohito's radio broadcast accepting the Potsdam Declaration on August 15, 1945 (V-J Day) preceded the formal surrender by 18 days. The war in Europe had already ended on May 8, 1945 (V-E Day), when Germany signed unconditional surrender at Reims, France. Thus September 2, 1945, marks the official end of World War II globally."
        ],
        "WWII end dates confirmed by U.S. National Archives documents and Imperial War Museum timeline",
        "National Archives holds the surrender document (Sep 2 1945); Imperial War Museum timeline confirms the V-J Day and V-E Day sequence",
        "history", "when", "multi_source",
        "temporal", "direct",
        context_sources=[
            {"source_id": "nara_japanese_surrender_1945", "source_type": "government", "authority": "official"},
            {"source_id": "iwm_wwii_timeline", "source_type": "academic", "authority": "primary"},
        ],
    ))

    cases.append(make_case(
        "t1_confident_medium_931", "medium", "multi_source_convergence",
        "What is the recommended daily water intake for adults?",
        [
            "The National Academies of Sciences, Engineering, and Medicine determined that adequate daily fluid intake is approximately 3.7 liters (125 oz) for men and 2.7 liters (91 oz) for women. This includes water from all beverages and food (approximately 20% comes from food).",
            "The European Food Safety Authority (EFSA) recommends 2.5 liters per day for men and 2.0 liters per day for women from all sources. The slight difference from U.S. guidelines reflects different methodology (EFSA uses balance studies while NASEM uses intake surveys).",
            "The Mayo Clinic notes that the common '8 glasses a day' (1.9 liters) guideline, while not scientifically derived, is a reasonable approximation for most adults in temperate climates. Individual needs vary with physical activity, climate, pregnancy/breastfeeding, and health conditions."
        ],
        "Adult water intake recommendations from three health authorities with methodological context",
        "NASEM, EFSA, and Mayo Clinic converge on approximately 2-3.7 liters/day with acknowledged individual variation",
        "food", "what", "multi_source",
        "factual", "direct",
        context_sources=[
            {"source_id": "nasem_dri_water_2004", "source_type": "academic", "authority": "official"},
            {"source_id": "efsa_water_guidance_2010", "source_type": "government", "authority": "official"},
            {"source_id": "mayo_clinic_water_faq", "source_type": "reference", "authority": "expert"},
        ],
    ))

    cases.append(make_case(
        "t1_confident_medium_932", "medium", "step_by_step",
        "How do you change a flat tire on a car?",
        [
            "Step 1: Pull over to a safe, flat surface away from traffic. Turn on hazard lights and apply the parking brake. Step 2: Place wheel wedges behind the tires opposite the flat. Remove the hubcap or wheel cover and loosen (but do not remove) the lug nuts by turning counterclockwise with the wrench, using your body weight if needed.",
            "Step 3: Place the jack under the vehicle frame near the flat tire (check owner's manual for the exact jack point) and raise until the flat tire is about 6 inches off the ground. Step 4: Remove the lug nuts completely and pull off the flat tire. Mount the spare tire, hand-tighten lug nuts in a star pattern. Step 5: Lower the vehicle until the spare touches the ground with partial weight, then tighten lug nuts fully in a star pattern to the manufacturer's torque specification (typically 80-100 ft-lbs). Step 6: Lower completely, remove the jack, check spare tire pressure (spares should be at 60 PSI), and drive to a repair shop. Spare tires (donuts) should not exceed 50 mph or 70 miles."
        ],
        "Complete tire-changing procedure with six numbered steps including safety, torque specs, and spare tire limits",
        "Sequential steps cover safety setup, loosening, jacking, mounting, tightening pattern, and spare tire operational limits",
        "transportation", "how", "single", "procedural",
    ))

    cases.append(make_case(
        "t1_confident_medium_933", "medium", "step_by_step",
        "How do you calculate your federal income tax owed in the United States?",
        [
            "Step 1: Calculate gross income by summing all income sources (wages, interest, dividends, capital gains, business income, etc.). Step 2: Subtract 'above the line' deductions (IRA contributions, student loan interest, HSA contributions) to get Adjusted Gross Income (AGI). Step 3: Subtract either the standard deduction ($14,600 for single filers, $29,200 for married filing jointly in 2024) or itemized deductions (mortgage interest, state/local taxes up to $10,000, charitable contributions), whichever is higher. This gives taxable income.",
            "Step 4: Apply the marginal tax brackets to taxable income. For 2024 single filers: 10% on $0-$11,600, 12% on $11,601-$47,150, 22% on $47,151-$100,525, 24% on $100,526-$191,950, 32% on $191,951-$243,725, 35% on $243,726-$609,350, and 37% on income above $609,350. Step 5: Subtract tax credits (child tax credit, earned income credit, education credits) from the calculated tax. Credits reduce tax dollar-for-dollar. Step 6: Compare total tax to taxes already withheld from paychecks (Form W-2 Box 2) and estimated payments made. The difference is either the amount you owe or your refund."
        ],
        "Six-step federal income tax calculation from gross income through refund/owed determination with 2024 brackets",
        "Sequential steps cover income, deductions, taxable income, bracket application, credits, and withholding reconciliation with specific dollar amounts",
        "finance", "how", "single", "procedural",
    ))

    cases.append(make_case(
        "t1_confident_medium_934", "medium", "definitional",
        "What is a blockchain and how does it work?",
        [
            "A blockchain is a distributed, append-only digital ledger where transactions are grouped into blocks that are cryptographically linked in chronological order. Each block contains a hash of the previous block, a timestamp, and a Merkle root of the transactions it contains. This chaining means altering any block would invalidate all subsequent blocks, making the ledger tamper-evident.",
            "New blocks are added through a consensus mechanism. In proof-of-work (Bitcoin), miners compete to solve a computational puzzle (finding a nonce that produces a hash below a target difficulty), with the winner broadcasting the block to the network. In proof-of-stake (Ethereum post-Merge), validators are selected proportionally to staked cryptocurrency. Once consensus is reached, the block is appended and replicated across all nodes."
        ],
        "Blockchain definition covering data structure, cryptographic linking, and consensus mechanisms",
        "Contexts define the ledger structure (blocks, hashes, Merkle root), immutability property, and two major consensus approaches",
        "finance", "what", "single", "factual",
    ))

    cases.append(make_case(
        "t1_confident_medium_935", "medium", "definitional",
        "What is the difference between a recession and a depression?",
        [
            "A recession is commonly defined as two consecutive quarters of negative real GDP growth, though the National Bureau of Economic Research (NBER) defines it more broadly as a significant decline in economic activity spread across the economy lasting more than a few months, visible in GDP, employment, industrial production, and retail sales. The U.S. has experienced 12 recessions since World War II, with an average duration of 10 months.",
            "A depression has no precise technical definition but is generally understood as a severe, prolonged recession. Rules of thumb include a real GDP decline exceeding 10% or a recession lasting over 3 years. The Great Depression (1929-1939) saw U.S. GDP fall 30%, unemployment reach 25%, and industrial production drop 47%. Since then, no U.S. downturn has met depression criteria, though the 2007-2009 Great Recession (GDP decline of 4.3%) was the most severe post-WWII."
        ],
        "Recession vs depression defined with NBER criteria, quantitative thresholds, and historical examples",
        "Contexts provide NBER's recession definition, depression rules of thumb, and Great Depression/Great Recession as reference points",
        "finance", "what", "single", "comparative",
    ))

    cases.append(make_case(
        "t1_confident_medium_936", "medium", "clear_explanation",
        "How effective are seatbelts at preventing traffic fatalities?",
        [
            "NHTSA estimates that seatbelts saved 14,955 lives in the United States in 2017 and reduce the risk of fatal injury to front-seat passenger car occupants by 45% and light truck occupants by 60%. The national seatbelt usage rate was 91.6% in 2022.",
            "The World Health Organization reports that wearing a seatbelt reduces the risk of death among front-seat occupants by 40-50% and among rear-seat occupants by 25-75%. WHO considers seatbelt legislation and enforcement among the most cost-effective road safety interventions globally.",
            "A Cochrane systematic review of seatbelt effectiveness (2010, updated 2018) analyzing data from multiple countries confirmed a 40-50% reduction in fatal and serious injuries, noting that the evidence quality is high and consistent across study designs and populations."
        ],
        "Seatbelt fatality reduction confirmed at 40-50% by three independent global health and safety authorities",
        "NHTSA, WHO, and Cochrane review all converge on 40-50% fatality reduction with consistent evidence",
        "transportation", "how", "multi_source",
        "factual", "direct",
        context_sources=[
            {"source_id": "nhtsa_traffic_safety_2022", "source_type": "government", "authority": "official"},
            {"source_id": "who_road_safety_2023", "source_type": "government", "authority": "official"},
            {"source_id": "cochrane_seatbelt_review_2018", "source_type": "academic", "authority": "primary"},
        ],
    ))

    cases.append(make_case(
        "t1_confident_medium_937", "medium", "direct_factual",
        "Which building is the tallest in the world as of 2024?",
        [
            "The Burj Khalifa in Dubai, United Arab Emirates, is the tallest building in the world at 828 metres (2,717 feet) with 163 floors. Designed by Adrian Smith of Skidmore, Owings & Merrill and completed in 2010, it features a reinforced concrete core with a buttressed Y-shaped floor plan for wind resistance. The Jeddah Tower in Saudi Arabia, planned at 1,000 metres, has been under construction since 2013 but remains incomplete."
        ],
        "World's tallest building with height, architect, structural design, and upcoming challenger status",
        "Context identifies Burj Khalifa with exact height, completion year, designer, and engineering features",
        "general", "which", "single", "factual",
    ))

    cases.append(make_case(
        "t1_confident_medium_938", "medium", "direct_factual",
        "Who invented the World Wide Web?",
        [
            "Tim Berners-Lee, a British computer scientist working at CERN (the European Organization for Nuclear Research) in Geneva, Switzerland, invented the World Wide Web in 1989. He wrote the first proposal in March 1989, created the first web browser (WorldWideWeb) and web server (httpd) in 1990, and launched the first website (info.cern.ch) on August 6, 1991. Berners-Lee also developed the foundational technologies: HTML (HyperText Markup Language), URI (Uniform Resource Identifier), and HTTP (HyperText Transfer Protocol)."
        ],
        "WWW invention attributed to Tim Berners-Lee with timeline, location, and foundational technologies",
        "Context provides inventor, institution, key dates, first browser/server/website, and three core technologies created",
        "history", "who", "single", "factual",
    ))

    cases.append(make_case(
        "t1_confident_medium_939", "medium", "different_framing",
        "How do vaccines work to prevent disease?",
        [
            "From an immunological perspective, vaccines introduce a harmless form of a pathogen (attenuated, inactivated, protein subunit, or mRNA-encoded antigen) to the immune system. Antigen-presenting cells process the vaccine antigen and display fragments on MHC molecules, activating T-helper cells. These trigger B-cell differentiation into antibody-producing plasma cells and memory B-cells. Memory cells persist for years or decades, enabling rapid secondary immune response upon actual infection.",
            "From a public health perspective, vaccines work through both individual protection and herd immunity. When a sufficient proportion of a population is vaccinated (the herd immunity threshold, e.g., 95% for measles, 80-85% for polio), transmission chains are broken, protecting those who cannot be vaccinated (infants, immunocompromised individuals). This collective effect is why vaccination programs aim for population-level coverage rather than just individual protection."
        ],
        "Vaccine mechanisms explained through individual immunology and population-level public health framings",
        "Immunological framing covers molecular mechanism (APCs, T-cells, B-cells, memory); public health framing covers herd immunity and population protection",
        "social_media", "how", "single", "causal",
    ))

    cases.append(make_case(
        "t1_confident_medium_940", "medium", "opposing_with_consensus",
        "Is the use of genetically modified organisms (GMOs) in food safe?",
        [
            "The National Academies of Sciences, Engineering, and Medicine conducted a comprehensive review of 900+ studies (2016) and concluded that genetically engineered crops are safe for human consumption, finding no substantiated evidence of health risks from foods derived from GE crops. The WHO, AMA, AAAS, and European Commission (reviewing 25 years of EU-funded research) independently reached the same conclusion. Over 3 trillion meals containing GMO ingredients have been consumed since 1996 with no documented adverse health effects.",
            "Anti-GMO organizations such as the Non-GMO Project and some organic farming advocates argue that long-term effects are unknown, cite concerns about herbicide-tolerant crops increasing glyphosate use, and raise ecological concerns about gene flow to wild relatives. The Seralini study (2012) claiming tumor growth in rats fed GM corn was retracted for inadequate sample size and inappropriate statistical methods, though it remains widely cited in anti-GMO media."
        ],
        "GMO food safety debate where overwhelming scientific consensus supports safety against advocacy opposition",
        "National Academies, WHO, AMA, AAAS, and EU Commission consensus on safety; opposition relies on retracted studies and precautionary concerns rather than evidence of harm",
        "food", "is", "single", "evaluative",
    ))

    cases.append(make_case(
        "t1_confident_medium_941", "medium", "authoritative_source",
        "What is the speed limit on interstate highways in the United States?",
        [
            "The Federal Highway Administration notes that speed limits on U.S. interstate highways vary by state, as speed regulation is a state responsibility. Rural interstate limits range from 65 mph (e.g., Oregon, Alaska) to 80 mph (Idaho, Montana, Utah, Wyoming) and 85 mph on a single stretch of Texas State Highway 130. Urban interstate limits are typically 55-65 mph. All states use radar, lidar, or aircraft-based enforcement. The national maximum speed limit of 55 mph (1974-1987) and 65 mph (1987-1995) was repealed by the National Highway System Designation Act of 1995, returning authority to states."
        ],
        "Interstate speed limits from FHWA showing state variation, current ranges, and legislative history",
        "FHWA authority confirms state-by-state variation with specific ranges and the federal maximum's repeal history",
        "transportation", "what", "single", "factual",
    ))

    cases.append(make_case(
        "t1_confident_medium_942", "medium", "contradiction_resolved",
        "Is Pluto a planet or not?",
        [
            "For 76 years after Clyde Tombaugh's discovery in 1930, Pluto was classified as the ninth planet of the solar system. Textbooks, NASA missions (New Horizons, launched 2006 when Pluto was still a planet), and popular culture treated it as a full planet.",
            "In August 2006, the International Astronomical Union (IAU) adopted Resolution 5A establishing three criteria for planethood: (1) orbits the Sun, (2) has sufficient mass for hydrostatic equilibrium (nearly round shape), and (3) has cleared the neighborhood around its orbit. Pluto meets criteria 1 and 2 but fails criterion 3, as it shares its orbital region with other Kuiper Belt objects. It was reclassified as a 'dwarf planet.' While some planetary scientists (notably Alan Stern, the New Horizons principal investigator) dispute the IAU definition, the IAU classification is the internationally recognized standard used by the global scientific community."
        ],
        "Pluto's classification controversy resolved by IAU's formal 2006 definition as the authoritative standard",
        "Historical planet status is acknowledged, then the IAU resolution's specific criteria resolve the contradiction, noting dissent but IAU authority",
        "general", "is", "single", "factual",
    ))

    cases.append(make_case(
        "t1_confident_medium_943", "medium", "conditional_confidence",
        "Does drinking coffee before a workout improve performance?",
        [
            "A 2021 meta-analysis in the British Journal of Sports Medicine analyzing 21 studies found that caffeine ingestion (3-6 mg per kilogram of body weight) 30-60 minutes before exercise improves endurance performance by 2-4%, strength performance by 2-7%, and sprint performance by 6-8%. The ergogenic effects are most pronounced in trained athletes and during sustained efforts longer than 5 minutes.",
            "However, habitual caffeine consumers show diminished effects (tolerance develops over 1-4 weeks of daily use), with performance gains dropping to 1-2%. Genetic variation in the CYP1A2 gene affects caffeine metabolism: fast metabolizers (AA genotype, ~50% of the population) benefit most, while slow metabolizers (CC genotype, ~10%) may experience no benefit or impaired performance. Side effects including GI distress, anxiety, and elevated heart rate can offset gains for sensitive individuals."
        ],
        "Pre-workout caffeine effectiveness with clear conditions (dose, timing, tolerance, genetics) that modulate benefit",
        "Evidence supports ergogenic effects at specific doses but effectiveness depends on caffeine habits, genetic metabolizer status, and individual sensitivity",
        "sports", "does", "single", "evaluative",
    ))

    cases.append(make_case(
        "t1_confident_medium_944", "medium", "near_complete_evidence",
        "How does the Electoral College work in U.S. presidential elections?",
        [
            "The Electoral College consists of 538 electors, with each state receiving a number equal to its total congressional delegation (House representatives + 2 senators). Washington, D.C. receives 3 electors under the 23rd Amendment. A candidate needs 270 electoral votes (a majority) to win the presidency. If no candidate reaches 270, the House of Representatives selects the president with each state delegation casting one vote.",
            "In 48 states and D.C., electors are awarded on a winner-take-all basis to the candidate winning the state's popular vote. Maine and Nebraska use a congressional district method, awarding 2 electors to the state popular vote winner and 1 elector per congressional district. Electors meet in their respective state capitals on the first Tuesday after the second Wednesday in December to cast their votes, which are certified by Congress on January 6."
        ],
        "Electoral College mechanics covering allocation, threshold, contingency, and two methods of elector assignment",
        "Contexts cover elector count, state allocation, 270 threshold, House contingency, winner-take-all and district methods, and certification timeline",
        "government", "how", "single", "procedural",
    ))

    cases.append(make_case(
        "t1_confident_medium_945", "medium", "quantitative_answer",
        "Is oxygen the most abundant gas in Earth's atmosphere?",
        [
            "Earth's atmosphere is composed of approximately 78.09% nitrogen (N2), 20.95% oxygen (O2), 0.93% argon (Ar), and 0.04% carbon dioxide (CO2) by volume in dry air at sea level. The oxygen fraction has remained relatively stable at 20.9-21.0% for the past 500 million years. Atmospheric oxygen originated from photosynthetic cyanobacteria during the Great Oxidation Event approximately 2.4 billion years ago, which raised O2 levels from less than 0.001% to current levels over hundreds of millions of years.",
            "At higher altitudes, the total atmospheric pressure decreases but the percentage composition remains approximately constant up to about 100 km (the Karman line). At the summit of Mount Everest (8,849 m), the oxygen percentage is still approximately 21%, but the partial pressure of oxygen is only about one-third of sea-level values (7 kPa versus 21 kPa), which is why supplemental oxygen is typically required above 8,000 m."
        ],
        "Atmospheric oxygen composition with precise percentages, historical origin, and altitude effects",
        "Context provides exact atmospheric composition, the Great Oxidation Event timeline, and altitude-pressure distinction explaining why percentage stays constant but partial pressure drops",
        "science", "is", "single", "factual",
    ))

    cases.append(make_case(
        "t1_confident_medium_946", "medium", "clear_explanation",
        "What is the literacy rate worldwide?",
        [
            "UNESCO's Institute for Statistics reports the global adult literacy rate at 87% as of 2022, with significant regional variation: Sub-Saharan Africa at 65%, South Asia at 73%, Latin America at 94%, and Europe at 99%. Youth literacy (ages 15-24) is higher at 92% globally, indicating improvement in recent decades.",
            "The World Bank's World Development Indicators confirm a global literacy rate of approximately 87% for 2022, noting that the rate has risen from 56% in 1950. The gender gap has narrowed but persists: male literacy is 90% versus female literacy at 83%, with the gap widest in Sub-Saharan Africa (75% male vs. 55% female).",
        ],
        "Global literacy rate confirmed at 87% by UNESCO and World Bank with regional and gender breakdowns",
        "UNESCO and World Bank independently report 87% with consistent regional variation and trend data",
        "education", "what", "multi_source",
        "factual", "direct",
        context_sources=[
            {"source_id": "unesco_uis_literacy_2023", "source_type": "government", "authority": "official"},
            {"source_id": "worldbank_wdi_2023", "source_type": "government", "authority": "official"},
        ],
    ))

    cases.append(make_case(
        "t1_confident_medium_947", "medium", "definitional",
        "Does photosynthesis convert light energy into chemical energy?",
        [
            "Photosynthesis is the process by which plants, algae, and cyanobacteria convert light energy into chemical energy stored in glucose. The overall equation is: 6CO2 + 6H2O + light energy -> C6H12O6 + 6O2. The process occurs in two stages within chloroplasts: the light-dependent reactions (in thylakoid membranes) split water using sunlight to produce ATP and NADPH, while the Calvin cycle (in the stroma) uses ATP and NADPH to fix CO2 into glucose through a series of enzyme-catalyzed reactions. Rubisco, the enzyme that catalyzes CO2 fixation, is the most abundant protein on Earth."
        ],
        "Photosynthesis definition with chemical equation, two-stage process, locations, and key enzyme",
        "Context provides the definition, balanced equation, both stages with subcellular locations, and Rubisco's role",
        "science", "does", "single", "factual",
    ))

    cases.append(make_case(
        "t1_confident_medium_948", "medium", "opposing_with_consensus",
        "Should fluoride be added to public drinking water?",
        [
            "The U.S. Public Health Service recommends community water fluoridation at 0.7 mg/L as a safe and effective method to prevent dental caries. The CDC named water fluoridation one of the 10 great public health achievements of the 20th century. A 2015 Cochrane review confirmed fluoridated water reduces tooth decay by 26% in children. The WHO, ADA, AAP, and AMA all endorse community water fluoridation at recommended levels.",
            "Opponents including the Fluoride Action Network argue that fluoridation constitutes mass medication without individual consent, cite studies linking high fluoride levels (above 4 mg/L, well above the recommended 0.7 mg/L) to skeletal fluorosis and potential neurotoxicity, and note that topical fluoride (toothpaste, rinses) may be sufficient. Some European countries have discontinued water fluoridation in favor of other delivery methods, though their dental health outcomes also reflect universal healthcare access and different dietary patterns."
        ],
        "Water fluoridation debate where major health organizations consensually support it against advocacy opposition",
        "CDC, WHO, ADA, AAP, and AMA consensus plus Cochrane evidence clearly supports fluoridation; opposition conflates high-dose risks with recommended levels and raises philosophical rather than evidence-based objections",
        "government", "should", "single", "evaluative",
    ))

    cases.append(make_case(
        "t1_confident_medium_949", "medium", "cross_source_agreement",
        "How long does it take light from the Sun to reach Earth?",
        [
            "NASA's Sun Fact Sheet states that the mean distance from the Sun to Earth is 149,597,870.7 km (1 astronomical unit). Light travels at 299,792.458 km/s in vacuum, yielding a one-way light travel time of approximately 499 seconds, or about 8 minutes and 19 seconds.",
            "The U.S. Naval Observatory's Astronomical Almanac provides the same mean Earth-Sun distance and confirms the light time as 498.66 seconds (8 minutes 18.66 seconds) for the mean distance. Due to Earth's elliptical orbit, actual light travel time varies from approximately 490 seconds at perihelion (January) to 507 seconds at aphelion (July)."
        ],
        "Sun-Earth light travel time confirmed by NASA and USNO with orbital variation noted",
        "NASA and USNO independently calculate approximately 499 seconds with consistent methodology and orbital range",
        "science", "how", "multi_source",
        "factual", "direct",
        context_sources=[
            {"source_id": "nasa_sun_fact_sheet", "source_type": "government", "authority": "official"},
            {"source_id": "usno_astronomical_almanac_2024", "source_type": "government", "authority": "official"},
        ],
    ))

    cases.append(make_case(
        "t1_confident_medium_950", "medium", "contradiction_resolved",
        "Is saturated fat the main dietary cause of heart disease?",
        [
            "For decades, the 'diet-heart hypothesis' held that saturated fat intake raised LDL cholesterol, directly causing atherosclerosis and coronary heart disease. The American Heart Association's 1961 guidelines recommended limiting saturated fat to less than 10% of calories, and the 1977 Dietary Goals for the United States endorsed this position, shaping decades of low-fat dietary policy.",
            "A 2020 meta-analysis in the Journal of the American College of Cardiology reviewing 17 systematic reviews found no significant association between saturated fat intake and all-cause mortality (RR 0.99, 95% CI 0.93-1.06) or cardiovascular events (RR 1.00, 95% CI 0.93-1.08). The resolution: saturated fat does raise LDL cholesterol, but the original hypothesis oversimplified by ignoring that saturated fat also raises HDL and that refined carbohydrate substitution (which occurred during the low-fat era) independently worsens cardiovascular risk. The current consensus focuses on overall dietary patterns rather than single nutrient demonization."
        ],
        "Saturated fat-heart disease link initially appears contradicted by meta-analyses but resolved by nuanced understanding",
        "Initial dietary hypothesis stated then contradicted by null meta-analysis results; resolution explains the oversimplification and substitution effect",
        "food", "is", "single", "evaluative",
    ))

    cases.append(make_case(
        "t1_confident_medium_951", "medium", "clear_explanation",
        "Which film is the highest-grossing of all time?",
        [
            "According to Box Office Mojo (an IMDb-owned industry-standard tracking service), Avatar (2009), directed by James Cameron, is the highest-grossing film of all time with a worldwide box office total of approximately $2.923 billion. This includes its original 2009 theatrical run and multiple re-releases (2010, 2020, 2022). Avengers: Endgame (2019) is second at $2.799 billion. When adjusted for inflation, Gone with the Wind (1939) holds the record at an estimated $3.7 billion in 2023 dollars."
        ],
        "Highest-grossing film from industry-standard Box Office Mojo with inflation-adjusted context",
        "Authoritative box office source identifies Avatar with precise total, re-release context, and inflation-adjusted alternative",
        "general", "which", "single", "factual",
    ))

    cases.append(make_case(
        "t1_confident_medium_952", "medium", "cross_source_agreement",
        "What are the benefits of regular physical exercise for mental health?",
        [
            "A 2023 umbrella review in the British Journal of Sports Medicine synthesizing 97 meta-analyses (1,039 RCTs, 128,119 participants) found that physical activity significantly reduces symptoms of depression (effect size: SMD -0.43), anxiety (SMD -0.35), and psychological distress (SMD -0.28). Exercise was 1.5 times more effective than cognitive behavioral therapy for depression in head-to-head comparisons.",
            "The WHO's 2020 Guidelines on Physical Activity and Sedentary Behaviour recommend 150-300 minutes of moderate-intensity aerobic activity per week, noting strong evidence that regular exercise reduces the risk of depression by 20-30% and improves cognitive function in older adults.",
            "The American Psychological Association's clinical practice guideline (2019) recognizes exercise as an evidence-based treatment for major depressive disorder, recommending it as an adjunct to psychotherapy and/or medication for mild-to-moderate depression."
        ],
        "Exercise-mental health benefits confirmed by BJSM meta-review, WHO guidelines, and APA clinical guidelines",
        "Three independent sources converge on exercise's antidepressant and anxiolytic effects with consistent effect sizes and clinical recommendations",
        "psychology", "what", "multi_source",
        "factual", "direct",
        context_sources=[
            {"source_id": "bjsm_umbrella_review_2023", "source_type": "academic", "authority": "primary"},
            {"source_id": "who_pa_guidelines_2020", "source_type": "government", "authority": "official"},
            {"source_id": "apa_depression_guideline_2019", "source_type": "academic", "authority": "expert"},
        ],
    ))

    cases.append(make_case(
        "t1_confident_medium_953", "medium", "conditional_confidence",
        "Is working from home more productive than commuting to an office?",
        [
            "A 2023 meta-analysis in Personnel Psychology of 38 studies found that remote workers report 4.8% higher productivity for independent tasks like writing, coding, and data analysis. However, collaborative tasks (brainstorming, mentoring, team problem-solving) showed a 3-5% productivity decrease in remote settings. The net effect depends heavily on job type and measurement approach.",
            "Key conditions affecting outcomes include home workspace quality (dedicated office vs. shared space), caregiving responsibilities, internet reliability, and management style. Organizations with clear remote work policies, regular check-ins, and outcome-based (not hours-based) evaluation saw the highest remote productivity gains. The optimal arrangement for most knowledge workers appears to be hybrid (2-3 days remote), combining focus time at home with collaborative time in office."
        ],
        "Remote work productivity with task-dependent evidence and conditions that modulate outcomes",
        "Evidence supports productivity for independent tasks but not collaborative ones; context clearly specifies conditions (workspace, management style, hybrid balance) that determine outcomes",
        "hr_workplace", "is", "single", "evaluative",
    ))

    cases.append(make_case(
        "t1_confident_medium_954", "medium", "clear_explanation",
        "What are the current interest rates set by the Federal Reserve?",
        [
            "The Federal Reserve's Federal Open Market Committee (FOMC) sets the federal funds rate target range, which as of late 2024 stands at 4.50-4.75% following a 25-basis-point cut in November 2024. This was the second rate cut in the easing cycle that began in September 2024 with a 50-basis-point reduction from the peak of 5.25-5.50% held since July 2023. The Fed also sets the discount rate (primary credit rate) at 4.75% and pays 4.65% on reserve balances (IORB).",
            "The FOMC's Summary of Economic Projections (dot plot) from September 2024 showed the median committee member expecting the funds rate to reach 3.25-3.50% by end of 2025, indicating approximately 100 additional basis points of cuts over the following year, contingent on inflation approaching the 2% target."
        ],
        "Federal Reserve interest rates from FOMC with rate history, related rates, and forward guidance",
        "Context cites the FOMC directly for current target range, cutting cycle history, related administered rates, and dot-plot projections",
        "finance", "what", "single", "factual",
    ))

    return cases


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_queries = {c["query"] for c in data["cases"]}
    existing_ids = {c["id"] for c in data["cases"]}

    new_cases = build_cases()

    # Validate no duplicate queries or IDs
    new_queries = set()
    new_ids = set()
    for c in new_cases:
        assert c["query"] not in existing_queries, f"Duplicate query: {c['query']}"
        assert c["query"] not in new_queries, f"Internal duplicate query: {c['query']}"
        assert c["id"] not in existing_ids, f"Duplicate ID: {c['id']}"
        assert c["id"] not in new_ids, f"Internal duplicate ID: {c['id']}"
        new_queries.add(c["query"])
        new_ids.add(c["id"])

    # Validate counts
    hard_cases = [c for c in new_cases if c["difficulty"] == "hard"]
    medium_cases = [c for c in new_cases if c["difficulty"] == "medium"]
    assert len(hard_cases) == 46, f"Expected 46 hard, got {len(hard_cases)}"
    assert len(medium_cases) == 45, f"Expected 45 medium, got {len(medium_cases)}"
    assert len(new_cases) == 91, f"Expected 91 total, got {len(new_cases)}"

    # Validate ID ranges
    for c in hard_cases:
        num = int(c["id"].split("_")[-1])
        assert 916 <= num <= 961, f"Hard ID out of range: {c['id']}"
    for c in medium_cases:
        num = int(c["id"].split("_")[-1])
        assert 910 <= num <= 954, f"Medium ID out of range: {c['id']}"

    # Validate subcategory distribution
    from collections import Counter
    subcat_counts = Counter(c["subcategory"] for c in new_cases)
    expected_subcats = {
        "technical_documented": 8,
        "clear_explanation": 8,
        "contradiction_resolved": 8,
        "opposing_with_consensus": 8,
        "different_framing": 6,
        "quantitative_answer": 6,
        "cross_source_agreement": 6,
        "direct_factual": 6,
        "multi_source_convergence": 6,
        "authoritative_source": 6,
        "near_complete_evidence": 5,
        "conditional_confidence": 5,
        "step_by_step": 7,
        "definitional": 6,
    }
    for subcat, expected_count in expected_subcats.items():
        actual = subcat_counts.get(subcat, 0)
        assert actual == expected_count, f"Subcategory {subcat}: expected {expected_count}, got {actual}"

    # Validate multi_source count
    multi_source = [c for c in new_cases if c["source_type"] == "multi_source"]
    assert len(multi_source) == 20, f"Expected 20 multi_source, got {len(multi_source)}"

    # Validate all multi_source_convergence are multi_source
    for c in new_cases:
        if c["subcategory"] == "multi_source_convergence":
            assert c["source_type"] == "multi_source", f"{c['id']}: multi_source_convergence must be multi_source"

    # Validate multi_source cases have context_sources
    for c in multi_source:
        assert "context_sources" in c, f"{c['id']}: multi_source missing context_sources"

    # Validate context lengths (150-700 chars; existing corpus median is 449, 42% over 500)
    for c in new_cases:
        for i, ctx in enumerate(c["contexts"]):
            length = len(ctx)
            assert 150 <= length <= 700, f"{c['id']} context {i}: {length} chars (expected 150-700)"

    # Validate domain spread (max 7 per domain)
    domain_counts = Counter(c["domain"] for c in new_cases)
    for domain, count in domain_counts.items():
        assert count <= 7, f"Domain {domain} has {count} cases (max 7)"

    # Validate query type spread
    qt_counts = Counter(c["query_type"] for c in new_cases)
    what_count = qt_counts.get("what", 0)
    how_count = qt_counts.get("how", 0)
    is_does = qt_counts.get("is", 0) + qt_counts.get("does", 0)
    why_should = qt_counts.get("why", 0) + qt_counts.get("should", 0)
    when_who_which = qt_counts.get("when", 0) + qt_counts.get("who", 0) + qt_counts.get("which", 0)

    assert what_count <= 23, f"what: {what_count} (max 23)"
    assert how_count >= 18, f"how: {how_count} (min 18)"
    assert is_does >= 18, f"is/does: {is_does} (min 18)"
    assert why_should >= 10, f"why/should: {why_should} (min 10)"
    assert when_who_which >= 8, f"when/who/which: {when_who_which} (min 8)"

    # Validate all required fields
    required_fields = [
        "id", "difficulty", "subcategory", "query", "contexts", "expected_mode",
        "description", "rationale", "domain", "query_type", "source_type",
        "context_count", "reasoning_type", "evidence_pattern", "category",
        "evaluation_config",
    ]
    for c in new_cases:
        for field in required_fields:
            assert field in c, f"{c['id']} missing field: {field}"

    print(f"All validations passed. Appending {len(new_cases)} cases.")
    print(f"  Hard: {len(hard_cases)}, Medium: {len(medium_cases)}")
    print(f"  Subcategories: {dict(subcat_counts)}")
    print(f"  Multi-source: {len(multi_source)}")
    print(f"  Domains: {dict(domain_counts)}")
    print(f"  Query types: {dict(qt_counts)}")

    data["cases"].extend(new_cases)
    print(f"  Total cases after append: {len(data['cases'])}")

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Done. File written successfully.")


if __name__ == "__main__":
    main()
