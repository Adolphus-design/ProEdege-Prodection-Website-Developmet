from .models import Notification

def notify(user, title, message=""):
    Notification.objects.create(user=user, title=title, message=message)