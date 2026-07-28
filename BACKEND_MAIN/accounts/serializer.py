
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer,TokenRefreshSerializer,TokenBlacklistSerializer
from rest_framework import serializers
from django.contrib.auth import authenticate
from accounts.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    
    def validate(self, attrs):

        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "role": self.user.role,
            "organization_id": self.user.organization_id,
            "organization_name": self.user.organization.name if self.user.organization else None,
        }
        return data
    

class CustomTokenRefreshPairSerializer(TokenRefreshSerializer):
    
    def validate(self, attrs):
        data=super().validate(attrs)
        return data
    

class LogoutSerializer(TokenBlacklistSerializer):
    pass


class ProfileSerializer(serializers.ModelSerializer):



    organization_name=serializers.CharField(
        source="organization.name",
        read_only=True
    )

    class Meta:
        model=User
        fields=[
            "id",
            "first_name",
            "last_name",
            "email",
            "role",
            "organization",
            "organization_name"
        ]


class EmployeeCreationSerializer(serializers.ModelSerializer):



    class Meta:
        model=User
        fields=[
            'first_name',
            'last_name',
            'email',
            'username',
            'is_active',
            'password',
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
    
            user = User.objects.create_user(**validated_data)
            return user


class OrganizationEmployeeSerializer(serializers.ModelSerializer):
    organization=serializers.CharField(source="organization.name",read_only=True)

    class Meta:
        model=User
        fields=[
            'id',
            'first_name',
            'last_name',
            'email',
            'username',
            'role',
            'organization'
        ]


class OrganizationEmployeeDetailsSerializer(serializers.ModelSerializer):

    organization=serializers.CharField(source="organization.name",read_only=True)

    class Meta:
        model=User
        fields=[
            'id',
            'first_name',
            'last_name',
            'email',
            'username',
            'role',
            'organization'
        ]



class OrganizationEmployeeUpdateSerializer(serializers.ModelSerializer):


    class Meta:
        model=User
        fields=[
            'first_name',
            'last_name',
            'email',
            'username',
            'is_active',
        ]


        
        