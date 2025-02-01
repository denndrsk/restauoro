from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

urlpatterns = [
    path('step1/', views.step1_upload, name='step1_upload'),
    path('step2/<str:project_id>/', views.step2_viewer, name='step2_viewer'),
    path('step3/<str:project_id>/', views.step3_selection, name='step3_selection'),
    path('step4/<str:project_id>/', views.step4_clean_up, name='step4_clean_up'),
    path('step5/<str:project_id>/', views.step5_filling_piece, name='step5_filling_piece'),
    path('step6/<str:project_id>/', views.step6_filling_piece_viewer, name='step6_filling_piece_viewer'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)