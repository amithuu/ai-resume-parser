# Create your models here.
from django.db import models

class Candidate(models.Model):
    name = models.CharField(max_length=255, blank=True)
    resume_file = models.FileField(upload_to='resumes/')
    parsed_data = models.JSONField(null=True, blank=True)

class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    parsed_data = models.JSONField(null=True, blank=True)

class MatchResult(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    match_score = models.IntegerField()
    missing_skills = models.JSONField()