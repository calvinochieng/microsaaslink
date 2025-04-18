from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.BooleanField(default= False)
    slug = models.SlugField(unique=True, blank=True, null=True)
    
    # JSON fields with default structures
    target_saas = models.JSONField(
        default=dict,
        blank=True
    )
    competitors = models.JSONField(default=list, blank=True)
    competitor_pain_points = models.JSONField(default=dict, blank=True)
    combined_pain_points = models.JSONField(default=list, blank=True)
    micro_saas_ideas = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    last_completed_step = models.CharField(
        max_length=20, 
        choices=[
            ('step1', 'Target SaaS Analysis'),
            ('step2', 'Competitor Identification'),
            ('step3', 'Pain Points Analysis'),
            ('step4', 'Combined Pain Points'),
            ('step5', 'Micro SaaS Ideas'),
            ('complete', 'Analysis Complete')
        ],
        default='',
        blank=True,
        null=True
    )
    
    def save(self, *args, **kwargs):
        # Generate slug from the target_saas_name if not already provided.
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            num = 1
            # Ensure uniqueness of the slug
            while Project.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{num}"
                num += 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name




