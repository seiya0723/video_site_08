from rest_framework import serializers

from .models import Video,VideoComment,MyList,History,GoodVideo,BadVideo

class VideoSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Video
        fields =["title","description","category","movie","thumbnail","user",]

class VideoCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model  = VideoComment
        fields = ["content","target","user",]

class MyListSerializer(serializers.ModelSerializer):

    class Meta:
        model   = MyList
        fields  = ["target","user",]

class HistorySerializer(serializers.ModelSerializer):

    class Meta:
        model   = History
        fields  = ["target","user",]

class RateSerializer(serializers.Serializer):

    flag    = serializers.BooleanField()

class GoodSerializer(serializers.ModelSerializer):

    class Meta:
        model   = GoodVideo
        fields  = [ "target","user",]

class BadSerializer(serializers.ModelSerializer):

    class Meta:
        model   = BadVideo
        fields  = [ "target","user",]
