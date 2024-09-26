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
router.register('surveyinfo',views.SurveyInfoViewset)
router.register('tieoninfo',views.TieOnInformationView)


urlpatterns = [
    path('',include(router.urls)),
    path('master-data/',views.MasterDataView.as_view()),

    path('job-data/<str:job_number>/',views.JobDetailsView.as_view()),

    path('upload-excel/',views.UploadExcelView.as_view(), name='upload-excel'),

    path('upload-excel/<str:job_number>/',views.UploadExcelView.as_view()),

    path('upload-excel/<str:job_number>/<int:run_number>/', views.UploadExcelView.as_view(), name='upload-excel'),

    path('upload-excel/<str:job_number>/<int:run_number>/<int:data_id>/',views.UploadExcelView.as_view()),

    path('surveycalculation/',views.SurveyCalculationView.as_view()),

    path('surveycalculation/<str:job_number>/<int:run_number>/',views.SurveyCalculationView.as_view()),

    path("surveycalculationdetails/",views.SurveyCalculationDetailsView.as_view()),

    path("surveycalculationdetails/<str:job_number>/",views.SurveyCalculationDetailsView.as_view()),

    path("create-job-detail/",views.CombinedJobCreationView.as_view()),

    path('tieOnInformationdetail/<str:job_number>/<int:run_number>/',views.TieOnInformationDetailView.as_view())
    
    
]

 # path('my-jobs/',views.EmployeeJobListAPIView.as_view())