from rest_framework import serializers
from organization.models import Organization
from accounts.models import User

class OrganizationCreation_Serializer(serializers.ModelSerializer):

    class Meta:
        model=Organization
        fields='__all__'

class OrganizationsList_Serializer(serializers.ModelSerializer):

    class Meta:
        model=Organization
        fields='__all__'


class OrganizationPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["name", "description", "logo", "is_active"]
        extra_kwargs = {
            "name": {"required": False},
            "description": {"required": False},
            "logo": {"required": False},
            "is_active": {"required": False},
        }

class OrganizationPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["name", "description", "logo", "is_active"]



class OrganizationAdminCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model=User

        fields=(
            'first_name',
            'last_name',
            'email',
            'username',
            'password'
        )
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):

        user = User.objects.create_user(**validated_data)
        return user




class OrganizationAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model=User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "role",
            "organization",
            "is_active",
            "date_joined",
        )



class OrganizationAdminUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model=User
        fields=[
            'first_name',
            'last_name',
            'email',
            'username',
        ]


class OrganizationsAdminsListSerializer(serializers.ModelSerializer):

    class Meta:
        model=User
        fields=[
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'organization'
        ]



class OrganizationAdminDetailSerializer(serializers.ModelSerializer):

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