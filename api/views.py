from rest_framework import permissions, status, generics
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.db import transaction

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import TokenError

from api_auth.serializer import UserSerializer, OrganisationSerializer
from api_auth.models import CustomUser, Organisation


def error_formatter(errors: dict):
    error_list = []

    for field, messages in errors.items():
        for message in messages:
            error_list.append({"field": field, "message": message})

    return error_list


class UserDetailAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    lookup_field = "userId"
    lookup_url_kwarg = "userId"

    def get_queryset(self):
        user = self.request.user
        related_orgs = Organisation.objects.filter(users=user)

        return CustomUser.objects.filter(organisations__in=related_orgs).distinct()


class OrganisationAPIView(APIView):
    """
    gets all your organisations the user belongs to or created.
    If a user is logged in properly, they can get all their organisations.
    They should not get another user’s organisation [PROTECTED].
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request):
        organisations = Organisation.objects.filter(users=request.user)
        serializer = OrganisationSerializer(organisations, many=True)
        payload = {
            "status": "success",
            "message": "Organisations related to user",
            "data": {"organisations": serializer.data},
        }
        return Response(payload, status=status.HTTP_200_OK)

    def post(self, request: Request, format=None):
        serializer = OrganisationSerializer(data=request.data)

        if serializer.is_valid():
            organisation = serializer.save()
            organisation.users.add(request.user)

            payload = {
                "status": "success",
                "message": "Organisation created successfully",
                "data": serializer.data,
            }

            return Response(payload, status=status.HTTP_201_CREATED)
        return Response(
            {"status": "Bad Request", "message": "Client error", "statusCode": 400},
            status=status.HTTP_400_BAD_REQUEST,
        )


class OrganisationDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, orgId):
        orgs = Organisation.objects.filter(users=request.user)
        try:
            organisation = orgs.get(orgId=orgId)
        except Organisation.DoesNotExist:
            return Response(
                {"message": "organisation does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OrganisationSerializer(organisation)

        return Response(
            {
                "status": "success",
                "message": "Organisation found",
                "data": serializer.data,
            }
        )
