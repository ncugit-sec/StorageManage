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


class FilePermission(models.Model):
    node = models.ForeignKey(FileNode, models.DO_NOTHING)
    user = models.ForeignKey(User, models.DO_NOTHING)
    can_write = models.IntegerField(default=0)
    is_active = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        managed = False
        db_table = 'file_permission'
