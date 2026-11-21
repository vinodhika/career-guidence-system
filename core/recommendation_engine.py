"""
Recommendation Engine for Career Recommendation System
Implements the SRS weighted matching algorithm:
Match Score = (Interest Fit × 0.40) + (Education Fit × 0.30) + (Skills Fit × 0.30)
Normalized to 0–100 scale with transparent factor explanations (FR-22 to FR-27).
"""

from .models import Career, CareerSkill, Recommendation, UserSkill, UserInterest, Interest

# Configurable weights as per SRS 3.6
WEIGHT_INTEREST = 0.40
WEIGHT_EDUCATION = 0.30
WEIGHT_SKILLS = 0.30

EDUCATION_HIERARCHY = {
    'school': 1,
    'diploma': 2,
    'undergraduate': 3,
    'postgraduate': 4,
    'doctorate': 5,
}

EDUCATION_KEYWORDS = {
    'school': ['school', '10th', '11th', '12th', 'high school', 'secondary', 'hsc', 'matric'],
    'diploma': ['diploma', 'polytechnic', 'associate'],
    'undergraduate': ['bachelor', 'btech', 'b.tech', 'bca', 'bsc', 'b.sc', 'be', 'b.e', 'bcom', 'ba', 'undergraduate', 'degree'],
    'postgraduate': ['master', 'mtech', 'm.tech', 'mca', 'msc', 'm.sc', 'mba', 'postgraduate'],
    'doctorate': ['phd', 'doctorate', 'fellowship', 'researcher'],
}

PROFICIENCY_SCORES = {
    'Beginner': 0.45,
    'Intermediate': 0.75,
    'Advanced': 1.0,
}

def calculate_interest_fit(user, career):
    """
    Computes interest alignment score (0 - 100).
    Evaluates overlap between user's chosen interest categories and career category / domain.
    """
    user_interests = UserInterest.objects.filter(user=user).select_related('interest')
    if not user_interests.exists():
        return 50.0, []  # Default neutral score if not filled

    user_cat_names = [ui.interest.category_name.lower() for ui in user_interests]
    career_cat = career.category.lower()
    career_title = career.title.lower()
    career_overview = career.overview.lower()

    score = 0.0
    matched_interests = []

    for ui in user_interests:
        cat_name = ui.interest.category_name.lower()
        strength = ui.preference_strength / 5.0  # normalize 1-5 to 0.2 - 1.0

        is_direct_match = (
            cat_name in career_cat or 
            career_cat in cat_name or
            any(w in career_title for w in cat_name.split() if len(w) > 3)
        )

        is_domain_match = (
            ('technology' in cat_name and any(k in career_title or k in career_cat for k in ['software', 'developer', 'games', 'systems', 'cloud', 'data', 'robotics', 'ai', 'cyber'])) or
            ('engineering' in cat_name and any(k in career_title or k in career_cat for k in ['engineer', 'robotics', 'aerospace', 'hardware', 'mechanical'])) or
            ('creative' in cat_name and any(k in career_title or k in career_cat for k in ['design', 'ui', 'ux', 'games', 'art', 'content'])) or
            ('finance' in cat_name and any(k in career_title or k in career_cat for k in ['analyst', 'investment', 'finance', 'banking', 'secretary', 'account'])) or
            ('science' in cat_name and any(k in career_title or k in career_cat for k in ['scientist', 'research', 'data', 'aerospace'])) or
            ('business' in cat_name and any(k in career_title or k in career_cat for k in ['product', 'manager', 'business', 'secretary', 'entrepreneur']))
        )

        if is_direct_match:
            score += 65.0 * strength
            matched_interests.append(ui.interest.category_name)
        elif is_domain_match:
            score += 45.0 * strength
            matched_interests.append(ui.interest.category_name)
        elif any(word in career_overview for word in cat_name.split() if len(word) > 4):
            score += 25.0 * strength

    final_score = min(100.0, max(20.0, score))
    return final_score, matched_interests


CAREER_SUBJECT_KEYWORDS = {
    'software-developer': ['computer', 'software', 'bca', 'mca', 'b.tech', 'programming', 'web', 'it', 'coding', 'information technology', 'btech', 'science', 'math', 'pcm'],
    'systems-analyst': ['computer', 'information systems', 'information technology', 'it', 'software', 'bca', 'mca', 'stem', 'systems', 'science', 'math'],
    'data-scientist': ['data science', 'statistics', 'mathematics', 'math', 'computer science', 'analytics', 'data', 'bca', 'mca', 'b.tech', 'science', 'pcm'],
    'computer-games-developer': ['game', 'computer science', 'software', 'graphics', 'multimedia', 'animation', 'bca', 'btech', 'programming', 'science'],
    'robotics-engineer': ['robotics', 'mechatronics', 'mechanical', 'electrical', 'electronics', 'automation', 'hardware', 'embedded', 'engineering', 'science', 'pcm'],
    'aerospace-engineer': ['aerospace', 'aeronautical', 'mechanical', 'aviation', 'space', 'propulsion', 'avionics', 'aircraft', 'engineering', 'science', 'pcm'],
    'investment-analyst': ['finance', 'commerce', 'economics', 'accounting', 'bcom', 'b.com', 'banking', 'investment', 'chartered', 'mba', 'financial', 'cfa', 'business'],
    'chartered-secretary': ['law', 'commerce', 'bcom', 'corporate governance', 'icsi', 'company secretary', 'business', 'management', 'accounting', 'legal'],
    'ui-ux-designer': ['design', 'graphic', 'ui', 'ux', 'human-computer interaction', 'hci', 'interaction design', 'fine arts', 'multimedia', 'visual arts', 'b.des', 'bdes', 'arts', 'media'],
    'cybersecurity-analyst': ['cybersecurity', 'security', 'information security', 'network security', 'computer science', 'information technology', 'it', 'cyber', 'forensics', 'bca', 'btech']
}

def calculate_education_fit(user_profile, career):
    """
    Computes education alignment score (0 - 100).
    Compares user qualification level and specialization with career required and preferred education.
    Evaluates both credential level and domain/field relevance.
    """
    if not user_profile:
        return 50.0, "General educational compatibility"

    user_level = user_profile.education_level
    user_qual = (user_profile.qualification or '').lower()
    user_spec = (user_profile.specialization or '').lower()
    combined_user_text = f"{user_qual} {user_spec}"
    
    career_min_req = career.eligibility_education.lower()
    career_pref = career.preferred_education.lower()
    career_slug = getattr(career, 'slug', '')

    user_rank = EDUCATION_HIERARCHY.get(user_level, 2)
    req_rank = EDUCATION_HIERARCHY.get(career_min_req, 3)

    # 1. Base credential level score (out of 35 pts)
    explanation_parts = []
    if user_rank >= req_rank:
        level_score = 35.0
        explanation_parts.append(f"Meets degree level requirement ({career.eligibility_education})")
    elif user_rank == req_rank - 1:
        level_score = 25.0
        explanation_parts.append(f"Progression pathway from current stage ({user_profile.qualification})")
    else:
        level_score = 15.0
        explanation_parts.append(f"Requires advancement to {career.eligibility_education}")

    # 2. Subject & Domain Relevance Match (out of 65 pts)
    subject_score = 10.0  # baseline if unrelated
    subject_keywords = CAREER_SUBJECT_KEYWORDS.get(career_slug, [])
    
    # Also include words from preferred_education and title
    title_words = [w for w in (career.title + " " + career_pref).lower().replace('/', ' ').replace(',', ' ').split() if len(w) > 3]
    all_target_keywords = set(subject_keywords + title_words)

    matched_keywords = []
    for kw in all_target_keywords:
        if kw in combined_user_text:
            matched_keywords.append(kw)

    if matched_keywords:
        # Strong direct subject match
        match_ratio = min(1.0, len(matched_keywords) / 2.0)
        subject_score = 35.0 + (30.0 * match_ratio)
        explanation_parts.append(f"Strong specialization match with {user_profile.specialization or user_profile.qualification}")
    else:
        # Stream / category broad check
        if any(w in combined_user_text for w in ['science', 'pcm', 'tech', 'math', 'stem']) and career.category in ['Technology', 'Engineering', 'Data Science & AI']:
            subject_score = 42.0
            explanation_parts.append("STEM stream alignment with this technical path")
        elif any(w in combined_user_text for w in ['commerce', 'finance', 'business', 'accounting', 'economics']) and career.category in ['Finance & Banking', 'Business & Governance']:
            subject_score = 45.0
            explanation_parts.append("Commerce/Finance stream alignment with this track")
        elif any(w in combined_user_text for w in ['arts', 'design', 'humanities', 'media']) and career.category in ['Creative & Design']:
            subject_score = 45.0
            explanation_parts.append("Creative/Arts background alignment")
        else:
            explanation_parts.append("Cross-domain transition path")

    final_score = min(100.0, max(20.0, level_score + subject_score))
    return final_score, "; ".join(explanation_parts)


def calculate_skills_fit(user, career):
    """
    Computes skills alignment score (0 - 100).
    Evaluates required vs acquired skills and proficiency depths.
    """
    career_skills = CareerSkill.objects.filter(career=career).select_related('skill')
    if not career_skills.exists():
        return 70.0, [], [], []

    user_skills_qs = UserSkill.objects.filter(user=user).select_related('skill')
    user_skills_map = {us.skill_id: us for us in user_skills_qs}

    total_weight = 0.0
    matched_weight = 0.0
    matched_skills = []
    gap_skills = []
    developing_skills = []

    for cs in career_skills:
        importance_multiplier = 1.0
        if cs.importance == 'Essential':
            importance_multiplier = 1.5
        elif cs.importance == 'Preferred':
            importance_multiplier = 1.2
        elif cs.importance == 'Useful':
            importance_multiplier = 0.9

        total_weight += importance_multiplier

        if cs.skill_id in user_skills_map:
            us = user_skills_map[cs.skill_id]
            user_prof_score = PROFICIENCY_SCORES.get(us.proficiency, 0.5)
            req_prof_score = PROFICIENCY_SCORES.get(cs.required_proficiency, 0.75)

            # Ratio of user proficiency vs required proficiency
            fit_ratio = min(1.0, user_prof_score / req_prof_score)
            matched_weight += (importance_multiplier * fit_ratio)

            if fit_ratio >= 0.9:
                matched_skills.append({
                    'name': cs.skill.name,
                    'user_prof': us.proficiency,
                    'req_prof': cs.required_proficiency,
                    'status': 'Strong Match'
                })
            else:
                developing_skills.append({
                    'name': cs.skill.name,
                    'user_prof': us.proficiency,
                    'req_prof': cs.required_proficiency,
                    'status': 'Needs Improvement'
                })
        else:
            gap_skills.append({
                'name': cs.skill.name,
                'req_prof': cs.required_proficiency,
                'importance': cs.importance,
                'status': 'Missing'
            })

    if total_weight > 0:
        raw_score = (matched_weight / total_weight) * 100.0
    else:
        raw_score = 60.0

    final_score = min(100.0, max(25.0, raw_score))
    return final_score, matched_skills, developing_skills, gap_skills


def generate_recommendations_for_user(user):
    """
    Calculates and persists recommendations for all active careers for the user.
    Uses: Match Score = (Interest Fit × 0.40) + (Education Fit × 0.30) + (Skills Fit × 0.30)
    """
    from .models import UserProfile
    user_profile = UserProfile.objects.filter(user=user).first()
    active_careers = Career.objects.filter(is_active=True)

    recommendations = []

    for career in active_careers:
        interest_fit, matched_interests = calculate_interest_fit(user, career)
        education_fit, edu_explanation = calculate_education_fit(user_profile, career)
        skills_fit, matched_skills, developing_skills, gap_skills = calculate_skills_fit(user, career)

        overall_score = (
            (interest_fit * WEIGHT_INTEREST) +
            (education_fit * WEIGHT_EDUCATION) +
            (skills_fit * WEIGHT_SKILLS)
        )
        overall_score = round(min(100.0, max(15.0, overall_score)), 1)

        # Build transparent explanation breakdown as per SRS FR-24
        explanation_lines = []
        explanation_lines.append(f"Interest Alignment: {int(round(interest_fit))}% (Weight 40%) - Aligned with your focus in {', '.join(matched_interests) if matched_interests else 'core career tracks'}.")
        explanation_lines.append(f"Education Alignment: {int(round(education_fit))}% (Weight 30%) - {edu_explanation}.")
        
        matched_names = [s['name'] for s in matched_skills]
        gap_names = [s['name'] for s in gap_skills[:3]]
        
        if matched_names:
            explanation_lines.append(f"Skill Match: {int(round(skills_fit))}% (Weight 30%) - You already possess {', '.join(matched_names[:4])}.")
        if gap_names:
            explanation_lines.append(f"Recommended next skills to acquire: {', '.join(gap_names)}.")

        explanation_text = " \n".join(explanation_lines)

        rec, created = Recommendation.objects.update_or_create(
            user=user,
            career=career,
            defaults={
                'match_score': overall_score,
                'interest_fit': interest_fit,
                'education_fit': education_fit,
                'skills_fit': skills_fit,
                'explanation': explanation_text,
            }
        )
        recommendations.append(rec)

    # Sort descending by match_score
    recommendations.sort(key=lambda x: x.match_score, reverse=True)
    return recommendations
