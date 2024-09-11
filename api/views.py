from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from  .serializer import CustomerSerializer,UnitOfMeasureSeializer,JobInfoSerializer,JodDetailSerializer,ServiceTypeSerializer,RigMasterSerilalizer,WelltypeSerializer,ToolTypeSerializer,HoleSectionSerializer,SurveyTypeSerializer,CreateJobSerializer,WellInfoSerializer,EmployeeSerializer
from rest_framework.viewsets import ModelViewSet
from .models import JobInfo,CustomerMaster,UnitofMeasureMaster,ServiceType,RigMaster,WelltypeMaster,ToolMaster,HoleSection,SurveyTypes,CreateJob,SurveyInitialDataHeader,SurveyInitialDataDetail,WellInfo,EmployeeMaster
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
import pandas as pd
from io import BytesIO
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAdminUser

class JobViewSet(ModelViewSet):
    queryset = JobInfo.objects.all()
    serializer_class = JobInfoSerializer
    lookup_field = 'job_number'

    # def get_object(self):
    #     job_number = self.kwargs.get(self.lookup_field)
    #     try:
    #         job = CreateJob.objects.get(job_number=job_number)
    #         return JobInfo.objects.get(job_number=job)
    #     except CreateJob.DoesNotExist:
    #         raise NotFound(f"Job with job_number {job_number} does not exist.")
    #     except JobInfo.DoesNotExist:
    #         raise NotFound(f"JobInfo for job_number {job_number} does not exist.")
class EmployeeViewSet(ModelViewSet):
    queryset = EmployeeMaster.objects.all()
    serializer_class = EmployeeSerializer
class CustomerDetailViewSet(ModelViewSet):
    queryset = CustomerMaster.objects.all()
    serializer_class = CustomerSerializer
    
class CreateJobViewSet(ModelViewSet):
    queryset = CreateJob.objects.all()
    serializer_class = CreateJobSerializer
    
    

class WellinfoViewSet(ModelViewSet):
    queryset = WellInfo.objects.all()
    serializer_class = WellInfoSerializer

class MasterDataView(APIView):
    def get(self,request):
        customers = CustomerSerializer(CustomerMaster.objects.all(),many=True).data
        service_type = ServiceTypeSerializer(ServiceType.objects.all(),many=True).data
        unit_of_measure = UnitOfMeasureSeializer(UnitofMeasureMaster.objects.all(),many=True).data
        rig_master = RigMasterSerilalizer(RigMaster.objects.all(),many=True).data
        well_type = WelltypeSerializer(WelltypeMaster.objects.all(),many=True).data
        tools_type = ToolTypeSerializer(ToolMaster.objects.all(),many=True).data
        hole_section = HoleSectionSerializer(HoleSection.objects.all(),many=True).data
        survey_type = SurveyTypeSerializer(SurveyTypes.objects.all(),many=True).data
        data ={
            'customers':customers,
            'service_type':service_type,
            'unit_of_measure ':unit_of_measure,
            'rig_master':rig_master,
            'well_type':well_type,
            'tools_type':tools_type,
            'hole_section':hole_section,
            'survey_type':survey_type
        }
        return Response(data)

class UploadExcelView(APIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        job_number = request.data.get('job_number')  
        survey_type_id = request.data.get('survey_type')

        if file is None:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(BytesIO(file.read()), engine='openpyxl')
        except Exception as e:
            return Response({"error": f"Error reading Excel file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        if not job_number or not survey_type_id:
            return Response({"error": "Missing job_number or survey_type"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            job = CreateJob.objects.get(job_number=job_number)
            survey_type_obj = SurveyTypes.objects.get(id=survey_type_id)
            survey_header = SurveyInitialDataHeader.objects.create(
                job_number=job,
                survey_type=survey_type_obj
            )
        except CreateJob.DoesNotExist:
            return Response({"error": f"Job with job_number {job_number} not found"}, status=status.HTTP_404_NOT_FOUND)
        except SurveyTypes.DoesNotExist:
            return Response({"error": "Survey type not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            well_info = WellInfo.objects.get(job_number=job)
        except WellInfo.DoesNotExist:
            return Response({"error": f"WellInfo for job_number {job_number} not found"}, status=status.HTTP_404_NOT_FOUND)
        except WellInfo.MultipleObjectsReturned:
            return Response({"error": "More than one WellInfo record found for the given job_number"}, status=status.HTTP_400_BAD_REQUEST)

        errors = []
        success_count = 0
        results = []
        # score_mapping = {
        #     "high": 1.5,
        #     "good": 1.2,
        #     "low": 1,
        #     "n/c": 0
        # }
        # total_g_t_score = 0
        # total_w_t_score = 0

        for index, row in df.iterrows():
            try:
                depth = row.get("depth")
                inc = row.get("Inc")
                azg = row.get("AzG")
                g_t = row.get("G(t)")
                w_t = row.get("W(t)")
                g_t_difference = round(well_info.get_G_t - g_t,2)
                w_t_difference = round(well_info.get_W_t - w_t,2)

                if -1 <= g_t_difference <= 1:
                    g_t_status = "high"
                elif -3 <= g_t_difference <= 3:
                    g_t_status = "good"
                elif -10 <= g_t_difference <= 10:
                    g_t_status = "low"
                else:
                    g_t_status = "n/c"

                if -1 <= w_t_difference <= 1:
                    w_t_status = "high"
                elif -5 <= w_t_difference <= 5:
                    w_t_status = "good"
                elif -10 <= w_t_difference <= 10:
                    w_t_status = "low"
                else:
                    w_t_status = "n/c"

                # current_g_t_score = score_mapping[g_t_status]
                # current_w_t_score = score_mapping[w_t_status]

                # total_g_t_score += current_g_t_score
                # total_w_t_score += current_w_t_score

                if g_t_status == "good" and w_t_status == "good":
                    overall_status = "PASS"
                elif (g_t_status == "good" and w_t_status == "high") or (g_t_status == "high" and w_t_status == "good"):
                    overall_status = "PASS"
                elif (g_t_status == "low" and w_t_status == "high") or (g_t_status == "high" and w_t_status == "low"):
                    overall_status = "PASS"
                elif (g_t_status == "low" and w_t_status == "low") or (g_t_status == "good" and w_t_status == "low"):
                    overall_status = "PASS"
                elif g_t_status == "high" and w_t_status == "high":
                    overall_status = "PASS"
                else:
                    overall_status = "REMOVE"

                detail = SurveyInitialDataDetail.objects.create(
                    header=survey_header,
                    job_number=job,
                    depth=depth,
                    Inc=inc,
                    AzG=azg,
                    g_t=g_t,
                    w_t=w_t,
                    g_t_difference=g_t_difference,
                    w_t_difference=w_t_difference,
                    g_t_status=g_t_status,
                    w_t_status=w_t_status,
                    status=overall_status
                )

                results.append({
                    "row": index + 2,
                    "depth": depth,
                    "inc": inc,
                    "azg": azg,
                    "g_t": g_t,
                    "w_t": w_t,
                    "g_t_status": g_t_status,
                    "w_t_status": w_t_status,
                    "g_t_difference": g_t_difference,
                    "w_t_difference": w_t_difference,
                    "status": overall_status
                })

                success_count += 1

            except Exception as e:
                errors.append({"row": index + 2, "error": str(e)})
            # delta_TGF_PER = round((total_g_t_score / len(df)) * 100, 2) if len(df) > 0 else 0
            # delta_TWT_PER = round((total_w_t_score / len(df)) * 100, 2) if len(df) > 0 else 0
        if errors:
            return Response({
                "status": "partial success",
                "success_count": success_count,
                # "delta_TGF_PER": delta_TGF_PER,
                # "delta_TWT_PER": delta_TWT_PER,
                # "total_g_t_score": total_g_t_score,
                # "total_w_t_score":total_w_t_score,
                "results": results,
                "errors": errors,
                
            }, status=status.HTTP_207_MULTI_STATUS)
        return Response({
            "status": "success",
            "success_count": success_count,
            # "delta_TGF_PER": delta_TGF_PER,
            # "delta_TWT_PER": delta_TWT_PER,
            # "total_g_t_score": total_g_t_score,
            # "total_w_t_score":total_w_t_score,
            "results": results,
        }, status=status.HTTP_201_CREATED)
    
