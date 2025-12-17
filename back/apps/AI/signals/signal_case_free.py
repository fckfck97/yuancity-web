import threading
from django.conf import settings
from django.db.models.signals import post_save
from django.db import transaction
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from apps.user.models import LawyerProfile
from apps.AI.models import ClientCase
from apps.AI.utils.chatbot.querys import assign_lawyer  # DO NOT modify this function
from apps.AI.utils.clientcasefree.prompt import classify_legal_area


def send_email_to_lawyer(subject, html_content, lawyer_email):
  """
  Helper to send an email to the assigned lawyer.
  """
  email = EmailMultiAlternatives(
    subject=subject,
    body="",
    from_email=settings.DEFAULT_FROM_EMAIL,
    to=[lawyer_email]
  )
  email.attach_alternative(html_content, "text/html")
  email.send(fail_silently=False)


@receiver(post_save, sender=ClientCase)
def client_case_post_save(sender, instance, created, **kwargs):
  """
  Called right after a ClientCase is saved.
  """
  if created:
    # For new cases, run the classification + lawyer assignment 
    # in a separate thread, after the DB transaction commits.
    transaction.on_commit(lambda: threading.Thread(
      target=_on_new_case_created, args=(instance.id,)
    ).start())


def _on_new_case_created(case_id):
  """
  This runs in the background after a new case is created 
  and fully committed to the DB.
  """
  from django.db import DatabaseError

  try:
    case = ClientCase.objects.get(id=case_id)
  except ClientCase.DoesNotExist:
    return

  # 1) Ask the LLM to identify the area of law
  area = classify_legal_area(case.desctiption or "")

  # 2) Optionally store that area into `jurisdiction` (or another field)
  case.jurisdiction = area[:100]  # just storing the area as text
  case.save(update_fields=["jurisdiction"])

  # 3) Assign a lawyer using your existing function (unchanged)
  available_profile = LawyerProfile.objects.filter(
        specialties__icontains=area,
        is_available=True
    ).order_by('current_caseload').first()
  if available_profile:
    case.lawyer = available_profile.user
    case.save(update_fields=["lawyer"])

    # 4) Send notification to the assigned lawyer
    subject = f"Nuevo caso asignado: {case.name}"
    html_content = render_to_string("case/new_case_free.html", {"case": case})
    send_email_to_lawyer(subject, html_content, available_profile.user.email)
