
from django.urls import path
from organization.views import OrganizationCreation,OrganizationsList,OrganizationsAdminsList,OrganizationAdminDetail,OrganizationAdmin,OrganizationDelete,OrganizationPut,OrganizationPatch,OrganizationAdminCreate,OrganizationAdminDelete,OrganizationAdminPut

urlpatterns = [

    ## Organization 
    path("api/v1/organizations/", OrganizationsList.as_view(), name="organization-list"),
    path("api/v1/organizations/create/", OrganizationCreation.as_view(), name="organization-create"),
    path("api/v1/organizations/<int:pk>/delete/", OrganizationDelete.as_view(), name="organization-delete"),
    path("api/v1/organizations/<int:pk>/update/", OrganizationPut.as_view(), name="organization-update"),
    path("api/v1/organizations/<int:pk>/partial-update/", OrganizationPatch.as_view(), name="organization-partial-update"),


    ## Organization Admins 
    path('api/v1/organizations/<int:organization_id>/admins/',OrganizationAdminCreate.as_view(),name='organization_admin_create'),
    path('api/v1/organizations/<int:organization_id>/admins/delete/<int:admin_id>/',OrganizationAdminDelete.as_view(),name='organization_admin_delete'),
    path('api/v1/organizations/<int:organization_id>/admin/',OrganizationAdmin.as_view(),name='organization_admin'),
    path("api/v1/organizations/<int:organization_id>/admins/update/<int:admin_id>/",OrganizationAdminPut.as_view(),name="organization_admin_update"),
    path('api/v1/organizations/admins/',OrganizationsAdminsList.as_view(),name='organizations_admins_list'),
    path('api/v1/organizations/<int:organization_id>/admins/detail/<int:admin_id>/',OrganizationAdminDetail.as_view(),name='organizations_admin_retreive'),
]

