# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.


class School(models.Model):
    name = models.CharField(max_length=20)
    max_student = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Student(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    student_identification = models.CharField(max_length=20)


    def clean(self):
        if Student.objects.filter(school=self.school).count() >= self.school.max_student:
            raise ValidationError(("School's max student limit is reached"))

    def __str__(self):
        return self.student_identification
