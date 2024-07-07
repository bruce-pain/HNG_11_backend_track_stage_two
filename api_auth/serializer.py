from rest_framework import serializers
from api_auth.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    # userId = serializers.CharField(source="user_id")
    firstName = serializers.CharField(source="first_name")
    lastName = serializers.CharField(source="last_name")

    class Meta:
        model = CustomUser
        fields = ["userId", "firstName", "lastName", "email", "password", "phone"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_phone(self, value: str):
        temp = value[1:] if value.startswith("+") else value
        for c in temp:
            if not c.isdigit():
                raise serializers.ValidationError(
                    "Phone number can only contain digits"
                )
        return value

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)
