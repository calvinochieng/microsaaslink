from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse

class SaaSAnalysis(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    search_queries = models.TextField( null =  True, blank= True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    product_url = models.URLField()
    description = models.TextField()
    analysis_result = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.product_name} ({self.user})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate base slug from product name
            base_slug = slugify(self.product_name)            
            self.slug = base_slug
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('analysis_detail', kwargs={'slug': self.slug})