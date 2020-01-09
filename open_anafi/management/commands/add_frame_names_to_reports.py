from django.core.management.base import BaseCommand
from open_anafi.models import  Report
from django.db import transaction


class Command(BaseCommand):
    help = "Transfers all the descriptions to libelles"
    def handle(self, *args, **options):
        reports = Report.objects.all()

        with transaction.atomic():

            for report in reports:
                if report.frame : report.frame_name = report.frame.name
                report.save()
