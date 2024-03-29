"""
URL configuration for mtis project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from mtisAapp import endpoints

urlpatterns = [
    path('api/v1/signup', endpoints.signup),
    path('api/v1/login', endpoints.login),
    path('api/v1/logout', endpoints.logout),
    path('api/v1/name', endpoints.change_name),

    path('api/v1/story', endpoints.new_story),
    path('api/v1/question/<int:question_id>', endpoints.question),
    path('api/v1/answer/<int:question_id>', endpoints.answer),

    path('api/v1/entry/<int:entry_id>', endpoints.get_entry),  # get and delete
    path('api/v1/entries', endpoints.entries),
    path('api/v1/entrygroup/<int:entrygroup_id>', endpoints.get_entrygroup),
    path('api/v1/entry', endpoints.new_entry),
    path('api/v1/entrygroup/entry/<int:entry_id>', endpoints.new_entrygroup),
    path('api/v1/entrygroup/<int:entrygroup_id>/mainentry/<int:entry_id>', endpoints.change_mainentry_of_entrygroup),
    path('api/v1/entrygroup/<int:entrygroup_id>/favorite', endpoints.favorite_entrygroup),
    path('api/v1/entrygroups', endpoints.entrygroups),

    path('api/v1/challenge/<int:entry_id>', endpoints.new_challenge),
    path('api/v1/goal', endpoints.new_goal),  # post and put
    path('api/v1/goal/<int:goal_id>', endpoints.goal),  # get and delete
    path('api/v1/goals', endpoints.goals),

    path('admin/', admin.site.urls),
]
