from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView,TokenBlacklistView
from accounts.serializer import OrganizationEmployeeUpdateSerializer,OrganizationEmployeeDetailsSerializer,OrganizationEmployeeSerializer,EmployeeCreationSerializer,CustomTokenObtainPairSerializer,CustomTokenRefreshPairSerializer,LogoutSerializer,ProfileSerializer
from drf_spectacular.utils import extend_schema , OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.generics import CreateAPIView,ListAPIView,RetrieveAPIView,UpdateAPIView,DestroyAPIView
from rest_framework.permissions import BasePermission
from accounts.models import User
from drf_spectacular.utils import extend_schema_view,OpenApiResponse
from django.shortcuts import get_object_or_404
# Create your views here.



##Class View to get Access and Refresh Token 
class CustomTokenObtainPairView(TokenObtainPairView):

    serializer_class=CustomTokenObtainPairSerializer


    @extend_schema(
    summary="User Login",
    description="Authenticate using email and password.",
    request=CustomTokenObtainPairSerializer,
    responses=CustomTokenObtainPairSerializer,
    tags=["Authentication"],
    )
    def post(self,request,*args,**kwargs):
        return super().post(request, *args, **kwargs)



## Class View to Refresh Token
class CustomTokenRefreshView(TokenRefreshView):
    serializer_class=CustomTokenRefreshPairSerializer


    @extend_schema(
    summary="Token Refresh",
    description="Takes Refresh Token and Gives new Access Token",
    request=CustomTokenRefreshPairSerializer,
    responses=CustomTokenRefreshPairSerializer,
    tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    

## Class view to Blaclist Token (Logout)
class Logout(TokenBlacklistView):



    serializer_class=LogoutSerializer


    @extend_schema(
    summary="User Logout",
    description="Blacklist Refresh Token",
    request=LogoutSerializer,
    responses=LogoutSerializer,
    tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)

        return Response({"message":"Logged out Successfully"},status=status.HTTP_200_OK)
    

## class view for profile data
class ProfileView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes =[IsAuthenticated]
    
    @extend_schema(
        summary="User Profile Data",
        description="input is Access Token and Output will be User Data with his organization and Role Details",
        request=ProfileSerializer,
        responses=ProfileSerializer
    )
    def get(self,request,*args,**kwargs):

        serializer=ProfileSerializer(request.user )


        
        return Response(serializer.data)
        

## class to allow permission to create employee

class IsOrgAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.role == "ORG_ADMIN"


## class view to create employee
@extend_schema_view(
    post=extend_schema(
        summary="Create Employee",
        description="Creates a new employee for the authenticated organization.",
        request=EmployeeCreationSerializer,
        responses={
            201: OpenApiResponse(
                description="Employee created successfully."
            ),
            400: OpenApiResponse(
                description="Validation error."
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            403: OpenApiResponse(
                description="Only organization admins can create employees."
            ),
        },
    )
)
class OrganizationEmployeeCreateView(CreateAPIView):

    authentication_classes=[JWTAuthentication]
    permission_classes =[IsAuthenticated,IsOrgAdmin]
    serializer_class=EmployeeCreationSerializer


    def perform_create(self, serializer):


        serializer.save(
        organization=self.request.user.organization,
        role=User.Role.EMPLOYEE,
        )   


## class view to get organization specific employees


@extend_schema_view(
    get=extend_schema(
        summary="List Organization EMployees",
        description='Returns all employees belonging to the authenticated organization',
        responses={
            200:OrganizationEmployeeSerializer(many=True),
            401:OpenApiResponse(
                description="Authentication Credentials were not provided"
            ),
            403:OpenApiResponse(
                description='Only organization admins can access this endpoint'
            )
        }
    )
)
class OrganizationEmployeesListView(ListAPIView):

    authentication_classes=[JWTAuthentication]
    permission_classes =[IsAuthenticated,IsOrgAdmin]
    serializer_class=OrganizationEmployeeSerializer


    def get_queryset(self):

        organization=self.request.user.organization

        users=User.objects.filter(organization=organization,role=User.Role.EMPLOYEE)

        return users



## class view to get a specific employee details
@extend_schema_view(
    get=extend_schema(
        summary="Organization Employee Details",
        description='Returns employee details belonging to the authenticated organization',
        responses={
            200:OrganizationEmployeeDetailsSerializer(many=True),
            401:OpenApiResponse(
                description="Authentication Credentials were not provided"
            ),
            403:OpenApiResponse(
                description='Only organization admins can access this endpoint'
            )
        }
    )
)
class OrganizationEmployeesDetailView(RetrieveAPIView):

    authentication_classes=[JWTAuthentication]
    permission_classes =[IsAuthenticated,IsOrgAdmin]
    serializer_class=OrganizationEmployeeDetailsSerializer


    def get_object(self):

        return get_object_or_404(
            User,
            pk=self.kwargs["pk"],
            organization=self.request.user.organization,
            role=User.Role.EMPLOYEE,
        )



## class view to update organization employee
@extend_schema_view(
    put=extend_schema(
        summary="Update Employee",
        description="Fully updates an employee belonging to the authenticated organization.",
        request=OrganizationEmployeeUpdateSerializer,
        responses={
            200: OrganizationEmployeeUpdateSerializer,
            400: OpenApiResponse(description="Validation error."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Only organization admins can update employees."),
            404: OpenApiResponse(description="Employee not found."),
        },
    ),
    patch=extend_schema(
        summary="Partially Update Employee",
        description="Updates only the provided fields for an employee belonging to the authenticated organization.",
        request=OrganizationEmployeeUpdateSerializer,
        responses={
            200: OrganizationEmployeeUpdateSerializer,
            400: OpenApiResponse(description="Validation error."),
            401: OpenApiResponse(description="Authentication required."),
            403: OpenApiResponse(description="Only organization admins can update employees."),
            404: OpenApiResponse(description="Employee not found."),
        },
    ),
)
class OrganizationEmployeeUpdateView(UpdateAPIView):

    authentication_classes=[JWTAuthentication]
    permission_classes =[IsAuthenticated,IsOrgAdmin]
    serializer_class=OrganizationEmployeeUpdateSerializer


    def get_object(self):
    
            return get_object_or_404(
                User,
                pk=self.kwargs["pk"],
                organization=self.request.user.organization,
                role=User.Role.EMPLOYEE,
            )



## class view to delete organization employee
@extend_schema_view(
    delete=extend_schema(
        summary="Delete Employee",
        description="Deletes an employee belonging to the authenticated organization.",
        responses={
            204: OpenApiResponse(
                description="Employee deleted successfully."
            ),
            401: OpenApiResponse(
                description="Authentication required."
            ),
            403: OpenApiResponse(
                description="Only organization admins can delete employees."
            ),
            404: OpenApiResponse(
                description="Employee not found."
            ),
        },
    )
)
class OrganizationEmployeeDeleteView(DestroyAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOrgAdmin]

    def get_queryset(self):
        return User.objects.filter(
            organization=self.request.user.organization,
            role=User.Role.EMPLOYEE,
        )