from django.urls import path
from . import views

app_name = 'packages'

urlpatterns = [
    path('', views.TravelPackageListView.as_view(), name='package_list'),
    path('categories/', views.PackageCategoryListView.as_view(), name='category_list'),
    path('search/', views.search_packages, name='search_packages'),
    path('<int:pk>/', views.TravelPackageDetailView.as_view(), name='package_detail'),
]