from .models import Settings

def currency(request):
    try:
        settings = Settings.get_solo()
        return {'currency': settings.currency}
    except:
        return {'currency': '$'}
