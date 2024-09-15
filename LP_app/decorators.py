from django.shortcuts import redirect
from datetime import datetime
from Subscription.models import *
def subscription_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('landing')
        else:
            try:
                subscription = Subscription.objects.get(user=request.user)
                if not subscription.is_active():
                    return redirect('subscribe')  # توجيه المستخدم إلى صفحة الاشتراك إذا لم يكن الاشتراك مفعلًا
            except Subscription.DoesNotExist:
                return redirect('subscribe')  # توجيه المستخدم إلى صفحة الاشتراك إذا لم يكن هناك اشتراك
            return view_func(request, *args, **kwargs)
    return _wrapped_view
