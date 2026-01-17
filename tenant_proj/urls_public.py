# todo_proj/urls_public.py
from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from home.api import views as home_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # public urls 
    path("", home_views.home, name="home-page"),# for home 
                                                # for subscriptions : just register in admin panel 
                                                
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

