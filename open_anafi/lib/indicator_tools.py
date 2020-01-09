from open_anafi.models import Indicator, IndicatorParameter, IndicatorLibelle
from open_anafi.serializers import IndicatorSerializer
from .frame_tools import FrameTools
from open_anafi.lib import parsing_tools
from open_anafi.lib.ply.parsing_classes import Indic
import re
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

class IndicatorTools:
    @staticmethod
    def calculate_max_depth(indicator):
        """Calculates the depth of an indicator (the max depth of all its parameters)
        
        :param indicator: The indicator to evaluate
        :type indicator: class:`open_anafi.models.Indicator`
        """
        depth = 0
        for parameter in indicator.parameters.all():
            if parameter.depth > depth:
                depth = parameter.depth

        indicator.max_depth = depth
        indicator.save()

    @staticmethod
    def update_depth(indicator):
        """Updates the depth of an indicator after an update.
           Recursively updates all the affected indicators/frames

        :param indicator: The indicator to evaluate
        :type indicator: class:`open_anafi.models.Indicator`
        """
        parameters = IndicatorParameter.objects.filter(original_equation__contains=indicator.name)
        indicators_to_update = list(set([param.indicator for param in parameters]))
        frames_to_update = list(indicator.frames.all()) 

        if len(indicators_to_update) > 0:
            for indic in indicators_to_update:
                for frame in indic.frames.all(): frames_to_update.append(frame)

                # For each indicator, we update the depth of all the parameters, then we calculate the max depth of the indicator
                for param in indic.parameters.all(): IndicatorParameterTools.calculate_depth(param)
                IndicatorTools.calculate_max_depth(indic)

            for indic in indicators_to_update: IndicatorTools.update_depth(indic)

        # We update the depth of the frames 
        frames_to_update = list(set(frames_to_update))

        if len(frames_to_update) > 0:
            for frame in frames_to_update: FrameTools.calculate_depth(frame)

    #This method can be optimized
    @staticmethod
    def update_indicator(equation, description, id, libelle=None):
        """Update an indicator.

           Note that we cannot modify the indicator's name.

           :param equation: The updated equation (updated or not)
           :type equation: str

           :param description: The updated description
           :type description: str

           :param id: The indicator's id
           :type id: int

           :param libelle: An extra libelle for the indicator
           :type libelle: str

           :return: The updated indicator
           :rtype: class:`open_anafi.models.Indicator` 
        """
        indic = Indicator.objects.get(id=id)
        if libelle is not None:
            indicator_libelle = IndicatorLibelle.objects.filter(indicator=indic)
            if len(indicator_libelle) > 1:
                raise Exception('Cet indicateur possède plusieurs libellés')
            elif len(indicator_libelle) == 0:
                indicator_libelle = IndicatorLibelle.objects.create(libelle=libelle, indicator=indic)
                indicator_libelle.save()
            else:
                indicator_libelle = indicator_libelle[0]
                indicator_libelle.libelle = libelle
                indicator_libelle.save()

        if description is not None :
            with transaction.atomic():
                indic.description = description
                indic.save()

        if equation is not None:
            #
            with transaction.atomic():
                backup_indicator = IndicatorSerializer(indic).data
                old_params = IndicatorParameter.objects.filter(indicator=indic)
                old_params_ids = [ p.id for p in old_params].copy()

                if len(backup_indicator.get('libelles')) > 1:
                    raise Exception('Cet indicateur possède plusieurs libellés')

                parsing_tools.update_formula(equation, indic)

                for parameter in IndicatorParameter.objects.filter(id__in=old_params_ids):
                    parameter.delete()

                indic = Indicator.objects.get(name=backup_indicator.get('name'))

                indic.save()
                IndicatorTools.update_depth(indic)

        return indic.name

    @staticmethod
    def check_equation_element(element):
        if type(element) is Indic:
            try:
                Indicator.objects.get(name=element.name)
            except ObjectDoesNotExist:
                raise Exception(f"L'indicateur {element.name} n'existe pas.")

    @staticmethod
    def check_equation(equation):
        try:
            parsed_indicator = parsing_tools.parse_equation(equation)

            for eq in parsed_indicator:
                if type(eq['tree']) is tuple:
                    for element in eq['tree']:
                        IndicatorTools.check_equation_element(element)
                else:
                    IndicatorTools.check_equation_element(eq['tree'])
        except Exception as e:
            raise Exception(f"Erreur dans la formule : {str(e)}")

    @staticmethod
    def check_indicator_usages_in_formulas(indicator):
        """
        Checks if an indicator is part of a formula of any other indicator.
        Used to check if an indicator is safe to remove.

        :param indicator: The indicator to check
        :type indicator: :class:`open_anafi.models.Indicator`
        """
        result = [indicator_parameter.indicator.name for indicator_parameter in
                  IndicatorParameter.objects.filter(original_equation__icontains=indicator.name)]
        return result



class IndicatorParameterTools:
    @staticmethod
    def calculate_depth(indicator_parameter):
        """Calculates the depth of an indicator parameter,
           given that all the indicators present in its equation already exist and have the correct depth.

           :param indicator_parameter: The indicator parameter to evaluate
           :type indicator_parameter: class:`open_anafi.models.IndicatorParameter`
        """
        depth = 0
        indicators = IndicatorParameterTools.extract_indicators_from_equation(indicator_parameter.original_equation)

        if len(indicators) == 0:
            indicator_parameter.depth = 1
            indicator_parameter.save()

        for indicator in indicators:
            if indicator.max_depth > depth:
                depth = indicator.max_depth

        indicator_parameter.depth = depth + 1
        indicator_parameter.save()


    @staticmethod
    def extract_indicators_from_equation(equation):
        """Retrieves all the indicator objects contained in a equation

        :param equation: An equation according to the defined language
        :type equation: str

        :return: The list of all the indicator objects present in the equation
        :rtype: list of class:`open_anafi.models.Indicator`
        """ 
        exp = re.compile('[\-+/*^(\[)\]]')
        is_indicator = re.compile('[A-Z0-9]+(_[A-Z0-9]+)+')
        split_equation = list(filter(None, map(str.strip, exp.split(equation))))
        indicators = []

        for item in split_equation:
            if not is_indicator.match(item) : continue
            try:
                indic = Indicator.objects.get(name = item)
                indicators.append(indic)
            except ObjectDoesNotExist:
                raise Exception(f"L'indicateur {item} n'existe pas.")

        return indicators

