"""billcalls URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework.schemas import get_schema_view
from rest_framework.routers import DefaultRouter

from calls.views import CallLogViewSet, CallInvoiceViewSet


schema_view = get_schema_view(
    title="Call API",
    description="Phone Call Record Api",
    version="1.0.0",
    url='https://billcalls.herokuapp.com/',
    urlconf='billcalls.urls'
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('doc', schema_view, name='Doc API Call Record'),
]

router = DefaultRouter(trailing_slash=False)
router.register(
    r'call-log',
    CallLogViewSet,
    base_name='call-log')
router.register(
    r'call-invoice',
    CallInvoiceViewSet,
    base_name='call-invoice')

urlpatterns += router.urls
