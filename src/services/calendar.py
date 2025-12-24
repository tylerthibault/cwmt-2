



from datetime import timedelta


def format_course_instances_for_calendar(instances):
    """
    Helper function to format course instances for calendar display.
    
    Args:
        instances: List of CourseInstance objects
        
    Returns:
        List of event dictionaries formatted for calendar
    """
    events = []
    for instance in instances:
        # Calculate end date from start date + duration
        end_date = instance.start_date + timedelta(days=instance.duration_days - 1) if instance.start_date and instance.duration_days else None
        
        # Get instructor names
        instructors_list = []
        c1_instructor_name = None
        c2_instructor_name = None
        
        if instance.c1_instructor and instance.c1_instructor.user:
            c1_instructor_name = instance.c1_instructor.user.full_name
            instructors_list.append(c1_instructor_name)
        if instance.c2_instructor and instance.c2_instructor.user:
            c2_instructor_name = instance.c2_instructor.user.full_name
            instructors_list.append(c2_instructor_name)
        instructor_text = ', '.join(instructors_list) if instructors_list else 'Unassigned'
        
        events.append({
            'id': instance.id,
            'title': instance.course_template.name if instance.course_template else 'Unknown Course',
            'start': instance.start_date.isoformat() if instance.start_date else None,
            'end': end_date.isoformat() if end_date else None,
            'location': instance.location,
            'instructor': instructor_text,
            'c1_instructor': c1_instructor_name,
            'c2_instructor': c2_instructor_name,
            'c1_instructor_id': instance.c1_instructor_id,
            'c2_instructor_id': instance.c2_instructor_id,
            'status': instance.status,
            'enrollment': f"0/{instance.max_students}"  # No current_enrollment tracking yet
        })
    
    return events