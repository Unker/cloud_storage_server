from functools import wraps

from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.http import FileResponse, Http404
from rest_framework import status
from rest_framework.response import Response

from .models import StorageFiles


def handle_file_download(get_file_instance):
    @wraps(get_file_instance)
    def wrapper(viewset, request, *args, **kwargs):
        try:
            file_instance = get_file_instance(viewset, request, *args, **kwargs)

            if not viewset.has_permission_to_download(request.user, file_instance):
                raise PermissionDenied("You do not have permission to download this file.")

            file_instance.last_download_date = timezone.now()
            file_instance.save()
            response = FileResponse(file_instance.file.open(), as_attachment=True, filename=file_instance.file.name)
            response['Access-Control-Expose-Headers'] = 'Content-Disposition'
            return response
        except StorageFiles.DoesNotExist:
            raise Http404("File not found")
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

    return wrapper
