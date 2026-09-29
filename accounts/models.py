from django.contrib.auth.models import User
from django.db import models


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Interest(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class StudentProfile(models.Model):
    GRADE_LEVELS = [
        ("FR", "Freshman"),
        ("SO", "Sophomore"),
        ("JU", "Junior"),
        ("SE", "Senior"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    grade_level = models.CharField(
        max_length=2,
        choices=GRADE_LEVELS,
        default="FR"
    )
    experience = models.TextField(blank=True)
    skills = models.ManyToManyField("Skill", through="StudentSkill", blank=True)
    interests = models.ManyToManyField("Interest", blank=True)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username

class StudentSkill(models.Model):
    LEVELS = [(1, "Beginner"), (2, "Intermediate"), (3, "Advanced")]

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level = models.IntegerField(choices=LEVELS, default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "skill"], name="unique_student_skill")
        ]

    def __str__(self):
        return f"{self.student} - {self.skill} ({self.get_level_display()})"

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_full_name() or self.user.username