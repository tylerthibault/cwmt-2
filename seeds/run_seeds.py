#!/usr/bin/env python
"""
Seed runner script for CWMT Flask Application

This script runs all seed files to populate the database with default data.
Can be run from command line or imported and used programmatically.

Usage:
    python seeds/run_seeds.py [--all|--roles|--users|--courses]
    
Examples:
    python seeds/run_seeds.py --all        # Run all seed files
    python seeds/run_seeds.py --roles      # Run only roles seed
    python seeds/run_seeds.py --users      # Run only users seed
    python seeds/run_seeds.py --courses    # Run only courses seed
"""
import sys
import argparse
from pathlib import Path

# Add project root to path to enable imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src import create_app
from seeds.seed_roles import seed_default_roles
from seeds.seed_users import seed_default_users
from seeds.seed_courses import seed_default_course_templates
from seeds.seed_students import seed_all_students
from seeds.seed_email_settings import seed_email_settings
from seeds.seed_email_actions import seed_email_actions
from seeds.seed_email_templates import seed_email_templates


def run_all_seeds(app):
    """
    Run all seed files in the correct order.
    
    Order matters:
    1. Roles must be created before users (users need roles)
    2. Users can be created after roles
    3. Courses can be created independently
    
    Args:
        app: Flask application instance
    """
    print("\n" + "="*60)
    print("Starting database seeding process...")
    print("="*60 + "\n")
    
    # Seed roles first (required for users)
    print("→ Seeding roles...")
    seed_default_roles(app)
    print("✓ Roles seeding completed\n")
    
    # Seed users (requires roles to exist)
    print("→ Seeding users...")
    seed_default_users(app)
    print("✓ Users seeding completed\n")
    
    # Seed email settings
    print("→ Seeding email settings...")
    seed_email_settings(app)
    print("✓ Email settings seeding completed\n")
    
    # Seed email actions
    print("→ Seeding email actions...")
    seed_email_actions(app)
    print("✓ Email actions seeding completed\n")
    
    # Seed email templates
    print("→ Seeding email templates...")
    seed_email_templates(app)
    print("✓ Email templates seeding completed\n")
    
    # Seed courses
    print("→ Seeding courses...")
    seed_default_course_templates(app)
    print("✓ Courses seeding completed\n")
    
    # Seed students and enrollments
    print("→ Seeding students...")
    seed_all_students(app)
    print("✓ Students seeding completed\n")
    
    print("="*60)
    print("Database seeding completed successfully!")
    print("="*60 + "\n")


def run_roles_seed(app):
    """Run only the roles seed file"""
    print("\n→ Seeding roles...")
    seed_default_roles(app)
    print("✓ Roles seeding completed\n")


def run_users_seed(app):
    """Run only the users seed file"""
    print("\n→ Seeding users...")
    seed_default_users(app)
    print("✓ Users seeding completed\n")


def run_courses_seed(app):
    """Run only the courses seed file"""
    print("\n→ Seeding courses...")
    seed_default_course_templates(app)
    print("✓ Courses seeding completed\n")


def run_students_seed(app):
    """Run only the students seed file"""
    print("\n→ Seeding students...")
    seed_all_students(app)
    print("✓ Students seeding completed\n")


def run_email_settings_seed(app):
    """Run only the email settings seed file"""
    print("\n→ Seeding email settings...")
    seed_email_settings(app)
    print("✓ Email settings seeding completed\n")


def run_email_actions_seed(app):
    """Run only the email actions seed file"""
    print("\n→ Seeding email actions...")
    seed_email_actions(app)
    print("✓ Email actions seeding completed\n")


def main():
    """Main entry point for command line usage"""
    parser = argparse.ArgumentParser(
        description='Run database seed files for CWMT application',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python seeds/run_seeds.py --all        # Run all seed files
  python seeds/run_seeds.py --roles      # Run only roles seed
  python seeds/run_seeds.py --users      # Run only users seed
  python seeds/run_seeds.py --courses    # Run only courses seed
  
Note: Running --users requires roles to exist first.
      Use --all to ensure proper order.
        """
    )
    
    # Create mutually exclusive group for seed options
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true', 
                      help='Run all seed files (recommended)')
    group.add_argument('--roles', action='store_true',
                      help='Run only roles seed')
    group.add_argument('--users', action='store_true',
                      help='Run only users seed (requires roles to exist)')
    group.add_argument('--email', action='store_true',
                      help='Run only email settings seed')
    group.add_argument('--email-actions', action='store_true',
                      help='Run only email actions seed')
    group.add_argument('--courses', action='store_true',
                      help='Run only courses seed')
    group.add_argument('--students', action='store_true',
                      help='Run only students seed (requires users and courses to exist)')
    
    args = parser.parse_args()
    
    # Create Flask app and push context
    app = create_app()
    
    with app.app_context():
        try:
            if args.all:
                run_all_seeds(app)
            elif args.roles:
                run_roles_seed(app)
            elif args.users:
                run_users_seed(app)
            elif args.email:
                run_email_settings_seed(app)
            elif args.email_actions:
                run_email_actions_seed(app)
            elif args.courses:
                run_courses_seed(app)
            elif args.students:
                run_students_seed(app)
                
            print("✅ Seeding process completed successfully!\n")
            return 0
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {str(e)}\n")
            import traceback
            traceback.print_exc()
            return 1


if __name__ == '__main__':
    sys.exit(main())
