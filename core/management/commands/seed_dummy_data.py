from django.core.management.base import BaseCommand
from core.models import Course, Office, StudentNotification

class Command(BaseCommand):
    help = 'Seed dummy data for homepage display'

    def handle(self, *args, **kwargs):
        # Courses
        courses = [
            {
                'title': 'Graphics Designing',
                'description': 'Learn Photoshop, Illustrator, and more.',
                'image': '',
                'duration': '3 Months',
                'fee': 'PKR 15,000',
                'mode': 'Online/Onsite',
            },
            {
                'title': 'Python Programming',
                'description': 'Python from basics to advanced.',
                'image': '',
                'duration': '2.5 Months',
                'fee': 'PKR 14,000',
                'mode': 'Online/Onsite',
            },
            {
                'title': 'Web Development',
                'description': 'HTML, CSS, JS, Django, React.',
                'image': '',
                'duration': '4 Months',
                'fee': 'PKR 18,000',
                'mode': 'Online/Onsite',
            },
            {
                'title': 'AI & Machine Learning',
                'description': 'Intro to AI, ML, and data science.',
                'image': '',
                'duration': '3 Months',
                'fee': 'PKR 20,000',
                'mode': 'Online/Onsite',
            },
        ]
        for c in courses:
            Course.objects.get_or_create(title=c['title'], defaults=c)

        # Offices
        offices = [
            {'name': 'Main Campus', 'address': '123 Main Road, Lahore, Pakistan'},
            {'name': 'City Branch', 'address': '45 City Center, Karachi, Pakistan'},
        ]
        for o in offices:
            Office.objects.get_or_create(name=o['name'], defaults=o)

        # Notifications
        notifications = [
            {'title': 'Admissions Open!', 'body': 'Register now for new batches starting soon.', 'is_active': True},
            {'title': 'Scholarships Available', 'body': 'Apply for merit-based scholarships.', 'is_active': True},
        ]
        for n in notifications:
            StudentNotification.objects.get_or_create(title=n['title'], defaults=n)

        self.stdout.write(self.style.SUCCESS('Dummy data seeded successfully.')) 