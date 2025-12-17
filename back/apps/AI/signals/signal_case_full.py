import threading
from django.conf import settings
from django.db.models.signals import post_save
from django.db import transaction
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from apps.AI.models import Case


def _send_case_email(subject, context, to_email_list):
    """
    Helper para enviar un correo renderizando el template `new_case_free.html`.
    """
    html_content = render_to_string("case/new_case_full.html", context)
    email = EmailMultiAlternatives(
        subject=subject, 
        body="", 
        from_email=settings.DEFAULT_FROM_EMAIL, 
        to=to_email_list
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)


@receiver(post_save, sender=Case)
def case_post_save(sender, instance, created, **kwargs):
    """
    Se activa después de guardar un Case. 
    Si es un nuevo caso (created == True), enviamos email al cliente y, si existe,
    al abogado asignado.
    """
    if created:
        # Esperamos a que la transacción se confirme para evitar problemas
        transaction.on_commit(lambda: threading.Thread(
            target=_on_new_case_created, 
            args=(instance.id,)
        ).start())


def _on_new_case_created(case_id):
    """
    Esto se ejecuta en un hilo aparte, una vez confirmada la transacción.
    """
    try:
        case = Case.objects.get(id=case_id)
    except Case.DoesNotExist:
        return

    # Armamos el contexto para el template
    context = {"case": case}

    # 1) Correo al cliente (si existe)
    if case.client and case.client.email:
        subject_for_client = f"Tu nuevo caso se ha registrado: {case.area}"
        _send_case_email(subject_for_client, context, [case.client.email])

    # 2) Correo al abogado asignado (si existe)
    if case.assigned_lawyer and case.assigned_lawyer.email:
        subject_for_lawyer = f"Se te ha asignado un caso: {case.area}"
        _send_case_email(subject_for_lawyer, context, [case.assigned_lawyer.email])
