from rest_framework import serializers
from comment.models import Comment, FrameComment, IndicatorComment
from open_anafi.models import Frame, Indicator

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('username', 'comment', 'date')

class FrameCommentSerializer(serializers.ModelSerializer):
    frame = serializers.PrimaryKeyRelatedField(queryset = Frame.objects.all(), allow_null = False, required = True)

    class Meta:
        model = FrameComment
        fields = ('username', 'comment', 'date', 'frame')

class IndicatorCommentSerializer(serializers.ModelSerializer):
    indicator = serializers.PrimaryKeyRelatedField(queryset = Indicator.objects.all(), allow_null = False, required = True)

    class Meta:
        model = IndicatorComment
        fields = ('username', 'comment', 'date', 'indicator')

