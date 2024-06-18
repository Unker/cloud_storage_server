from functools import wraps
from django.utils import timezone
from django.http import FileResponse, Http404
from .models import StorageFiles

def handle_file_download(get_file_instance):
    @wraps(get_file_instance)
    def wrapper(viewset, request, *args, **kwargs):
        try:
            file_instance = get_file_instance(viewset, request, *args, **kwargs)
            file_instance.last_download_date = timezone.now()
            file_instance.save()
            return FileResponse(file_instance.file.open(), as_attachment=True, filename=file_instance.file.name)
        except StorageFiles.DoesNotExist:
            raise Http404("File not found")
    return wrapper
