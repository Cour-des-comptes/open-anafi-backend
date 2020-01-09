from codecs import open
from os.path import dirname, abspath

import django.db as db
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from open_anafi.models import Frame, Report
from open_anafi.serializers import ReportSerializer, ReportModelSerializer, AggregatedReportSerializer
from open_anafi.tasks import compute_frame, compute_balance


class ReportViews(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        report_serialized = ReportSerializer(data=request.data)

        if not report_serialized.is_valid():
            # If the report_serialized is badly formed
            return Response(report_serialized.errors, status=400)
        data = report_serialized.data
        report = Report.objects.create(state="PENDING")
        report.year_min = data['financial_year_min']
        report.year_max = data['financial_year_max']
        report.identifier = data['identifiers']
        report.identifier_type = data['identifiers_type']
        report.frame = Frame.objects.get(id=data['frame'])
        report.frame_name = Frame.objects.get(id=data['frame']).name
        report.user = request.user
        report.save()
        compute_frame.delay(data['frame'], data['financial_year_min'], data['financial_year_max'], data['identifiers'],
                            data['identifiers_type'],request.data['nomenclature'],request.data['institutions'], report.id)

        return Response({'report_id': report.id}, status=201)

    def get(self, request):
        try:
            reports = Report.objects.all()
            reports = reports.filter(user__username=request.user.username)
            reports_json = ReportModelSerializer(reports, many=True).data
            return Response(reports_json, status=200)
        except Exception as e:
            return Response({'error': str(e)}, status=400)



class ReportGetViews(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            report = Report.objects.get(id=pk)
            report_json = ReportModelSerializer(report)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        if report.state == "PENDING":
            return Response(report_json.data, status=200)
        elif report.state == "FAILED":
            return Response(report_json.data, status=200)
        elif report.state == "DONE":
            return Response(report_json.data, status=200)
        else:
            return Response(status=400)


class BalanceViews(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        balance_serialized = ReportSerializer(data=request.data)

        if not balance_serialized.is_valid():
            # If the report_serialized is badly formed
            return Response(balance_serialized.errors, status=400)

        data = balance_serialized.data
        report = Report.objects.create(state="PENDING")
        report.year_min = data['financial_year_min']
        report.year_max = data['financial_year_max']
        report.identifier = data['identifiers']
        report.identifier_type = data['identifiers_type']
        report.user = request.user
        report.save()

        compute_balance.delay(data['financial_year_min'], data['financial_year_max'], data['identifiers'],
                              data['identifiers_type'], report.id)

        return Response({'report_id': report.id}, status=201)


class ReportDownloadViews(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            report = Report.objects.get(id=pk)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
        if report.state == "DONE":
            ## We upload the file to the client
            file_path = '{}/reports/{}'.format(dirname(dirname(dirname(abspath(__file__)))), report.name)
            with open(file_path, "rb") as FilePointer:
                data = FilePointer.read()
            response = HttpResponse(data,
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename={}'.format(report.name)

            return response
        else:
            return Response(status=400)


class AggregatedReportViews(APIView):
    permission_classes = (IsAuthenticated,)

    # TODO centralize sql request
    SQL_REQUEST = '''
        SELECT C.ident as ident, C.exer as exer
        FROM collectivite AS C 
        WHERE
         C.ndept IN {ndept} 
         AND 
         C.ctype IN {ctype}
         and
         C.exer IN {exer}
         AND
         C.cnome = \'{nomen}\'
    '''

    def _get_identifiers(self, institutions, departments, exer, nomen, pop_min=None, pop_max=None):
        departments_string = f"{departments}".replace('[', '(').replace(']', ')')

        institutions_string = f"{institutions}".replace('[', '(').replace(']', ')')

        exer_string = f"{exer}".replace('[', '(').replace(']', ')')

        sql_query = self.SQL_REQUEST.format(ndept=departments_string,
                                            ctype=institutions_string,
                                            exer=exer_string,
                                            nomen=nomen)

        if pop_min:
            sql_query += f' AND C.mpoid::int4 >= {pop_min}'
        if pop_max:
            sql_query += f' AND C.mpoid::int4 <= {pop_max}'



        with db.connections['cci'].cursor() as cursor:
            cursor.execute(sql_query)
            columns = [col[0] for col in cursor.description]
            identifiers = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return identifiers

    def post(self, request):
        report_serialized = AggregatedReportSerializer(data=request.data)

        if not report_serialized.is_valid():
            # If the report_serialized is badly formed
            return Response(report_serialized.errors, status=400)
        data = report_serialized.validated_data

        identifiers = self._get_identifiers([str(inst.number) for inst in data['institutions']],
                                            [dept.number for dept in data['departments']],
                                            list(range(data['financial_year_min'], data['financial_year_max'] + 1)),
                                            data['frame'].nomenclature.name   ,
                                            pop_min=data.get('pop_min', None),
                                            pop_max=data.get('pop_max', None))

        if len(identifiers) == 0:
            raise Exception("Il n'y a pas de SIRET pour les critères donnés")

        report = Report.objects.create(state="PENDING")
        report.year_min = data['financial_year_min']
        report.year_max = data['financial_year_max']
        report.identifier = str(identifiers)
        report.identifier_type = 'SIRET'
        report.frame = data['frame']
        report.user = request.user
        report.save()

        compute_frame.delay(data['frame'].id,
                            data['financial_year_min'],
                            data['financial_year_max'],
                            identifiers,
                            'SIRET',
                            data['nomenclature'],
                            data['institutions'],
                            report.id,
                            aggregate=True)

        return Response({'report_id': report.id}, status=201)