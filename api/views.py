from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from  .serializer import ( CustomerSerializer,UnitOfMeasureSeializer,JobInfoSerializer,
                          JodDetailSerializer,ServiceTypeSerializer,
                          RigMasterSerilalizer,WelltypeSerializer,
                          ToolTypeSerializer,HoleSectionSerializer,
                          SurveyTypeSerializer,CreateJobSerializer,WellInfoSerializer,EmployeeSerializer,SurveyInitialDataSerializer,
                          SurveyCalculationSerializer,SurveyCalculationDetailSerializer,
                          SurveyInfoSerializer,TieOnInformationSerializer,
                          CompleteJobCreationSerializer,AssetInfoSerializer,AssetHeaderSerializer,GyroDataSerializer,VehicleSerilaizer,JobAssetSerializer,SequenceOfEventsSerializer
                          ,SoeMasterSerializer,InterPolationDataHeaderSerializer,InterPolationDataDeatilsSerializer)

from .models import (JobInfo,CustomerMaster,UnitofMeasureMaster,ServiceType,RigMaster,WelltypeMaster,ToolMaster,HoleSection,SurveyTypes,CreateJob,
                    SurveyInitialDataHeader,SurveyInitialDataDetail,WellInfo,EmployeeMaster,TieOnInformation,SurveyCalculationHeader, SurveyCalculationDetails,
                    SurveyInfo,TieOnInformation,AssetMasterDetails,AssetMasterHeader,GyrodataMaster,VehiclesDataMaster,JobAssetMaster,
                    SequenceOfEventsMaster,SoeMaster,InterPolationDataHeader,InterPolationDataDeatils)

from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
import pandas as pd
import decimal
from io import BytesIO
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAdminUser
import math
from django.db.models import Sum
from django.db import models
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal, ROUND_HALF_UP
from rest_framework.parsers import MultiPartParser, FormParser
import numpy as np
from django.db import transaction




class JobViewSet(ModelViewSet):
    queryset = JobInfo.objects.all()
    serializer_class = JobInfoSerializer
    lookup_field = 'job_number'

class EmployeeViewSet(ModelViewSet):
    queryset = EmployeeMaster.objects.all()
    serializer_class = EmployeeSerializer

class CustomerDetailViewSet(ModelViewSet):
    queryset = CustomerMaster.objects.all()
    serializer_class = CustomerSerializer
    
class CreateJobViewSet(ModelViewSet):
    queryset = CreateJob.objects.all()
    serializer_class = CreateJobSerializer
    lookup_field = 'job_number'
    
class WellinfoViewSet(ModelViewSet):
    queryset = WellInfo.objects.all()
    serializer_class = WellInfoSerializer
    lookup_field = 'job_number'

class SurveyInfoViewset(ModelViewSet):
    queryset = SurveyInfo.objects.all()
    serializer_class = SurveyInfoSerializer
    lookup_field = 'job_number'

class TieOnInformationView(ModelViewSet):
    queryset = TieOnInformation.objects.all()
    serializer_class = TieOnInformationSerializer
    lookup_field = 'job_number'

class GetAssetHeaderView(ModelViewSet):
    queryset = AssetMasterHeader.objects.all()
    serializer_class = AssetHeaderSerializer

class GetAssetMaster(ModelViewSet):
    queryset = SoeMaster.objects.all()
    serializer_class = SoeMasterSerializer
    
class GetAssetDetailsView(APIView): 
    def get(self, request, header=None):
        try:
            queryset = AssetMasterDetails.objects.filter(cost_center__header=header)

            if not queryset.exists():
                return Response({
                    "error": f"No AssetMasterDetails found for header {header}."
                }, status=status.HTTP_404_NOT_FOUND)
            serializer = AssetInfoSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GyroDataviewSet(ModelViewSet):
    queryset = GyrodataMaster.objects.all()
    serializer_class = GyroDataSerializer


class VehicleViewSet(ModelViewSet):
    queryset = VehiclesDataMaster.objects.all()
    serializer_class = VehicleSerilaizer


class TieOnInformationDetailView(APIView):

    def get(self, request, job_number=None, run_number=None):
        
        try:
            queryset = TieOnInformation.objects.filter(job_number__job_number=job_number, run_number=run_number)

            if not queryset.exists():
                return Response({
                    "error": f"No TieOnInformation found for job_number {job_number} and run_number {run_number}."
                }, status=status.HTTP_404_NOT_FOUND)
            serializer = TieOnInformationSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        job_number = request.data.get('job_number')
        run_number = request.data.get('run_number')
        if not job_number:
            return Response({"error": "job_number is required."}, status=status.HTTP_400_BAD_REQUEST)
        if run_number is None:
            return Response({"error": "run_number is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if TieOnInformation.objects.filter(job_number__job_number=job_number, run_number=run_number).exists():
                return Response({
                    "error": f"TieOnInformation for job_number {job_number} and run_number {run_number} already exists."
                }, status=status.HTTP_400_BAD_REQUEST)
            survey_info = SurveyInfo.objects.filter(job_number__job_number=job_number, run_number=run_number).first()

            if not survey_info:
                return Response({
                    "error": f"No matching survey info found for job_number {job_number} and run_number {run_number}."
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = TieOnInformationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    

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
class CombinedJobCreationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CompleteJobCreationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class JobDetailsView(APIView):
    def get(self, request, job_number=None):
        if job_number:
            try:
                job = CreateJob.objects.get(job_number=job_number)
                customer = CustomerMaster.objects.filter(createjob__job_number=job_number).first()
                well_info = WellInfo.objects.filter(job_number=job).first()
                
              
                survey_info_list = SurveyInfo.objects.filter(job_number=job)
                tie_on_info_list = TieOnInformation.objects.filter(job_number=job)
                job_info = JobInfo.objects.filter(job_number=job).first()

              
                job_serializer = CreateJobSerializer(job)
                customer_serializer = CustomerSerializer(customer) if customer else None
                well_info_serializer = WellInfoSerializer(well_info) if well_info else None
                
               
                survey_info_serializer = SurveyInfoSerializer(survey_info_list, many=True).data
                tie_on_info_serializer = TieOnInformationSerializer(tie_on_info_list, many=True).data
                job_info_serializer = JobInfoSerializer(job_info) if job_info else None
                response_data = {
                    "job_info": job_info_serializer.data if job_info_serializer else None,
                    "customer_details": customer_serializer.data if customer_serializer else None,
                    "well_info": well_info_serializer.data if well_info_serializer else None,
                    "survey_info": survey_info_serializer, 
                    "tie_on_information": tie_on_info_serializer,
                }

                return Response(response_data, status=status.HTTP_200_OK)

            except CreateJob.DoesNotExist:
                return Response({"error": f"Job with job_number {job_number} not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"error": "job_number parameter is required"}, status=status.HTTP_400_BAD_REQUEST)


class Asset(ModelViewSet):
    queryset = JobAssetMaster.objects.all()
    serializer_class = JobAssetSerializer


class UpdateAsset(APIView):
    def get(self, request, job_number=None):
        try:
            job = CreateJob.objects.get(job_number=job_number)
            queryset = JobAssetMaster.objects.filter(job_number=job)
            if not queryset.exists():
                return Response({
                    "error": f"No asset details found for job_number {job_number}."
                }, status=status.HTTP_404_NOT_FOUND)
            serializer = JobAssetSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except CreateJob.DoesNotExist:
            return Response({
                "error": f"No job found with job_number {job_number}."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def post(self, request, job_number=None):
        try:
            job = CreateJob.objects.get(job_number=job_number)
          
            if JobAssetMaster.objects.filter(job_number=job).exists():
                return Response({
                    "error": f"Asset details for job_number {job_number} already exist."
                }, status=status.HTTP_400_BAD_REQUEST)
            data = request.data.copy()  

            cost_center = AssetMasterHeader.objects.get(id=data.get('cost_center'))
            gyro_data = GyrodataMaster.objects.get(id=data.get('gyro_data'))
            vehicle = VehiclesDataMaster.objects.get(id=data.get('vehicle'))
            emp_1 = EmployeeMaster.objects.get(id=data.get('emp_1'))
            emp_2 = EmployeeMaster.objects.get(id=data.get('emp_2'))
            emp_3 = EmployeeMaster.objects.get(id=data.get('emp_3'))
            emp_4 = EmployeeMaster.objects.get(id=data.get('emp_4'))
            emp_5 = EmployeeMaster.objects.get(id=data.get('emp_5')) if data.get('emp_5') else None
            emp_6 = EmployeeMaster.objects.get(id=data.get('emp_6')) if data.get('emp_6') else None
            emp_7 = EmployeeMaster.objects.get(id=data.get('emp_7')) if data.get('emp_7') else None

           
            job_asset_master = JobAssetMaster(
                job_number=job,
                cost_center=cost_center,
                gyro_data=gyro_data,
                vehicle=vehicle,
                emp_1=emp_1,
                emp_2=emp_2,
                emp_3=emp_3,
                emp_4=emp_4,
                emp_5=emp_5,
                emp_6=emp_6,
                emp_7=emp_7
            )
            job_asset_master.save()
            response_data = {
                "id": job_asset_master.id,
                "job_number": job.job_number,
                "cost_center": job_asset_master.cost_center.id,
                "gyro_data": job_asset_master.gyro_data.id,
                "vehicle": job_asset_master.vehicle.id,
                "emp_1": job_asset_master.emp_1.id,
                "emp_2": job_asset_master.emp_2.id,
                "emp_3": job_asset_master.emp_3.id,
                "emp_4": job_asset_master.emp_4.id,
                "emp_5": job_asset_master.emp_5.id if job_asset_master.emp_5 else None,
                "emp_6": job_asset_master.emp_6.id if job_asset_master.emp_6 else None,
                "emp_7": job_asset_master.emp_7.id if job_asset_master.emp_7 else None,
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except CreateJob.DoesNotExist:
            return Response({
                "error": f"No job found with job_number {job_number}."
            }, status=status.HTTP_404_NOT_FOUND)

        except AssetMasterHeader.DoesNotExist:
            return Response({
                "error": "Invalid cost_center ID."
            }, status=status.HTTP_400_BAD_REQUEST)

        except GyrodataMaster.DoesNotExist:
            return Response({
                "error": "Invalid gyro_data ID."
            }, status=status.HTTP_400_BAD_REQUEST)

        except VehiclesDataMaster.DoesNotExist:
            return Response({
                "error": "Invalid vehicle ID."
            }, status=status.HTTP_400_BAD_REQUEST)

        except EmployeeMaster.DoesNotExist as e:
            return Response({
                "error": f"Invalid employee ID: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

#!-------------------------------------excel-upload-------starts-----------------------------------------!


class UploadExcelView(APIView):
    
    def get(self, request, job_number=None, run_number=None):
     if job_number and run_number is not None:
        try:
            job = CreateJob.objects.get(job_number=job_number)
            survey_info_header  = SurveyInitialDataHeader.objects.get(job_number=job, run_number=run_number)

          
            queryset = SurveyInitialDataDetail.objects.filter(
                job_number=job,
                header=survey_info_header 
            )
          
            if not queryset.exists():
                return Response({"error": f"No data found for job_number {job_number} and run_number {run_number}"}, status=status.HTTP_404_NOT_FOUND)

            total_g_t_difference_pass = queryset.filter(status='PASS').aggregate(Sum('g_t_difference'))['g_t_difference__sum'] or 0
            total_w_t_difference_pass = queryset.filter(status='PASS').aggregate(Sum('w_t_difference'))['w_t_difference__sum'] or 0
            total_g_t_difference = queryset.aggregate(Sum('g_t_difference'))['g_t_difference__sum'] or 0
            total_w_t_difference = queryset.aggregate(Sum('w_t_difference'))['w_t_difference__sum'] or 0

            g_t_score = f"{total_g_t_difference_pass:.2f} / {total_g_t_difference:.2f}"
            w_t_score = f"{total_w_t_difference_pass:.2f} / {total_w_t_difference:.2f}"
            g_t_percentage = (total_g_t_difference_pass / total_g_t_difference * 100) if total_g_t_difference else 0
            w_t_percentage = (total_w_t_difference_pass / total_w_t_difference * 100) if total_w_t_difference else 0

          
            serializer = SurveyInitialDataSerializer(queryset, many=True)
            return Response({
                "status": "success",
                "success_count": queryset.count(),
                "g_t_score": g_t_score,
                "w_t_score": w_t_score,
                "g_t_percentage": f"{g_t_percentage:.2f}%",
                "w_t_percentage": f"{w_t_percentage:.2f}%",
                "results": serializer.data,
            }, status=status.HTTP_200_OK)

        except CreateJob.DoesNotExist:
            return Response({"error": f"Job with job_number {job_number} not found"}, status=status.HTTP_404_NOT_FOUND)
        except SurveyInfo.DoesNotExist:
            return Response({"error": f"SurveyInfo with job_number {job_number} and run_number {run_number} not found"}, status=status.HTTP_404_NOT_FOUND)

     else:
        return Response({"error": "job_number and run_number are required"}, status=status.HTTP_400_BAD_REQUEST)




    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        job_number = kwargs.get('job_number')
        run_number = kwargs.get('run_number')  
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
          
            if not SurveyInfo.objects.filter(job_number__job_number=job_number, run_number=run_number).exists():
                return Response({"error": f"No SurveyInfo found for job_number {job_number} with run_number {run_number}"}, status=status.HTTP_404_NOT_FOUND)

            job = CreateJob.objects.get(job_number=job_number)
            survey_type_obj = SurveyTypes.objects.get(id=survey_type_id)
            
           
            if SurveyInitialDataHeader.objects.filter(job_number=job, run_number=run_number).exists():
                return Response({"error": f"SurveyInitialDataHeader already exists for job_number {job_number} and run_number {run_number}"}, status=status.HTTP_400_BAD_REQUEST)

           
            survey_header = SurveyInitialDataHeader.objects.create(
                job_number=job,
                survey_type=survey_type_obj,
                run_number=run_number 
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

        total_g_t_difference_pass = 0
        total_w_t_difference_pass = 0
        total_g_t_difference = 0
        total_w_t_difference = 0

        for index, row in df.iterrows():
            try:
                depth = row.get("depth")
                inc = row.get("Inc")
                azg = row.get("AzG")
                g_t = row.get("G(t)")
                w_t = row.get("W(t)")
                g_t_difference = round( g_t - well_info.get_G_t, 2)
      
                w_t_difference = round(w_t - well_info.get_W_t , 2)

                total_g_t_difference += g_t_difference
                total_w_t_difference += w_t_difference

                g_t_status = "high" if -1 <= g_t_difference <= 1 else "good" if -3 <= g_t_difference <= 3 else "low" if -10 <= g_t_difference <= 10 else "n/c"
                w_t_status = "high" if -1 <= w_t_difference <= 1 else "good" if -5 <= w_t_difference <= 5 else "low" if -10 <= w_t_difference <= 10 else "n/c"

                if g_t_status == "good" and w_t_status == "good":
                  overall_status = "PASS"
                elif g_t_status == "good" and w_t_status == "low":
                    overall_status = "PASS"
                elif g_t_status == "good" and w_t_status == "high":
                    overall_status = "PASS"
                elif g_t_status == "high" and w_t_status == "good":
                    overall_status = "PASS"
                elif g_t_status == "low" and w_t_status == "good":
                    overall_status = "PASS"
                elif g_t_status == "high" and w_t_status == "low":
                    overall_status = "PASS"
                elif g_t_status == "low" and w_t_status == "high":
                    overall_status = "PASS"
                elif g_t_status == "low" and w_t_status == "low":
                    overall_status = "PASS"
                elif g_t_status == "high" and w_t_status == "high":
                    overall_status = "PASS"
                else:
                    overall_status = "REMOVE"

                if overall_status == "PASS":
                    total_g_t_difference_pass += g_t_difference
                    total_w_t_difference_pass += w_t_difference

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
                    status=overall_status,
                    run_number = run_number,
                    survey_type_status = survey_type_id
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
 
        g_t_score = f"{total_g_t_difference_pass:.2f} / {total_g_t_difference:.2f}"
        w_t_score = f"{total_w_t_difference_pass:.2f} / {total_w_t_difference:.2f}"

        g_t_percentage = (total_g_t_difference_pass / total_g_t_difference * 100) if total_g_t_difference else 0
        w_t_percentage = (total_w_t_difference_pass / total_w_t_difference * 100) if total_w_t_difference else 0

        if errors:
            return Response({
                "status": "partial success",
                "success_count": success_count,
                "results": results,
                "errors": errors,
                "g_t_score": g_t_score,
                "w_t_score": w_t_score,
                "g_t_percentage": f"{g_t_percentage:.2f}%",
                "w_t_percentage": f"{w_t_percentage:.2f}%",
            }, status=status.HTTP_207_MULTI_STATUS)
        
        return Response({
            "status": "success",
            "success_count": success_count,
            "g_t_score": g_t_score,
            "w_t_score": w_t_score,
            "g_t_percentage": f"{g_t_percentage:.2f}%",
            "w_t_percentage": f"{w_t_percentage:.2f}%",
            "results": results,
        }, status=status.HTTP_201_CREATED)


    def delete(self, request, job_number=None, data_id=None, run_number=None):
     if job_number and data_id and run_number is not None:
        try:
            job = CreateJob.objects.get(job_number=job_number)
            survey_info_header = SurveyInitialDataHeader.objects.get(job_number=job, run_number=run_number)

            row_to_delete = SurveyInitialDataDetail.objects.filter(
                id=data_id,
                job_number=job,
                header=survey_info_header 
            )
            
            if not row_to_delete.exists():
                return Response({
                    "error": "No data found for the provided job_number, data_id, and run_number."
                }, status=status.HTTP_404_NOT_FOUND)

          
            deleted_count, _ = row_to_delete.delete()
            remaining_queryset = SurveyInitialDataDetail.objects.filter(
                job_number=job,
                header=survey_info_header 
            )

            if not remaining_queryset.exists():
                return Response({
                    "message": f"{deleted_count} row(s) deleted successfully. No remaining data for the provided job_number and run_number."
                }, status=status.HTTP_200_OK)

            total_g_t_difference_pass = remaining_queryset.filter(status='PASS').aggregate(Sum('g_t_difference'))['g_t_difference__sum'] or 0
            total_w_t_difference_pass = remaining_queryset.filter(status='PASS').aggregate(Sum('w_t_difference'))['w_t_difference__sum'] or 0
            total_g_t_difference = remaining_queryset.aggregate(Sum('g_t_difference'))['g_t_difference__sum'] or 0
            total_w_t_difference = remaining_queryset.aggregate(Sum('w_t_difference'))['w_t_difference__sum'] or 0

            g_t_score = f"{total_g_t_difference_pass:.2f} / {total_g_t_difference:.2f}"
            w_t_score = f"{total_w_t_difference_pass:.2f} / {total_w_t_difference:.2f}"
            g_t_percentage = (total_g_t_difference_pass / total_g_t_difference * 100) if total_g_t_difference else 0
            w_t_percentage = (total_w_t_difference_pass / total_w_t_difference * 100) if total_w_t_difference else 0

            # Serialize the remaining results
            serializer = SurveyInitialDataSerializer(remaining_queryset, many=True)

            return Response({
                "status": "success",
                "message": f"{deleted_count} row(s) deleted successfully.",
                "success_count": remaining_queryset.count(),
                "g_t_score": g_t_score,
                "w_t_score": w_t_score,
                "g_t_percentage": f"{g_t_percentage:.2f}%",
                "w_t_percentage": f"{w_t_percentage:.2f}%",
                "results": serializer.data,
            }, status=status.HTTP_200_OK)

        except CreateJob.DoesNotExist:
            return Response({"error": f"Job with job_number {job_number} not found"}, status=status.HTTP_404_NOT_FOUND)
        except SurveyInitialDataHeader.DoesNotExist:
            return Response({"error": f"SurveyInitialDataHeader with job_number {job_number} and run_number {run_number} not found"}, status=status.HTTP_404_NOT_FOUND)

     else:
        return Response({"error": "Both job_number, run_number, and data_id are required"}, status=status.HTTP_400_BAD_REQUEST)

#----------------------------------------survey-calculations starts ----------------------------------------------!
       
class SurveyCalculationView(APIView):
    def get(self, request, job_number=None, run_number=None):
        if job_number and run_number:
            try:
                tie_on_info = TieOnInformation.objects.get(job_number__job_number=job_number, run_number=run_number)
                header = SurveyCalculationHeader.objects.get(job_number__job_number=job_number,run = run_number) 
                survey_details = SurveyCalculationDetails.objects.filter(header_id=header.id)
                serializer = SurveyCalculationDetailSerializer(survey_details, many=True)

                return Response(serializer.data, status=status.HTTP_200_OK)

            except TieOnInformation.DoesNotExist:
                return Response({
                    "error": f"No TieOnInformation found for job_number {job_number} and run_number {run_number}"
                }, status=status.HTTP_404_NOT_FOUND)

            except SurveyCalculationHeader.DoesNotExist:
                return Response({
                    "error": f"No survey calculation header found for job_number {job_number}"
                }, status=status.HTTP_404_NOT_FOUND)

        return Response({"error": "job_number and run_number parameters are required"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        job_number = request.data.get('job_number')
        run_number = request.data.get('run_number')
        
        if not job_number:
            return Response({"error": "Missing job_number"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not run_number:  
            return Response({"error": "Missing run_number"}, status=status.HTTP_400_BAD_REQUEST)

        try:
          
            tie_on_info = TieOnInformation.objects.get(job_number__job_number=job_number, run_number=run_number)
        except TieOnInformation.DoesNotExist:
            return Response({
                "error": f"TieOnInformation with job_number {job_number} and run_number {run_number} not found"
            }, status=status.HTTP_404_NOT_FOUND)

        try:
            survey_calc_header = SurveyCalculationHeader.objects.create(
                job_number=tie_on_info.job_number,
                depth=tie_on_info.measured_depth,         
                inclination=tie_on_info.inclination,    
                azimuth=tie_on_info.azimuth,             
                true_vertical_depth=tie_on_info.true_vertical_depth,
                latitude=tie_on_info.latitude,
                departure=tie_on_info.departure,
                DLS=None,
                Vertical_Section=0.0,
                closure_distance=math.sqrt(tie_on_info.latitude ** 2 + tie_on_info.departure ** 2),
                closure_direction=0.0,
                CL=None,
                dog_leg=None,
                ratio_factor=None,
                run = run_number
            )

            return Response({
                "status": "success",
                "data": {
                    "job_number": survey_calc_header.job_number.job_number,
                    "depth": survey_calc_header.depth,
                    "inclination": survey_calc_header.inclination,
                    "azimuth": survey_calc_header.azimuth,
                    "Vertical_Section": survey_calc_header.Vertical_Section,
                    "true_vertical_depth": survey_calc_header.true_vertical_depth,
                    "latitude": survey_calc_header.latitude,
                    "departure": survey_calc_header.departure,
                    "DLS": survey_calc_header.DLS,
                    "closure_distance": survey_calc_header.closure_distance,
                    "closure_direction": survey_calc_header.closure_direction,
                    "CL": survey_calc_header.CL,
                    "dog_leg": survey_calc_header.dog_leg,
                    "ratio_factor": survey_calc_header.ratio_factor,
                    "run": run_number  
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"Error creating SurveyCalculationHeader: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
class SurveyCalculationDetailsView(APIView):
    def get(self, request, job_number=None, run_number=None):
        if job_number and run_number:
            try:
               
                header = SurveyCalculationHeader.objects.get(job_number__job_number=job_number, run=run_number)

              
                survey_details = SurveyCalculationDetails.objects.filter(header_id=header.id)

                if not survey_details.exists():
                    return Response({"error": f"No survey calculation details found for header ID {header.id}"}, status=status.HTTP_404_NOT_FOUND)

              
                serializer = SurveyCalculationDetailSerializer(survey_details, many=True)

              
                max_inclination = survey_details.aggregate(max_inclination=models.Max('inclination'))['max_inclination']
               
                last_row = survey_details.order_by('-id').first()
                last_row_details = {
                    "header_id": header.id,
                    "closure_distance": last_row.closure_distance,
                    "closure_direction": last_row.closure_direction,
                    "vertical_section": last_row.Vertical_Section
                } if last_row else None

                # Response
                return Response({
                    "max_inclination": max_inclination,
                    "last_row": last_row_details,
                    "survey_details": serializer.data,
                }, status=status.HTTP_200_OK)

            except SurveyCalculationHeader.DoesNotExist:
                return Response({"error": f"No survey calculation header found for job_number {job_number} and run_number {run_number}"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"error": "job_number and run_number parameters are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    
    def post(self, request, *args, **kwargs):
        job_number = request.data.get('job_number')
        run_number = request.data.get('run_number')

        if not job_number:
            return Response({"error": "Job number not provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
           existing_calculation = SurveyCalculationDetails.objects.filter(header_id__job_number=job_number, header_id__run=run_number)
           if existing_calculation.exists():
            return Response({
                "status": "failed",
                "error": f"Survey calculation details already exist for job_number {job_number} and run_number {run_number}"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
         return Response({"error": f"Error checking existing survey calculation details: {str(e)}"}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            job = CreateJob.objects.get(job_number=job_number)
        except CreateJob.DoesNotExist:
            return Response({"error": f"Job with job_number {job_number} not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            survey_headers = SurveyCalculationHeader.objects.filter(job_number=job,run = run_number)
            if not survey_headers.exists():
                return Response({"error": "Survey Calculation Header not found for this job"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            survey_info = SurveyInfo.objects.get(job_number=job,run_number = run_number)
            proposal_direction = survey_info.proposal_direction 
        except SurveyInfo.DoesNotExist:
            proposal_direction = None  

        results = []
        max_inclination = float('-inf')  
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

           
            if previous_inclination is not None:
                max_inclination = max(max_inclination, previous_inclination)

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
                "inclination": previous_inclination,
                "azimuth": previous_azimuth,
                "CL": survey_header.CL,
                "dog_leg": survey_header.dog_leg,
                "ratio_factor": survey_header.ratio_factor,
                "tvd": survey_header.true_vertical_depth,
                "latitude": survey_header.latitude,
                "departure": survey_header.departure,
                "closure_distance": survey_header.closure_distance,
                "closure_direction": survey_header.closure_direction,
                "DLS": survey_header.DLS,
                "Vertical_Section": survey_header.Vertical_Section
            })

            initial_data_details = SurveyInitialDataDetail.objects.filter(job_number=job,run_number = run_number).order_by('depth')
            for initial_data in initial_data_details:
                try:
                    current_measured_depth = initial_data.depth
                    if SurveyCalculationDetails.objects.filter(header_id=survey_header, measured_depth=current_measured_depth).exists():
                        continue
            

                    CL = current_measured_depth - previous_measured_depth
                    current_inclination = float(initial_data.Inc)
                    current_azimuth = float(initial_data.AzG)

                    # Update max inclination
                    max_inclination = max(max_inclination, current_inclination)

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
                    if previous_tvd is not None and ratio_factor is not None and CL is not None:
                        tvd = round(float(previous_tvd) + (float(ratio_factor) * float(CL) / 2 * (
                            math.cos(math.radians(float(current_inclination))) +
                            math.cos(math.radians(float(previous_inclination))))), 2)
                    else:
                        tvd = None
                        
                    # Latitude Calculation (+N/-S)
                    if previous_latitude is not None and ratio_factor is not None and CL is not None:
                        latitude = round(float(previous_latitude) + (
                            float(ratio_factor) * float(CL) / 2 *
                            ((math.sin(math.radians(float(current_inclination))) * math.cos(math.radians(float(current_azimuth)))) +
                            (math.sin(math.radians(float(previous_inclination))) * math.cos(math.radians(float(previous_azimuth)))))), 2)
                    else:
                        latitude = None

                    # Departure Calculation (+E/-W)
                    if previous_departure is not None and ratio_factor is not None and CL is not None:
        
                        departure = round(float(previous_departure) + (
                            float(ratio_factor) * float(CL) / 2 *
                            ((math.sin(math.radians(float(current_inclination))) * math.sin(math.radians(float(current_azimuth)))) +
                            (math.sin(math.radians(float(previous_inclination))) * math.sin(math.radians(float(previous_azimuth)))))), 2)
                    else:
                        departure = None

                    # Closure Distance
                    if latitude is not None and departure is not None:
                        closure_distance = round(math.sqrt(float(latitude)**2 + float(departure)**2), 2)
                    else:
                        closure_distance = None

                    # Closure Direction
                    if latitude is not None and departure is not None:
                        try:
                            atan_value = math.atan2(float(departure), float(latitude)) 
                            if float(latitude) < 0:
                                closure_direction = round(180 + math.degrees(atan_value), 2)
                            elif float(latitude) > 0 and float(departure) > 0:
                                closure_direction = round(math.degrees(atan_value), 2)
                            else:
                                closure_direction = round(360 + math.degrees(atan_value),2)
                        except ZeroDivisionError:
                            closure_direction = None  
                    else:
                        closure_direction = None

                    
                    # Vertical Section Calculation
                    if proposal_direction is not None and closure_distance is not None and closure_direction is not None:
                        vertical_section = round(closure_distance * math.cos(math.radians(float(proposal_direction) - closure_direction)), 2)
                    else:
                        vertical_section = None

                    # Dog Leg Severity (DLS)
                    if dog_leg is not None and CL != 0:
                        dls_30 = round((dog_leg * 30) / float(CL), 2)
                    else:
                        dls_30 = None

                    calculation_detail = SurveyCalculationDetails.objects.create(
                        header_id=survey_header,
                        measured_depth=current_measured_depth,
                        inclination=current_inclination,
                        azimuth=current_azimuth,
                        tvd=tvd,
                        Vertical_Section=vertical_section,
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
                        "inclination": current_inclination,
                        "azimuth": current_azimuth,
                        "CL": CL,
                        "dog_leg": dog_leg,
                        "ratio_factor": ratio_factor,
                        "tvd": tvd,
                        "latitude": latitude,
                        "departure": departure,
                        "closure_distance": closure_distance,
                        "closure_direction": closure_direction,
                        "DLS": dls_30,
                        "Vertical_Section": vertical_section  
                    })

                 
                    previous_measured_depth = current_measured_depth
                    previous_inclination = current_inclination
                    previous_azimuth = current_azimuth
                    previous_tvd = tvd
                    previous_latitude = latitude
                    previous_departure = departure

                except Exception as e:
                    return Response({"error": f"Failed to create calculation detail for depth {initial_data.depth}: {str(e)}"},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

      
        last_row_details = []
        for survey_header in survey_headers:
            last_row = SurveyCalculationDetails.objects.filter(header_id=survey_header).order_by('-id').first()
            if last_row:
                last_row_details.append({
                    "header_id": survey_header.id,
                    "closure_distance": last_row.closure_distance,
                    "closure_direction": last_row.closure_direction,
                    "vertical_section": last_row.Vertical_Section
                })

        return Response({
            "status": "success",
            "message": "Survey calculation details created successfully",
            "max_inclination": max_inclination,  
            "last_rows": last_row_details, 
            "results": results
        }, status=status.HTTP_201_CREATED)
    


class InterPolationDataHeaderViewSet(APIView):
    def get(self, request, job_number=None, run_number=None):
        
        if job_number and run_number:
            records = InterPolationDataHeader.objects.filter(job_number=job_number, run_number=run_number)
        else:
            records = InterPolationDataHeader.objects.all()
        if not records.exists():
            return Response({'error': 'No records found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = InterPolationDataHeaderSerializer(records, many=True)  
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    def post(self, request, job_number, run_number, *args, **kwargs):
        # Extract parameters from the request body
        data = request.data
        resolution = data.get('resolution')
        range_from = data.get('range_from')
        range_to = data.get('range_to')

        # Validate required fields
        if not resolution:
            return Response({
                "message": "Missing required field: 'resolution'."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check that both range_from and range_to are either null or have values
        if (range_from is None and range_to is not None) or (range_from is not None and range_to is None):
            return Response({
                "message": "'range_from' and 'range_to' must both be provided or both be null."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate range values if not null
        if range_from is not None and range_to is not None:
            if int(range_from) > int(range_to):
                return Response({
                    "message": "'range_from' cannot be greater than 'range_to'."
                }, status=status.HTTP_400_BAD_REQUEST)

        # Check for duplicate records
        existing_record = InterPolationDataHeader.objects.filter(
            job_number=job_number,
            run_number=run_number,
            resolution=resolution,
            range_from=range_from,
            range_to=range_to
        ).first()

        if existing_record:
            return Response({
                "message": "A record with the same resolution and range already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Prepare the data to be saved
        interpolation_data = {
            "resolution": resolution,
            "range_from": range_from,
            "range_to": range_to,
            "job_number": job_number,
            "run_number": run_number,
        }

        # Serialize and save the data
        serializer = InterPolationDataHeaderSerializer(data=interpolation_data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Data saved successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        # Handle validation errors
        return Response({
            "message": "Validation failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class InterPolationDataDeatilsViewSet(APIView):
    
    def get(self, request, job_number=None, run_number=None):
        # Fetch headers based on job_number and run_number
        if job_number and run_number:
            headers = InterPolationDataHeader.objects.filter(job_number=job_number, run_number=run_number,)
        else:
            headers = InterPolationDataHeader.objects.all()
        
        if not headers.exists():
            return Response({'error': 'No records found.'}, status=status.HTTP_404_NOT_FOUND)

        # Collect interpolation details for the fetched headers
        result_data = []
        for header in headers:
            details = InterPolationDataDeatils.objects.filter(header_id=header.id)
            for detail in details:
                result_data.append({
                    "new_depth": detail.new_depth,
                    "inclination": detail.inclination,
                    "azimuth": detail.azimuth,
                    "dog_leg": round(detail.dog_leg, 2),
                    "CL": round(detail.CL, 2),
                    "ratio_factor": round(detail.ratio_factor, 2),
                    "tvd": round(detail.tvd, 2),
                    "latitude": round(detail.latitude, 2),
                    "departure": round(detail.departure, 2),
                    "closure_distance": round(detail.closure_distance, 2),
                    "closure_direction": round(detail.closure_direction, 2),
                    "DLS": round(detail.dls, 2),
                    "vertical_section": round(detail.vertical_section, 2)
                })

        if not result_data:
            return Response({'error': 'No interpolation details found.'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(result_data, status=status.HTTP_200_OK)

    def post(self,request, job_number, run_number, resolution,header_id):
        try:
            # Fetch required data from the database
            header = InterPolationDataHeader.objects.get(job_number=job_number, run_number=run_number,id = header_id,resolution=resolution)
            tie_on_info = TieOnInformation.objects.get(job_number=job_number, run_number=run_number)
            survey_info = SurveyInfo.objects.get(job_number=job_number, run_number=run_number)
        except (InterPolationDataHeader.DoesNotExist, TieOnInformation.DoesNotExist):
            return Response({'error': 'Invalid job_number or run_number.'}, status=status.HTTP_400_BAD_REQUEST)
       
        # Fetch survey data
        survey_data_rows = list(SurveyInitialDataDetail.objects.filter(
            job_number=job_number, run_number=run_number).order_by('depth'))
        if not survey_data_rows:
            return Response({'error': 'No SurveyInitialDataDetail found.'}, status=status.HTTP_404_NOT_FOUND)

        results = []
        resolution_value = float(resolution)
        range_from = header.range_from or float(tie_on_info.measured_depth)
        range_to = header.range_to or float(survey_data_rows[-1].depth)
        if header.range_from is None or header.range_to is None:
            range_from = float(tie_on_info.measured_depth)
            range_to = float(survey_data_rows[-1].depth)
        else:
            range_from = float(header.range_from)
            range_to = float(header.range_to)

        header_data = {
        "Measured_Depth": float(tie_on_info.measured_depth),
        "Inclination": float(tie_on_info.inclination),
        "Azimuth": float(tie_on_info.azimuth),
        "TVD":float(tie_on_info.true_vertical_depth),
        "latitude": float(tie_on_info.latitude),
        "departure": float(tie_on_info.departure),
        "Proposal_Direction":float(survey_info.proposal_direction),
        "From":range_from,
        "To":range_to,
        "Course_Length":resolution,
        "Maximum Inclination":None,
        "Closure Distance": None,
        "Closure Direction": None,
        "Vertical Section": None
        }

        # Fetch the initial TVD and inclination from the SurveyCalculationDetails
        previous_tvd = self.get_initial_tvd(job_number, run_number)
        previous_inclination = self.get_initial_inclination(job_number, run_number)
        previous_latitude = self.get_initial_latitude(job_number,run_number)
        previous_azimuth = self.get_initial_azimuth(job_number, run_number)
        previous_departure = self.get_initial_departure(job_number,run_number)
        
    
        # Check if previous_tvd and previous_inclination are available
        if previous_tvd is None or previous_inclination is None:
            return Response({'error': 'Initial TVD or inclination not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        max_inclination = 0.0

        # Interpolation logic
        upper_depth, upper_inclination, upper_azimuth = self.get_previous_survey_data(job_number, run_number, range_from, tie_on_info)
        lower_depth, lower_inclination, lower_azimuth = self.get_next_survey_data(survey_data_rows, range_from, range_to)
        
        max_inclination = max(max_inclination, upper_inclination, lower_inclination)

        interpolated_inclination, interpolated_azimuth = self.interpolate(
            upper_depth, upper_inclination, upper_azimuth,
            lower_depth, lower_inclination, lower_azimuth, range_from
        )

        dog_leg = self.calculate_dog_leg(
            upper_inclination, upper_azimuth, interpolated_inclination, interpolated_azimuth
        )

        # Calculate the initial TVD
        previous_measured_depth = upper_depth
        current_measured_depth = range_from
        CL = current_measured_depth - previous_measured_depth
       
        ratio_factor = self.calculate_ratio_factor(dog_leg)
        current_tvd = self.calculate_tvd(previous_tvd, ratio_factor, CL, interpolated_inclination, upper_inclination)

        current_latitude = self.calculate_northing(
        previous_latitude, ratio_factor, CL,
        interpolated_inclination, interpolated_azimuth,
        previous_inclination, previous_azimuth)

        current_departure = self.calculate_departure(
        previous_departure, ratio_factor, CL,
        interpolated_inclination, interpolated_azimuth,
        previous_inclination, previous_azimuth)

        proposal_direction = float(survey_info.proposal_direction)  # assuming proposal_direction is stored here
        vertical_section = round(current_latitude * math.cos(math.radians(proposal_direction - current_departure)), 2)
        
        # Update the previous values for the next iteration
        previous_tvd = current_tvd
        previous_inclination = interpolated_inclination
        previous_azimuth = interpolated_azimuth
        previous_latitude = current_latitude
        previous_departure = current_departure
        

        results.append(self.format_result(
            range_from, interpolated_inclination, interpolated_azimuth,
             dog_leg, CL, ratio_factor, current_tvd,current_latitude,previous_departure,vertical_section
        ))

        upper_depth, upper_inclination, upper_azimuth = range_from, interpolated_inclination, interpolated_azimuth

        # Loop through survey data rows
        for survey_data in survey_data_rows:
            
            lower_depth = float(survey_data.depth)
            if lower_depth < range_from or lower_depth > range_to:
                continue

            while upper_depth < lower_depth:
                new_depth = upper_depth + resolution_value
                print(f"new_depth:{new_depth}")

                # Perform interpolation between the depths
                interpolated_inclination, interpolated_azimuth = self.interpolate(
                    upper_depth, upper_inclination, upper_azimuth,
                    lower_depth, float(survey_data.Inc), float(survey_data.AzG), new_depth
                )
                max_inclination = max(max_inclination, interpolated_inclination)
                dog_leg = self.calculate_dog_leg(upper_inclination, upper_azimuth,
                                                 interpolated_inclination, interpolated_azimuth)

                # Calculate TVD and update previous values
                previous_measured_depth = upper_depth
                current_measured_depth = new_depth
                CL = current_measured_depth - previous_measured_depth
                ratio_factor = self.calculate_ratio_factor(dog_leg)
                current_tvd = self.calculate_tvd(previous_tvd, ratio_factor, CL, interpolated_inclination, upper_inclination)
                current_latitude = self.calculate_northing(
                            previous_latitude, ratio_factor, CL,
                            interpolated_inclination, interpolated_azimuth,
                            previous_inclination, previous_azimuth
                        )
                current_departure = self.calculate_departure(
                    previous_departure, ratio_factor, CL,
                    interpolated_inclination, interpolated_azimuth,
                    previous_inclination, previous_azimuth
                )
                vertical_section = round(current_latitude * math.cos(math.radians(proposal_direction - current_departure)), 2)
                # Append the result to the list
                results.append(self.format_result(
                    new_depth, interpolated_inclination, interpolated_azimuth,
                     dog_leg, CL, ratio_factor, current_tvd,current_latitude,current_departure, vertical_section
                ))

                # Update the upper values for the next loop
                upper_depth = new_depth
                upper_inclination, upper_azimuth = interpolated_inclination, interpolated_azimuth
                previous_inclination = interpolated_inclination
                previous_azimuth = interpolated_azimuth
                previous_latitude = current_latitude
                previous_departure = current_departure

        if results:
            last_result = results[-1]
            header_data["Maximum Inclination"] = round(max_inclination, 2)
            header_data["Closure Distance"] = last_result["closure_distance"]
            header_data["Closure Direction"] = last_result["closure_direction"]
            header_data["Vertical Section"] = last_result["vertical_section"]
        try:
            save_response = self.save_results_to_db(results, header_id, resolution)
            if save_response["status"] == "error":
             return Response({'error': save_response["message"]}, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return Response({'error': f'Error saving data: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({"header": header_data, "results": results}, status=status.HTTP_200_OK)
               
    def calculate_northing(self, previous_latitude, ratio_factor, CL, current_inclination, current_azimuth, previous_inclination, previous_azimuth):
       
        if previous_latitude is not None and ratio_factor is not None and CL is not None:
            latitude = float(previous_latitude) + (
                            float(ratio_factor) * float(CL) / 2 *
                            ((math.sin(math.radians(float(current_inclination))) * math.cos(math.radians(float(current_azimuth)))) +
                            (math.sin(math.radians(float(previous_inclination))) * math.cos(math.radians(float(previous_azimuth))))))
            return latitude
        return None
    def calculate_departure(self, previous_departure, ratio_factor, CL, current_inclination, current_azimuth, previous_inclination, previous_azimuth):
       
        if previous_departure is not None and ratio_factor is not None and CL is not None:
            departure = previous_departure + (
                ratio_factor * CL / 2 *
                ((math.sin(math.radians(current_inclination)) * math.sin(math.radians(current_azimuth))) +
                (math.sin(math.radians(previous_inclination)) * math.sin(math.radians(previous_azimuth))))
            )
            return departure
        return None
    def get_initial_departure(self, job_number, run_number):
        try:
            survey_header = SurveyCalculationHeader.objects.get(
                job_number=job_number,
                run=run_number
            )
            return float(survey_header.departure)
        except SurveyCalculationHeader.DoesNotExist:
            return None
    def get_initial_azimuth(self,job_number,run_number):
            try:
                survey_header = SurveyCalculationHeader.objects.get(
                    job_number = job_number,
                    run = run_number
                )
                return float(survey_header.azimuth)
            except SurveyCalculationHeader.DoesNotExist:
                return None
    def get_initial_latitude(self,job_number,run_number):
        try:
            survey_header = SurveyCalculationHeader.objects.get(
                job_number = job_number,
                run = run_number
            )
            return float(survey_header.latitude)
        except SurveyCalculationHeader.DoesNotExist:
            return None
    def get_initial_tvd(self, job_number, run_number):
        try:
            survey_header = SurveyCalculationHeader.objects.get(
                job_number=job_number,
                run=run_number
            )
            return float(survey_header.true_vertical_depth)
        except SurveyCalculationHeader.DoesNotExist:
            return None

    def get_initial_inclination(self, job_number, run_number):
        try:
            survey_header = SurveyCalculationHeader.objects.get(
                job_number=job_number,
                run=run_number
            )
            return float(survey_header.inclination)
        except SurveyCalculationHeader.DoesNotExist:
            return None

    def get_previous_survey_data(self, job_number,run_number, range_from, tie_on_info):
            previous_data = SurveyCalculationHeader.objects.filter(
            job_number=job_number,
            run=run_number,
            depth__lt=range_from  
        ).order_by('-depth').first()  

            if previous_data:
                return float(previous_data.depth), float(previous_data.inclination), float(previous_data.azimuth)
            return float(tie_on_info.measured_depth), float(tie_on_info.inclination), float(tie_on_info.azimuth)

    def get_next_survey_data(self, survey_data_rows, range_from, range_to):
        next_data = next((data for data in survey_data_rows if data.depth >= range_from), None)
        return (float(next_data.depth), float(next_data.Inc), float(next_data.AzG)) if next_data else (range_from, 0, 0)

    def interpolate(self, upper_depth, upper_inclination, upper_azimuth, lower_depth, lower_inclination, lower_azimuth, target_depth):
        ratio = (target_depth - upper_depth) / (lower_depth - upper_depth)
        interpolated_inclination = upper_inclination + (lower_inclination - upper_inclination) * ratio
        delta_azimuth = lower_azimuth - upper_azimuth
        if delta_azimuth > 180:
            delta_azimuth -= 360
        elif delta_azimuth < -180:
            delta_azimuth += 360

        interpolated_azimuth = upper_azimuth + delta_azimuth * ratio

        if interpolated_azimuth < 0:
                interpolated_azimuth += 360
        elif interpolated_azimuth >= 360:
                interpolated_azimuth -= 360
        return round(interpolated_inclination, 2), round(interpolated_azimuth, 2)

    def calculate_dog_leg(self, previous_inclination, previous_azimuth, current_inclination, current_azimuth):
        delta_inclination = math.radians(current_inclination - previous_inclination)
        delta_azimuth = math.radians(current_azimuth - previous_azimuth)
        try:
            dog_leg_radians = math.acos(
                math.cos(delta_inclination) +
                (math.sin(math.radians(current_inclination)) * math.sin(math.radians(previous_inclination))) *
                (math.cos(delta_azimuth) - 1)
            )
            return math.degrees(dog_leg_radians)
        except ValueError:
            return 0.0
    
    def calculate_ratio_factor(self, dog_leg):
        if dog_leg < 0.25:
            return 1
        return (2 / dog_leg) * math.degrees(math.tan(math.radians(dog_leg / 2)))

    def calculate_tvd(self, previous_tvd, ratio_factor, CL, current_inclination, previous_inclination):
       
        if previous_tvd is not None and ratio_factor is not None and CL is not None:
            return round(
                float(previous_tvd) + (float(ratio_factor) * float(CL) / 2 * (
                    math.cos(math.radians(current_inclination)) +
                    math.cos(math.radians(previous_inclination))
                )), 3)
        return None
    def calculate_closure_direction(self,current_northing, current_departure):
        if current_northing == 0:
            return 0.0
        try:
            # Match Excel precision by rounding intermediate division
            ratio = round(current_departure / current_northing, 15)
           
            atan_value = math.atan(ratio)  # Similar to Excel's ATAN(I14/H14)
            atan_degrees = round(math.degrees(atan_value), 15)  # Convert radians to degrees
            
            if current_northing < 0:  # Corresponds to H14 < 0 in Excel
                closure_direction = 180 + atan_degrees
            elif current_northing > 0 and current_departure > 0:  # H14 > 0 AND I14 > 0
                closure_direction = atan_degrees
            else:  # All other cases, equivalent to 360 + ATAN(I14/H14) in Excel
                closure_direction = 360 + atan_degrees
            
            return closure_direction
        except ZeroDivisionError:
            return None
    def save_results_to_db(self, results, header_id, resolution):
        try:
        # Fetch the InterPolationDataHeader instance using the header_id
            header_instance = InterPolationDataHeader.objects.get(id=header_id)
            if InterPolationDataDeatils.objects.filter(header_id=header_instance).exists():
             return {
                "status": "error",
                "message": "Data already exists for the given header ID."
            }
            with transaction.atomic():
                for result in results:
                    InterPolationDataDeatils.objects.create(
                        header_id=header_instance,
                        resolution=resolution,
                        new_depth=result["new_depth"],
                        inclination=result["inclination"],
                        azimuth=result["azimuth"],
                        dog_leg=result["dog_leg"],
                        CL=result["CL"],
                        ratio_factor=result["ratio_factor"],
                        tvd=result["tvd"],
                        latitude=result["latitude"],
                        departure=result["departure"],
                        closure_distance=result["closure_distance"],
                        closure_direction=result["closure_direction"],
                        DLS=result["DLS"],
                        vertical_section=result["vertical_section"],
                        survey_status=0 
                    )
                return {
            "status": "success",
            "message": "Data saved successfully."
        }
        except InterPolationDataHeader.DoesNotExist:
          raise ValueError(f"InterPolationDataHeader with ID {header_id} does not exist.")
        
    def format_result(self, new_depth, inclination, azimuth, dog_leg, CL, ratio_factor, tvd,latitude, departure, vertical_section):
        closure_distance = round((latitude**2 + departure**2)**0.5, 2)
        closure_direction = self.calculate_closure_direction(latitude, departure)
        dls = round((dog_leg * 30) / CL, 2) if CL != 0 else 0
       
        return {
            "new_depth": new_depth,
            "inclination": inclination,
            "azimuth": azimuth,
            "dog_leg": round(dog_leg, 2),
            "CL": round(CL, 2),
            "ratio_factor": round(ratio_factor, 2),
            "tvd": round(tvd,2),
            "latitude": round(latitude,2),
            "departure": round(departure,2),
            "closure_distance": round(closure_distance,2),
            "closure_direction": round(closure_direction,2),
            "DLS": round(dls,2),
            "vertical_section": round(vertical_section,2)
        }
    
class ComparisonViewSet(APIView):
    parser_classes = [MultiPartParser, FormParser]
    REQUIRED_COLUMNS = {"depth", "Inc", "Azg"}
    INTERPOLATION_RESOLUTION = 5  # Resolution for interpolation

    def post(self, request, *args, **kwargs):
        # Fetch the uploaded files
        file1 = request.FILES.get('file1')
        file2 = request.FILES.get('file2')
        
        if not file1 or not file2:
            return Response({"error": "Both file1 and file2 are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not file1.name.endswith(('.xls', '.xlsx')) or not file2.name.endswith(('.xls', '.xlsx')):
            return Response({"error": "Both files must be Excel files."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve additional interpolation parameters from the request
        initial_depth = float(request.data.get("initial_depth", 0))  # Default to 0 if not provided
        initial_inclination = float(request.data.get("initial_inclination", 0))
        initial_azimuth = float(request.data.get("azi", 0))

        try:
            # Read both Excel files into DataFrames
            df1 = pd.read_excel(file1)
            df2 = pd.read_excel(file2)

            # Check for required columns in both files
            missing_columns_file1 = self.REQUIRED_COLUMNS - set(df1.columns)
            missing_columns_file2 = self.REQUIRED_COLUMNS - set(df2.columns)

            if missing_columns_file1:
                return Response({
                    "error": "File1 is missing required columns.",
                    "missing_columns_file1": list(missing_columns_file1)
                }, status=status.HTTP_400_BAD_REQUEST)

            if missing_columns_file2:
                return Response({
                    "error": "File2 is missing required columns.",
                    "missing_columns_file2": list(missing_columns_file2)
                }, status=status.HTTP_400_BAD_REQUEST)

            # Perform interpolation on both files
            df1_interpolated = self.interpolate_data(df1, initial_depth, initial_inclination, initial_azimuth)
            df2_interpolated = self.interpolate_data(df2, initial_depth, initial_inclination, initial_azimuth)

            # Prepare file interpolated data
            file1_data = [
                {
                    "depth": row["depth"],
                    "inclination": row["Inc"],
                    "azimuth": row["Azg"],
                    "CL": row["CL"],
                    "dog_leg": row["dog_leg"]
                } for _, row in df1_interpolated.iterrows()
            ]

            file2_data = [
                {
                    "depth": row["depth"],
                    "inclination": row["Inc"],
                    "azimuth": row["Azg"],
                    "CL": row["CL"],
                    "dog_leg": row["dog_leg"]
                } for _, row in df2_interpolated.iterrows()
            ]

            # Perform comparison of interpolated data
            comparison_result = self.compare_interpolated_data(df1_interpolated, df2_interpolated)

            # Return the structured response
            return Response({
                "status": "success",
                "file1_interpolated": file1_data,
                "file2_interpolated": file2_data,
                "comparison_result": comparison_result
            })
        
        except Exception as e:
            return Response({"error": f"Error processing files: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def dog_leg(self, INC1, INC2, AZI1, AZI2):
        """Calculate the dogleg angle between two points based on the formula."""
        # Convert degrees to radians
        I1 = math.radians(INC1)
        I2 = math.radians(INC2)
        A1 = math.radians(AZI1)
        A2 = math.radians(AZI2)

        # Dogleg formula using spherical trigonometry
        cos_term = math.cos(I1) * math.cos(I2) + (math.sin(I1) * math.sin(I2) * (math.cos(A2 - A1) - 1))

        # Ensure the cosine term is within the valid range for ACOS to avoid NaN errors
        cos_term = min(1, max(cos_term, -1))

        # Dogleg in radians, then convert to degrees
        DL = math.acos(cos_term)
        return math.degrees(DL)

    def interpolate_data(self, df, initial_depth, initial_inclination, initial_azimuth):
        """Interpolates data in a DataFrame and calculates dog_leg using the provided equation."""
        df = df.sort_values(by="depth").reset_index(drop=True)

        # Initialize variables for iteration
        MD1 = initial_depth
        INC1 = initial_inclination
        AZI1 = initial_azimuth
        previous_depth = None  # For calculating CL

        # Initialize interpolated data with the initial values from the request body
        interpolated_data = {
            "depth": [initial_depth],
            "Inc": [initial_inclination],
            "Azg": [initial_azimuth],
            "CL": [0.0],  
            "dog_leg": [0.0] 
        }

        # Iterate through the depth values in the dataframe
        for i in range(len(df)):
            MD2 = df["depth"].iloc[i]
            INC2 = df["Inc"].iloc[i]
            AZI2 = df["Azg"].iloc[i]

            while MD1 < MD2:
                if MD1 == initial_depth:
                    # Skip the first depth since it's already initialized
                    previous_depth = MD1
                    MD1 += self.INTERPOLATION_RESOLUTION
                    continue

                # Calculate Dogleg (DL)
                DL = self.dog_leg(INC1, INC2, AZI1, AZI2)
                DL0 = DL * ((MD1 - initial_depth) / (MD2 - initial_depth))

                # Calculate interpolated inclination
                INC0 = INC1 + (INC2 - INC1) * (DL0 / DL if DL != 0 else 1)

                # Calculate interpolated azimuth
                if (AZI2 - AZI1) > 180:
                    AZI0 = AZI1 + ((AZI2 - AZI1 - 360) * DL0 / DL if DL != 0 else 1)
                    if AZI0 < 0:
                        AZI0 += 360
                else:
                    AZI0 = AZI1 + ((AZI2 - AZI1) * DL0 / DL if DL != 0 else 1)

                # Calculate CL (Cumulative Length)
                CL = MD1 - previous_depth if previous_depth is not None else 0

                # Append interpolated values and dog_leg
                interpolated_data["depth"].append(MD1)
                interpolated_data["Inc"].append(round(INC0, 2))
                interpolated_data["Azg"].append(round(AZI0, 2))
                interpolated_data["CL"].append(CL)
                interpolated_data["dog_leg"].append(round(DL, 2))

                # Update MD1 for the next interpolation point
                previous_depth = MD1
                MD1 += self.INTERPOLATION_RESOLUTION

            # Update variables for the next segment
            initial_depth = MD2
            INC1, AZI1 = INC2, AZI2

        return pd.DataFrame(interpolated_data)


    def compare_interpolated_data(self, df1, df2):
        """Compares the interpolated data from two DataFrames."""
        comparison_result = []
        for depth in df1["depth"]:
            if depth in df2["depth"].values:
                row1 = df1[df1["depth"] == depth]
                row2 = df2[df2["depth"] == depth]
                comparison_result.append({
                    "depth": depth,
                    "Inc_difference": round(abs(row1["Inc"].values[0] - row2["Inc"].values[0]), 2),
                    "Azg_difference": round(abs(row1["Azg"].values[0] - row2["Azg"].values[0]), 2),
                    "CL": abs(row1["CL"].values[0] - row2["CL"].values[0]),
                    "dog_leg_difference": round(abs(row1["dog_leg"].values[0] - row2["dog_leg"].values[0]), 2)  # Add dog_leg_difference
                })
        
        return comparison_result

# class SaveCalculationViewSet(APIView):
#      def post(self, request):
#         try:
#             # Extract required data from the request
#             resolution_data = request.data.get('resolution_data', [])
#             job_number = request.data.get('job_number')
#             run_number = request.data.get('run_number')

#             if not resolution_data or not job_number or not run_number:
#                 return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

#             # Save each resolution data entry to the database
#             for data in resolution_data:
#                 InterPolationDataDeatils.objects.create(
#                     job_number=job_number,
#                     run_number=run_number,
#                     depth=data['new_depth'],
#                     inclination=data['inclination'],
#                     azimuth=data['azimuth'],
#                     dog_leg=data['dog_leg'],
#                     tvd=data['tvd'],
#                     latitude=data['latitude'],
#                     departure=data['departure'],
#                     closure_distance=data['closure_distance'],
#                     closure_direction=data['closure_direction'],
#                     vertical_section=data['vertical_section']
#                 )

#             return Response({'message': 'Resolution data saved successfully.'}, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# # class SoeViewSet(APIView):
#      def get(self, request, job_number=None):
#         if job_number is not None:
#             try:
#                 job = CreateJob.objects.get(job_number = job_number)
#                 events = SequenceOfEventsMaster.objects.filter(job_number=job)
#                 if not events.exists():
#                     return Response({
#                         "message": f"No events found for job_number {job_number}."
#                     }, status=status.HTTP_404_NOT_FOUND)
#                 serializer = SequenceOfEventsSerializer(events, many=True)
#                 return Response(serializer.data, status=status.HTTP_200_OK)

#             except CreateJob.DoesNotExist:
#                 return Response({
#                     "error": f"No job found with job_number {job_number}."
#                 }, status=status.HTTP_404_NOT_FOUND)

#             except Exception as e:
#                 return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return Response({
#             "error": "job_number must be provided."
#         }, status=status.HTTP_400_BAD_REQUEST)
     


# class SoeViewSet(APIView):
#     def get(self, request, job_number=None):
#         if job_number is not None:
#             try:
#                 job = CreateJob.objects.get(job_number=job_number)
#                 events = SequenceOfEventsMaster.objects.filter(job_number=job)
#                 if not events.exists():
#                     return Response({
#                         "message": f"No events found for job_number {job_number}."
#                     }, status=status.HTTP_404_NOT_FOUND)
#                 serializer = SequenceOfEventsSerializer(events, many=True)
#                 return Response(serializer.data, status=status.HTTP_200_OK)

#             except CreateJob.DoesNotExist:
#                 return Response({
#                     "error": f"No job found with job_number {job_number}."
#                 }, status=status.HTTP_404_NOT_FOUND)

#             except Exception as e:
#                 return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return Response({
#             "error": "job_number must be provided."
#         }, status=status.HTTP_400_BAD_REQUEST)

#     def post(self, request,job_number=None):
#         job_number = request.data.get('job_number')  
#         action_id = request.data.get('action_id')
#         if job_number is None or action_id is None:
#             return Response({
#                 "error": "job_number and action_id must be provided."
#             }, status=status.HTTP_400_BAD_REQUEST)

#         try:
            
#             job = CreateJob.objects.get(job_number=job_number)
#             action = SoeMaster.objects.get(id=action_id)
          
#             sequence_of_event = SequenceOfEventsMaster.objects.create(
#                 job_number=job,
#                 soe_desc=action.action 
#             )

           
#             serializer = SequenceOfEventsSerializer(sequence_of_event)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         except CreateJob.DoesNotExist:
#             return Response({
#                 "error": f"No job found with job_number {job_number}."
#             }, status=status.HTTP_404_NOT_FOUND)

#         except SoeMaster.DoesNotExist:
#             return Response({
#                 "error": f"No action found with action_id {action_id}."
#             }, status=status.HTTP_404_NOT_FOUND)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)