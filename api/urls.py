from django.urls import path,include
from . import views
from rest_framework.routers import SimpleRouter,DefaultRouter
from pprint import pprint


router = DefaultRouter()
router.register('customer',views.CustomerDetailViewSet)
router.register('job',views.JobViewSet)
router.register('create-job',views.CreateJobViewSet)
router.register('well-info',views.WellinfoViewSet)
router.register('employee',views.EmployeeViewSet)
router.register('surveyinfo',views.SurveyInfoSerializer)


urlpatterns = [
    path('',include(router.urls)),
    path('master-data/',views.MasterDataView.as_view()),
    # path('my-jobs/',views.EmployeeJobListAPIView.as_view())
    path('upload-excel/',views.UploadExcelView.as_view(), name='upload-excel'),
    path('upload-excel/<str:job_number>/',views.UploadExcelView.as_view()),
    path('surveycalculation/',views.SurveyCalculationView.as_view()),
     path('surveycalculation/<str:job_number>/',views.SurveyCalculationView.as_view()),
    path("surveycalculationdetails/",views.SurveyCalculationDetailsView.as_view())
]
