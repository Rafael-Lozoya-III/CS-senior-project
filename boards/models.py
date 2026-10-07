from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


class Class(models.Model):
    """A class (course) that contains discussion boards."""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='taught_classes'
    )
    members = models.ManyToManyField(
        User, related_name='enrolled_classes', blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Classes'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('class_detail', args=[self.slug])


class Team(models.Model):
    """A team within a class."""
    name = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    class_group = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name='teams'
    )
    members = models.ManyToManyField(User, related_name='teams', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('class_group', 'slug')
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.class_group.name} - {self.name}"

    def get_absolute_url(self):
        return reverse('team_detail', args=[self.class_group.slug, self.slug])


class Thread(models.Model):
    """A discussion thread (topic) posted in a class or team board."""
    title = models.CharField(max_length=300)
    slug = models.SlugField(blank=True)
    body = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='threads'
    )
    class_group = models.ForeignKey(
        Class, on_delete=models.CASCADE,
        related_name='threads', null=True, blank=True
    )
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE,
        related_name='threads', null=True, blank=True
    )
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-updated_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:50]
            slug = base
            n = 1
            while Thread.objects.filter(slug=slug).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('thread_detail', args=[self.slug])

    @property
    def reply_count(self):
        return self.posts.count()

    @property
    def last_activity(self):
        last = self.posts.order_by('-created_at').first()
        return last.created_at if last else self.created_at


class Post(models.Model):
    """A reply within a thread."""
    thread = models.ForeignKey(
        Thread, on_delete=models.CASCADE, related_name='posts'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts'
    )
    body = models.TextField()
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True, related_name='replies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Reply by {self.author} on {self.thread}"