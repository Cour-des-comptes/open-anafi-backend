from django.db import models
from mptt.models import MPTTModel

from open_anafi.models import Indicator, Frame


# Create your models here.

class Comment(models.Model):
    username = models.CharField(max_length=100, null=True)
    comment = models.TextField(null=True)
    date = models.DateField(auto_now=True, null=True)

class FrameComment(models.Model):
    username = models.CharField(max_length=100, null=True)
    comment = models.TextField(null=True)
    date = models.DateField(auto_now=True, null=True)
    frame = models.ForeignKey(Frame, on_delete = models.CASCADE, null = True, related_name = "related_frame")

class IndicatorComment(models.Model):
    username = models.CharField(max_length=100, null=True)
    comment = models.TextField(null=True)
    date = models.DateField(auto_now=True, null=True)
    indicator = models.ForeignKey(Indicator, on_delete = models.CASCADE, null = True, related_name = "related_indicator")