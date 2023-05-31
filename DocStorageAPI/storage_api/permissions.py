from rest_framework.permissions import BasePermission

class HasObjectPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        isOwner = obj.author == request.user
        hasRead = obj.node.filepermission_set.filter(user=request.user, is_active=True).exists()
        if request.method == 'GET':
            return hasRead
        else:
            return isOwner
        