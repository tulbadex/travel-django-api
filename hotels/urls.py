from django.urls import path
from . import views

app_name = 'hotels'

urlpatterns = [
    path('', views.HotelListView.as_view(), name='hotel_list'),
    path('categories/', views.HotelCategoryListView.as_view(), name='category_list'),
    path('search/', views.search_hotels, name='search_hotels'),
    path('<int:pk>/', views.HotelDetailView.as_view(), name='hotel_detail'),
]