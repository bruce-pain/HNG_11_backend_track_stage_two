from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import TokenError

from api_auth.serializer import UserSerializer


class UserRegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request, format=None):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

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
            return Response(payload, status=status.HTTP_201_CREATED)
        return Response(
            self.error_formatter(serializer.errors),
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    def error_formatter(self, errors: dict):
        error_list = []

        for field, messages in errors.items():
            for message in messages:
                error_list.append({"field": field, "message": message})

        return error_list
