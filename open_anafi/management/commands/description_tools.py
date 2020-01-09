from open_anafi.models import  Indicator, IndicatorLibelle
from django.db import transaction
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Transfers all the descriptions to libelles"
    def handle(self, *args, **options):
        indicators = Indicator.objects.all()

        with transaction.atomic():

            for indic in indicators:

                temp_desc = indic.description
                indicator_libelle = IndicatorLibelle.objects.filter(indicator=indic)
                if len(indicator_libelle)==1:

                    temp_lib = indicator_libelle[0].libelle
                    if temp_desc : indicator_libelle[0].libelle = temp_desc
                    else : indicator_libelle[0].libelle  = ''
                    indic.description = temp_lib
                    indicator_libelle[0].save()
                    indic.save()

                else :
                    for lib in indicator_libelle : lib.delete()
                    if temp_desc :

                        indicator_libelle = IndicatorLibelle.objects.create(libelle=temp_desc, indicator=indic)
                        indicator_libelle.save()
                    indic.description = None
                    indic.save()


