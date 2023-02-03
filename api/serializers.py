from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import *


class PostSerializer(ModelSerializer):
    created_on = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")
    author = serializers.CharField(source="author.username", read_only=True)
    pupil = serializers.CharField(source="pupil.fio", read_only=True)

    class Meta:
        model = Post
        fields = '__all__'


class PupilSerializer(ModelSerializer):
    class Meta:
        model = Pupil
        fields = '__all__'


class SchoolSerializer(ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'


class ClassroomSerializer(ModelSerializer):
    class Meta:
        model = Classroom
        fields = '__all__'


class ResultSerializer(ModelSerializer):
    class Meta:
        model = PupilResult
        fields = '__all__'


class TestInfoSerializer(ModelSerializer):
    class Meta:
        model = Test_Info
        fields = '__all__'


class Test4Serializer(ModelSerializer):
    class Meta:
        model = ActivityTest
        fields = '__all__'


class Test3Serializer(ModelSerializer):
    class Meta:
        model = MotivationTest
        fields = '__all__'


class Test2Serializer(ModelSerializer):
    class Meta:
        model = TemperamentTest
        fields = '__all__'


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_superuser', 'groups', 'first_name', 'last_name')
