from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from  .serializer import CustomerSerializer,UnitOfMeasureSeializer,JobInfoSerializer,JodDetailSerializer,ServiceTypeSerializer,RigMasterSerilalizer,WelltypeSerializer,ToolTypeSerializer,HoleSectionSerializer,SurveyTypeSerializer,CreateJobSerializer,SurveyInitialDataSerializer
from rest_framework.viewsets import ModelViewSet
from .models import JobInfo,CustomerMaster,UnitofMeasureMaster,ServiceType,RigMaster,WelltypeMaster,ToolMaster,HoleSection,SurveyTypes,CreateJob,SurveyInitialDataHeader,SurveyInitialDataDetail
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
import pandas as pd
from io import BytesIO
from rest_framework import status

class JobViewSet(ModelViewSet):
    queryset = JobInfo.objects.all()
    serializer_class = JobInfoSerializer

class CustomerDetailViewSet(ModelViewSet):
    queryset = CustomerMaster.objects.all()
    serializer_class = CustomerSerializer
    
class CreateJobViewSet(ModelViewSet):
    queryset = CreateJob.objects.all()
    serializer_class = CreateJobSerializer
   

class MasterDataView(APIView):
    def get(self,request):
        service_type = ServiceTypeSerializer(ServiceType.objects.all(),many=True).data
        unit_of_measure = UnitOfMeasureSeializer(UnitofMeasureMaster.objects.all(),many=True).data
        rig_master = RigMasterSerilalizer(RigMaster.objects.all(),many=True).data
        well_type = WelltypeSerializer(WelltypeMaster.objects.all(),many=True).data
        tools_type = ToolTypeSerializer(ToolMaster.objects.all(),many=True).data
        hole_section = HoleSectionSerializer(HoleSection.objects.all(),many=True).data
        survey_type = SurveyTypeSerializer(SurveyTypes.objects.all(),many=True).data
        data ={
            'service_type':service_type,
            'unit_of_measure ':unit_of_measure,
            'rig_master':rig_master,
            'well_type':well_type,
            'tools_type':tools_type,
            'hole_section':hole_section,
            'survey_type':survey_type
        }
        return Response(data)
# class EmployeeJobListAPIView(generics.ListAPIView):
#     serializer_class = JobInfoSerializer
    

#     def get_queryset(self):
#         return JobInfo.objects.filter(job_number__assign_to=self.request.user.employee)



# class UploadExcelView(APIView):
    
#     def post(self, request, *args, **kwargs):
#         file = request.FILES.get('file')
        
#         if file is None:
#             return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             df = pd.read_excel(BytesIO(file.read()), engine='openpyxl')
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
#         for _, row in df.iterrows():
#             data = {
#                 "depth": row.get("depth"),
#                 "Inc": row.get("Inc"),
#                 "AzG": row.get("AzG"),  
#             }
#             serializer = SurveyInitialDataSerializer(data=data)
#             if serializer.is_valid():
#                 serializer.save()
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         return Response({"status": "success"}, status=status.HTTP_201_CREATED)
class UploadExcelView(APIView):

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        job_number = request.data.get('job_number')  
        survey_type = request.data.get('survey_type')  
        if file is None:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(BytesIO(file.read()), engine='openpyxl')
        except Exception as e:
            return Response({"error": f"Error reading Excel file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        if not job_number or not survey_type:
            return Response({"error": "Missing job_number or survey_type"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            job = CreateJob.objects.get(job_number=job_number)
            survey_type = SurveyTypes.objects.get(id=survey_type)

            survey_header = SurveyInitialDataHeader.objects.create(
                job_number=job,
                survey_type=survey_type
            )

        except CreateJob.DoesNotExist:
            return Response({"error": f"Job with job_number {job_number} not found"}, status=status.HTTP_404_NOT_FOUND)
        except SurveyTypes.DoesNotExist:
            return Response({"error": "Survey type not found"}, status=status.HTTP_404_NOT_FOUND)

        errors = []
        success_count = 0
        for index, row in df.iterrows():
            try:
                depth = row.get("depth")
                inc = row.get("Inc")
                azg = row.get("AzG")
                g_t= row.get("G(t)")
                w_t = row.get("W(t)")

               
                SurveyInitialDataDetail.objects.create(
                    survey_type=survey_type,
                    job_number=job,
                    depth=depth,
                    Inc=inc,
                    AzG=azg,
                    g_t = g_t,
                    w_t = w_t
                )
                success_count += 1
            except Exception as e:
                errors.append({"row": index + 2, "error": str(e)})

        if errors:
            return Response({
                "status": "partial success",
                "success_count": success_count,
                "errors": errors
            }, status=status.HTTP_207_MULTI_STATUS)

        return Response({
            "status": "success",
            "success_count": success_count
        }, status=status.HTTP_201_CREATED)
