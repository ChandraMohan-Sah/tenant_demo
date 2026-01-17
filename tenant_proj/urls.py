# todo_proj/urls.py
from django.urls import path
from django.contrib import admin
from todo import views as task_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # tenant-specfic urls -todo 
    path("api/tasks/", task_views.task_list, name="task-list"),
    path("api/tasks/<int:pk>/", task_views.task_detail, name="task-detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

