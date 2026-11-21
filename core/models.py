from django.db import models
from django.contrib.auth.models import User
import json

class UserProfile(models.Model):
    EDUCATION_LEVEL_CHOICES = [
        ('school', 'School / 10th-12th Grade'),
        ('diploma', 'Diploma'),
        ('undergraduate', 'Undergraduate / Bachelor Degree'),
        ('postgraduate', 'Postgraduate / Master Degree'),
        ('doctorate', 'Doctorate / Professional'),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ('Beginner/Student', 'Beginner / Student (0-1 yrs)'),
        ('Intermediate/Graduate', 'Early Career / Graduate (1-3 yrs)'),
        ('Experienced', 'Experienced Professional (3+ yrs)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=150, default='Rahul Sharma')
    headline = models.CharField(max_length=255, default='High School Student / Tech Enthusiast')
    education_level = models.CharField(max_length=50, choices=EDUCATION_LEVEL_CHOICES, default='school')
    qualification = models.CharField(max_length=150, default='11th Grade (Science & Mathematics)')
    institution = models.CharField(max_length=200, default='Modern High School')
    specialization = models.CharField(max_length=150, default='Physics, Chemistry & Math (PCM)')
    graduation_year = models.IntegerField(default=2026)
    experience_level = models.CharField(max_length=50, choices=EXPERIENCE_LEVEL_CHOICES, default='Beginner/Student')
    profile_completed = models.BooleanField(default=True)
    
    # Gamification stats (matching Ascento / Aivance / CareerWithinU UI)
    xp_points = models.IntegerField(default=2840)
    xp_needed = models.IntegerField(default=3200)
    level = models.IntegerField(default=12)
    streak_days = models.IntegerField(default=7)
    total_points = models.IntegerField(default=15420)
    lessons_completed = models.IntegerField(default=46)
    hours_spent = models.IntegerField(default=127)
    assessment_date_str = models.CharField(max_length=100, default='Monday, 11 AM')
    avatar = models.CharField(max_length=50, default='avatar-1')

    # Progress percentages for dashboard
    psychometric_score = models.IntegerField(default=80)
    college_shortlist_count = models.IntegerField(default=50)
    roadmap_progress = models.IntegerField(default=30)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Profile ({self.full_name})"

    @property
    def level_progress_percent(self):
        if self.xp_needed <= 0:
            return 100
        return min(100, int((self.xp_points / self.xp_needed) * 100))


class Interest(models.Model):
    category_name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='compass')

    def __str__(self):
        return self.category_name


class UserInterest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_interests')
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE)
    preference_strength = models.IntegerField(default=4)  # 1 to 5 scale

    class Meta:
        unique_together = ('user', 'interest')

    def __str__(self):
        return f"{self.user.username} -> {self.interest.category_name} ({self.preference_strength}/5)"


class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('technical', 'Technical Skill'),
        ('soft', 'Soft Skill'),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='technical')
    domain = models.CharField(max_length=50, default='Software')
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.category})"


class UserSkill(models.Model):
    PROFICIENCY_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default='Intermediate')

    class Meta:
        unique_together = ('user', 'skill')

    def __str__(self):
        return f"{self.user.username} -> {self.skill.name} ({self.proficiency})"


class Career(models.Model):
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True)
    category = models.CharField(max_length=100, default='Technology')
    overview = models.TextField()
    responsibilities = models.TextField(help_text="Bullet points or detailed responsibilities")
    work_environment = models.TextField(blank=True)
    eligibility_education = models.CharField(max_length=100, default='undergraduate')
    preferred_education = models.CharField(max_length=255, default="Bachelor's degree in Computer Science, Engineering, or related STEM field")
    entry_routes = models.TextField(blank=True)
    salary_range = models.CharField(max_length=100, default="$85,000 - $140,000 / ₹9,00,000 - ₹26,00,000")
    salary_source = models.CharField(max_length=100, default="Bureau of Labor Statistics / Glassdoor 2024")
    job_outlook = models.CharField(max_length=100, default="+22% (Much faster than average)")
    related_careers_count = models.IntegerField(default=2)
    icon = models.CharField(max_length=50, default='laptop')
    image_url = models.CharField(max_length=300, blank=True)
    certifications = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class CareerSkill(models.Model):
    PROFICIENCY_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    IMPORTANCE_CHOICES = [
        ('Essential', 'Essential'),
        ('Preferred', 'Preferred'),
        ('Useful', 'Useful'),
    ]

    career = models.ForeignKey(Career, on_delete=models.CASCADE, related_name='career_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    required_proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default='Intermediate')
    importance = models.CharField(max_length=20, choices=IMPORTANCE_CHOICES, default='Essential')

    class Meta:
        unique_together = ('career', 'skill')

    def __str__(self):
        return f"{self.career.title} requires {self.skill.name} ({self.required_proficiency})"


class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    career = models.ForeignKey(Career, on_delete=models.CASCADE)
    match_score = models.FloatField(default=0.0)  # 0 to 100
    interest_fit = models.FloatField(default=0.0)
    education_fit = models.FloatField(default=0.0)
    skills_fit = models.FloatField(default=0.0)
    explanation = models.TextField()
    generated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'career')
        ordering = ['-match_score']

    def __str__(self):
        return f"{self.user.username} - {self.career.title} ({self.match_score:.0f}%)"

    @property
    def score_round(self):
        return int(round(self.match_score))


class SavedCareer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_careers')
    career = models.ForeignKey(Career, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)
    is_binned = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('user', 'career')

    def __str__(self):
        status = "Binned" if self.is_binned else "Favorited"
        return f"{self.user.username} {status}: {self.career.title}"


class CareerRoadmap(models.Model):
    career = models.OneToOneField(Career, on_delete=models.CASCADE, related_name='roadmap')
    title = models.CharField(max_length=200, default='Master Career Path')
    subtitle = models.CharField(max_length=255, default='Complete journey from beginner to senior professional')
    total_xp = models.IntegerField(default=4500)
    estimated_hours = models.IntegerField(default=350)

    def __str__(self):
        return f"Roadmap: {self.title}"

    @property
    def total_milestones_count(self):
        return self.milestones.count()


class RoadmapMilestone(models.Model):
    LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    roadmap = models.ForeignKey(CareerRoadmap, on_delete=models.CASCADE, related_name='milestones')
    order = models.IntegerField(default=1)
    title = models.CharField(max_length=150)
    description = models.TextField()
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='Beginner')
    xp_reward = models.IntegerField(default=200)
    estimated_hours = models.IntegerField(default=40)
    resource_provider = models.CharField(max_length=100, default='Official Documentation / Coursera')
    resource_url = models.CharField(max_length=255, default='https://roadmap.sh')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.roadmap.career.title} - Step {self.order}: {self.title}"


class UserMilestoneProgress(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_milestones')
    milestone = models.ForeignKey(RoadmapMilestone, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    progress_percent = models.IntegerField(default=0)
    completed_date = models.CharField(max_length=50, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'milestone')

    def __str__(self):
        return f"{self.user.username} - {self.milestone.title} ({self.status})"


class AssistantConversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assistant_conversations')
    title = models.CharField(max_length=150, default='Career Guidance Session')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chat for {self.user.username} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class AssistantMessage(models.Model):
    SENDER_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]

    conversation = models.ForeignKey(AssistantConversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_redirected = models.BooleanField(default=False)
    cards_json = models.TextField(blank=True, default='')  # JSON of recommended cards

    def get_cards(self):
        if self.cards_json:
            try:
                return json.loads(self.cards_json)
            except Exception:
                return []
        return []

    def set_cards(self, cards_list):
        self.cards_json = json.dumps(cards_list)

    def __str__(self):
        return f"[{self.sender}] {self.text[:40]}"


class UserCV(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cv_uploads')
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500, blank=True)
    extracted_skills = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} CV: {self.filename}"


class MockInterview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interviews')
    role_target = models.CharField(max_length=150, default='Software Engineer')
    scheduled_time = models.CharField(max_length=100, default='Tomorrow, 3:00 PM')
    status = models.CharField(max_length=50, default='Scheduled')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} Interview: {self.role_target} ({self.scheduled_time})"
