from django.shortcuts import render
from rest_framework.views import APIView
from organization.serializer import OrganizationPutSerializer,OrganizationPatchSerializer,OrganizationCreation_Serializer,OrganizationsList_Serializer,OrganizationAdminCreateSerializer,OrganizationsAdminsListSerializer,OrganizationAdminSerializer,OrganizationAdminUpdateSerializer,OrganizationAdminDetailSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema,OpenApiResponse,extend_schema_view
from rest_framework.parsers import MultiPartParser, FormParser
from organization.models import Organization
from rest_framework.generics import CreateAPIView,DestroyAPIView,ListAPIView,UpdateAPIView,RetrieveAPIView
from accounts.models import User
from django.shortcuts import get_object_or_404
from django.http import Http404

# Create your views here.

## class view to create a superadmin permission
class IsSuperAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.role == "SUPER_ADMIN"



## Class View to create Organization

class OrganizationCreation(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsSuperAdmin]
    parser_classes = [MultiPartParser, FormParser]


    @extend_schema(
        summary='Organization Creation',
        description='take access token and only allow Super_admin to create organization',
        request=OrganizationCreation_Serializer,
        responses=OrganizationCreation_Serializer
    )
    def post(self,request,*args,**kwargs):
        serializer=OrganizationCreation_Serializer(data=request.data)
        serializer.is_valid(raise_exception=True) 
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)


## class view to get Active organziations List
class OrganizationsList(APIView):

    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsSuperAdmin]


    @extend_schema(
            summary="Organziations List",
            description="return list of all organizations",
            request=OrganizationsList_Serializer,
            responses=OrganizationsList_Serializer
    )
    def get(self,request,*args,**kwargs):

        Organizations=Organization.objects.all()

        serializer=OrganizationsList_Serializer(Organizations,many=True)

        return Response({"message":"organizations List Sent","organizations":serializer.data},status=status.HTTP_200_OK)
            


## class view to delete organziation

class OrganizationDelete(APIView):     

    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsSuperAdmin]


    @extend_schema(
    summary="Delete Organization",
    description="Deletes an organization by its ID. Only Super Admins can perform this action.",
    responses={
        204: None,
        404: OpenApiResponse(description="Organization not found"),
    },
)
    def delete(self,request,pk,*args,**kwargs):

        try:
            organization=Organization.objects.get(id=pk)

            organization.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Organization.DoesNotExist:

            return Response(status=status.HTTP_404_NOT_FOUND)

    
## class view to update [put mehtod]  organization

class OrganizationPut(APIView):

    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsSuperAdmin]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
    summary="Update Organization",
    description="Fully updates an existing organization. All fields should be provided.",
    request=OrganizationPutSerializer,
    responses={
        200: OpenApiResponse(
            description="Organization updated successfully."
        ),
        404: OpenApiResponse(
            description="Organization not found."
        ),
    },
)
    def put(self, request, pk, *args, **kwargs):

        try:
            organization = Organization.objects.get(pk=pk)

            serializer = OrganizationPutSerializer(
            organization,
            data=request.data
            )

            if serializer.is_valid():
                serializer.save()

            return Response(serializer.data)


        except Organization.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)



        
## class view to update [patch mehtod]  organization

class OrganizationPatch(APIView):



    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    parser_classes = [MultiPartParser, FormParser]


    @extend_schema(
    summary="Partially Update Organization",
    description="Updates only the fields provided for an existing organization.",
    request=OrganizationPatchSerializer,
    responses={
        200: OpenApiResponse(
            description="Organization updated successfully."
        ),
        404: OpenApiResponse(
            description="Organization not found."
        ),
    },
)
    def patch(self, request, pk, *args, **kwargs):

        try:
            organization = Organization.objects.get(pk=pk)

            print(request.data)
            serializer = OrganizationPatchSerializer(
            organization,
            data=request.data,
            partial=True
        )

            if serializer.is_valid():
                serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)


        except Organization.DoesNotExist:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        


## class view to create Organization Admin
@extend_schema_view(
    post=extend_schema(
        summary="Create Organization Admin",
        description="Create a new organization administrator for a specific organization.",
        request=OrganizationAdminCreateSerializer,
        responses=OrganizationAdminCreateSerializer,
    )
)
class OrganizationAdminCreate(CreateAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    serializer_class=OrganizationAdminCreateSerializer


    def perform_create(self, serializer):

        organization = get_object_or_404(
            Organization,
            pk=self.kwargs["organization_id"]
        )

        serializer.save(role=User.Role.ORG_ADMIN,organization=organization)



## class view to delete Organization Admin
@extend_schema_view(
    delete=extend_schema(
        summary="Delete Organization Admin",
        description="Delete a specific organization admin.",
        responses={204: None, 404: None}
    )
)
class OrganizationAdminDelete(DestroyAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSuperAdmin]


    def get_object(self):

        organization = get_object_or_404(
            Organization,
            pk=self.kwargs["organization_id"]
        )

        user = get_object_or_404(
            User,
            pk=self.kwargs["admin_id"],
            organization=organization
        )

        if user.role == User.Role.ORG_ADMIN:
            return user

        else :
            raise Http404("This user cannot be deleted.")
    


## class view to Retreive Organization ADmins
@extend_schema_view(
    get=extend_schema(
        summary="Organization Admins List",
        description="Get all Organization Admins for a specific organization.",
        responses=OrganizationAdminSerializer(many=True),
    )
)
class OrganizationAdmin(ListAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    serializer_class = OrganizationAdminSerializer

    def get_queryset(self):

        organization = get_object_or_404(
            Organization,
            pk=self.kwargs["organization_id"]
        )

        return User.objects.filter(
            role=User.Role.ORG_ADMIN,
            organization=organization
        )


## class view to Update Organziation Admin Details
@extend_schema_view(
    put=extend_schema(
        summary="Update Organization Admin",
        description="Replace all editable details of a specific organization administrator.",
        request=OrganizationAdminUpdateSerializer,
        responses={200: OrganizationAdminUpdateSerializer},
    ),
    patch=extend_schema(
        summary="Partially Update Organization Admin",
        description="Update one or more editable fields of a specific organization administrator.",
        request=OrganizationAdminUpdateSerializer,
        responses={200: OrganizationAdminUpdateSerializer},
    ),
)
class OrganizationAdminPut(UpdateAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    serializer_class=OrganizationAdminUpdateSerializer

    def get_object(self):

        organization = get_object_or_404(
        Organization,
        pk=self.kwargs["organization_id"]
    )

        user = get_object_or_404(
        User,
        pk=self.kwargs["admin_id"],
        organization=organization
    )

        if user.role != User.Role.ORG_ADMIN:
            raise Http404("Organization Admin not found.")

        return user



## CLass view to get all admins of all organziations 
@extend_schema_view(
    get=extend_schema(
        summary="List Organizations Admins",
        description="Retrieve all organization admins",
        responses=OrganizationsAdminsListSerializer(many=True),
    )
)
class OrganizationsAdminsList(ListAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    serializer_class=OrganizationsAdminsListSerializer


    def get_queryset(self):
    
            return User.objects.filter(
                role=User.Role.ORG_ADMIN,
            )


## class view to retreive organization admin detail
@extend_schema_view(
    get=extend_schema(
        summary="Organization Admin Detail",
        description="Retrieve the details of a specific organization administrator.",
        responses=OrganizationAdminDetailSerializer,
    )
)
class OrganizationAdminDetail(RetrieveAPIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    serializer_class=OrganizationAdminDetailSerializer


    def get_object(self):

        organization=get_object_or_404(
            Organization,
            pk=self.kwargs['organization_id']
        )


        user=get_object_or_404(
            User,
            pk=self.kwargs["admin_id"],
            role=User.Role.ORG_ADMIN,
            organization=organization
        )
        return user

        