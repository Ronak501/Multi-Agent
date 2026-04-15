from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("api/experiments/", views.experiment_api, name="experiment_api"),
    path("api/demo/", views.demo_api, name="demo_api"),
    path("api/immac-demo/", views.immac_api, name="immac_api"),
    path("api/a2a-demo/", views.a2a_api, name="a2a_api"),
]
