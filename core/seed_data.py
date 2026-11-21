"""
Seed data script to populate comprehensive career catalogue, skills, interests,
roadmaps, and initial demo profile (Rahul Sharma) matching the 4 UI screenshots.
"""

from django.contrib.auth.models import User
from core.models import (
    UserProfile, Interest, UserInterest, Skill, UserSkill,
    Career, CareerSkill, Recommendation, SavedCareer,
    CareerRoadmap, RoadmapMilestone, UserMilestoneProgress,
    AssistantConversation, AssistantMessage, MockInterview
)
from core.recommendation_engine import generate_recommendations_for_user

def populate_database():
    print("Beginning database population...")

    # 1. Create or get Demo User (Rahul)
    user, created = User.objects.get_or_create(username='rahul', defaults={'email': 'rahul@example.com'})
    user.set_password('password123')
    user.save()

    # Create Admin User
    admin_user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True})
    admin_user.set_password('admin123')
    admin_user.save()

    # User Profile matching UI Screen 1, 2, 4
    profile, _ = UserProfile.objects.update_or_create(
        user=user,
        defaults={
            'full_name': 'Rahul Sharma',
            'headline': 'High School STEM Student | Aspiring Tech Innovator',
            'education_level': 'school',
            'qualification': '11th Grade (Science & Mathematics)',
            'institution': 'St. Xavier International School',
            'specialization': 'Physics, Chemistry, Math & Computer Science',
            'graduation_year': 2026,
            'experience_level': 'Beginner/Student',
            'profile_completed': True,
            'xp_points': 2840,
            'xp_needed': 3200,
            'level': 12,
            'streak_days': 7,
            'total_points': 15420,
            'lessons_completed': 46,
            'hours_spent': 127,
            'assessment_date_str': 'Monday, 11 AM',
            'avatar': 'avatar-rahul',
            'psychometric_score': 80,
            'college_shortlist_count': 50,
            'roadmap_progress': 30,
        }
    )

    # 2. Populate 10 SRS Interest Categories (FR-11)
    interests_data = [
        ("Technology and programming", "Designing software, coding apps, cloud computing and cyber systems.", "laptop"),
        ("Business, entrepreneurship and management", "Launching startups, managing products, leadership and operations.", "briefcase"),
        ("Creative design, arts and content creation", "Visual UI/UX design, 3D modeling, digital media and aesthetics.", "palette"),
        ("Healthcare and life sciences", "Medicine, bioinformatics, biotechnology and public health.", "heart-pulse"),
        ("Teaching, education and research", "Academia, pedagogy, curriculum design and scientific inquiry.", "book-open"),
        ("Finance, accounting and banking", "Financial modeling, investment analysis, economics and wealth management.", "dollar-sign"),
        ("Engineering and manufacturing", "Robotics, aerospace, civil infrastructure and mechanical systems.", "cpu"),
        ("Media, communication and marketing", "Digital journalism, content strategy, public relations and branding.", "radio"),
        ("Government and public services", "Policy analysis, civic governance, public administration and defense.", "landmark"),
        ("Science, environment and research", "Astrophysics, environmental sustainability, climate and laboratory research.", "flask-conical"),
    ]

    interest_objs = {}
    for name, desc, icon in interests_data:
        obj, _ = Interest.objects.update_or_create(category_name=name, defaults={'description': desc, 'icon': icon})
        interest_objs[name] = obj

    # Assign user interests
    UserInterest.objects.update_or_create(user=user, interest=interest_objs["Technology and programming"], defaults={'preference_strength': 5})
    UserInterest.objects.update_or_create(user=user, interest=interest_objs["Science, environment and research"], defaults={'preference_strength': 4})
    UserInterest.objects.update_or_create(user=user, interest=interest_objs["Engineering and manufacturing"], defaults={'preference_strength': 4})
    UserInterest.objects.update_or_create(user=user, interest=interest_objs["Creative design, arts and content creation"], defaults={'preference_strength': 3})

    # 3. Populate Standardized Skills
    skills_data = [
        ("Python", "technical", "Software"),
        ("JavaScript", "technical", "Software"),
        ("HTML & CSS", "technical", "Software"),
        ("React", "technical", "Software"),
        ("Node.js & Express", "technical", "Software"),
        ("SQL & Relational Databases", "technical", "Data"),
        ("Data Structures & Algorithms", "technical", "Software"),
        ("Git & GitHub", "technical", "Software"),
        ("Docker & Containers", "technical", "Software"),
        ("Cloud Computing (AWS/GCP)", "technical", "Software"),
        ("Data Analysis & Pandas", "technical", "Data"),
        ("Machine Learning", "technical", "Data"),
        ("Mathematics & Statistics", "technical", "Data"),
        ("UI/UX Design & Figma", "technical", "Design"),
        ("User Research & Wireframing", "technical", "Design"),
        ("Linux & Bash Scripting", "technical", "Software"),
        ("Cybersecurity Fundamentals", "technical", "Security"),
        ("Network Protocols (TCP/IP)", "technical", "Security"),
        ("Game Engine (Unity/Unreal)", "technical", "Software"),
        ("C++ Programming", "technical", "Software"),
        ("Robotics & Embedded Systems", "technical", "Engineering"),
        ("Aerodynamics & CAD Modeling", "technical", "Engineering"),
        ("Financial Modeling & Excel", "technical", "Finance"),
        ("Corporate Governance & Compliance", "technical", "Finance"),
        ("System Architecture & Design", "technical", "Software"),
        ("Problem Solving", "soft", "General"),
        ("Critical Thinking", "soft", "General"),
        ("Communication", "soft", "General"),
        ("Team Collaboration", "soft", "General"),
        ("Project Management", "soft", "Management"),
        ("Time Management", "soft", "General"),
    ]

    skill_objs = {}
    for name, cat, domain in skills_data:
        obj, _ = Skill.objects.update_or_create(name=name, defaults={'category': cat, 'domain': domain})
        skill_objs[name] = obj

    # Assign User Skills for Rahul
    user_skills_data = [
        ("Python", "Intermediate"),
        ("HTML & CSS", "Advanced"),
        ("JavaScript", "Intermediate"),
        ("React", "Intermediate"),
        ("Node.js & Express", "Beginner"),
        ("SQL & Relational Databases", "Intermediate"),
        ("Data Structures & Algorithms", "Beginner"),
        ("Git & GitHub", "Intermediate"),
        ("Mathematics & Statistics", "Advanced"),
        ("Problem Solving", "Advanced"),
        ("UI/UX Design & Figma", "Beginner"),
    ]
    for s_name, prof in user_skills_data:
        UserSkill.objects.update_or_create(user=user, skill=skill_objs[s_name], defaults={'proficiency': prof})

    # 4. Populate Careers (from UI Screen 3 & SRS)
    careers_data = [
        {
            "title": "Systems Analyst",
            "slug": "systems-analyst",
            "category": "Technology",
            "overview": "Systems analysts evaluate existing computer systems, design IT architectures, and translate user requirements into technical blueprints.",
            "responsibilities": "Analyze business processes and software architectures; design scalable specifications; collaborate with programmers and stakeholders; run system compatibility testing.",
            "work_environment": "Tech firms, financial institutions, consulting agencies or hybrid remote.",
            "eligibility_education": "undergraduate",
            "preferred_education": "Bachelor's in Computer Science, Information Systems, or STEM field",
            "entry_routes": "Undergraduate degree in CS/IT, or progression from Software Developer.",
            "salary_range": "$92,000 - $145,000 / ₹11,00,000 - ₹28,00,000",
            "salary_source": "Glassdoor & BLS 2024",
            "job_outlook": "+12% (Steady growth)",
            "related_careers_count": 2,
            "icon": "cpu",
            "image_url": "https://images.unsplash.com/photo-1551434678-e076c223a692?w=600&auto=format&fit=crop&q=80",
            "certifications": "CBAP (Certified Business Analysis Professional), TOGAF, AWS Solutions Architect",
            "required_skills": [
                ("System Architecture & Design", "Intermediate", "Essential"),
                ("SQL & Relational Databases", "Intermediate", "Essential"),
                ("Problem Solving", "Advanced", "Essential"),
                ("Communication", "Intermediate", "Essential"),
                ("Project Management", "Intermediate", "Preferred"),
            ]
        },
        {
            "title": "Software Developer",
            "slug": "software-developer",
            "category": "Technology",
            "overview": "Software developers design, write, test, and maintain code for computer applications, web systems, and mobile applications.",
            "responsibilities": "Write clean and efficient code; build REST APIs and user interfaces; debug software flaws; participate in code reviews and agile sprints.",
            "work_environment": "Tech startups, enterprises, remote and collaborative software studios.",
            "eligibility_education": "undergraduate",
            "preferred_education": "Bachelor's in Computer Science, Software Engineering, BCA, or equivalent experience",
            "entry_routes": "B.Tech/BCA degree, coding bootcamps with portfolio, or open-source contributions.",
            "salary_range": "$95,000 - $160,000 / ₹10,00,000 - ₹32,00,000",
            "salary_source": "BLS & Levels.fyi 2024",
            "job_outlook": "+25% (Much faster than average)",
            "related_careers_count": 3,
            "icon": "code",
            "image_url": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=600&auto=format&fit=crop&q=80",
            "certifications": "AWS Certified Developer, Meta Frontend/Backend Professional Certificate",
            "required_skills": [
                ("Python", "Intermediate", "Essential"),
                ("JavaScript", "Intermediate", "Essential"),
                ("HTML & CSS", "Intermediate", "Essential"),
                ("React", "Intermediate", "Preferred"),
                ("Node.js & Express", "Intermediate", "Preferred"),
                ("Data Structures & Algorithms", "Intermediate", "Essential"),
                ("Git & GitHub", "Intermediate", "Essential"),
                ("Problem Solving", "Advanced", "Essential"),
            ]
        },
        {
            "title": "Computer Games Developer",
            "slug": "computer-games-developer",
            "category": "Technology & Entertainment",
            "overview": "Game developers combine artistic vision with computer programming to produce video games across PC, console, mobile, and VR platforms.",
            "responsibilities": "Program gameplay mechanics and physics simulations; integrate audio, 2D/3D assets; optimize rendering performance; implement multiplayer networking.",
            "work_environment": "Game studios, indie production teams, creative technology labs.",
            "eligibility_education": "undergraduate",
            "preferred_education": "Degree in Computer Science, Game Design & Programming, or Software Engineering",
            "entry_routes": "Computer Science degree, indie game jams, building Unity/Unreal prototypes.",
            "salary_range": "$82,000 - $138,000 / ₹8,00,000 - ₹25,00,000",
            "salary_source": "Game Developer Salary Survey 2024",
            "job_outlook": "+16% (Faster than average)",
            "related_careers_count": 2,
            "icon": "monitor",
            "image_url": "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=600&auto=format&fit=crop&q=80",
            "certifications": "Unity Certified Programmer, Unreal Engine Specialist",
            "required_skills": [
                ("Game Engine (Unity/Unreal)", "Intermediate", "Essential"),
                ("C++ Programming", "Intermediate", "Essential"),
                ("Data Structures & Algorithms", "Intermediate", "Essential"),
                ("Mathematics & Statistics", "Intermediate", "Preferred"),
                ("Problem Solving", "Intermediate", "Essential"),
            ]
        },
        {
            "title": "Data Scientist",
            "slug": "data-scientist",
            "category": "Data Science & AI",
            "overview": "Data scientists extract actionable knowledge from raw data using machine learning algorithms, statistical modeling, and data pipelines.",
            "responsibilities": "Clean and preprocess large datasets; construct predictive ML models; communicate quantitative findings to leadership via visualizations.",
            "work_environment": "Tech enterprises, fintech, healthcare research, e-commerce.",
            "eligibility_education": "undergraduate",
            "preferred_education": "Bachelor's or Master's in Data Science, Statistics, Mathematics, or Computer Science",
            "entry_routes": "STEM degree with Python and statistics portfolio; Kaggle competitions.",
            "salary_range": "$105,000 - $175,000 / ₹12,00,000 - ₹35,00,000",
            "salary_source": "Glassdoor & LinkedIn Jobs 2024",
            "job_outlook": "+35% (Extremely high demand)",
            "related_careers_count": 2,
            "icon": "database",
            "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&auto=format&fit=crop&q=80",
            "certifications": "TensorFlow Developer Certificate, Google Professional Data Engineer",
            "required_skills": [
                ("Python", "Advanced", "Essential"),
                ("Mathematics & Statistics", "Advanced", "Essential"),
                ("SQL & Relational Databases", "Intermediate", "Essential"),
                ("Data Analysis & Pandas", "Advanced", "Essential"),
                ("Machine Learning", "Intermediate", "Essential"),
                ("Critical Thinking", "Advanced", "Essential"),
            ]
        },
        {
            "title": "Robotics Engineer",
            "slug": "robotics-engineer",
            "category": "Engineering",
            "overview": "Robotics engineers design, build, and program autonomous machines and robotic systems for manufacturing, healthcare, space, and logistics.",
            "responsibilities": "Design mechanical actuators and sensory arrays; write embedded firmware; integrate computer vision and kinematics control loops.",
            "work_environment": "R&D facilities, manufacturing plants, autonomous vehicle test tracks.",
            "eligibility_education": "undergraduate",
            "preferred_education": "B.Tech/B.E in Robotics, Mechatronics, Electrical, or Mechanical Engineering",
            "entry_routes": "Engineering degree, collegiate robotics clubs, ROS (Robot Operating System) projects.",
            "salary_range": "$98,000 - $155,000 / ₹10,00,000 - ₹30,00,000",
            "salary_source": "IEEE Robotics & BLS 2024",
            "job_outlook": "+18% (Faster than average)",
            "related_careers_count": 2,
            "icon": "cpu",
            "image_url": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=600&auto=format&fit=crop&q=80",
            "certifications": "ROS Certified Developer, Certified Robotics Systems Professional",
            "required_skills": [
                ("Robotics & Embedded Systems", "Intermediate", "Essential"),
                ("C++ Programming", "Intermediate", "Essential"),
                ("Python", "Intermediate", "Preferred"),
                ("Mathematics & Statistics", "Advanced", "Essential"),
                ("Problem Solving", "Advanced", "Essential"),
            ]
        },
        {
            "title": "Aerospace Engineer",
            "slug": "aerospace-engineer",
            "category": "Engineering",
            "overview": "Aerospace engineers design, simulate, and test aircraft, spacecraft, satellites, and missile propulsion systems.",
            "responsibilities": "Perform aerodynamic CFD simulations; analyze structural stress under high thermal and g-force loads; ensure aerospace safety compliance.",
            "work_environment": "Aviation corporations, space agencies (NASA/ISRO/ESA), defense contractors.",
            "eligibility_education": "undergraduate",
            "preferred_education": "Bachelor's or Master's in Aerospace, Aeronautical, or Mechanical Engineering",
            "entry_routes": "Specialized B.Tech Aerospace degree, internships at aerospace firms.",
            "salary_range": "$102,000 - $168,000 / ₹11,00,000 - ₹32,00,000",
            "salary_source": "AIAA & BLS 2024",
            "job_outlook": "+8% (Steady demand)",
            "related_careers_count": 1,
            "icon": "send",
            "image_url": "https://images.unsplash.com/photo-1517976487507-5b3b4a4d4a02?w=600&auto=format&fit=crop&q=80",
            "certifications": "FE/PE Exam, Certified CAD Professional (Siemens NX / CATIA)",
            "required_skills": [
                ("Aerodynamics & CAD Modeling", "Intermediate", "Essential"),
                ("Mathematics & Statistics", "Advanced", "Essential"),
                ("Problem Solving", "Advanced", "Essential"),
                ("Critical Thinking", "Advanced", "Essential"),
            ]
        },
        {
            "title": "Investment Analyst",
            "slug": "investment-analyst",
            "category": "Finance & Banking",
            "overview": "Investment analysts evaluate financial assets, market trends, and corporate financial statements to guide investment decisions.",
            "responsibilities": "Build discounted cash flow (DCF) models; write equity research memos; evaluate financial risks; advise portfolio managers.",
            "work_environment": "Investment banks, private equity firms, asset management funds.",
            "eligibility_education": "undergraduate",
            "preferred_education": "Degree in Finance, Economics, Commerce, or quantitative field (Math/Stats)",
            "entry_routes": "Finance/Economics degree, CFA charter track, investment banking analyst internships.",
            "salary_range": "$90,000 - $165,000 / ₹12,00,000 - ₹34,00,000",
            "salary_source": "Wall Street Oasis & Glassdoor 2024",
            "job_outlook": "+10% (Average)",
            "related_careers_count": 1,
            "icon": "trending-up",
            "image_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&auto=format&fit=crop&q=80",
            "certifications": "CFA (Chartered Financial Analyst) Level 1/2, Financial Modeling Certification (FMVA)",
            "required_skills": [
                ("Financial Modeling & Excel", "Advanced", "Essential"),
                ("Mathematics & Statistics", "Intermediate", "Essential"),
                ("Critical Thinking", "Advanced", "Essential"),
                ("Communication", "Advanced", "Essential"),
            ]
        },
        {
            "title": "Company (Chartered) Secretary",
            "slug": "chartered-secretary",
            "category": "Business & Governance",
            "overview": "Chartered secretaries ensure companies comply with statutory and regulatory legal requirements, corporate governance, and board procedures.",
            "responsibilities": "Coordinate board meetings; advise directors on corporate laws; file statutory annual returns; audit corporate disclosures.",
            "work_environment": "Corporate headquarters, legal compliance firms, multinational enterprises.",
            "eligibility_education": "undergraduate",
            "preferred_education": "Professional qualification from ICSI/CGI or Bachelor's in Law/Commerce",
            "entry_routes": "Professional CS examination stages (Foundation, Executive, Professional).",
            "salary_range": "$78,000 - $130,000 / ₹8,00,000 - ₹22,00,000",
            "salary_source": "Institute of Chartered Secretaries & PayScale 2024",
            "job_outlook": "+9% (Steady)",
            "related_careers_count": 1,
            "icon": "file-text",
            "image_url": "https://images.unsplash.com/photo-1450133064473-71024230f91b?w=600&auto=format&fit=crop&q=80",
            "certifications": "ACIS/FCIS, Chartered Governance Institute Fellow",
            "required_skills": [
                ("Corporate Governance & Compliance", "Advanced", "Essential"),
                ("Communication", "Advanced", "Essential"),
                ("Critical Thinking", "Intermediate", "Essential"),
                ("Project Management", "Intermediate", "Preferred"),
            ]
        },
        {
            "title": "UI/UX Designer",
            "slug": "ui-ux-designer",
            "category": "Creative & Design",
            "overview": "UI/UX designers craft intuitive, accessible, and delightful digital user journeys for mobile apps, web applications, and enterprise software.",
            "responsibilities": "Conduct user interviews; build wireframes and interactive Figma prototypes; create design systems; collaborate with frontend developers.",
            "work_environment": "Design agencies, tech product companies, creative studios.",
            "eligibility_education": "diploma",
            "preferred_education": "Degree in Human-Computer Interaction (HCI), Graphic Design, or portfolio track",
            "entry_routes": "Design bootcamp, portfolio of real-world redesigns and prototypes.",
            "salary_range": "$80,000 - $140,000 / ₹8,00,000 - ₹26,00,000",
            "salary_source": "Dribbble & Glassdoor 2024",
            "job_outlook": "+19% (Faster than average)",
            "related_careers_count": 2,
            "icon": "palette",
            "image_url": "https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?w=600&auto=format&fit=crop&q=80",
            "certifications": "Google UX Design Professional Certificate, Nielsen Norman UX Master",
            "required_skills": [
                ("UI/UX Design & Figma", "Advanced", "Essential"),
                ("User Research & Wireframing", "Advanced", "Essential"),
                ("HTML & CSS", "Beginner", "Preferred"),
                ("Communication", "Advanced", "Essential"),
                ("Problem Solving", "Intermediate", "Essential"),
            ]
        },
        {
            "title": "Cybersecurity Analyst",
            "slug": "cybersecurity-analyst",
            "category": "Technology & Security",
            "overview": "Cybersecurity analysts protect computer systems and networks from cyber threats, unauthorized access, ransomware, and vulnerabilities.",
            "responsibilities": "Monitor network traffic for anomalies; conduct vulnerability assessments; deploy firewalls and encryption; respond to security incidents.",
            "work_environment": "Security operations centers (SOC), enterprise IT, defense, cloud providers.",
            "eligibility_education": "undergraduate",
            "preferred_education": "Bachelor's in Cybersecurity, Computer Science, or Information Technology",
            "entry_routes": "IT degree, Security+ certification, Capture The Flag (CTF) competitions.",
            "salary_range": "$95,000 - $150,000 / ₹9,00,000 - ₹28,00,000",
            "salary_source": "CyberSeek & BLS 2024",
            "job_outlook": "+32% (Much faster than average)",
            "related_careers_count": 2,
            "icon": "shield",
            "image_url": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=600&auto=format&fit=crop&q=80",
            "certifications": "CompTIA Security+, CEH (Certified Ethical Hacker), CISSP",
            "required_skills": [
                ("Cybersecurity Fundamentals", "Advanced", "Essential"),
                ("Network Protocols (TCP/IP)", "Advanced", "Essential"),
                ("Linux & Bash Scripting", "Intermediate", "Essential"),
                ("Python", "Intermediate", "Preferred"),
                ("Problem Solving", "Advanced", "Essential"),
            ]
        }
    ]

    career_objs = {}
    for c_data in careers_data:
        req_skills = c_data.pop("required_skills")
        career_obj, _ = Career.objects.update_or_create(
            slug=c_data["slug"],
            defaults=c_data
        )
        career_objs[c_data["slug"]] = career_obj

        # Assign required skills
        for s_name, req_prof, imp in req_skills:
            if s_name in skill_objs:
                CareerSkill.objects.update_or_create(
                    career=career_obj,
                    skill=skill_objs[s_name],
                    defaults={
                        'required_proficiency': req_prof,
                        'importance': imp
                    }
                )

    # 5. Populate Learning Roadmap for Full-Stack Development (UI Screen 2 Ascento style)
    sw_career = career_objs.get("software-developer")
    if sw_career:
        roadmap, _ = CareerRoadmap.objects.update_or_create(
            career=sw_career,
            defaults={
                'title': 'Master Full-Stack Development',
                'subtitle': 'Complete journey from beginner to senior developer',
                'total_xp': 4500,
                'estimated_hours': 350
            }
        )

        milestones_data = [
            (1, "HTML & CSS Fundamentals", "Master the building blocks of web development, semantic markup, responsive layout, Flexbox and CSS Grid.", "Beginner", 200, 40, "Completed", 100, "2024-01-15", "FreeCodeCamp & MDN", "https://developer.mozilla.org"),
            (2, "JavaScript Essentials", "Learn programming fundamentals, DOM manipulation, ES6+ features, closures, and asynchronous programming.", "Beginner", 350, 60, "Completed", 100, "2024-02-10", "JavaScript.info", "https://javascript.info"),
            (3, "React Framework", "Build dynamic, component-driven user interfaces with modern React, hooks, state management, and routing.", "Intermediate", 500, 80, "Completed", 100, "2024-03-20", "Official React Docs", "https://react.dev"),
            (4, "Node.js & Express", "Create scalable server-side applications, RESTful APIs, middleware architecture, and JWT authentication.", "Intermediate", 450, 70, "In Progress", 65, None, "Node.js Guides", "https://nodejs.org"),
            (5, "Database Design with SQL & PostgreSQL", "Model relational schemas, write performant queries, indexes, joins, and transactions.", "Intermediate", 400, 50, "Not Started", 0, None, "PostgreSQL Tutorial", "https://www.postgresqltutorial.com"),
            (6, "Full-Stack Project: SaaS Application", "Integrate frontend React with backend API, payments, background jobs, and cloud deployment.", "Intermediate", 600, 90, "Not Started", 0, None, "FullStack Open", "https://fullstackopen.com"),
            (7, "DevOps, Docker & CI/CD", "Containerize services with Docker, set up automated GitHub Actions deployment pipelines.", "Advanced", 500, 60, "Not Started", 0, None, "Docker Docs", "https://docs.docker.com"),
            (8, "System Architecture & Senior Principles", "Master microservices, caching with Redis, load balancing, security hardening and observability.", "Advanced", 700, 80, "Not Started", 0, None, "System Design Primer", "https://github.com/donnemartin/system-design-primer")
        ]

        for order, title, desc, lvl, xp, hrs, status, pct, comp_date, provider, url in milestones_data:
            ms, _ = RoadmapMilestone.objects.update_or_create(
                roadmap=roadmap,
                order=order,
                defaults={
                    'title': title,
                    'description': desc,
                    'level': lvl,
                    'xp_reward': xp,
                    'estimated_hours': hrs,
                    'resource_provider': provider,
                    'resource_url': url,
                }
            )

            status_val = 'completed' if status == 'Completed' else ('in_progress' if status == 'In Progress' else 'not_started')
            UserMilestoneProgress.objects.update_or_create(
                user=user,
                milestone=ms,
                defaults={
                    'status': status_val,
                    'progress_percent': pct,
                    'completed_date': comp_date
                }
            )

    # 6. Populate Saved Careers for Rahul (Favourites)
    for c_slug in ["systems-analyst", "software-developer", "data-scientist"]:
        if c_slug in career_objs:
            SavedCareer.objects.update_or_create(user=user, career=career_objs[c_slug], defaults={'is_binned': False})

    # 7. Preload Chat Messages matching Screen 1 (CareerWithinU)
    convo, _ = AssistantConversation.objects.update_or_create(
        user=user,
        defaults={'title': 'Rahul Career Guidance'}
    )
    if convo.messages.count() == 0:
        m1 = AssistantMessage.objects.create(
            conversation=convo,
            sender='user',
            text="Hi! I'm in 11th grade and I'm not sure what career to pursue. Can you help me?"
        )
        m2 = AssistantMessage.objects.create(
            conversation=convo,
            sender='assistant',
            text="Of course, Rahul! We can explore different career paths based on your interests, strengths, and favorite subjects in school.\n\nLet's start by knowing your interests. What subjects, hobbies, or activities do you enjoy the most?"
        )
        m3 = AssistantMessage.objects.create(
            conversation=convo,
            sender='user',
            text="I enjoy science and math. I'm also interested in technology and solving real-world problems."
        )
        m4 = AssistantMessage.objects.create(
            conversation=convo,
            sender='assistant',
            text="Great! Based on your interests in science, math, and technology, here are a few career options you might enjoy:"
        )
        m4.set_cards([
            {"title": "Software Engineer", "icon": "code", "match": "98%", "category": "Technology"},
            {"title": "Data Scientist", "icon": "bar-chart-2", "match": "94%", "category": "Data Science"},
            {"title": "Engineer (Mechanical, Electrical)", "icon": "tool", "match": "92%", "category": "Engineering"},
            {"title": "Research Scientist", "icon": "search", "match": "90%", "category": "Science & Research"}
        ])
        m4.save()

    # 8. Create Mock Interview
    MockInterview.objects.update_or_create(
        user=user,
        role_target='Software Engineer',
        defaults={'scheduled_time': 'Tomorrow, 3:00 PM', 'status': 'Scheduled'}
    )

    # 9. Calculate initial recommendations for Rahul
    generate_recommendations_for_user(user)

    print("Database population completed successfully!")

if __name__ == '__main__':
    populate_database()
