import io
import zipfile
from os.path import dirname, abspath

from django.http import HttpResponse
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from open_anafi.lib.excelwriter_tools import ExcelWriterTools
from open_anafi.models import Frame


def write_to_excel():
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)

    # Here we will adding the code to add data

    workbook.close()
    xlsx_data = output.getvalue()
    # xlsx_data contains the Excel file
    return xlsx_data


class FrameDownloadViews(APIView):
    @permission_classes((IsAuthenticated,))
    def get(self ,request ,pk):
        frame_id = pk
        frame = Frame.objects.get(id=frame_id)
        model_filename = frame.model_name
        pseudo_filename = frame.name+ '_recreated_pseudo.xlsx'
        model_w_formulas_filename = frame.name+ '_Model_+_Formulas.xlsx'
        indicators = frame.indicators
        model_file_path = '{}/templates/{}'.format(dirname(dirname(abspath(__file__))), model_filename)
        wb, wb2 = ExcelWriterTools.write_pseudo(indicators, model_file_path)
        s1 = io.BytesIO()
        s2 =  io.BytesIO()
        wb.save(s1)
        wb2.save(s2)
        s = io.BytesIO()
        zip_file = zipfile.ZipFile(s, 'w')
        zip_file.write( model_file_path,model_filename)
        zip_file.writestr( pseudo_filename , s1.getvalue())
        zip_file.writestr( model_w_formulas_filename , s2.getvalue())
        zip_file.close()
        #os.remove(pseudo_file_path)
        #os.remove(model_w_formulas_file_path)
        zip_filename = 'export.zip'
        response = HttpResponse(s.getvalue(),content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=%s'%zip_filename
        return response



class FrameDownloadLightViews(APIView):
    @permission_classes((IsAuthenticated,))
    def get(self ,request ,pk):
        frame_id = pk
        frame = Frame.objects.get(id=frame_id)
        model_filename = frame.model_name
        model_w_formulas_filename = frame.name+ '_Model_+_Formulas.xlsx'
        indicators = frame.indicators
        model_file_path = '{}/templates/{}'.format(dirname(dirname(abspath(__file__))), model_filename)
        wb, wb2 = ExcelWriterTools.write_pseudo(indicators, model_file_path)
        s2 =  io.BytesIO()
        wb2.save(s2)
        s = io.BytesIO()
        zip_file = zipfile.ZipFile(s, 'w')
        #zip_file.write( model_file_path,model_filename)
        zip_file.writestr( model_w_formulas_filename , s2.getvalue())
        zip_file.close()
        #os.remove(pseudo_file_path)
        #os.remove(model_w_formulas_file_path)
        zip_filename = 'export.zip'
        response = HttpResponse(s.getvalue(),content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=%s'%zip_filename
        return response



