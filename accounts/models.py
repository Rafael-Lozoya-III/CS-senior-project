from django.contrib.auth.models import User
from django.db import models


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
    in_team = models.BooleanField(default=False)
    skills = models.ManyToManyField("Skill", blank=True)
    interests = models.ManyToManyField("Interest", blank=True)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Interest(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name