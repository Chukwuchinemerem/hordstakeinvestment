from django.db import models


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default='CryptoVest')
    site_tagline = models.CharField(max_length=200, default='Smart Crypto Investment Platform')
    site_description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    favicon = models.ImageField(upload_to='site/', blank=True, null=True)
    whatsapp_number = models.CharField(max_length=30, default='+1234567890')
    support_email = models.EmailField(default='support@cryptovest.com')
    referral_bonus_percent = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    min_withdrawal = models.DecimalField(max_digits=20, decimal_places=2, default=10.00)
    withdrawal_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    total_users_display = models.PositiveIntegerField(default=0)
    total_paid_display = models.CharField(max_length=50, default='$0')
    maintenance_mode = models.BooleanField(default=False)
    hero_title = models.CharField(max_length=200, default='Grow Your Wealth With Crypto')
    hero_subtitle = models.TextField(default='Professional crypto investment platform with guaranteed returns.')
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    telegram_url = models.URLField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    message = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.country}"

    class Meta:
        ordering = ['-created_at']


class FAQ(models.Model):
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.question

    class Meta:
        ordering = ['order']


class Partner(models.Model):
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='partners/', blank=True, null=True)
    url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class CarouselSlide(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    image_url = models.URLField(blank=True, help_text='Unsplash or external image URL')
    image = models.ImageField(upload_to='carousel/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order']
