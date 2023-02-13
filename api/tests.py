from django.test import TestCase, Client
from rest_framework.reverse import reverse
from rest_framework import status
from django.contrib.auth.models import User
from api.serializers import PupilSerializer
from .models import Pupil, Teacher, School, Classroom


import logging

logger = logging.getLogger(__name__)

# initialize the APIClient app
client = Client()


class GetPupilsTest(TestCase):

    def setUp(self):
        School.objects.create(
            name='Школа 1',
        )
        Classroom.objects.create(
            name='11 Б',
            school_id=1
        )

        Pupil.objects.create(
            fio='Casper', phone='1234', email='Bull Dog', classroom_id=1)
        Pupil.objects.create(
            fio='Muffin', phone='1234', email='Gradane', classroom_id=1)
        Pupil.objects.create(
            fio='Rambo', phone='1234', email='Labrador', classroom_id=1)
        Pupil.objects.create(
            fio='Ricky', phone='1234', email='Labrafr', classroom_id=1)

        self.user = User.objects.create_user(username='john',
                                             email='jo...@doe.info',
                                             password='doe')
        Teacher.objects.create(
            user_id=1,
            fio='Casper',
            phone='1234',
            email='Bull Do',
            classroom_id=1
        )

    def test_get_all_pupils(self):
        # get API response
        response = client.post(reverse('classroom'), data={"id": 1})
        print(response.data)
        # get data from db
        pupils = Pupil.objects.all()
        serializer = PupilSerializer(pupils, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
