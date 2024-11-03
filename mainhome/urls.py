from django.urls import path
from . import views

urlpatterns = [
    path('home/',views.home,name = 'home'),
    path('logout/',views.logout_user,name = 'logout'),
    path('convert/', views.pdf_to_docx_view, name='pdf_to_docx'),
    
]

