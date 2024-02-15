from django.conf import settings
from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.models import generic

import os


# Create your models here.
# def file_upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    # return "{}_{}".format(instance.user.username, filename)
ALLOWED = ['jpg', 'jpeg', 'png', 'pdf', 'doc']

class MediaFile(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    file_name = models.CharField(_('File Name'), 
                                 max_length=500)
    file = models.FileField(_('File'), 
                            upload_to='mediastore/', 
                            validators=[FileExtensionValidator(allowed_extensions=ALLOWED)])

    def get_file_path(self):
        if self.file:
            return os.path.join(settings.MEDIA_ROOT, self.file_name)
    
    def delete_file(self):
        os.remove(self.get_file_path())
        # self.file.delete()