from django.http import JsonResponse
from django.shortcuts import render

from .services import (
    default_process_steps,
    run_a2a_demo,
    run_demo_round,
    run_experiment_summary,
    run_immac_demo,
)


def index(request):
    context = {
        "steps": default_process_steps(),
        "default_results": run_experiment_summary(episodes=30, length=10),
    }
    return render(request, "webapp/index.html", context)


def experiment_api(request):
    episodes = int(request.GET.get("episodes", "30"))
    length = int(request.GET.get("length", "10"))

    episodes = max(1, min(episodes, 200))
    length = max(1, min(length, 100))

    result = run_experiment_summary(episodes=episodes, length=length)
    return JsonResponse(result)


def demo_api(request):
    return JsonResponse(run_demo_round())


def immac_api(request):
    return JsonResponse(run_immac_demo())


def a2a_api(request):
    return JsonResponse(run_a2a_demo())
