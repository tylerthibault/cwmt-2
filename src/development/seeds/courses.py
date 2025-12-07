from datetime import datetime, timedelta
from src.models import db
from src.models.courses_model import CourseTemplate, Course
from src.models.user import User
from src.models.payable_item_model import PayableItemTemplate, CourseTemplatePayableItem


def seed_courses(app):
    """
    Seed course templates and create scheduled courses for testing.
    Creates courses starting from today for the next few weeks.
    """
    with app.app_context():
        # Get instructors for course assignment
        instructor1 = User.query.filter_by(email='instructor1@cwmt.com').first()
        instructor2 = User.query.filter_by(email='instructor2@cwmt.com').first()
        
        if not instructor1 or not instructor2:
            print("⚠ Instructors not found. Please run user seeds first.")
            return
        
        # Define course templates
        templates_data = [
            {
                'name': 'Basic Rider Course (BRC)',
                'description': 'The Basic Rider Course is a comprehensive motorcycle training program for beginners.',
                'duration_days': 3,
                'max_students': 12,
                'experience_level': 'beginner',
                'tuition_price': 350.00,
                'is_active': True
            },
            {
                'name': 'Advanced Rider Course',
                'description': 'Advanced techniques for experienced riders looking to improve their skills.',
                'duration_days': 2,
                'max_students': 8,
                'experience_level': 'advanced',
                'tuition_price': 275.00,
                'is_active': True
            },
            {
                'name': 'Weekend Warrior Course',
                'description': 'Intensive weekend course covering essential riding skills.',
                'duration_days': 2,
                'max_students': 10,
                'experience_level': 'intermediate',
                'tuition_price': 299.00,
                'is_active': True
            }
        ]
        
        # Define payable items for courses
        payable_items_data = [
            {
                'name': 'Tuition',
                'description': 'Course tuition fee',
                'item_type': 'tuition',
                'base_price': 0.00  # Will be overridden per course
            },
            {
                'name': 'Materials Fee',
                'description': 'Course materials and handbook',
                'item_type': 'misc',
                'base_price': 25.00
            },
            {
                'name': 'Bike Rental',
                'description': 'Motorcycle rental for the duration of the course',
                'item_type': 'rental',
                'base_price': 50.00
            }
        ]
        
        # Create payable item templates if they don't exist
        payable_templates = {}
        for item_data in payable_items_data:
            existing = PayableItemTemplate.query.filter_by(name=item_data['name']).first()
            if existing:
                payable_templates[item_data['name']] = existing
                print(f"⚠ Payable item template already exists: {item_data['name']}")
            else:
                template = PayableItemTemplate(
                    name=item_data['name'],
                    description=item_data['description'],
                    item_type=item_data['item_type'],
                    base_price=item_data['base_price'],
                    is_active=True,
                    is_required=(item_data['item_type'] == 'tuition')
                )
                db.session.add(template)
                db.session.flush()
                payable_templates[item_data['name']] = template
                print(f"✓ Created payable item template: {item_data['name']}")
        
        db.session.commit()
        
        # Create course templates
        created_templates = []
        for template_data in templates_data:
            # Check if template already exists
            existing = CourseTemplate.query.filter_by(name=template_data['name']).first()
            if existing:
                created_templates.append(existing)
                print(f"⚠ Course template already exists: {template_data['name']}")
                continue
            
            # Create course template
            template = CourseTemplate(
                name=template_data['name'],
                description=template_data['description'],
                duration_days=template_data['duration_days'],
                max_students=template_data['max_students'],
                experience_level=template_data['experience_level'],
                is_active=template_data['is_active']
            )
            db.session.add(template)
            db.session.flush()
            
            # Add payable items to template
            # Tuition - required
            tuition_item = CourseTemplatePayableItem(
                course_template_id=template.id,
                payable_item_template_id=payable_templates['Tuition'].id,
                is_required=True,
                display_order=1
            )
            db.session.add(tuition_item)
            
            # Materials Fee - required
            materials_item = CourseTemplatePayableItem(
                course_template_id=template.id,
                payable_item_template_id=payable_templates['Materials Fee'].id,
                is_required=True,
                display_order=2
            )
            db.session.add(materials_item)
            
            # Bike Rental - optional
            rental_item = CourseTemplatePayableItem(
                course_template_id=template.id,
                payable_item_template_id=payable_templates['Bike Rental'].id,
                is_required=False,
                display_order=3
            )
            db.session.add(rental_item)
            
            created_templates.append(template)
            print(f"✓ Created course template: {template_data['name']}")
        
        db.session.commit()
        
        # Create scheduled courses
        today = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        
        # Create courses for the next 4 weeks
        courses_to_create = [
            # Week 1 - This week
            {
                'template': created_templates[0],  # BRC
                'start_date': today + timedelta(days=2),
                'instructor': instructor1,
                'location': 'Main Training Facility'
            },
            {
                'template': created_templates[1],  # Advanced
                'start_date': today + timedelta(days=5),
                'instructor': instructor2,
                'location': 'Advanced Track'
            },
            # Week 2
            {
                'template': created_templates[2],  # Weekend Warrior
                'start_date': today + timedelta(days=7),
                'instructor': instructor1,
                'location': 'Main Training Facility'
            },
            {
                'template': created_templates[0],  # BRC
                'start_date': today + timedelta(days=9),
                'instructor': instructor2,
                'location': 'South Campus'
            },
            # Week 3
            {
                'template': created_templates[1],  # Advanced
                'start_date': today + timedelta(days=14),
                'instructor': instructor1,
                'location': 'Advanced Track'
            },
            {
                'template': created_templates[0],  # BRC
                'start_date': today + timedelta(days=16),
                'instructor': instructor2,
                'location': 'Main Training Facility'
            },
            # Week 4
            {
                'template': created_templates[2],  # Weekend Warrior
                'start_date': today + timedelta(days=21),
                'instructor': instructor1,
                'location': 'Main Training Facility'
            },
            {
                'template': created_templates[0],  # BRC
                'start_date': today + timedelta(days=23),
                'instructor': instructor2,
                'location': 'North Campus'
            }
        ]
        
        for course_data in courses_to_create:
            template = course_data['template']
            start_date = course_data['start_date']
            end_date = start_date + timedelta(days=template.duration_days)
            
            # Check if course already exists at this time
            existing = Course.query.filter_by(
                template_id=template.id,
                start_date=start_date,
                location=course_data['location']
            ).first()
            
            if existing:
                print(f"⚠ Course already exists: {template.name} on {start_date.strftime('%Y-%m-%d')}")
                continue
            
            # Create course
            course = Course(
                template_id=template.id,
                instructor_id=course_data['instructor'].id,
                start_date=start_date,
                end_date=end_date,
                location=course_data['location'],
                status='scheduled',
                current_students=0
            )
            db.session.add(course)
            print(f"✓ Created course: {template.name} starting {start_date.strftime('%Y-%m-%d')} at {course_data['location']}")
        
        db.session.commit()
        print(f"\n✓ Course seeding complete!")
        print(f"  - {len(created_templates)} course templates")
        print(f"  - {len(courses_to_create)} scheduled courses")
