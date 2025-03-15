#!/usr/bin/env python3
"""
Script to create migrations for model refactoring.

This script creates migrations to fix model duplication issues by:
1. Adding inheritance from UUIDModel and TimeStampedModel
2. Standardizing user references to use settings.AUTH_USER_MODEL
"""

import os
import subprocess
import sys

MAKEMIGRATIONS_CMD = "python manage.py makemigrations"
MIGRATE_CMD = "python manage.py migrate"

APPS_WITH_MODELS = [
    "catalog",
    "interaction",
]

def run_command(command, check=True):
    """Run a shell command and print its output."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    print("STDOUT:")
    print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if check and result.returncode != 0:
        print(f"Command failed with return code {result.returncode}")
        sys.exit(1)
    
    return result

def create_migrations():
    """Create migrations for the model refactoring."""
    for app in APPS_WITH_MODELS:
        print(f"\n--- Creating migrations for {app} ---")
        run_command(f"{MAKEMIGRATIONS_CMD} {app}")

def apply_migrations():
    """Apply migrations for the model refactoring."""
    print("\n--- Applying migrations ---")
    run_command(MIGRATE_CMD)

def generate_model_metadata():
    """Generate model metadata to verify the migrations."""
    print("\n--- Generating model metadata ---")
    for app in APPS_WITH_MODELS:
        run_command(f"python manage.py inspectdb {app} > {app}_models_after.py", check=False)
        print(f"Model metadata written to {app}_models_after.py")

def verify_migrations():
    """Verify that the migrations were applied correctly."""
    print("\n--- Verifying migrations ---")
    run_command("python manage.py check", check=True)
    # Check for any model errors
    run_command("python manage.py validate", check=False)

def main():
    """Main function."""
    # Check if Django is set up correctly
    print("Checking Django setup...")
    run_command("python manage.py check")
    
    # Create migrations
    print("\nCreating migrations for model refactoring...")
    create_migrations()
    
    # Ask for confirmation before applying migrations
    confirm = input("\nReview the migrations above. Apply migrations? [y/N] ")
    if confirm.lower() != 'y':
        print("Migration canceled.")
        return 1
    
    # Apply migrations
    apply_migrations()
    
    # Verify migrations
    verify_migrations()
    
    # Generate model metadata for verification
    generate_model_metadata()
    
    print("\nModel refactoring complete!")
    print("Inheritance from UUIDModel and TimeStampedModel has been applied.")
    print("User references have been standardized to settings.AUTH_USER_MODEL.")
    print("\nNotes:")
    print("1. Review the generated model metadata files to verify the changes.")
    print("2. Run tests to ensure everything works as expected.")
    print("3. Commit the migrations with the model changes.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())