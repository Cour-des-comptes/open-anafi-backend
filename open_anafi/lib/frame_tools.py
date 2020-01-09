from django.core.exceptions import ObjectDoesNotExist

from open_anafi.models import Frame, Indicator, InstitutionType, IdentifierType, Nomenclature
from open_anafi.serializers import FrameSerializer


class FrameTools:
    @staticmethod
    def get_or_create_frame(frame_name, model_name, frame_description, nomenclature, institution_types,
                            identifier_types):
        """
        Retrieves or create an open_anafi frame.

        :param frame_name: The name of the frame
        :type frame_name: str

        :param model_name: The name of the excel file the frame outputs to
        :type model_name: str

        :param frame_description: The description of the frame
        :type frame_description: str

        :param nomenclature: The id of the nomenclature to attach the frame to
        :type nomenclature: optional int

        :param institution_types: The institutions the frame can be calculated on
        :type institution_types: list of int

        :param identifier_types: The types of identifiers that the frame can be calculated on
        :type identifier_types: list of int

        :return: The retrieved or created Frame
        :rtype: class:`open_anafi.models.Frame`
        """
        try:
            frame = Frame.objects.get(name=frame_name)
            frame.model_name = model_name  # TODO Check if this is useful

        except ObjectDoesNotExist:
            frame_ser = FrameSerializer(
                data={"name": frame_name, "description": frame_description, 'model_name': model_name})
            frame_ser.is_valid(raise_exception=True)
            frame_ser.save()
            frame = Frame.objects.get(name=frame_name)
            for institution_type in institution_types:
                frame.institutions_type.add(InstitutionType.objects.get(number=int(institution_type)))
            for identifier_type in identifier_types:
                frame.identifiers_type.add(IdentifierType.objects.get(name=identifier_type))

        if nomenclature is not '':
                frame.nomenclature = Nomenclature.objects.get(id=nomenclature)
                frame.save()

        return frame

    @staticmethod
    def calculate_depth(frame):
        """Evaluate the depth of a frame (the maximum depth among all its children)

        :param frame: The frame to evaluate
        :type frame: class:`open_anafi.models.Frame`
        """
        depth = 0
        for indicator in frame.indicators.all():
            if indicator.max_depth > depth:
                depth = indicator.max_depth

        frame.max_depth = depth
        frame.save()

    @staticmethod
    def add_indicator_to_frame(frame_id, indicators):
        try:
            frame = Frame.objects.get(id=frame_id)
        except ObjectDoesNotExist:
            raise Exception("Error while retrieving frame.")

        for indicator in indicators:
            try:
                indic = Indicator.objects.get(id=indicator)
            except ObjectDoesNotExist:
                raise Exception("Error while retrieving indicator of id {}.".format(indicator))
                
            indic.frames.add(frame.id)
            frame.indicators.add(indic)
            indic.save()
        frame.save()

    @staticmethod
    def remove_indicator_from_frame(frame_id, indicators):
        try:
            frame = Frame.objects.get(id=frame_id)
        except ObjectDoesNotExist:
            raise Exception("Error while retrieving frame.")

        for indicator in indicators:
            try:
                indic = Indicator.objects.get(id=indicator)
            except ObjectDoesNotExist:
                raise Exception("Error while retrieving indicator of id {}.".format(indicator))
                
            indic.frames.remove(frame.id)
            frame.indicators.remove(indic)
            indic.save()
        frame.save()