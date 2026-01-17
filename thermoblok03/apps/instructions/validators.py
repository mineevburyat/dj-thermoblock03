import os
import magic
from django.core.exceptions import ValidationError

def validate_is_video(file):
    valid_mime_types = ['video/mp4','video/webm', 'video/ogg']
    file_mime_type = magic.from_buffer(file.read(1024), mime=True)
    if file_mime_type not in valid_mime_types:
        raise ValidationError('Unsupported file type.')
    valid_file_extensions = ['.mp4', '.ogg', '.avi', '.mov']
    ext = os.path.splitext(file.name)[1]
    if ext.lower() not in valid_file_extensions:
        raise ValidationError('Unacceptable file extension.')