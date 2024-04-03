from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login, name="login"),
    path("index/", views.index, name="index"),
    path("logout/", views.logout, name="logout"),
    path("buy/", views.buy, name="buy"),
    path("create/", views.create, name="create"),
    path("edit/", views.edit, name="edit"),
    path("rank/", views.rank, name="rank"),
    path("analysis/", views.analysis, name="analysis"),
    path("k_image/<str:code>/", views.k_image, name="k_image"),
]