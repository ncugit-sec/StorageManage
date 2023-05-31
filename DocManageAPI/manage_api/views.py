from manage_api.models import FileNode, FileVersion, FilePermission
from manage_api.serializers import NodeSerializer, NodeCreateSerializer, VersionSerializer, PermissionSerializer, PermissionCreateSerializer
from manage_api.functions import get_object_or_403
from manage_api.permissions import HasObjectPermission, HasObjectChangePermission, get_permission_filter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, status, mixins
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class FileNodeViewSet(viewsets.ModelViewSet):
    queryset = FileNode.objects.filter(is_deleted=False)
    serializer_class = NodeSerializer
    permission_classes = (IsAuthenticated, HasObjectPermission)

    def list(self, request):
        queryset = self.get_queryset()
        queryset = queryset.filter(**get_permission_filter(request.user), parent=None)
        serializer = NodeSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        parent_id = request.data['parent']
        if parent_id is not None and (isinstance(parent_id, int) or (isinstance(parent_id, str) and parent_id.isdigit())):
            queryset = self.get_queryset()
            parent = queryset.get(id=request.data['parent'])
            self.check_object_permissions(self.request, parent)
        return super().create(request)
        
    def get_serializer_class(self): 
        serializer_class = self.serializer_class 
        if self.request.method == 'POST': 
            serializer_class = NodeCreateSerializer 
        return serializer_class

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.prefetch_related(
                Prefetch(
                'filenode_set',
                queryset=FileNode.objects.filter(**get_permission_filter(self.request.user)),
                to_attr="childs"
            ),
                Prefetch(
                'filepermission_set',
                queryset=FilePermission.objects.filter(is_active=True),
                to_attr="permissions"
            )
        )
        return queryset
        

class FileVersionViewSet(mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    queryset = FileVersion.objects.filter()
    serializer_class = VersionSerializer
    permission_classes = (IsAuthenticated, HasObjectPermission)

    @swagger_auto_schema(
        responses={200: VersionSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH,
                description="A unique integer value identifying the file node for querying versions.",
                type=openapi.TYPE_INTEGER,
                required=True)
        ]
    )
    def retrieve(self, request, pk=None):
        nodeQueryset = FileNode.objects.filter(is_deleted=False)
        obj = get_object_or_404(nodeQueryset, pk=pk)
        self.check_object_permissions(request, obj)

        queryset = self.get_queryset()
        queryset = queryset.filter(node_id=pk)
        queryset = queryset.order_by('-id')
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

class PermissionViewSet(mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    queryset = FilePermission.objects.filter(is_active=True)
    serializer_class = PermissionSerializer
    permission_classes = (IsAuthenticated, HasObjectChangePermission)
    
    def get_serializer_class(self): 
        serializer_class = self.serializer_class 
        if self.request.method == 'POST': 
            serializer_class = PermissionCreateSerializer
        return serializer_class

