from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, OfficeViewSet, StudentViewSet, MenuItemViewSet, ProjectViewSet, home, course_list, register, contact, student_dashboard, student_login, admin_dashboard, student_profile_edit, student_password_reset_request, student_password_reset_confirm, student_verify_email, admin_export_students, student_certificate_download, projects, resend_verification_email

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'offices', OfficeViewSet)
router.register(r'students', StudentViewSet)
router.register(r'menus', MenuItemViewSet)
router.register(r'projects', ProjectViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('', home, name='home'),
    path('courses/', course_list, name='course_list'),
    path('projects/', projects, name='projects'),
    path('register/', register, name='register'),
    path('contact/', contact, name='contact'),
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('student/login/', student_login, name='student_login'),
    path('student/profile/edit/', student_profile_edit, name='student_profile_edit'),
    path('student/password-reset/', student_password_reset_request, name='student_password_reset_request'),
    path('student/password-reset-confirm/<str:token>/', student_password_reset_confirm, name='student_password_reset_confirm'),
    path('student/verify-email/<str:token>/', student_verify_email, name='student_verify_email'),
    path('student/resend-verification/', resend_verification_email, name='resend_verification_email'),
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/export-students/', admin_export_students, name='admin_export_students'),
    path('student/certificate/<int:course_id>/', student_certificate_download, name='student_certificate_download'),
] 