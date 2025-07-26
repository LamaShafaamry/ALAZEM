from rest_framework import serializers
from .models import Activities, Services, Media


class ServiceSerializer(serializers.ModelSerializer):
    media = serializers.SerializerMethodField()
    class Meta:
        model = Services
        fields = [
           'title',
           'description',
           'id',
           'creation_date',
           'media'
        ]
    def get_media(self, obj):
        service_media = obj.service_media.all()
        return MediaSerializer(service_media, many=True , context = {'request': self.context.get('request')}).data

class MediaSerializer(serializers.ModelSerializer):
    file_path = serializers.SerializerMethodField()
    class Meta:
        model = Media
        fields = [
            'id',
            'file_path',
        ]

    def get_file_path(self, obj):
            request = self.context.get('request')
            print(request)
            host = request.build_absolute_uri('/') if request else ''
            return f"{host}static/images/{obj.file_path}"

class ActivitieSerializer(serializers.ModelSerializer):
    media = serializers.SerializerMethodField()
    class Meta:
        model = Activities
        fields = [
           'title',
           'description',
           'id',
           'creation_date',
           'media'
        ]
    def get_media(self, obj):
        activity_media = obj.activity_media.all()
        return MediaSerializer(activity_media, many=True , context = {'request': self.context.get('request')}).data
