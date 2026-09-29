from django.contrib import admin
from .models import Skill, Interest, StudentProfile, StudentSkill, TeacherProfile

class StudentSkillInline(admin.TabularInline):
    model = StudentSkill
    extra = 1

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("get_name", "grade_level")
    inlines = [StudentSkillInline]

    def get_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    get_name.short_description = "Student"

admin.site.register(Skill)
admin.site.register(Interest)
admin.site.register(TeacherProfile)