from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

@api_view()
def pilot(request: Request):
    return Response({"status": "LFGGGGGG"})
