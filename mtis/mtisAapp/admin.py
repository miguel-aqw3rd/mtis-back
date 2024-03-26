from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(User)
admin.site.register(Weights)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Story)
admin.site.register(Entry)
admin.site.register(EntryGroup)
admin.site.register(Groups)
admin.site.register(Goal)
admin.site.register(Banner)

