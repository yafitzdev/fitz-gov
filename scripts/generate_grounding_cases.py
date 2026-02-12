#!/usr/bin/env python3
"""Generate 166 new grounding cases for Phase 2 expansion.

Uses domain-specific content templates combined with subcategory patterns
to generate diverse, realistic test cases with proper forbidden_claims.
"""

import json
from pathlib import Path

# ── Domain content pools ──────────────────────────────────────────────────

DOMAIN_CONTENT = {
    "technology": {
        "topics": [
            ("cloud migration project", "The enterprise cloud migration project deployed 47 microservices across three AWS regions."),
            ("API gateway performance", "The API gateway handles 12,000 requests per second with 99.97% uptime."),
            ("cybersecurity audit", "The annual security audit identified 23 vulnerabilities, with 8 classified as critical."),
            ("machine learning pipeline", "The ML pipeline processes 2.3 terabytes of training data daily using GPU clusters."),
            ("database optimization", "PostgreSQL query optimization reduced average response time from 450ms to 89ms."),
            ("container orchestration", "Kubernetes manages 340 pods across 12 nodes with auto-scaling enabled."),
            ("DevOps pipeline", "The CI/CD pipeline runs 1,200 automated tests per deployment cycle."),
            ("frontend framework", "React 19 introduced server components reducing client-side bundle size by 35%."),
            ("network infrastructure", "The CDN serves content from 45 edge locations with average latency of 23ms."),
            ("open source project", "The open-source library has 15,000 GitHub stars and 230 active contributors."),
        ],
        "entities": ["AWS", "Google Cloud", "Azure", "Kubernetes", "Docker", "React", "PostgreSQL", "Redis", "Nginx", "GraphQL"],
    },
    "finance": {
        "topics": [
            ("quarterly earnings", "TechCorp reported Q3 2024 revenue of $4.2 billion, up 18% year-over-year."),
            ("venture capital round", "The Series B funding round raised $45 million at a $320 million valuation."),
            ("stock market analysis", "The S&P 500 gained 12.3% in the first half of 2024, driven by tech sector growth."),
            ("corporate merger", "The proposed merger valued HealthFirst at $8.7 billion including $2.1 billion in debt."),
            ("credit risk assessment", "The portfolio's default rate decreased from 3.2% to 2.1% over the fiscal year."),
            ("cryptocurrency market", "Bitcoin mining difficulty increased 14% following the latest halving event."),
            ("pension fund performance", "The state pension fund's assets grew to $142 billion with a 7.8% annual return."),
            ("mortgage market trends", "Average 30-year fixed mortgage rates reached 6.8% in October 2024."),
            ("IPO filing", "The IPO prospectus disclosed annual recurring revenue of $890 million."),
            ("hedge fund strategy", "The long-short equity fund returned 22.4% net of fees in 2024."),
        ],
        "entities": ["Goldman Sachs", "JPMorgan", "BlackRock", "Vanguard", "Berkshire Hathaway", "S&P 500", "NASDAQ", "Federal Reserve", "SEC", "NYSE"],
    },
    "medicine": {
        "topics": [
            ("clinical trial results", "The Phase III trial enrolled 2,400 patients across 85 sites in 12 countries."),
            ("drug efficacy study", "The new antibiotic showed 89% efficacy against resistant strains in laboratory tests."),
            ("surgical outcomes", "Robotic-assisted surgery reduced average hospital stay from 5.2 to 2.8 days."),
            ("vaccine development", "The mRNA vaccine candidate produced neutralizing antibodies in 94% of participants."),
            ("diagnostic imaging", "The AI-assisted MRI analysis detected tumors with 97.3% sensitivity."),
            ("mental health treatment", "Cognitive behavioral therapy showed 62% remission rate for moderate depression."),
            ("pediatric care study", "Early intervention programs reduced ADHD symptom severity by 40% in children aged 6-12."),
            ("cardiology research", "The new stent design reduced restenosis rates from 15% to 4.7% at one-year follow-up."),
            ("oncology treatment", "Combination immunotherapy achieved a 45% objective response rate in advanced melanoma."),
            ("epidemiological data", "Hospital readmission rates decreased from 18.5% to 12.3% after protocol changes."),
        ],
        "entities": ["FDA", "WHO", "NIH", "Mayo Clinic", "Johns Hopkins", "Pfizer", "Moderna", "AstraZeneca", "Merck", "CDC"],
    },
    "science": {
        "topics": [
            ("quantum computing", "The 127-qubit processor achieved quantum advantage on a specific optimization problem."),
            ("space exploration", "The Mars rover collected 43 soil samples over 18 months of operation."),
            ("climate research", "Arctic ice coverage declined by 13.4% per decade since satellite measurements began in 1979."),
            ("particle physics", "The collider experiment detected 847 candidate events consistent with the predicted particle."),
            ("genetic research", "CRISPR gene editing corrected the mutation in 78% of treated cells in the laboratory."),
            ("astronomy discovery", "The telescope identified 23 exoplanets in the habitable zone of their host stars."),
            ("materials science", "The new superconductor maintained zero resistance at temperatures up to 15 Kelvin."),
            ("oceanography study", "Deep sea measurements recorded water temperatures 0.8°C above the 50-year average."),
            ("paleontology find", "The fossil site yielded 156 specimens from at least 12 distinct species."),
            ("renewable energy", "The experimental solar cell achieved 33.7% energy conversion efficiency."),
        ],
        "entities": ["NASA", "CERN", "MIT", "Caltech", "Nature", "Science", "ESA", "SpaceX", "NOAA", "IPCC"],
    },
    "law": {
        "topics": [
            ("patent dispute", "The patent infringement case involved 7 claims across 3 patent families filed between 2018-2022."),
            ("regulatory compliance", "GDPR enforcement actions resulted in fines totaling €2.1 billion in 2024."),
            ("antitrust investigation", "The merger review examined market share in 14 geographic regions."),
            ("employment law case", "The class action represented 3,400 employees alleging wage theft over a 5-year period."),
            ("intellectual property", "The copyright registration covered 45 distinct software modules and their documentation."),
            ("environmental regulation", "The new EPA rule applies to facilities emitting more than 25,000 tons of CO2 annually."),
            ("contract dispute", "The breach of contract claim sought $12.5 million in damages plus attorneys' fees."),
            ("privacy legislation", "The state privacy law grants consumers the right to delete data within 45 days of request."),
            ("criminal sentencing", "The federal sentencing guidelines recommend 37-46 months for the offense level."),
            ("corporate governance", "The SEC settlement required the company to appoint an independent compliance monitor for 3 years."),
        ],
        "entities": ["Supreme Court", "SEC", "FTC", "EPA", "DOJ", "EEOC", "GDPR", "CCPA", "USPTO", "NLRB"],
    },
    "education": {
        "topics": [
            ("university enrollment", "Fall 2024 enrollment reached 42,500 students with a 23% acceptance rate."),
            ("standardized testing", "Average SAT scores rose 12 points nationally to 1,040 in 2024."),
            ("online learning", "The MOOC platform served 28 million learners across 190 countries."),
            ("STEM education", "STEM program graduation rates increased from 34% to 51% over five years."),
            ("early childhood", "Pre-K programs showed a 0.4 standard deviation improvement in literacy readiness."),
            ("teacher retention", "District teacher turnover dropped from 22% to 14% after salary increases."),
            ("special education", "Inclusive classrooms improved social skills scores by 28% for students with autism."),
            ("student debt", "Average student loan debt at graduation was $37,400 for the class of 2024."),
            ("curriculum reform", "The new math curriculum aligned with 95% of state standards across 38 states."),
            ("campus safety", "Campus security investments reduced reported incidents by 45% over three years."),
        ],
        "entities": ["Harvard", "Stanford", "MIT", "College Board", "ACT", "Department of Education", "UNESCO", "OECD", "Common Core", "AP Program"],
    },
    "environment": {
        "topics": [
            ("renewable energy adoption", "Solar capacity installations reached 420 gigawatts globally in 2024."),
            ("deforestation tracking", "Amazon deforestation decreased 34% in 2024 compared to the previous year."),
            ("electric vehicle impact", "EV sales represented 18% of all new car purchases in 2024."),
            ("carbon capture", "The pilot carbon capture facility processes 500,000 tons of CO2 annually."),
            ("wildlife conservation", "The wolf reintroduction program increased the population from 31 to 108 individuals."),
            ("ocean pollution", "Microplastic concentrations averaged 24 particles per liter in coastal waters."),
            ("air quality monitoring", "PM2.5 levels dropped below 15 μg/m³ after coal plant closures."),
            ("sustainable agriculture", "Regenerative farming practices increased soil organic carbon by 0.4% per year."),
            ("water resources", "Desalination capacity doubled to 120 million cubic meters per day globally."),
            ("biodiversity assessment", "The ecosystem survey catalogued 3,400 species including 23 previously undocumented."),
        ],
        "entities": ["EPA", "IPCC", "NOAA", "WWF", "Greenpeace", "Sierra Club", "UNEP", "Tesla", "BP", "Shell"],
    },
    "sports": {
        "topics": [
            ("player statistics", "The quarterback completed 68.7% of passes for 4,183 yards and 32 touchdowns."),
            ("team performance", "The team's defensive efficiency rating ranked 3rd in the league at 104.2."),
            ("transfer market", "The transfer fee was reported at €85 million plus €15 million in performance bonuses."),
            ("Olympic results", "The national team won 14 gold, 21 silver, and 18 bronze medals at the Games."),
            ("sports science", "VO2 max testing showed improvement from 55.2 to 61.8 mL/kg/min after training."),
            ("stadium development", "The new stadium project has a budget of $1.7 billion with 65,000 seat capacity."),
            ("coaching strategy", "The pressing system recovered possession within 6 seconds of losing it 43% of the time."),
            ("injury recovery", "Return-to-play protocols reduced ACL re-injury rates from 23% to 12%."),
            ("draft analysis", "The draft class included 14 first-round picks from the conference."),
            ("league expansion", "The expansion franchise will begin play in 2026 with a $750 million entry fee."),
        ],
        "entities": ["FIFA", "NFL", "NBA", "MLB", "UEFA", "IOC", "ESPN", "Nike", "Adidas", "Premier League"],
    },
    "food": {
        "topics": [
            ("nutrition research", "The study found that Mediterranean diet adherence reduced cardiovascular risk by 31%."),
            ("food safety recall", "The recall affected 2.4 million pounds of product distributed across 23 states."),
            ("organic farming", "Organic food sales grew 12.8% to reach $67.6 billion in the US market."),
            ("dietary supplement", "The clinical trial found no significant difference between the supplement and placebo groups."),
            ("restaurant industry", "Average restaurant profit margins narrowed to 3.5% amid rising food costs."),
            ("food technology", "Plant-based meat alternatives captured 2.7% of the packaged meat market."),
            ("beverage trends", "Sugar-sweetened beverage consumption declined 23% among teens over five years."),
            ("food labeling", "New labeling requirements mandate added sugar disclosure on 78% of packaged foods."),
            ("fermentation science", "Controlled fermentation reduced antinutrient content by 65% in legume-based products."),
            ("food waste", "Supply chain optimization reduced food waste by 18% across participating retailers."),
        ],
        "entities": ["FDA", "USDA", "WHO", "Beyond Meat", "Impossible Foods", "Whole Foods", "Nestlé", "PepsiCo", "Coca-Cola", "Kraft"],
    },
    "social_media": {
        "topics": [
            ("platform engagement", "Daily active users reached 450 million with average session time of 38 minutes."),
            ("content moderation", "The AI moderation system flagged 12 million posts per month with 91% accuracy."),
            ("influencer marketing", "Influencer marketing spending grew to $21.1 billion globally in 2024."),
            ("algorithm impact", "The recommendation algorithm increased watch time by 35% but also amplified divisive content."),
            ("creator economy", "Top 1% of creators earned 80% of platform ad revenue totaling $4.2 billion."),
            ("misinformation study", "False claims spread 6 times faster than corrections on the platform."),
            ("digital advertising", "Social media ad revenue reached $230 billion with a 15% year-over-year increase."),
            ("user privacy", "The platform collected 47 categories of personal data according to its privacy policy."),
            ("viral content analysis", "Posts with emotional language received 3.2x more engagement than neutral posts."),
            ("platform regulation", "The Digital Services Act required transparency reports from platforms with over 45 million users."),
        ],
        "entities": ["Meta", "TikTok", "Twitter/X", "YouTube", "Instagram", "Snapchat", "Reddit", "LinkedIn", "Pinterest", "ByteDance"],
    },
    "history": {
        "topics": [
            ("archaeological discovery", "Excavations uncovered 234 artifacts dating to approximately 3,200 BCE."),
            ("military history", "The battle involved 45,000 troops and lasted 3 days with 12,000 casualties."),
            ("ancient civilization", "The city supported an estimated population of 80,000 at its peak around 500 CE."),
            ("colonial era", "The colony exported 2.4 million pounds of tobacco annually by 1700."),
            ("industrial revolution", "Factory production increased 340% between 1820 and 1860 in the region."),
            ("civil rights movement", "The boycott lasted 381 days and involved an estimated 40,000 participants."),
            ("medieval period", "The cathedral took 142 years to build from 1163 to 1345."),
            ("exploration era", "The expedition mapped 2,300 miles of coastline over 18 months."),
            ("diplomatic history", "The treaty was signed by 27 nations and established 14 new international bodies."),
            ("immigration history", "Between 1892 and 1954, approximately 12 million immigrants entered through the processing center."),
        ],
        "entities": ["Rome", "Egypt", "Ottoman Empire", "British Empire", "Ming Dynasty", "Aztec", "Mesopotamia", "Byzantine", "Viking", "Mongol"],
    },
    "government": {
        "topics": [
            ("municipal budget", "The city approved a $4.8 billion operating budget for fiscal year 2025."),
            ("census data", "The 2020 census counted 331.4 million residents with 7.4% population growth."),
            ("infrastructure project", "The bridge rehabilitation project is budgeted at $340 million over 4 years."),
            ("public health program", "The vaccination campaign reached 78% of the eligible population."),
            ("election results", "Voter turnout reached 66.8% with 158.4 million ballots cast."),
            ("welfare program", "SNAP benefits served 42.1 million recipients in 21.6 million households."),
            ("tax policy", "The corporate tax rate adjustment is projected to generate $180 billion over 10 years."),
            ("immigration policy", "Processing times averaged 8.5 months for employment-based applications."),
            ("public safety", "Crime rates decreased 5.7% overall with violent crime down 8.2%."),
            ("housing initiative", "The affordable housing program funded 12,400 new units across 35 municipalities."),
        ],
        "entities": ["Congress", "Senate", "White House", "CBO", "GAO", "HHS", "DOT", "HUD", "IRS", "FEMA"],
    },
    "psychology": {
        "topics": [
            ("cognitive study", "The memory recall experiment tested 280 participants across four age groups."),
            ("behavioral research", "Screen time exceeding 4 hours daily correlated with 23% higher anxiety scores."),
            ("developmental psychology", "Bilingual children showed a 6-month advantage in executive function tasks."),
            ("clinical trial", "The mindfulness intervention reduced PTSD symptoms by 34% over 12 weeks."),
            ("social psychology", "The conformity experiment replicated Asch's findings with a 37% conformity rate."),
            ("neuropsychology", "Brain imaging revealed increased prefrontal cortex activation during decision-making tasks."),
            ("educational psychology", "Spaced repetition improved long-term retention by 42% compared to massed practice."),
            ("personality research", "The Big Five personality assessment showed test-retest reliability of 0.87."),
            ("addiction study", "Cognitive behavioral therapy achieved a 45% abstinence rate at 6-month follow-up."),
            ("child psychology", "Secure attachment at age 2 predicted social competence scores at age 10."),
        ],
        "entities": ["APA", "WHO", "NIH", "Stanford", "Harvard", "Kahneman", "Piaget", "Bandura", "DSM-5", "Beck"],
    },
    "hr_workplace": {
        "topics": [
            ("employee satisfaction", "The annual engagement survey showed a 72% satisfaction rate across 8,400 respondents."),
            ("remote work study", "Hybrid employees reported 18% higher productivity than fully in-office peers."),
            ("compensation benchmark", "Median software engineer salary reached $165,000 in major tech hubs."),
            ("diversity initiative", "Women in leadership roles increased from 24% to 35% over three years."),
            ("hiring trends", "Average time-to-fill for technical roles decreased from 52 to 38 days."),
            ("employee benefits", "Companies offering fertility benefits increased from 24% to 42% since 2020."),
            ("workplace safety", "OSHA-recordable incidents decreased 28% after implementing the new safety program."),
            ("training effectiveness", "Employees completing the program showed 23% higher promotion rates within 2 years."),
            ("retention analysis", "Voluntary turnover averaged 13.2% with the highest rates in the first 18 months."),
            ("performance management", "Continuous feedback models replaced annual reviews at 67% of Fortune 500 companies."),
        ],
        "entities": ["SHRM", "LinkedIn", "Glassdoor", "Indeed", "Gallup", "McKinsey", "Deloitte", "OSHA", "EEOC", "ADP"],
    },
    "agriculture": {
        "topics": [
            ("crop yield study", "Precision agriculture techniques increased corn yield by 12% to 198 bushels per acre."),
            ("livestock management", "The automated feeding system reduced feed waste by 22% across 1,200 cattle."),
            ("soil health research", "No-till farming practices increased soil microbial diversity by 34%."),
            ("irrigation efficiency", "Drip irrigation systems reduced water usage by 40% compared to flood irrigation."),
            ("pest management", "Integrated pest management reduced pesticide application by 55% without yield loss."),
            ("organic certification", "Organic farmland expanded to 7.3 million acres representing 1.4% of total cropland."),
            ("agricultural technology", "Drone surveys covered 5,000 acres per day detecting early signs of crop disease."),
            ("dairy production", "Average milk production per cow reached 23,391 pounds annually."),
            ("harvest logistics", "Automated harvesting reduced labor costs by 35% and post-harvest losses by 18%."),
            ("seed development", "The drought-resistant variety maintained 85% of normal yield under water stress conditions."),
        ],
        "entities": ["USDA", "FAO", "John Deere", "Monsanto/Bayer", "Cargill", "ADM", "Syngenta", "Pioneer", "Land-Grant University", "CGIAR"],
    },
    "transportation": {
        "topics": [
            ("fleet management", "The logistics company operates 4,200 vehicles covering 8.3 million miles monthly."),
            ("aviation safety", "The airline maintained a 99.97% on-time departure rate across 340,000 flights."),
            ("rail infrastructure", "The high-speed rail project will connect the two cities in 2.5 hours vs 5 by car."),
            ("autonomous vehicles", "The self-driving fleet completed 4.2 million miles with 0.3 incidents per 100,000 miles."),
            ("shipping industry", "Container shipping rates dropped 62% from the 2022 peak to $1,400 per TEU."),
            ("public transit", "The new bus rapid transit line serves 45,000 riders daily across 28 stations."),
            ("electric fleet", "Converting the delivery fleet to EVs reduced fuel costs by $12.4 million annually."),
            ("traffic management", "Smart signal timing reduced average commute times by 14% on the corridor."),
            ("freight logistics", "Last-mile delivery costs represent 53% of total shipping expenses."),
            ("airport expansion", "The terminal expansion added 12 gates and increased annual capacity by 8 million passengers."),
        ],
        "entities": ["Boeing", "Airbus", "Tesla", "FedEx", "UPS", "Maersk", "NTSB", "FAA", "DOT", "Uber"],
    },
    "real_estate": {
        "topics": [
            ("housing market", "Median home prices rose 5.4% year-over-year to $412,000 nationally."),
            ("commercial property", "Office vacancy rates climbed to 19.6% in major metropolitan areas."),
            ("construction costs", "Building material costs increased 8.3% with lumber up 22% from the prior year."),
            ("rental market", "Average rent for a two-bedroom apartment reached $1,850 in urban markets."),
            ("property development", "The mixed-use development includes 400 residential units and 50,000 sq ft of retail."),
            ("REIT performance", "The residential REIT index returned 14.2% including dividends in 2024."),
            ("green building", "LEED-certified buildings commanded a 7.5% rental premium over conventional properties."),
            ("property valuation", "Comparable sales analysis showed a range of $285 to $310 per square foot."),
            ("zoning changes", "The rezoning proposal would allow up to 12 stories in the transit-oriented district."),
            ("mortgage lending", "First-time homebuyers represented 32% of purchases with average down payments of 8%."),
        ],
        "entities": ["NAR", "Zillow", "Redfin", "CBRE", "JLL", "Blackstone", "Fannie Mae", "Freddie Mac", "HUD", "CoreLogic"],
    },
}

# ── Subcategory templates ─────────────────────────────────────────────────

def make_numerical_hallucination(idx, domain, topic_data, query_type):
    """Context has numbers but NOT the specific number asked about."""
    topic_name, base_content = topic_data
    queries = {
        "what": f"What is the total cost of the {topic_name}?",
        "how": f"How much was spent on the {topic_name}?",
        "is": f"Is the {topic_name} budget over $10 million?",
        "does": f"Does the {topic_name} exceed initial projections?",
        "why": f"Why did the {topic_name} costs increase?",
        "when": f"When was the final budget for the {topic_name} approved?",
        "who": f"Who approved the budget for the {topic_name}?",
        "which": f"Which phase of the {topic_name} was most expensive?",
        "should": f"Should additional funding be allocated to the {topic_name}?",
        "compare": f"How does the {topic_name} budget compare to similar projects?",
    }
    return {
        "id": f"t1_grounding_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "numerical_hallucination",
        "query": queries.get(query_type, queries["what"]),
        "contexts": [base_content + " The project timeline spans 18 months with quarterly milestones."],
        "expected_mode": "trustworthy",
        "description": f"Asks for specific cost/budget number not present in {domain} context",
        "rationale": "Context mentions numerical metrics but not the specific figure asked about — LLM may invent a number",
        "forbidden_claims": [
            "\\$\\d",
            "\\d+\\s*(million|billion|thousand)",
            "budget (is|was|of) \\$?\\d",
            "costs? (approximately|about|around) \\$?\\d",
            "total (of |cost )\\$?\\d",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
    }


def make_attribution_hallucination(idx, domain, topic_data, query_type, multi_source=False):
    """Multiple sources — forbidden_claims catch attributing claims to wrong source."""
    topic_name, base_content = topic_data
    entities = DOMAIN_CONTENT[domain]["entities"]
    e1, e2 = entities[idx % len(entities)], entities[(idx + 3) % len(entities)]

    ctx1 = f"According to {e1}: {base_content}"
    ctx2 = f"{e2} reported different findings on {topic_name}, noting significant methodological concerns with previous analyses."

    queries = {
        "what": f"What did {e1} specifically report about the {topic_name}?",
        "who": f"Who conducted the primary research on {topic_name}?",
        "how": f"How did {e2} evaluate the {topic_name}?",
        "is": f"Is {e1}'s analysis of the {topic_name} more recent?",
        "does": f"Does {e2} agree with {e1}'s findings on {topic_name}?",
        "why": f"Why do {e1} and {e2} differ on the {topic_name}?",
        "which": f"Which organization's {topic_name} analysis is more comprehensive?",
    }

    case = {
        "id": f"t1_grounding_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "attribution_hallucination",
        "query": queries.get(query_type, queries["what"]),
        "contexts": [ctx1, ctx2],
        "expected_mode": "trustworthy",
        "description": f"Tests whether claims are attributed to correct source in {domain}",
        "rationale": f"LLM might attribute {e1}'s claims to {e2} or vice versa",
        "forbidden_claims": [
            f"(?i){e2}.*(?:found|reported|showed|concluded|stated).*(?:\\d+|increase|decrease)",
            f"(?i)according to {e2}.*\\d",
            f"(?i){e1}.*methodological concerns",
            "(?i)both (organizations?|groups?|sources?) (agree|found|reported)",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "multi_source" if multi_source else "single",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
    }
    if multi_source:
        case["context_sources"] = [
            {"source_id": f"src_grounding_{idx:03d}_a", "source_type": "report", "authority": "high"},
            {"source_id": f"src_grounding_{idx:03d}_b", "source_type": "article", "authority": "medium"},
        ]
    return case


def make_temporal_confusion(idx, domain, topic_data, query_type):
    """Dates/timelines in context — forbidden_claims catch mixing up dates."""
    topic_name, base_content = topic_data
    return {
        "id": f"t1_grounding_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "temporal_confusion",
        "query": {
            "when": f"When did the {topic_name} results become available?",
            "what": f"What were the {topic_name} outcomes in the most recent period?",
            "how": f"How has the {topic_name} changed over the measured timeframe?",
            "is": f"Is the {topic_name} data from the current year?",
            "does": f"Does the {topic_name} timeline align with initial projections?",
            "why": f"Why was the {topic_name} timeline extended?",
            "who": f"Who managed the {topic_name} during the transition period?",
            "which": f"Which year showed the best {topic_name} results?",
        }.get(query_type, f"When were the {topic_name} results published?"),
        "contexts": [
            base_content + " Initial data collection began in January 2022.",
            f"The {topic_name} review was completed in March 2024 covering the previous 24-month period.",
        ],
        "expected_mode": "trustworthy",
        "description": f"Asks about timing of {domain} events with multiple dates in context",
        "rationale": "Multiple timeframes in context may cause LLM to confuse which date applies to which event",
        "forbidden_claims": [
            "(?i)(completed|finished|published|released) in (january|february|march|april|may|june|july|august|september|october|november|december) 202[0-1]",
            "(?i)began in (march|april|may|june|july|august|september|october|november|december) 2024",
            "(?i)(started|initiated|launched) in 2024",
            "\\b202[56789]\\b",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "single",
        "context_count": 2,
        "reasoning_type": "temporal",
        "evidence_pattern": "direct",
    }


def make_entity_blending(idx, domain, topic_data, query_type, multi_source=False):
    """Info about multiple entities — forbidden_claims catch merging facts."""
    topic_name, base_content = topic_data
    entities = DOMAIN_CONTENT[domain]["entities"]
    e1, e2 = entities[idx % len(entities)], entities[(idx + 5) % len(entities)]

    ctx1 = f"{e1} reported: {base_content}"
    ctx2 = f"{e2} took a different approach to {topic_name}, focusing on long-term sustainability metrics rather than short-term performance indicators."

    queries = {
        "what": f"What approach did {e1} take regarding the {topic_name}?",
        "how": f"How does {e1}'s {topic_name} strategy differ from {e2}'s?",
        "is": f"Is {e1}'s {topic_name} approach focused on sustainability?",
        "does": f"Does {e1} prioritize short-term performance in {topic_name}?",
        "which": f"Which organization focuses on sustainability metrics for {topic_name}?",
        "who": f"Who led {e1}'s {topic_name} initiative?",
        "why": f"Why did {e1} and {e2} take different approaches to {topic_name}?",
    }

    case = {
        "id": f"t1_grounding_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "entity_blending",
        "query": queries.get(query_type, queries["what"]),
        "contexts": [ctx1, ctx2],
        "expected_mode": "trustworthy",
        "description": f"Tests whether {e1} and {e2} facts stay separated in {domain}",
        "rationale": f"LLM might blend {e1}'s metrics/claims with {e2}'s approach or vice versa",
        "forbidden_claims": [
            f"(?i){e1}.*sustainability metrics",
            f"(?i){e1}.*long-term sustainability",
            f"(?i){e2}.*(?:\\d+|reported|quarterly|annual)",
            f"(?i)both.*(?:reported|found|achieved|showed)",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "multi_source" if multi_source else "single",
        "context_count": 2,
        "reasoning_type": "comparative",
        "evidence_pattern": "direct",
    }
    if multi_source:
        case["context_sources"] = [
            {"source_id": f"src_grounding_{idx:03d}_a", "source_type": "report", "authority": "high"},
            {"source_id": f"src_grounding_{idx:03d}_b", "source_type": "study", "authority": "high"},
        ]
    return case


def make_process_hallucination(idx, domain, topic_data, query_type):
    """Process described — forbidden_claims catch fabricated steps."""
    topic_name, base_content = topic_data
    queries = {
        "how": f"How is the {topic_name} process implemented step by step?",
        "what": f"What are the specific steps in the {topic_name} process?",
        "is": f"Is there a verification step in the {topic_name} process?",
        "does": f"Does the {topic_name} process include a review phase?",
        "which": f"Which steps in the {topic_name} process are automated?",
        "why": f"Why does the {topic_name} process require multiple stages?",
    }
    return {
        "id": f"t1_grounding_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "process_hallucination",
        "query": queries.get(query_type, queries["how"]),
        "contexts": [base_content + f" The {topic_name} follows established protocols."],
        "expected_mode": "trustworthy",
        "description": f"Asks about specific process steps not detailed in {domain} context",
        "rationale": "Context mentions a process exists but doesn't detail specific steps — LLM may fabricate steps",
        "forbidden_claims": [
            "(?i)step \\d+",
            "(?i)first,?\\s+.*(?:then|next|after|followed)",
            "(?i)(phase|stage) \\d+:?\\s+\\w",
            "(?i)the (first|second|third|fourth|final) (step|phase|stage)",
            "(?i)begins? (by|with).*(?:then|next|after)",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "procedural",
        "evidence_pattern": "direct",
    }


def make_quote_fabrication(idx, domain, topic_data, query_type):
    """Text context — forbidden_claims catch invented quotes."""
    topic_name, base_content = topic_data
    entities = DOMAIN_CONTENT[domain]["entities"]
    e1 = entities[idx % len(entities)]
    queries = {
        "what": f"What did {e1} say about the {topic_name}?",
        "who": f"Who commented on the {topic_name} findings?",
        "how": f"How did {e1} characterize the {topic_name}?",
        "is": f"Is there an official statement from {e1} on the {topic_name}?",
        "does": f"Does {e1} endorse the {topic_name} approach?",
    }
    return {
        "id": f"t1_grounding_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "quote_fabrication",
        "query": queries.get(query_type, queries["what"]),
        "contexts": [base_content + f" {e1} was involved in reviewing the {topic_name} outcomes."],
        "expected_mode": "trustworthy",
        "description": f"Asks for specific quotes not present in {domain} context",
        "rationale": f"Context mentions {e1} but provides no direct quotes — LLM may fabricate quotes",
        "forbidden_claims": [
            '(?i)"[^"]{10,}"',
            "(?i)stated that ['\"]",
            f"(?i){e1} (said|stated|commented|remarked|noted|declared),? ['\"]",
            "(?i)in (his|her|their) words",
            "(?i)quote:?\\s+['\"]",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
    }


def make_statistical_inference(idx, domain, topic_data, query_type):
    """Statistics given — forbidden_claims catch extrapolations."""
    topic_name, base_content = topic_data
    queries = {
        "what": f"What is the projected trend for {topic_name} next year?",
        "how": f"How will the {topic_name} metrics change going forward?",
        "is": f"Is the {topic_name} trend likely to continue?",
        "does": f"Does the data suggest {topic_name} will improve?",
        "should": f"Should we expect {topic_name} growth to accelerate?",
        "why": f"Why is the {topic_name} trend expected to continue?",
    }
    return {
        "id": f"t1_grounding_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "statistical_inference",
        "query": queries.get(query_type, queries["what"]),
        "contexts": [base_content, f"Historical {topic_name} data shows year-over-year variation with no clear directional trend."],
        "expected_mode": "trustworthy",
        "description": f"Asks for projection/forecast not supported by {domain} data",
        "rationale": "Context has historical stats but no projections — LLM may extrapolate trends",
        "forbidden_claims": [
            "(?i)(project|forecast|predict|expect|anticipat).*\\d+%",
            "(?i)will (likely |probably )?(reach|grow|increase|decrease|decline)",
            "(?i)by (2025|2026|2027|next year).*\\d",
            "(?i)(estimated|projected) to (be|reach|hit)",
            "(?i)on track to",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "single",
        "context_count": 2,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
    }


def make_code_hallucination(idx, domain, topic_data, query_type):
    """Code/tech contexts — forbidden_claims catch invented features."""
    topic_name, base_content = topic_data
    queries = {
        "what": f"What specific configuration options does the {topic_name} support?",
        "how": f"How do you configure the advanced settings for {topic_name}?",
        "is": f"Is there a built-in debugging mode for the {topic_name}?",
        "does": f"Does the {topic_name} support hot-reloading?",
        "which": f"Which version of {topic_name} introduced this feature?",
    }
    return {
        "id": f"t1_grounding_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "code_hallucination",
        "query": queries.get(query_type, queries["how"]),
        "contexts": [base_content + " Documentation covers basic setup and deployment."],
        "expected_mode": "trustworthy",
        "description": f"Asks for specific technical config not in {domain} documentation",
        "rationale": "Context describes general capabilities but not specific config — LLM may invent settings",
        "forbidden_claims": [
            "(?i)(config|setting|parameter|flag|option)\\s*[:=]\\s*['\"]?\\w+['\"]?",
            "(?i)--[a-z]+-[a-z]+",
            "(?i)set\\s+\\w+\\s*=",
            "(?i)add the following (to|in) (your|the) (config|settings|yaml|json)",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "procedural",
        "evidence_pattern": "direct",
    }


def make_table_inference(idx, domain, topic_data, query_type):
    """Tabular data — forbidden_claims catch unsupported conclusions."""
    topic_name, base_content = topic_data
    queries = {
        "what": f"What caused the changes shown in the {topic_name} data?",
        "why": f"Why did the {topic_name} metrics shift as shown?",
        "how": f"How do the {topic_name} results correlate with external factors?",
        "is": f"Is there a causal relationship in the {topic_name} data?",
        "does": f"Does the {topic_name} data indicate a structural change?",
        "which": f"Which factor most influenced the {topic_name} outcomes?",
    }
    return {
        "id": f"t1_grounding_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "table_inference",
        "query": queries.get(query_type, queries["what"]),
        "contexts": [
            base_content,
            f"Summary table for {topic_name}: Period 1 metrics, Period 2 metrics, and Period 3 metrics are provided without explanatory notes.",
        ],
        "expected_mode": "trustworthy",
        "description": f"Asks for causal explanation of {domain} tabular data that only shows correlation",
        "rationale": "Data shows changes over time but no causal explanations — LLM may invent causes",
        "forbidden_claims": [
            "(?i)(caused|due to|because of|result of|driven by|attributed to)\\s+(?!the data|the context|the information)",
            "(?i)this (is|was) (likely |probably )?(caused|because|due)",
            "(?i)(led to|resulted in|contributed to)\\s+the (increase|decrease|change|shift)",
            "(?i)the (primary|main|key) (cause|reason|factor|driver) (is|was)",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "single",
        "context_count": 2,
        "reasoning_type": "causal",
        "evidence_pattern": "direct",
    }


def make_causal_hallucination(idx, domain, topic_data, query_type):
    """NEW: Contexts show correlation — forbidden_claims catch invented causation."""
    topic_name, base_content = topic_data
    queries = {
        "why": f"Why did the {topic_name} outcomes change?",
        "what": f"What caused the {topic_name} shift?",
        "how": f"How did the {topic_name} outcomes come about?",
        "is": f"Is the {topic_name} change caused by the intervention?",
        "does": f"Does the evidence prove a causal link in {topic_name}?",
    }
    return {
        "id": f"t1_grounding_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "causal_hallucination",
        "query": queries.get(query_type, queries["why"]),
        "contexts": [
            base_content,
            f"The {topic_name} data shows a correlation between the measured variables. No controlled experiment has been conducted to establish causation.",
            f"External reviews note that multiple confounding factors could explain the observed {topic_name} pattern.",
        ],
        "expected_mode": "trustworthy",
        "description": f"Asks for causal explanation when only correlation exists in {domain}",
        "rationale": "Context explicitly states correlation only — LLM should not claim causation",
        "forbidden_claims": [
            "(?i)(proves?|demonstrat|establish|confirm).*caus",
            "(?i)(directly |clearly )?(caused|causes|causing)",
            "(?i)the (reason|cause) (is|was) (that|because|due)",
            "(?i)this (led|leads) (directly |)to",
            "(?i)(definitively|conclusively) (shows?|proved?|linked)",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "single",
        "context_count": 3,
        "reasoning_type": "causal",
        "evidence_pattern": "direct",
    }


def make_comparative_hallucination(idx, domain, topic_data, query_type):
    """NEW: Multiple items described separately — forbidden_claims catch fabricated comparisons."""
    topic_name, base_content = topic_data
    entities = DOMAIN_CONTENT[domain]["entities"]
    e1, e2 = entities[idx % len(entities)], entities[(idx + 4) % len(entities)]

    queries = {
        "compare": f"How does {e1}'s {topic_name} compare to {e2}'s?",
        "which": f"Which is better for {topic_name}: {e1} or {e2}?",
        "is": f"Is {e1}'s {topic_name} performance superior to {e2}'s?",
        "what": f"What are the differences between {e1} and {e2} on {topic_name}?",
        "how": f"How do {e1} and {e2} rank on {topic_name}?",
    }
    return {
        "id": f"t1_grounding_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "comparative_hallucination",
        "query": queries.get(query_type, queries["compare"]),
        "contexts": [
            f"{e1}: {base_content}",
            f"{e2} operates in the {topic_name} space with a different strategic focus. Detailed metrics are not publicly available.",
        ],
        "expected_mode": "trustworthy",
        "description": f"Asks to compare entities when only one has detailed {domain} data",
        "rationale": f"Only {e1} has specific data — LLM may fabricate {e2}'s numbers for comparison",
        "forbidden_claims": [
            f"(?i){e2}.*\\d+\\s*%",
            f"(?i){e2}.*\\$\\d",
            f"(?i){e2}.*(higher|lower|better|worse|faster|slower|more|fewer) than {e1}",
            f"(?i){e1} (outperform|beat|exceed|lag|trail|surpass).*{e2}",
            "(?i)(ranks?|ranked) (first|second|third|last|higher|lower)",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "single",
        "context_count": 2,
        "reasoning_type": "comparative",
        "evidence_pattern": "direct",
    }


def make_geographic_hallucination(idx, domain, topic_data, query_type):
    """NEW: Locations mentioned — forbidden_claims catch wrong geographic info."""
    topic_name, base_content = topic_data
    queries = {
        "where": f"Where specifically is the {topic_name} located?",
        "what": f"What region does the {topic_name} primarily serve?",
        "which": f"Which countries are included in the {topic_name}?",
        "how": f"How many locations does the {topic_name} cover?",
        "is": f"Is the {topic_name} available in Europe?",
    }
    return {
        "id": f"t1_grounding_hard_{idx:03d}",
        "difficulty": "hard",
        "subcategory": "geographic_hallucination",
        "query": queries.get(query_type, queries["what"]),
        "contexts": [base_content + f" The {topic_name} operates across multiple regions."],
        "expected_mode": "trustworthy",
        "description": f"Asks for specific geographic details not provided in {domain} context",
        "rationale": "Context mentions multiple regions but doesn't specify which — LLM may invent locations",
        "forbidden_claims": [
            "(?i)(located|based|headquartered) in (New York|London|Tokyo|Paris|Berlin|Sydney|Beijing|Toronto|Singapore|Mumbai)",
            "(?i)(operates|available|present) in (\\d+) (countries|states|regions|cities)",
            "(?i)(North America|Europe|Asia|Africa|South America|Australia|Middle East)",
            "(?i)(including|such as)\\s+(the )?(US|UK|China|Japan|Germany|France|India|Brazil|Canada|Australia)",
        ],
        "domain": domain,
        "query_type": query_type,
        "source_type": "single",
        "context_count": 1,
        "reasoning_type": "factual",
        "evidence_pattern": "direct",
    }


# ── Main generation ───────────────────────────────────────────────────────

def generate_all_cases():
    """Generate all 166 new grounding cases with even distribution."""
    cases = []
    idx = 25

    domains = list(DOMAIN_CONTENT.keys())
    query_types = ["what", "how", "is", "does", "why", "when", "who", "which", "should", "compare"]

    # Distribution: subcategory -> count
    subcategory_counts = {
        "numerical_hallucination": 20,
        "attribution_hallucination": 18,
        "temporal_confusion": 18,
        "entity_blending": 18,
        "process_hallucination": 14,
        "quote_fabrication": 14,
        "statistical_inference": 14,
        "code_hallucination": 10,
        "table_inference": 10,
        "causal_hallucination": 12,
        "comparative_hallucination": 10,
        "geographic_hallucination": 8,
    }

    # Query type distribution targets (~percentages)
    qt_weights = {
        "what": 0.30, "how": 0.20, "is": 0.12, "does": 0.08,
        "why": 0.10, "when": 0.05, "who": 0.05, "which": 0.05,
        "should": 0.03, "compare": 0.02,
    }

    # Multi-source targets: first 15 attribution_hallucination + first 15 entity_blending
    multi_source_attribution = set()
    multi_source_entity_blending = set()

    maker_map = {
        "numerical_hallucination": make_numerical_hallucination,
        "attribution_hallucination": make_attribution_hallucination,
        "temporal_confusion": make_temporal_confusion,
        "entity_blending": make_entity_blending,
        "process_hallucination": make_process_hallucination,
        "quote_fabrication": make_quote_fabrication,
        "statistical_inference": make_statistical_inference,
        "code_hallucination": make_code_hallucination,
        "table_inference": make_table_inference,
        "causal_hallucination": make_causal_hallucination,
        "comparative_hallucination": make_comparative_hallucination,
        "geographic_hallucination": make_geographic_hallucination,
    }

    qt_index = 0
    qt_list = []
    for qt, weight in qt_weights.items():
        qt_list.extend([qt] * max(1, round(weight * 166)))
    # Ensure we have enough query types
    while len(qt_list) < 166:
        qt_list.append("what")

    case_num = 0
    for subcat, count in subcategory_counts.items():
        for i in range(count):
            domain = domains[case_num % len(domains)]
            topic_idx = (case_num // len(domains)) % len(DOMAIN_CONTENT[domain]["topics"])
            topic_data = DOMAIN_CONTENT[domain]["topics"][topic_idx]
            qt = qt_list[case_num % len(qt_list)]

            maker = maker_map[subcat]

            if subcat == "attribution_hallucination":
                multi = i < 15  # first 15 get multi-source
                case = maker(idx, domain, topic_data, qt, multi_source=multi)
            elif subcat == "entity_blending":
                multi = i < 15  # first 15 get multi-source
                case = maker(idx, domain, topic_data, qt, multi_source=multi)
            else:
                case = maker(idx, domain, topic_data, qt)

            cases.append(case)
            idx += 1
            case_num += 1

    return cases


def main():
    filepath = Path("data/tier1_core/grounding.json")
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    new_cases = generate_all_cases()
    data["cases"].extend(new_cases)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Added {len(new_cases)} grounding cases (total: {len(data['cases'])})")

    # Verify distribution
    from collections import Counter
    subcats = Counter(c["subcategory"] for c in new_cases)
    domains = Counter(c["domain"] for c in new_cases)
    qts = Counter(c["query_type"] for c in new_cases)
    multi = sum(1 for c in new_cases if c.get("source_type") == "multi_source")
    ctx_counts = Counter(c["context_count"] for c in new_cases)

    print(f"\nSubcategory distribution:")
    for s, n in subcats.most_common():
        print(f"  {s:30s} {n}")
    print(f"\nDomain distribution:")
    for d, n in domains.most_common():
        print(f"  {d:20s} {n}")
    print(f"\nQuery type distribution:")
    for q, n in qts.most_common():
        print(f"  {q:10s} {n}")
    print(f"\nMulti-source cases: {multi}")
    print(f"Context count distribution: {dict(ctx_counts)}")


if __name__ == "__main__":
    main()
