from rest_framework import viewsets

from comment.models import Comment, FrameComment, IndicatorComment
from comment.serializers import CommentSerializer, IndicatorCommentSerializer, FrameCommentSerializer


# Create your views here.
class CommentsView(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class FrameCommentsView(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = FrameCommentSerializer

    def get_queryset(self):

        frame_id = self.request.query_params.get('frame', None)

        if frame_id is not None:
            return_val =  FrameComment.objects.all().filter(frame = frame_id)
        else:
            return_val =  FrameComment.objects.all()
        return return_val


class IndicatorCommentsView(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = IndicatorCommentSerializer

    def get_queryset(self):

        indicator_id = self.request.query_params.get('indicator', None)

        if indicator_id is not None:
            return_val = IndicatorComment.objects.all().filter(indicator = indicator_id)
        else:
            return_val = IndicatorComment.objects.all()
        return return_val
