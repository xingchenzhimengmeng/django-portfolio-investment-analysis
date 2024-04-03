from django.urls import path
from . import views

urlpatterns = [
    path("users/list/", views.users_list, name="users_list"),
    path("users/add/", views.users_add, name="users_add"),
    path("users/<int:user_id>/edit/", views.users_edit, name="users_edit"),
    path("users/<int:user_id>/delete/", views.users_delete, name="users_delete"),
    # path("users/login", views.users_login, name="users_login"),
]
