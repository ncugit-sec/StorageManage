from storage_api.models import FileVersion
from storage_api.serializers import FileSerializer, FileInnerSerializer, pkToPath
from storage_api.permissions import HasObjectPermission
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import viewsets, status
from django.http import HttpResponse, QueryDict
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import os

id_param = openapi.Parameter("id", openapi.IN_PATH, description="A unique integer value identifying the file to download.", type=openapi.TYPE_STRING)
id_upload_param = openapi.Parameter("id", openapi.IN_PATH, description="A unique integer value identifying the file to upload.", type=openapi.TYPE_STRING)

class FileViewSet(viewsets.ViewSet):
    serializer_class = FileSerializer
    permission_classes = (IsAuthenticated, HasObjectPermission)
    parser_classes = (MultiPartParser,)
    
    @swagger_auto_schema(
        manual_parameters=[id_param],
        responses={200: openapi.Response('File Attachment', schema=openapi.Schema(type=openapi.TYPE_FILE)),
                   400: openapi.Response('Not a file'),
                   404: openapi.Response('File is not ready'),
        })
    def retrieve(self, request, pk=None):
        version = self._get_version(pk)
        self.check_object_permissions(request, version)
        if version.is_uploaded == 0:
            return Response({'details': 'File is not ready'}, status=status.HTTP_404_NOT_FOUND)
        if not version.node.type.should_upload:
            return Response({'details': 'Not a file'}, status=status.HTTP_400_BAD_REQUEST)
        
        location = pkToPath(pk)
        if not os.path.exists(location):
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
        with open(location, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = 'inline; filename=test.txt'
            return response
    
    @swagger_auto_schema(
        manual_parameters=[id_upload_param,
                           openapi.Parameter(
                            name="file",
                            in_=openapi.IN_FORM,
                            type=openapi.TYPE_FILE,
                            required=True,
                            description="Document"
                           )],
        responses={200: openapi.Response('File uploaded'),
                   409: openapi.Response('File already uploaded'),
        })
    def update(self, request, pk=None):
        version = self._get_version(pk)
        self.check_object_permissions(request, version)
        if version.is_uploaded == 1:
            return Response(status=status.HTTP_409_CONFLICT)
        
        query_dict = QueryDict('', mutable=True)
        query_dict.update({**request.data.dict(), 'version': pk})
        serializer = FileInnerSerializer(data=query_dict)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response( status=status.HTTP_200_OK)

    def _get_version(self, pk=None):
        versionQuery = FileVersion.objects.filter(pk=pk, node__is_deleted=False)
        version = get_object_or_404(versionQuery)
        return version