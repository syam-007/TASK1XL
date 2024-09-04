from django.db import models
from core.models import User



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
    user_id = models.ForeignKey(User,on_delete = models.PROTECT,db_column='user_id')
    emp_id = models.CharField(max_length=255,unique=True)
    emp_name = models.CharField(max_length=255)
    emp_short_name = models.CharField(max_length=255)
    emp_designation = models.CharField(max_length=255)
    
    

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
    assign_to = models.ForeignKey(EmployeeMaster,on_delete=models.PROTECT)
    location = models.CharField(max_length=255)
    customer = models.ForeignKey(CustomerMaster,on_delete=models.PROTECT)
    rig_number = models.ForeignKey(RigMaster,on_delete=models.PROTECT)
    unit_of_measure = models.ForeignKey(UnitofMeasureMaster,on_delete=models.PROTECT)
    estimated_date = models.DateTimeField()
    job_created_date = models.DateTimeField(auto_now=True)
    job_assign_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'task_create_job'
        # permissions = [
        #     ('cancel_job','can cancel job')
        # ]

class JobInfo(models.Model):
    job_number = models.ForeignKey(CreateJob, on_delete=models.PROTECT, db_column='job_number')
    client_rep = models.CharField(max_length=255)
    arrival_date = models.DateField(auto_now_add=True)
    well_id = models.IntegerField()
    well_name = models.CharField(max_length=255)
    estimated_date = models.DateTimeField()

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



    # def save(self, *args, **kwargs):
    #     if not self.job_number:
    #         prefix = "OM"
    #         last_job = JobInfo.objects.all().order_by('job_number').last()
    #         if last_job:
    #             last_job_number = int(last_job.job_number[2:]) 
    #             new_job_number = last_job_number + 1
    #         else:
    #             new_job_number = 1100

    #         self.job_number = f"{prefix}{new_job_number}"

    #     super(JobInfo, self).save(*args, **kwargs)    
    
class WellInfo(models.Model):
    well_info_id = models.AutoField(primary_key=True)
    well_id = models.IntegerField()
    job_number = models.ForeignKey(CreateJob,on_delete=models.PROTECT)
    latitude_1 = models.IntegerField()
    latitude_2 = models.IntegerField()
    latitude_3 = models.DecimalField(max_digits=4,decimal_places=2)
    longitude_1 = models.IntegerField()
    longitude_2 = models.IntegerField()
    longitude_3 = models.DecimalField(max_digits=4,decimal_places=2)
    northing = models.DecimalField(max_digits=10,decimal_places=4)
    easting = models.DecimalField(max_digits=10,decimal_places=4)
    well_type = models.ForeignKey(WelltypeMaster,on_delete=models.PROTECT)
    expected_well_temp = models.IntegerField()
    expected_wellbore_inclination= models.IntegerField()
    central_meridian = models.IntegerField()
    GLE = models.DecimalField(max_digits=3,decimal_places=2)
    RKB = models.DecimalField(max_digits=3,decimal_places=2)
    ref_elivation = models.CharField(max_length=255)
    ref_datum  = models.CharField(max_length=255) 

    class Meta:
        db_table = 'task_well_info'


class SurveyInfo(models.Model):
    survey_info_id = models.AutoField(primary_key=True)
    run_name = models.CharField(max_length=3)
    job_number = models.ForeignKey(CreateJob,on_delete=models.PROTECT)
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
    proposal_direction = models.IntegerField()

    class Meta:
        db_table = 'task_survey_info'
    def save(self, *args, **kwargs):
        if self.hole_section:
            self.survey_run_in = self.hole_section.survey_run_in
            self.minimum_id = self.hole_section.minimum_id

        super(SurveyInfo, self).save(*args, **kwargs)
   
class TieOnInformation(models.Model):
    measured_depth = models.IntegerField()
    true_vertical_depth = models.IntegerField()
    inclination = models.IntegerField()
    latitude = models.IntegerField()
    azimuth = models.IntegerField()
    departure = models.IntegerField()
    job_number = models.ForeignKey(CreateJob,on_delete=models.PROTECT)
    class Meta:
        db_table = 'task_survey_tie_on_info'

class ToolsData(models.Model):
    job_number = models.ForeignKey(CreateJob,on_delete=models.PROTECT)
    Measured_Depth = models.DecimalField(max_digits=3,decimal_places=2)
    Inclination = models.DecimalField(max_digits=3,decimal_places=2)
    Azimuth = models.DecimalField(max_digits=3,decimal_places=2)

    class Meta:
        db_table = 'task_tools_data'
class SurveyInitialDataDetail(models.Model):
    id = models.AutoField(primary_key=True)
    depth = models.IntegerField()
    Inc = models.DecimalField(max_digits=3,decimal_places=2)
    AzG = models.DecimalField(max_digits=5,decimal_places=2)
    class Meta:
        db_table = 'task_survey_initial_data_detail'


