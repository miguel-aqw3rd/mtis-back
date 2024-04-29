from django.urls import path
from mtisAapp import endpoints

urlpatterns = [
    path('entry/<int:entry_id>', endpoints.get_entry),  # get and delete
    path('entries', endpoints.entries),
    path('entrygroup/<int:entrygroup_id>', endpoints.get_entrygroup),
    path('entry', endpoints.new_entry),
    path('entrygroup/entry/<int:entry_id>', endpoints.new_entrygroup),
    path('entrygroup/<int:entrygroup_id>/mainentry/<int:entry_id>', endpoints.change_mainentry_of_entrygroup),
    path('entrygroup/<int:entrygroup_id>/favorite', endpoints.favorite_entrygroup),
    path('entrygroups', endpoints.entrygroups),

    path('challenge/<int:entry_id>', endpoints.new_challenge),
    path('goal', endpoints.new_goal),  # post and put
    path('goal/<int:goal_id>', endpoints.goal),  # get and delete
    path('goals', endpoints.goals),

]