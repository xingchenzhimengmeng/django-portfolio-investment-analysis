from django.db import models

# Create your models here.


# 报名信息
gender_choices = [
    (1, '男'),
    (0, '女'),
]
class User(models.Model):
    account = models.CharField(10, max_length=10, unique=True)
    name = models.CharField(max_length=10)
    gender = models.IntegerField(
        choices=gender_choices,
    )
    email = models.EmailField(max_length=50, null=True)
    phone = models.CharField(max_length=20, null=True)
    password = models.CharField(max_length=20, default='1')
    fund = models.IntegerField(default=100000)





