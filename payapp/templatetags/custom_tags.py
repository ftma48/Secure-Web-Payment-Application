from django import template
from payapp.models import Notification

register = template.Library()

@register.simple_tag
def unread_count(user):
    # returns number of unread notifs
    if user.is_authenticated:
        return Notification.objects.filter(user=user, is_read=False).count()
    return 0