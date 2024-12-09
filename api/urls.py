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
router.register('asset-master',views.GetAssetHeaderView)
router.register('gyro-data',views.GyroDataviewSet)
router.register('vehicle-data',views.VehicleViewSet),
router.register('asset',views.GetAssetMaster)
# router.register('interpolation',views.InterPolationDataHeaderViewSet)




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

    path("surveycalculationdetails/<str:job_number>/<int:run_number>/",views.SurveyCalculationDetailsView.as_view()),

    path("create-job-detail/",views.CombinedJobCreationView.as_view()),

    path('tieOnInformationdetail/<str:job_number>/<int:run_number>/',views.TieOnInformationDetailView.as_view()),

    path('asset-info/<str:header>/',views.GetAssetDetailsView.as_view()),

    path('get-jobassets/<str:job_number>/',views.UpdateAsset.as_view()),

    # path('soe/<str:job_number>/',views.SoeViewSet.as_view()),

    path('interpolation/<str:job_number>/<int:run_number>/',views.InterPolationDataHeaderViewSet.as_view()),

    path('interpolation-details/<str:job_number>/<int:run_number>/<int:resolution>/<int:header_id>/',views.InterPolationDataDeatilsViewSet.as_view()),
    
    # path('save-calculation/', views.SaveCalculationViewSet.as_view(), name='save-calculation'),

    path('comaprison/',views.ComparisonViewSet.as_view())
    
  
]


 # path('my-jobs/',views.EmployeeJobListAPIView.as_view())