from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from  .serializer import CustomerSerializer,UnitOfMeasureSeializer,JobInfoSerializer,JodDetailSerializer,ServiceTypeSerializer,RigMasterSerilalizer,WelltypeSerializer,ToolTypeSerializer,HoleSectionSerializer,SurveyTypeSerializer,CreateJobSerializer,WellInfoSerializer,EmployeeSerializer,SurveyInitialDataSerializer,SurveyCalculationSerializer,SurveyCalculationDetailSerializer,SurveyInfoSerializer
from rest_framework.viewsets import ModelViewSet
from .models import JobInfo,CustomerMaster,UnitofMeasureMaster,ServiceType,RigMaster,WelltypeMaster,ToolMaster,HoleSection,SurveyTypes,CreateJob,SurveyInitialDataHeader,SurveyInitialDataDetail,WellInfo,EmployeeMaster,TieOnInformation,SurveyCalculationHeader, SurveyCalculationDetails,SurveyInfo
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
import pandas as pd
import decimal
from io import BytesIO
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAdminUser
import math

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

class SurveyInfoSerializer(ModelViewSet):
    queryset = SurveyInfo.objects.all()
    serializer_class = SurveyInfoSerializer

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
            'unit_of_measure':unit_of_measure,
            'rig_master':rig_master,
            'well_type':well_type,
            'tools_type':tools_type,
            'hole_section':hole_section,
            'survey_type':survey_type
        }
        return Response(data)

class UploadExcelView(APIView):

    def get(self, request, job_number=None):
        if job_number:
            try:
                job = CreateJob.objects.get(job_number=job_number)
                queryset = SurveyInitialDataDetail.objects.filter(job_number=job)
                if not queryset.exists():
                    return Response({"error": f"No data found for job_number {job_number}"}, status=status.HTTP_404_NOT_FOUND)
                serializer = SurveyInitialDataSerializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except CreateJob.DoesNotExist:
                return Response({"error": f"Job with job_number {job_number} not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            queryset = SurveyInitialDataDetail.objects.all()
            serializer = SurveyInitialDataSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    
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
        if errors:
            return Response({
                "status": "partial success",
                "success_count": success_count,
                "results": results,
                "errors": errors,
                
            }, status=status.HTTP_207_MULTI_STATUS)
        return Response({
            "status": "success",
            "success_count": success_count,
            "results": results,
        }, status=status.HTTP_201_CREATED)
    
class SurveyCalculationView(APIView):
    def get(self,request):
        queryset = SurveyCalculationHeader.objects.all()
        serializer = SurveyCalculationSerializer(queryset,many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        job_number = request.data.get('job_number')
        
        if not job_number:
            return Response({"error": "Missing job_number"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            tie_on_info = TieOnInformation.objects.get(job_number=job_number)
        except TieOnInformation.DoesNotExist:
            return Response({"error": f"TieOnInformation with job_number {job_number} not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            survey_calc_header = SurveyCalculationHeader.objects.create(
                job_number=tie_on_info.job_number,
                depth=tie_on_info.measured_depth,         
                inclination=tie_on_info.inclination,    
                azimuth=tie_on_info.azimuth,             
                true_vertical_depth = tie_on_info.true_vertical_depth,
                latitude = tie_on_info.latitude,
                departure = tie_on_info.departure,
                DLS =None,
                Vertical_Section = 0.0,
                closure_distance= math.sqrt(tie_on_info.latitude ** 2 + tie_on_info.departure ** 2),
                closure_direction = 0.0,
                CL = None,
                dog_leg = None,
                ratio_factor = None
            )

            return Response({
                "status": "success",
                "data": {
                    "job_number": survey_calc_header.job_number.job_number,
                    "depth": survey_calc_header.depth,
                    "inclination": survey_calc_header.inclination,
                    "azimuth": survey_calc_header.azimuth,
                    "Vertical_Section": survey_calc_header.Vertical_Section,
                    "true_vertical_depth":survey_calc_header.true_vertical_depth,
                    "latitude": survey_calc_header.latitude,
                    "departure ":survey_calc_header.departure,
                    " DLS":survey_calc_header.DLS,
                    "closure_distance":survey_calc_header.closure_distance,
                    "closure_direction":survey_calc_header.closure_direction,
                    "CL":survey_calc_header.CL,
                    "dog_leg":survey_calc_header.dog_leg,
                    "ratio_factor":survey_calc_header.ratio_factor
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"Error creating SurveyCalculationHeader: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class SurveyCalculationDetailsView(APIView):

    def post(self, request, *args, **kwargs):
        job_number = request.data.get('job_number')

        if not job_number:
            return Response({"error": "Job number not provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            job = CreateJob.objects.get(job_number=job_number)
        except CreateJob.DoesNotExist:
            return Response({"error": f"Job with job_number {job_number} not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            survey_headers = SurveyCalculationHeader.objects.filter(job_number=job)
            if not survey_headers.exists():
                return Response({"error": "Survey Calculation Header not found for this job"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        results = []
        previous_inclination = None
        previous_azimuth = None
        previous_measured_depth = None
        previous_tvd = None
        previous_latitude = None 
        previous_departure = None 

        for survey_header in survey_headers:
            previous_measured_depth = survey_header.depth
            previous_inclination = survey_header.inclination
            previous_azimuth = survey_header.azimuth
            previous_tvd = survey_header.true_vertical_depth
            previous_latitude = survey_header.latitude
            previous_departure = survey_header.departure  

            SurveyCalculationDetails.objects.create(
                header_id=survey_header,
                measured_depth=previous_measured_depth,
                inclination=previous_inclination,
                azimuth=previous_azimuth,
                tvd=previous_tvd,
                Vertical_Section=survey_header.Vertical_Section,
                latitude=previous_latitude,
                departure=previous_departure,
                DLS=survey_header.DLS,
                closure_distance=survey_header.closure_distance,
                closure_direction=survey_header.closure_direction,
                CL=survey_header.CL,
                dog_leg=None,
                ratio_factor=survey_header.ratio_factor
            )

            results.append({
                "measured_depth": previous_measured_depth,
                "CL": survey_header.CL,
                "closure_distance": survey_header.closure_distance,
                "dog_leg": survey_header.dog_leg
            })

            initial_data_details = SurveyInitialDataDetail.objects.filter(job_number=job).order_by('depth')
            for initial_data in initial_data_details:
                try:
                    current_measured_depth = initial_data.depth
                    if SurveyCalculationDetails.objects.filter(header_id=survey_header, measured_depth=current_measured_depth).exists():
                        continue

                    CL = current_measured_depth - previous_measured_depth
                    current_inclination = float(initial_data.Inc)
                    current_azimuth = float(initial_data.AzG)

                    # Dog Leg Calculation
                    if previous_inclination is not None and previous_azimuth is not None:
                        delta_inclination = math.radians(float(current_inclination) - float(previous_inclination))
                        delta_azimuth = math.radians(float(current_azimuth) - float(previous_azimuth))
                        try:
                            dog_leg_radians = math.acos(
                                math.cos(delta_inclination) +
                                (math.sin(math.radians(float(current_inclination))) *
                                 math.sin(math.radians(float(previous_inclination)))) *
                                (math.cos(delta_azimuth) - 1)
                            )
                            dog_leg = math.degrees(dog_leg_radians)
                        except ValueError:
                            dog_leg = 0.0
                    else:
                        dog_leg = None

                    # Ratio Factor Calculation
                    if dog_leg is not None:
                        if dog_leg < 0.25:
                            ratio_factor = 1
                        else:
                            ratio_factor = (2 / dog_leg) * math.degrees(math.tan(math.radians(dog_leg / 2)))
                    else:
                        ratio_factor = None

                    # TVD Calculation
                    if previous_tvd is not None and ratio_factor is not None and CL is not None:
                        tvd = float(previous_tvd) + (float(ratio_factor) * float(CL) / 2 * (
                            math.cos(math.radians(float(current_inclination))) +
                            math.cos(math.radians(float(previous_inclination)))))
                        tvd = round(tvd, 2)
                    else:
                        tvd = None

                   
                    if previous_latitude is not None and ratio_factor is not None and CL is not None:
                        latitude = float(previous_latitude) + (
                            float(ratio_factor) * float(CL) / 2 *
                            ((math.sin(math.radians(float(current_inclination))) * math.cos(math.radians(float(current_azimuth)))) +
                             (math.sin(math.radians(float(previous_inclination))) * math.cos(math.radians(float(previous_azimuth))))))    
                        latitude = round(latitude, 2)
                    else:
                        latitude = None

                    
                    if previous_departure is not None and ratio_factor is not None and CL is not None:
                        departure = float(previous_departure) + (
                            float(ratio_factor) * float(CL) / 2 *
                            ((math.sin(math.radians(float(current_inclination))) * math.sin(math.radians(float(current_azimuth)))) +
                             (math.sin(math.radians(float(previous_inclination))) * math.sin(math.radians(float(previous_azimuth))))))
                        departure = round(departure, 2)
                    else:
                        departure = None

                   
                    if latitude is not None and departure is not None:
                        closure_distance = math.sqrt(float(latitude)**2 + float(departure)**2)
                    else:
                        closure_distance = None

                    
                    if previous_latitude is not None and previous_departure is not None:
                        try:
                            atan_value = math.atan2(float(departure), float(latitude)) 
                            if float(latitude) < 0:
                                closure_direction = 180 + math.degrees(atan_value)
                            elif float(latitude) > 0 and float(departure) > 0:
                                closure_direction = math.degrees(atan_value)
                            else:
                                closure_direction = 360 + math.degrees(atan_value)
                        except ZeroDivisionError:
                            closure_direction = None  
                    else:
                        closure_direction = None

                    
                    CL = float(CL) if isinstance(CL, decimal.Decimal) else CL
                    dog_leg = float(dog_leg) if isinstance(dog_leg, decimal.Decimal) else dog_leg

                   
                    if dog_leg is not None and CL != 0:
                        dls_30 = round((dog_leg * 30) / float(CL),2)
                        dls_100 = (dog_leg * 100) / float(CL)
                    else:
                        dls_30 = None
                        dls_100 = None

                    
                    calculation_detail = SurveyCalculationDetails.objects.create(
                        header_id=survey_header,
                        measured_depth=current_measured_depth,
                        inclination=current_inclination,
                        azimuth=current_azimuth,
                        tvd=tvd,
                        Vertical_Section=0,
                        latitude=latitude,  
                        departure=departure,  
                        DLS=dls_30, 
                        closure_distance=closure_distance,  
                        closure_direction=closure_direction, 
                        CL=CL,
                        dog_leg=dog_leg,
                        ratio_factor=ratio_factor
                    )

                    results.append({
                        "measured_depth": current_measured_depth,
                        "CL": CL,
                        "dog_leg": dog_leg,
                        "ratio_factor": ratio_factor,
                        "tvd": tvd,
                        "latitude": latitude, 
                        "departure": departure, 
                        "closure_distance": closure_distance,  
                        "closure_direction": closure_direction,
                        "DLS": dls_30 
                          
                    })

                   
                    previous_measured_depth = current_measured_depth
                    previous_inclination = current_inclination
                    previous_azimuth = current_azimuth
                    previous_tvd = tvd
                    previous_latitude = latitude  
                    previous_departure = departure 

                except Exception as e:
                    return Response({"error": f"Failed to create calculation detail for depth {initial_data.depth}: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "status": "success",
            "message": "Survey calculation details created successfully",
            "results": results
            
        }, status=status.HTTP_201_CREATED)
