from rest_framework import serializers
from lms_user import models as lms_user_models
from leave_manager import models as leave_manager_models
from mobile_api import models as mobile_api_models

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('user', 'phone_number','department', 'leave_issuer', 'date_of_birth', 'joined_date')
        model = lms_user_models.LmsUser


class LeaveSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('user', 'type','from_date', 'to_date', 'reason','half_day')
        model = leave_manager_models.Leave


class CompensationSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('user','reason','days',)
        model = leave_manager_models.CompensationLeave


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('title','from_date','to_date','description','image')
        model = leave_manager_models.Holiday


class ChangeUserPhotoSerailizer(serializers.ModelSerializer):
    class Meta:
        fields = ('image',)
        model = lms_user_models.LmsUser


class ChangeUserPhoneSerailizer(serializers.ModelSerializer):
    class Meta:
        fields = ('phone_number',)
        model = lms_user_models.LmsUser


class PasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for password reset endpoint.
    """
    email = serializers.EmailField(required=True)


class PasswordResetDoneSerializer(serializers.Serializer):
    """
    Serializer for password reset done endpoint.
    """
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

