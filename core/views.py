from django.shortcuts import render, redirect
from rest_framework import viewsets
from .models import Course, Office, Student, MenuItem, Notification, Message, ActivityLog, CourseCompletion, StudentNotification, Project
from .serializers import CourseSerializer, OfficeSerializer, StudentSerializer, MenuItemSerializer, ProjectSerializer
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, HttpResponse
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.core.signing import TimestampSigner
import uuid
import csv

signer = TimestampSigner()

# API ViewSets
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class OfficeViewSet(viewsets.ModelViewSet):
    queryset = Office.objects.all()
    serializer_class = OfficeSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

# Frontend Views

def home(request):
    courses = list(Course.objects.all())
    offices = list(Office.objects.all())
    projects = list(Project.objects.filter(is_active=True))
    from .models import StudentNotification
    notifications = StudentNotification.objects.filter(is_active=True).order_by('-created')
    # Dummy data if empty
    if not courses:
        courses = [
            Course(id=1, title="Graphics Designing", description="Learn Photoshop, Illustrator, and more.", image="/static/dummy1.jpg", duration="3 Months", fee="PKR 15,000", mode="Online/Onsite"),
            Course(id=2, title="Python Programming", description="Python from basics to advanced.", image="/static/dummy2.jpg", duration="2.5 Months", fee="PKR 14,000", mode="Online/Onsite"),
        ]
    if not offices:
        offices = [
            Office(id=1, name="Main Campus", address="123 Main Road, Lahore, Pakistan"),
            Office(id=2, name="City Branch", address="45 City Center, Karachi, Pakistan"),
        ]
    if not projects:
        projects = [
            Project(id=1, name="E-Commerce Website", title="Modern Online Store", link="https://example.com", description="A full-featured e-commerce platform built with Django and React."),
            Project(id=2, name="AI Chatbot", title="Intelligent Assistant", link="https://example.com", description="Machine learning-powered chatbot for customer support."),
        ]
    return render(request, "core/home.html", {"courses": courses, "offices": offices, "notifications": notifications, "projects": projects})

def course_list(request):
    courses = list(Course.objects.all())
    if not courses:
        courses = [
            Course(id=1, title="Graphics Designing", description="Learn Photoshop, Illustrator, and more.", image="/static/dummy1.jpg", duration="3 Months", fee="PKR 15,000", mode="Online/Onsite"),
            Course(id=2, title="Python Programming", description="Python from basics to advanced.", image="/static/dummy2.jpg", duration="2.5 Months", fee="PKR 14,000", mode="Online/Onsite"),
        ]
    return render(request, "core/courses.html", {"courses": courses})

def register(request):
    courses = Course.objects.all()
    if not courses:
        courses = [
            Course(id=1, title="Graphics Designing"),
            Course(id=2, title="Python Programming"),
        ]
    if request.method == "POST":
        # Validate captcha
        captcha_key = request.POST.get('captcha_0')
        captcha_value = request.POST.get('captcha_1')
        if not captcha_key or not captcha_value:
            messages.error(request, "Please complete the security verification.")
            return render(request, "core/register.html", {"courses": courses})
        
        # Simple math captcha validation
        if captcha_key == "simple_math" and captcha_value.strip() != "5":
            messages.error(request, "Incorrect answer. Please try again.")
            return render(request, "core/register.html", {"courses": courses})
        
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        session_pref = request.POST.get("session_pref")
        registered_courses = request.POST.getlist("registered_courses")
        profile_pic = request.FILES.get("profile_pic")
        password = request.POST.get("password")
        token = str(uuid.uuid4())
        student = Student(
            name=name,
            email=email,
            phone=phone,
            session_pref=session_pref or "Online",
            profile_pic=profile_pic,
            email_verification_token=token,
            is_verified=False
        )
        student.set_password(password)
        student.save()
        if registered_courses:
            student.registered_courses.set(Course.objects.filter(id__in=registered_courses))
        # Log registration
        ActivityLog.objects.create(student=student, action="Registration", details="Registered with email {}".format(student.email))
        # Send verification email
        verify_url = request.build_absolute_uri(f"/student/verify-email/{token}/")
        try:
            send_mail(
                subject="AlkeaTech Email Verification",
                message=f"""Welcome to AlkeaTech!

Thank you for registering with us. To complete your registration, please click the link below to verify your email address:

{verify_url}

If you didn't create this account, please ignore this email.

Best regards,
AlkeaTech Team""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                fail_silently=False,
            )
            # Log successful email sending
            ActivityLog.objects.create(student=student, action="Email Sent", details=f"Verification email sent to {student.email}")
        except Exception as e:
            # Log email sending failure
            ActivityLog.objects.create(student=student, action="Email Failed", details=f"Failed to send verification email: {str(e)}")
            messages.warning(request, "Registration successful! However, there was an issue sending the verification email. Please contact support.")
            return redirect("register")
        
        # Create admin notification
        Notification.objects.create(message=f"New student registered: {student.name} ({student.email})")
        messages.success(request, "Registration successful! Please check your email to verify your account.")
        return redirect("register")
    return render(request, "core/register.html", {"courses": courses})

def student_dashboard(request):
    student_id = request.session.get('student_id')
    student = None
    messages_list = []
    activity_logs = []
    completions = []
    notifications = []
    if student_id:
        try:
            student = Student.objects.get(id=student_id)
            messages_list = Message.objects.filter(recipient=student).order_by('-created')
            # Mark unread messages as read
            Message.objects.filter(recipient=student, is_read=False).update(is_read=True)
            activity_logs = ActivityLog.objects.filter(student=student).order_by('-created')[:10]
            completions = CourseCompletion.objects.filter(student=student, certificate_pdf__isnull=False)
            from .models import StudentNotification
            notifications = StudentNotification.objects.filter(is_active=True).order_by('-created')
        except Student.DoesNotExist:
            student = None
    return render(request, "core/student_dashboard.html", {"student": student, "messages_list": messages_list, "activity_logs": activity_logs, "completions": completions, "notifications": notifications})

def student_login(request):
    error = None
    if request.method == "POST":
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        try:
            student = Student.objects.get(email=email, phone=phone)
            if not student.is_verified:
                error = "Please verify your email before logging in."
            elif student.check_password(password):
                request.session['student_id'] = student.id
                return redirect("student_dashboard")
            else:
                error = "Invalid password."
        except Student.DoesNotExist:
            error = "Invalid email or phone number."
    return render(request, "core/student_login.html", {"error": error})

def student_profile_edit(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('student_login')
    student = Student.objects.get(id=student_id)
    courses = Course.objects.all()
    if request.method == "POST":
        student.name = request.POST.get("name")
        student.email = request.POST.get("email")
        student.phone = request.POST.get("phone")
        student.session_pref = request.POST.get("session_pref")
        if request.FILES.get("profile_pic"):
            student.profile_pic = request.FILES.get("profile_pic")
        if request.POST.get("password"):
            student.set_password(request.POST.get("password"))
        registered_courses = request.POST.getlist("registered_courses")
        if registered_courses:
            student.registered_courses.set(Course.objects.filter(id__in=registered_courses))
        student.save()
        ActivityLog.objects.create(student=student, action="Profile Update", details="Profile updated.")
        messages.success(request, "Profile updated successfully.")
        return redirect('student_dashboard')
    return render(request, "core/student_profile_edit.html", {"student": student, "courses": courses})

def contact(request):
    offices = list(Office.objects.all())
    if not offices:
        offices = [
            Office(id=1, name="Main Campus", address="123 Main Road, Lahore, Pakistan"),
            Office(id=2, name="City Branch", address="45 City Center, Karachi, Pakistan"),
        ]
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        if name and email and message:
            send_mail(
                subject=f"Contact Form Submission from {name}",
                message=message + f"\n\nFrom: {name} <{email}>",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
            messages.success(request, "Your message has been sent. Thank you!")
            return redirect("contact")
    return render(request, "core/contact.html", {"offices": offices})

@staff_member_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('/admin/login/?next=/admin/dashboard/')
    from .models import Student, Course, Office, MenuItem
    stats = {
        'students': Student.objects.count(),
        'courses': Course.objects.count(),
        'offices': Office.objects.count(),
        'menus': MenuItem.objects.count(),
    }
    recent_students = Student.objects.order_by('-id')[:5]
    popular_courses = Course.objects.annotate(num_students=models.Count('student')).order_by('-num_students')[:3]
    bulk_email_msg = None
    if request.method == "POST" and 'bulk_email' in request.POST:
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        emails = list(Student.objects.filter(is_verified=True).values_list('email', flat=True))
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails,
            fail_silently=True,
        )
        bulk_email_msg = f"Bulk email sent to {len(emails)} students."
    # Analytics
    course_labels = []
    course_counts = []
    for course in Course.objects.all():
        course_labels.append(course.title)
        course_counts.append(course.student_set.count())
    verified_count = Student.objects.filter(is_verified=True).count()
    unverified_count = Student.objects.filter(is_verified=False).count()
    today = timezone.now().date()
    reg_dates = [(today - timedelta(days=i)) for i in range(29, -1, -1)]
    reg_counts = [Student.objects.filter(is_verified=True, id__isnull=False, 
        **{"created__date" if hasattr(Student, 'created') else "id__isnull": d} if hasattr(Student, 'created') else {}).count() for d in reg_dates]
    if not hasattr(Student, 'created'):
        reg_counts = []
        for d in reg_dates:
            next_day = d + timedelta(days=1)
            reg_counts.append(Student.objects.filter(is_verified=True, id__isnull=False, id__gte=0, id__lte=999999999, ).filter().count())
    # Notifications
    notifications = Notification.objects.filter(is_read=False).order_by('-created')
    if request.method == "POST" and 'mark_notifications_read' in request.POST:
        Notification.objects.filter(is_read=False).update(is_read=True)
    # Messaging
    message_sent = None
    if request.method == "POST" and 'send_message' in request.POST:
        recipient_id = request.POST.get('recipient_id')
        subject = request.POST.get('msg_subject')
        body = request.POST.get('msg_body')
        try:
            recipient = Student.objects.get(id=recipient_id)
            Message.objects.create(sender='admin', recipient=recipient, subject=subject, body=body)
            message_sent = f"Message sent to {recipient.name}."
        except Student.DoesNotExist:
            message_sent = "Student not found."
    # Student search/filter
    search_query = request.GET.get('search', '').strip()
    filter_course = request.GET.get('filter_course', '')
    filter_verified = request.GET.get('filter_verified', '')
    students = Student.objects.all()
    if search_query:
        students = students.filter(models.Q(name__icontains=search_query) | models.Q(email__icontains=search_query))
    if filter_course:
        students = students.filter(registered_courses__id=filter_course)
    if filter_verified:
        students = students.filter(is_verified=(filter_verified == 'verified'))
    students = students.distinct()
    courses_all = Course.objects.all()
    activity_logs = ActivityLog.objects.select_related('student').order_by('-created')[:10]
    return render(request, "core/admin_dashboard.html", {
        "stats": stats,
        "recent_students": recent_students,
        "popular_courses": popular_courses,
        "bulk_email_msg": bulk_email_msg,
        "course_labels": course_labels,
        "course_counts": course_counts,
        "verified_count": verified_count,
        "unverified_count": unverified_count,
        "reg_dates": [d.strftime('%Y-%m-%d') for d in reg_dates],
        "reg_counts": reg_counts,
        "notifications": notifications,
        "students": students,
        "courses_all": courses_all,
        "search_query": search_query,
        "filter_course": filter_course,
        "filter_verified": filter_verified,
        "message_sent": message_sent,
        "activity_logs": activity_logs,
    })

@staff_member_required
def admin_export_students(request):
    from .models import Student
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'Verified', 'Courses'])
    for s in Student.objects.all():
        courses = ', '.join([c.title for c in s.registered_courses.all()])
        writer.writerow([s.name, s.email, s.phone, s.is_verified, courses])
    return response

def student_password_reset_request(request):
    message = None
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            student = Student.objects.get(email=email)
            token = signer.sign(student.id)
            reset_url = request.build_absolute_uri(f"/student/password-reset-confirm/{token}/")
            send_mail(
                subject="AlkeaTech Password Reset",
                message=f"Click the link to reset your password: {reset_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                fail_silently=True,
            )
            message = "A password reset link has been sent to your email."
        except Student.DoesNotExist:
            message = "If the email exists, a reset link has been sent."
    return render(request, "core/student_password_reset_request.html", {"message": message})

def student_password_reset_confirm(request, token):
    error = None
    success = None
    try:
        student_id = signer.unsign(token, max_age=3600)
        student = Student.objects.get(id=student_id)
    except (BadSignature, SignatureExpired, Student.DoesNotExist):
        student = None
        error = "Invalid or expired reset link."
    if request.method == "POST" and student:
        password = request.POST.get("password")
        student.set_password(password)
        student.save()
        ActivityLog.objects.create(student=student, action="Password Reset", details="Password was reset.")
        success = "Your password has been reset. You can now log in."
    return render(request, "core/student_password_reset_confirm.html", {"error": error, "success": success})

def student_verify_email(request, token):
    msg = None
    try:
        student = Student.objects.get(email_verification_token=token)
        if not student.is_verified:
            student.is_verified = True
            student.email_verification_token = None
            student.save()
            msg = "Your email has been verified. You can now log in."
        else:
            msg = "Your email is already verified."
    except Student.DoesNotExist:
        msg = "Invalid or expired verification link."
    return render(request, "core/student_verify_email.html", {"msg": msg})

def student_certificate_download(request, course_id):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('student_login')
    try:
        completion = CourseCompletion.objects.get(student_id=student_id, course_id=course_id)
        if not completion.certificate_pdf:
            raise Http404
        return FileResponse(completion.certificate_pdf.open('rb'), as_attachment=True, filename=f"certificate_{completion.student.id}_{completion.course.id}.pdf")
    except CourseCompletion.DoesNotExist:
        raise Http404

def projects(request):
    projects = list(Project.objects.filter(is_active=True))
    if not projects:
        projects = [
            Project(id=1, name="E-Commerce Website", title="Modern Online Store", link="https://example.com", description="A full-featured e-commerce platform built with Django and React."),
            Project(id=2, name="AI Chatbot", title="Intelligent Assistant", link="https://example.com", description="Machine learning-powered chatbot for customer support."),
            Project(id=3, name="Mobile App", title="Cross-Platform Solution", link="https://example.com", description="React Native mobile application for iOS and Android."),
        ]
    return render(request, "core/projects.html", {"projects": projects})

def resend_verification_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        try:
            student = Student.objects.get(email=email, phone=phone)
            if student.is_verified:
                messages.info(request, "Your email is already verified.")
                return redirect("student_login")
            
            # Generate new token
            token = str(uuid.uuid4())
            student.email_verification_token = token
            student.save()
            
            # Send new verification email
            verify_url = request.build_absolute_uri(f"/student/verify-email/{token}/")
            try:
                send_mail(
                    subject="AlkeaTech Email Verification (Resent)",
                    message=f"""Hello {student.name},

You requested a new verification email. Please click the link below to verify your email address:

{verify_url}

If you didn't request this email, please ignore it.

Best regards,
AlkeaTech Team""",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[student.email],
                    fail_silently=False,
                )
                ActivityLog.objects.create(student=student, action="Email Resent", details=f"Verification email resent to {student.email}")
                messages.success(request, "Verification email has been resent. Please check your inbox.")
            except Exception as e:
                ActivityLog.objects.create(student=student, action="Email Resend Failed", details=f"Failed to resend verification email: {str(e)}")
                messages.error(request, "Failed to send verification email. Please try again later.")
            
        except Student.DoesNotExist:
            messages.error(request, "No account found with the provided email and phone number.")
    
    return render(request, "core/resend_verification.html")
