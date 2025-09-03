############################################## MSSQL ###########################################################

#################### TABLES ####################

from django.db import models
import uuid

# Table_1: Client Project Details
class ClientProject(models.Model):
    cp_id = models.AutoField(db_column='ClientID', primary_key=True)  # Field name made lowercase.
    client_name = models.CharField(db_column='ClientName', max_length=100)  # Field name made lowercase.
    project_name = models.CharField(db_column='ProjectName', max_length=100)  # Field name made lowercase.
    assessment_type = models.CharField(db_column='AssessmentType', max_length=50, blank=True, null=True)  # Field name made lowercase.
    start_date = models.DateField(db_column='ProjectStartDate')  # Field name made lowercase.
    end_date = models.DateField(db_column='ProjectEndDate')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'client_project'
        unique_together = (('client_name', 'project_name'),)

    def __str__(self):
        return f"{self.client_name} - {self.project_name}"

# Table_2: Super Users
class SuperUser(models.Model):
    cp = models.OneToOneField(ClientProject, models.DO_NOTHING, db_column='ClientID', primary_key=True)  # Field name made lowercase. The composite primary key (ClientID, SuperUserEmail) found, that is not supported. The first column is selected.
    super_user_first_name = models.CharField(db_column='SuperUserFirstName', max_length=100)  # Field name made lowercase.
    super_user_last_name = models.CharField(db_column='SuperUserLastName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    super_user_email = models.CharField(db_column='SuperUserEmail', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'client_superuser'
        unique_together = (('cp', 'super_user_email'),)
    def __str__(self):
        return f"{self.super_user_first_name} {self.super_user_last_name}"


class MainClient(models.Model):
    clientid = models.AutoField(db_column='ClientID', primary_key=True)  # Field name made lowercase.
    clientname = models.CharField(db_column='ClientName', max_length=255)  # Field name made lowercase.
    projectname = models.CharField(db_column='ProjectName', max_length=255)  # Field name made lowercase.
    superusername = models.CharField(db_column='SuperUserName', max_length=255)  # Field name made lowercase.
    superuseremail = models.CharField(db_column='SuperUserEmail', max_length=255)  # Field name made lowercase.
    assessmenttype = models.CharField(db_column='AssessmentType', max_length=50, blank=True, null=True)  # Field name made lowercase.
    projectstartdate = models.DateField(db_column='ProjectStartDate')  # Field name made lowercase.
    projectenddate = models.DateField(db_column='ProjectEndDate')  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'main_client'


class MainQuestion(models.Model):
    questionid = models.AutoField(db_column='QuestionID', primary_key=True)  # Field name made lowercase.
    clientname = models.CharField(db_column='ClientName', max_length=255)  # Field name made lowercase.
    projectname = models.CharField(db_column='ProjectName', max_length=255)  # Field name made lowercase.
    questiontext = models.CharField(db_column='QuestionText', max_length=255)  # Field name made lowercase.
    questiontype = models.CharField(db_column='QuestionType', max_length=50)  # Field name made lowercase.
    competency = models.CharField(db_column='Competency', max_length=50)  # Field name made lowercase.
    clientid = models.ForeignKey(MainClient, models.DO_NOTHING, db_column='ClientID')  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'main_question'


class MainUser(models.Model):
    userid = models.AutoField(db_column='UserID', primary_key=True)  # Field name made lowercase.
    clientname = models.CharField(db_column='ClientName', max_length=255)  # Field name made lowercase.
    projectname = models.CharField(db_column='ProjectName', max_length=255)  # Field name made lowercase.
    seekername = models.CharField(db_column='SeekerName', max_length=255)  # Field name made lowercase.
    seekeremail = models.CharField(db_column='SeekerEmail', max_length=255)  # Field name made lowercase.
    providername = models.CharField(db_column='ProviderName', max_length=255)  # Field name made lowercase.
    provideremail = models.CharField(db_column='ProviderEmail', max_length=255)  # Field name made lowercase.
    relationship = models.CharField(db_column='Relationship', max_length=50)  # Field name made lowercase.
    cp = models.ForeignKey(MainClient, models.DO_NOTHING, db_column='ClientID')  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=50)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'main_user'

# Table_3: Seeker Details
class Seeker(models.Model):
    seeker_id = models.AutoField(db_column='SeekerID', primary_key=True)  # Field name made lowercase.
    seeker_first_name = models.CharField(db_column='FirstName', max_length=100)  # Field name made lowercase.
    seeker_last_name = models.CharField(db_column='LastName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    seeker_email = models.CharField(db_column='Email', max_length=255)  # Field name made lowercase.
    cp = models.ForeignKey(ClientProject, models.DO_NOTHING, db_column='ClientID')  # Field name made lowercase.
    user_id = models.ForeignKey(MainUser, models.DO_NOTHING, db_column='UserID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'seeker'

    def __str__(self):
        return f"{self.seeker_first_name} {self.seeker_last_name}"

# # Table_4: Provider Details
# class Provider(models.Model):
#     provider_id = models.AutoField(db_column='ProviderID', primary_key=True)  # Field name made lowercase.
#     provider_first_name = models.CharField(db_column='FirstName', max_length=100)  # Field name made lowercase.
#     provider_last_name = models.CharField(db_column='LastName', max_length=100, blank=True, null=True)  # Field name made lowercase.
#     provider_email = models.CharField(db_column='Email', max_length=255)  # Field name made lowercase.
#     cp = models.ForeignKey(ClientProject, models.DO_NOTHING, db_column='ClientID')  # Field name made lowercase.
#     user_id = models.ForeignKey(MainUser, models.DO_NOTHING, db_column='UserID')  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'provider'

#     def __str__(self):
#         return f"{self.provider_first_name} {self.provider_last_name}"

# Table_4: Provider Details
class Provider(models.Model):
    provider_id = models.AutoField(db_column='ProviderID', primary_key=True)  # Field name made lowercase.
    provider_first_name = models.CharField(db_column='FirstName', max_length=100)  # Field name made lowercase.
    provider_last_name = models.CharField(db_column='LastName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    provider_email = models.CharField(db_column='Email', max_length=255)  # Field name made lowercase.
    cp = models.ForeignKey(ClientProject, models.DO_NOTHING, db_column='ClientID')  # Field name made lowercase.
    user_id = models.ForeignKey(MainUser, models.DO_NOTHING, db_column='UserID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'provider_copy'

    def __str__(self):
        return f"{self.provider_first_name} {self.provider_last_name}"
    

# Table_5: Relationships
# class SeekerProviderLink(models.Model):
# class Relationship(models.Model):
#     #cp = models.ForeignKey(ClientProject, models.DO_NOTHING, db_column='ClientID')
#     seeker_id = models.ForeignKey(Seeker, models.DO_NOTHING, db_column='SeekerID')  # Field name made lowercase. The composite primary key (SeekerID, ProviderID) found, that is not supported. The first column is selected.
#     provider_id = models.ForeignKey(Provider, models.DO_NOTHING, db_column='ProviderID')  # Field name made lowercase.
#     relationship = models.CharField(db_column='Relationship', max_length=50)  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'seeker_provider_link'
#         unique_together = (('seeker_id', 'provider_id'),)

# class Relationship(models.Model):
#     seeker_id = models.IntegerField(db_column='SeekerID', primary_key=True)  # Field name made lowercase. The composite primary key (SeekerID, ProviderID) found, that is not supported. The first column is selected.
#     provider_id = models.ForeignKey(Provider, models.DO_NOTHING, db_column='ProviderID')  # Field name made lowercase.
#     relationship = models.CharField(db_column='Relationship', max_length=50)  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'seeker_provider_link'
#         unique_together = (('seeker_id', 'provider_id'),)

# class Relationship(models.Model):
#     seeker_id = models.ForeignKey(Seeker, models.DO_NOTHING, db_column='SeekerID')  # Field name made lowercase. The composite primary key (SeekerID, ProviderID) found, that is not supported. The first column is selected.
#     provider_id = models.ForeignKey(Provider, models.DO_NOTHING, db_column='ProviderID')  # Field name made lowercase.
#     relationship = models.CharField(db_column='Relationship', max_length=50)  # Field name made lowercase.

#     class Meta:
#         managed = False
#         db_table = 'seeker_provider_link'
#         unique_together = (('seeker_id', 'provider_id'),)

#     def __str__(self):
#         return f"Relationship between {self.seeker_id} and {self.provider_id}: {self.relationship}"
    
# class Relationship(models.Model):
#     seeker_id = models.ForeignKey(Seeker, on_delete=models.DO_NOTHING, db_column='SeekerID', unique=True)
#     provider_id = models.ForeignKey(Provider, on_delete=models.DO_NOTHING, db_column='ProviderID')
#     relationship = models.CharField(db_column='Relationship', max_length=50)

#     class Meta:
#         managed = False  # The table is already created in the database
#         #db_table = 'seeker_provider_link'
#         unique_together = (('seeker_id', 'provider_id'),)

#     def __str__(self):
#         return f"Relationship between {self.seeker_id} and {self.provider_id}: {self.relationship}"


    
# Table_5: Questions
class Question(models.Model):
    question_id = models.IntegerField(db_column='QuestionID', primary_key=True)  # Field name made lowercase.
    question_text = models.CharField(db_column='QuestionText', max_length=500, blank=True, null=True)  # Field name made lowercase.
    question_type = models.CharField(db_column='QuestionType', max_length=50, blank=True, null=True)  # Field name made lowercase.
    competency = models.CharField(db_column='Competency', max_length=100, blank=True, null=True)  # Field name made lowercase.
    cp = models.ForeignKey(ClientProject, models.DO_NOTHING, db_column='ClientID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'question'
    def __str__(self):
        return self.question_text
    
# Table_6: Feedback
class Feedback(models.Model):
    cp = models.OneToOneField(ClientProject, models.DO_NOTHING, db_column='ClientID', primary_key=True)  # Field name made lowercase. The composite primary key (ClientID, SeekerID, ProviderID, QuestionID) found, that is not supported. The first column is selected.
    seeker_id = models.ForeignKey(Seeker, models.DO_NOTHING, db_column='SeekerID')  # Field name made lowercase.
    provider_id = models.ForeignKey(Provider, models.DO_NOTHING, db_column='ProviderID')  # Field name made lowercase.
    question_id = models.ForeignKey(Question, models.DO_NOTHING, db_column='QuestionID')  # Field name made lowercase.
    feedback_value = models.IntegerField(db_column='FeedbackValue', blank=True, null=True)  # Field name made lowercase.
    feedback_text = models.CharField(db_column='FeedbackText', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    feedback_status = models.CharField(db_column='FeedbackStatus', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'feedback'
        unique_together = (('cp', 'seeker_id', 'provider_id', 'question_id'),)


#################### VIEWS ####################

# # View_1: Client Project
# class CliPr(models.Model):

#     cp_id = models.IntegerField(db_column="ClientID", primary_key=True)
#     client_name = models.CharField(max_length=255, db_column="ClientName")
#     project_name = models.CharField(max_length=255, db_column="ProjectName")
#     seeker_id = models.IntegerField(db_column="SeekerID")
#     seeker_name = models.CharField(max_length=255, db_column="SeekerName")
#     seeker_email = models.EmailField(db_column="SeekerEmail")
#     provider_id = models.IntegerField(db_column="ProviderID")
#     provider_name = models.CharField(max_length=255, db_column="ProviderName")
#     provider_email = models.EmailField(db_column="ProviderEmail")
#     relationship = models.CharField(max_length=255, db_column="Relationship")
#     status = models.CharField(max_length=50, db_column="Status")


#     class Meta:
#         managed = False  # Prevent migrations for this model
#         db_table = 'client_project_view'

#     def __str__(self):
#         return f"{self.client_name} - {self.project_name} - {self.status}"
    
# View_1: Client_Project_copy:
class CliPr(models.Model):

    cp_id = models.IntegerField(db_column="ClientID", primary_key=True)
    client_name = models.CharField(max_length=255, db_column="ClientName")
    project_name = models.CharField(max_length=255, db_column="ProjectName")
    seeker_id = models.IntegerField(db_column="SeekerID")
    seeker_name = models.CharField(max_length=255, db_column="SeekerName")
    seeker_email = models.EmailField(db_column="SeekerEmail")
    provider_id = models.IntegerField(db_column="ProviderID")
    provider_name = models.CharField(max_length=255, db_column="ProviderName")
    provider_email = models.EmailField(db_column="ProviderEmail")
    relationship = models.CharField(max_length=255, db_column="Relationship")
    status = models.CharField(max_length=50, db_column="Status")


    class Meta:
        managed = False  # Prevent migrations for this model
        db_table = 'client_project_view_copy'

    def __str__(self):
        return f"{self.client_name} - {self.project_name} - {self.status}"

# Table_7: Provider URL View
class ProviderURL(models.Model):
    cp = models.ForeignKey(ClientProject, on_delete=models.CASCADE, db_column="ClientID")
    client_name = models.CharField(max_length=255, db_column="ClientName")
    project_name = models.CharField(max_length=255, db_column="ProjectName")
    provider_id = models.IntegerField( db_column="ProviderID")
    provider_name = models.CharField(max_length=255, db_column="ProviderName")
    provider_email = models.EmailField( db_column="ProviderEmail")
    provi_url = models.URLField(db_column="ProviderURL")  # Unique URL for the provider
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_column="UniqueID")  # Store unique ID for validation

    class Meta:
        
        db_table = 'provider_url'  # Ensure this points to a valid table in your database
        #unique_together = (('cp','unique_id'),)
    def __str__(self):
        return f"{self.provider_name} ({self.provider_email})"

# class ProviderURL(models.Model):
#     cp = models.ForeignKey('ClientProject', on_delete=models.CASCADE)
#     client_name = models.CharField(max_length=255)
#     project_name = models.CharField(max_length=255)
#     provider_id = models.IntegerField()
#     provider_name = models.CharField(max_length=255)
#     provider_email = models.EmailField()
#     provi_url = models.URLField()  # Unique URL for the provider
#     unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Store unique ID for validation

#     def __str__(self):
#         return f"{self.provider_name} ({self.provider_email})"

# Table_8: Superuser URL View
class SuperUserURL(models.Model):
    cp = models.ForeignKey(ClientProject, on_delete=models.CASCADE, db_column="ClientID")
    client_name = models.CharField(max_length=255, db_column="ClientName")
    project_name = models.CharField(max_length=255, db_column="ProjectName")
    superuser_name = models.CharField(max_length=255, db_column="SuperUserName")
    superuser_email = models.EmailField( db_column="SuperUserEmail")
    super_url = models.URLField( db_column="SuperUserURL")  # Unique URL for the superuser
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_column="UniqueID")  # Store unique ID for validation

    class Meta:
        
        db_table = 'superuser_url'  # Ensure this points to a valid table in your database
        #unique_together = (('cp','unique_id'),)
    def __str__(self):
        return f"{self.superuser_name} ({self.superuser_email})"

# class SuperUserURL(models.Model):
#     cp = models.ForeignKey('ClientProject', on_delete=models.CASCADE)
#     client_name = models.CharField(max_length=255)
#     project_name = models.CharField(max_length=255)
#     superuser_name = models.CharField(max_length=255)
#     superuser_email = models.EmailField()
#     super_url = models.URLField()  # Unique URL for the superuser
#     unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Store unique ID for validation

#     def __str__(self):
#         return f"{self.superuser_name} ({self.superuser_email})"


# View_2: Relationship View
class RelationshipView(models.Model):
    seeker_id = models.IntegerField(db_column='SeekerID', primary_key=True)  # Match the column name and type
    provider_id = models.IntegerField(db_column='ProviderID')  # Match the column name and type
    cp = models.IntegerField(db_column='ClientID')  # Match the column name and type
    relationship = models.CharField(max_length=50, db_column='Relationship')  # Match the column name and type

    class Meta:
        managed = False  # Django won't manage the view
        db_table = 'relationship_view_copy'  # Name of the database view
        unique_together = (('cp','seeker_id', 'provider_id'),)
    def __str__(self):
         return f"Relationship between {self.seeker_id} and {self.provider_id}: {self.relationship}"
    

# View_3: 
class UserDateView(models.Model):
    cp_id = models.IntegerField(primary_key=True, db_column='ClientID')
    client_name = models.CharField(max_length=255, db_column='ClientName')
    project_name = models.CharField(max_length=255, db_column='ProjectName')
    project_start_date = models.DateField(db_column='ProjectStartDate')
    project_end_date = models.DateField(db_column='ProjectEndDate')

    class Meta:
        managed = False  # This ensures that Django doesn't attempt to manage this view
        db_table = 'user_date_view'  # Name of the database view

# View_4: 
class UserSeekerView(models.Model):
    cp_id = models.IntegerField(db_column="ClientID", primary_key=True)  # Column: CP_Id
    provider_id = models.IntegerField(db_column="ProviderID")  # Column: ProviderID
    seeker_id = models.IntegerField(db_column="SeekerID")  # Column: SeekerID
    seeker_name = models.CharField(max_length=255, db_column="SeekerName")  # Column: SeekerName
    seeker_email = models.EmailField(db_column="SeekerEmail")  # Column: SeekerEmail
    relationship = models.CharField(max_length=255, db_column="Relationship")  # Column: Relationship
    status = models.CharField(max_length=50, db_column="Status")  # Column: Status
    user_id = models.IntegerField(db_column="UserID") 

    class Meta:
        managed = False  # Prevent migrations for this model
        db_table = "user_seeker_view_copy"  # Database view name

    def __str__(self):
        return f"{self.seeker_name} ({self.seeker_email})"

# View_5: 
class UserProviderView(models.Model):
    cp_id = models.IntegerField(db_column="ClientID", primary_key=True)  # Column: CP_Id
    provider_id = models.IntegerField(db_column="ProviderID")  # Column: ProviderID
    seeker_id = models.IntegerField(db_column="SeekerID")  # Column: SeekerID
    provider_name = models.CharField(max_length=255, db_column="ProviderName")  # Column: ProviderName
    provider_email = models.EmailField(db_column="ProviderEmail")  # Column: ProviderEmail
    relationship = models.CharField(max_length=255, db_column="Relationship")  # Column: Relationship
    status = models.CharField(max_length=50, db_column="Status")  # Column: Status
    # user_id = models.IntegerField(db_column="UserID")

    class Meta:
        managed = False  # Prevent migrations for this model
        db_table = "user_provider_view_copy"  # Database view name

    def __str__(self):
        return f"{self.provider_name} ({self.provider_email})"
    
# View_6: 
class UniqueSeekerProviderView(models.Model):
    cp_id = models.IntegerField(db_column="ClientID", primary_key=True)  # Column: CP_Id
    provider_id = models.IntegerField(db_column="ProviderID")  # Column: ProviderID
    seeker_id = models.IntegerField(db_column="SeekerID")  # Column: SeekerID
    relationship = models.CharField(max_length=255, db_column="Relationship")  # Column: Relationship

    class Meta:
        managed = False  # Prevent migrations for this model
        db_table = "unique_seeker_provider_view_copy"  # Database view name

    # def __str__(self):
    #     return f"{self.provider_name} ({self.provider_email})"
    
# View_7:
class OptimumMinimumCriteriaView(models.Model):
    cp_id = models.IntegerField(db_column="ClientID", primary_key=True)  # Column: CP_Id
    seeker_id = models.IntegerField(db_column="SeekerID")  # Column: SeekerID
    seeker_name = models.CharField(max_length=255, db_column="SeekerName")  # Column: SeekerName
    seeker_email = models.EmailField(db_column="SeekerEmail")  # Column: SeekerEmail
    optimum_criteria = models.CharField(max_length=255, db_column="Optimum_Criteria")  # Column: Optimum_Criteria
    minimum_criteria = models.CharField(max_length=255, db_column="Minimum_Criteria")  # Column: Minimum_Criteria

    class Meta:
        managed = False  # Prevent migrations for this model
        db_table = "optimum_minimum_criteria_view_copy"  # Database view name

    # def __str__(self):
    #     return f"{self.cp_id}, Seeker ID: {self.seeker_id}"
    

# View_8:
class FullRatingDataView(models.Model):
    cp_id = models.IntegerField(primary_key=True, db_column='ClientID')
    client_name = models.CharField(max_length=255, db_column='ClientName')
    project_name = models.CharField(max_length=255, db_column='ProjectName')
    seeker_name = models.CharField(max_length=255, db_column="SeekerName")  # Column: SeekerName 
    seeker_email = models.EmailField(db_column="SeekerEmail")  # Column: SeekerEmail
    provider_email = models.EmailField(db_column="ProviderEmail")  # Column: ProviderEmail
    relationship = models.CharField(max_length=255, db_column="Relationship")  # Column: Relationship
    question_text = models.TextField(db_column="QuestionText")  # Column: QuestionText
    competency = models.CharField(max_length=255, db_column="Competency")  # Column: Competency
    feedback_value = models.FloatField(db_column="FeedbackValue")  # Column: FeedbackValue

    class Meta:
        managed = False  # Prevent migrations for this model
        db_table = "full_rating_data_view_copy"  # Database view name

    def __str__(self):
        return f"{self.seeker_name} ({self.seeker_email}) "

# View_9:
class OpenQuestionView(models.Model):
    cp_id = models.IntegerField(primary_key=True, db_column='ClientID')
    client_name = models.CharField(max_length=255, db_column='ClientName')
    project_name = models.CharField(max_length=255, db_column='ProjectName')
    seeker_name = models.CharField(max_length=255, db_column="SeekerName")  # Column: SeekerName
    seeker_email = models.EmailField(db_column="SeekerEmail")  # Column: SeekerEmail
    provider_email = models.EmailField(db_column="ProviderEmail")  # Column: ProviderEmail
    relationship = models.CharField(max_length=255, db_column="Relationship")  # Column: Relationship
    question_text = models.TextField(db_column="QuestionText")  # Column: QuestionText
    feedback_text = models.TextField(db_column="FeedbackText")  # Column: FeedbackValue

    class Meta:
        managed = False  # Prevent migrations for this model
        db_table = "open_question_view_copy"  # Database view name

    def __str__(self):
        return f"{self.seeker_name} ({self.seeker_email})"
    

# Table_9: Feedback
class FeedbackUI(models.Model):
    # cp = models.ForeignKey(ClientProject, on_delete=models.CASCADE, db_column='ClientID')  # Field name made lowercase. The composite primary key (ClientID, SeekerID, ProviderID, QuestionID) found, that is not supported. The first column is selected.
    # seeker_id = models.ForeignKey('Seeker', on_delete=models.DO_NOTHING, db_column='SeekerID')  # Field name made lowercase.
    # provider_id = models.ForeignKey('Provider', on_delete=models.DO_NOTHING, db_column='ProviderID')  # Field name made lowercase.
    # question_id = models.ForeignKey('Question', on_delete=models.DO_NOTHING, db_column='QuestionID')
    cp = models.IntegerField(db_column='ClientID')  # Field name made lowercase. The composite primary key (ClientID, SeekerID, ProviderID, QuestionID) found, that is not supported. The first column is selected.
    seeker_id = models.IntegerField(db_column='SeekerID')  # Field name made lowercase.
    provider_id = models.IntegerField(db_column='ProviderID')  # Field name made lowercase.
    question_id = models.IntegerField(db_column='QuestionID')
    feedback_value = models.CharField(db_column='FeedbackValue',max_length=5, blank=True, null=True)  # Field name made lowercase.
    feedback_text = models.CharField(db_column='FeedbackText', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    feedback_status = models.CharField(db_column='FeedbackStatus', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'feedback_ui'
        # unique_together = (('cp', 'seeker_id', 'provider_id', 'question_id'),)

# View_10:
class AssessmentNumberView(models.Model):
    cp_id = models.IntegerField(primary_key=True, db_column='ClientID')
    client_name = models.CharField(max_length=255, db_column='ClientName')
    project_name = models.CharField(max_length=255, db_column='ProjectName')
    assessment_type = models.CharField(max_length=255, db_column='AssessmentType')

    class Meta:
        managed = False  # Since this is a database view
        db_table = 'assessment_number_view'  # Matches the name of the view in the database

    def __str__(self):
        return f"{self.client_name} - {self.project_name} ({self.assessment_type})"

# View_11:

class ProviderRelationshipView(models.Model):
    seeker_id = models.IntegerField(db_column='SeekerID', primary_key=True)  # Match the column name and type
    provider_id = models.IntegerField(db_column='ProviderID')  # Match the column name and type
    cp = models.IntegerField(db_column='ClientID')  # Match the column name and type
    relationship = models.CharField(max_length=50, db_column='Relationship')  # Match the column name and type

    class Meta:
        managed = False  # Django won't manage the view
        db_table = 'provider_relationship_view_copy'  # Name of the database view
        unique_together = (('cp','seeker_id', 'provider_id'),)
    def __str__(self):
         return f"Relationship between {self.seeker_id} and {self.provider_id}: {self.relationship}"
    
# # View_12:
# class OpenInProgressStatus(models.Model):
#     client_id = models.IntegerField(db_column='ClientID')
#     client_name = models.CharField(max_length=255, db_column='ClientName')
#     project_name = models.CharField(max_length=255, db_column='ProjectName')
#     seeker_id = models.IntegerField(db_column='SeekerID', primary_key=True)
#     seeker_name = models.CharField(max_length=255, db_column='SeekerName')
#     seeker_email = models.EmailField(db_column='SeekerEmail')
#     provider_id = models.IntegerField(db_column='ProviderID')
#     provider_name = models.CharField(max_length=255, db_column='ProviderName')
#     provider_email = models.EmailField(db_column='ProviderEmail')
#     relationship = models.CharField(max_length=255, db_column='Relationship')
#     status = models.CharField(max_length=50, db_column='Status')
#     seeker_url = models.URLField(db_column='SeekerUrl')
#     provider_url = models.URLField(db_column='ProviderUrl')

#     class Meta:
#         managed = False  # Django won't manage the view
#         db_table = 'open_inprogress_status_view'  # Name of the database view
#         #unique_together = (('ClientID', 'SeekerID', 'ProviderID'),)

    # def __str__(self):
    #     return f"{self.ProjectName} - {self.Status}"

# Table_10: Seeker URL
class SeekerURL(models.Model):
    cp = models.ForeignKey(ClientProject, on_delete=models.CASCADE, db_column="ClientID")
    client_name = models.CharField(max_length=255, db_column="ClientName")
    project_name = models.CharField(max_length=255, db_column="ProjectName")
    seeker_id = models.IntegerField( db_column="SeekerID")
    seeker_name = models.CharField(max_length=255, db_column="SeekerName")
    seeker_email = models.EmailField( db_column="SeekerEmail")
    seeker_url = models.URLField(db_column="SeekerURL")  # Unique URL for the provider
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_column="UniqueID")  # Store unique ID for validation

    class Meta:
        
        db_table = 'seeker_url'  # Ensure this points to a valid table in your database
        #unique_together = (('cp','unique_id'),)

    def __str__(self):
        return f"{self.seeker_name} ({self.seeker_email})"
    
# View_13:
class ProviderStatusView(models.Model):
    client_id = models.IntegerField(db_column='ClientID')
    client_name = models.CharField(max_length=255, db_column='ClientName')
    project_name = models.CharField(max_length=255, db_column='ProjectName')
    provider_id = models.IntegerField(db_column='ProviderID', primary_key=True)
    provider_name = models.CharField(max_length=255, db_column='ProviderName')
    provider_email = models.EmailField(db_column='ProviderEmail')
    status = models.CharField(max_length=50, db_column='Status')
    provider_url = models.URLField(db_column='ProviderUrl')

    class Meta:
        managed = False  # Django won't manage the view
        db_table = 'provider_status_view'  # Name of the database view
        # verbose_name = "Provider Status View"
        # verbose_name_plural = "Provider Status Views"
        # ordering = ["project_name"]

    def __str__(self):
        return f"{self.project_name} - {self.status}"
    
# View_14:
class SeekerStatusView(models.Model):
    client_id = models.IntegerField(db_column='ClientID')
    client_name = models.CharField(max_length=255, db_column='ClientName')
    project_name = models.CharField(max_length=255, db_column='ProjectName')
    provider_id = models.IntegerField(db_column='ProviderID', primary_key=True)
    provider_name = models.CharField(max_length=255, db_column='ProviderName')
    provider_email = models.EmailField(db_column='ProviderEmail')
    status = models.CharField(max_length=50, db_column='Status')
    seeker_url = models.URLField(db_column='SeekerUrl')

    class Meta:
        managed = False  # Django won't manage the view
        db_table = 'seeker_status_view'  # Name of the database view

    def __str__(self):
        return f"{self.project_name} - {self.status}"