import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# Уақытша тапсырмалар тізімі (3-жұмыста базаға ауыстырамыз)
TASKS = [
    {"id": 1, "title": "Django үйрену", "status": "in_progress"},
    {"id": 2, "title": "Практикалық жұмыс 2", "status": "todo"},
    {"id": 3, "title": "Git орнату", "status": "done"},
]


def health(request):
    return JsonResponse({"status": "ok"})


def index(request):
    return JsonResponse({"message": "Task Manager API"})


def about(request):
    return JsonResponse({"project": "Task Manager", "version": "1.0"})


def task_list(request):
    return JsonResponse(TASKS, safe=False)


def task_detail(request, id):
    for task in TASKS:
        if task["id"] == id:
            return JsonResponse(task)
    return JsonResponse({"error": "Task not found"}, status=404)


@csrf_exempt
@require_POST
def echo(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    return JsonResponse(data, safe=False)