# tasks/views.py
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Task

# List all tasks (public)
def task_list(request):
    tasks = Task.objects.all()  # you could filter for published tasks only
    data = [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "completed": t.completed,
            "published_at": t.published_at,
            "summary": t.summary,
            "is_overdue": t.is_overdue
        } for t in tasks
    ]
    return JsonResponse(data, safe=False)


# Detail of one task
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    data = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "published_at": task.published_at,
        "summary": task.summary,
        "is_overdue": task.is_overdue
    }
    return JsonResponse(data)
