from django.contrib import admin
from .models import StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("get_name", "grade_level", "in_team")

    def get_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    get_name.short_description = "Student"
