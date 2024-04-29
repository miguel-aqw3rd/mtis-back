from django.contrib import admin
from models import Question, Story, Weights, Answer

admin.site.register(Question)
admin.site.register(Story)
admin.site.register(Answer)
admin.site.register(Weights)
