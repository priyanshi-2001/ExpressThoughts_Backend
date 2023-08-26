# Create your models here.
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
# Create your models here.

class BlogsData(models.Model):
    userId=models.ForeignKey(User,on_delete=models.CASCADE)
    description=models.TextField(max_length=2000)
    dateCreated=models.DateTimeField(default=datetime.now())
    dateModified=models.DateTimeField(default=datetime.now())

class Likes(models.Model):
    userId=models.ForeignKey(User,on_delete=models.CASCADE)
    blogId=models.ForeignKey(BlogsData,on_delete=models.CASCADE)
    dateCreated=models.DateTimeField(default=datetime.now())

class Comments(models.Model):
    userId=models.ForeignKey(User,on_delete=models.CASCADE)
    blogId=models.ForeignKey(BlogsData,on_delete=models.CASCADE)
    dateCreated=models.DateTimeField(default=datetime.now())
    description=models.CharField(max_length=500)

class Loggers(models.Model):
    apiName=models.CharField(max_length=200)
    ref1=models.CharField(max_length=300)
    ref2=models.CharField(max_length=300)
    dateCreated=models.DateTimeField(default=datetime.now())











