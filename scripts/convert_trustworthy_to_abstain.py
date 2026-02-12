#!/usr/bin/env python3
"""Convert 50 trustworthy_hedged/direct cases to abstention cases.

Reads trustworthy_hedged.json and trustworthy_direct.json, converts 50 specific
cases to abstain cases by replacing their contexts with content that makes the
query unanswerable, removes originals from source files, and appends to abstention.json.

Conversion groups:
  A) 15 different_aspects -> converted_off_domain (completely unrelated contexts)
  B) 10 partial_answer -> converted_insufficient (tangentially related, non-answering)
  C) 10 entity_ambiguity -> converted_wrong_entity (different entity, same name)
  D) 5 scope_condition -> converted_wrong_scope (wrong scope/geography/segment)
  E) 10 different_framing -> converted_insufficient (related domain, doesn't answer)
"""

import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "tier1_core"
HEDGED_FILE = DATA_DIR / "trustworthy_hedged.json"
DIRECT_FILE = DATA_DIR / "trustworthy_direct.json"
ABSTENTION_FILE = DATA_DIR / "abstention.json"

NEXT_ABSTAIN_ID = 951

# ---------------------------------------------------------------------------
# Group A: different_aspects -> converted_off_domain
# Replace ALL contexts with completely unrelated off-domain content
# ---------------------------------------------------------------------------
GROUP_A_IDS = [
    "t1_qualify_hard_100", "t1_qualify_hard_101", "t1_qualify_hard_102",
    "t1_qualify_hard_103", "t1_qualify_hard_104",
    "t1_qualify_hard_200", "t1_qualify_hard_201", "t1_qualify_hard_202",
    "t1_qualify_hard_203", "t1_qualify_hard_204", "t1_qualify_hard_205",
    "t1_qualify_hard_206", "t1_qualify_hard_207", "t1_qualify_hard_208",
    "t1_qualify_hard_209",
]

GROUP_A_REPLACEMENTS = {
    # t1_qualify_hard_100: query about drug Veralixib for rheumatoid arthritis
    "t1_qualify_hard_100": {
        "contexts": [
            "Marine biologists at the Woods Hole Oceanographic Institution discovered a new species of deep-sea coral, Desmophyllum abyssalis, at 2,300 meters depth along the New England seamount chain during the 2024 R/V Atlantis expedition. The species forms dense colonies on basalt substrate and hosts a unique chemosynthetic bacterial symbiont not previously documented in cold-water corals. DNA barcoding confirmed it as a distinct species within the Caryophylliidae family.",
            "The Monterey Bay Aquarium Research Institute published a comprehensive survey of hydrothermal vent ecosystems along the Juan de Fuca Ridge. Using ROV Doc Ricketts, researchers catalogued 47 invertebrate species including 6 previously undescribed tubeworm species. Vent fluid temperatures ranged from 28 to 372 degrees Celsius, with hydrogen sulfide concentrations varying from 1.2 to 8.7 millimoles per liter across the surveyed sites.",
            "A 2024 study in Deep-Sea Research documented the migration patterns of the giant isopod Bathynomus giganteus in the Gulf of Mexico. Acoustic tagging of 240 individuals revealed seasonal depth migrations between 300 and 1,800 meters, correlated with bottom water temperature fluctuations. The study also found that giant isopods can survive up to 5 years between feeding events by reducing metabolic rates to 2% of basal levels."
        ],
        "description": "Query asks about rheumatoid arthritis drug efficacy but contexts discuss deep-sea marine biology discoveries",
        "rationale": "The contexts cover deep-sea coral species, hydrothermal vent ecosystems, and giant isopod behavior - completely unrelated to pharmaceutical efficacy, rheumatoid arthritis treatment, or drug safety profiles"
    },
    # t1_qualify_hard_101: query about Falcon 9 rocket reliability
    "t1_qualify_hard_101": {
        "contexts": [
            "The International Olive Council's 2024 production report documented that global olive oil output declined 23% to 2.4 million tonnes due to severe drought conditions in the Mediterranean basin. Spain, which typically produces 40-50% of world supply, saw output drop from 1.3 million tonnes to 680,000 tonnes. The report projected that consumer prices would increase 35-60% across retail markets by mid-2025.",
            "Traditional olive harvesting in the Jaen province of Andalusia involves the 'vareo' technique, where workers use long poles to knock olives from branches onto ground nets. Mechanical trunk-shaking harvesters have increased efficiency by 400% but are only suitable for intensive plantations with tree spacing of 4x1.5 meters. Super-high-density plantations using hedgerow systems now account for 28% of new plantings in Spain and Portugal.",
            "Chemical analysis of extra virgin olive oil requires testing for free fatty acid content (oleic acid equivalent), peroxide value (meq O2/kg), UV absorbance coefficients (K232 and K270), and organoleptic assessment by certified tasting panels. The European Commission Regulation 2568/91 sets maximum limits of 0.8% free acidity and 20 meq/kg peroxide value for the extra virgin classification."
        ],
        "description": "Query asks about Falcon 9 rocket commercial launch reliability but contexts discuss olive oil production, harvesting, and chemical analysis",
        "rationale": "The contexts cover olive oil production statistics, harvesting techniques, and quality testing standards - entirely unrelated to rocket reliability, commercial satellite launches, or aerospace engineering"
    },
    # t1_qualify_hard_102: query about ERP system at Greenfield Manufacturing
    "t1_qualify_hard_102": {
        "contexts": [
            "The Svalbard Global Seed Vault, located 1,300 kilometers from the North Pole on the Norwegian island of Spitsbergen, stores 1.3 million seed samples from gene banks worldwide. The vault operates at minus 18 degrees Celsius inside a mountain of permafrost, ensuring seed viability for centuries without electrical cooling. In 2024, the vault accepted its largest single deposit of 72,000 samples from the International Center for Tropical Agriculture.",
            "Seed dormancy mechanisms vary by species and include physical dormancy (impermeable seed coat), physiological dormancy (hormone-mediated germination inhibition), and morphological dormancy (underdeveloped embryo). Stratification - exposing seeds to cold moist conditions for 4-16 weeks - is required to break dormancy in many temperate tree species including sugar maple, American beech, and northern red oak."
        ],
        "description": "Query asks about ERP system performance at a manufacturing company but contexts discuss seed vault storage and plant dormancy mechanisms",
        "rationale": "The contexts cover the Svalbard Global Seed Vault and botanical seed dormancy science - completely unrelated to enterprise resource planning software, manufacturing operations, or business system performance"
    },
    # t1_qualify_hard_103: query about teacher evaluation framework
    "t1_qualify_hard_103": {
        "contexts": [
            "The Fédération Internationale de Football Association published updated Laws of the Game for the 2024-2025 season, with significant changes to the offside rule. Law 11 now specifies that a player is offside only if any part of the body that can legitimately score a goal is nearer to the opponents' goal line than both the ball and the second-last opponent. Semi-automated offside technology using limb-tracking cameras was mandated for all top-tier competitions.",
            "Video Assistant Referee protocols were revised to require on-field reviews for all penalty area incidents involving potential denial of an obvious goal-scoring opportunity. The IFAB decision matrix now categorizes referee interventions into four tiers: clear and obvious error, serious missed incident, mistaken identity, and goal/no-goal decisions. Average stoppage time for VAR reviews decreased from 73 seconds to 48 seconds following the introduction of streamlined communication protocols.",
            "The offside semi-automated technology system uses 12 dedicated tracking cameras installed beneath the stadium roof, generating 29 data points on each player's body at 50 times per second. The system can detect offside positions with millimeter precision and generates a 3D animation within 25 seconds for broadcast use. FIFA reported a 97.4% accuracy rate in offside decisions during the 2024 Club World Cup."
        ],
        "description": "Query asks about a teacher evaluation framework and educational outcomes but contexts discuss FIFA Laws of the Game and VAR technology",
        "rationale": "The contexts cover football (soccer) rules, VAR protocols, and offside tracking technology - completely unrelated to teacher evaluation, educational assessment, or school district outcomes"
    },
    # t1_qualify_hard_104: query about Azure Government Cloud security
    "t1_qualify_hard_104": {
        "contexts": [
            "The Great Barrier Reef Marine Park Authority's 2024 reef health survey reported that 44% of surveyed reefs experienced moderate to severe coral bleaching during the 2023-2024 austral summer, when sea surface temperatures exceeded the bleaching threshold of 1 degree Celsius above the long-term maximum monthly mean for 8 consecutive weeks. The survey covered 1,080 individual reefs using aerial and in-water methods.",
            "Coral reproduction in the Great Barrier Reef occurs through annual mass spawning events triggered by water temperature, lunar cycles, and day length. The primary spawning event on the outer reef typically occurs 4-6 nights after the full moon in November. Each Acropora colony can release millions of egg-sperm bundles in a synchronized event lasting 30-90 minutes. Fertilization occurs at the ocean surface where bundles break apart.",
            "Crown-of-thorns starfish (Acanthaster planci) populations have undergone four major outbreak cycles on the Great Barrier Reef since monitoring began in 1962. A single adult starfish can consume up to 10 square meters of coral per year. The current control program deploys 23 dedicated vessels injecting bile salt solutions that kill individual starfish within 24-48 hours, treating an average of 135,000 starfish annually."
        ],
        "description": "Query asks about Azure Government Cloud security for classified workloads but contexts discuss Great Barrier Reef coral bleaching and marine ecology",
        "rationale": "The contexts cover coral bleaching surveys, coral reproduction biology, and crown-of-thorns starfish control - entirely unrelated to cloud security, classified workload handling, or government IT infrastructure"
    },
    # t1_qualify_hard_200: query about ProMax 3000 performance
    "t1_qualify_hard_200": {
        "contexts": [
            "The 2024 International Coffee Organization annual report documented that global coffee production reached 178.5 million 60-kilogram bags, with Brazil contributing 66.4 million bags (37.2% of world output). Arabica varieties accounted for 58% of production, with robusta growing to 42% due to expanding plantings in Vietnam and Indonesia. Average C-market prices for Arabica futures on ICE rose to $2.34 per pound, a 12-year high driven by drought in Brazil's Minas Gerais region.",
            "The specialty coffee grading system developed by the Specialty Coffee Association evaluates green coffee on a 100-point scale. Coffees scoring 80 points or above are classified as specialty grade. Evaluation criteria include fragrance/aroma, flavor, aftertaste, acidity, body, balance, uniformity, clean cup, sweetness, and defects. A certified Q-grader must complete 22 individual sensory tests and maintain calibration through triennial recertification.",
            "Processing methods significantly influence coffee flavor profiles. Washed (wet) processing produces cleaner, brighter cups with pronounced acidity. Natural (dry) processing yields fruitier, more full-bodied flavors with reduced acidity. Honey processing, where varying amounts of mucilage remain on the bean during drying, creates intermediate flavor characteristics. Anaerobic fermentation, an emerging technique, involves sealed-tank fermentation at controlled temperatures for 48-96 hours."
        ],
        "description": "Query asks about the ProMax 3000 product performance but contexts discuss global coffee production, grading systems, and processing methods",
        "rationale": "The contexts cover coffee production statistics, the SCA grading scale, and coffee processing techniques - entirely unrelated to the ProMax 3000 product, its sales performance, or its technical reliability"
    },
    # t1_qualify_hard_201: query about downtown transit line success
    "t1_qualify_hard_201": {
        "contexts": [
            "The National Beekeeping Institute's 2024 annual survey recorded 2.71 million managed honey bee colonies in the United States, a 2.3% decline from the previous year. Colony loss rates during the October 2023 to April 2024 winter period averaged 37.4%, with Varroa destructor mites identified as the primary contributing factor in 68% of losses. Backyard beekeepers (managing fewer than 50 colonies) reported higher loss rates of 44.2% compared to 28.1% for commercial operations managing more than 500 colonies.",
            "Neonicotinoid pesticides, particularly imidacloprid, clothianidin, and thiamethoxam, have been implicated in sublethal effects on honey bee navigation and foraging efficiency. A 2024 meta-analysis in Environmental Science and Technology found that field-realistic exposure levels reduced foraging trip success by 23% and impaired the waggle dance communication accuracy by 31%. The European Union maintained its outdoor ban on the three neonicotinoids, while the US EPA completed a new biological evaluation finding unacceptable risk to bee colonies from registered uses."
        ],
        "description": "Query asks about the success of a downtown transit line but contexts discuss honey bee colony losses and pesticide impacts on pollinators",
        "rationale": "The contexts cover beekeeping colony statistics and neonicotinoid pesticide effects on honey bees - completely unrelated to urban transit, light rail ridership, or transportation infrastructure"
    },
    # t1_qualify_hard_202: query about Chesapeake Bay biodiversity
    "t1_qualify_hard_202": {
        "contexts": [
            "The European Space Agency's Rosetta mission to Comet 67P/Churyumov-Gerasimenko revealed that the comet's nucleus is composed primarily of dust and water ice in roughly equal proportions, with trace amounts of carbon dioxide, carbon monoxide, and molecular oxygen. The bilobed shape results from a low-velocity collision between two distinct bodies approximately 4.5 billion years ago. Surface temperatures ranged from minus 70 to plus 50 degrees Celsius depending on solar distance and local topography.",
            "Analysis of cometary dust collected by the Stardust mission and returned to Earth in 2006 identified crystalline silicates including forsterite and enstatite that must have formed at temperatures exceeding 1,000 degrees Celsius, far higher than expected in the outer solar system. This finding supports models of large-scale radial mixing in the protoplanetary disk, where materials formed near the young Sun were transported to the comet-forming region beyond Neptune.",
            "The Oort Cloud, a hypothesized spherical shell of icy bodies extending from 2,000 to 200,000 astronomical units from the Sun, is believed to contain several trillion cometary nuclei with a combined mass of approximately 5 Earth masses. Long-period comets originate from gravitational perturbations by passing stars and galactic tides that redirect Oort Cloud objects into the inner solar system. The Kuiper Belt, a flattened disk extending from 30 to 55 AU, is the source of short-period comets with orbital periods under 200 years."
        ],
        "description": "Query asks about biodiversity in the Chesapeake Bay but contexts discuss comet composition, cometary dust analysis, and the Oort Cloud",
        "rationale": "The contexts cover cometary science, solar system formation, and the Oort Cloud - completely unrelated to Chesapeake Bay ecology, aquatic biodiversity, or estuarine environmental conditions"
    },
    # t1_qualify_hard_203: query about company's remote work policy effectiveness
    "t1_qualify_hard_203": {
        "contexts": [
            "The International Astronomical Union's 2024 Planetary Defense Conference reported that NASA's DART mission successfully altered asteroid Dimorphos's orbital period by 33 minutes (from 11 hours 55 minutes to 11 hours 22 minutes), exceeding the minimum requirement of 73 seconds. The kinetic impactor struck at 6.1 kilometers per second, excavating approximately 1,000 tonnes of ejecta that provided additional momentum transfer beyond the direct impact.",
            "The Vera C. Rubin Observatory's Legacy Survey of Space and Time, expected to begin operations in 2025, will catalog an estimated 5.8 million near-Earth objects over its 10-year survey period, increasing the known population by a factor of 10. The 8.4-meter telescope's 3.2-gigapixel camera will image the entire visible sky every three nights, enabling detection of objects as small as 140 meters at distances beyond 1 AU.",
            "Planetary defense strategies beyond kinetic impact include gravity tractors (spacecraft hovering near an asteroid to slowly alter its trajectory via gravitational attraction over years), ion beam deflection (using a spacecraft's ion thruster to push the asteroid), and nuclear standoff detonation (detonating a nuclear device near the asteroid surface to vaporize material and generate thrust). Each method has different lead-time requirements ranging from months for kinetic impact to decades for gravity tractors."
        ],
        "description": "Query asks about the effectiveness of a company's remote work policy but contexts discuss asteroid deflection, the DART mission, and planetary defense strategies",
        "rationale": "The contexts cover NASA's DART asteroid impact mission, observatory surveys, and planetary defense techniques - completely unrelated to remote work policies, employee productivity, or organizational management"
    },
    # t1_qualify_hard_204: query about country's education system improving
    "t1_qualify_hard_204": {
        "contexts": [
            "The 2024 World Whisky Awards recognized Kavalan Distillery of Taiwan as World's Best Single Malt for its Solist Vinho Barrique expression. Japanese distilleries claimed 7 of the top 20 positions, with Yamazaki, Hakushu, and Chichibu all receiving multiple awards. Scottish single malts from Islay dominated the peated category, with Ardbeg and Laphroaig sharing gold medals.",
            "Whisky maturation in oak casks involves complex chemical interactions between the spirit and the wood. Vanillin and other phenolic compounds are extracted from lignin, while tannins and lactones contribute to flavor complexity. The 'angel's share' - spirit lost to evaporation through the cask - averages 2% per year in Scotland's cool climate but reaches 6-10% annually in tropical aging environments like Taiwan and India, significantly accelerating the maturation process."
        ],
        "description": "Query asks about improvement in a country's education system but contexts discuss international whisky awards and cask maturation chemistry",
        "rationale": "The contexts cover whisky competition results and barrel aging science - entirely unrelated to education systems, enrollment rates, learning outcomes, or educational policy"
    },
    # t1_qualify_hard_205: query about Zephyr autonomous driving system safety
    "t1_qualify_hard_205": {
        "contexts": [
            "The Bayreuth Festival's 2024 season premiered a new production of Wagner's Parsifal directed by Jay Scheib, incorporating augmented reality headsets for 300 of the 1,974 audience members. The production featured real-time holographic projections of the Holy Grail and Klingsor's magic garden overlaid on the physical stage. Music director Pablo Heras-Casado led the festival orchestra in a performance described by Die Zeit as 'the most technologically ambitious staging in the Festspielhaus's 148-year history.'",
            "Wagner's concept of Gesamtkunstwerk (total work of art) aimed to synthesize music, poetry, visual arts, and stagecraft into a unified dramatic experience. The specially designed Bayreuth Festspielhaus features a covered orchestra pit that blends instrumental sound before it reaches the audience, creating the distinctive 'Bayreuth sound.' The theater seats 1,974 on wooden chairs without armrests, and performances are traditionally unjacketed due to the lack of air conditioning.",
            "The Ring Cycle (Der Ring des Nibelungen) requires approximately 15 hours of performance across four operas - Das Rheingold, Die Walkure, Siegfried, and Gotterdammerung. A complete Ring Cycle at Bayreuth employs over 300 musicians, singers, and technical staff. Ticket allocation uses a waiting list that historically averaged 10 years, though recent reforms have introduced a lottery system for 25% of tickets."
        ],
        "description": "Query asks about the safety of an autonomous driving system but contexts discuss the Bayreuth Wagner Festival, opera staging, and the Ring Cycle",
        "rationale": "The contexts cover Wagnerian opera performances, theater architecture, and the Ring Cycle - completely unrelated to autonomous vehicle safety, collision rates, or self-driving technology"
    },
    # t1_qualify_hard_206: query about whether new hospital is performing well
    "t1_qualify_hard_206": {
        "contexts": [
            "The 2024 International Cheese Awards at Nantwich received 5,891 entries from 42 countries. The Supreme Champion title went to a 24-month aged Comte from Fromagerie Marcel Petite in eastern France, which scored 98 out of 100 on texture, flavor complexity, and aroma. Swiss Gruyere and Italian Parmigiano Reggiano placed second and third respectively in the hard cheese category.",
            "Artisanal cheese production relies on carefully maintained microbial cultures. Penicillium roqueforti creates the blue veins in Roquefort and Gorgonzola through aerobic growth in needle-punctured curd. Brevibacterium linens produces the orange rind and pungent aroma of washed-rind cheeses like Epoisses and Munster. Propionibacterium freudenreichii generates carbon dioxide during fermentation, forming the characteristic holes in Emmental and Jarlsberg."
        ],
        "description": "Query asks about whether a new hospital is performing well but contexts discuss international cheese competitions and artisanal cheese microbiology",
        "rationale": "The contexts cover cheese awards and the microbiology of cheese production - entirely unrelated to hospital performance, patient outcomes, clinical quality, or healthcare operations"
    },
    # t1_qualify_hard_207: query about minimum wage increase impact on workers
    "t1_qualify_hard_207": {
        "contexts": [
            "The James Webb Space Telescope's Mid-Infrared Instrument (MIRI) detected atmospheric carbon dioxide in the atmosphere of exoplanet WASP-39b, a hot Jupiter orbiting a Sun-like star 700 light-years from Earth. The transmission spectrum obtained during a single transit event revealed a CO2 absorption feature at 4.3 microns with a signal-to-noise ratio of 26. This marked the first unambiguous detection of CO2 in an exoplanet atmosphere.",
            "JWST's Near-Infrared Spectrograph (NIRSpec) observed the galaxy JADES-GS-z13-0 at redshift z=13.2, corresponding to 320 million years after the Big Bang. The galaxy's stellar mass was estimated at 100 million solar masses with a star formation rate of 1.7 solar masses per year. The spectrum showed strong Lyman-alpha emission and metal line detections suggesting rapid chemical enrichment inconsistent with standard models of early galaxy evolution.",
            "Exoplanet detection via the transit method measures the fractional decrease in stellar brightness as a planet crosses the star's disk. For a Jupiter-sized planet orbiting a Sun-like star, the transit depth is approximately 1%, while an Earth-sized planet produces a transit depth of only 0.008%. JWST's photometric precision of 10-20 parts per million enables atmospheric characterization of planets as small as sub-Neptunes around M-dwarf stars."
        ],
        "description": "Query asks about the impact of a minimum wage increase on workers but contexts discuss JWST exoplanet atmospheric detection and early galaxy observations",
        "rationale": "The contexts cover exoplanet spectroscopy, high-redshift galaxy observations, and transit photometry - completely unrelated to labor economics, minimum wage policy, or worker employment outcomes"
    },
    # t1_qualify_hard_208: query about Dynamo Software enterprise competitiveness
    "t1_qualify_hard_208": {
        "contexts": [
            "The International Association of Volcanology reported 47 eruptions from 39 different volcanoes during 2024, with the most significant being the February eruption of Sundhnukur on Iceland's Reykjanes Peninsula, which produced a 4.2-kilometer fissure and lava flows that threatened the town of Grindavik. Lava effusion rates peaked at 200 cubic meters per second during the initial phase.",
            "Volcanic eruption prediction relies on monitoring seismic swarms, ground deformation via InSAR satellite imagery, gas emissions (particularly SO2 and CO2 ratios), and changes in hydrothermal activity. The Philippines Institute of Volcanology and Seismology uses a five-level alert system for Taal Volcano, with Level 5 indicating a hazardous eruption in progress. GPS stations around Taal have detected cumulative inflation of 1.2 meters since 2020.",
            "Pyroclastic flows, the most lethal volcanic hazard, consist of hot gas and volcanic fragments traveling at speeds up to 700 kilometers per hour at temperatures exceeding 400 degrees Celsius. The AD 79 eruption of Vesuvius killed an estimated 16,000 people primarily through pyroclastic surges. Modern hazard maps for Vesuvius define a 'red zone' requiring mandatory evacuation of 700,000 residents in the event of a VEI 4 or greater eruption."
        ],
        "description": "Query asks about Dynamo Software's enterprise market competitiveness but contexts discuss volcanic eruptions, eruption prediction, and pyroclastic flow hazards",
        "rationale": "The contexts cover global volcanic activity, monitoring techniques, and pyroclastic flow physics - entirely unrelated to enterprise software competitiveness, market analysis, or technology vendor evaluation"
    },
    # t1_qualify_hard_209: query about environmental impact of lithium mining
    "t1_qualify_hard_209": {
        "contexts": [
            "The 2024 World Championship of Competitive Eating sanctioned by Major League Eating saw Joey Chestnut consume 83 Nathan's Famous hot dogs in 10 minutes at the annual July 4th contest on Coney Island, breaking his own record of 76 set in 2021. The competition draws approximately 35,000 live spectators and 1.5 million television viewers annually on ESPN.",
            "Competitive eating physiology research published in the American Journal of Roentgenology found that elite competitive eaters develop the ability to suppress the gag reflex and relax the stomach fundus to accommodate volumes exceeding 4 liters. MRI studies showed that top competitors' stomachs expanded to approximately 10 times normal resting volume during competition. Long-term health effects remain understudied, though gastroenterologists have documented cases of gastroparesis in retired competitive eaters.",
            "The International Federation of Competitive Eating maintains a ranking system based on performance in sanctioned events across 15 food disciplines including hot dogs, chicken wings, oysters, and pie. Training regimens for elite competitors typically involve stomach capacity expansion using water or low-calorie fluids, jaw strength conditioning, and technique refinement for specific food items. Prize purses at major events range from $10,000 to $40,000."
        ],
        "description": "Query asks about environmental impact of a lithium mining operation but contexts discuss competitive eating records, physiology, and federation rankings",
        "rationale": "The contexts cover competitive eating competitions, gastrointestinal physiology of speed eaters, and eating contest organization - completely unrelated to lithium mining, environmental impact assessment, or resource extraction"
    },
}

# ---------------------------------------------------------------------------
# Group B: partial_answer -> converted_insufficient
# Replace with tangentially related contexts that don't answer ANY part
# ---------------------------------------------------------------------------
GROUP_B_IDS = [
    "t1_qualify_hard_400", "t1_qualify_hard_401", "t1_qualify_hard_402",
    "t1_qualify_hard_403", "t1_qualify_hard_404", "t1_qualify_hard_405",
    "t1_qualify_hard_406", "t1_qualify_hard_407", "t1_qualify_hard_408",
    "t1_qualify_hard_409",
]

GROUP_B_REPLACEMENTS = {
    # t1_qualify_hard_400: query about metformin dosage for stage 3 CKD patients
    "t1_qualify_hard_400": {
        "contexts": [
            "The history of metformin traces back to medieval European herbal medicine, where French lilac (Galega officinalis) was used to treat symptoms associated with frequent urination. Guanidine, the active compound in Galega, was synthesized in the laboratory in 1922 by Werner and Bell. Metformin (dimethylbiguanide) was first described by Emil Werner and James Bell in 1922 but was not investigated for glucose-lowering properties until Jean Sterne published results in 1957.",
            "The global diabetes pharmaceutical market was valued at $78.2 billion in 2024, with metformin accounting for approximately $4.8 billion despite being available as a generic since 2002. Market analysts project the diabetes drug market will reach $126 billion by 2030, driven primarily by GLP-1 receptor agonists such as semaglutide and tirzepatide. Metformin's market share has declined from 18% to 6% over the past decade as newer agents have gained formulary preference."
        ],
        "description": "Query asks about metformin dosage adjustments for stage 3 CKD patients but contexts discuss the historical origins of metformin and the diabetes pharmaceutical market size",
        "rationale": "The contexts provide the history of metformin's discovery and its market position among diabetes drugs, but contain no prescribing information, dosage guidelines, or renal dosing adjustments needed to answer the specific clinical question"
    },
    # t1_qualify_hard_401: query about penalty for late filing Form 1120-S
    "t1_qualify_hard_401": {
        "contexts": [
            "The history of the S corporation election dates to the Technical Amendments Act of 1958, which created Subchapter S of the Internal Revenue Code. The original legislation was championed by President Eisenhower's Treasury Department to allow small businesses to avoid double taxation while maintaining limited liability protection. The Subchapter S Revision Act of 1982 expanded eligibility and simplified the election process, increasing the maximum number of shareholders from 15 to 35.",
            "A comparative analysis of business entity taxation published in the Tax Law Review examined the relative tax efficiency of S corporations, C corporations, LLCs taxed as partnerships, and sole proprietorships. The study found that S corporations provided the greatest tax efficiency for businesses with annual net income between $100,000 and $400,000 when owners actively participate in the business. For passive investors or businesses with income exceeding $500,000, the qualified business income deduction under Section 199A often made LLC structures more advantageous."
        ],
        "description": "Query asks about the specific penalty amount for late filing Form 1120-S but contexts discuss the legislative history of S corporations and comparative business entity taxation",
        "rationale": "The contexts cover the history of Subchapter S legislation and comparative tax efficiency of business entities - neither mentions late filing penalties, IRS penalty calculations, or any specific dollar amounts for Form 1120-S delinquency"
    },
    # t1_qualify_hard_402: query about maximum occupancy for assembly spaces under 2021 fire code
    "t1_qualify_hard_402": {
        "contexts": [
            "The history of building fire codes in the United States traces to the Great Chicago Fire of 1871 and the Triangle Shirtwaist Factory fire of 1911. The first model building code was published by the Building Officials and Code Administrators International in 1950. The International Code Council was formed in 1994 from the merger of three regional code organizations, and the first International Fire Code was published in 2000. Major code revisions have historically been driven by catastrophic fire events including the Station nightclub fire in 2003.",
            "Fire protection engineering as a professional discipline emerged from the insurance industry's need to quantify fire risk. The Society of Fire Protection Engineers, founded in 1950, currently has 4,500 members globally. University programs in fire protection engineering are offered at the University of Maryland, Worcester Polytechnic Institute, and Cal Poly San Luis Obispo. The discipline integrates heat transfer, fluid dynamics, combustion science, human behavior in fire, and structural engineering to design fire-safe buildings."
        ],
        "description": "Query asks about specific maximum occupancy numbers under the 2021 fire code but contexts discuss the history of US fire codes and fire protection engineering as a profession",
        "rationale": "The contexts cover the historical development of building codes and fire protection engineering education, but contain no specific occupancy load factors, assembly space calculations, or 2021 IFC provisions needed to answer the question"
    },
    # t1_qualify_hard_403: query about five-year survival rate for stage IIIA NSCLC with immunotherapy
    "t1_qualify_hard_403": {
        "contexts": [
            "The Nobel Prize in Physiology or Medicine was awarded in 2018 to James P. Allison and Tasuku Honjo for their discovery of cancer therapy by inhibition of negative immune regulation. Allison's work on CTLA-4 at UC Berkeley in the 1990s demonstrated that blocking this immune checkpoint could unleash T-cell responses against tumors. Honjo's identification of PD-1 at Kyoto University in 1992 led to the development of anti-PD-1 antibodies now used in clinical practice.",
            "The global immunotherapy market reached $187 billion in 2024, with checkpoint inhibitors representing $68 billion of that total. Pembrolizumab (Keytruda) alone generated $25.0 billion in global sales, making it the world's best-selling drug. The market is projected to reach $290 billion by 2030 as immunotherapy combinations expand into earlier disease stages and new tumor types. Competition is intensifying with over 5,000 immunotherapy clinical trials registered on ClinicalTrials.gov as of December 2024."
        ],
        "description": "Query asks about specific five-year survival rates for stage IIIA NSCLC treated with immunotherapy but contexts discuss the Nobel Prize for checkpoint inhibitor discovery and the immunotherapy market size",
        "rationale": "The contexts cover the scientific history of immune checkpoint discovery and the commercial immunotherapy market, but provide no survival statistics, clinical trial outcomes, or stage-specific lung cancer prognosis data"
    },
    # t1_qualify_hard_404: query about minimum ventilation rates for operating rooms per ASHRAE 170
    "t1_qualify_hard_404": {
        "contexts": [
            "The American Society of Heating, Refrigerating and Air-Conditioning Engineers was founded in 1894 and currently has over 57,000 members in 132 countries. ASHRAE publishes standards, guidelines, and handbooks covering building HVAC systems, refrigeration, and indoor air quality. The organization's headquarters moved from Atlanta to Peachtree Corners, Georgia, in 2022 into a net-zero-energy building that serves as a living laboratory for sustainable building technologies.",
            "The evolution of hospital ventilation practices was shaped by landmark infection control studies. The Wells-Riley equation, developed in the 1970s, models airborne infection probability as a function of quantum generation rate, pulmonary ventilation rate, and room air supply. Seminal work by Lidwell et al. in the 1980s demonstrated that ultra-clean air enclosures reduced deep surgical site infection rates from 3.4% to 1.6% in joint replacement procedures. These studies provided the scientific basis for modern operating room ventilation standards."
        ],
        "description": "Query asks about specific minimum ventilation rates from ASHRAE Standard 170 but contexts discuss ASHRAE's organizational history and the epidemiological basis of hospital ventilation research",
        "rationale": "The contexts cover ASHRAE as an organization and the historical infection control research underlying ventilation standards, but provide no specific air change rates, pressure relationships, or filtration requirements from ASHRAE Standard 170"
    },
    # t1_qualify_hard_405: query comparing Samsung T7 Shield vs SanDisk Extreme Pro SSD
    "t1_qualify_hard_405": {
        "contexts": [
            "NAND flash memory technology has evolved through several generations. Single-level cell (SLC) stores 1 bit per cell and offers the highest endurance. Multi-level cell (MLC) stores 2 bits per cell. Triple-level cell (TLC) stores 3 bits and is used in most consumer SSDs. Quad-level cell (QLC) stores 4 bits but has reduced write endurance. The transition from planar NAND to 3D NAND, pioneered by Samsung's V-NAND in 2013, stacks memory cells vertically to increase density. Current 3D NAND designs reach 236 layers.",
            "The USB Implementers Forum ratified the USB4 Version 2.0 specification in September 2022, supporting data transfer rates up to 80 Gbps over USB Type-C cables. USB4 is based on the Thunderbolt 3 protocol contributed by Intel to the USB-IF. Backward compatibility with USB 3.2, USB 2.0, and Thunderbolt 3 devices is maintained. The specification includes optional support for DisplayPort 2.1 alternate mode, enabling 8K display output over a single cable."
        ],
        "description": "Query asks for a specific comparison of Samsung T7 Shield versus SanDisk Extreme Pro SSD specs but contexts discuss NAND flash technology generations and the USB4 specification",
        "rationale": "The contexts cover NAND memory technology evolution and USB4 standards but provide no product-specific specifications, benchmark data, or durability ratings for either the Samsung T7 Shield or SanDisk Extreme Pro"
    },
    # t1_qualify_hard_406: query about ingredients, nutrition, and allergens for plant-based burger
    "t1_qualify_hard_406": {
        "contexts": [
            "The global plant-based meat market was valued at $7.9 billion in 2024, with North America representing 42% of sales. Key players include Beyond Meat, Impossible Foods, and Nestle's Garden Gourmet brand. Market growth decelerated from 27% annually in 2020-2021 to 8% in 2024 as novelty purchasing faded and repeat purchase rates stabilized at 34%. Venture capital investment in alternative protein companies declined 52% from peak 2021 levels.",
            "Consumer attitudes toward plant-based meat alternatives were surveyed in a 2024 Mintel study of 4,000 US adults. Key findings: 62% of respondents had tried a plant-based meat product, 31% purchased at least monthly, and the primary motivation was health concerns (47%) followed by environmental sustainability (28%) and animal welfare (18%). The top barriers to adoption were taste (cited by 54% of non-adopters), price premium (41%), and ingredient concerns about ultra-processing (38%)."
        ],
        "description": "Query asks about specific ingredients, nutritional information, and allergen warnings for a plant-based burger but contexts discuss the plant-based meat market size and consumer attitude surveys",
        "rationale": "The contexts cover market valuation, competitive landscape, and consumer purchase motivation, but provide no specific product formulation, ingredient lists, nutritional facts, or allergen declarations"
    },
    # t1_qualify_hard_407: query about company revenue, operating expenses, and net income for Q4 2024
    "t1_qualify_hard_407": {
        "contexts": [
            "SEC Form 10-K filing requirements mandate that public companies disclose audited annual financial statements, management's discussion and analysis (MD&A), and risk factors within 60 days of fiscal year end for large accelerated filers. The Sarbanes-Oxley Act of 2002 added requirements for internal control assessments (Section 404) and CEO/CFO certification of financial statements (Section 302). The PCAOB conducts inspections of the auditing firms that perform these audits.",
            "Financial statement analysis ratios commonly used by investors include the current ratio (current assets divided by current liabilities), debt-to-equity ratio, return on equity (net income divided by shareholders' equity), and earnings per share. Price-to-earnings ratio allows comparison of company valuation relative to earnings across industry peers. Free cash flow, calculated as operating cash flow minus capital expenditures, is considered a more reliable indicator of financial health than net income because it is less susceptible to accounting manipulation."
        ],
        "description": "Query asks for specific Q4 2024 revenue, operating expenses, and net income figures but contexts discuss SEC filing requirements and generic financial analysis ratios",
        "rationale": "The contexts cover regulatory filing requirements and textbook financial ratios but contain no actual company financial data, quarterly results, or specific monetary figures for Q4 2024"
    },
    # t1_qualify_hard_408: query about eligibility, benefit amounts, and deadlines for renewable energy tax credit
    "t1_qualify_hard_408": {
        "contexts": [
            "The history of renewable energy tax incentives in the United States began with the Energy Tax Act of 1978, which offered a 30% residential energy credit for solar and wind installations. The Production Tax Credit for wind energy was first enacted in the Energy Policy Act of 1992 at 1.5 cents per kilowatt-hour. The Investment Tax Credit for solar was set at 30% in the Energy Policy Act of 2005 and has been extended multiple times, most recently through the Inflation Reduction Act of 2022.",
            "A comparative study of state renewable energy programs published in Energy Policy found wide variation in program design, with direct rebates, performance-based incentives, property tax exemptions, and sales tax exemptions used alongside tax credits. States with the most effective programs combined financial incentives with streamlined permitting processes and interconnection standards. The study identified the top five state programs based on installed capacity per capita: Hawaii, California, Massachusetts, New Jersey, and Arizona."
        ],
        "description": "Query asks about specific eligibility requirements, benefit amounts, and deadlines for a state renewable energy tax credit but contexts discuss the federal history of energy tax incentives and a comparative study of state program designs",
        "rationale": "The contexts cover the legislative history of federal energy tax credits and an academic comparison of state program structures, but contain no specific state program eligibility criteria, credit amounts, or application deadlines"
    },
    # t1_qualify_hard_409: query about setup process, languages, and pricing for AI translation API
    "t1_qualify_hard_409": {
        "contexts": [
            "The history of machine translation dates to Warren Weaver's 1949 memorandum proposing the application of cryptographic and statistical techniques to language translation. The Georgetown-IBM experiment of 1954 demonstrated the first successful machine translation of Russian sentences into English using a rule-based approach. Statistical machine translation, pioneered by Peter Brown and colleagues at IBM in the late 1980s, dominated the field for two decades before neural machine translation, introduced by Sutskever, Vinyals, and Le in 2014, achieved breakthrough quality improvements.",
            "The BLEU (Bilingual Evaluation Understudy) metric, developed by Kishore Papineni et al. at IBM Research in 2002, remains the most widely used automatic metric for evaluating machine translation quality. BLEU calculates the modified n-gram precision between machine translation output and human reference translations. Scores range from 0 to 1, with scores above 0.3 generally indicating understandable translations. Alternative metrics include METEOR, TER (Translation Edit Rate), and the more recent COMET metric based on cross-lingual sentence embeddings."
        ],
        "description": "Query asks about specific setup process, supported languages, and pricing for an AI translation API but contexts discuss the history of machine translation and automatic evaluation metrics",
        "rationale": "The contexts cover the historical evolution of machine translation technology and evaluation metrics like BLEU, but provide no API setup instructions, supported language lists, or pricing information"
    },
}

# ---------------------------------------------------------------------------
# Group C: entity_ambiguity -> converted_wrong_entity
# Replace contexts with information about a DIFFERENT entity sharing a similar name
# ---------------------------------------------------------------------------
GROUP_C_IDS = [
    "t1_qualify_hard_028", "t1_qualify_hard_029", "t1_qualify_hard_030",
    "t1_qualify_hard_031", "t1_qualify_hard_032", "t1_qualify_hard_033",
    "t1_qualify_hard_036", "t1_qualify_hard_037", "t1_qualify_hard_125",
    "t1_qualify_hard_126",
]

GROUP_C_REPLACEMENTS = {
    # t1_qualify_hard_028: query "What was Apple's revenue last quarter?"
    # Original has Apple Inc, Apple Records, and apple fruit. Replace with ONLY Apple Records.
    "t1_qualify_hard_028": {
        "contexts": [
            "Apple Records Ltd, the record label founded in 1968 by the Beatles, reported its annual financial results for the fiscal year ending March 2024. The label's revenue from catalogue licensing and digital distribution totaled 14.8 million pounds, a 6% increase over the prior year driven by strong streaming performance of remastered Beatles tracks on Spotify and Apple Music. The label's parent company, Apple Corps Ltd, also receives ongoing royalties from the Beatles' publishing catalogue managed through Sony Music Publishing.",
            "Apple Corps Ltd, the holding company for the Beatles' business interests, disclosed total group revenue of 28.3 million pounds for the year. The company's divisions include Apple Records (music), Apple Films (visual media), and Apple Publishing. A significant contributor to the year's results was the November 2023 release of the AI-completed Beatles track 'Now and Then,' which generated 3.2 million pounds in its first four months. Apple Corps maintains its headquarters at 27 Ovington Square, London."
        ],
        "description": "Query asks about Apple's revenue last quarter (likely meaning Apple Inc., the technology company) but contexts only discuss Apple Records Ltd and Apple Corps Ltd, the Beatles' record label and holding company",
        "rationale": "The contexts provide financial data for Apple Records and Apple Corps - the Beatles' business entities - not Apple Inc., the trillion-dollar technology company. The query cannot be answered because no Apple Inc. revenue data is provided"
    },
    # t1_qualify_hard_029: query "When was the Mercury program completed?"
    # Original has NASA Mercury, Ford Mercury, and Mercury Prize. Replace with ONLY Mercury car.
    "t1_qualify_hard_029": {
        "contexts": [
            "The Mercury Automobile Division of Ford Motor Company traced its origins to Edsel Ford's desire to create a mid-price vehicle bridging the gap between Ford and Lincoln brands. The first Mercury model, the Mercury Eight, debuted in 1938 with a flathead V-8 engine producing 95 horsepower. Peak production occurred in 1978 when Mercury sold 580,000 vehicles. The brand suffered declining sales through the 1990s and 2000s as its model lineup increasingly overlapped with Ford-branded equivalents.",
            "Ford Motor Company officially discontinued the Mercury brand on January 4, 2011, after 72 years of production. The final Mercury vehicle, a Grand Marquis sedan, rolled off the assembly line at Ford's St. Thomas Assembly Plant in Ontario, Canada, on September 15, 2010. The decision to terminate Mercury was announced by Ford CEO Alan Mulally as part of the 'One Ford' restructuring strategy, which consolidated resources around the Ford and Lincoln nameplates. Approximately 2,800 Mercury dealers received transition assistance to become Ford or Lincoln dealers.",
            "The Mercury Cougar, one of the brand's most iconic models, was produced in various forms from 1967 to 2002. The first-generation Cougar shared its platform with the Ford Mustang but featured more upscale appointments and distinctive sequential turn signals. The model name was revived in 1999 as a front-wheel-drive coupe based on the Ford Contour platform but was discontinued in 2002 due to poor sales averaging only 25,000 units annually."
        ],
        "description": "Query asks about when the Mercury program was completed (likely meaning NASA's Project Mercury space program) but contexts only discuss the Mercury automobile brand produced by Ford Motor Company from 1938 to 2011",
        "rationale": "The contexts cover the Ford Mercury car brand's history and discontinuation - a completely different 'Mercury program' than NASA's human spaceflight program (1958-1963). The query about the space program completion cannot be answered from automobile brand history"
    },
    # t1_qualify_hard_030: query "What is the current status of the Paris Agreement?"
    # Original has climate, Vietnam peace, AI safety. Replace with ONLY Paris peace agreement.
    "t1_qualify_hard_030": {
        "contexts": [
            "The Paris Peace Agreements of January 27, 1973, officially titled the Agreement on Ending the War and Restoring Peace in Vietnam, were signed by representatives of the United States, North Vietnam, South Vietnam, and the Provisional Revolutionary Government of the Viet Cong. The agreements called for a cease-fire throughout Vietnam, withdrawal of all US forces within 60 days, release of prisoners of war, and the establishment of an international commission to oversee the agreements' implementation.",
            "Henry Kissinger and Le Duc Tho were jointly awarded the 1973 Nobel Peace Prize for negotiating the Paris Peace Agreements, though Le Duc Tho declined the award stating that peace had not yet been established in Vietnam. The International Commission of Control and Supervision, comprising representatives from Canada, Hungary, Indonesia, and Poland, was deployed to monitor compliance but was widely regarded as ineffective. North Vietnamese forces violated the cease-fire provisions almost immediately, and the agreements ultimately failed to prevent the fall of Saigon on April 30, 1975.",
            "Scholarly reassessment of the Paris Peace Agreements in the decades since their signing has generally concluded that the agreements served primarily as a diplomatic mechanism for US withdrawal rather than as a genuine framework for peace. Historian Larry Berman's 2001 work 'No Peace, No Honor' documented that both Kissinger and Tho understood the agreements were unlikely to hold, with Tho privately telling colleagues the cease-fire would last '18 months at most.'"
        ],
        "description": "Query asks about the current status of the Paris Agreement (likely meaning the 2015 UN climate agreement) but contexts only discuss the 1973 Paris Peace Agreements ending US involvement in the Vietnam War",
        "rationale": "The contexts cover the 1973 Vietnam peace agreements - their signing, failure, and historical reassessment - not the 2015 Paris climate agreement. The current ratification status, emissions targets, and implementation progress of the climate Paris Agreement cannot be determined from Vietnam War peace accord history"
    },
    # t1_qualify_hard_031: query "What is the budget for the project?"
    # Original has three projects. Replace with a completely different unnamed project.
    "t1_qualify_hard_031": {
        "contexts": [
            "The Crossrail project (now the Elizabeth Line) in London was the largest infrastructure project in Europe when construction began in 2009. The project's budget was initially set at 14.8 billion pounds but ultimately cost 18.9 billion pounds by completion in 2022, a 28% overrun. The 13-year construction program involved boring 42 kilometers of new tunnels beneath central London using eight tunnel boring machines, each weighing approximately 1,000 tonnes.",
            "Project management literature identifies optimism bias as the primary driver of infrastructure cost overruns. Bent Flyvbjerg's analysis of 258 transportation projects found that rail projects exceeded budgets by an average of 45%, while road projects exceeded budgets by 20%. The UK Treasury's Green Book guidance now requires quantitative adjustment for optimism bias, adding 66% to the base estimate for standard civil engineering projects and up to 200% for novel or complex projects."
        ],
        "description": "Query asks about 'the project's' budget in a general business context but contexts discuss London's Crossrail infrastructure project and academic research on infrastructure cost overruns",
        "rationale": "The query references 'the project' in what appears to be a business context (original case had internal business projects), but the contexts discuss the London Crossrail megaproject and general research on infrastructure budget overruns - a completely different project scope that cannot answer the implied question about internal business project budgets"
    },
    # t1_qualify_hard_032: query "When is the deadline?"
    # Original has three internal deadlines. Replace with completely different context.
    "t1_qualify_hard_032": {
        "contexts": [
            "The FCC spectrum auction for C-Band frequencies (3.7-3.98 GHz) allocated for 5G deployment concluded on January 15, 2021, raising $81.2 billion in gross proceeds. Winning bidders were required to make full payment within 10 business days of the FCC's public notice of winning bids. The deadline for clearing existing satellite operators from the spectrum was December 5, 2023, with accelerated clearing incentive payments totaling $9.7 billion available to operators who vacated by December 5, 2021.",
            "The GDPR compliance deadline of May 25, 2018, required all organizations processing personal data of EU residents to implement comprehensive data protection measures. Organizations that failed to achieve compliance by the deadline faced potential fines of up to 20 million euros or 4% of global annual turnover, whichever is greater. The Irish Data Protection Commission has since issued the largest GDPR fine of 1.2 billion euros against Meta Platforms in May 2023 for data transfer violations."
        ],
        "description": "Query asks about 'the deadline' in what appears to be a business project context but contexts discuss FCC spectrum auction deadlines and the GDPR compliance deadline",
        "rationale": "The query references 'the deadline' implying a specific business or project context, but the contexts discuss regulatory deadlines (FCC spectrum auctions, GDPR compliance) from entirely different domains that cannot be the deadline being asked about"
    },
    # t1_qualify_hard_033: query "Who is the team lead?"
    # Original has three team leads. Replace with a different team entirely.
    "t1_qualify_hard_033": {
        "contexts": [
            "The 2024 Americas Cup sailing competition in Barcelona featured Team New Zealand defending the Auld Mug against challenger INEOS Britannia. Team New Zealand's helmsman and team lead Peter Burling, at age 33, became the youngest skipper to defend the America's Cup. The Kiwi team's AC75 foiling monohull, Taihoro, incorporated a novel wing design that generated 20% more lift than the previous generation.",
            "INEOS Britannia, skippered by Sir Ben Ainslie, won the Louis Vuitton Cup challenger selection series by defeating Luna Rossa Prada Pirelli 7-4 in the final. Ainslie, a five-time Olympic medalist and the most decorated sailor in Olympic history, assembled a shore team of 130 engineers and designers at the team's Brackley technical base. The team's design director, Martin Fischer, previously served as chief designer for Oracle Team USA."
        ],
        "description": "Query asks about 'the team lead' in what appears to be a business/engineering context but contexts discuss America's Cup sailing team leadership",
        "rationale": "The query implies a business team lead (original case had software engineering team leads), but the contexts discuss competitive sailing team leaders - Peter Burling and Ben Ainslie - who are entirely different people in an entirely different domain"
    },
    # t1_qualify_hard_036: query "What is the system's performance?"
    # Original has IT system metrics. Replace with a different 'system'.
    "t1_qualify_hard_036": {
        "contexts": [
            "The Hennessey Venom F5 performance system achieved a verified top speed of 271.6 mph (437.0 km/h) on a 2.3-mile stretch of the Johnny Bohmer Proving Grounds runway in February 2024. The vehicle's twin-turbocharged 6.6-liter V-8 engine produces 1,817 horsepower on E85 ethanol fuel. The seven-speed single-clutch automated manual transmission delivers power to the rear wheels through a carbon fiber driveshaft rated to 1,600 lb-ft of torque.",
            "The Venom F5's aerodynamic system uses active elements including a deployable rear wing and adjustable front splitter that modify downforce from 140 kg at 200 mph in Attack mode to near-zero in top-speed configuration. The carbon fiber monocoque weighs just 86 kg, contributing to a total dry weight of 1,360 kg. The braking system uses carbon-ceramic discs measuring 390mm front and 380mm rear with six-piston front calipers capable of generating 2.1g of deceleration from 200 mph."
        ],
        "description": "Query asks about 'the system's performance' in what appears to be an IT/software context but contexts discuss the Hennessey Venom F5 hypercar's performance specifications",
        "rationale": "The query implies an IT or software system (original case had server latency, accuracy, and uptime metrics), but the contexts discuss a hypercar's top speed, engine output, and aerodynamic system - an entirely different meaning of 'system' and 'performance'"
    },
    # t1_qualify_hard_037: query "How efficient is the process?"
    # Original has manufacturing/business process metrics. Replace with different 'process'.
    "t1_qualify_hard_037": {
        "contexts": [
            "The Haber-Bosch process for industrial ammonia synthesis operates at temperatures of 400-500 degrees Celsius and pressures of 150-300 atmospheres using an iron-based catalyst promoted with potassium and aluminum oxides. The thermodynamic conversion efficiency per pass is approximately 15%, necessitating recycling of unreacted nitrogen and hydrogen. Global ammonia production via the Haber-Bosch process consumes approximately 1.2% of world energy supply and generates 1.8% of global CO2 emissions.",
            "Alternative green ammonia production processes under development aim to replace the Haber-Bosch process's reliance on natural gas-derived hydrogen. Electrochemical nitrogen reduction using renewable electricity achieves Faradaic efficiencies of 2-15% at laboratory scale, well below the 80-85% energy efficiency of the mature Haber-Bosch process with waste heat recovery. Pilot plants by Yara and CF Industries are testing green hydrogen from electrolysis fed into modified Haber-Bosch reactors, achieving 65-70% overall energy efficiency."
        ],
        "description": "Query asks about 'the process' efficiency in what appears to be a business or manufacturing context but contexts discuss the Haber-Bosch ammonia synthesis process and green ammonia alternatives",
        "rationale": "The query implies a business or manufacturing process (original case had time, cost, energy, and labor efficiency metrics), but the contexts discuss industrial chemical synthesis - the Haber-Bosch process for ammonia production - which is an entirely different 'process' than what is being asked about"
    },
    # t1_qualify_hard_125: query "What is the revenue of Mercury?"
    # Original has three Mercury entities. Replace with only Mercury Insurance.
    "t1_qualify_hard_125": {
        "contexts": [
            "Mercury Insurance Group (NYSE: MCY), headquartered in Los Angeles, California, is primarily a personal automobile insurance carrier operating in 11 US states. Founded in 1961 by George Joseph, the company has been publicly traded since 1990. For fiscal year 2023, Mercury Insurance reported net premiums earned of $4.62 billion, net investment income of $312 million, and total revenue of $5.08 billion. The combined ratio improved to 98.2% from 102.4% in the prior year, returning the company to underwriting profitability.",
            "Mercury Insurance's California operations accounted for 73% of total premiums written, making it the company's most geographically concentrated book of business. The California Department of Insurance approved Mercury's requested 6.9% rate increase effective July 2023 after the company demonstrated actuarial justification based on rising repair costs and increased claims frequency. Mercury holds approximately 4.2% market share in the California personal auto insurance market, ranking it as the sixth largest writer in the state behind State Farm, GEICO, Progressive, Farmers, and USAA."
        ],
        "description": "Query asks about 'the revenue of Mercury' which could refer to multiple companies, but contexts only provide data for Mercury Insurance Group - if the questioner meant Mercury Systems (defense contractor) or Mercury Financial (fintech), the answer is unavailable",
        "rationale": "The contexts exclusively cover Mercury Insurance Group's financial results and California operations. If the query intended Mercury Systems (NASDAQ: MRCY, a defense technology company with $937M revenue) or Mercury Financial (a fintech startup), the provided contexts contain no relevant information"
    },
    # t1_qualify_hard_126: query "What are the side effects of Paxil?"
    # Original has Paxil and Brisdelle. Replace with Paxlovid (similar name, different drug).
    "t1_qualify_hard_126": {
        "contexts": [
            "Paxlovid (nirmatrelvir/ritonavir), manufactured by Pfizer, is an oral antiviral medication authorized for the treatment of mild-to-moderate COVID-19 in adults at high risk for progression to severe disease. The most commonly reported adverse reactions in clinical trials were dysgeusia (altered taste, reported by 5.6% of patients), diarrhea (3.1%), hypertension (1.6%), and myalgia (1.3%). The distinctive metallic or bitter taste associated with Paxlovid typically begins within hours of the first dose and resolves within days of completing the 5-day treatment course.",
            "Post-authorization safety monitoring of Paxlovid identified drug interaction concerns due to the ritonavir component, which is a potent inhibitor of cytochrome P450 3A4. Contraindicated co-medications include certain statins (lovastatin, simvastatin), anticonvulsants (carbamazepine, phenobarbital), immunosuppressants (tacrolimus at standard doses), and sedative-hypnotics (triazolam, oral midazolam). The FDA revised the Paxlovid fact sheet in March 2024 to include additional warnings about 'Paxlovid rebound' - the recurrence of COVID-19 symptoms 2-8 days after completing treatment, observed in approximately 10-15% of patients."
        ],
        "description": "Query asks about side effects of Paxil (paroxetine, an SSRI antidepressant) but contexts describe side effects and drug interactions of Paxlovid (nirmatrelvir/ritonavir, a COVID-19 antiviral)",
        "rationale": "Despite the similar names, Paxil and Paxlovid are entirely different medications with different active ingredients, mechanisms, indications, and side effect profiles. The dysgeusia, drug interactions, and COVID rebound described for Paxlovid cannot be attributed to Paxil (paroxetine)"
    },
}

# ---------------------------------------------------------------------------
# Group D: scope_condition -> converted_wrong_scope
# Replace with wrong-scope content (different size, geography, segment)
# ---------------------------------------------------------------------------
GROUP_D_IDS = [
    "t1_qualify_hard_110", "t1_qualify_hard_111", "t1_qualify_hard_112",
    "t1_qualify_hard_113", "t1_qualify_hard_114",
]

GROUP_D_REPLACEMENTS = {
    # t1_qualify_hard_110: query about adopting Kubernetes for container orchestration
    # Original discusses enterprise vs small teams. Replace with hobby/home lab only.
    "t1_qualify_hard_110": {
        "contexts": [
            "For home lab enthusiasts and hobbyist developers, a single-node Kubernetes cluster using minikube or k3s provides an excellent learning environment. Minikube runs a single-node cluster inside a virtual machine on a personal laptop, requiring a minimum of 2 CPUs, 2 GB of RAM, and 20 GB of disk space. K3s, developed by Rancher Labs, is a lightweight Kubernetes distribution that runs on a Raspberry Pi 4 with 4 GB RAM. Both tools enable developers to experiment with pod deployments, services, and ingress controllers without cloud provider costs.",
            "The popular YouTube channel 'Home Lab Heroes' published a step-by-step guide for running a personal Kubernetes cluster on three Raspberry Pi 5 boards costing a total of $240. The setup uses k3s with Longhorn for persistent storage and MetalLB for bare-metal load balancing. Average power consumption is 18 watts for the entire cluster. The guide notes that this configuration is suitable for personal projects, learning, and hosting small applications like Pi-hole DNS and a personal wiki, but should not be used for business-critical workloads due to limited redundancy and the absence of enterprise support.",
            "Docker Compose remains the recommended orchestration tool for personal projects and small-scale development environments. A 2024 Stack Overflow survey found that 78% of individual developers and hobbyists prefer Docker Compose over Kubernetes for personal projects, citing setup simplicity (average 5 minutes versus 2 hours), minimal resource overhead (100 MB versus 2 GB RAM minimum), and a learning curve measured in hours versus weeks. The survey noted that developers running fewer than 10 containers reported no benefit from Kubernetes orchestration."
        ],
        "description": "Query asks whether to adopt Kubernetes for container orchestration (implying a business/production decision) but contexts only discuss hobbyist, home lab, and personal learning use cases on Raspberry Pi hardware",
        "rationale": "The contexts exclusively cover home lab setups, personal learning environments, and hobby-scale Kubernetes on Raspberry Pi boards. For an organization evaluating Kubernetes for production container orchestration, information about home lab configurations, personal projects, and Docker Compose for individual developers provides no relevant guidance on enterprise scalability, team requirements, or production reliability"
    },
    # t1_qualify_hard_111: query about LASIK safety and effectiveness
    # Original discusses general population vs contraindicated patients. Replace with veterinary LASIK.
    "t1_qualify_hard_111": {
        "contexts": [
            "Veterinary ophthalmology has explored laser-assisted corneal procedures for companion animals, though the practice remains uncommon compared to human LASIK. A 2024 study in Veterinary Ophthalmology evaluated photorefractive keratectomy (PRK, not LASIK) in 34 horses with superficial corneal scarring. The procedure used an excimer laser at 193 nm wavelength to remove scar tissue from the corneal stroma. Outcomes were favorable in 82% of equine subjects, with improved corneal transparency and no post-operative infections. The study noted that the equine cornea's greater thickness (approximately 800-1000 microns versus 540 microns in humans) provided a wider safety margin for ablation.",
            "Canine refractive surgery research at the University of California Davis veterinary hospital has focused on intraocular lens implants rather than corneal reshaping. Dogs naturally have a refractive error range of +1 to +3 diopters (mild farsightedness) and lack the visual acuity demands that motivate human LASIK. The primary indication for canine lens surgery is cataract removal, performed on approximately 100,000 dogs annually in the United States. Post-cataract IOL implantation costs $3,500-$5,000 per eye. Dr. Christine Kim, the lead researcher, noted that LASIK-style procedures are not indicated for dogs because their visual ecology does not require the corrective precision that human patients seek."
        ],
        "description": "Query asks whether LASIK eye surgery is safe and effective for human patients but contexts discuss laser eye procedures in horses and lens implant research in dogs",
        "rationale": "The contexts cover veterinary ophthalmology - equine PRK procedures and canine lens surgery - not human LASIK. Animal corneal anatomy, visual requirements, and surgical outcomes differ fundamentally from human LASIK, making veterinary data inapplicable to the human safety and effectiveness question"
    },
    # t1_qualify_hard_112: query about LFP as best battery for electric vehicles
    # Original discusses EVs broadly. Replace with grid-scale stationary storage only.
    "t1_qualify_hard_112": {
        "contexts": [
            "Grid-scale stationary energy storage installations have increasingly adopted lithium iron phosphate chemistry due to its exceptional cycle life and safety profile in large-format installations. The 3,287 MWh Moss Landing Energy Storage Facility in Monterey County, California, operated by Vistra Energy, uses LFP cells from CATL and has completed over 1,200 full charge-discharge cycles since commissioning in 2021 with less than 2% capacity degradation. The facility occupies a 33-acre site and performs energy arbitrage, frequency regulation, and capacity services for the CAISO grid.",
            "The National Renewable Energy Laboratory's 2024 benchmark report on utility-scale battery storage found that LFP systems achieved an installed cost of $210 per kWh for 4-hour duration systems, approximately 20% less than NMC-based alternatives at the same scale. Round-trip efficiency for LFP grid storage averaged 87%, and the fire risk profile was assessed as 'negligible' in ground-mounted containerized configurations. NREL projected that LFP would capture 95% of the US grid storage market by 2026, up from 78% in 2024.",
            "Flow batteries represent the primary competitor to LFP for long-duration grid storage applications exceeding 8 hours. Vanadium redox flow batteries offer effectively unlimited cycle life and the ability to independently scale power and energy capacity. However, the levelized cost of storage for vanadium flow batteries remains 40-60% higher than LFP for 4-hour applications, limiting their competitiveness to niche long-duration applications where LFP's energy density advantage is irrelevant."
        ],
        "description": "Query asks whether LFP is the best battery chemistry for electric vehicles but contexts exclusively discuss grid-scale stationary energy storage applications",
        "rationale": "The contexts cover utility-scale battery installations, grid storage costs, and stationary storage comparisons. Electric vehicle applications have fundamentally different requirements - energy density, weight, temperature performance, and fast charging - that are not addressed by grid storage data. What makes LFP optimal for a 33-acre stationary installation does not determine its suitability for a passenger vehicle"
    },
    # t1_qualify_hard_113: query about law firms adopting AI contract review
    # Original discusses large vs small firms. Replace with consumer/individual use context.
    "t1_qualify_hard_113": {
        "contexts": [
            "Consumer-facing AI legal tools experienced rapid growth in 2024, with DoNotPay, LawDroid, and Rocket Lawyer's AI assistant collectively serving 14 million individual users for personal legal tasks. The most popular consumer use cases were generating cease-and-desist letters (23%), reviewing residential lease agreements (19%), contesting parking tickets (17%), and drafting simple wills (14%). Consumer satisfaction surveys showed 71% of users rated the tools as helpful for straightforward personal legal matters.",
            "A Stanford Legal Design Lab study of AI legal tools for self-represented litigants in small claims court found that individuals using AI assistance filed motions with 34% fewer procedural errors and achieved favorable outcomes in 48% of cases compared to 31% for unassisted self-represented parties. The study covered 2,400 small claims cases with amounts in controversy under $10,000 in California, Michigan, and New York. Pro se litigants reported spending an average of $29 on AI tool subscriptions versus $1,200-$3,000 for attorney consultation.",
            "The American Bar Association's 2024 Legal Technology Survey found that 82% of solo practitioners and 67% of small firms (2-9 attorneys) had not adopted any AI-powered document review tools, citing cost ($200-$500 per month per user), the complexity of integration with existing practice management software, and concerns about professional responsibility implications. The ABA's Standing Committee on Ethics noted that most consumer AI legal tools include disclaimers that they do not provide legal advice and are not substitutes for attorney representation."
        ],
        "description": "Query asks whether law firms should adopt AI-powered contract review tools (implying enterprise/professional adoption) but contexts discuss consumer-facing AI legal tools for individuals handling personal legal matters",
        "rationale": "The contexts cover AI legal tools for individual consumers - parking tickets, small claims court, personal lease review - not enterprise contract review platforms for law firms. The accuracy requirements, liability considerations, deal complexity, and ROI analysis for professional law firm contract review are entirely different from consumer self-help legal tools"
    },
    # t1_qualify_hard_114: query about desalination viability for water scarcity
    # Original discusses coastal wealthy vs inland poor. Replace with space/Mars context.
    "t1_qualify_hard_114": {
        "contexts": [
            "NASA's Mars Water Extraction Technology program has developed a sublimation-based water harvesting system for future crewed Mars missions. The Subsurface Ice Mapping Analysis for Resources (SIMAR) instrument aboard the Mars Reconnaissance Orbiter identified accessible water ice deposits within 1-2 meters of the surface at latitudes between 35 and 60 degrees in both hemispheres. The proposed extraction process uses microwave-frequency heating rods inserted into the regolith to sublimate buried ice at temperatures of minus 60 degrees Celsius and 600 Pascal atmospheric pressure, recovering approximately 0.8 liters per kilowatt-hour of energy input.",
            "The International Space Station's Water Recovery System processes an average of 3,600 liters of wastewater per year through a multi-step process: the Urine Processor Assembly uses vapor compression distillation to recover 85% of water from crew urine, and the Water Processor Assembly further purifies this along with humidity condensate and hygiene water through filtration, ion exchange, and catalytic oxidation. The system achieves 98% total water recovery, reducing the annual water resupply requirement from 10,000 liters to approximately 200 liters. System mass is 1,800 kg with an operational power draw of 1.5 kW.",
            "The Lunar Gateway habitat, planned for deployment in 2028, will incorporate a next-generation water recycling system capable of supporting 4 crew members for 90-day missions. The closed-loop system combines forward osmosis membranes, electrolytic disinfection, and mineralization to produce potable water meeting NASA's Spacecraft Water Exposure Guideline standards for 200 chemical contaminants. Total system mass target is 400 kg, a 78% reduction from ISS hardware."
        ],
        "description": "Query asks about desalination as a solution to terrestrial water scarcity but contexts discuss water extraction on Mars, ISS water recycling, and Lunar Gateway water systems",
        "rationale": "The contexts cover extraterrestrial water recovery - Mars ice sublimation, ISS urine processing, and Lunar Gateway recycling. These space-based systems operate under fundamentally different constraints (zero gravity, extreme cost, crew of 4-6) than terrestrial desalination addressing municipal water supply for millions of people at commercial scale"
    },
}

# ---------------------------------------------------------------------------
# Group E: different_framing (from trustworthy_direct) -> converted_insufficient
# Replace with related-but-insufficient content
# ---------------------------------------------------------------------------
GROUP_E_EXCLUDE_IDS = {220, 221, 222, 223, 224, 230, 231, 232, 233, 234}

GROUP_E_REPLACEMENTS = {
    # t1_confident_hard_300: query "How did Quantum Computing Corp perform in Q3 2024?"
    "t1_confident_hard_300": {
        "contexts": [
            "The quantum computing industry experienced significant milestones in 2024. IBM unveiled its 1,121-qubit Condor processor and announced plans for a 100,000-qubit system by 2033. Google DeepMind demonstrated quantum error correction on its Sycamore processor achieving logical error rates below physical error rates for the first time. IonQ reported its trapped-ion systems achieved 99.7% two-qubit gate fidelity. Venture capital investment in quantum computing companies totaled $2.1 billion across 87 deals in 2024.",
            "Quantum computing stocks experienced high volatility in 2024, with the Defiance Quantum ETF (QTUM) returning 24% for the year after a mid-year drawdown of 31%. Analysts noted that most publicly traded quantum computing companies remain pre-revenue or early-revenue, with commercial quantum advantage not expected before 2028-2030 for optimization and simulation workloads. The sector's total market capitalization reached $18 billion by year-end."
        ],
        "description": "Query asks how Quantum Computing Corp specifically performed in Q3 2024 but contexts discuss the broader quantum computing industry and quantum computing stocks generally",
        "rationale": "The contexts cover industry-wide quantum computing milestones and sector-level stock performance but contain no specific financial results, earnings data, or operational metrics for Quantum Computing Corp's Q3 2024 quarter"
    },
    # t1_confident_hard_301: query "What is the crime rate trend in the city?"
    "t1_confident_hard_301": {
        "contexts": [
            "The Bureau of Justice Statistics' National Crime Victimization Survey for 2024 estimated that 6.6 million violent victimizations occurred nationwide, a rate of 22.5 per 1,000 persons aged 12 and older. Property crime victimizations totaled 11.7 million. The survey methodology captures both reported and unreported crime, providing a more comprehensive measure than police statistics alone. The survey has been conducted annually since 1973.",
            "Criminology research identifies several macroeconomic factors correlated with crime rate trends. A meta-analysis in the Journal of Quantitative Criminology found that a 1 percentage point increase in unemployment is associated with a 2-4% increase in property crime but has no statistically significant effect on violent crime. Temperature is positively correlated with assault rates, with each degree Celsius increase in average summer temperature associated with a 1.5-2% increase in assaults. Lead exposure in childhood, measured by blood lead levels, has been linked to violent crime rates with a 20-year lag."
        ],
        "description": "Query asks about crime rate trends in a specific city but contexts discuss national crime survey data and general criminological research on macro-level crime determinants",
        "rationale": "The contexts provide national aggregate crime statistics and academic research on macro factors affecting crime rates, but contain no city-specific crime data, local police statistics, or information about any particular city's crime trends"
    },
    # t1_confident_hard_302: query "Is the new trade agreement beneficial for the country?"
    "t1_confident_hard_302": {
        "contexts": [
            "International trade theory provides several frameworks for evaluating trade agreements. The Ricardian model demonstrates that countries benefit from trade through comparative advantage, even when one country has absolute advantage in all goods. The Heckscher-Ohlin model predicts that trade benefits factor-abundant countries by increasing demand for their abundant factors. The Stolper-Samuelson theorem shows that trade liberalization benefits owners of the abundant factor while harming owners of the scarce factor.",
            "The World Trade Organization's 2024 World Trade Report examined the economic effects of 34 regional trade agreements implemented between 2000 and 2020. The analysis found that member countries experienced average trade creation of 18-25% with partner countries within 5 years of implementation. However, trade diversion effects reduced trade with non-member countries by 5-8% on average. The report cautioned that aggregate GDP effects are modest (typically 0.5-2% over a decade) and that distributional impacts between sectors, regions, and income groups are often more significant than aggregate effects."
        ],
        "description": "Query asks whether a specific new trade agreement is beneficial for a specific country but contexts discuss general trade theory models and a WTO meta-analysis of 34 different trade agreements",
        "rationale": "The contexts cover theoretical trade frameworks and aggregate statistical patterns across dozens of agreements, but contain no information about any specific trade agreement, its provisions, or its projected effects on any particular country"
    },
    # t1_confident_hard_303: query "How is the hospital performing on patient outcomes?"
    "t1_confident_hard_303": {
        "contexts": [
            "The Centers for Medicare and Medicaid Services Hospital Compare program publicly reports quality metrics for over 4,000 US hospitals. Metrics include 30-day mortality rates for heart attack, heart failure, and pneumonia; 30-day readmission rates; patient safety indicators; and patient experience scores from the HCAHPS survey. CMS assigns each hospital an overall star rating from 1 to 5 based on a weighted composite of these measures. In 2024, 455 hospitals received 5 stars, 1,074 received 4 stars, and 889 received 1 or 2 stars.",
            "Hospital quality measurement methodology has evolved significantly over the past two decades. Risk adjustment models account for patient age, comorbidities, and socioeconomic factors to enable fair comparison between hospitals serving different populations. Critics argue that current risk adjustment models inadequately account for social determinants of health, potentially penalizing safety-net hospitals. The National Quality Forum endorses 85 hospital performance measures, while The Leapfrog Group independently grades hospitals on patient safety using its own methodology."
        ],
        "description": "Query asks about a specific hospital's patient outcome performance but contexts discuss the CMS Hospital Compare program generally and quality measurement methodology",
        "rationale": "The contexts describe the national hospital quality reporting infrastructure and measurement methodology but contain no data about any specific hospital's mortality rates, readmission rates, infection rates, or patient experience scores"
    },
    # t1_confident_hard_304: query "How did the new education funding formula affect schools?"
    "t1_confident_hard_304": {
        "contexts": [
            "Education finance research has identified several approaches to equitable school funding. Foundation formulas guarantee a minimum per-pupil expenditure with state funds filling the gap between local revenue and the foundation amount. Weighted student funding allocates additional resources for students with higher educational needs, including English learners, students with disabilities, and economically disadvantaged students. Centralized funding models eliminate local property tax funding entirely, as in Hawaii's single state-district system.",
            "The National Education Association's 2024 report on school funding adequacy found that 28 states had been involved in school finance litigation since 2000, with courts ruling in favor of plaintiffs (finding inadequate or inequitable funding) in 19 cases. Average per-pupil expenditure nationally was $14,347, ranging from $8,280 in Utah to $28,356 in New York. The report noted that the correlation between per-pupil spending and student outcomes, while positive, is moderated by how funds are allocated, with targeted interventions showing stronger effects than across-the-board spending increases."
        ],
        "description": "Query asks about the effects of a specific new education funding formula on schools but contexts discuss general education finance theory and national spending statistics",
        "rationale": "The contexts cover general approaches to education finance and national spending averages but contain no information about any specific state's new funding formula, its implementation, or its measurable effects on schools"
    },
    # t1_confident_hard_305: query "What was the outcome of the clinical trial for Neurexal?"
    "t1_confident_hard_305": {
        "contexts": [
            "The Alzheimer's disease drug development pipeline has experienced historically high failure rates, with an estimated 99.6% of clinical trials between 2002 and 2022 failing to demonstrate efficacy. The amyloid hypothesis, which posits that accumulation of beta-amyloid plaques is the primary driver of Alzheimer's pathology, has dominated drug development strategy despite decades of clinical failures. Recent approvals of aducanumab (2021, subsequently withdrawn) and lecanemab (2023) have renewed interest in anti-amyloid approaches despite modest clinical benefit.",
            "Clinical trial design for Alzheimer's disease has evolved to address the challenges of measuring treatment effects in a slowly progressive neurodegenerative condition. The Clinical Dementia Rating-Sum of Boxes (CDR-SB) is the most commonly used primary endpoint in Phase III trials, measuring cognition and function on an 18-point scale. The Alzheimer's Disease Assessment Scale-Cognitive Subscale (ADAS-Cog) provides a 70-point cognitive measure. Both instruments have been criticized for floor and ceiling effects. The minimum clinically important difference on CDR-SB is generally considered to be 0.5-1.0 points, though this threshold remains debated."
        ],
        "description": "Query asks about the outcome of the Neurexal clinical trial specifically but contexts discuss Alzheimer's drug development failure rates generally and clinical trial endpoint methodology",
        "rationale": "The contexts cover the broader Alzheimer's drug development landscape and clinical trial measurement approaches, but contain no data about Neurexal specifically - no trial results, efficacy endpoints, safety data, or regulatory status"
    },
    # t1_confident_hard_306: query "What is the state of the housing market?"
    "t1_confident_hard_306": {
        "contexts": [
            "The Federal Reserve's monetary policy decisions significantly influence housing market conditions through their effect on mortgage rates. The federal funds rate, set by the Federal Open Market Committee, indirectly determines mortgage rates through its influence on Treasury yields and secondary mortgage market pricing. A 2024 Brookings Institution study estimated that each 100 basis point increase in the federal funds rate reduces existing home sales by approximately 8-12% within 6-9 months and dampens home price appreciation by 2-4 percentage points over the following year.",
            "Housing market analysis employs several key indicators. The Case-Shiller Home Price Index tracks repeat-sale residential property values in 20 metropolitan areas. The National Association of Realtors reports existing home sales volume and median prices monthly. The Census Bureau tracks new residential construction permits and housing starts. The Mortgage Bankers Association publishes weekly mortgage application data including purchase and refinance volumes. Months of supply, calculated by dividing active listings by the monthly sales pace, indicates market balance: under 4 months favors sellers, 4-6 months is balanced, and over 6 months favors buyers."
        ],
        "description": "Query asks about the current state of the housing market but contexts discuss the Fed's influence on housing and definitions of housing market indicators",
        "rationale": "The contexts explain how monetary policy affects housing and define the indicators used to measure housing markets, but provide no actual current data - no median prices, sales volumes, inventory levels, or mortgage rate figures to describe the market's current state"
    },
    # t1_confident_hard_307: query "Was the corporate restructuring successful?"
    "t1_confident_hard_307": {
        "contexts": [
            "Corporate restructuring strategies broadly fall into financial restructuring (debt renegotiation, equity issuance, asset sales) and operational restructuring (workforce reductions, plant closures, business unit divestitures, process reengineering). A McKinsey study of 1,200 restructuring programs found that 58% achieved their stated cost reduction targets, but only 26% sustained those savings beyond three years. The most common cause of restructuring failure was 'initiative fatigue' where organizational capacity for change was exhausted before transformation was complete.",
            "Key performance indicators for evaluating restructuring success include operating margin improvement, revenue trajectory, employee engagement scores, customer retention rates, and total shareholder return relative to industry peers. The Boston Consulting Group's restructuring framework emphasizes that purely financial metrics are insufficient, as cost cuts that impair revenue growth or talent retention may produce short-term margin improvement while destroying long-term enterprise value. The 'restructuring paradox' refers to the empirical finding that company stock prices typically rise on restructuring announcements but underperform peers over a 3-5 year horizon in 60% of cases."
        ],
        "description": "Query asks whether a specific corporate restructuring was successful but contexts discuss generic restructuring strategy frameworks and evaluation methodologies",
        "rationale": "The contexts cover theoretical restructuring approaches and general KPIs for measuring success, but contain no information about any specific company's restructuring - no cost savings figures, headcount changes, revenue impacts, or operational outcomes"
    },
    # t1_confident_hard_308: query "How much water does the state's agriculture sector use?"
    "t1_confident_hard_308": {
        "contexts": [
            "The United Nations Food and Agriculture Organization estimates that agriculture accounts for 70% of global freshwater withdrawals, with irrigation being the dominant use. The Aqueduct Water Risk Atlas developed by the World Resources Institute identifies 17 countries experiencing extremely high baseline water stress, with agriculture competing increasingly with urban, industrial, and environmental water demands. Global irrigated area has grown from 139 million hectares in 1961 to 310 million hectares in 2024.",
            "Agricultural water use efficiency varies enormously by irrigation method. Flood irrigation, still practiced on approximately 60% of irrigated land globally, achieves application efficiency of 40-50%. Sprinkler systems improve efficiency to 70-80%. Drip irrigation systems achieve 90-95% application efficiency by delivering water directly to the root zone. Israel pioneered drip irrigation technology through Netafim, founded in 1965, and currently irrigates 75% of its agricultural land using drip systems."
        ],
        "description": "Query asks about water usage by a specific state's agriculture sector but contexts discuss global agricultural water statistics and irrigation efficiency methods",
        "rationale": "The contexts provide global aggregate agricultural water use data and irrigation technology comparisons, but contain no state-specific water use figures, regional agricultural data, or information about any particular state's farming water consumption"
    },
    # t1_confident_hard_309: query "Is the new immigration policy working?"
    "t1_confident_hard_309": {
        "contexts": [
            "Immigration policy analysis frameworks distinguish between stock-based measures (total foreign-born population, unauthorized population estimates) and flow-based measures (border encounters, visa issuances, asylum adjudications, deportations). The Migration Policy Institute notes that evaluating whether an immigration policy is 'working' requires specifying the policy objective, as immigration policies simultaneously affect border security, economic productivity, humanitarian protection, family reunification, and demographic trends, often with tradeoffs between these goals.",
            "Comparative immigration policy research published in the Journal of Ethnic and Migration Studies examined enforcement-focused immigration reforms in 12 OECD countries between 2010 and 2023. The study found that border enforcement investments reduced unauthorized border crossings in the short term (first 12-18 months) by an average of 25-35%, but long-term effects were attenuated by shifts to alternative entry routes and increased visa overstays. Interior enforcement measures (workplace audits, mandatory E-Verify) showed more sustained effects on unauthorized employment but had negligible impact on total unauthorized population estimates."
        ],
        "description": "Query asks whether a specific new immigration policy is working but contexts discuss general analytical frameworks for immigration evaluation and a comparative study of 12 countries' enforcement reforms",
        "rationale": "The contexts provide theoretical evaluation frameworks and cross-national research findings on immigration enforcement generally, but contain no information about any specific new policy, its provisions, or its measurable outcomes"
    },
}


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def find_case(cases: list, case_id: str) -> dict | None:
    for c in cases:
        if c["id"] == case_id:
            return c
    return None


def make_abstain_case(
    original: dict,
    new_id: str,
    replacement: dict,
    subcategory: str,
    conversion_method: str,
) -> dict:
    """Create a new abstention case from an original case and replacement data."""
    return {
        "id": new_id,
        "category": "abstention",
        "subcategory": subcategory,
        "difficulty": "hard",
        "query": original["query"],
        "contexts": replacement["contexts"],
        "expected_mode": "abstain",
        "description": replacement["description"],
        "rationale": replacement["rationale"],
        "metadata": {
            "converted_from": original["id"],
            "conversion_method": conversion_method,
        },
    }


def main():
    print("=" * 72)
    print("Convert Trustworthy Cases to Abstention Cases")
    print("=" * 72)

    # Load files
    hedged_data = load_json(HEDGED_FILE)
    direct_data = load_json(DIRECT_FILE)
    abstention_data = load_json(ABSTENTION_FILE)

    hedged_cases = hedged_data["cases"]
    direct_cases = direct_data["cases"]
    abstention_cases = abstention_data["cases"]

    new_cases = []
    removed_hedged_ids = []
    removed_direct_ids = []
    next_id = NEXT_ABSTAIN_ID
    skipped = []

    # --- Group A: different_aspects -> converted_off_domain ---
    print("\nGroup A: different_aspects -> converted_off_domain (15 cases)")
    for orig_id in GROUP_A_IDS:
        case = find_case(hedged_cases, orig_id)
        if case is None:
            skipped.append(orig_id)
            print(f"  SKIP {orig_id} (not found)")
            continue
        replacement = GROUP_A_REPLACEMENTS[orig_id]
        new_id = f"t1_abstain_hard_{next_id}"
        new_case = make_abstain_case(
            case, new_id, replacement, "converted_off_domain", "off_domain_replacement"
        )
        new_cases.append(new_case)
        removed_hedged_ids.append(orig_id)
        print(f"  {orig_id} -> {new_id}")
        next_id += 1

    # --- Group B: partial_answer -> converted_insufficient ---
    print("\nGroup B: partial_answer -> converted_insufficient (10 cases)")
    for orig_id in GROUP_B_IDS:
        case = find_case(hedged_cases, orig_id)
        if case is None:
            skipped.append(orig_id)
            print(f"  SKIP {orig_id} (not found)")
            continue
        replacement = GROUP_B_REPLACEMENTS[orig_id]
        new_id = f"t1_abstain_hard_{next_id}"
        new_case = make_abstain_case(
            case, new_id, replacement, "converted_insufficient", "insufficient_replacement"
        )
        new_cases.append(new_case)
        removed_hedged_ids.append(orig_id)
        print(f"  {orig_id} -> {new_id}")
        next_id += 1

    # --- Group C: entity_ambiguity -> converted_wrong_entity ---
    print("\nGroup C: entity_ambiguity -> converted_wrong_entity (10 cases)")
    for orig_id in GROUP_C_IDS:
        case = find_case(hedged_cases, orig_id)
        if case is None:
            skipped.append(orig_id)
            print(f"  SKIP {orig_id} (not found)")
            continue
        replacement = GROUP_C_REPLACEMENTS[orig_id]
        new_id = f"t1_abstain_hard_{next_id}"
        new_case = make_abstain_case(
            case, new_id, replacement, "converted_wrong_entity", "wrong_entity_replacement"
        )
        new_cases.append(new_case)
        removed_hedged_ids.append(orig_id)
        print(f"  {orig_id} -> {new_id}")
        next_id += 1

    # --- Group D: scope_condition -> converted_wrong_scope ---
    print("\nGroup D: scope_condition -> converted_wrong_scope (5 cases)")
    for orig_id in GROUP_D_IDS:
        case = find_case(hedged_cases, orig_id)
        if case is None:
            skipped.append(orig_id)
            print(f"  SKIP {orig_id} (not found)")
            continue
        replacement = GROUP_D_REPLACEMENTS[orig_id]
        new_id = f"t1_abstain_hard_{next_id}"
        new_case = make_abstain_case(
            case, new_id, replacement, "converted_wrong_scope", "wrong_scope_replacement"
        )
        new_cases.append(new_case)
        removed_hedged_ids.append(orig_id)
        print(f"  {orig_id} -> {new_id}")
        next_id += 1

    # --- Group E: different_framing -> converted_insufficient ---
    print("\nGroup E: different_framing -> converted_insufficient (10 cases)")
    # Find 10 different_framing cases not in the exclude set
    df_cases = [
        c for c in direct_cases if c.get("subcategory") == "different_framing"
    ]
    candidates = []
    for c in df_cases:
        num = int(c["id"].split("_")[-1])
        if num not in GROUP_E_EXCLUDE_IDS:
            candidates.append(c)

    target_e_ids = [c["id"] for c in candidates[:10]]
    for orig_id in target_e_ids:
        case = find_case(direct_cases, orig_id)
        if case is None:
            skipped.append(orig_id)
            print(f"  SKIP {orig_id} (not found)")
            continue
        replacement = GROUP_E_REPLACEMENTS.get(orig_id)
        if replacement is None:
            skipped.append(orig_id)
            print(f"  SKIP {orig_id} (no replacement defined)")
            continue
        new_id = f"t1_abstain_hard_{next_id}"
        new_case = make_abstain_case(
            case, new_id, replacement, "converted_insufficient", "insufficient_replacement"
        )
        new_cases.append(new_case)
        removed_direct_ids.append(orig_id)
        print(f"  {orig_id} -> {new_id}")
        next_id += 1

    # --- Remove originals from source files ---
    print(f"\nRemoving {len(removed_hedged_ids)} cases from trustworthy_hedged.json...")
    hedged_before = len(hedged_cases)
    hedged_data["cases"] = [
        c for c in hedged_cases if c["id"] not in removed_hedged_ids
    ]
    hedged_after = len(hedged_data["cases"])
    print(f"  {hedged_before} -> {hedged_after} cases")

    print(f"Removing {len(removed_direct_ids)} cases from trustworthy_direct.json...")
    direct_before = len(direct_cases)
    direct_data["cases"] = [
        c for c in direct_cases if c["id"] not in removed_direct_ids
    ]
    direct_after = len(direct_data["cases"])
    print(f"  {direct_before} -> {direct_after} cases")

    # --- Append to abstention.json ---
    print(f"\nAppending {len(new_cases)} converted cases to abstention.json...")
    abstention_before = len(abstention_cases)
    abstention_data["cases"].extend(new_cases)
    abstention_after = len(abstention_data["cases"])
    print(f"  {abstention_before} -> {abstention_after} cases")

    # --- Write files ---
    print("\nWriting files...")
    save_json(HEDGED_FILE, hedged_data)
    print(f"  Wrote {HEDGED_FILE}")
    save_json(DIRECT_FILE, direct_data)
    print(f"  Wrote {DIRECT_FILE}")
    save_json(ABSTENTION_FILE, abstention_data)
    print(f"  Wrote {ABSTENTION_FILE}")

    # --- Summary ---
    print("\n" + "=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print(f"Total cases converted: {len(new_cases)}")
    print(f"  Group A (off_domain):     {sum(1 for c in new_cases if c['subcategory'] == 'converted_off_domain')}")
    print(f"  Group B (insufficient):   {sum(1 for c in new_cases if c['metadata']['conversion_method'] == 'insufficient_replacement' and c['metadata']['converted_from'].startswith('t1_qualify'))}")
    print(f"  Group C (wrong_entity):   {sum(1 for c in new_cases if c['subcategory'] == 'converted_wrong_entity')}")
    print(f"  Group D (wrong_scope):    {sum(1 for c in new_cases if c['subcategory'] == 'converted_wrong_scope')}")
    print(f"  Group E (insufficient):   {sum(1 for c in new_cases if c['metadata']['conversion_method'] == 'insufficient_replacement' and c['metadata']['converted_from'].startswith('t1_confident'))}")
    print(f"\nCases removed from trustworthy_hedged.json: {len(removed_hedged_ids)}")
    print(f"Cases removed from trustworthy_direct.json: {len(removed_direct_ids)}")
    print(f"Cases added to abstention.json: {len(new_cases)}")
    print(f"Skipped (not found or no replacement): {len(skipped)}")
    if skipped:
        for s in skipped:
            print(f"  - {s}")
    print(f"\nNew abstention IDs: t1_abstain_hard_{NEXT_ABSTAIN_ID} through t1_abstain_hard_{next_id - 1}")
    print("=" * 72)


if __name__ == "__main__":
    main()
