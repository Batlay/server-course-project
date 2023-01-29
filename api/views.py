import base64

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.utils import json

from .models import Note, Post, Teacher, Pupil, Test_Info, ActivityTest, MotivationTest, TemperamentTest, Overall, \
    Criteria, PupilResult, InfoResult
from .report import make_radar_chart
from .serializers import NoteSerializer, UserSerializer, PostSerializer, PupilSerializer, TestInfoSerializer, \
    Test4Serializer, Test3Serializer, Test2Serializer, ResultSerializer
from django.contrib.auth import authenticate, login, logout


# Create your views here.

@api_view(['GET'])
def getRoutes(request):
    routes = [
        {
            'Endpoint': '/notes/',
            'method': 'GET',
            'body': None,
            'description': 'Returns an array of notes'
        },
        {
            'Endpoint': '/notes/id',
            'method': 'GET',
            'body': None,
            'description': 'Returns a single note object'
        },
        {
            'Endpoint': '/notes/create/',
            'method': 'POST',
            'body': {'body': ""},
            'description': 'Creates new note with data sent in post request'
        },
        {
            'Endpoint': '/notes/id/update/',
            'method': 'PUT',
            'body': {'body': ""},
            'description': 'Creates an existing note with data sent in post request'
        },
        {
            'Endpoint': '/notes/id/delete/',
            'method': 'DELETE',
            'body': None,
            'description': 'Deletes and exiting note'
        },
        {
            'Endpoint': '/login/',
            'method': 'POST',
            'body': {'username': '', 'password': ''},
            'description': 'Login'
        },
        {
            'Endpoint': '/pupils/',
            'method': 'GET',
            'body': None,
            'description': 'Classroom Info'
        },
        {
            'Endpoint': '/pupils/create',
            'method': 'POST',
            'body': {'fio': "", 'phone': "", 'email': "", 'profile_pic': ""},
            'description': 'Classroom Info'
        },
        {
            'Endpoint': '/pupils/id',
            'method': 'GET',
            'body': None,
            'description': 'Returns a single pupil'
        },
        {
            'Endpoint': '/pupils/overall/id',
            'method': 'GET',
            'body': None,
            'description': 'Returns overall pupil'
        },
        {
            'Endpoint': '/pupils/result/id',
            'method': 'GET',
            'body': None,
            'description': 'Returns result pupil'
        },
        {
            'Endpoint': '/notes/person/id/',
            'method': 'GET',
            'body': {'body': ""},
            'description': 'Notes'
        },
        {
            'Endpoint': '/tests/',
            'method': 'GET',
            'body': None,
            'description': 'Tests Info'
        },
        {
            'Endpoint': 'tests/test4/',
            'method': 'GET',
            'body': None,
            'description': 'Test4 Info'
        },
        {
            'Endpoint': 'tests/test4/answers/',
            'method': 'POST',
            'body': None,
            'description': 'Test4 answers'
        },
        {
            'Endpoint': 'tests/test3/',
            'method': 'GET',
            'body': None,
            'description': 'Test3 Info'
        },
        {
            'Endpoint': 'tests/test3/answers/',
            'method': 'POST',
            'body': None,
            'description': 'Test3 answers'
        },
        {
            'Endpoint': 'tests/test2/',
            'method': 'GET',
            'body': None,
            'description': 'Test2 Info'
        },
        {
            'Endpoint': 'tests/test2/answers/',
            'method': 'POST',
            'body': None,
            'description': 'Test2 answers'
        },
        {
            'Endpoint': 'tests/test1/answers/',
            'method': 'POST',
            'body': None,
            'description': 'Test1 answers'
        },
    ]

    return Response(routes)


@api_view(['GET'])
def getNotes(request):
    current_user = request.user
    teacher_details = get_object_or_404(Teacher, user=current_user)
    classroom = teacher_details.classroom
    pupils = Pupil.objects.filter(classroom=classroom).order_by('fio')
    posts = Post.objects.filter(pupil__in=pupils).order_by('-created_on')

    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getNote(request, pk):
    notes = Post.objects.get(slug=pk)
    serializer = PostSerializer(notes, many=False)
    return Response(serializer.data)


@api_view(['GET'])
def getPupilNote(request, pk):
    print(pk)
    pupil = Pupil.objects.get(id=pk)
    notes = Post.objects.filter(pupil=pupil)
    serializer = PostSerializer(notes, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def createNote(request):
    data = request.data
    note = Note.objects.create(
        body=data['body']
    )
    serializer = NoteSerializer(note, many=False)
    return Response(serializer.data)


@api_view(['POST'])
def loginPage(request):
    data = request.data
    username = data['username']
    password = data['password']

    print(request.data, username, password)
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)
    else:
        content = {'Error': 'No such User'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def getPupils(request):
    current_user = request.user
    teacher_details = get_object_or_404(Teacher, user=current_user)
    classroom = teacher_details.classroom
    pupils = Pupil.objects.filter(classroom=classroom).order_by('fio')

    serializer = PupilSerializer(pupils, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getPupil(request, pk):
    pupil = Pupil.objects.get(id=pk)
    serializer = PupilSerializer(pupil, many=False)
    return Response(serializer.data)


@api_view(['GET'])
def getPupilOverall(request, pk):
    pupil = Pupil.objects.get(id=pk)
    score = 0
    a = []
    for i in range(1, 6):
        try:
            overall = Overall.objects.get(pupil=pupil, criteria_id=i).result
        except Overall.DoesNotExist:
            overall = 0
        a.append(overall)
        score += overall

    chart = make_radar_chart(a)

    return Response(chart)


@api_view(['GET'])
def getPupilResult(request, pk):
    pupil = Pupil.objects.get(id=pk)
    # result = PupilResult.objects.filter(pupil=pupil).order_by('result_name_id')
    a = []
    for i in range(1, 12):
        try:
            result = PupilResult.objects.get(pupil=pupil, result_name_id=i).result
        except PupilResult.DoesNotExist:
            result = 0
        a.append(result)
    # serializer = ResultSerializer(result, many=True)

    return Response(a)


@api_view(['POST'])
def addPupil(request):
    data = request.data

    Pupil.objects.create(
        fio=data['fio'],
        phone=data['phone'],
        email=data['email'],
    )

    image_data = data['profile_pic']
    image = ContentFile(base64.b64decode(image_data))
    file_name = data['fio'] + ".png"

    current_user = request.user
    teacher_details = get_object_or_404(Teacher, user=current_user)
    classroom = teacher_details.classroom

    pupil = Pupil.objects.get(email=data['email'])
    user = User.objects.create_user(data['email'], data['email'], data['email'])
    pupil.classroom = classroom
    pupil.user = user
    pupil.save()
    pupil.profile_pic.save(file_name, image, save=True)

    serializer = PupilSerializer(pupil, many=False)
    return Response(serializer.data)


@api_view(['GET'])
def getTests(request):
    tests = Test_Info.objects.all()
    current_user = request.user
    pupil = get_object_or_404(Pupil, user=current_user)
    print(pupil)
    # overall = Overall.objects.get(pupil=pupil)
    # test1 = overall.criteria5
    # test2 = overall.criteria1
    # test3 = overall.criteria3
    # test4 = overall.criteria3

    serializer = TestInfoSerializer(tests, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getTest4(request):
    test = ActivityTest.objects.all()

    serializer = Test4Serializer(test, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def Test4Answers(request):
    data = request.data
    test = ActivityTest.objects.all()
    criteria = Criteria.objects.get(id=4)
    print(data)
    mark = 0
    score = 0

    for i in test:
        if str(i.id) in data:
            if (data[str(i.id)] == "Да" and i.yes) or (data[str(i.id)] == "Нет" and i.no):
                mark += 1

    if 19 <= mark <= 23:
        score += 5
    elif 16 <= mark <= 18:
        score += 4
    elif 10 <= mark <= 15:
        score += 3
    elif 7 <= mark <= 9:
        score += 2
    elif 0 <= mark <= 6:
        score += 1

    print(mark)
    print(score)

    res = InfoResult.objects.get(id=8)

    current_user = request.user
    pupil_details = get_object_or_404(Pupil, user=current_user)
    check_object = Overall.objects.filter(pupil=pupil_details, criteria=criteria)
    check_object1 = PupilResult.objects.filter(pupil=pupil_details, result_name=res)
    if check_object or check_object1:
        print('Ошибка')
    else:
        result = PupilResult(pupil=pupil_details, result_name=res, result=mark)
        result.save()
        overall = Overall(pupil=pupil_details, criteria=criteria, result=score)
        overall.save()

    return Response()


@api_view(['GET'])
def getTest3(request):
    test = MotivationTest.objects.all()
    serializer = Test3Serializer(test, many=True)

    return Response(serializer.data)


@api_view(['POST'])
def Test3Answers(request):
    data = request.data
    test = MotivationTest.objects.all()
    print(data)

    # Сохранить оценку
    return Response()


@api_view(['GET'])
def getTest2(request):
    test = TemperamentTest.objects.all()
    serializer = Test2Serializer(test, many=True)

    return Response(serializer.data)


@api_view(['POST'])
def Test2Answers(request):
    data = request.data
    test = TemperamentTest.objects.all()
    criteria = Criteria.objects.get(id=1)

    mark1 = 0
    mark2 = 0
    mark3 = 0
    score = 0

    for i in test:
        if str(i.id) in data:
            if data[str(i.id)] == "Да":
                if i.type == "Экстраверсия - интроверсия" and i.key:
                    mark1 += 1
                elif i.type == "Нейротизм" and i.key:
                    mark2 += 1
                elif i.type == "Шкала лжи" and i.key:
                    mark3 += 1
    print(data)

    if 10 <= mark1 <= 14:
        score += 2
    elif (5 <= mark1 <= 9) or (15 <= mark1 <= 19):
        score += 1

    if mark2 <= 7:
        score += 2
    elif 8 <= mark2 <= 13:
        score += 1

    if mark3 <= 4:
        score += 1

    print(mark1, mark2, mark3)
    print(score)

    intr = InfoResult.objects.get(id=1)
    neur = InfoResult.objects.get(id=2)
    lie = InfoResult.objects.get(id=3)
    current_user = request.user
    pupil_details = get_object_or_404(Pupil, user=current_user)

    check_object = Overall.objects.filter(pupil=pupil_details, criteria=criteria)
    check_object1 = PupilResult.objects.filter(pupil=pupil_details, result_name=intr)
    check_object2 = PupilResult.objects.filter(pupil=pupil_details, result_name=neur)
    check_object3 = PupilResult.objects.filter(pupil=pupil_details, result_name=lie)
    if check_object or check_object1 or check_object2 or check_object3:
        print('Ошибка')
    else:
        result1 = PupilResult(pupil=pupil_details, result_name=intr, result=mark1)
        result2 = PupilResult(pupil=pupil_details, result_name=neur, result=mark2)
        result3 = PupilResult(pupil=pupil_details, result_name=lie, result=mark3)
        result1.save()
        result2.save()
        result3.save()
        overall = Overall(pupil=pupil_details, criteria=criteria, result=score)
        overall.save()

    return Response()


@api_view(['POST'])
def Test1Answers(request):
    data = request.data
    criteria = Criteria.objects.get(id=5)
    self_esteem = 0
    expectations = 0
    score = 0
    area1 = data[0:6]
    print(area1)
    area2 = data[6:12]
    print(area2)
    for i in area1:
        self_esteem += int(i)
    for i in area2:
        expectations += int(i)
    self_esteem /= 6
    expectations /= 6
    print(self_esteem)
    print(expectations)

    diff = round(expectations, 0) - round(self_esteem, 0)
    print(diff)
    print(score)

    if 60 <= expectations <= 90:
        score += 2
    else:
        score += 1

    if 45 <= self_esteem <= 74:
        score += 2
    else:
        score += 1

    if 8 <= diff <= 22:
        score += 1

    current_user = request.user
    pupil_details = get_object_or_404(Pupil, user=current_user)

    se = InfoResult.objects.get(id=9)
    ex = InfoResult.objects.get(id=10)
    di = InfoResult.objects.get(id=11)

    check_object = Overall.objects.filter(pupil=pupil_details, criteria=criteria)
    check_object1 = PupilResult.objects.filter(pupil=pupil_details, result_name=se)
    check_object2 = PupilResult.objects.filter(pupil=pupil_details, result_name=ex)
    check_object3 = PupilResult.objects.filter(pupil=pupil_details, result_name=di)
    if check_object or check_object1 or check_object2 or check_object3:
        print('Ошибка')
    else:
        result1 = PupilResult(pupil=pupil_details, result_name=se, result=round(self_esteem, 0))
        result2 = PupilResult(pupil=pupil_details, result_name=ex, result=round(expectations, 0))
        result3 = PupilResult(pupil=pupil_details, result_name=di, result=diff)
        result1.save()
        result2.save()
        result3.save()
        overall = Overall(pupil=pupil_details, criteria=criteria, result=score)
        overall.save()

    return Response()
