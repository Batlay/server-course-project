from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Note(models.Model):
    body = models.TextField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[0:50]


class School(models.Model):
    name = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name


class Classroom(models.Model):
    name = models.CharField(max_length=200, null=True)
    school = models.ForeignKey(School, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name + " - " + self.school.name


class Teacher(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    fio = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    profile_pic = models.ImageField(default="profile2.png", null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    classroom = models.ForeignKey(Classroom, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.fio + " " + self.classroom.name + " " + self.classroom.school.name


class Pupil(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    fio = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    profile_pic = models.ImageField(default="profile2.png", null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    classroom = models.ForeignKey(Classroom, null=True, on_delete=models.CASCADE)

    def __str__(self):
        if self.user == None:
            return "ERROR-PUPIL NAME IS NULL"
        return self.fio + " " + self.classroom.name + " " + self.classroom.school.name


class Post(models.Model):
    RESULTS = [
        ('Плохой результат', 'Плохой результат'),
        ('Хорошие показатели', 'Хорошие показатели'),
        ('Стоит обратить внимание', 'Стоит обратить внимание'),
    ]
    title = models.CharField(max_length=200, unique=True)
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    content = models.TextField()
    slug = models.SlugField(max_length=200, unique=True)
    pupil = models.ForeignKey(Pupil, null=True, blank=True, on_delete=models.CASCADE)
    result = models.CharField(choices=RESULTS, max_length=100, default='Хорошие показатели')

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title


class Test_Info(models.Model):
    name = models.CharField(max_length=200, unique=True)
    time = models.IntegerField()
    url = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name


class TemperamentTest(models.Model):
    TYPES_CHOICES = [
        ('Экстраверсия - интроверсия', 'Экстраверсия - интроверсия'),
        ('Нейротизм', 'Нейротизм'),
        ('Шкала лжи', 'Шкала лжи'),
    ]

    question = models.CharField(max_length=200)
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    type = models.CharField(choices=TYPES_CHOICES, max_length=100)
    key = models.BooleanField()

    def __str__(self):
        return self.id


class MotivationTest(models.Model):
    question = models.CharField(max_length=200)
    option1 = models.CharField(max_length=200, null=True)
    option2 = models.CharField(max_length=200, null=True)
    option3 = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.question


class ActivityTest(models.Model):
    question = models.CharField(max_length=200)
    option1 = models.CharField(max_length=200, null=True)
    option2 = models.CharField(max_length=200, null=True)
    yes = models.BooleanField(default=True)
    no = models.BooleanField(default=True)

    def __str__(self):
        return self.question + str(self.id)


class Criteria(models.Model):
    name = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.id) + self.name


class Overall(models.Model):
    pupil = models.ForeignKey(Pupil, null=True, on_delete=models.CASCADE)
    criteria = models.ForeignKey(Criteria, null=True, on_delete=models.CASCADE)
    result = models.IntegerField(null=True)

    def __str__(self):
        if self.pupil == None:
            return "ERROR-PUPIL NAME IS NULL"
        return self.pupil.fio + " - " + self.pupil.classroom.name + ", " + self.pupil.classroom.school.name + ", " \
               + self.criteria.name + ", " + str(self.result)


class InfoResult(models.Model):
    name = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.id) + self.name


class PupilResult(models.Model):
    pupil = models.ForeignKey(Pupil, null=True, on_delete=models.CASCADE)
    result_name = models.ForeignKey(InfoResult, null=True, on_delete=models.CASCADE)
    result = models.IntegerField(null=True)

    def __str__(self):
        if self.pupil == None:
            return "ERROR-PUPIL NAME IS NULL"
        return self.pupil.fio + " - " + self.pupil.classroom.name + ", " + self.pupil.classroom.school.name + ", " \
               + self.result_name.name + ", " + str(self.result)
