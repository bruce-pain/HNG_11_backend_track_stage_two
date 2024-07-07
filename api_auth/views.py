from rest_framework import permissions, status, generics
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.db import transaction

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import TokenError

from api_auth.serializer import UserSerializer, LoginSerializer
from api_auth.models import CustomUser, Organisation


def error_formatter(errors: dict):
    error_list = []

    for field, messages in errors.items():
        for message in messages:
            error_list.append({"field": field, "message": message})

    return error_list


class UserRegisterAPIView(APIView):
    """
    Registers a users and creates a default organisation
    """

    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request: Request, format=None):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            token_serializer = TokenObtainPairSerializer(
                data={
                    "email": request.data["email"],
                    "password": request.data["password"],
                }
            )

            try:
                token_serializer.is_valid(raise_exception=True)
                tokens = token_serializer.validated_data
            except TokenError:
                return Response(
                    {
                        "status": "Bad request",
                        "message": "Registration unsuccessful",
                        "statusCode": 400,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            payload = {
                "status": "success",
                "message": "Registration successful",
                "data": {
                    "accessToken": tokens["access"],
                    "user": serializer.data,
                },
            }
            new_organisation = Organisation.objects.create(
                name=f"{serializer.data["firstName"]}'s Organisation"
            )

            new_organisation.users.add(user)

            return Response(payload, status=status.HTTP_201_CREATED)
        return Response(
            error_formatter(serializer.errors),
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class UserLoginAPIView(APIView):
    """
    logs in a user. When you log in, you can select an organisation to interact with
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request: Request, format=None):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = authenticate(
                request=request,
                email=request.data["email"],
                password=request.data["password"],
            )

            if user is not None:
                token_serializer = TokenObtainPairSerializer(
                    data={
                        "email": request.data["email"],
                        "password": request.data["password"],
                    }
                )

                try:
                    token_serializer.is_valid(raise_exception=True)
                    tokens = token_serializer.validated_data
                except TokenError:
                    # Token error
                    return Response(
                        {
                            "status": "Bad request",
                            "message": "Authentication failed",
                            "statusCode": 401,
                        },
                        status=status.HTTP_401_UNAUTHORIZED,
                    )

                payload = {
                    "status": "success",
                    "message": "Login successful",
                    "data": {
                        "accessToken": tokens["access"],
                        "user": UserSerializer(user).data,
                    },
                }
                return Response(payload, status=status.HTTP_200_OK)

            # User does not exist
            return Response(
                {
                    "status": "Bad request",
                    "message": "Authentication failed",
                    "statusCode": 401,
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # validation error
        return Response(
            error_formatter(serializer.errors),
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
