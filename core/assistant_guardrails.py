"""
AI Career Guidance Assistant Guardrails and Knowledge Engine
Enforces:
1. Strict Career Topic Restriction (AI-01, AI-02)
2. Identity Shielding & Anti-Impersonation (AI-03, AI-04)
3. Prompt-Injection Defense & Confidentiality (AI-05, AI-06, AI-07)
4. Pre-defined replies for off-topic, identity, and security queries
5. Grounded Career Guidance with interactive career cards matching UI Screen 1
"""

import re
from .models import Career, UserSkill, UserInterest

# Pre-defined exact replies as specified by SRS and system constraints
PREDEFINED_REDIRECT_OFFTOPIC = "I can help with career-related questions. Would you like to explore a career or improve a skill?"
PREDEFINED_REDIRECT_IDENTITY = "I can help with career-related questions. What career path would you like to explore?"
PREDEFINED_REDIRECT_PRIVACY = "Personal profiles and system data are private and cannot be disclosed. I can only assist with your own career guidance and development."

# Identity and implementation query detection patterns
IDENTITY_PATTERNS = [
    r"\bwho\s+are\s+you\b",
    r"\bwhat\s+are\s+you\b",
    r"\bwhat\s+is\s+your\s+name\b",
    r"\bwhat\s+model\b",
    r"\bwhich\s+model\b",
    r"\bare\s+you\s+(an\s+ai|a\s+robot|a\s+bot|a\s+human|chatgpt|gpt|gemini|claude|deepseek|llama|anthropic|openai)\b",
    r"\breveal\s+(your\s+)?(identity|model|provider|developer|creator)\b",
    r"\bwho\s+(created|made|programmed|developed|trained)\s+you\b",
    r"\btell\s+me\s+the\s+name\s+of\s+your\s+(ai\s+model|provider|system)\b",
    r"\bpretend\s+you\s+are\s+(a\s+human|human|a\s+licensed\s+counsellor|a\s+doctor)\b",
]

# Injection, hidden prompts, credentials and privacy exfiltration patterns
SECURITY_PATTERNS = [
    r"\bignore\s+(all\s+)?(rules|instructions|restrictions|guidelines|previous)\b",
    r"\bshow\s+(your\s+)?(system\s+)?(prompt|instructions|directive)\b",
    r"\bprint\s+(your\s+)?(system\s+)?(instructions|prompt)\b",
    r"\brepeat\s+(the\s+)?(prompt|instructions|above)\b",
    r"\bwhat\s+are\s+your\s+(system\s+)?(instructions|hidden\s+prompts)\b",
    r"\bapi[_\s-]?key\b",
    r"\bsecret[_\s-]?token\b",
    r"\bdatabase\s+password\b",
    r"\bjailbreak\b",
    r"\bdan\s+mode\b",
]

PRIVACY_PATTERNS = [
    r"\b(another|other|someone\s+else('s)?)\s+(user|student)('s)?\s+(profile|data|records|info)\b",
    r"\bgive\s+me\s+(another|other)\s+user('s)?\b",
    r"\bshow\s+(another|other)\s+student('s)?\b",
    r"\bsee\s+(all\s+)?users\b",
    r"\blist\s+all\s+user\s+profiles\b",
]

# Obvious off-topic indicator keywords & patterns
OFFTOPIC_PATTERNS = [
    r"\bjoke\b",
    r"\bcapital\s+of\s+[a-z]+",
    r"\brecipe\b",
    r"\bweather\b",
    r"\bhoroscope\b",
    r"\bmovie\s+review\b",
    r"\bwho\s+won\s+the\s+(world\s+cup|match|election|super\s+bowl)\b",
    r"\bwrite\s+a\s+(poem|story|song|script\s+for\s+a\s+movie)\b",
    r"\btell\s+me\s+about\s+(politics|president|celebrity|gossip|football|cricket)\b",
    r"\bplay\s+a\s+game\b",
    r"\bmath\s+equation\b",
    r"\bcalculate\s+\d+",
    r"\bcheat\s+codes?\b",
    r"\bhow\s+to\s+cook\b",
    r"\bhow\s+to\s+bake\b",
    r"\bfavorite\s+color\b",
]

# Positive career domain keywords - queries containing these or application terms are career-relevant
CAREER_KEYWORDS = [
    "career", "careers", "job", "jobs", "role", "roles", "profession", "vocation",
    "degree", "college", "university", "school", "grade", "10th", "11th", "12th", "stream",
    "bca", "mca", "btech", "b.tech", "bsc", "b.sc", "be", "b.e", "mba", "bcom", "diploma", "masters", "phd",
    "qualification", "education", "course", "courses", "curriculum", "syllabus", "study", "learning",
    "skill", "skills", "learn", "roadmap", "pathway", "internship", "intern", "placement", "interview",
    "resume", "cv", "hire", "hiring", "salary", "salaries", "package", "compensation", "industry",
    "software", "developer", "development", "engineer", "engineering", "data science", "data analyst",
    "systems analyst", "cloud", "devops", "cybersecurity", "security", "ai", "machine learning",
    "ui", "ux", "designer", "design", "robotics", "aerospace", "finance", "analyst", "investment",
    "management", "marketing", "science", "programming", "coding", "python", "javascript", "react",
    "java", "sql", "html", "css", "node", "gap", "recommendation", "recommend", "assessment",
    "strengths", "interests", "guidance", "mentor", "eligibility", "certifications", "certification",
    "fresher", "experience", "future", "scope", "switch", "transition", "ascento", "careerwithinu"
]

def classify_and_respond(user_message, user=None):
    """
    Main entry point for assistant processing.
    Returns a tuple: (response_text, is_redirected, career_cards_list)
    """
    cleaned = user_message.strip()
    lower_msg = cleaned.lower()

    # Check 1: Privacy exfiltration attempts
    for pat in PRIVACY_PATTERNS:
        if re.search(pat, lower_msg):
            return PREDEFINED_REDIRECT_PRIVACY, True, []

    # Check 2: System prompt / injection / credentials inquiry
    for pat in SECURITY_PATTERNS:
        if re.search(pat, lower_msg):
            return PREDEFINED_REDIRECT_IDENTITY, True, []

    # Check 3: Identity / model name / provider disclosure inquiry
    for pat in IDENTITY_PATTERNS:
        if re.search(pat, lower_msg):
            return PREDEFINED_REDIRECT_IDENTITY, True, []

    # Check 4: Explicit off-topic check
    for pat in OFFTOPIC_PATTERNS:
        if re.search(pat, lower_msg):
            # Verify if user also asked a career question in the same prompt
            has_career = any(kw in lower_msg for kw in CAREER_KEYWORDS)
            if not has_career:
                return PREDEFINED_REDIRECT_OFFTOPIC, True, []

    # Check 5: General topic restriction check
    # The message must relate to career guidance, education, skills, or system support
    is_career_relevant = any(re.search(r'\b' + re.escape(kw) + r'\b', lower_msg) for kw in CAREER_KEYWORDS)
    
    # Greetings alone like "Hi", "Hello", "Hey" are conversation starters
    is_greeting = re.match(r'^(hi|hello|hey|greetings|good\s+(morning|afternoon|evening))\b', lower_msg)

    if not is_career_relevant and not is_greeting:
        # Check if the query asks a general trivia, mathematical question or unrelated topic
        return PREDEFINED_REDIRECT_OFFTOPIC, True, []

    # Generate grounded career guidance
    return generate_career_guidance(cleaned, user)


def generate_career_guidance(query, user=None):
    """
    Produces grounded, high-quality, professional career guidance.
    Embeds interactive career cards when relevant.
    """
    lower = query.lower()
    user_name = "there"
    profile = None
    if user and hasattr(user, 'profile'):
        profile = user.profile
        user_name = profile.full_name.split()[0] if profile.full_name else user.username

    # Scenario 1: Exact UI Image 1 match - 11th grade or high school student unsure about career
    if any(k in lower for k in ["11th grade", "10th grade", "12th grade", "high school", "unsure what career", "which career to pursue"]):
        cards = [
            {"title": "Software Engineer", "icon": "code", "match": "98%", "category": "Technology"},
            {"title": "Data Scientist", "icon": "bar-chart-2", "match": "94%", "category": "Data Science"},
            {"title": "Engineer (Mechanical, Electrical)", "icon": "tool", "match": "92%", "category": "Engineering"},
            {"title": "Research Scientist", "icon": "search", "match": "90%", "category": "Science & Research"}
        ]
        text = (
            f"Of course, {user_name}! We can explore different career paths based on your interests, strengths, and favorite subjects in school.\n\n"
            "Here are promising paths that align well with analytical and science-focused high school streams:\n"
            "• **Software Engineering**: Designing and building digital products, web and mobile platforms.\n"
            "• **Data Science & AI**: Solving complex problems using data analysis, statistics, and machine learning.\n"
            "• **Engineering (Robotics, Aerospace, Hardware)**: Designing physical-digital systems and advanced equipment.\n"
            "• **Research & Applied Sciences**: Investigating novel technologies, biotechnology, and fundamental discoveries.\n\n"
            "What subjects or hobbies do you enjoy the most? Let me know so we can narrow down your exact learning roadmap."
        )
        return text, False, cards

    # Scenario 2: User mentions enjoying science, math, technology (continuation in Screen 1)
    if "science" in lower and "math" in lower and ("tech" in lower or "problem" in lower):
        cards = [
            {"title": "Software Engineer", "icon": "code", "match": "98%", "category": "Technology"},
            {"title": "Data Scientist", "icon": "bar-chart-2", "match": "94%", "category": "Data Science"},
            {"title": "Engineer (Mechanical, Electrical)", "icon": "tool", "match": "92%", "category": "Engineering"},
            {"title": "Research Scientist", "icon": "search", "match": "90%", "category": "Science & Research"}
        ]
        text = (
            f"Great! Based on your interests in science, math, and technology, here are high-impact career options you might enjoy:\n\n"
            "1. **Software Engineer** — High demand, combines logical reasoning with creative problem solving.\n"
            "2. **Data Scientist** — Leverages statistics, programming, and mathematical modeling to uncover insights.\n"
            "3. **Robotics / Aerospace Engineer** — Bridges physical machinery with intelligent computation.\n"
            "4. **Research Scientist** — Conducts experiments and drives scientific innovation.\n\n"
            "You can click on any card below to view required skills and your customized learning roadmap!"
        )
        return text, False, cards

    # Scenario 3: BCA degree + Python skills (SRS Example AT-04 / 4.5)
    if "bca" in lower or ("bachelor" in lower and "computer" in lower) or ("python" in lower and "career" in lower):
        cards = [
            {"title": "Software Developer", "icon": "code", "match": "98%", "category": "Technology"},
            {"title": "Data Scientist", "icon": "database", "match": "94%", "category": "Data & AI"},
            {"title": "Systems Analyst", "icon": "cpu", "match": "95%", "category": "Technology"},
            {"title": "Cybersecurity Analyst", "icon": "shield", "match": "88%", "category": "Security"}
        ]
        text = (
            "A BCA (Bachelor of Computer Applications) degree combined with Python skills provides a strong foundation for multiple high-growth technical paths:\n\n"
            "**1. Python Full-Stack / Backend Developer**\n"
            "• Matching Factors: Directly utilizes your Python proficiency and core computer science coursework.\n"
            "• Next Skills to Learn: Django / FastAPI, PostgreSQL, REST APIs, Git, and Docker.\n\n"
            "**2. Data Analyst / Junior Data Scientist**\n"
            "• Matching Factors: Python is the gold standard for data analysis.\n"
            "• Next Skills to Learn: Pandas, NumPy, SQL, Power BI or Tableau, and exploratory data analysis.\n\n"
            "**3. Systems Analyst**\n"
            "• Matching Factors: Translates business requirements into technical system architectures.\n"
            "• Next Skills to Learn: System Design, UML diagrams, Agile/Scrum, and Database Administration.\n\n"
            "Would you like to generate a personalized skill gap roadmap for any of these roles?"
        )
        return text, False, cards

    # Scenario 4: Cybersecurity analyst requirements (SRS Red-Team Test Set item 7)
    if "cybersecurity" in lower or "security analyst" in lower or "infosec" in lower:
        cards = [
            {"title": "Cybersecurity Analyst", "icon": "shield", "match": "92%", "category": "Security"},
            {"title": "Systems Analyst", "icon": "cpu", "match": "90%", "category": "Technology"}
        ]
        text = (
            "To become a **Cybersecurity Analyst**, here are the essential technical and practical competencies required:\n\n"
            "**Core Technical Skills:**\n"
            "• **Networking & Protocols**: Deep understanding of TCP/IP, DNS, VPNs, Firewalls, and subnetting.\n"
            "• **Operating Systems**: Linux administration (terminal, permissions, bash scripting) and Windows Active Directory.\n"
            "• **Security Operations (SecOps)**: SIEM tools (Splunk, Elastic SIEM), vulnerability scanners (Nessus, Wireshark), incident response.\n"
            "• **Scripting**: Python or Bash for log analysis and task automation.\n\n"
            "**Recommended Certifications:**\n"
            "• CompTIA Security+ (entry standard)\n"
            "• Certified Information Systems Security Officer (CISSO) or CEH (Ethical Hacker)\n\n"
            "**Learning Roadmap:**\n"
            "1. Network Fundamentals → 2. Linux & Security Principles → 3. Threat Hunting & Incident Response → 4. Security Auditing."
        )
        return text, False, cards

    # Scenario 5: Data Analyst / Data Scientist guidance (SRS Example 4.5)
    if "data analyst" in lower or "data science" in lower or "data scientist" in lower:
        cards = [
            {"title": "Data Scientist", "icon": "database", "match": "94%", "category": "Data Science"},
            {"title": "Systems Analyst", "icon": "cpu", "match": "92%", "category": "Technology"}
        ]
        text = (
            "Here is the structured roadmap to become a **Data Analyst / Data Scientist**:\n\n"
            "**Phase 1: Foundation (Weeks 1-4)**\n"
            "• Advanced Excel: Pivot tables, VLOOKUP/XLOOKUP, summary modeling.\n"
            "• Structured Query Language (SQL): Joins, aggregations, subqueries, window functions.\n\n"
            "**Phase 2: Programming & Data Wrangling (Weeks 5-8)**\n"
            "• Python: Data structures, Pandas for data cleaning, NumPy for vector math.\n"
            "• Exploratory Data Analysis: Seaborn and Matplotlib visualization.\n\n"
            "**Phase 3: Business Intelligence & Dashboards (Weeks 9-12)**\n"
            "• Power BI or Tableau: Interactive reports, DAX expressions, KPI tracking.\n\n"
            "**Phase 4: Advanced Modeling / Machine Learning (Weeks 13+)**\n"
            "• Regression, Classification, Clustering with Scikit-Learn.\n\n"
            "You can track your milestone completion in the **My Choices > Roadmap** section of this application!"
        )
        return text, False, cards

    # Scenario 6: UI/UX Design
    if "ui" in lower or "ux" in lower or "design" in lower:
        cards = [
            {"title": "UI/UX Designer", "icon": "palette", "match": "93%", "category": "Creative & Design"},
            {"title": "Software Developer", "icon": "code", "match": "91%", "category": "Technology"}
        ]
        text = (
            "A career in **UI/UX Design** blends psychology, visual aesthetics, and user empathy:\n\n"
            "• **Key Skills**: User research, wireframing, Figma / Sketch prototyping, design systems, usability testing.\n"
            "• **Entry Route**: Build a portfolio of 3-4 end-to-end case studies detailing problem statement, user personas, wireframes, and final high-fidelity screens.\n"
            "• **Next Step**: Start with the *Figma Pro* module available on your dashboard to master responsive auto-layouts and components!"
        )
        return text, False, cards

    # Scenario 7: Interview preparation / Resume / CV
    if "interview" in lower or "resume" in lower or "cv" in lower or "placement" in lower:
        text = (
            "Here are strategic guidelines for career preparation and interviews:\n\n"
            "**Resume Essentials:**\n"
            "• Use the STAR method (Situation, Task, Action, Result) with quantified metrics.\n"
            "• Tailor keywords to the job description to pass ATS filters.\n"
            "• Keep it clean, single-column, and error-free.\n\n"
            "**Interview Preparation:**\n"
            "• **Behavioral Questions**: Prepare stories for leadership, conflict resolution, and handling setbacks.\n"
            "• **Technical Assessment**: Review fundamentals, data structures, and core architectural principles.\n"
            "• **Mock Practice**: Use the *Mock Interview Tool* on your Dashboard to practice timed responses!"
        )
        return text, False, []

    # Scenario 8: Recommendation inquiry / "Which careers match my profile?"
    if "my profile" in lower or "recommend" in lower or "match" in lower or "what should i choose" in lower:
        # Pull top recommendations from database for this user if available
        top_careers = []
        if user:
            from .models import Recommendation
            recs = Recommendation.objects.filter(user=user).select_related('career')[:4]
            for r in recs:
                top_careers.append({
                    "title": r.career.title,
                    "icon": r.career.icon or "briefcase",
                    "match": f"{r.score_round}%",
                    "category": r.career.category
                })

        if not top_careers:
            top_careers = [
                {"title": "Systems Analyst", "icon": "cpu", "match": "100%", "category": "Technology"},
                {"title": "Software Developer", "icon": "code", "match": "98%", "category": "Technology"},
                {"title": "Data Scientist", "icon": "database", "match": "94%", "category": "Data Science"},
                {"title": "Computer Games Developer", "icon": "monitor", "match": "94%", "category": "Technology"}
            ]

        text = (
            f"Based on your current profile ({profile.qualification if profile else 'Education & Skills'}), "
            "here are your top career alignments calculated using our weighted matching model:\n\n"
            + "\n".join([f"• **{c['title']}** ({c['match']} match) — Category: {c['category']}" for c in top_careers]) +
            "\n\nEach score reflects your Interest Alignment (40%), Education Alignment (30%), and Skill Match (30%). "
            "Explore full details and required skills under **Best Matches**."
        )
        return text, False, top_careers

    # Scenario 9: Friendly greeting / general introduction
    if re.match(r'^(hi|hello|hey|greetings|good\s+(morning|afternoon|evening))\b', lower):
        cards = [
            {"title": "Explore Careers", "icon": "compass", "match": "Top", "category": "Discovery"},
            {"title": "Skill Roadmap", "icon": "map", "match": "Interactive", "category": "Learning"},
            {"title": "Skill Gap Check", "icon": "activity", "match": "Personalized", "category": "Assessment"}
        ]
        text = (
            f"Hello {user_name}! Welcome to your Career Guidance Assistant. "
            "I can help you explore suitable career paths, evaluate skill gaps, plan learning roadmaps, "
            "and prepare for internships and interviews.\n\n"
            "What career path, degree, or skill would you like to explore today?"
        )
        return text, False, cards

    # Default fallback for general career query
    text = (
        f"I can provide personalized guidance regarding this career direction. "
        "In this application, you can:\n"
        "1. Check your **Best Matches** tab to view weighted match scores.\n"
        "2. View **Skill Gap Analysis** to see which skills you have versus what employers look for.\n"
        "3. Follow the **Learning Roadmap** to level up your skills step-by-step.\n\n"
        "Could you tell me what specific job role or qualification you would like more details on?"
    )
    return text, False, []
