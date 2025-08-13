# proedge/emails.py

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def _send_html_email(subject, to_email, template_name, context):
    html = render_to_string(template_name, context)
    text = strip_tags(html)
    email = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, [to_email])
    email.attach_alternative(html, "text/html")
    email.send(fail_silently=False)

def notify_agency_new_join_request(join_request, summary):
    """
    Email the agency when an agent submits a join request.
    `summary` is a short text about auto-check results.
    """
    agency_email = getattr(join_request.agency, 'email', None) or getattr(join_request.agency, 'contact_email', None)
    if not agency_email:
        return  # no email on agency; skip

    ctx = {
        'join_request': join_request,
        'summary': summary,
    }
    _send_html_email(
        subject=f"New Agent Join Request: {join_request.agent.username}",
        to_email=agency_email,
        template_name='emails/agency_new_join_request.html',
        context=ctx
    )

def notify_agent_request_decision(join_request, approved, reason=None):
    """
    Email the agent when their request is approved/rejected.
    """
    agent_email = getattr(join_request.agent, 'email', None)
    if not agent_email:
        return

    ctx = {
        'join_request': join_request,
        'approved': approved,
        'reason': reason,
    }
    _send_html_email(
        subject="Your agency join request has been " + ("approved" if approved else "rejected"),
        to_email=agent_email,
        template_name='emails/agent_request_decision.html',
        context=ctx
    )
