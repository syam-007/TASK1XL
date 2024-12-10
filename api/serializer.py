from rest_framework import serializers
from .models import (JobInfo,CustomerMaster,UnitofMeasureMaster,
                     ServiceType,RigMaster,WelltypeMaster,ToolMaster,HoleSection,
                     SurveyTypes,CreateJob,EmployeeMaster,SurveyInitialDataDetail,WellInfo,SurveyCalculationHeader,SurveyCalculationDetails,SurveyInfo, 
                     TieOnInformation,AssetMasterDetails,AssetMasterHeader, GyrodataMaster,VehiclesDataMaster,
                     JobAssetMaster,SequenceOfEventsMaster,SoeMaster,InterPolationDataHeader,
                     InterPolationDataDeatils
                     )


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
        fields = "__all__"

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
# class SurveyRunInMaster(serializers.ModelSerializer):
#     class Meta:
#         model = SurveyRunInMaster
#         fields = "__all__"

# class MinimumIdSerailzer(serializers.ModelSerializer):
#     class Meta:
#         model = MinimumIdMaster
#         fields = "__all__"
        
class SurveyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model= SurveyTypes
        fields=['id','survey_types']

class SoeMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoeMaster
        fields = "__all__"


class SequenceOfEventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequenceOfEventsMaster
        fields = '__all__'



#-------------------JOB CREATION STARTS --------------#

class CreateJobSerializer(serializers.ModelSerializer):
    class Meta:
        model=CreateJob
        fields = ['job_number','location','assign_to' ,'customer','rig_number','estimated_date','unit_of_measure','service','job_created_date']


class JobInfoSerializer(serializers.ModelSerializer):
    # job_number = CreateJobSerializer(read_only = True)
    class Meta:
        model=JobInfo
        fields="__all__"

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
    grid_correction = serializers.SerializerMethodField()

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
    def get_grid_correction(self,obj):
        return obj.get_grid_correction

class AssetHeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetMasterHeader
        fields ='__all__'

class AssetInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetMasterDetails
        fields = '__all__'

class GyroDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = GyrodataMaster
        fields = '__all__'

class VehicleSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = VehiclesDataMaster
        fields = '__all__'
class JobAssetSerializer(serializers.ModelSerializer):
       
        cost_center = serializers.PrimaryKeyRelatedField(queryset=AssetMasterHeader.objects.all())
        gyro_data = serializers.PrimaryKeyRelatedField(queryset=GyrodataMaster.objects.all())
        vehicle = serializers.PrimaryKeyRelatedField(queryset=VehiclesDataMaster.objects.all())
        emp_1 = serializers.PrimaryKeyRelatedField(queryset=EmployeeMaster.objects.all())
        emp_2 = serializers.PrimaryKeyRelatedField(queryset=EmployeeMaster.objects.all())
        emp_3 = serializers.PrimaryKeyRelatedField(queryset=EmployeeMaster.objects.all())
        emp_4 = serializers.PrimaryKeyRelatedField(queryset=EmployeeMaster.objects.all())
        emp_5 = serializers.PrimaryKeyRelatedField(queryset=EmployeeMaster.objects.all())
        emp_6 = serializers.PrimaryKeyRelatedField(queryset=EmployeeMaster.objects.all())
        emp_7 = serializers.PrimaryKeyRelatedField(queryset=EmployeeMaster.objects.all())
        class Meta:
            model = JobAssetMaster
            fields = [
                 'cost_center', 'gyro_data', 'vehicle', 
                'emp_1', 'emp_2', 'emp_3', 'emp_4', 'emp_5', 'emp_6', 'emp_7'
            ]


# class JobAssetSerializer(serializers.ModelSerializer):
#     cost_center = AssetHeaderSerializer(read_only=True)
#     gyro_data = GyroDataSerializer(read_only=True)
#     vehicle = VehicleSerilaizer(read_only=True)
#     emp_1 =  EmployeeSerializer(read_only=True)
#     emp_2 =  EmployeeSerializer(read_only=True)
#     emp_3 =  EmployeeSerializer(read_only=True)
#     emp_4 =  EmployeeSerializer(read_only=True)
#     emp_5 =  EmployeeSerializer(read_only=True)
#     emp_6 =  EmployeeSerializer(read_only=True)
#     emp_7 =  EmployeeSerializer(read_only=True)

#     class Meta:
#         model = JobAssetMaster
#         fields = [
#             'cost_center', 'gyro_data', 'vehicle', 
#             'emp_1', 'emp_2', 'emp_3', 'emp_4', 'emp_5', 'emp_6', 'emp_7'
#         ]


        
class CompleteJobCreationSerializer(serializers.Serializer):
    job_info = JobInfoSerializer()
    well_info = WellInfoSerializer()
    survey_info = SurveyInfoSerializer()
    tie_on_information = TieOnInformationSerializer()
    asset_master = JobAssetSerializer()

    def create(self, validated_data):
        job_info_data = validated_data.pop('job_info')
        well_info_data = validated_data.pop('well_info')
        survey_info_data = validated_data.pop('survey_info')
        tie_on_info_data = validated_data.pop('tie_on_information')
        asset_master_data = validated_data.pop('asset_master')

       
        job_info = JobInfoSerializer().create(validated_data=job_info_data)
        job_number = job_info.job_number 

       
        well_info = WellInfo.objects.create(**well_info_data)
        survey_info = SurveyInfo.objects.create(**survey_info_data)
        tie_on_information = TieOnInformation.objects.create(**tie_on_info_data)

       
        asset_master_data['job_number'] = job_number 
        asset_master = JobAssetMaster.objects.create(**asset_master_data)

        
        return {
            'job_info': job_info,
            'well_info': well_info,
            'survey_info': survey_info,
            'tie_on_information': tie_on_information,
            'asset_master': asset_master
        }

    
class SurveyCalculationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyCalculationHeader
        fields = '__all__'
class SurveyCalculationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyCalculationDetails
        fields='__all__'

class InterPolationDataHeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterPolationDataHeader
        fields = ['id','resolution', 'range_from', 'range_to', 'job_number', 'run_number', 'status']
    def validate(self, data):
        # Custom validation logic if needed
        if data.get('range_from') and data.get('range_to') and data['range_from'] > data['range_to']:
            raise serializers.ValidationError("'range_from' cannot be greater than 'range_to'.")
        return data

class InterPolationDataDeatilsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterPolationDataDeatils
        fields = "__all__"