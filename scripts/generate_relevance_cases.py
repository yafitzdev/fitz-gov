#!/usr/bin/env python3
"""Generate 168 new relevance cases for Phase 3 expansion.

Uses domain-specific content templates combined with subcategory patterns
to generate diverse, realistic test cases with proper required_elements.
"""

import json
from pathlib import Path

# ── Domain content pools ──────────────────────────────────────────────────

DOMAIN_CONTENT = {
    "technology": [
        {"topic": "cloud platform migration", "detail": "supports auto-scaling, load balancing, and containerization", "tangent": "cloud computing pricing models and cost optimization strategies"},
        {"topic": "API rate limiting", "detail": "throttles requests at 1000/min per API key with exponential backoff", "tangent": "API design best practices and RESTful architecture patterns"},
        {"topic": "database sharding", "detail": "horizontal partitioning across 8 nodes using consistent hashing", "tangent": "database indexing strategies and query optimization techniques"},
        {"topic": "CI/CD pipeline", "detail": "runs 450 unit tests and 120 integration tests per build", "tangent": "software testing methodologies and code coverage metrics"},
        {"topic": "microservices architecture", "detail": "12 services communicating via gRPC with circuit breakers", "tangent": "monolithic vs microservices architectural comparisons"},
        {"topic": "cybersecurity framework", "detail": "zero-trust model with multi-factor authentication", "tangent": "cybersecurity threat landscape and emerging attack vectors"},
        {"topic": "machine learning model", "detail": "transformer with 175M parameters fine-tuned on domain data", "tangent": "the history of neural network architectures and breakthroughs"},
        {"topic": "DevOps toolchain", "detail": "Terraform for IaC, Prometheus for monitoring, Grafana for dashboards", "tangent": "DevOps culture and organizational transformation"},
        {"topic": "frontend performance", "detail": "First Contentful Paint of 1.2s with code splitting and lazy loading", "tangent": "web accessibility standards and WCAG compliance"},
        {"topic": "data pipeline", "detail": "Apache Kafka ingests 2M events/sec with exactly-once semantics", "tangent": "big data ecosystem comparison and open-source alternatives"},
    ],
    "finance": [
        {"topic": "quarterly earnings report", "detail": "revenue of $3.8B with EBITDA margin of 28%", "tangent": "revenue recognition standards and accounting methodology"},
        {"topic": "portfolio allocation", "detail": "60% equities, 25% bonds, 10% alternatives, 5% cash", "tangent": "modern portfolio theory and efficient frontier calculations"},
        {"topic": "credit risk model", "detail": "probability of default model using logistic regression on 45 features", "tangent": "regulatory capital requirements under Basel III framework"},
        {"topic": "startup valuation", "detail": "Series C at $2.1B with 15x revenue multiple", "tangent": "venture capital fund structures and LP/GP dynamics"},
        {"topic": "mortgage underwriting", "detail": "DTI ratio maximum of 43% with 3.5% minimum down payment", "tangent": "housing market trends and inventory levels by region"},
        {"topic": "derivatives pricing", "detail": "Black-Scholes model with implied volatility of 22%", "tangent": "history of financial crises and market regulation evolution"},
        {"topic": "tax optimization", "detail": "Roth conversion ladder strategy for early retirement", "tangent": "federal budget deficits and national debt implications"},
        {"topic": "ESG investing", "detail": "scoring methodology weights governance 40%, environmental 35%, social 25%", "tangent": "corporate social responsibility programs and community impact"},
        {"topic": "forex trading", "detail": "EUR/USD pair with 12-pip average daily range", "tangent": "geopolitical factors affecting currency markets"},
        {"topic": "insurance actuarial", "detail": "combined ratio of 95.3% with loss ratio of 62.1%", "tangent": "insurance industry market structure and competitive dynamics"},
    ],
    "medicine": [
        {"topic": "clinical trial Phase III", "detail": "primary endpoint: progression-free survival of 14.2 months", "tangent": "history of clinical trial methodology and ethical standards"},
        {"topic": "drug interaction study", "detail": "CYP3A4 inhibitor increases plasma concentration 3.2-fold", "tangent": "pharmacokinetics textbook principles and absorption models"},
        {"topic": "diagnostic accuracy", "detail": "sensitivity 94.2%, specificity 87.6%, PPV 89.3%", "tangent": "healthcare system costs and insurance coverage policies"},
        {"topic": "surgical technique", "detail": "laparoscopic approach with 3 trocar sites and 45-minute operative time", "tangent": "surgical residency training requirements and board certification"},
        {"topic": "treatment guidelines", "detail": "first-line therapy: metformin 500mg BID titrated to 2000mg", "tangent": "diabetes prevalence statistics and public health campaigns"},
        {"topic": "vaccine efficacy", "detail": "88.7% efficacy against symptomatic infection at 6-month follow-up", "tangent": "vaccine manufacturing processes and cold chain logistics"},
        {"topic": "imaging protocol", "detail": "contrast-enhanced MRI with T1 and T2-weighted sequences", "tangent": "medical imaging equipment market size and hospital budgets"},
        {"topic": "rehabilitation program", "detail": "8-week protocol with progressive loading and ROM targets", "tangent": "sports medicine career pathways and certification requirements"},
        {"topic": "genetic screening", "detail": "panel tests 84 genes associated with hereditary cancer syndromes", "tangent": "history of genetics from Mendel to CRISPR"},
        {"topic": "antimicrobial stewardship", "detail": "restricted formulary reduced broad-spectrum antibiotic use by 34%", "tangent": "antimicrobial resistance global surveillance data"},
    ],
    "science": [
        {"topic": "quantum entanglement experiment", "detail": "Bell inequality violation at 4.2 sigma significance", "tangent": "philosophical interpretations of quantum mechanics"},
        {"topic": "exoplanet characterization", "detail": "transit spectroscopy detecting water vapor at 3.6 sigma", "tangent": "space telescope engineering and mirror fabrication"},
        {"topic": "CRISPR gene editing", "detail": "on-target efficiency of 78% with <2% off-target events", "tangent": "bioethics debates surrounding human genetic modification"},
        {"topic": "climate model projection", "detail": "RCP 4.5 scenario projects 1.8°C warming by 2100", "tangent": "climate policy negotiations and international agreements"},
        {"topic": "particle accelerator", "detail": "center-of-mass energy of 13.6 TeV with luminosity of 2×10^34", "tangent": "funding challenges for large-scale physics experiments"},
        {"topic": "materials synthesis", "detail": "CVD graphene on copper substrate with 99.4% monolayer coverage", "tangent": "history of carbon allotropes and Nobel Prize discoveries"},
        {"topic": "protein folding", "detail": "AlphaFold prediction with median GDT score of 92.4", "tangent": "AI applications across scientific disciplines"},
        {"topic": "seismological survey", "detail": "P-wave velocity of 6.8 km/s at 25km depth indicating basaltic composition", "tangent": "earthquake early warning system deployments worldwide"},
        {"topic": "battery chemistry", "detail": "solid-state lithium with 400 Wh/kg energy density at 500 cycles", "tangent": "electric vehicle market adoption trends and projections"},
        {"topic": "fusion reactor", "detail": "plasma temperature of 150 million degrees sustained for 17 seconds", "tangent": "energy policy and grid modernization challenges"},
    ],
    "law": [
        {"topic": "patent claim construction", "detail": "claim 1 recites a method comprising 4 specific steps", "tangent": "intellectual property law history and landmark decisions"},
        {"topic": "GDPR compliance audit", "detail": "data processing agreements with 23 third-party processors", "tangent": "privacy regulation comparison across jurisdictions"},
        {"topic": "antitrust merger review", "detail": "HHI increase of 400 points in the relevant market", "tangent": "economic theory of market concentration and competition"},
        {"topic": "employment discrimination case", "detail": "statistical analysis showing 2.3 standard deviation disparity", "tangent": "workplace diversity training programs and effectiveness"},
        {"topic": "environmental impact assessment", "detail": "NOx emissions projected at 145 tons/year requiring offset credits", "tangent": "environmental movement history and advocacy organizations"},
        {"topic": "contract interpretation", "detail": "force majeure clause covering pandemic, natural disaster, and civil unrest", "tangent": "contract drafting best practices and negotiation strategies"},
        {"topic": "securities fraud allegation", "detail": "alleged material misstatement in Q2 earnings call regarding revenue recognition", "tangent": "SEC enforcement history and organizational structure"},
        {"topic": "immigration proceedings", "detail": "asylum claim under INA § 208 based on political persecution", "tangent": "immigration statistics and demographic trends"},
        {"topic": "zoning variance request", "detail": "setback reduction from 25ft to 15ft for mixed-use development", "tangent": "urban planning philosophy and smart growth principles"},
        {"topic": "criminal sentencing", "detail": "federal guidelines level 24 with criminal history category III", "tangent": "prison reform movements and recidivism statistics"},
    ],
    "education": [
        {"topic": "standardized test redesign", "detail": "new format: 2 hours, 54 questions, adaptive difficulty", "tangent": "debate over standardized testing in college admissions"},
        {"topic": "curriculum alignment", "detail": "85% alignment with state standards across 12 subject areas", "tangent": "educational philosophy and progressive vs traditional approaches"},
        {"topic": "student retention program", "detail": "first-year retention rate improved from 72% to 84%", "tangent": "college ranking methodologies and their influence"},
        {"topic": "online learning platform", "detail": "completion rate of 34% across 450 courses with 2M enrollments", "tangent": "digital divide and internet access disparities"},
        {"topic": "teacher professional development", "detail": "40 hours annually with coaching observation cycles", "tangent": "teacher unions and collective bargaining history"},
        {"topic": "special education evaluation", "detail": "psychoeducational assessment battery taking 6-8 hours", "tangent": "disability rights legislation and advocacy organizations"},
        {"topic": "STEM pipeline program", "detail": "48% female enrollment vs 22% national average in CS", "tangent": "gender equity in workplace hiring and promotion"},
        {"topic": "school nutrition program", "detail": "free/reduced lunch eligibility at 64% with 78% participation", "tangent": "childhood obesity statistics and prevention programs"},
        {"topic": "bilingual education model", "detail": "dual-language immersion 50/50 split English/Spanish", "tangent": "immigration policy and language assimilation debates"},
        {"topic": "campus mental health services", "detail": "counseling center with 8 FTE staff serving 15,000 students", "tangent": "mental health crisis trends among young adults"},
    ],
    "environment": [
        {"topic": "solar farm performance", "detail": "capacity factor of 24.3% generating 285 GWh annually", "tangent": "solar panel manufacturing processes and supply chain"},
        {"topic": "wetland restoration", "detail": "300 acres restored with native plantings and hydrological reconnection", "tangent": "wetland ecology educational programs and ecotourism"},
        {"topic": "emissions reduction plan", "detail": "42% reduction target by 2030 from 2005 baseline", "tangent": "history of environmental regulation from Clean Air Act forward"},
        {"topic": "species conservation", "detail": "population census counted 847 breeding pairs up from 312", "tangent": "wildlife photography and nature documentary production"},
        {"topic": "water treatment facility", "detail": "processes 50 million gallons daily with UV disinfection", "tangent": "municipal government structure and public utility governance"},
        {"topic": "carbon offset program", "detail": "verified carbon credits from 12,000 acres of reforestation", "tangent": "corporate sustainability marketing and greenwashing concerns"},
        {"topic": "air quality monitoring", "detail": "23 stations measuring PM2.5, ozone, and NO2 continuously", "tangent": "public health impacts of air pollution and epidemiological studies"},
        {"topic": "recycling program", "detail": "diversion rate of 48% with contamination rate under 12%", "tangent": "plastic production statistics and ocean pollution"},
        {"topic": "electric grid integration", "detail": "15% renewable penetration with 200MW battery storage", "tangent": "energy company stock performance and investment opportunities"},
        {"topic": "biodiversity survey", "detail": "identified 2,340 species across 5 transects over 3 years", "tangent": "citizen science programs and community engagement strategies"},
    ],
    "sports": [
        {"topic": "player performance analytics", "detail": "WAR of 7.2 with .312/.405/.589 slash line", "tangent": "sports analytics history from Moneyball to present"},
        {"topic": "team salary cap", "detail": "$224M cap with $45M in dead money from prior contracts", "tangent": "professional athletes' charitable foundations and community work"},
        {"topic": "injury prevention program", "detail": "ACL injury rate reduced 42% with neuromuscular training", "tangent": "sports medicine career opportunities and education paths"},
        {"topic": "draft prospect evaluation", "detail": "4.38s 40-yard dash, 38\" vertical, 6.72s 3-cone drill", "tangent": "college football recruiting and NIL deal landscape"},
        {"topic": "stadium economics", "detail": "30-year lease at $12M/year with $450M in public financing", "tangent": "urban development and gentrification around sports venues"},
        {"topic": "coaching tactical analysis", "detail": "3-4 defense generating 2.1 sacks/game and 28% pressure rate", "tangent": "coaching career biographies and leadership philosophies"},
        {"topic": "youth development academy", "detail": "18 players promoted to first team over 5 years from 240 intake", "tangent": "youth sports participation trends and parental involvement"},
        {"topic": "broadcasting rights deal", "detail": "$7.5B over 7 years covering all regular season and playoff games", "tangent": "media industry transformation and streaming platform competition"},
        {"topic": "anti-doping testing", "detail": "6,000 out-of-competition tests annually with 1.2% adverse findings", "tangent": "Olympic Games hosting bid process and economic impact"},
        {"topic": "athlete nutrition protocol", "detail": "3,500 kcal/day with 2g protein/kg body weight periodization", "tangent": "supplement industry regulation and marketing claims"},
    ],
    "food": [
        {"topic": "food allergen labeling", "detail": "Top 9 allergens required on labels affecting 85% of packaged foods", "tangent": "food packaging design trends and sustainability materials"},
        {"topic": "organic certification", "detail": "USDA organic requires 3-year transition with annual inspections", "tangent": "organic food market growth statistics and consumer demographics"},
        {"topic": "sodium reduction initiative", "detail": "voluntary target of 2,300mg/day from current average of 3,400mg", "tangent": "restaurant industry labor shortages and operational challenges"},
        {"topic": "food safety inspection", "detail": "HACCP plan with 7 critical control points and daily monitoring", "tangent": "foodborne illness outbreak investigation procedures"},
        {"topic": "plant-based protein", "detail": "pea protein isolate with 85% protein content and complete amino acid profile", "tangent": "agricultural subsidies and crop insurance programs"},
        {"topic": "fermented food study", "detail": "4 servings/week associated with improved gut microbiome diversity", "tangent": "microbiome research funding and academic programs"},
        {"topic": "school lunch program", "detail": "must provide 1/3 of DRI for calories, protein, and key vitamins", "tangent": "child poverty statistics and social welfare programs"},
        {"topic": "caffeine research", "detail": "400mg/day maximum recommendation with half-life of 5-6 hours", "tangent": "coffee industry economics and fair trade certification"},
        {"topic": "food preservation method", "detail": "high-pressure processing at 600 MPa extending shelf life 2-3x", "tangent": "food waste statistics and supply chain inefficiencies"},
        {"topic": "artificial sweetener review", "detail": "FDA-approved at ADI of 50mg/kg body weight per day", "tangent": "sugar industry lobbying and public health advocacy"},
    ],
    "social_media": [
        {"topic": "content algorithm update", "detail": "new ranking prioritizes engagement quality over quantity, reducing clickbait 23%", "tangent": "founder biographies and company origin stories"},
        {"topic": "influencer marketing ROI", "detail": "average ROI of $5.20 per $1 spent with micro-influencers outperforming", "tangent": "celebrity culture and parasocial relationship psychology"},
        {"topic": "platform moderation policy", "detail": "AI flags 94% of violating content before user reports", "tangent": "free speech legal frameworks and First Amendment jurisprudence"},
        {"topic": "user data privacy", "detail": "platform collects location, contacts, browsing history, and device data", "tangent": "data broker industry and personal information marketplace"},
        {"topic": "creator monetization", "detail": "top 500 creators average $47K/month from platform ad revenue share", "tangent": "gig economy labor classification and worker protections"},
        {"topic": "misinformation detection", "detail": "fact-checking partnership covers 14 languages across 45 countries", "tangent": "journalism ethics and media literacy education"},
        {"topic": "social commerce", "detail": "in-app purchases grew 42% to $1.2B in Q3 2024", "tangent": "e-commerce fulfillment logistics and delivery infrastructure"},
        {"topic": "mental health impact study", "detail": "teens using platform 3+ hours daily showed 30% higher anxiety scores", "tangent": "parenting strategies for digital age and screen time management"},
        {"topic": "bot detection system", "detail": "removed 1.8B fake accounts in Q2 2024 using behavioral analysis", "tangent": "artificial intelligence ethics and responsible AI development"},
        {"topic": "ad targeting precision", "detail": "lookalike audiences achieve 2.8x conversion rate vs broad targeting", "tangent": "advertising industry history and evolution of marketing"},
    ],
    "history": [
        {"topic": "archaeological excavation", "detail": "stratigraphy reveals 5 occupation layers spanning 2000 years", "tangent": "museum curation practices and artifact preservation"},
        {"topic": "census historical records", "detail": "population grew from 3.9M in 1790 to 31.4M in 1860", "tangent": "genealogy research methods and DNA ancestry testing"},
        {"topic": "trade route analysis", "detail": "Silk Road merchants averaged 15-20 miles per day across 4,000 miles", "tangent": "modern globalization and international trade agreements"},
        {"topic": "battle casualties", "detail": "32,000 total casualties over 3 days including 7,000 killed in action", "tangent": "veterans affairs and military memorial design"},
        {"topic": "colonial economic records", "detail": "tobacco exports valued at £500,000 annually by 1770", "tangent": "modern tobacco industry regulation and health warnings"},
        {"topic": "medieval manuscript", "detail": "illuminated text dated to 1250 CE with 342 vellum pages", "tangent": "modern rare book collecting and auction market"},
        {"topic": "industrial output data", "detail": "steel production tripled from 1870 to 1900 reaching 11.2M tons", "tangent": "labor union organizing movements and strikes"},
        {"topic": "diplomatic correspondence", "detail": "237 letters exchanged between the two heads of state over 8 years", "tangent": "current diplomatic relations and embassy functions"},
        {"topic": "immigration records", "detail": "12.7M immigrants processed between 1892 and 1924 at the facility", "tangent": "modern immigration policy debates and border enforcement"},
        {"topic": "plague mortality data", "detail": "estimated 30-60% population mortality across affected regions", "tangent": "modern pandemic preparedness and public health infrastructure"},
    ],
    "government": [
        {"topic": "municipal budget allocation", "detail": "public safety 38%, education 24%, infrastructure 18%, other 20%", "tangent": "political campaign strategies and fundraising methods"},
        {"topic": "census methodology", "detail": "100% count of households plus 1% sample for detailed demographics", "tangent": "redistricting and gerrymandering legal challenges"},
        {"topic": "infrastructure spending bill", "detail": "$1.2T over 10 years: roads $110B, broadband $65B, rail $66B", "tangent": "lobbying industry and special interest group influence"},
        {"topic": "public health program", "detail": "vaccination coverage: 94% for MMR, 87% for flu, 72% for COVID booster", "tangent": "anti-vaccine movement history and social media amplification"},
        {"topic": "welfare reform evaluation", "detail": "TANF enrollment declined 65% while poverty rate decreased 4 points", "tangent": "political philosophy debates on government role in society"},
        {"topic": "housing assistance program", "detail": "Section 8 vouchers serve 2.3M households with 4.6M person waitlist", "tangent": "homelessness advocacy organizations and shelter operations"},
        {"topic": "emergency response plan", "detail": "FEMA staging areas within 500 miles of all major metropolitan areas", "tangent": "climate change and increased natural disaster frequency"},
        {"topic": "public transit funding", "detail": "$18.4B federal allocation with 80/20 federal/local match", "tangent": "urban sprawl history and suburban development patterns"},
        {"topic": "voter registration data", "detail": "72.7% of eligible population registered with 66.8% turnout", "tangent": "campaign advertising spending and media buying strategies"},
        {"topic": "education funding formula", "detail": "per-pupil spending of $13,600 with equity adjustments for poverty", "tangent": "school choice movement and charter school expansion"},
    ],
    "psychology": [
        {"topic": "cognitive load experiment", "detail": "dual-task paradigm showing 34% performance degradation under high load", "tangent": "meditation apps and commercial mindfulness products"},
        {"topic": "attachment style assessment", "detail": "54% secure, 22% anxious, 18% avoidant, 6% disorganized in sample", "tangent": "dating app psychology and online relationship formation"},
        {"topic": "PTSD treatment trial", "detail": "EMDR showed 68% remission at 12 months vs 42% for control", "tangent": "military veteran support organizations and advocacy"},
        {"topic": "developmental milestone study", "detail": "mean age for first words: 12 months, two-word combinations: 24 months", "tangent": "parenting book market and popular psychology publications"},
        {"topic": "addiction recovery research", "detail": "CBT + MAT achieved 58% abstinence at 1 year vs 32% for MAT alone", "tangent": "substance abuse policy and criminal justice reform"},
        {"topic": "social conformity experiment", "detail": "74% of participants conformed at least once across 12 trials", "tangent": "marketing persuasion techniques and consumer behavior"},
        {"topic": "IQ test norming study", "detail": "Flynn effect: 3 IQ points per decade from 1930 to 2000", "tangent": "educational equity debates and gifted program access"},
        {"topic": "sleep deprivation effects", "detail": "reaction time increased 25% after 24 hours without sleep", "tangent": "workplace productivity tips and time management strategies"},
        {"topic": "phobia treatment", "detail": "exposure therapy: 85% significant improvement over 12 sessions", "tangent": "mental health stigma and awareness campaigns"},
        {"topic": "memory reconsolidation", "detail": "recall accuracy decreased 23% when memories were reactivated and modified", "tangent": "eyewitness testimony legal standards and wrongful convictions"},
    ],
    "hr_workplace": [
        {"topic": "employee engagement survey", "detail": "72% engaged, 18% neutral, 10% disengaged across 8,400 respondents", "tangent": "corporate culture books and leadership guru methodologies"},
        {"topic": "compensation benchmarking", "detail": "median total compensation at 75th percentile of market for senior roles", "tangent": "income inequality statistics and minimum wage debates"},
        {"topic": "remote work productivity", "detail": "18% output increase with 23% reduction in unplanned absences", "tangent": "co-working space industry growth and WeWork history"},
        {"topic": "hiring funnel analysis", "detail": "1,200 applications → 85 phone screens → 24 on-sites → 8 offers → 6 hires", "tangent": "job search advice and interview preparation tips"},
        {"topic": "diversity metrics", "detail": "women in leadership up from 24% to 35% over 3 years", "tangent": "civil rights history and equal opportunity legislation"},
        {"topic": "benefits utilization", "detail": "HSA participation 43%, 401k enrollment 89%, FSA usage 31%", "tangent": "healthcare system reform debates and single-payer proposals"},
        {"topic": "performance management overhaul", "detail": "shift from annual reviews to quarterly check-ins with OKR framework", "tangent": "management consulting industry and Big Four firm offerings"},
        {"topic": "workplace safety audit", "detail": "OSHA recordable rate of 2.1 per 100 workers, down from 3.8", "tangent": "workers' compensation insurance market and claims management"},
        {"topic": "L&D program evaluation", "detail": "leadership program graduates promoted 2.3x faster than peers", "tangent": "MBA program rankings and business school admissions"},
        {"topic": "attrition analysis", "detail": "voluntary turnover 13.2% concentrated in 6-18 month tenure band", "tangent": "career coaching industry and personal branding strategies"},
    ],
    "agriculture": [
        {"topic": "precision agriculture trial", "detail": "variable-rate seeding increased yield 12% while reducing seed cost 8%", "tangent": "agricultural equipment manufacturer financial results"},
        {"topic": "soil amendment study", "detail": "biochar application at 10 tons/hectare increased CEC by 22%", "tangent": "organic farming movement philosophy and advocacy groups"},
        {"topic": "livestock feed optimization", "detail": "adding 2% seaweed supplement reduced methane emissions 42%", "tangent": "animal welfare organizations and ethical farming debates"},
        {"topic": "irrigation scheduling", "detail": "soil moisture sensors reduced water usage 35% without yield impact", "tangent": "water rights legal frameworks and interstate water disputes"},
        {"topic": "pest resistance study", "detail": "Bt corn showed 98% European corn borer mortality through season", "tangent": "GMO labeling controversy and consumer attitudes"},
        {"topic": "crop rotation trial", "detail": "3-year corn-soybean-wheat rotation improved soil N by 28%", "tangent": "farm subsidy programs and agricultural policy debates"},
        {"topic": "greenhouse automation", "detail": "automated climate control maintaining ±0.5°C and ±3% humidity", "tangent": "vertical farming investment trends and startup ecosystem"},
        {"topic": "harvest loss assessment", "detail": "combine header losses averaged 1.2 bu/acre with proper adjustment", "tangent": "food waste statistics from farm to consumer"},
        {"topic": "dairy herd genetics", "detail": "genomic selection improved milk yield 450 lbs/lactation over 5 years", "tangent": "dairy industry consolidation and small farm preservation"},
        {"topic": "cover crop study", "detail": "crimson clover fixed 120 lbs N/acre reducing fertilizer need 40%", "tangent": "regenerative agriculture certification programs and standards"},
    ],
    "transportation": [
        {"topic": "autonomous vehicle test", "detail": "4.2M miles with 0.3 reportable incidents per 100K miles", "tangent": "self-driving car ethical dilemmas and trolley problem debates"},
        {"topic": "airline on-time data", "detail": "87.3% on-time arrival rate with average delay of 14 minutes", "tangent": "airline industry history and deregulation effects"},
        {"topic": "fleet electrification", "detail": "TCO analysis shows EV breakeven at 62,000 miles vs diesel", "tangent": "charging infrastructure investment and government incentives"},
        {"topic": "freight rail efficiency", "detail": "fuel consumption of 0.87 gallons per ton-mile on the corridor", "tangent": "railroad history and transcontinental construction"},
        {"topic": "traffic signal optimization", "detail": "adaptive signals reduced travel time 14% on the 8-mile corridor", "tangent": "urban transportation planning degree programs and careers"},
        {"topic": "port throughput analysis", "detail": "container moves per hour increased 22% with new crane system", "tangent": "global supply chain disruption case studies"},
        {"topic": "bus rapid transit ridership", "detail": "45,000 daily riders with 97% schedule adherence", "tangent": "public transportation equity and transit deserts"},
        {"topic": "aviation fuel efficiency", "detail": "new engine design reduces fuel burn 15% vs previous generation", "tangent": "aerospace engineering education and career paths"},
        {"topic": "last-mile delivery", "detail": "drone delivery completes within 15 minutes for packages under 5 lbs", "tangent": "gig economy delivery platform worker classification"},
        {"topic": "highway safety audit", "detail": "rumble strips reduced run-off-road crashes 45% on the segment", "tangent": "distracted driving campaigns and smartphone usage statistics"},
    ],
    "real_estate": [
        {"topic": "appraisal methodology", "detail": "comparable sales within 0.5 miles adjusted for age, size, and condition", "tangent": "real estate agent commission structures and industry disruption"},
        {"topic": "vacancy rate analysis", "detail": "office vacancy 19.6% with Class A at 14.2% and Class B at 24.8%", "tangent": "remote work trends and future of office design"},
        {"topic": "construction cost estimate", "detail": "$285/sqft for Type III construction including FF&E", "tangent": "construction worker shortage and immigration policy effects"},
        {"topic": "rental yield calculation", "detail": "gross yield 6.2% with NOI after expenses at 4.1% cap rate", "tangent": "real estate investment seminars and guru marketing"},
        {"topic": "zoning variance application", "detail": "requesting increase from 35ft to 48ft height limit on 2.3-acre parcel", "tangent": "NIMBY vs YIMBY advocacy and community activism"},
        {"topic": "energy audit results", "detail": "LEED Gold certification with Energy Star score of 87", "tangent": "green building marketing trends and consumer preferences"},
        {"topic": "market absorption study", "detail": "12-month absorption rate of 85% for new multifamily units", "tangent": "housing affordability crisis and homelessness statistics"},
        {"topic": "property tax assessment", "detail": "assessed at $4.2M with effective rate of 1.23% yielding $51,660 annually", "tangent": "tax policy debates and Proposition 13 history"},
        {"topic": "flood risk evaluation", "detail": "Zone AE with BFE of 12ft and 1% annual flood probability", "tangent": "climate change adaptation strategies and sea level rise"},
        {"topic": "HOA financial analysis", "detail": "reserve fund at 72% funded with special assessment risk for roof", "tangent": "community governance and homeowner association disputes"},
    ],
}


# ── Subcategory generators ────────────────────────────────────────────────

def make_partial_answer(idx, domain, content, query_type, multi_source=False):
    """Query asks for multiple things, context only covers some."""
    topic = content["topic"]
    detail = content["detail"]

    multi_parts = {
        "what": (f"What are the specific metrics AND the timeline for the {topic}?", "timeline"),
        "how": (f"How is the {topic} implemented AND what are the costs involved?", "cost"),
        "is": (f"Is the {topic} effective AND has it been independently validated?", "independent validation"),
        "who": (f"Who manages the {topic} AND what is their qualification?", "qualification"),
        "when": (f"When was the {topic} initiated AND when is it expected to conclude?", "conclusion date"),
        "which": (f"Which components of the {topic} are complete AND which are pending?", "pending components"),
        "should": (f"Should the {topic} be expanded AND what would that cost?", "expansion cost"),
        "why": (f"Why was the {topic} approach chosen AND what alternatives were considered?", "alternatives"),
        "does": (f"Does the {topic} meet standards AND what certifications does it have?", "certifications"),
        "compare": (f"How does the {topic} compare to alternatives in both cost and effectiveness?", "cost comparison"),
    }
    query, missing_aspect = multi_parts.get(query_type, multi_parts["what"])

    case = {
        "id": f"t1_relevance_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "partial_answer",
        "query": query,
        "contexts": [f"The {topic}: {detail}. Additional performance metrics are being tracked."],
        "expected_mode": "trustworthy",
        "description": f"Asks about both metrics AND {missing_aspect} for {domain} topic, context only has metrics",
        "rationale": f"LLM should acknowledge that {missing_aspect} information is not provided",
        "required_elements": [
            missing_aspect,
            "not mentioned",
            "not specified",
            "not provided",
            "no information",
            "not available",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "multi_source" if multi_source else "single",
        "context_count": 2 if multi_source else 1,
        "reasoning_type": "factual",
        "evidence_pattern": "partial",
    }
    if multi_source:
        case["contexts"].append(f"A second analysis of {topic} confirmed the primary metrics but did not address {missing_aspect}.")
        case["context_sources"] = [
            {"source_id": f"src_relevance_{idx:03d}_a", "source_type": "report", "authority": "high"},
            {"source_id": f"src_relevance_{idx:03d}_b", "source_type": "study", "authority": "medium"},
        ]
    return case


def make_wrong_entity_focus(idx, domain, content, query_type):
    """Context is about a different entity than asked about."""
    topic = content["topic"]
    detail = content["detail"]
    return {
        "id": f"t1_relevance_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "wrong_entity_focus",
        "query": {
            "what": f"What is CompanyB's approach to {topic}?",
            "how": f"How does Organization Alpha handle {topic}?",
            "is": f"Is Team Beta's {topic} strategy effective?",
            "does": f"Does Division X follow {topic} best practices?",
            "who": f"Who leads Project Gamma's {topic} efforts?",
            "which": f"Which department manages Agency Z's {topic}?",
            "why": f"Why did Regional Office differ on {topic}?",
        }.get(query_type, f"What is CompanyB's approach to {topic}?"),
        "contexts": [
            f"CompanyA's {topic}: {detail}. CompanyA has been a leader in this area for over a decade.",
            f"Industry-wide trends in {topic} show increasing adoption across all major players.",
        ],
        "expected_mode": "trustworthy",
        "description": f"Asks about a different entity than what the {domain} context describes",
        "rationale": "Context describes CompanyA but question asks about CompanyB/another entity — LLM should note this",
        "required_elements": [
            "CompanyA",
            "not about",
            "different",
            "does not address",
            "no information about",
            "not mentioned",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "single",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
    }


def make_temporal_mismatch(idx, domain, content, query_type):
    """Context is from wrong time period for the question."""
    topic = content["topic"]
    detail = content["detail"]
    return {
        "id": f"t1_relevance_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "temporal_mismatch",
        "query": {
            "what": f"What are the current 2025 figures for {topic}?",
            "how": f"How has {topic} changed in the last quarter?",
            "is": f"Is the 2025 {topic} data available?",
            "when": f"When were the most recent {topic} results released?",
            "does": f"Does the latest {topic} report show improvement?",
            "which": f"Which 2025 {topic} metrics are most notable?",
            "who": f"Who is currently responsible for {topic} reporting?",
        }.get(query_type, f"What are the current 2025 figures for {topic}?"),
        "contexts": [f"2022 Annual Report on {topic}: {detail}. This report covers the fiscal year ending December 2022."],
        "expected_mode": "trustworthy",
        "description": f"Asks for current/2025 {domain} data but context is from 2022",
        "rationale": "Context is 3 years old — LLM should flag the temporal gap rather than presenting outdated data as current",
        "required_elements": [
            "2022",
            "outdated",
            "not current",
            "older",
            "may have changed",
            "from 2022",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "temporal",
        "evidence_pattern": "indirect",
    }


def make_tangent_drift(idx, domain, content, query_type):
    """Context starts relevant but drifts off-topic."""
    topic = content["topic"]
    detail = content["detail"]
    tangent = content["tangent"]
    return {
        "id": f"t1_relevance_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "tangent_drift",
        "query": {
            "what": f"What are the specific {topic} implementation details?",
            "how": f"How exactly is {topic} configured?",
            "is": f"Is the {topic} meeting its performance targets?",
            "does": f"Does {topic} meet the stated requirements?",
            "why": f"Why was this specific {topic} approach chosen?",
            "which": f"Which {topic} specifications are most important?",
        }.get(query_type, f"What are the specific {topic} implementation details?"),
        "contexts": [
            f"Overview of {topic}: {detail}. Moving to broader context, {tangent} has become increasingly important in the industry.",
            f"Industry analysts note that {tangent} represents a significant area of investment.",
        ],
        "expected_mode": "trustworthy",
        "description": f"Context starts with {topic} but drifts into {tangent}",
        "rationale": "Only the first sentence addresses the question — LLM should focus on that and note limited detail",
        "required_elements": [
            topic.split()[0],
            "limited",
            "brief",
            "does not detail",
            "not elaborated",
            "specific",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "single",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
    }


def make_over_answering(idx, domain, content, query_type):
    """Context has info but answer adds unrequested detail."""
    topic = content["topic"]
    detail = content["detail"]
    return {
        "id": f"t1_relevance_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "over_answering",
        "query": {
            "what": f"What is the single most important metric for {topic}?",
            "how": f"How is the primary {topic} KPI measured?",
            "is": f"Is {topic} on track for its primary goal?",
            "which": f"Which one metric best captures {topic} success?",
            "does": f"Does {topic} have a single key success indicator?",
        }.get(query_type, f"What is the single most important metric for {topic}?"),
        "contexts": [f"The {topic}: {detail}. Multiple KPIs are tracked including efficiency, quality, cost, and timeline adherence."],
        "expected_mode": "trustworthy",
        "description": f"Asks for ONE specific metric but {domain} context lists many",
        "rationale": "LLM should identify the most relevant single metric rather than listing everything available",
        "required_elements": [
            "primary",
            "key",
            "most important",
            "main",
            "single",
            "principal",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "evaluative",
        "evidence_pattern": "direct",
    }


def make_summarization_vs_answer(idx, domain, content, query_type):
    """Task is to answer a specific question, not summarize."""
    topic = content["topic"]
    detail = content["detail"]
    return {
        "id": f"t1_relevance_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "summarization_vs_answer",
        "query": {
            "is": f"Is {topic} achieving its stated objective — yes or no?",
            "does": f"Does {topic} meet the minimum threshold — yes or no?",
            "should": f"Should the {topic} program be continued based on the evidence?",
            "what": f"What is the bottom-line conclusion on {topic} effectiveness?",
            "how": f"How would you rate {topic} success in one sentence?",
        }.get(query_type, f"Is {topic} achieving its stated objective — yes or no?"),
        "contexts": [
            f"Comprehensive report on {topic}: {detail}. The program has been in operation for 3 years with annual reviews.",
            f"Stakeholder feedback on {topic} has been mixed, with supporters citing measurable outcomes and critics noting implementation challenges.",
        ],
        "expected_mode": "trustworthy",
        "description": f"Asks for a direct yes/no or bottom-line answer, not a {domain} summary",
        "rationale": "LLM should provide a direct answer, not just summarize all the context provided",
        "required_elements": [
            "yes",
            "no",
            "overall",
            "conclusion",
            "bottom line",
            "in summary",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "single",
        "context_count": 2,
        "reasoning_type": "evaluative",
        "evidence_pattern": "direct",
    }


def make_related_but_different(idx, domain, content, query_type):
    """Context answers a related but different question."""
    topic = content["topic"]
    detail = content["detail"]
    tangent = content["tangent"]
    return {
        "id": f"t1_relevance_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "related_but_different",
        "query": {
            "what": f"What is the long-term strategic vision for {topic}?",
            "how": f"How will {topic} evolve over the next 5 years?",
            "why": f"Why was the {topic} strategic direction changed?",
            "should": f"Should {topic} pivot to a new approach?",
            "which": f"Which strategic options are being considered for {topic}?",
        }.get(query_type, f"What is the long-term strategic vision for {topic}?"),
        "contexts": [
            f"Current operational status of {topic}: {detail}. Quarterly review confirmed all systems operating within parameters.",
        ],
        "expected_mode": "trustworthy",
        "description": f"Asks about strategy/vision but {domain} context only has current operational data",
        "rationale": "Context covers operations but not strategy — related topic but different question",
        "required_elements": [
            "strategic",
            "vision",
            "long-term",
            "future",
            "not addressed",
            "operational",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "evaluative",
        "evidence_pattern": "indirect",
    }


def make_prerequisite_missing(idx, domain, content, query_type):
    """Context gives prerequisites, not the actual answer."""
    topic = content["topic"]
    detail = content["detail"]
    return {
        "id": f"t1_relevance_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "prerequisite_missing",
        "query": {
            "what": f"What were the actual outcomes of the {topic}?",
            "how": f"How did the {topic} perform in practice?",
            "does": f"Does the {topic} deliver on its promises?",
            "is": f"Is the {topic} producing measurable results?",
            "which": f"Which {topic} outcomes exceeded expectations?",
        }.get(query_type, f"What were the actual outcomes of the {topic}?"),
        "contexts": [
            f"Pre-implementation plan for {topic}: {detail}. Requirements gathering, stakeholder alignment, and resource allocation phases were completed.",
            f"The {topic} launch prerequisites include training, documentation, and pilot testing.",
        ],
        "expected_mode": "trustworthy",
        "description": f"Asks for outcomes but {domain} context only describes planning/prerequisites",
        "rationale": "Context has planning details but no actual outcomes — LLM should distinguish prerequisites from results",
        "required_elements": [
            "outcomes",
            "results",
            "not yet",
            "planning",
            "pre-implementation",
            "no outcome data",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "single",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
    }


def make_granularity_mismatch(idx, domain, content, query_type):
    """Answer at wrong detail level for the question."""
    topic = content["topic"]
    detail = content["detail"]
    return {
        "id": f"t1_relevance_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "granularity_mismatch",
        "query": {
            "what": f"What are the day-by-day details of the {topic} over the past week?",
            "how": f"How does each individual component of {topic} perform?",
            "which": f"Which specific sub-metric of {topic} needs the most attention?",
            "when": f"When exactly did each phase of {topic} begin and end?",
            "who": f"Who is responsible for each individual task in {topic}?",
        }.get(query_type, f"What are the day-by-day details of the {topic} over the past week?"),
        "contexts": [f"Annual summary of {topic}: {detail}. Year-end review covers aggregate performance across all divisions."],
        "expected_mode": "trustworthy",
        "description": f"Asks for granular detail but {domain} context only has high-level summary",
        "rationale": "Question asks for daily/component-level detail but context is annual/aggregate — granularity mismatch",
        "required_elements": [
            "aggregate",
            "summary",
            "annual",
            "not broken down",
            "high-level",
            "detailed breakdown",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
    }


def make_scope_mismatch(idx, domain, content, query_type):
    """Answer for wrong scope (global vs local, etc.)."""
    topic = content["topic"]
    detail = content["detail"]
    return {
        "id": f"t1_relevance_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "scope_mismatch",
        "query": {
            "what": f"What are the global trends in {topic}?",
            "how": f"How does {topic} vary across international markets?",
            "is": f"Is {topic} consistent worldwide?",
            "does": f"Does the {topic} approach apply globally?",
            "which": f"Which countries lead in {topic}?",
            "compare": f"How does US {topic} compare to European approaches?",
        }.get(query_type, f"What are the global trends in {topic}?"),
        "contexts": [
            f"Regional report on {topic} for the Northeast district: {detail}. This analysis covers operations within the district's 12-county service area.",
        ],
        "expected_mode": "trustworthy",
        "description": f"Asks for global/broad scope but {domain} context is regional/local",
        "rationale": "Question asks about global trends but context covers only one region — scope mismatch",
        "required_elements": [
            "regional",
            "local",
            "Northeast",
            "district",
            "not global",
            "limited scope",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "indirect",
    }


def make_format_mismatch(idx, domain, content, query_type):
    """Wrong output format for the question type."""
    topic = content["topic"]
    detail = content["detail"]
    return {
        "id": f"t1_relevance_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "format_mismatch",
        "query": {
            "how": f"How do you implement {topic}? Provide numbered steps.",
            "what": f"What are the top 3 priorities for {topic}? List them in order.",
            "which": f"Which {topic} factors matter most? Rank them 1-5.",
            "should": f"Should we proceed with {topic}? Provide a pros and cons table.",
        }.get(query_type, f"How do you implement {topic}? Provide numbered steps."),
        "contexts": [f"General overview of {topic}: {detail}. The approach has been refined based on industry experience."],
        "expected_mode": "trustworthy",
        "description": f"Asks for structured format (list/steps/table) but {domain} context is prose",
        "rationale": "Question specifies output format — answer should attempt to match the requested structure",
        "required_elements": [
            "1.",
            "step",
            "first",
            "priority",
            "rank",
            "pros",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "procedural",
        "evidence_pattern": "direct",
    }


def make_cherry_picking(idx, domain, content, query_type):
    """NEW: selectively quoting to distort meaning."""
    topic = content["topic"]
    detail = content["detail"]
    return {
        "id": f"t1_relevance_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "cherry_picking",
        "query": {
            "what": f"What is the overall assessment of {topic}?",
            "how": f"How should {topic} be evaluated comprehensively?",
            "is": f"Is {topic} successful when considering all factors?",
            "does": f"Does the evidence support {topic} overall?",
            "should": f"Should {topic} be considered a success?",
        }.get(query_type, f"What is the overall assessment of {topic}?"),
        "contexts": [
            f"Positive findings: {detail}. The program exceeded its primary targets.",
            f"Challenges identified: implementation costs were 40% over budget, staff turnover increased 25%, and three key milestones were missed by 2+ months.",
            f"The independent review concluded that {topic} shows promise but requires significant adjustments before scaling.",
        ],
        "expected_mode": "trustworthy",
        "description": f"Tests whether answer includes BOTH positive and negative {domain} evidence",
        "rationale": "Answer should not cherry-pick only positive or only negative findings — must present balanced view",
        "required_elements": [
            "challenges",
            "over budget",
            "adjustments",
            "both",
            "however",
            "mixed",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "multi_source",
        "context_count": 3,
        "reasoning_type": "evaluative",
        "evidence_pattern": "mixed",
        "context_sources": [
            {"source_id": f"src_relevance_{idx:03d}_a", "source_type": "report", "authority": "high"},
            {"source_id": f"src_relevance_{idx:03d}_b", "source_type": "audit", "authority": "high"},
            {"source_id": f"src_relevance_{idx:03d}_c", "source_type": "review", "authority": "medium"},
        ],
    }


def make_false_precision(idx, domain, content, query_type):
    """NEW: Over-precise answers from vague data."""
    topic = content["topic"]
    return {
        "id": f"t1_relevance_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "false_precision",
        "query": {
            "what": f"What is the exact figure for {topic}?",
            "how": f"How precisely can we measure {topic} outcomes?",
            "is": f"Is the {topic} figure exactly as reported?",
            "does": f"Does the data support a precise estimate of {topic}?",
        }.get(query_type, f"What is the exact figure for {topic}?"),
        "contexts": [
            f"Preliminary estimates suggest {topic} falls in the range of typical industry performance. Exact figures are pending final audit.",
            f"Industry sources indicate {topic} outcomes vary significantly depending on methodology and sample selection.",
        ],
        "expected_mode": "trustworthy",
        "description": f"Asks for exact figures but {domain} data is approximate/preliminary",
        "rationale": "LLM should convey the imprecision of the source data rather than providing false precision",
        "required_elements": [
            "estimate",
            "preliminary",
            "approximate",
            "range",
            "pending",
            "varies",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "single",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "partial",
    }


def make_assumption_injection(idx, domain, content, query_type):
    """NEW: Answer assumes unstated premises."""
    topic = content["topic"]
    detail = content["detail"]
    return {
        "id": f"t1_relevance_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "assumption_injection",
        "query": {
            "should": f"Should {topic} be expanded to new regions?",
            "what": f"What would happen if {topic} were scaled up?",
            "how": f"How should {topic} be adapted for different contexts?",
            "is": f"Is {topic} ready for broader deployment?",
        }.get(query_type, f"Should {topic} be expanded to new regions?"),
        "contexts": [f"Performance data for {topic} in the pilot region: {detail}. The pilot operated under specific conditions including dedicated staffing and executive sponsorship."],
        "expected_mode": "trustworthy",
        "description": f"Asks about scaling {domain} initiative but context is pilot-only",
        "rationale": "LLM should note that pilot conditions may not replicate elsewhere rather than assuming they will",
        "required_elements": [
            "pilot",
            "specific conditions",
            "may not",
            "assumption",
            "dedicated",
            "cannot assume",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "evaluative",
        "evidence_pattern": "partial",
    }


# ── Main generation ───────────────────────────────────────────────────────

def generate_all_cases():
    """Generate all 168 new relevance cases with even distribution."""
    cases = []
    idx = 24  # start after t1_relevance_hard_023

    domains = list(DOMAIN_CONTENT.keys())

    subcategory_counts = {
        "partial_answer": 16,
        "wrong_entity_focus": 14,
        "temporal_mismatch": 14,
        "tangent_drift": 14,
        "over_answering": 12,
        "summarization_vs_answer": 12,
        "related_but_different": 12,
        "prerequisite_missing": 12,
        "granularity_mismatch": 12,
        "scope_mismatch": 12,
        "format_mismatch": 10,
        "cherry_picking": 12,
        "false_precision": 10,
        "assumption_injection": 8,
    }

    # Query type distribution
    qt_weights = {
        "what": 0.30, "how": 0.20, "is": 0.12, "does": 0.08,
        "why": 0.08, "when": 0.04, "who": 0.04, "which": 0.05,
        "should": 0.05, "compare": 0.04,
    }
    qt_list = []
    for qt, weight in qt_weights.items():
        qt_list.extend([qt] * max(1, round(weight * 170)))
    while len(qt_list) < 170:
        qt_list.append("what")

    maker_map = {
        "partial_answer": make_partial_answer,
        "wrong_entity_focus": make_wrong_entity_focus,
        "temporal_mismatch": make_temporal_mismatch,
        "tangent_drift": make_tangent_drift,
        "over_answering": make_over_answering,
        "summarization_vs_answer": make_summarization_vs_answer,
        "related_but_different": make_related_but_different,
        "prerequisite_missing": make_prerequisite_missing,
        "granularity_mismatch": make_granularity_mismatch,
        "scope_mismatch": make_scope_mismatch,
        "format_mismatch": make_format_mismatch,
        "cherry_picking": make_cherry_picking,
        "false_precision": make_false_precision,
        "assumption_injection": make_assumption_injection,
    }

    # Multi-source: 10 partial_answer + all 12 cherry_picking + 3 more from tangent_drift = 25
    multi_source_partial = 10
    multi_source_tangent = 3

    case_num = 0
    for subcat, count in subcategory_counts.items():
        for i in range(count):
            domain = domains[case_num % len(domains)]
            content_idx = (case_num // len(domains)) % len(DOMAIN_CONTENT[domain])
            content = DOMAIN_CONTENT[domain][content_idx]
            qt = qt_list[case_num % len(qt_list)]

            maker = maker_map[subcat]

            if subcat == "partial_answer" and i < multi_source_partial:
                case = maker(idx, domain, content, qt, multi_source=True)
            elif subcat == "cherry_picking":
                # cherry_picking maker always creates multi-source
                case = maker(idx, domain, content, qt)
            else:
                case = maker(idx, domain, content, qt)

            cases.append(case)
            idx += 1
            case_num += 1

    return cases


def main():
    filepath = Path("data/tier1_core/relevance.json")
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    new_cases = generate_all_cases()
    data["cases"].extend(new_cases)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Added {len(new_cases)} relevance cases (total: {len(data['cases'])})")

    # Verify distribution
    from collections import Counter
    subcats = Counter(c["subcategory"] for c in new_cases)
    domains_c = Counter(c["domain"] for c in new_cases)
    qts = Counter(c["query_type"] for c in new_cases)
    multi = sum(1 for c in new_cases if c.get("source_type") == "multi_source")
    ctx_counts = Counter(c["context_count"] for c in new_cases)

    print(f"\nSubcategory distribution:")
    for s, n in subcats.most_common():
        print(f"  {s:30s} {n}")
    print(f"\nDomain distribution:")
    for d, n in domains_c.most_common():
        print(f"  {d:20s} {n}")
    print(f"\nQuery type distribution:")
    for q, n in qts.most_common():
        print(f"  {q:10s} {n}")
    print(f"\nMulti-source cases: {multi}")
    print(f"Context count distribution: {dict(ctx_counts)}")


if __name__ == "__main__":
    main()
