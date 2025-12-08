from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import AppVersion

@api_view(['GET'])
@permission_classes([AllowAny])
def latest_version(request):
    latest = AppVersion.objects.first() # Ordered by -version_code in Meta
    if latest:
        data = {
            "version_code": latest.version_code,
            "version_name": latest.version_name,
            "download_url": request.build_absolute_uri(latest.apk_file.url),
            "is_mandatory": latest.is_mandatory,
            "release_notes": latest.release_notes,
        }
        return Response(data)
    return Response({"error": "Nenhuma versão encontrada"}, status=404)
