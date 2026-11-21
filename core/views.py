import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Q

from .models import (
    UserProfile, Interest, UserInterest, Skill, UserSkill,
    Career, CareerSkill, Recommendation, SavedCareer,
    CareerRoadmap, RoadmapMilestone, UserMilestoneProgress,
    AssistantConversation, AssistantMessage, UserCV, MockInterview
)
from .recommendation_engine import generate_recommendations_for_user, calculate_skills_fit
from .assistant_guardrails import classify_and_respond, PREDEFINED_REDIRECT_IDENTITY, PREDEFINED_REDIRECT_OFFTOPIC, PREDEFINED_REDIRECT_PRIVACY


def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Allow sign in with email or username
        user = None
        if '@' in username_or_email:
            try:
                u_obj = User.objects.get(email__iexact=username_or_email)
                user = authenticate(request, username=u_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        else:
            user = authenticate(request, username=username_or_email, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username/email or password.')

    return render(request, 'login.html')


def user_register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not email or not password:
            messages.error(request, 'All required fields must be filled.')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username__iexact=username).exists():
            messages.error(request, 'Username is already taken.')
        elif User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'An account with this email address already exists.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            UserProfile.objects.create(
                user=user,
                full_name=full_name or username,
                education_level='school',
                qualification='11th Grade (Science)',
                specialization='Science & Technology',
                profile_completed=False
            )
            login(request, user)
            return redirect('profile_wizard')

    return render(request, 'register.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    """
    Renders UI Screen 4 ("Aivance" style dashboard):
    - Lessons took (46 completed)
    - Skill tracker progress (Design 46%, Management 12%, Software 27%)
    - Hours spent (127h)
    - Calendar widget
    - Upcoming lessons (Figma Pro 62%)
    - Mock interview & Upload CV cards
    - Course recommendations
    """
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    top_recs = Recommendation.objects.filter(user=user).select_related('career')[:4]
    if not top_recs.exists():
        generate_recommendations_for_user(user)
        top_recs = Recommendation.objects.filter(user=user).select_related('career')[:4]

    upcoming_interview = MockInterview.objects.filter(user=user).first()
    recent_cv = UserCV.objects.filter(user=user).last()

    context = {
        'profile': profile,
        'top_recommendations': top_recs,
        'upcoming_interview': upcoming_interview,
        'recent_cv': recent_cv,
        'active_nav': 'dashboard',
    }
    return render(request, 'dashboard.html', context)


@login_required
def chat_view(request):
    """
    Renders UI Screen 1 ("CareerWithinU" style AI Chat):
    - Left side: transfers/activities, next assessment card ("Monday, 11 AM"), progress metrics
    - Right side: rich chat interface with conversation history and career cards
    """
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    conversation, _ = AssistantConversation.objects.get_or_create(
        user=user,
        defaults={'title': f'{profile.full_name} Career Chat'}
    )

    chat_messages = conversation.messages.all().order_by('timestamp')

    context = {
        'profile': profile,
        'conversation': conversation,
        'chat_messages': chat_messages,
        'active_nav': 'chat',
    }
    return render(request, 'chat.html', context)


@login_required
def careers_view(request):
    """
    Renders UI Screen 3 ("My Choices" / Best Matches Explorer):
    - Refine and filter pills (2-4 GCSEs, A-levels, Degree, Categories)
    - Grid view of best matches with match percentage bars
    - Favorite and bin/remove actions
    - Compare selection
    """
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    # Check for recalculation or initialize if needed
    if not Recommendation.objects.filter(user=user).exists():
        generate_recommendations_for_user(user)

    query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', 'all').strip()
    edu_filter = request.GET.get('edu', 'all').strip()
    view_binned = request.GET.get('binned', '0') == '1'
    view_favorites = request.GET.get('favorites', '0') == '1'

    # Retrieve recommendations joined with career and saved state
    recs_qs = Recommendation.objects.filter(user=user).select_related('career')

    if query:
        recs_qs = recs_qs.filter(
            Q(career__title__icontains=query) |
            Q(career__category__icontains=query) |
            Q(career__overview__icontains=query)
        )

    if category_filter and category_filter != 'all':
        recs_qs = recs_qs.filter(career__category__icontains=category_filter)

    if edu_filter and edu_filter != 'all':
        recs_qs = recs_qs.filter(career__eligibility_education=edu_filter)

    saved_careers = SavedCareer.objects.filter(user=user)
    fav_career_ids = set(saved_careers.filter(is_binned=False).values_list('career_id', flat=True))
    binned_career_ids = set(saved_careers.filter(is_binned=True).values_list('career_id', flat=True))

    if view_binned:
        recs_qs = recs_qs.filter(career_id__in=binned_career_ids)
    elif view_favorites:
        recs_qs = recs_qs.filter(career_id__in=fav_career_ids)
    else:
        # Exclude binned careers by default
        recs_qs = recs_qs.exclude(career_id__in=binned_career_ids)

    recommendations = list(recs_qs.order_by('-match_score'))

    # Decorate with favorite status
    for r in recommendations:
        r.is_favorited = r.career_id in fav_career_ids
        r.is_binned = r.career_id in binned_career_ids

    context = {
        'profile': profile,
        'recommendations': recommendations,
        'fav_count': len(fav_career_ids),
        'binned_count': len(binned_career_ids),
        'selected_category': category_filter,
        'selected_edu': edu_filter,
        'query': query,
        'view_binned': view_binned,
        'view_favorites': view_favorites,
        'active_nav': 'careers',
    }
    return render(request, 'careers.html', context)


@login_required
def career_detail_view(request, slug):
    """
    Renders detailed career information and Skill Gap Analysis (FR-29, FR-32 to FR-34)
    """
    user = request.user
    profile = getattr(user, 'profile', None)
    career = get_object_or_404(Career, slug=slug)

    rec = Recommendation.objects.filter(user=user, career=career).first()
    if not rec:
        generate_recommendations_for_user(user)
        rec = Recommendation.objects.filter(user=user, career=career).first()

    skills_fit_score, matched_skills, developing_skills, gap_skills = calculate_skills_fit(user, career)

    # Check if saved
    saved_obj = SavedCareer.objects.filter(user=user, career=career).first()
    is_favorited = saved_obj and not saved_obj.is_binned

    # Related careers
    related_careers = Career.objects.filter(category=career.category).exclude(id=career.id)[:3]

    # Roadmap if available
    roadmap = getattr(career, 'roadmap', None)

    context = {
        'profile': profile,
        'career': career,
        'recommendation': rec,
        'matched_skills': matched_skills,
        'developing_skills': developing_skills,
        'gap_skills': gap_skills,
        'is_favorited': is_favorited,
        'related_careers': related_careers,
        'roadmap': roadmap,
        'active_nav': 'careers',
    }
    return render(request, 'career_detail.html', context)


@login_required
def roadmap_view(request, career_slug=None):
    """
    Renders UI Screen 2 ("Ascento" style Gamified Learning Roadmap):
    - Level Progress (Level 12, 2840/3200 XP)
    - 7 Day Streak & 15420 Total Points
    - Milestones list (HTML & CSS, JavaScript, React, Node.js...)
    - Progress bars and status updates
    """
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    all_roadmaps = CareerRoadmap.objects.select_related('career').all()

    if career_slug:
        roadmap = get_object_or_404(CareerRoadmap, career__slug=career_slug)
    else:
        # Default to Software Developer roadmap or first available
        roadmap = CareerRoadmap.objects.filter(career__slug='software-developer').first() or all_roadmaps.first()

    milestones_with_progress = []
    completed_count = 0
    total_count = 0

    if roadmap:
        milestones = roadmap.milestones.all().order_by('order')
        total_count = milestones.count()

        for m in milestones:
            prog, _ = UserMilestoneProgress.objects.get_or_create(
                user=user,
                milestone=m,
                defaults={'status': 'not_started', 'progress_percent': 0}
            )
            if prog.status == 'completed':
                completed_count += 1

            milestones_with_progress.append({
                'milestone': m,
                'progress': prog
            })

    roadmap_completion_pct = int((completed_count / total_count * 100)) if total_count > 0 else 0

    context = {
        'profile': profile,
        'roadmap': roadmap,
        'all_roadmaps': all_roadmaps,
        'milestones_data': milestones_with_progress,
        'completed_count': completed_count,
        'total_count': total_count,
        'roadmap_completion_pct': roadmap_completion_pct,
        'active_nav': 'learning',
    }
    return render(request, 'roadmap.html', context)


@login_required
def career_compare_view(request):
    """
    Renders side-by-side career comparison view (FR-31)
    """
    user = request.user
    profile = getattr(user, 'profile', None)

    slug1 = request.GET.get('c1', 'systems-analyst')
    slug2 = request.GET.get('c2', 'software-developer')
    slug3 = request.GET.get('c3', 'data-scientist')

    careers_to_compare = []
    for s in [slug1, slug2, slug3]:
        if s:
            c = Career.objects.filter(slug=s).first()
            if c:
                rec = Recommendation.objects.filter(user=user, career=c).first()
                _, matched, developing, missing = calculate_skills_fit(user, c)
                careers_to_compare.append({
                    'career': c,
                    'rec': rec,
                    'matched_skills': matched,
                    'developing_skills': developing,
                    'missing_skills': missing,
                })

    all_careers = Career.objects.all().order_by('title')

    context = {
        'profile': profile,
        'compared_careers': careers_to_compare,
        'all_careers': all_careers,
        'selected_slugs': [slug1, slug2, slug3],
        'active_nav': 'careers',
    }
    return render(request, 'career_compare.html', context)


@login_required
def profile_wizard_view(request):
    """
    Renders multi-step Profile Setup Wizard (FR-06 to FR-13, FR-18 to FR-21):
    - Education details
    - Interests selection with preference questions
    - Technical and Soft skills with proficiency levels
    """
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'save_education':
            profile.full_name = request.POST.get('full_name', profile.full_name)
            profile.headline = request.POST.get('headline', profile.headline)
            profile.education_level = request.POST.get('education_level', profile.education_level)
            profile.qualification = request.POST.get('qualification', profile.qualification)
            profile.institution = request.POST.get('institution', profile.institution)
            profile.specialization = request.POST.get('specialization', profile.specialization)
            profile.experience_level = request.POST.get('experience_level', profile.experience_level)
            profile.profile_completed = True
            profile.save()
            
            # Recalculate recommendations immediately
            recs = generate_recommendations_for_user(user)
            top_rec = recs[0] if recs else None
            top_info = f"Top match: {top_rec.career.title} ({top_rec.score_round}% match)!" if top_rec else ""
            messages.success(request, f'Education details saved and recommendations recalculated! {top_info}')

            if request.POST.get('redirect_to') == 'careers':
                return redirect('careers')
            return redirect('profile_wizard')

        elif action == 'save_interests':
            # Clear old and save new selected interests
            selected_interest_ids = request.POST.getlist('interests')
            UserInterest.objects.filter(user=user).delete()
            for i_id in selected_interest_ids:
                strength = int(request.POST.get(f'strength_{i_id}', 4))
                UserInterest.objects.create(
                    user=user,
                    interest_id=i_id,
                    preference_strength=strength
                )
            messages.success(request, 'Interest preferences saved!')

        elif action == 'save_skills':
            # Add new skill or update proficiency
            skill_id = request.POST.get('skill_id')
            proficiency = request.POST.get('proficiency', 'Intermediate')
            if skill_id:
                UserSkill.objects.update_or_create(
                    user=user,
                    skill_id=skill_id,
                    defaults={'proficiency': proficiency}
                )
                messages.success(request, 'Skill added/updated!')

        elif action == 'remove_skill':
            user_skill_id = request.POST.get('user_skill_id')
            UserSkill.objects.filter(user=user, id=user_skill_id).delete()
            messages.info(request, 'Skill removed.')

        # Recalculate recommendations after profile changes
        generate_recommendations_for_user(user)
        return redirect('profile_wizard')

    all_interests = Interest.objects.all().order_by('category_name')
    user_interest_ids = set(UserInterest.objects.filter(user=user).values_list('interest_id', flat=True))

    all_skills = Skill.objects.all().order_by('category', 'name')
    user_skills = UserSkill.objects.filter(user=user).select_related('skill')
    user_skill_ids = set(user_skills.values_list('skill_id', flat=True))

    top_recommendations = Recommendation.objects.filter(user=user).select_related('career')[:4]

    context = {
        'profile': profile,
        'all_interests': all_interests,
        'user_interest_ids': user_interest_ids,
        'all_skills': all_skills,
        'user_skills': user_skills,
        'user_skill_ids': user_skill_ids,
        'top_recommendations': top_recommendations,
        'active_nav': 'profile',
    }
    return render(request, 'profile_wizard.html', context)


@login_required
def admin_portal_view(request):
    """
    Renders Admin Management Dashboard (FR-05, UC-04, SRS 9.4):
    - Catalogue management
    - Users overview
    - Interactive guardrail testing panel
    """
    user = request.user
    if not (user.is_staff or user.is_superuser):
        messages.error(request, 'Administrator access required.')
        return redirect('dashboard')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_career':
            title = request.POST.get('title')
            category = request.POST.get('category')
            overview = request.POST.get('overview')
            responsibilities = request.POST.get('responsibilities')
            salary_range = request.POST.get('salary_range')
            eligibility = request.POST.get('eligibility', 'undergraduate')
            slug = title.lower().replace(' ', '-').replace('/', '-').replace('(', '').replace(')', '')
            
            Career.objects.create(
                title=title,
                slug=slug,
                category=category,
                overview=overview,
                responsibilities=responsibilities,
                salary_range=salary_range,
                eligibility_education=eligibility,
            )
            messages.success(request, f'Career "{title}" successfully added to catalogue!')
            return redirect('admin_portal')

    careers = Career.objects.all().order_by('-id')
    users = User.objects.all().select_related('profile').order_by('-id')
    skills_count = Skill.objects.count()
    recommendations_count = Recommendation.objects.count()

    context = {
        'careers': careers,
        'users': users,
        'skills_count': skills_count,
        'recommendations_count': recommendations_count,
        'active_nav': 'admin',
    }
    return render(request, 'admin_custom.html', context)


# ==========================================
# REST API ENDPOINTS FOR DYNAMIC UI
# ==========================================

@login_required
def api_chat_message(request):
    """
    Handles user chat message submission.
    Applies strict guardrails:
    - Topic classification
    - Identity shielding
    - Prompt-injection defense
    - Predefined replies for off-topic, identity, privacy
    - Returns structured answer and career cards
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    try:
        data = json.loads(request.body)
        user_text = data.get('message', '').strip()
    except Exception:
        user_text = request.POST.get('message', '').strip()

    if not user_text:
        return JsonResponse({'error': 'Empty message'}, status=400)

    user = request.user
    conversation, _ = AssistantConversation.objects.get_or_create(
        user=user,
        defaults={'title': f'{user.username} Career Guidance'}
    )

    # Save user message
    user_msg = AssistantMessage.objects.create(
        conversation=conversation,
        sender='user',
        text=user_text
    )

    # Classify & Respond through Guardrail Engine
    bot_reply, is_redirected, cards = classify_and_respond(user_text, user=user)

    # Save assistant message
    asst_msg = AssistantMessage.objects.create(
        conversation=conversation,
        sender='assistant',
        text=bot_reply,
        is_redirected=is_redirected
    )
    if cards:
        asst_msg.set_cards(cards)
        asst_msg.save()

    return JsonResponse({
        'status': 'success',
        'reply': bot_reply,
        'is_redirected': is_redirected,
        'cards': cards,
        'timestamp': asst_msg.timestamp.strftime('%H:%M'),
    })


@login_required
def api_update_milestone(request):
    """
    Updates milestone progress status (not_started, in_progress, completed)
    and awards XP to user profile.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    try:
        data = json.loads(request.body)
        milestone_id = data.get('milestone_id')
        new_status = data.get('status')  # 'not_started', 'in_progress', 'completed'
    except Exception:
        milestone_id = request.POST.get('milestone_id')
        new_status = request.POST.get('status')

    milestone = get_object_or_404(RoadmapMilestone, id=milestone_id)
    user = request.user
    prog, _ = UserMilestoneProgress.objects.get_or_create(user=user, milestone=milestone)

    old_status = prog.status
    prog.status = new_status
    if new_status == 'completed':
        prog.progress_percent = 100
        prog.completed_date = 'Today'
        # Award XP to profile
        profile = getattr(user, 'profile', None)
        if profile and old_status != 'completed':
            profile.xp_points += milestone.xp_reward
            profile.total_points += milestone.xp_reward
            profile.save()
    elif new_status == 'in_progress':
        prog.progress_percent = 50
    else:
        prog.progress_percent = 0
    prog.save()

    return JsonResponse({
        'status': 'success',
        'new_status': new_status,
        'progress_percent': prog.progress_percent,
        'xp_points': user.profile.xp_points if hasattr(user, 'profile') else 0,
        'total_points': user.profile.total_points if hasattr(user, 'profile') else 0,
    })


@login_required
def api_toggle_save_career(request):
    """
    Toggles save/favorite or bin/hide for a career.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    try:
        data = json.loads(request.body)
        career_id = data.get('career_id')
        action_type = data.get('action', 'favorite')  # 'favorite' or 'bin'
    except Exception:
        career_id = request.POST.get('career_id')
        action_type = request.POST.get('action', 'favorite')

    career = get_object_or_404(Career, id=career_id)
    user = request.user

    saved_obj, created = SavedCareer.objects.get_or_create(user=user, career=career)

    if action_type == 'favorite':
        if not created and not saved_obj.is_binned:
            # Toggle off
            saved_obj.delete()
            is_fav = False
        else:
            saved_obj.is_binned = False
            saved_obj.save()
            is_fav = True
        return JsonResponse({'status': 'success', 'is_favorited': is_fav, 'is_binned': False})

    elif action_type == 'bin':
        saved_obj.is_binned = True
        saved_obj.save()
        return JsonResponse({'status': 'success', 'is_binned': True})

    elif action_type == 'unbin':
        saved_obj.delete()
        return JsonResponse({'status': 'success', 'is_binned': False})

    return JsonResponse({'error': 'Invalid action'}, status=400)


@login_required
def api_upload_cv(request):
    """
    Handles CV upload and simulated skill extraction (Screen 4).
    """
    if request.method != 'POST' or 'cv_file' not in request.FILES:
        return JsonResponse({'error': 'File upload required'}, status=400)

    uploaded_file = request.FILES['cv_file']
    filename = uploaded_file.name

    # Mock extraction of skills based on filename/content
    extracted = "Python, HTML/CSS, SQL, Problem Solving, Communication"
    user_cv = UserCV.objects.create(
        user=request.user,
        filename=filename,
        file_path=filename,
        extracted_skills=extracted
    )

    return JsonResponse({
        'status': 'success',
        'filename': filename,
        'extracted_skills': extracted,
        'message': 'CV analyzed successfully! Skills mapped to profile.'
    })


@login_required
def api_schedule_interview(request):
    """
    Schedules a mock interview session (Screen 4).
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    try:
        data = json.loads(request.body)
        role = data.get('role', 'Software Engineer')
        time_slot = data.get('time_slot', 'Tomorrow, 3:00 PM')
    except Exception:
        role = request.POST.get('role', 'Software Engineer')
        time_slot = request.POST.get('time_slot', 'Tomorrow, 3:00 PM')

    interview = MockInterview.objects.create(
        user=request.user,
        role_target=role,
        scheduled_time=time_slot,
        status='Confirmed'
    )

    return JsonResponse({
        'status': 'success',
        'role': role,
        'time_slot': time_slot,
        'message': f'Mock interview for {role} scheduled for {time_slot}!'
    })
