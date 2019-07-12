"""lms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path, include
from lms_user import urls as user_urls
from mobile_api import urls as mobile_urls
from lms_api import urls as api_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_urls)),
    path('v1/api/', include(mobile_urls)),
    path('', include(user_urls))
]
