from django.contrib import admin
from .models import SiteSettings, Testimonial, FAQ, Partner, NewsletterSubscriber, CarouselSlide

admin.site.register(SiteSettings)
admin.site.register(Testimonial)
admin.site.register(FAQ)
admin.site.register(Partner)
admin.site.register(NewsletterSubscriber)
admin.site.register(CarouselSlide)
