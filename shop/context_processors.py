from .models import SiteSettings, TrustBadge


def site_settings(request):
    settings = SiteSettings.load()
    badges = TrustBadge.objects.filter(is_active=True)
    return {
        'site_settings': settings,
        'trust_badges': badges,
    }
