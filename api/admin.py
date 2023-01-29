from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Note)
admin.site.register(Pupil)
admin.site.register(Post)
admin.site.register(Classroom)
admin.site.register(School)
admin.site.register(Teacher)
admin.site.register(Test_Info)
admin.site.register(TemperamentTest)
admin.site.register(MotivationTest)
admin.site.register(ActivityTest)
admin.site.register(Overall)
admin.site.register(Criteria)
admin.site.register(PupilResult)
admin.site.register(InfoResult)

