
from django.urls import path
from accounts import views as AccountViews

urlpatterns=[

    ## JWt Auth
    path('api/v1/login/',AccountViews.CustomTokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('api/v1/token/refresh/',AccountViews.CustomTokenRefreshView.as_view(),name='token_refresh_pair'),
    path('api/v1/logout/',AccountViews.Logout.as_view(),name='logout'),
    path('api/v1/profile/',AccountViews.ProfileView.as_view(),name='profile'),


    ## Employees related URls
    path('api/v1/employee/',AccountViews.OrganizationEmployeeCreateView.as_view(),name='employee_create'),
    path('api/v1/employees_list/',AccountViews.OrganizationEmployeesListView.as_view(),name='employees_list'),
    path('api/v1/employee/<int:pk>/',AccountViews.OrganizationEmployeesDetailView.as_view(),name='employee_details'),
    path('api/v1/employee_update/<int:pk>/',AccountViews.OrganizationEmployeeUpdateView.as_view(),name='employee_update'),
    path('api/v1/employee_delete/<int:pk>/',AccountViews.OrganizationEmployeeDeleteView.as_view(),name='employee_delete'),
]