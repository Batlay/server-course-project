import base64
import io
from datetime import datetime
import reportlab.rl_config
import reportlab
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.http import HttpResponse, FileResponse, JsonResponse
from reportlab.lib.colors import Color
from reportlab.lib.enums import TA_JUSTIFY
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
from django.templatetags.static import static
from .models import Post, Teacher, Pupil, Test_Info, ActivityTest, MotivationTest, TemperamentTest, Overall, \
    Criteria, PupilResult, InfoResult, School, Classroom
from .report import make_radar_chart, bar2, make_radar_chart1, pdf_report, bar1, temperament_circle1, bar
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
            'Endpoint': '/pupils/create/',
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
            'Endpoint': '/pupils/chart/id',
            'method': 'GET',
            'body': None,
            'description': 'Returns chart pupil'
        },
        {
            'Endpoint': '/pupils/result/id',
            'method': 'GET',
            'body': None,
            'description': 'Returns result pupil'
        },
        {
            'Endpoint': '/pupils/form/results/',
            'method': 'POST',
            'body': {'id': ''},
            'description': 'Returns form result pupil'
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
            'Endpoint': '/tests/results/',
            'method': 'POST',
            'body': {'id': ''},
            'description': 'Results Info'
        },
        {
            'Endpoint': '/tests/test4/',
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
        {
            'Endpoint': '/pupils/form/id/',
            'method': 'POST',
            'body': None,
            'description': 'Returns form answers'
        },
        {
            'Endpoint': '/pupils/report/id/',
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
    ]

    return Response(routes)


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
    notes = Post.objects.all()
    note = ''
    for i in notes:
        date_field = i.created_on.strftime(format="%d-%m-%Y %H:%M:%S")
        if date_field == pk:
            note = i
    serializer = PostSerializer(note, many=False)
    return Response(serializer.data)


@api_view(['GET'])
def getPupilNote(request, pk):
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

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)
    else:
        content = {'Error': 'Пользователь с таким логином и паролем не найден. Попробуйте ещё раз.'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def ResetPassword(request):
    data = request.data
    email = data['email']

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
    schools = School.objects.all().order_by('name')

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
def getPupilChart(request, pk):
    self = 0
    task = 0
    interaction = 0
    try:
        pupil = Pupil.objects.get(id=pk)

        for i in range(1, 6):
            try:
                self = PupilResult.objects.get(pupil=pupil, result_name_id=5).result
                task = PupilResult.objects.get(pupil=pupil, result_name_id=6).result
                interaction = PupilResult.objects.get(pupil=pupil, result_name_id=7).result
            except PupilResult.DoesNotExist:
                content = {'Error': 'Результаты не найдены'}
                return Response(content)
        chart = bar(self, interaction, task)
        return Response(chart)
    except Pupil.DoesNotExist:
        content = {'Error': 'Нет такого ученика'}
        return Response(content)


@api_view(['GET'])
def getPupilResult(request, pk):
    try:
        pupil = Pupil.objects.get(id=pk)

        a = []
        for i in range(1, 12):
            try:
                result = PupilResult.objects.get(pupil=pupil, result_name_id=i).result
            except PupilResult.DoesNotExist:
                result = 0
            a.append(result)
        return Response(a)
    except Pupil.DoesNotExist:
        return Response()


@api_view(['POST'])
def addPupil(request):
    all_data = request.data
    data = all_data['newPupil']
    try:
        Pupil.objects.get(email=data['email'])
        content = {'Пользователь с таким email уже существует'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    except Pupil.DoesNotExist:
        Pupil.objects.create(
            fio=data['fio'],
            phone=data['phone'],
            email=data['email'],
        )

        image_data = data['profile_pic']
        image = ContentFile(base64.b64decode(image_data))
        file_name = data['fio'] + ".png"

        userdata = all_data['userdata']['id']
        current_user = User.objects.get(id=userdata)
        teacher_details = get_object_or_404(Teacher, user=current_user)
        classroom = teacher_details.classroom

        pupil = Pupil.objects.get(email=data['email'])
        user = User.objects.create_user(data['email'], data['email'], data['email'])
        pupil.classroom = classroom
        pupil.user = user
        pupil.save()
        my_group = Group.objects.get(name='student')
        my_group.user_set.add(user)
        if image_data != '':
            pupil.profile_pic.save(file_name, image, save=True)

        serializer = PupilSerializer(pupil, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def getTests(request):
    tests = Test_Info.objects.all()

    serializer = TestInfoSerializer(tests, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def getTestResults(request):
    array = ['Рефлексивный', 'Когнитивно-эмоциональный', 'Мотивационно-ценностный', 'Деятельностно-процессуальный']

    data = request.data
    id_user = data['id']
    current_user = User.objects.get(id=id_user)
    pupil = get_object_or_404(Pupil, user=current_user)
    overall = Overall.objects.filter(pupil=pupil)
    results = []
    index = 0
    for i in array:
        for o in overall:
            if i == o.criteria.name:
                results.append(o.result)
        if len(results) == index:
            results.append(0)
        index += 1

    return Response(results)


@api_view(['POST'])
def getFormResults(request):
    data = request.data
    id_user = data['id']
    current_user = User.objects.get(id=id_user)
    teacher_details = get_object_or_404(Teacher, user=current_user)
    classroom = teacher_details.classroom
    pupils = Pupil.objects.filter(classroom=classroom).order_by('fio')
    results = []
    for pupil in pupils:
        try:
            overall = Overall.objects.get(pupil=pupil, criteria_id=2)
            results.append(overall.result)
        except Overall.DoesNotExist:
            results.append(0)

    return Response(results)


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

    mark = 0
    score = 0

    for i in test:
        if str(i.id) in data['answers']:
            if (data['answers'][str(i.id)] == "Да" and i.yes) or (data['answers'][str(i.id)] == "Нет" and i.no):
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

    res = InfoResult.objects.get(id=8)

    userdata = data['userdata']['id']
    current_user = User.objects.get(id=userdata)
    pupil_details = get_object_or_404(Pupil, user=current_user)

    check_object = Overall.objects.filter(pupil=pupil_details, criteria=criteria)
    check_object1 = PupilResult.objects.filter(pupil=pupil_details, result_name=res)

    if check_object or check_object1:
        content = {'Error': 'Результаты уже были сохранены'}
        return Response(content)
    else:
        result = PupilResult(pupil=pupil_details, result_name=res, result=mark)
        result.save()
        overall = Overall(pupil=pupil_details, criteria=criteria, result=score)
        overall.save()

    return Response('Результаты успешно сохранены')


@api_view(['GET'])
def getTest3(request):
    test = MotivationTest.objects.all()
    serializer = Test3Serializer(test, many=True)

    return Response(serializer.data)


@api_view(['POST'])
def Test3Answers(request):
    data = request.data
    criteria = Criteria.objects.get(id=3)

    key1 = "1А 2Б 3А 4А 5Б 6В 7А 8В 9В 10В 11Б 12Б 13В 14В 15А " \
           "16Б 17А 18А 19А 20В 21В 22В 23Б 24В 25Б 26Б 27А 28Б 29А 30В"
    key2 = "1В 2В 3В 4Б 5А 6А 7В 8Б 9А 10Б 11В 12А 13А 14А 15В" \
           "16В 17В 18В 19Б 20Б 21А 22А 23В 24А 25А 26А 27Б 28В 29В 30А"
    key3 = "1Б 2А 3Б 4В 5В 6Б 7Б 8А 9Б 10А 11А 12В 13Б 14Б 15Б" \
           "16А 17Б 18Б 19В 20А 21Б 22Б 23А 24Б 25В 26В 27В 28А 29Б 30Б"
    answers = ""
    answers1 = ""
    section1 = 0
    section2 = 0
    section3 = 0
    score = 0

    # Получение данных
    data1 = data['answers']
    data2 = data['answers2']

    for i in range(len(data1)):
        answer = data1[str(i + 1)]
        answers += answer + " "

    for i in range(len(data2)):
        answer1 = data2[str(i + 1)]
        answers1 += answer1 + " "

    # Запись ответов по категориям

    k1 = key1.split()
    k2 = key2.split()
    k3 = key3.split()
    y = answers.split()
    y1 = answers1.split()

    for i in y:
        for j in k1:
            if i == j:
                section1 += 1
    for i in y1:
        for j in k1:
            if i == j:
                section1 -= 1
    for i in y:
        for j in k2:
            if i == j:
                section2 += 1
    for i in y1:
        for j in k2:
            if i == j:
                section2 -= 1
    for i in y:
        for j in k3:
            if i == j:
                section3 += 1
    for i in y1:
        for j in k3:
            if i == j:
                section3 -= 1

    section1 += 30
    section2 += 30
    section3 += 30

    for i in section1, section2, section3:
        if 21 <= i <= 49:
            score += 1
        elif 50 <= i <= 67:
            score += 2

    userdata = data['userdata']['id']
    current_user = User.objects.get(id=userdata)
    pupil_details = get_object_or_404(Pupil, user=current_user)

    self = InfoResult.objects.get(id=5)
    task = InfoResult.objects.get(id=6)
    interaction = InfoResult.objects.get(id=7)

    check_object = Overall.objects.filter(pupil=pupil_details, criteria=criteria)
    check_object1 = PupilResult.objects.filter(pupil=pupil_details, result_name=self)
    check_object2 = PupilResult.objects.filter(pupil=pupil_details, result_name=interaction)
    check_object3 = PupilResult.objects.filter(pupil=pupil_details, result_name=task)

    if check_object or check_object1 or check_object2 or check_object3:
        content = {'Error': 'Результаты уже были сохранены'}
        return Response(content)
    else:
        result1 = PupilResult(pupil=pupil_details, result_name=self, result=section1)
        result2 = PupilResult(pupil=pupil_details, result_name=interaction, result=section2)
        result3 = PupilResult(pupil=pupil_details, result_name=task, result=section3)
        result1.save()
        result2.save()
        result3.save()
        overall = Overall(pupil=pupil_details, criteria=criteria, result=score)
        overall.save()

    # Сохранить оценку
    return Response('Результаты успешно сохранены')


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
        if str(i.id) in data['answers']:
            if data['answers'][str(i.id)] == "Да":
                if i.type == "Экстраверсия - интроверсия" and i.key:
                    mark1 += 1
                elif i.type == "Нейротизм" and i.key:
                    mark2 += 1
                elif i.type == "Шкала лжи" and i.key:
                    mark3 += 1

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

    intr = InfoResult.objects.get(id=1)
    neur = InfoResult.objects.get(id=2)
    lie = InfoResult.objects.get(id=3)

    userdata = data['userdata']['id']
    current_user = User.objects.get(id=userdata)
    pupil_details = get_object_or_404(Pupil, user=current_user)

    check_object = Overall.objects.filter(pupil=pupil_details, criteria=criteria)
    check_object1 = PupilResult.objects.filter(pupil=pupil_details, result_name=intr)
    check_object2 = PupilResult.objects.filter(pupil=pupil_details, result_name=neur)
    check_object3 = PupilResult.objects.filter(pupil=pupil_details, result_name=lie)
    if check_object or check_object1 or check_object2 or check_object3:
        content = {'Error': 'Результаты уже были сохранены'}
        return Response(content)
    else:
        result1 = PupilResult(pupil=pupil_details, result_name=intr, result=mark1)
        result2 = PupilResult(pupil=pupil_details, result_name=neur, result=mark2)
        result3 = PupilResult(pupil=pupil_details, result_name=lie, result=mark3)
        result1.save()
        result2.save()
        result3.save()
        overall = Overall(pupil=pupil_details, criteria=criteria, result=score)
        overall.save()

    return Response('Результаты успешно сохранены')


@api_view(['POST'])
def getForm(request, pk):
    data = request.data
    criteria = Criteria.objects.get(id=2)
    result_name = InfoResult.objects.get(id=4)

    score = 0
    sum = 0

    for i in range(10):
        answer = data[str(i + 1)]
        sum += int(answer)

    if 34 <= sum <= 40:
        score = 5
    elif 27 <= sum <= 33:
        score = 4
    elif 21 <= sum <= 26:
        score = 3
    elif 16 <= sum <= 20:
        score = 2
    elif 10 <= sum <= 15:
        score = 1

    pupil_details = get_object_or_404(Pupil, id=pk)

    check_object = Overall.objects.filter(pupil=pupil_details, criteria=criteria)
    check_object1 = PupilResult.objects.filter(pupil=pupil_details, result_name=result_name)
    if check_object or check_object1:
        content = {'Error': 'Результаты уже были сохранены'}
        return Response(content)
    else:
        result = PupilResult(pupil=pupil_details, result_name=result_name, result=sum)
        result.save()
        overall = Overall(pupil=pupil_details, criteria=criteria, result=score)
        overall.save()

        return Response('Результаты успешно сохранены')


@api_view(['POST'])
def Test1Answers(request):
    data = request.data

    criteria = Criteria.objects.get(id=5)
    self_esteem = 0
    expectations = 0
    score = 0

    area1 = data['answers'][0:6]
    area2 = data['answers'][6:12]

    for i in area1:
        self_esteem += int(i)
    for i in area2:
        expectations += int(i)
    self_esteem /= 6
    expectations /= 6

    if self_esteem > expectations:
        diff = round(self_esteem, 0) - round(expectations, 0)
    else:
        diff = round(expectations, 0) - round(self_esteem, 0)

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

    userdata = data['userdata']['id']
    current_user = User.objects.get(id=userdata)
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
        text = "К показателям когнитивно-эмоционального критерия относятся:<br/>" \
               "&nbsp;&nbsp;&nbsp;– дивергентное мышление;<br/>" \
               "&nbsp;&nbsp;&nbsp;– легкость в использовании ассоциаций (ассоциативная и экспрессивная беглость);<br/>" \
               "&nbsp;– особенности темперамента (пластичность, вариативность, эмоциональная устойчивость, склонность к напряженной деятельности, социальная энергичность);<br/>" \
               "&nbsp;&nbsp;&nbsp;– эмпатия." \
               "<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" \
               "<br/>К показателям личностно-креативного критерия относятся:<br/>" \
               "&nbsp;&nbsp;&nbsp;– воображение;<br/>" \
               "&nbsp;&nbsp;&nbsp;– критическое мышление;<br/>" \
               "&nbsp;&nbsp;&nbsp;– стремление к независимости, отсутствие страха высказывать свою точку зрения на проблему;<br/>" \
               "&nbsp;&nbsp;&nbsp;– надситуативная активность (инициативность, выход за пределы заданного);<br/>" \
               "&nbsp;&nbsp;&nbsp;– внутренняя позиция творца (заинтересованность в решении проблемно-поисковых задач, тенденции к индивидуализации творческой деятельности)." \
               "<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br/>" \
               "Показателями мотивационно-ценностного критерия являются:<br/>" \
               "&nbsp;&nbsp;&nbsp;– потребность в творческой деятельности;<br/>" \
               "&nbsp;&nbsp;&nbsp;– потребность в участии в учебно-познавательной деятельности;<br/>" \
               "&nbsp;&nbsp;&nbsp;– положительное отношение к обучению, школе, учителю, одноклассникам;<br/>" \
               "&nbsp;&nbsp;&nbsp;– признание ценности творчества." \
               "<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br/>" \
               "Показателями деятельностно-процессуального критерия являются:" \
               "<br/>&nbsp;&nbsp;&nbsp;– творческая и познавательная самостоятельность;<br/>" \
               "&nbsp;&nbsp;&nbsp;– освоение способов творческой деятельности;<br/>" \
               "&nbsp;&nbsp;&nbsp;– качество выполняемых действий;<br/>" \
               "&nbsp;&nbsp;&nbsp;– стремление к достижению цели, получению конкретных результатов своей деятельности;<br/>" \
               "&nbsp;&nbsp;&nbsp;– навыки сотрудничества;<br/>" \
               "&nbsp;&nbsp;&nbsp;– способность оптимизации своего поведения (навыки организации творческого процесса, гибкий выбор той или иной стратегии поведения, безболезненный отказ от неэффективного способа действия)." \
               "<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br/>" \
               "К показателям рефлексивного критерия относятся:<br/>" \
               "&nbsp;&nbsp;&nbsp;– особенности эмоционально-ценностного отношения к себе (уровень самооценки, её адекватность);<br/>" \
               "&nbsp;&nbsp;&nbsp;– стремление к самообразованию, саморазвитию;<br/>" \
               "&nbsp;&nbsp;&nbsp;– умение объективно оценить свой и чужой творческий продукт."
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
        url='https://newway.herokuapp.com/static/fonts/times.ttf'
        # pdfmetrics.registerFont(TTFont('TNR', 'C:/Users/Gleb/Documents/newway/static/fonts/times.ttf'))
        pdfmetrics.registerFont(TTFont('TNR', url))
        pdf.setFont("TNR", 14)
        my_Style = ParagraphStyle('style1',
                                  style='style1', alignment=TA_JUSTIFY,
                                  fontName='TNR',
                                  backColor=None,
                                  borderColor=None,
                                  borderPadding=0,
                                  borderRadius=None,
                                  borderWidth=0,
                                  endDots=None,
                                  fontSize=12,
                                  textColor=Color(0, 0, 0, 1),
                                  wordWrap=None,
                                  leading=11,
                                  spaceAfter=5,
                                  firstLineIndent=15
                                  )
        my_Style1 = ParagraphStyle('style1',
                                   style='style1', alignment=0,
                                   backColor=None,
                                   fontName='TNR',
                                   borderColor=None,
                                   borderPadding=0,
                                   borderRadius=None,
                                   borderWidth=0,
                                   endDots=None,
                                   fontSize=12,
                                   textColor=Color(0, 0, 0, 1),
                                   wordWrap=None,
                                   leading=11,
                                   spaceAfter=5,
                                   firstLineIndent=0
                                   )
        pdf.setTitle(pupil.fio + " | Оценка творческих способностей")
        pdf.drawImage('https://newway.herokuapp.com/static' + pupil.profile_pic.url, x=70, y=600, width=200, height=200,
                      preserveAspectRatio=True, mask='auto')
        pdf.drawImage(chart, x=300, y=580, width=250, height=250, preserveAspectRatio=True, mask='auto')
        pdf.drawString(x=180, y=555, text=pupil.classroom.name)
        pdf.drawString(x=70, y=555, text=pupil.classroom.school.name)
        pdf.drawString(x=70, y=570, text=pupil.fio)
        p = Paragraph(text, my_Style1)
        w, h = p.wrap(450, 700)
        p.drawOn(pdf, x=80, y=530 - h)
        pdf.showPage()

        pdf.setFont("TNR", 14)
        pdf.drawString(x=385, y=800, text="Рефлексивный критерий")
        pdf.line(70, 795, 530, 795)

        pdf.drawString(x=70, y=750, text="Уровень самооценки (" + str(results[8]) + ")")
        p1 = Paragraph(b[0], my_Style)
        w, h = p1.wrap(200, 400)
        p1.drawOn(pdf, x=70, y=730 - h)

        pdf.drawString(x=320, y=750, text="Уровень притязаний (" + str(results[9]) + ")")
        p2 = Paragraph(b[1], my_Style)
        w, h = p2.wrap(200, 400)
        p2.drawOn(pdf, x=320, y=730 - h)

        pdf.drawString(x=70, y=410, text="Разница (" + str(results[10]) + ")")
        p3 = Paragraph(b[2], my_Style)
        w, h = p3.wrap(200, 400)
        p3.drawOn(pdf, x=70, y=390 - h)
        pdf.showPage()

        pdf.setFont("TNR", 14)
        pdf.drawString(x=300, y=800, text="Когнитивно-эмоциональный критерий")
        pdf.line(70, 795, 530, 795)

        pdf.drawString(x=70, y=560, text="Темперамент")
        p1 = Paragraph(b[3], my_Style)
        w, h = p1.wrap(200, 400)
        p1.drawOn(pdf, x=70, y=540 - h)

        pdf.setFont("TNR", 14)
        pdf.drawString(x=320, y=560, text="Нейротизм")
        p1 = Paragraph(b[4], my_Style)
        w, h = p1.wrap(200, 400)
        p1.drawOn(pdf, x=320, y=540 - h)

        pdf.setFont("TNR", 14)
        pdf.drawString(x=70, y=210, text="Шкала искренности")
        p1 = Paragraph(b[5], my_Style)
        w, h = p1.wrap(200, 400)
        p1.drawOn(pdf, x=70, y=190 - h)

        chart1 = bar1(results[2], results[0], results[1])
        chart2 = temperament_circle1(results[0], results[1])
        pdf.drawImage(chart1, x=300, y=550, width=250, height=250, preserveAspectRatio=True, mask='auto')
        pdf.drawImage(chart2, x=70, y=550, width=200, height=280, preserveAspectRatio=True, mask='auto')
        pdf.showPage()

        pdf.setFont("TNR", 14)
        pdf.drawString(x=35, y=800,
                       text="Деятельностно-процессуальный / Личностно-креативный / Мотивационно-ценностный")
        pdf.line(70, 795, 530, 795)
        pdf.drawString(x=70, y=750, text="Потребность в достижении успеха (" + str(results[7]) + "). ")
        p1 = Paragraph(b[6], my_Style)
        w, h = p1.wrap(200, 400)
        p1.drawOn(pdf, x=70, y=730 - h)

        pdf.drawString(x=320, y=750, text="Уровень креативности (" + str(results[3]) + ").")
        p1 = Paragraph(b[7], my_Style)
        w, h = p1.wrap(200, 400)
        p1.drawOn(pdf, x=320, y=730 - h)

        pdf.drawString(x=70, y=400, text="Определение направленности")
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
        p2 = Paragraph(text, my_Style1)
        w, h = p2.wrap(452, 400)
        p2.drawOn(pdf, x=70, y=380 - h)
        p3 = Paragraph(self, my_Style)
        w, h = p3.wrap(452, 400)
        p3.drawOn(pdf, x=70, y=270 - h)

        chart3 = bar2(results[4], results[5], results[6])
        pdf.drawImage(chart3, x=315, y=240, width=200, height=200, preserveAspectRatio=True, mask='auto')
        pdf.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='hello.pdf')
    except Pupil.DoesNotExist:
        content = {'Error': 'No such Pupil'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)
