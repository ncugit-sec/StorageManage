from rest_framework import serializers
from manage_api.models import User, FileNode, FileType, FileVersion, FilePermission
from manage_api.permissions import get_permission_filter
from django.db.models import Max
from django.core.exceptions import ValidationError
from django.core.exceptions import PermissionDenied

class NodePreviewSerializer(serializers.ModelSerializer):
    version_details = serializers.SerializerMethodField()
    class Meta:
        model = FileNode
        fields = ['id', 'type', 'is_public', 'created_at', 'version_details']
    
    def get_version_details(self, obj):
        max_version = FileVersion.objects.filter(node_id=obj.id).order_by('-id').first()
        return {
            'id': getattr(max_version, 'id', None),
            'name': getattr(max_version, 'name', None),
            'is_uploaded': getattr(max_version, 'is_uploaded', 0),
        }

class PermissionSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        many=False,
        queryset=User.objects.all(),
        slug_field='username'
    )
    class Meta:
        model = FilePermission
        fields = ['id', 'user', 'can_write', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']

class PermissionCreateSerializer(PermissionSerializer):
    class Meta(PermissionSerializer.Meta):
        fields = [*PermissionSerializer.Meta.fields, 'node']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        node = validated_data['node']
        permission = FilePermission.objects.create(
            node=node,
            user=validated_data['user'],
            can_write=validated_data['can_write'],
            is_active=1,
        )
        return permission

class NodeSerializer(NodePreviewSerializer):
    name = serializers.CharField(max_length=256, write_only=True)
    owner = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username'
    )
    childs = NodePreviewSerializer(many=True, read_only=True)
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = FileNode
        fields = ['id', 'name', 'owner', 'type', 'is_public', 'created_at', 'parent', 'version_details', 'childs', 'permissions']
        read_only_fields = ['type', 'created_at', 'version_details']

    def create(self, validated_data):
        parent = validated_data['parent']
        node = FileNode.objects.create(
            owner=self._user(),
            type=validated_data['type'],
            is_public=validated_data['is_public'],
            parent=parent,
        )
        node = self.update(node, validated_data)
        permission = FilePermission.objects.create(
            node=node,
            user=self._user(),
            can_write=1,
            is_active=1,
        )
        if parent is not None:
            parent_permission = parent.filepermission_set.filter(is_active=True)
            for p in parent_permission:
                if p.user != self._user():
                    FilePermission.objects.create(
                        node=node,
                        user=p.user,
                        can_write=p.can_write,
                        is_active=1,
                    )
        return node

    def update(self, instance, validated_data):
        should_upload = instance.type.should_upload
        version = FileVersion.objects.create(
            node=instance,
            name=validated_data['name'],
            is_uploaded=not should_upload,
            author=self._user(),
        )
        return instance

    def _user(self):
        request = self.context.get('request', None)
        if request:
            return request.user


class NodeCreateSerializer(NodeSerializer):
    class Meta(NodeSerializer.Meta):
        read_only_fields = ['created_at', 'version_details']


class VersionSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username'
    )
    class Meta:
        model = FileVersion
        fields = ['id', 'name', 'author', 'is_uploaded', 'created_at']

