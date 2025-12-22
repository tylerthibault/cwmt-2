from flask import Blueprint, render_template, redirect, url_for
from src.dev.people import get_person
from src.models.user_folder import admins, instructors, students, superusers, users

# Create blueprint
seed_bp = Blueprint('seed', __name__)

@seed_bp.route('/seed/people')
def seed_people():
    seed_superusers(internal=True)
    # seed_admins()
    # seed_instructors()
    # seed_students()

    return redirect(url_for('auth.loginReg'))

@seed_bp.route('/seed/superuser')
@seed_bp.route('/seed/superuser/<int:amount>')
def seed_superusers(amount = 1, internal=False):
    for _ in range(amount):
        person = get_person()
        print(person)
        user = users.User.create(
            first_name=person['first_name'],
            last_name=person['last_name'],
            email=person['email'],
            password='Pass123!!'
            )
        superusers.Superuser.create(user_id=user.id)
    if not internal:
        return redirect(url_for('auth.loginReg'))
    return


@seed_bp.route('/seed/admin')
@seed_bp.route('/seed/admin/<int:amount>')
def seed_admins(amount = 1, internal=False):
    for _ in range(amount):
        person = get_person()
        print(person)
        user = users.User.create(
            first_name=person['first_name'],
            last_name=person['last_name'],
            email=person['email'],
            password='Pass123!!'
            )
        admins.Admin.create(user_id=user.id)
    if not internal:
        return redirect(url_for('auth.loginReg'))
    return  

@seed_bp.route('/seed/instructor')
@seed_bp.route('/seed/instructor/<int:amount>')
def seed_instructors(amount = 1, internal=False):
    for _ in range(amount):
        person = get_person()
        print(person)
        user = users.User.create(
            first_name=person['first_name'],
            last_name=person['last_name'],
            email=person['email'],
            password='Pass123!!'
            )
        instructors.Instructor.create(user_id=user.id)
    if not internal:
        return redirect(url_for('auth.loginReg'))
    return

@seed_bp.route('/seed/student')
@seed_bp.route('/seed/student/<int:amount>')
def seed_students(amount = 1, internal=False):
    for _ in range(amount):
        person = get_person()
        print(person)
        user = users.User.create(
            first_name=person['first_name'],
            last_name=person['last_name'],
            email=person['email'],
            password='Pass123!!'
            )
        students.Student.create(
            user_id=user.id,
            first_name=person['first_name'],
            last_name=person['last_name']
            )
    if not internal:
        return redirect(url_for('auth.loginReg'))
    return