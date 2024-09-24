from rest_framework import serializers
from .models import (JobInfo,CustomerMaster,UnitofMeasureMaster,
                     ServiceType,RigMaster,WelltypeMaster,ToolMaster,HoleSection,
                     SurveyTypes,CreateJob,EmployeeMaster,SurveyInitialDataDetail,WellInfo,SurveyCalculationHeader,SurveyCalculationDetails,SurveyInfo, TieOnInformation)


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=ServiceType
        fields=['id','service_type']

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model= CustomerMaster
        fields = [ 'customer_id','customer_name']

class UnitOfMeasureSeializer(serializers.ModelSerializer):
    class Meta:
        model=UnitofMeasureMaster
        fields=['id','unit_of_measure']

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeMaster
        fields = ["emp_id","emp_name"] 

class RigMasterSerilalizer(serializers.ModelSerializer):
    class Meta:
        model= RigMaster
        fields=['id','rig_number']

class WelltypeSerializer(serializers.ModelSerializer):
    class Meta:
        model= WelltypeMaster
        fields=['id','well_type']

class WelltypeSerializer(serializers.ModelSerializer):
    class Meta:
        model= WelltypeMaster
        fields=['id','well_type']

class ToolTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model= ToolMaster
        fields=['id','type_of_tools']

class HoleSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model= HoleSection
        fields=['id','hole_section','survey_run_in','minimum_id']
        
class SurveyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model= SurveyTypes
        fields=['id','survey_types']


#-------------------JOB CREATION STARTS --------------

class CreateJobSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=CreateJob
        fields = ['job_number','location','assign_to' ,'customer','rig_number','unit_of_measure','estimated_date','service','job_created_date']


class JobInfoSerializer(serializers.ModelSerializer):
    job_number = CreateJobSerializer(read_only = True)
    class Meta:
        model=JobInfo
        fields=['client_rep','well_id','well_name','job_number']

class JodDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model=JobInfo
        fields="__all__"
class  TieOnInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TieOnInformation
        fields = '__all__'
class SurveyInitialDataSerializer(serializers.ModelSerializer):
     class Meta:
         model = SurveyInitialDataDetail
         fields = '__all__'
class SurveyInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyInfo
        fields = '__all__'
class WellInfoSerializer(serializers.ModelSerializer):
    north_coordinates = serializers.SerializerMethodField()
    east_coorinates = serializers.SerializerMethodField()
    w_t = serializers.SerializerMethodField()
    max_wt = serializers.SerializerMethodField()
    min_wt = serializers.SerializerMethodField()
    g_t = serializers.SerializerMethodField()
    max_gt = serializers.SerializerMethodField()
    min_gt = serializers.SerializerMethodField()

    class Meta:
        model = WellInfo
        fields='__all__'
    def get_north_coordinates(self, obj):
        return obj.get_north_coordinate
    def get_east_coorinates(self, obj):
        return obj.get_east_coordinate
    def get_w_t(self,obj):
        return obj.get_W_t
    def get_max_wt(self,obj):
        return obj.max_w_t
    def get_min_wt(self,obj):
        return obj.min_w_t
    def get_g_t(self,obj):
        return obj. get_G_t
    def get_max_gt(self,obj):
        return obj. max_G_t
    def get_min_gt(self,obj):
        return obj. min_G_t


class JobCreationSerializer(serializers.Serializer):
    job = CreateJobSerializer() 
    well_info = WellInfoSerializer()  
    survey_info = SurveyInfoSerializer()  
    tie_on_info = TieOnInformationSerializer() 
    job_info = JobInfoSerializer() 

    def create(self, validated_data):
      
        job_data = validated_data.pop('job')
        well_info_data = validated_data.pop('well_info')
        survey_info_data = validated_data.pop('survey_info')
        tie_on_info_data = validated_data.pop('tie_on_info')
        job_info_data = validated_data.pop('job_info')


        # Create the Job object
        job = CreateJob.objects.create(**job_data)
        well_info_data['job_number'] = job
        survey_info_data['job_number'] = job
        tie_on_info_data['job_number'] = job
        job_info_data['job_number'] = job

        WellInfo.objects.create(**well_info_data)
        SurveyInfo.objects.create(**survey_info_data)
        TieOnInformation.objects.create(**tie_on_info_data)

        return job
    
class SurveyCalculationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyCalculationHeader
        fields = '__all__'
class SurveyCalculationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyCalculationDetails
        fields='__all__'