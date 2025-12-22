people = [
    {
        'first_name': 'John',
        'last_name': 'Smith',
        'email': 'john.smith@email.com'
    },
    {
        'first_name': 'Sarah',
        'last_name': 'Johnson',
        'email': 'sarah.johnson@email.com'
    },
    {
        'first_name': 'Michael',
        'last_name': 'Davis',
        'email': 'michael.davis@email.com'
    },
    {
        'first_name': 'Emily',
        'last_name': 'Wilson',
        'email': 'emily.wilson@email.com'
    },
    {
        'first_name': 'David',
        'last_name': 'Brown',
        'email': 'david.brown@email.com'
    },
    {
        'first_name': 'Jessica',
        'last_name': 'Garcia',
        'email': 'jessica.garcia@email.com'
    },
    {
        'first_name': 'Christopher',
        'last_name': 'Martinez',
        'email': 'christopher.martinez@email.com'
    },
    {
        'first_name': 'Amanda',
        'last_name': 'Anderson',
        'email': 'amanda.anderson@email.com'
    },
    {
        'first_name': 'James',
        'last_name': 'Taylor',
        'email': 'james.taylor@email.com'
    },
    {
        'first_name': 'Ashley',
        'last_name': 'Thomas',
        'email': 'ashley.thomas@email.com'
    },
    {
        'first_name': 'Robert',
        'last_name': 'Jackson',
        'email': 'robert.jackson@email.com'
    },
    {
        'first_name': 'Michelle',
        'last_name': 'White',
        'email': 'michelle.white@email.com'
    },
    {
        'first_name': 'William',
        'last_name': 'Harris',
        'email': 'william.harris@email.com'
    },
    {
        'first_name': 'Nicole',
        'last_name': 'Clark',
        'email': 'nicole.clark@email.com'
    },
    {
        'first_name': 'Daniel',
        'last_name': 'Lewis',
        'email': 'daniel.lewis@email.com'
    }
]

def get_person():
    import random
    random_indx = random.randint(0, len(people)-1)
    return people[random_indx]