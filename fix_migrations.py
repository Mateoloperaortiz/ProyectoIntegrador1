#!/usr/bin/env python
"""
Script to fix the inconsistent migration history in the Django database.
This script adds the missing catalog.0002_initial migration record to the database.
"""
import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inspireIA.settings')
django.setup()

# Now we can import Django models
from django.db import connection

def fix_migration_history():
    """
    Fix the inconsistent migration history by adding the missing catalog.0002_initial
    migration record to the django_migrations table.
    """
    with connection.cursor() as cursor:
        # Check if catalog.0002_initial already exists
        cursor.execute(
            "SELECT * FROM django_migrations WHERE app = 'catalog' AND name = '0002_initial'"
        )
        if cursor.fetchone():
            print("Migration catalog.0002_initial already exists in the database.")
            return

        # Get the applied_at timestamp from the catalog.0001_initial migration
        cursor.execute(
            "SELECT applied FROM django_migrations WHERE app = 'catalog' AND name = '0001_initial'"
        )
        result = cursor.fetchone()
        if not result:
            print("Error: catalog.0001_initial migration not found in the database.")
            return
        
        applied_timestamp = result[0]
        
        # Insert the missing migration record
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
            ['catalog', '0002_initial', applied_timestamp]
        )
        
        print("Successfully added catalog.0002_initial migration record to the database.")
        print("You should now be able to run 'python manage.py makemigrations' and 'python manage.py migrate' without errors.")

if __name__ == "__main__":
    fix_migration_history()
