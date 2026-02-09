def currency(request):
    if request.user.is_authenticated:
        try:
            return {'currency': request.user.settings.currency}
        except:
            return {'currency': '$'}
    return {'currency': '$'}
