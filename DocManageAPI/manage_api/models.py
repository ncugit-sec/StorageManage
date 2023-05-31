from django.db import models
from django.contrib.auth.models import AbstractUser

class FileNode(models.Model):
    parent = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    owner = models.ForeignKey('User', models.DO_NOTHING)
    type = models.ForeignKey('FileType', models.DO_NOTHING)
    is_public = models.IntegerField()
    is_deleted = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        managed = False
        db_table = 'file_node'

    def delete(self):
        self.is_deleted = True
        for child in self.filenode_set.all():
            child.delete()
        self.save()

class FileType(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    should_upload = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = 'file_type'


class FileVersion(models.Model):
    node = models.ForeignKey(FileNode, models.DO_NOTHING)
    name = models.CharField(max_length=256)
    author = models.ForeignKey('User', models.DO_NOTHING)
    is_uploaded = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        managed = False
        db_table = 'file_version'


class User(AbstractUser):
    department = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'user'
    
    class Meta:
        managed = False
        db_table = 'user'


class FilePermissionManager(models.Manager):
    def create(self, *args, **kwargs):
        if 'node' not in kwargs or 'user' not in kwargs:
            raise Exception('node and user are required')
        node = kwargs['node']
        user = kwargs['user']
        permission = node.filepermission_set.filter(user=user, is_active=True).first()
        childs = node.filenode_set.filter(is_deleted=False).all()
        for child in childs:
            kwargs['node'] = child
            FilePermission.objects.create(*args, **kwargs)
        kwargs['node'] = node
        if permission:
            return permission
        return super().create(*args, **kwargs)

class FilePermission(models.Model):
    node = models.ForeignKey(FileNode, models.DO_NOTHING)
    user = models.ForeignKey(User, models.DO_NOTHING)
    can_write = models.IntegerField()
    is_active = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    objects = FilePermissionManager()

    class Meta:
        managed = False
        db_table = 'file_permission'

    def delete(self):
        self.is_active = False
        for child in self.node.filenode_set.all():
            for child_perm in child.filepermission_set.filter(user=self.user, is_active=True).all():
                child_perm.delete()
        self.save()
