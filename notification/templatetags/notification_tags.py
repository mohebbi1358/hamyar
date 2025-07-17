from django import template
from notification.models import NotificationGroup

register = template.Library()

@register.simple_tag(takes_context=True)
def is_notification_manager(context):
    request = context.get("request")
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        return NotificationGroup.objects.filter(managers=user).exists()
    return False
