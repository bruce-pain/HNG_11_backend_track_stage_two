from rest_framework import permissions, status, generics
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from api_auth.serializer import UserSerializer, OrganisationSerializer
from api.serializer import UserIdSerializer

from api_auth.models import CustomUser, Organisation


def error_formatter(errors: dict):
    error_list = []

    for field, messages in errors.items():
        for message in messages:
            error_list.append({"field": field, "message": message})

    return error_list


class UserDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, userId):
        related_orgs = Organisation.objects.filter(users=request.user)
        users = CustomUser.objects.filter(organisations__in=related_orgs).distinct()
        try:
            user = users.get(userId=userId)
        except CustomUser.DoesNotExist:
            return Response(
                {"message": "user does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UserSerializer(user)

        return Response(
            {
                "status": "success",
                "message": "User found",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


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
        # return Response(
        #     {"status": "Bad Request", "message": "Client error", "statusCode": 400},
        #     status=status.HTTP_400_BAD_REQUEST,
        # )
        return Response(
            error_formatter(serializer.errors),
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class OrganisationDetailAPIView(APIView):
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
            },
            status=status.HTTP_200_OK,
        )


class OrganisationAddUserAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, orgId):
        serializer = UserIdSerializer(data=request.data)

        if serializer.is_valid():
            userId = request.data["userId"]

            try:
                user = CustomUser.objects.get(userId=userId)
            except CustomUser.DoesNotExist:
                return Response(
                    {"message": "user does not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            try:
                organisation = Organisation.objects.get(orgId=orgId)
            except Organisation.DoesNotExist:
                return Response(
                    {"message": "organisation does not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            organisation.users.add(user)

            payload = {
                "status": "success",
                "message": "User added to organisation successfully",
            }

            return Response(payload, status=status.HTTP_200_OK)

        # return Response(
        #     {"status": "Bad Request", "message": "Client error", "statusCode": 400},
        #     status=status.HTTP_400_BAD_REQUEST,
        # )
        return Response(
            error_formatter(serializer.errors),
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
