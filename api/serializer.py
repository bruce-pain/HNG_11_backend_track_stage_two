from rest_framework import serializers


class UserIdSerializer(serializers.Serializer):
    userId = serializers.UUIDField()
