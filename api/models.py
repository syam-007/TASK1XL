from django.db import models
from django.conf import settings
import math
from django.conf import settings



class ServiceType(models.Model):
    id = models.AutoField(primary_key=True)
    service_type = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.service_type

    class Meta:
        db_table = 'task_service_master'

class CustomerMaster(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=255)
    def __str__(self) -> str:
        return self.customer_name
    class Meta:
        db_table = 'task_customer_master'
        

class UnitofMeasureMaster(models.Model):
    id = models.AutoField(primary_key=True)
    unit_of_measure = models.CharField(max_length=3)

    def __str__(self) -> str:
        return self.unit_of_measure
    
    class Meta:
        db_table = 'task_unit_of_measure'
       
class RigMaster(models.Model):
    id = models.AutoField(primary_key=True)
    rig_number = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.rig_number

    class Meta:
        db_table = 'task_rig_master'

class EmployeeMaster(models.Model):
    id = models.AutoField(primary_key=True)
    emp_id = models.CharField(max_length=255,unique=True)
    emp_name = models.CharField(max_length=255)
    emp_short_name = models.CharField(max_length=255,null=True)
    emp_designation = models.CharField(max_length=255,null=True)
    # user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)

    def __str__(self) -> str:
        return self.emp_name
    class Meta:
        db_table = 'task_employee_master'


class WelltypeMaster(models.Model):
    id = models.AutoField(primary_key=True)
    well_type = models.CharField(max_length=255)
    class Meta:
        db_table = 'task_well_type_master'

class ToolMaster(models.Model):
    id = models.AutoField(primary_key=True)
    type_of_tools = models.CharField(max_length=255)
    class Meta:
        db_table = 'task_tools_master'

class HoleSection(models.Model):
    id = models.AutoField(primary_key=True)
    hole_section = models.CharField(max_length=255)
    survey_run_in = models.CharField(max_length=255)  
    minimum_id = models.CharField(max_length=100)
    class Meta:
        db_table = 'task_holesection_master'

class SurveyTypes(models.Model):
    id = models.AutoField(primary_key=True)
    survey_types = models.CharField(max_length=255)
    class Meta:
        db_table = 'task_survey_types_master'

class CreateJob(models.Model):
    job_number = models.CharField(max_length=255,unique=True,primary_key=True)
    service = models.ForeignKey(ServiceType,on_delete=models.PROTECT)
    assign_to = models.ForeignKey(EmployeeMaster,on_delete=models.PROTECT,db_column='assign_to')
    location = models.CharField(max_length=255)
    customer = models.ForeignKey(CustomerMaster,on_delete=models.PROTECT)
    rig_number = models.ForeignKey(RigMaster,on_delete=models.PROTECT,db_column='rig_number')
    unit_of_measure = models.ForeignKey(UnitofMeasureMaster,on_delete=models.PROTECT,db_column='unit_of_measure')
    estimated_date = models.DateTimeField()
    job_created_date = models.DateTimeField()
    job_assign_date = models.DateTimeField(auto_now=True)
    
    class Meta:
      db_table = 'task_create_job'


class JobInfo(models.Model):
    job_number = models.ForeignKey(CreateJob, on_delete=models.PROTECT, db_column='job_number')
    client_rep = models.CharField(max_length=255)
    arrival_date = models.DateTimeField()
    well_id = models.IntegerField()
    well_name = models.CharField(max_length=255)
   
    class Meta:
        db_table = 'task_job_info'

    @property
    def service(self):
        return self.job_number.service

    @property
    def rig(self):
        return self.job_number.rig_number

    @property
    def customer(self):
        return self.job_number.customer

    @property
    def unit_of_measure(self):
        return self.job_number.unit_of_measure

    @property
    def job_created_date(self):
        return self.job_number.job_created_date

    @property
    def job_assign_date(self):
        return self.job_number.job_assign_date

    @property
    def location(self):
        return self.job_number.location
    

class WellInfo(models.Model):
    well_info_id = models.AutoField(primary_key=True)
    well_id = models.IntegerField()
    job_number = models.ForeignKey(CreateJob,on_delete=models.PROTECT,)
    latitude_1 = models.IntegerField()
    latitude_2 = models.IntegerField()
    latitude_3 = models.DecimalField(max_digits=7,decimal_places=5)
    longitude_1 = models.IntegerField()
    longitude_2 = models.IntegerField()
    longitude_3 = models.DecimalField(max_digits=7,decimal_places=5)
    northing = models.DecimalField(max_digits=12,decimal_places=4)
    easting = models.DecimalField(max_digits=12,decimal_places=4)
    well_type = models.ForeignKey(WelltypeMaster,on_delete=models.PROTECT)
    expected_well_temp = models.IntegerField()
    expected_wellbore_inclination= models.IntegerField()
    central_meridian = models.IntegerField()
    GLE = models.DecimalField(max_digits=6,decimal_places=2)
    RKB = models.DecimalField(max_digits=6,decimal_places=2)
    ref_elivation = models.CharField(max_length=255)
    ref_datum  = models.CharField(max_length=255)


    class Meta:
        db_table = 'task_well_info'
    @property
    def get_north_coordinate(self):
        north_coordinate = self.latitude_1 + (((self.latitude_3 / 60) + self.latitude_2) / 60)
        return float(f"{north_coordinate:.8f}")
    @property
    def get_east_coordinate(self):
        east_coordinate = self.longitude_1 + (((self.longitude_3 / 60) + self.longitude_2) / 60)
        return float(f"{ east_coordinate:.8f}")
    @property
    def get_W_t(self):  
        PI = math.pi 
        north_coord_in_radians = math.radians(self.get_north_coordinate)
        return round(15.041 * math.cos(north_coord_in_radians),2) 
    @property
    def max_w_t(self):  
        return round(self.get_W_t + 3,2) 
    @property
    def min_w_t(self):  
        return round(self.get_W_t - 3,2) 
    @property
    def get_G_t(self): 
        north_coord = float(self.get_north_coordinate)
        north_coord_radians = math.radians(north_coord)
        two_north_coord_radians = math.radians(2 * north_coord)
        G18 = float(self.GLE)
        G_t = (
            (9.780327 * (1 + (0.0053024 * (math.sin(north_coord_radians) ** 2)) -
            (0.0000058 * (math.sin(two_north_coord_radians) ** 2)))) - ((3.086 * 10 ** -6) * G18)
        ) * 102
        return float(f"{G_t:.5f}")
    @property
    def max_G_t(self):  
        return round(self.get_G_t + 10,2) 
    @property
    def min_G_t(self):  
        return round(self.get_G_t - 10,2) 
    @property
    def get_grid_correction(self):
        central_meridian = self.central_meridian
        longitude = self.get_east_coordinate
        latitude = self.get_north_coordinate
        grid_correction = (longitude - central_meridian) * math.sin(math.radians(latitude))
        return round(grid_correction, 6)

class SurveyInfo(models.Model):
    survey_info_id = models.AutoField(primary_key=True)
    run_name = models.CharField(max_length=50)
    job_number = models.ForeignKey(CreateJob,on_delete=models.PROTECT,db_column='job_number')
    run_number = models.IntegerField()
    type_of_tool = models.ForeignKey(ToolMaster,on_delete=models.PROTECT)
    survey_type = models.ForeignKey(SurveyTypes,on_delete=models.PROTECT)
    hole_section = models.ForeignKey(HoleSection,on_delete=models.PROTECT)
    survey_run_in = models.CharField(max_length=255)
    minimum_id = models.CharField(max_length=100) 
    north_reference = models.CharField(max_length=255)
    survey_calculation_method = models.CharField(max_length=255)
    geodetic_system = models.CharField(max_length=255)
    map_zone = models.CharField(max_length=255)
    geodetic_system = models.CharField(max_length=255)
    geodetic_datum = models.CharField(max_length=255)
    start_depth = models.IntegerField()
    tag_depth = models.IntegerField()
    proposal_direction = models.DecimalField(max_digits=6,decimal_places=2)

    class Meta:
        db_table = 'task_survey_info'
    def save(self, *args, **kwargs):
        if self.hole_section:
            self.survey_run_in = self.hole_section.survey_run_in
            self.minimum_id = self.hole_section.minimum_id

        super(SurveyInfo, self).save(*args, **kwargs)


class TieOnInformation(models.Model):
    measured_depth = models.DecimalField(max_digits=6,decimal_places=2)
    true_vertical_depth = models.DecimalField(max_digits=6,decimal_places=2)
    inclination = models.DecimalField(max_digits=6,decimal_places=2)
    latitude = models.DecimalField(max_digits=6,decimal_places=2)
    azimuth = models.DecimalField(max_digits=6,decimal_places=2)
    departure = models.DecimalField(max_digits=6,decimal_places=2)
    job_number = models.ForeignKey(CreateJob,on_delete=models.PROTECT,db_column='job_number')
    run_number = models.SmallIntegerField()
    class Meta:
        db_table = 'task_survey_tie_on_info'


class SequenceOfEventsMaster(models.Model):
    soe_desc = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now=True)
    job_number = models.ForeignKey(CreateJob,on_delete=models.CASCADE,db_column="job_number")

    class Meta:
        db_table = 'task_soe_Details'

class SoeMaster(models.Model):

    action = models.CharField(max_length=255)
    class Meta:
        db_table = 'task_soe_master'


class AssetMasterHeader(models.Model):
    header = models.CharField(max_length=255)
    class Meta:
        db_table = 'task_asset_master_header'

class AssetMasterDetails(models.Model):
    asset_code =models.CharField(max_length=255,null=True)
    asset_group = models.CharField(max_length=255,null=True)
    asset_main_category = models.CharField(max_length=255,null=True)
    asset_description = models.CharField(max_length=255)
    serial_no = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    cost_center = models.ForeignKey(AssetMasterHeader,on_delete=models.PROTECT,db_column="cost_center")

    class Meta:
        db_table = 'task_asset_master_details'

class GyrodataMaster(models.Model):
    asset_code =models.CharField(max_length=255,null=True)
    asset_group = models.CharField(max_length=255,null=True)
    asset_main_category = models.CharField(max_length=255,null=True)
    asset_description = models.CharField(max_length=255)
    serial_no = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    

    class Meta:
        db_table = 'task_gyrodata_master'

class VehiclesDataMaster(models.Model):
    asset_code =models.CharField(max_length=255,null=True)
    physical_location = models.CharField(max_length=255,null=True)
    asset_main_category = models.CharField(max_length=255,null=True)
    asset_description = models.CharField(max_length=255)
    serial_no = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    class Meta:
        db_table = 'task_vehicle_master'


class JobAssetMaster(models.Model):
    job_number = models.ForeignKey(CreateJob,models.PROTECT,db_column="job_number",null=True)
    cost_center = models.ForeignKey(AssetMasterHeader,on_delete=models.PROTECT,db_column="cost_center")
    gyro_data = models.ForeignKey(GyrodataMaster,models.PROTECT,db_column="gyro_data")
    vehicle = models.ForeignKey(VehiclesDataMaster,on_delete=models.PROTECT,db_column="vehicle")
    emp_1 = models.ForeignKey(EmployeeMaster, on_delete=models.PROTECT, related_name='emp_1_jobs',db_column="emp_1")
    emp_2 = models.ForeignKey(EmployeeMaster, on_delete=models.PROTECT, related_name='emp_2_jobs',db_column="emp_2")
    emp_3 = models.ForeignKey(EmployeeMaster, on_delete=models.PROTECT, related_name='emp_3_jobs',db_column="emp_3")
    emp_4 = models.ForeignKey(EmployeeMaster, on_delete=models.PROTECT, related_name='emp_4_jobs',db_column="emp_4")
    emp_5 = models.ForeignKey(EmployeeMaster, on_delete=models.PROTECT, null=True, related_name='emp_5_jobs',db_column="emp_5")
    emp_6 = models.ForeignKey(EmployeeMaster, on_delete=models.PROTECT, null=True, related_name='emp_6_jobs',db_column="emp_6")
    emp_7 = models.ForeignKey(EmployeeMaster, on_delete=models.PROTECT, null=True, related_name='emp_7_jobs',db_column="emp_7")
    class Meta:
        db_table = 'task_job_asset_master'
    
    
class SurveyInitialDataHeader(models.Model):
    id = models.AutoField(primary_key=True)
    job_number = models.ForeignKey(CreateJob,on_delete = models.CASCADE,db_column='job_number')
    survey_type = models.ForeignKey(SurveyTypes,on_delete = models.CASCADE,db_column='survey_type')
    survey_date = models.DateField(auto_now_add=True)
    run_number = models.SmallIntegerField()
    
    class Meta:
        db_table = 'task_survey_initial_data_header'

class SurveyInitialDataDetail(models.Model):
    id = models.AutoField(primary_key=True)
    job_number = models.ForeignKey(CreateJob,on_delete=models.CASCADE,db_column='job_number')
    header = models.ForeignKey(SurveyInitialDataHeader, on_delete=models.CASCADE, related_name='details', db_column='header_id')
    depth = models.DecimalField(max_digits=6,decimal_places=2)
    Inc = models.DecimalField(max_digits=3,decimal_places=2)
    AzG = models.DecimalField(max_digits=5,decimal_places=2)
    g_t = models.DecimalField(max_digits=6,decimal_places=2,db_column="G(t)")
    w_t = models.DecimalField(max_digits=6,decimal_places=2,db_column="W(t)")
    g_t_status = models.CharField(max_length=10) 
    w_t_status = models.CharField(max_length=10)
    status = models.CharField(max_length=10) 
    g_t_difference = models.DecimalField(max_digits=10, decimal_places=2)
    w_t_difference = models.DecimalField(max_digits=10, decimal_places=2)
    run_number = models.SmallIntegerField()
  
    class Meta:
        db_table = 'task_survey_initial_data_detail'

class SurveyCalculationHeader(models.Model):
    job_number = models.ForeignKey(CreateJob,on_delete=models.CASCADE,db_column='job_number')
    depth  = models.DecimalField(max_digits=6,decimal_places=2)
    inclination = models.DecimalField(max_digits=3,decimal_places=2)
    azimuth = models.DecimalField(max_digits=6,decimal_places=2)
    Vertical_Section = models.DecimalField(max_digits=3,decimal_places=2)
    true_vertical_depth = models.DecimalField(max_digits=5,decimal_places=2,db_column='TVD')
    latitude = models.DecimalField(max_digits=3,decimal_places=2,db_column="+N/-S")
    departure = models.DecimalField(max_digits=3,decimal_places=2,db_column="+E/-W")
    DLS = models.DecimalField(max_digits=4,decimal_places=2,null=True)
    closure_distance= models.DecimalField(max_digits=4,decimal_places=2)
    closure_direction = models.DecimalField(max_digits=4,decimal_places=2)
    CL = models.DecimalField(max_digits=4,decimal_places=2,null=True)
    dog_leg = models.DecimalField(max_digits=6,decimal_places=5,null=True)
    ratio_factor = models.DecimalField(max_digits=6,decimal_places=5,null=True)
    run = models.SmallIntegerField()
   
    class Meta:
        db_table = 'task_survey_calculation_header'

class SurveyCalculationDetails(models.Model):
    header_id = models.ForeignKey(SurveyCalculationHeader,on_delete=models.CASCADE,db_column='header_id')
    measured_depth = models.DecimalField(max_digits=6,decimal_places=2)
    inclination = models.DecimalField(max_digits=8,decimal_places=4)
    azimuth = models.DecimalField(max_digits=8,decimal_places=4)
    tvd = models.DecimalField(max_digits=5,decimal_places=2,null=True)
    Vertical_Section = models.DecimalField(max_digits=3,decimal_places=2)
    latitude = models.DecimalField(max_digits=4,decimal_places=2,db_column="+N/-S")
    departure = models.DecimalField(max_digits=6,decimal_places=3,db_column="+E/-W")
    DLS = models.DecimalField(max_digits=4,decimal_places=3,null=True)
    closure_distance= models.DecimalField(max_digits=6,decimal_places=2)
    closure_direction = models.DecimalField(max_digits=6,decimal_places=2)
    CL = models.DecimalField(max_digits=4,decimal_places=2,null=True)
    dog_leg = models.DecimalField(max_digits=6,decimal_places=5,null=True)
    ratio_factor = models.DecimalField(max_digits=6,decimal_places=5,null=True)
    
    class Meta:
        db_table = 'task_survey_calculation_details'


class InterPolationDataHeader(models.Model):
    resolution = models.DecimalField(max_digits=6, decimal_places=2)
    range_from = models.IntegerField(null=True)
    range_to = models.IntegerField(null=True)
    job_number = models.ForeignKey(CreateJob, on_delete=models.CASCADE, db_column='job_number')
    run_number = models.SmallIntegerField()
    date = models.DateTimeField(auto_now=True)
    status = models.SmallIntegerField(default=0)

    class Meta:
        db_table = 'task_survey_interpolation_header'

class InterPolationDataDeatils(models.Model):
    header_id = models.ForeignKey(InterPolationDataHeader,on_delete=models.PROTECT,db_column='header_id')
    resolution = models.FloatField()
    new_depth = models.FloatField()
    inclination = models.FloatField()
    azimuth = models.FloatField()
    dog_leg = models.FloatField()
    CL = models.FloatField()  # Closure Length
    ratio_factor = models.FloatField()
    tvd = models.FloatField()  # True Vertical Depth
    latitude = models.FloatField()
    departure = models.FloatField()
    closure_distance = models.FloatField()
    closure_direction = models.FloatField()
    DLS = models.FloatField()  # Dog Leg Severity
    vertical_section = models.FloatField()
    survey_status = models.IntegerField()

    def __str__(self):
        return f"TaskSurveyInterpolationDetails({self.job_number}, {self.run_number}, {self.new_depth})"
    
    class Meta:
        db_table = 'task_survey_interpolation_details'
    


   

    
