from rest_framework.permissions import BasePermission
from manage_api.models import FileNode

def get_permission_filter(user):
    return {'filepermission__user':user, 'filepermission__is_active':True}

class HasObjectPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        hasRead = obj.filepermission_set.filter(user=request.user, is_active=True).exists()
        hasWrite = obj.filepermission_set.filter(user=request.user, is_active=True, can_write=True).exists()
        
        if request.method == 'GET':
            return hasRead
        else:
            return hasWrite


class HasObjectChangePermission(HasObjectPermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            node_id = request.data.get('node')
            try:
                node = FileNode.objects.get(id=node_id)
                return super().has_object_permission(request, view, node)
            except:
                pass
        return True
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj.node)
        