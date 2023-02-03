import base64
import io

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.http import HttpResponse, FileResponse, JsonResponse
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from datetime import datetime

from .models import Post, Teacher, Pupil, Test_Info, ActivityTest, MotivationTest, TemperamentTest, Overall, \
    Criteria, PupilResult, InfoResult, School, Classroom
from .report import make_radar_chart, bar2, make_radar_chart1, pdf_report, bar1, temperament_circle1
from .serializers import UserSerializer, PostSerializer, PupilSerializer, TestInfoSerializer, \
    Test4Serializer, Test3Serializer, Test2Serializer, SchoolSerializer, ClassroomSerializer


@api_view(['GET'])
def getRoutes(request):
    routes = [
        {
            'Endpoint': '/notes/',
            'method': 'POST',
            'body': {'id': ''},
            'description': 'Returns an array of notes'
        },
        {
            'Endpoint': '/notes/id',
            'method': 'GET',
            'body': None,
            'description': 'Returns a single note object'
        },
        {
            'Endpoint': '/notes/create/id',
            'method': 'POST',
            'body': {'title': "", 'content': ''},
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
            'method': 'POST',
            'body': {'id': ''},
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
            'Endpoint': 'tests/test1/answers/id',
            'method': 'POST',
            'body': None,
            'description': 'Test1 answers'
        },
        {
            'Endpoint': '/pupils/report/id/',
            'method': 'GET',
            'body': None,
            'description': 'Returns pdf file'
        },
        {
            'Endpoint': '/pupils/report/download/id/',
            'method': 'GET',
            'body': None,
            'description': 'Returns pdf file'
        },
        {
            'Endpoint': '/user-forgot-password/',
            'method': 'POST',
            'body': {'email': ""},
            'description': 'Email for password reset'
        },
        {
            'Endpoint': '/user-change-password/id',
            'method': 'POST',
            'body': {'password': ""},
            'description': 'Email for reset'
        },
        {
            'Endpoint': '/schools/',
            'method': 'GET',
            'body': None,
            'description': 'Schools Info'
        },
        {
            'Endpoint': '/schools/id',
            'method': 'GET',
            'body': None,
            'description': 'Returns a list of classrooms'
        },
        {
            'Endpoint': '/classrooms/',
            'method': 'GET',
            'body': None,
            'description': 'Classrooms Info'
        },
        {
            'Endpoint': '/classrooms/id',
            'method': 'GET',
            'body': None,
            'description': 'Returns a list of pupils'
        },
        {
            'Endpoint': '/pupils/',
            'method': 'POST',
            'body': {'id': ""},
            'description': 'Classroom Info'
        },
        {
            'Endpoint': '/schools/delete/id',
            'method': 'DELETE',
            'body': {'id': ""},
            'description': 'Delete school'
        },
        {
            'Endpoint': '/schools/create/',
            'method': 'POST',
            'body': {'name': ""},
            'description': 'Create school'
        },
        {
            'Endpoint': '/schools/edit/id',
            'method': 'PUT',
            'body': {'name': ""},
            'description': 'Edit school'
        },
        {
            'Endpoint': '/classrooms/delete/id',
            'method': 'DELETE',
            'body': {'id': ""},
            'description': 'Delete classroom'
        },
        {
            'Endpoint': '/classrooms/create/id',
            'method': 'POST',
            'body': {'name': ""},
            'description': 'Create classroom'
        },
        {
            'Endpoint': '/classrooms/edit/id',
            'method': 'PUT',
            'body': {'name': ""},
            'description': 'Edit classroom'
        },
    ]

    return Response(routes)


@api_view(['PUT'])
def editClassroom(request, pk):
    data = request.data
    ids = pk.split('&')
    id_school = ids[0]
    id_classroom = ids[1]
    school = School.objects.get(id=id_school)
    if Classroom.objects.filter(school=school, name=data['name']).exists():
        content = {'Error': 'Такой класс уже существует'}
        return Response(content, status=status.HTTP_409_CONFLICT)
    elif data['name'] in [None, '']:
        content = {'Error': 'Заполните все поля'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        classroom = Classroom.objects.get(id=id_classroom, school=school)
        classroom.name = data['name']
        classroom.save()
        return JsonResponse({'message': 'Classroom was edited successfully!'})


@api_view(['DELETE'])
def deleteClassroom(request, pk):
    ids = pk.split('&')
    id_school = ids[0]
    id_classroom = ids[1]
    school = School.objects.get(id=id_school)
    try:
        Classroom.objects.get(id=id_classroom, school=school).delete()
        return JsonResponse({'message': 'Classroom was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
    except Classroom.DoesNotExist:
        content = {'Error': 'Нет такого класса'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def createClassroom(request, pk):
    data = request.data
    school = School.objects.get(id=pk)
    if Classroom.objects.filter(school=school, name=data['name']).exists():
        content = {'Error': 'Такой класс уже существует'}
        return Response(content, status=status.HTTP_409_CONFLICT)
    elif data['name'] in [None, '']:
        content = {'Error': 'Заполните все поля'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        classroom = Classroom.objects.create(
            name=data['name'], school=school
        )
        serializer = ClassroomSerializer(classroom, many=False)
        return Response(serializer.data)


@api_view(['PUT'])
def editSchool(request, pk):
    data = request.data
    if School.objects.filter(name=data['name']).exists():
        content = {'Error': 'Такая школа уже существует'}
        return Response(content, status=status.HTTP_409_CONFLICT)
    elif data['name'] in [None, '']:
        content = {'Error': 'Заполните все поля'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        school = School.objects.get(id=pk)
        school.name = data['name']
        school.save()
        return JsonResponse({'message': 'School was edited successfully!'})



@api_view(['DELETE'])
def deleteSchool(request, pk):
    try:
        School.objects.get(id=pk).delete()
        return JsonResponse({'message': 'School was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
    except School.DoesNotExist:
        content = {'Error': 'Нет такой школы'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def createSchool(request):
    data = request.data
    if School.objects.filter(name=data['name']).exists():
        content = {'Error': 'Такая школа уже существует'}
        return Response(content, status=status.HTTP_409_CONFLICT)
    elif data['name'] in [None, '']:
        content = {'Error': 'Заполните все поля'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        school = School.objects.create(
            name=data['name'],
        )
        serializer = SchoolSerializer(school, many=False)
        return Response(serializer.data)


@api_view(['POST'])
def getPupils(request):
    data = request.data
    id_user = data['id']
    current_user = User.objects.get(id=id_user)
    teacher_details = get_object_or_404(Teacher, user=current_user)
    classroom = teacher_details.classroom
    pupils = Pupil.objects.filter(classroom=classroom).order_by('fio')

    serializer = PupilSerializer(pupils, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def getNotes(request):
    data = request.data
    id_user = data['id']
    current_user = User.objects.get(id=id_user)
    teacher_details = get_object_or_404(Teacher, user=current_user)
    classroom = teacher_details.classroom
    pupils = Pupil.objects.filter(classroom=classroom).order_by('fio')
    posts = Post.objects.filter(pupil__in=pupils).order_by('-created_on')

    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getNote(request, pk):
    print(pk)
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
def createNote(request, pk):
    pupil = Pupil.objects.get(id=pk)
    data = request.data
    if Post.objects.filter(title=data['title']).exists():
        content = {'Error': 'Заполните все поля'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    elif data['title'] in [None, ''] or data['content'] in [None, '']:
        content = {'Error': 'Заполните все поля'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        now = datetime.now()
        note = Post.objects.create(
            title=data['title'],
            content=data['content'],
            pupil=pupil,
            slug=now.strftime("%d%m%Y%H%M%S")
        )
        serializer = PostSerializer(note, many=False)
        return Response(serializer.data)


@api_view(['POST'])
def loginPage(request):
    data = request.data
    username = data['username']
    password = data['password']

    print(request.data, username, password)
    if data['username'] in [None, ''] or data['password'] in [None, '']:
        content = {'Error': 'Заполните все поля'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            serializer = UserSerializer(user, many=False)
            return Response(serializer.data)
        else:
            content = {'Error': 'No such User'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def ResetPassword(request):
    data = request.data
    print(data)
    email = data['email']
    print(email)
    verify = User.objects.filter(email=email).first()
    if verify:
        link = f"http://localhost:3000/user-change-password/{verify.id}"
        send_mail(
            'NewWay | Подтвердите сообщение',
            'Пожалуйста, подтвердите сообщение ниже для сброса своего пароля',
            'gleb.batyan@gmail.com',
            [email],
            fail_silently=False,
            html_message=f'<p>Пожалуйста, перейдите по ссылке ниже для сброса вашего пароля </p><p>{link}</p>'
                         f'<br></br><p>С уважением, команда NewWay</p>'
        )

        return JsonResponse({'bool': True, 'msg': 'Пожалуйста, проверьте ваш email'},
                            json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({'bool': False, 'msg': 'Данный email не найден'}, json_dumps_params={'ensure_ascii': False})


@api_view(['POST'])
def ChangePassword(request, pk):
    data = request.data
    password = data['password']

    verify = User.objects.filter(id=pk).first()
    if verify:
        try:
            user = User.objects.get(id=pk)
            user.set_password(password)
            user.save()
            return JsonResponse({'bool': True, 'msg': 'Пароль был успешно изменен'})
        except User.DoesNotExist:
            return JsonResponse({'bool': False, 'msg': 'Упс... Произошла ошибка'})
    else:
        return JsonResponse({'bool': False, 'msg': 'Упс... Произошла ошибка'})


@api_view(['GET'])
def getSchools(request):
    schools = School.objects.all()

    serializer = SchoolSerializer(schools, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getClassrooms(request, pk):
    try:
        school = School.objects.get(id=pk)
        classrooms = Classroom.objects.filter(school=school).order_by('name')
        serializer = ClassroomSerializer(classrooms, many=True)
        return Response(serializer.data)
    except School.DoesNotExist:
        content = {'Error': 'No such school'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def getClassroomPupils(request, pk):
    try:
        classroom = Classroom.objects.get(id=pk)
        pupils = Pupil.objects.filter(classroom=classroom).order_by('fio')

        serializer = PupilSerializer(pupils, many=True)
        return Response(serializer.data)
    except Classroom.DoesNotExist:
        content = {'Error': 'No such classroom'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def getPupil(request, pk):
    try:
        pupil = Pupil.objects.get(id=pk)
        serializer = PupilSerializer(pupil, many=False)
        return Response(serializer.data)
    except Pupil.DoesNotExist:
        content = {'Error': 'No such Pupil'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def getPupilOverall(request, pk):
    try:
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
    except Pupil.DoesNotExist:
        content = {'Error': 'No such Pupil'}
        return Response()


@api_view(['GET'])
def getPupilResult(request, pk):
    try:
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
    except Pupil.DoesNotExist:
        return Response()


@api_view(['POST'])
def addPupil(request):
    data = request.data

    if Pupil.objects.filter(email=data['email']).exists():
        content = {'Error': 'Пользователь с таким email уже существует'}
        return Response(content, status=status.HTTP_409_CONFLICT)
    elif data['fio'] in [None, ''] or data['phone'] in [None, ''] or data['email'] in [None, '']:
        content = {'Error': 'Заполните все поля'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
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
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def getTests(request):
    tests = Test_Info.objects.all()
    data = request.data
    id_user = data['id']
    current_user = User.objects.get(id=id_user)
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
def Test1Answers(request, pk):
    data = request.data
    print(data)
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

    current_user = User.objects.get(id=pk)
    pupil_details = get_object_or_404(Pupil, user=current_user)

    se = InfoResult.objects.get(id=9)
    ex = InfoResult.objects.get(id=10)
    di = InfoResult.objects.get(id=11)

    check_object = Overall.objects.filter(pupil=pupil_details, criteria=criteria)
    check_object1 = PupilResult.objects.filter(pupil=pupil_details, result_name=se)
    check_object2 = PupilResult.objects.filter(pupil=pupil_details, result_name=ex)
    check_object3 = PupilResult.objects.filter(pupil=pupil_details, result_name=di)
    if check_object or check_object1 or check_object2 or check_object3:
        content = {'Error': 'Тест уже был пройден'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        result1 = PupilResult(pupil=pupil_details, result_name=se, result=round(self_esteem, 0))
        result2 = PupilResult(pupil=pupil_details, result_name=ex, result=round(expectations, 0))
        result3 = PupilResult(pupil=pupil_details, result_name=di, result=diff)
        result1.save()
        result2.save()
        result3.save()
        overall = Overall(pupil=pupil_details, criteria=criteria, result=score)
        overall.save()
        return Response({'msg': 'Results saved'})


@api_view(['GET'])
def getPdf(request, pk):
    try:
        pupil = Pupil.objects.get(id=pk)
        text = "К показателям когнитивно-эмоционального критерия относятся:<br/>– дивергентное мышление;<br/>– легкость в использовании ассоциаций (ассоциативная и экспрессивная беглость);<br/>– особенности темперамента (пластичность, вариативность, эмоциональная устойчивость, склонность к напряженной деятельности, социальная энергичность);<br/>– эмпатия." \
               "<br/>К показателям личностно-креативного критерия относятся:<br/>– воображение;<br/>– критическое мышление;<br/>– стремление к независимости, отсутствие страха высказывать свою точку зрения на проблему;<br/>– надситуативная активность (инициативность, выход за пределы заданного);<br/>– внутренняя позиция творца (заинтересованность в решении проблемно-поисковых задач, тенденции к индивидуализации творческой деятельности)." \
               "<br/>Показателями мотивационно-ценностного критерия являются:<br/>– потребность в творческой деятельности;<br/>– потребность в участии в учебно-познавательной деятельности;<br/>– положительное отношение к обучению, школе, учителю, одноклассникам;<br/>– признание ценности творчества." \
               "<br/>Показателями деятельностно-процессуального критерия являются:" \
               "<br/>– творческая и познавательная самостоятельность;<br/>– освоение способов творческой деятельности;<br/>– качество выполняемых действий;<br/>– стремление к достижению цели, получению конкретных результатов своей деятельности;<br/>– навыки сотрудничества;<br/>– способность оптимизации своего поведения (навыки организации творческого процесса, гибкий выбор той или иной стратегии поведения, безболезненный отказ от неэффективного способа действия)." \
               "<br/>К показателям рефлексивного критерия относятся:<br/>– особенности эмоционально-ценностного отношения к себе (уровень самооценки, её адекватность);<br/>– стремление к самообразованию, саморазвитию;<br/>– умение объективно оценить свой и чужой творческий продукт."
        results = []
        overall_results = []
        buffer = io.BytesIO()
        for i in range(1, 12):
            try:
                result = PupilResult.objects.get(pupil=pupil, result_name_id=i).result
            except PupilResult.DoesNotExist:
                result = 0
            results.append(result)
        for i in range(1, 6):
            try:
                overall = Overall.objects.get(pupil=pupil, criteria_id=i).result
            except Overall.DoesNotExist:
                overall = 0
            overall_results.append(overall)

        chart = make_radar_chart1(overall_results)

        b = pdf_report(results)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline;'
        pdf = canvas.Canvas(buffer, pagesize=A4)
        pdfmetrics.registerFont(TTFont('TNR', 'times.ttf'))
        pdf.setFont("TNR", 14)
        my_Style = ParagraphStyle('style1',
                                  style='style1',
                                  backColor='#F1F1F1',
                                  fontName='TNR',
                                  fontSize=12,
                                  borderColor='#8AFF8A',
                                  borderWidth=1,
                                  borderPadding=(10, 10, 10),
                                  leading=10,
                                  alignment=TA_CENTER
                                  )

        pdf.setTitle(pupil.fio + " | Оценка творческих способностей")
        pdf.drawImage(pupil.profile_pic.path, x=70, y=600, width=200, height=200, preserveAspectRatio=True, mask='auto')
        pdf.drawImage(chart, x=300, y=580, width=250, height=250, preserveAspectRatio=True, mask='auto')
        pdf.drawString(x=180, y=555, text=pupil.classroom.name)
        pdf.drawString(x=70, y=555, text=pupil.classroom.school.name)
        pdf.drawString(x=70, y=570, text=pupil.fio)
        p = Paragraph(text, my_Style)
        p.wrapOn(pdf, 450, 150)
        p.drawOn(pdf, x=80, y=150)
        pdf.showPage()
        score = 0
        # for i in results:
        #     if i == 0:
        #         score += 1
        # if score >= 1:
        #     pdf.setFont("TNR", 14)
        #     pdf.drawString(x=40, y=780, text="Для получения аналитической статистики необходимо получить все результаты тестов!")
        #     pdf.save()
        # else:
        pdf.setFont("TNR", 14)
        pdf.drawString(x=70, y=780, text="Уровень притязаний")
        p1 = Paragraph(b[0], my_Style)
        p1.wrapOn(pdf, 450, 650)
        p1.drawOn(pdf, x=80, y=650)

        pdf.drawString(x=70, y=600, text="Уровень самооценки")
        p2 = Paragraph(b[1], my_Style)
        p2.wrapOn(pdf, 450, 500)
        p2.drawOn(pdf, x=80, y=500)

        pdf.drawString(x=70, y=450, text="Разница")
        p3 = Paragraph(b[2], my_Style)
        p3.wrapOn(pdf, 450, 350)
        p3.drawOn(pdf, x=80, y=350)
        pdf.showPage()

        pdf.setFont("TNR", 14)
        pdf.drawString(x=70, y=780, text="Темперамент")
        p1 = Paragraph(b[3], my_Style)
        p1.wrapOn(pdf, 450, 100)
        p1.drawOn(pdf, x=80, y=100)

        pdf.setFont("TNR", 14)
        pdf.drawString(x=70, y=600, text="Нейротизм")
        p1 = Paragraph(b[4], my_Style)
        p1.wrapOn(pdf, 450, 400)
        p1.drawOn(pdf, x=80, y=400)

        chart1 = bar1(results[2], results[0], results[1])
        chart2 = temperament_circle1(results[0], results[1])
        pdf.setFont("TNR", 14)
        pdf.drawString(x=70, y=300, text="Шкала искренности")
        p1 = Paragraph(b[5], my_Style)
        p1.wrapOn(pdf, 450, 300)
        p1.drawOn(pdf, x=80, y=300)
        pdf.drawImage(chart2, x=70, y=600, width=200, height=200, preserveAspectRatio=True, mask='auto')
        pdf.drawImage(chart1, x=300, y=580, width=250, height=250, preserveAspectRatio=True, mask='auto')

        chart3 = bar2(results[4], results[5], results[6])
        pdf.showPage()
        pdf.setFont("TNR", 14)
        pdf.drawString(x=70, y=750, text="Оценка потребности в достижении успеха")
        p1 = Paragraph(b[6], my_Style)
        p1.wrapOn(pdf, 450, 700)
        p1.drawOn(pdf, x=80, y=700)
        pdf.drawString(x=70, y=650, text="Уровень креативности")
        p1 = Paragraph(b[7], my_Style)
        p1.wrapOn(pdf, 450, 600)
        p1.drawOn(pdf, x=80, y=600)
        pdf.drawImage(chart3, x=150, y=300, width=300, height=300, preserveAspectRatio=True, mask='auto')
        text = "0-20 баллов - низкие значения <br/>" \
               "21-49 баллов - средние значения <br/>" \
               "50-67 баллов - высокие значения <br/>"
        self = "Направленность на себя связывается с преобладанием мотивов собственного благополучия, стремления к личному" \
               " первенству, престижу. Такой человек чаще всего бывает занят самим собой, своими чувствами и переживаниями и" \
               " мало реагирует на потребности людей вокруг себя. В работе видит прежде всего возможность удовлетворить свои" \
               " притязания и амбиции. Характерна агрессивность в достижении статуса, властность, склонность к соперничеству," \
               " раздражительность, тревожность.<br/><br/>" \
               "Направленность на взаимодействие имеет место тогда, когда поступки человека определяются потребностью в" \
               " общении, стремлением поддерживать хорошие отношения с товарищами по работе. Такой человек проявляет" \
               " интерес к совместной деятельности, иногда в ущерб выполнению своих должностных обязанностей. Характерно" \
               " оказание искренней помощи людям, ориентация на социальное одобрение, зависимость от группы, потребность" \
               " в привязанности и эмоциональных отношениях.<br/><br/>" \
               "Направленность на задачу отражает преобладание мотивов, порождаемых самой деятельностью, увлечение" \
               " процессом деятельности, бескорыстное стремление к познанию, овладению новыми умениями и навыками." \
               " Характерна заинтересованность в решении деловых проблем, выполнение работы как можно лучше, стремление" \
               " добивается наибольшей продуктивности группы, ориентация на деловое сотрудничество, способность отстаивать" \
               " в интересах дела точку зрения, которую считает полезной для выполнения поставленной задачи."
        p2 = Paragraph(text, my_Style)
        p2.wrapOn(pdf, 450, 300)
        p2.drawOn(pdf, x=80, y=300)
        p3 = Paragraph(self, my_Style)
        p3.wrapOn(pdf, 450, 50)
        p3.drawOn(pdf, x=80, y=50)
        pdf.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='hello.pdf')
    except Pupil.DoesNotExist:
        content = {'Error': 'No such Pupil'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def downloadPdf(request, pk):
    try:
        pupil = Pupil.objects.get(id=pk)
        text = "К показателям когнитивно-эмоционального критерия относятся:<br/>– дивергентное мышление;<br/>– легкость в использовании ассоциаций (ассоциативная и экспрессивная беглость);<br/>– особенности темперамента (пластичность, вариативность, эмоциональная устойчивость, склонность к напряженной деятельности, социальная энергичность);<br/>– эмпатия." \
               "<br/>К показателям личностно-креативного критерия относятся:<br/>– воображение;<br/>– критическое мышление;<br/>– стремление к независимости, отсутствие страха высказывать свою точку зрения на проблему;<br/>– надситуативная активность (инициативность, выход за пределы заданного);<br/>– внутренняя позиция творца (заинтересованность в решении проблемно-поисковых задач, тенденции к индивидуализации творческой деятельности)." \
               "<br/>Показателями мотивационно-ценностного критерия являются:<br/>– потребность в творческой деятельности;<br/>– потребность в участии в учебно-познавательной деятельности;<br/>– положительное отношение к обучению, школе, учителю, одноклассникам;<br/>– признание ценности творчества." \
               "<br/>Показателями деятельностно-процессуального критерия являются:" \
               "<br/>– творческая и познавательная самостоятельность;<br/>– освоение способов творческой деятельности;<br/>– качество выполняемых действий;<br/>– стремление к достижению цели, получению конкретных результатов своей деятельности;<br/>– навыки сотрудничества;<br/>– способность оптимизации своего поведения (навыки организации творческого процесса, гибкий выбор той или иной стратегии поведения, безболезненный отказ от неэффективного способа действия)." \
               "<br/>К показателям рефлексивного критерия относятся:<br/>– особенности эмоционально-ценностного отношения к себе (уровень самооценки, её адекватность);<br/>– стремление к самообразованию, саморазвитию;<br/>– умение объективно оценить свой и чужой творческий продукт."
        results = []
        overall_results = []
        buffer = io.BytesIO()
        for i in range(1, 12):
            try:
                result = PupilResult.objects.get(pupil=pupil, result_name_id=i).result
            except PupilResult.DoesNotExist:
                result = 0
            results.append(result)
        for i in range(1, 6):
            try:
                overall = Overall.objects.get(pupil=pupil, criteria_id=i).result
            except Overall.DoesNotExist:
                overall = 0
            overall_results.append(overall)

        chart = make_radar_chart1(overall_results)

        b = pdf_report(results)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline;'
        pdf = canvas.Canvas(buffer, pagesize=A4)
        pdfmetrics.registerFont(TTFont('TNR', 'times.ttf'))
        pdf.setFont("TNR", 14)
        my_Style = ParagraphStyle('style1',
                                  style='style1',
                                  backColor='#F1F1F1',
                                  fontName='TNR',
                                  fontSize=12,
                                  borderColor='#8AFF8A',
                                  borderWidth=1,
                                  borderPadding=(10, 10, 10),
                                  leading=10,
                                  alignment=TA_CENTER
                                  )

        pdf.setTitle(pupil.fio + " | Оценка творческих способностей")
        pdf.drawImage(pupil.profile_pic.path, x=70, y=600, width=200, height=200, preserveAspectRatio=True, mask='auto')
        pdf.drawImage(chart, x=300, y=580, width=250, height=250, preserveAspectRatio=True, mask='auto')
        pdf.drawString(x=180, y=555, text=pupil.classroom.name)
        pdf.drawString(x=70, y=555, text=pupil.classroom.school.name)
        pdf.drawString(x=70, y=570, text=pupil.fio)
        p = Paragraph(text, my_Style)
        p.wrapOn(pdf, 450, 150)
        p.drawOn(pdf, x=80, y=150)
        pdf.showPage()
        score = 0
        # for i in results:
        #     if i == 0:
        #         score += 1
        # if score >= 1:
        #     pdf.setFont("TNR", 14)
        #     pdf.drawString(x=40, y=780, text="Для получения аналитической статистики необходимо получить все результаты тестов!")
        #     pdf.save()
        # else:
        pdf.setFont("TNR", 14)
        pdf.drawString(x=70, y=780, text="Уровень притязаний")
        p1 = Paragraph(b[0], my_Style)
        p1.wrapOn(pdf, 450, 650)
        p1.drawOn(pdf, x=80, y=650)

        pdf.drawString(x=70, y=600, text="Уровень самооценки")
        p2 = Paragraph(b[1], my_Style)
        p2.wrapOn(pdf, 450, 500)
        p2.drawOn(pdf, x=80, y=500)

        pdf.drawString(x=70, y=450, text="Разница")
        p3 = Paragraph(b[2], my_Style)
        p3.wrapOn(pdf, 450, 350)
        p3.drawOn(pdf, x=80, y=350)
        pdf.showPage()

        pdf.setFont("TNR", 14)
        pdf.drawString(x=70, y=780, text="Темперамент")
        p1 = Paragraph(b[3], my_Style)
        p1.wrapOn(pdf, 450, 100)
        p1.drawOn(pdf, x=80, y=100)

        pdf.setFont("TNR", 14)
        pdf.drawString(x=70, y=600, text="Нейротизм")
        p1 = Paragraph(b[4], my_Style)
        p1.wrapOn(pdf, 450, 400)
        p1.drawOn(pdf, x=80, y=400)

        chart1 = bar1(results[2], results[0], results[1])
        chart2 = temperament_circle1(results[0], results[1])
        pdf.setFont("TNR", 14)
        pdf.drawString(x=70, y=300, text="Шкала искренности")
        p1 = Paragraph(b[5], my_Style)
        p1.wrapOn(pdf, 450, 300)
        p1.drawOn(pdf, x=80, y=300)
        pdf.drawImage(chart2, x=70, y=600, width=200, height=200, preserveAspectRatio=True, mask='auto')
        pdf.drawImage(chart1, x=300, y=580, width=250, height=250, preserveAspectRatio=True, mask='auto')

        chart3 = bar2(results[4], results[5], results[6])
        pdf.showPage()
        pdf.setFont("TNR", 14)
        pdf.drawString(x=70, y=750, text="Оценка потребности в достижении успеха")
        p1 = Paragraph(b[6], my_Style)
        p1.wrapOn(pdf, 450, 700)
        p1.drawOn(pdf, x=80, y=700)
        pdf.drawString(x=70, y=650, text="Уровень креативности")
        p1 = Paragraph(b[7], my_Style)
        p1.wrapOn(pdf, 450, 600)
        p1.drawOn(pdf, x=80, y=600)
        pdf.drawImage(chart3, x=150, y=300, width=300, height=300, preserveAspectRatio=True, mask='auto')
        text = "0-20 баллов - низкие значения <br/>" \
               "21-49 баллов - средние значения <br/>" \
               "50-67 баллов - высокие значения <br/>"
        self = "Направленность на себя связывается с преобладанием мотивов собственного благополучия, стремления к личному" \
               " первенству, престижу. Такой человек чаще всего бывает занят самим собой, своими чувствами и переживаниями и" \
               " мало реагирует на потребности людей вокруг себя. В работе видит прежде всего возможность удовлетворить свои" \
               " притязания и амбиции. Характерна агрессивность в достижении статуса, властность, склонность к соперничеству," \
               " раздражительность, тревожность.<br/><br/>" \
               "Направленность на взаимодействие имеет место тогда, когда поступки человека определяются потребностью в" \
               " общении, стремлением поддерживать хорошие отношения с товарищами по работе. Такой человек проявляет" \
               " интерес к совместной деятельности, иногда в ущерб выполнению своих должностных обязанностей. Характерно" \
               " оказание искренней помощи людям, ориентация на социальное одобрение, зависимость от группы, потребность" \
               " в привязанности и эмоциональных отношениях.<br/><br/>" \
               "Направленность на задачу отражает преобладание мотивов, порождаемых самой деятельностью, увлечение" \
               " процессом деятельности, бескорыстное стремление к познанию, овладению новыми умениями и навыками." \
               " Характерна заинтересованность в решении деловых проблем, выполнение работы как можно лучше, стремление" \
               " добивается наибольшей продуктивности группы, ориентация на деловое сотрудничество, способность отстаивать" \
               " в интересах дела точку зрения, которую считает полезной для выполнения поставленной задачи."
        p2 = Paragraph(text, my_Style)
        p2.wrapOn(pdf, 450, 300)
        p2.drawOn(pdf, x=80, y=300)
        p3 = Paragraph(self, my_Style)
        p3.wrapOn(pdf, 450, 50)
        p3.drawOn(pdf, x=80, y=50)
        pdf.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='hello.pdf')
    except Pupil.DoesNotExist:
        content = {'Error': 'No such Pupil'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)
