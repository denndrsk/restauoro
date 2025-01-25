from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

urlpatterns = [
    path('step1/', views.step1_upload, name='step1_upload'),
    path('step2/<str:project_id>/', views.step2_viewer, name='step2_viewer'),
    path('step_2_5_selection/<str:project_id>/', views.step2_5_selection, name='step2_5_selection'),
    path('step3/<str:project_id>/', views.step3_clean_up, name='step3_clean_up'),
    path('step4/<str:project_id>/', views.step4_filling_piece, name='step4_filling_piece'),
    path('step5/<str:project_id>/', views.step5_filling_peace_viewer, name='step5_filling_peace_viewer'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)