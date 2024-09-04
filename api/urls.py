from django.urls import path,include
from . import views
from rest_framework.routers import SimpleRouter,DefaultRouter
from pprint import pprint


router = DefaultRouter()
router.register('customer',views.CustomerDetailViewSet)
router.register('job',views.JobViewSet)
router.register('create-job',views.CreateJobViewSet)



urlpatterns = [
    path('',include(router.urls)),
    path('master-data/',views.MasterDataView.as_view()),
    # path('my-jobs/',views.EmployeeJobListAPIView.as_view())
    path('upload-excel/',views.UploadExcelView.as_view(), name='upload-excel'),
   
]
