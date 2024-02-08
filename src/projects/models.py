import uuid

from django.conf import settings
from django.db import models

# Create your models here.


class TypeChoices(models.TextChoices):
    BACKEND = "Back-end"
    FRONTEND = "Front-end"
    IOS = 'iOS'
    ANDROID = 'Android'


class PriorityChoices(models.TextChoices):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = 'High'


class IssueTagChoices(models.TextChoices):
    BUG = "BUG"
    FEATURE = "Feature"
    TASK = 'Task'


class Project(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=10, choices=TypeChoices.choices)
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    contributors = models.ManyToManyField(to="Contributor")

    def add_contributor(self, user):
        contributor, created = Contributor.objects.get_or_create(user=user)
        self.contributors.add(contributor)


class Issue(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PriorityChoices.choices)
    tag = models.CharField(max_length=10, choices=IssueTagChoices.choices)
    contributor = models.ForeignKey(to="Contributor", on_delete=models.CASCADE)
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    description = models.TextField()
    author = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)


class Contributor(models.Model):
    user = models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
