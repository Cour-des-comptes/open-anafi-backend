from rest_framework.response import Response
from rest_framework.views import APIView

from open_anafi.lib.frame_tools import FrameTools


class IndicatorFrameView(APIView):
    def post(self, request, pk):
        operation = request.data.get('operation', 'add')
        indicators = request.data.get('formValues').get('indicators', [])

        if operation == 'add':
            FrameTools.add_indicator_to_frame(pk, indicators)
        elif operation == 'delete':
            FrameTools.remove_indicator_from_frame(pk, indicators)

        return Response(status=201)