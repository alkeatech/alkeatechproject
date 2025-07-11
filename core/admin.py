from django.contrib import admin
from .models import Course, Office, Student, MenuItem, Notification, Message, ActivityLog, CourseCompletion, StudentNotification, Project
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile
import io
from django.core.mail import EmailMessage

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration', 'fee', 'mode')

@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'session_pref')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('session_pref', 'education', 'registered_courses')

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('label', 'link')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('message', 'created', 'is_read')
    list_filter = ('is_read',)
    ordering = ('-created',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'recipient', 'sender', 'created', 'is_read')
    list_filter = ('is_read', 'recipient')
    search_fields = ('subject', 'body', 'recipient__name', 'recipient__email')
    ordering = ('-created',)

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('student', 'action', 'created')
    search_fields = ('student__name', 'action', 'details')
    ordering = ('-created',)

@admin.register(CourseCompletion)
class CourseCompletionAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'completed_on', 'certificate_pdf')
    search_fields = ('student__name', 'course__title')
    list_filter = ('course',)
    ordering = ('-completed_on',)
    actions = ['generate_certificate', 'email_certificate']

    def generate_certificate(self, request, queryset):
        for obj in queryset:
            if obj.certificate_pdf:
                continue
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            c.setFont('Helvetica-Bold', 24)
            c.drawCentredString(width/2, height-100, 'Certificate of Completion')
            c.setFont('Helvetica', 16)
            c.drawCentredString(width/2, height-160, f"This is to certify that")
            c.setFont('Helvetica-Bold', 20)
            c.drawCentredString(width/2, height-200, obj.student.name)
            c.setFont('Helvetica', 16)
            c.drawCentredString(width/2, height-240, f"has successfully completed the course")
            c.setFont('Helvetica-Bold', 18)
            c.drawCentredString(width/2, height-280, obj.course.title)
            c.setFont('Helvetica', 14)
            c.drawCentredString(width/2, height-320, f"Date: {obj.completed_on}")
            c.setFont('Helvetica', 12)
            c.drawCentredString(width/2, height-360, 'AlkeaTech')
            c.showPage()
            c.save()
            buffer.seek(0)
            obj.certificate_pdf.save(f"certificate_{obj.student.id}_{obj.course.id}.pdf", ContentFile(buffer.read()))
            obj.save()
        self.message_user(request, "Certificates generated.")
    generate_certificate.short_description = "Generate PDF certificate for selected completions"

    def email_certificate(self, request, queryset):
        for obj in queryset:
            if obj.certificate_pdf:
                email = EmailMessage(
                    subject=f"Your Certificate for {obj.course.title}",
                    body=f"Dear {obj.student.name},\n\nAttached is your certificate for completing {obj.course.title} at AlkeaTech.",
                    from_email=None,
                    to=[obj.student.email],
                )
                email.attach(obj.certificate_pdf.name, obj.certificate_pdf.read(), 'application/pdf')
                email.send(fail_silently=True)
        self.message_user(request, "Certificates emailed to students.")
    email_certificate.short_description = "Email certificate PDF to student(s)"

@admin.register(StudentNotification)
class StudentNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'created', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'body')
    ordering = ('-created',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'link', 'is_active', 'created']
    list_filter = ['is_active', 'created']
    search_fields = ['name', 'title', 'description']
    list_editable = ['is_active']
    readonly_fields = ['created', 'updated']
