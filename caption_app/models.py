from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_pro = models.BooleanField(default=False)
    transcription_minutes_left = models.IntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {'Pro' if self.is_pro else 'Free'}"

class CaptionTemplate(models.Model):
    EFFECT_CHOICES = [
        ('clean', 'Clean / Classic'),
        ('neon', 'Neon Glow'),
        ('fire', 'Fire Animation'),
        ('emboss', 'Emboss Style'),
        ('gradient', 'Gradient Split'),
        ('pill', 'Pill Badge'),
        ('podcast', 'Podcast Stack')
    ]

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    font_family = models.CharField(max_length=100)
    effect_type = models.CharField(max_length=50, choices=EFFECT_CHOICES, default='clean')
    layout_type = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class VideoProject(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects', null=True, blank=True)
    title = models.CharField(max_length=255, default='Untitled video')
    input_video = models.FileField(upload_to='uploads/videos/')
    output_video = models.FileField(upload_to='outputs/videos/', blank=True, null=True)
    template = models.ForeignKey(CaptionTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    # Lets the user override the template's font with any Google Font
    # picked from the font-search box on the dashboard.
    selected_font = models.CharField(max_length=150, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transcript_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.status}"

    @property
    def active_font(self):
        """Font to actually use when rendering: user's pick, else template's font."""
        return self.selected_font or (self.template.font_family if self.template else 'Poppins')
    from django.db import models

class FontOption(models.Model):
    name = models.CharField(max_length=100)
    font_file_name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class KineticPreset(models.Model):
    title = models.CharField(max_length=100)
    badge_color = models.CharField(max_length=50, default="#F5A623")

    def __str__(self):
        return self.title

class UserProject(models.Model):
    title = models.CharField(max_length=200, default="Untitled Clip")
    status = models.CharField(max_length=50, default="Completed")
    font_used = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
