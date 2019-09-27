from django.contrib import admin
from .models import CallLog, Call, CallInvoice

admin.site.register(Call)
admin.site.register(CallLog)
admin.site.register(CallInvoice)
