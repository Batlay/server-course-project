from django.urls import path
from . import views

urlpatterns = [
    path('', views.getRoutes, name='routes'),
    path('notes/', views.getNotes, name='notes'),
    path('notes/<str:pk>', views.getNote, name='note'),
    path('notes/create/<str:pk>', views.createNote, name='create-note'),
    path('login/', views.loginPage, name='login'),
    path('pupils/', views.getPupils, name='classroom'),
    path('pupils/<str:pk>', views.getPupil, name='pupil'),
    path('pupils/form/<str:pk>', views.getForm, name='form'),
    path('pupils/report/<str:pk>', views.getPdf, name='pdf'),
    path('pupils/overall/<str:pk>', views.getPupilOverall, name='pupil_overall'),
    path('pupils/chart/<str:pk>', views.getPupilChart, name='chart'),
    path('pupils/result/<str:pk>', views.getPupilResult, name='pupil_result'),
    path('pupils/form/results/', views.getFormResults, name='result'),
    path('pupils/create/', views.addPupil, name='add-pupil'),
    path('notes/person/<str:pk>', views.getPupilNote, name='pupil_note'),
    path('tests/', views.getTests, name='tests'),
    path('tests/results/', views.getTestResults, name='results'),
    path('tests/test4/', views.getTest4, name='test4'),
    path('tests/test4/answers/', views.Test4Answers, name='test4_answers'),
    path('tests/test3/', views.getTest3, name='test3'),
    path('tests/test3/answers/', views.Test3Answers, name='test3_answers'),
    path('tests/test2/', views.getTest2, name='test2'),
    path('tests/test2/answers/', views.Test2Answers, name='test2_answers'),
    path('tests/test1/answers/', views.Test1Answers, name='test1_answers'),
    path('user-forgot-password/', views.ResetPassword, name='reset_password'),
    path('user-change-password/<str:pk>', views.ChangePassword, name='change_password'),
    path('schools/', views.getSchools, name='schools'),
    path('schools/<str:pk>', views.getClassrooms, name='classrooms'),
    path('classrooms/<str:pk>', views.getClassroomPupils, name='pupils'),
]
