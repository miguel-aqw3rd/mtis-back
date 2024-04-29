from django.urls import path
from mtisAapp import endpoints

urlpatterns = [
    path('story', endpoints.new_story),
    path('question/<int:question_id>', endpoints.question),
    path('answer/<int:question_id>', endpoints.answer),
]