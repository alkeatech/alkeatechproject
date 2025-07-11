from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.

class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='courses/')
    duration = models.CharField(max_length=50)
    fee = models.CharField(max_length=50)
    mode = models.CharField(
        max_length=20,
        choices=[('Online', 'Online'), ('Onsite', 'Onsite'), ('Online/Onsite', 'Online/Onsite')]
    )

    def __str__(self):
        return self.title

class Office(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Student(models.Model):
    EDUCATION_LEVELS = [
        ('Master', 'Master'),
        ('Bachelor', 'Bachelor'),
        ('Intermediate', 'Intermediate'),
        ('Matric', 'Matric'),
        ('Other', 'Other'),
    ]
    profile_pic = models.ImageField(upload_to='students/', blank=True, null=True)
    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.CharField(max_length=255, blank=True)
    father_phone = models.CharField(max_length=20, blank=True)
    education = models.CharField(max_length=20, choices=EDUCATION_LEVELS, blank=True)
    last_degree = models.CharField(max_length=100, blank=True)
    registered_courses = models.ManyToManyField(Course)
    session_pref = models.CharField(max_length=10, choices=[('Online', 'Online'), ('Onsite', 'Onsite')])
    password = models.CharField(max_length=128)
    is_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=128, blank=True, null=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    label = models.CharField(max_length=50)
    link = models.CharField(max_length=255)

    def __str__(self):
        return self.label

class Notification(models.Model):
    message = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message

class Message(models.Model):
    sender = models.CharField(max_length=100, default='admin')  # 'admin' or student name/email
    recipient = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='messages')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"To {self.recipient.name}: {self.subject}"

class ActivityLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name}: {self.action} at {self.created}"

class CourseCompletion(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='completed_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed_on = models.DateField(auto_now_add=True)
    certificate_pdf = models.FileField(upload_to='certificates/', blank=True, null=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.name} - {self.course.title}"

class StudentNotification(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Project(models.Model):
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    link = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created']
