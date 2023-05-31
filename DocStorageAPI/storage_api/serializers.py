from rest_framework import serializers
from storage_api.models import FileVersion

def pkToPath(pk):
    return f"/files/{pk}"

class FileSerializer(serializers.Serializer):
    file = serializers.FileField()

class FileInnerSerializer(FileSerializer):
    version = serializers.PrimaryKeyRelatedField(queryset=FileVersion.objects.all())

    def create(self, validated_data):
        f = validated_data['file']
        version = validated_data['version']
        location = pkToPath(version.id)
        with open(location, 'wb') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        version.is_uploaded = 1
        version.save()

        return validated_data