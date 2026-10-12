
from django.contrib import admin
from .models import (
    Skill,
    Interest,
    StudentProfile,
    StudentSkill,
    TeacherProfile,
    Project,
    ProjectApplication,
)


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


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "creator",
        "class_group",
        "max_members",
        "created_at",
    )
    list_filter = ("class_group",)
    search_fields = ("title", "description", "creator__username")


@admin.register(ProjectApplication)
class ProjectApplicationAdmin(admin.ModelAdmin):
    list_display = ("project", "applicant", "status")
    list_filter = ("status",)
    search_fields = ("project__title", "applicant__username")


admin.site.register(Skill)
admin.site.register(Interest)
admin.site.register(TeacherProfile)
