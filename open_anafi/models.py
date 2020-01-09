from django.db import models
from mptt.models import MPTTModel
from django.contrib.auth.models import User
# Create your models here.

class Indicator(models.Model):
    """This Table represents an indicator, who can store multiple parameters based on years / budgets, and can be linked to multiple frames.

        :param name: The name of the indicator
        :type name: str
        
        :param description: The description of the indicator
        :type description: str
        
        :param max_depth: The maximum depth among all the parameters
        :type max_depth: int
        
        :param public: Indicates if the indicator is visible to other users
        :type public: bool

        :param last_modified_by: The user who last modified this indicator
        :type last_modified_by: class:`django.contrib.auth.models.User`

        :param frames: The frames the indicator is associated to
        :type frames: list, class:`open_anafi.models.Frame`, optional

        :param parameters: The parameters linked to this indicator
        :type parameters: list, class:`open_anafi.models.IndicatorParameter`, optional

        :param libelles: The list of libelles linked to an indicator:
        :type libelles: list, class:`open_anafi.models.IndicatorLibelle`, optional
    """
    name = models.CharField(max_length = 100, null = True, unique = True)
    description = models.TextField(null = True, blank = True)
    max_depth = models.IntegerField(null = True, blank = True)
    public = models.BooleanField(default=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="modified_indicators")
    # equation = models.OneToOneField(Node, on_delete = models.SET_NULL, null = True, related_name = "indicator_node")

class IndicatorLibelle(models.Model):
    """An indicator can have multiple aliases, for better understanding of its purpose

    :param libelle: The libelle
    :type libelle: str

    :param indicator: The indicator it describes
    :type indicator: class:`open_anafi.models.Indicator`
    """

    libelle = models.TextField(null=True, unique=False)
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, related_name="libelles")

class IndicatorParameter(models.Model):
    """An indicator parameter, containing a formula. It is linked to a single indicator.
    
        :param indicator: The indicator this parameter belongs to
        :type indicator: class:`open_anafi.model.Indicator`

        :param year_min: The minimum year for this parameter to apply
        :type year_min: int

        :param year_max: The maximum year for thisparameter to apply
        :type year_max: int

        :param readable_equation: The equation in a python readable way based on tuples
        :type readable_equation: tuple

        :param displaying: Stores parameters related to calculating this parameter. For example, absolute value
        :type displaying: str

        :param institution_type_number: The identifier of the institution this parameter is valid on
        :type institution_type_number: int

        :param institution_type_string: The label of the institution this parameter is valid on
        :type institution_type_string: str

        :param type_budget: Specifies the way we calculate the indicator
        :type type_budget: str

        :param original_equation: The original equation for this parameter, in a human readable way
        :type original_equation: str

        :param depth: How many indicators have to be calculated before this one can
        :type depth: int
    """
    indicator = models.ForeignKey(Indicator, null = True, related_name = 'parameters', on_delete = models.CASCADE)
    year_min = models.CharField(max_length = 100, null = True)
    year_max = models.CharField(max_length = 100, null = True)
    readable_equation = models.TextField(null = True)
    displaying = models.CharField(max_length = 100, null = True)
    institution_type_number = models.IntegerField(null = True)
    institution_type_string = models.CharField(max_length = 4, null = True)
    type_budget = models.CharField(max_length = 100, null = True)
    original_equation = models.TextField(null = True)
    depth = models.IntegerField(null = True)

class Nomenclature(models.Model):
    """A nomenclature, which is used to group frames together.

       :param name: The name of the nomenclature
       :type name: str

       :param description: The description of the nomenclature
       :type description: str, optional
    """

    name = models.CharField(max_length = 100, null = True)
    description = models.TextField(null = True, blank = True)

class IdentifierType(models.Model):
    """Stores the 3 different types of identifiers (SIRET, SIREN, FINESS)

       :param name: The name of the identifier type
       :type name: str
    """

    name = models.CharField(max_length = 100)

class InstitutionType(models.Model):
    """Represents a type of institution (Commune, EPHAD etc)

       :param name: The name of this institution type
       :type name: str

       :param number: The identifier used to represent this institution type (different from the primary key in the database)
       :type number: int

       :param legal_status: Number representing the legal status
       :type legal_status: int
    """
    name = models.CharField(max_length = 255, null = True)
    number = models.IntegerField()
    legal_status = models.IntegerField()

class Frame(models.Model):
    """A frame contains multiple indicators, as well as an output file, and is used to generate reports.

       :param name: The name of the frame
       :type name: str

       :param indicators: The indicators linked to the frame
       :type indicators: list, class:`open_anafi.models.Indicator`, optional

       :param identifiers_type: The types of identifiers that the frame can be calculated on
       :type identifiers_type: list, class:`open_anafi.models.IdentifierType`

       :param insitutions_type: The institutions the frame can be calculated on
       :type institutions_type: list, class:`open_anafi.models.InstitutionType`

       :param model_name: The name of the excel file the frame outputs to
       :type model_name: str

       :param description: The description of the frame
       :type description: str, optional

       :param max_depth: The maximum depth among all the indicators linked to the frame
       :type max_depth: int
    
       :param reports: The list of reports generated by this frame
       :type reports: list, class:`open_anafi.models.Reports`, optional
    """

    name = models.CharField(max_length = 100, null = True, unique = True)
    indicators = models.ManyToManyField(Indicator, blank = True, related_name = 'frames')
    nomenclature = models.ForeignKey(Nomenclature, null = True, on_delete = models.CASCADE, related_name = 'frames')
    identifiers_type = models.ManyToManyField(IdentifierType, blank = True, related_name = 'frames')
    institutions_type = models.ManyToManyField(InstitutionType, blank = True, related_name = 'frames')
    model_name = models.CharField(max_length = 100, null = True) 
    description = models.TextField(null = True, blank = True)
    max_depth = models.IntegerField(null = True, blank = True)

class Variable(models.Model):
    """A variable used inside of formulas. Represents a line of a compte

       :param name: The full name of the variable (a concatenation of all the information to calculate it)
       :type name: str

       :param indicator_parameter: The indicator parameter the variable is linked to
       :type indicator_parameter: class:`open_anafi.models.IndicatorParameter`

       :param numero_compte: The identifier of the compte to extract the values from
       :type numero_compte: str

       :param type_solde: The type of operation (debit, crédit)
       :type type_solde: str

       :param solde: The solde of the account, stored in as a string to ensure proper decimal values
       :type solde: str
    """

    name = models.CharField(max_length = 100, null = True)
    indicator_parameter = models.ForeignKey(IndicatorParameter, null = True, related_name = 'parent_indicator', on_delete = models.CASCADE)
    numero_compte = models.CharField(max_length = 100, null = True)
    type_solde = models.CharField(max_length = 100, null = True)
    solde = models.CharField(max_length = 100, null = True)

class Department(models.Model):
    """The list of all the french departments

       :param name: The department's name
       :type name: str

       :param number: The identifier of the department. Stored as a string because one of them contains a letter
       :type number: str
    
    """
    name = models.CharField(max_length = 100, null = True)
    number = models.CharField(max_length = 3, null = True)

class Report(models.Model):
    """All the reports generated

    :param frame: The frame used to generate the report
    :type frame: class:`open_anafi.models.Frame`

    :param frame_name : Name of the frame used (in case of the original frame is deleted)
    :type frame_name : str

    :param year_min: The lower bound of the range to calculate the report on
    :type year_min: int

    :param year_max: The upper bound of the range to calculate the report on
    :type year_max: int

    :param identifier: The identifier to generate the report on (can be a concat of multiple identifiers)
    :type identifier: str

    :param identifier_type: The type of the identifier 
    :type identifier_type: str

    :param state: Arbitrary string to indicate the state of the report. (En cours, Terminé, En échec)
    :type state: str

    :param name: The name of the produced excel file
    :type name: str

    :param date: The creation date of the report
    :type date: date

    :param user: The user who created the report
    :type user: class:`django.contrib.auth.models.User`

    """
    frame = models.ForeignKey(Frame, on_delete = models.SET_NULL, null = True, related_name = "reports")
    frame_name = models.CharField(max_length = 100, null = True)
    year_min = models.CharField(max_length = 100, null = True)
    year_max = models.CharField(max_length = 100, null = True)
    identifier = models.TextField(null=True)
    identifier_type = models.CharField(max_length = 100, null = True) 
    state = models.CharField(max_length = 100, null = True)
    name = models.CharField(max_length = 400, null = True)
    date = models.DateField(auto_now = True)
    user = models.ForeignKey(User, on_delete = models.SET_NULL, null = True, related_name = "reports")

class TranslationTableEstablishmentType(models.Model):
    type_budget = models.CharField(max_length = 100, null = True) # BP or BA
    letter = models.CharField(max_length = 1, null = True) # H, B, C, E, J, N, P, L, M A, G
    type_establishment = models.IntegerField() # 1, 2, 3, 4 
