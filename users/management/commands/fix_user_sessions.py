"""
Management command to fix user sessions with invalid UUID values.
"""
import uuid
from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Fix user sessions with invalid UUID values'

    def handle(self, *args, **options):
        # Get all sessions
        sessions = Session.objects.all()
        fixed_count = 0
        deleted_count = 0

        for session in sessions:
            session_data = session.get_decoded()
            # Check if the session has a user ID
            if '_auth_user_id' in session_data:
                user_id = session_data['_auth_user_id']
                self.stdout.write(f"Found session with user ID: {user_id}")
                
                # Check if the user ID is not a valid UUID
                try:
                    uuid.UUID(user_id)
                    self.stdout.write(f"  - Valid UUID: {user_id}")
                except ValueError:
                    self.stdout.write(f"  - Invalid UUID: {user_id}")
                    # Delete the session
                    session.delete()
                    deleted_count += 1
                    self.stdout.write(f"  - Deleted session with invalid UUID: {user_id}")

        self.stdout.write(self.style.SUCCESS(f"Fixed {fixed_count} sessions, deleted {deleted_count} sessions"))
