from Subscription.models import Subscription
def subscription_status(request):
    if request.user.is_authenticated:
        try:
            status = Subscription.objects.get(user=request.user)
        except Subscription.DoesNotExist:
            status = False
    else:
        status = False

    return {
        'status': status,
    }