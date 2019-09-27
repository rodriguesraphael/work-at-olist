from django.db.models.signals import post_save
from django.dispatch import receiver
from calls.models import CallInvoice, CallLog


@receiver(post_save, sender=CallLog)
def create_call_invoice(sender, instance, **kwargs):
    if instance.type == 'end':
        CallInvoice.objects.create(call_id=instance.call_id)
