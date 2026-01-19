# Diff Details

Date : 2026-01-19 11:26:09

Directory c:\\Users\\tyler\\Documents\\Coding\\Flask\\cwmt

Total : 119 files,  19947 codes, 1806 comments, 3544 blanks, all 25297 lines

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [Dockerfile](/Dockerfile) | Docker | 0 | 2 | 1 | 3 |
| [docs/DEPLOYMENT\_MIGRATION.md](/docs/DEPLOYMENT_MIGRATION.md) | Markdown | 112 | 0 | 34 | 146 |
| [docs/EMAIL\_ENCRYPTION\_FIX.md](/docs/EMAIL_ENCRYPTION_FIX.md) | Markdown | 80 | 0 | 18 | 98 |
| [docs/todo/flask\_mail/email-purposes.md](/docs/todo/flask_mail/email-purposes.md) | Markdown | 467 | 0 | 82 | 549 |
| [docs/todo/flask\_mail/sql-tables.md](/docs/todo/flask_mail/sql-tables.md) | Markdown | 245 | 0 | 66 | 311 |
| [docs/todo/flask\_mail/user-stories.md](/docs/todo/flask_mail/user-stories.md) | Markdown | 185 | 0 | 53 | 238 |
| [docs/todo/frontend/style\_description.md](/docs/todo/frontend/style_description.md) | Markdown | 219 | 0 | 61 | 280 |
| [fix\_column.sql](/fix_column.sql) | MS SQL | 3 | 4 | 3 | 10 |
| [migrations/alembic.ini](/migrations/alembic.ini) | Ini | 38 | 0 | 13 | 51 |
| [migrations/env.py](/migrations/env.py) | Python | 54 | 34 | 26 | 114 |
| [migrations/versions/a1b2c3d4e5f6\_rename\_mail\_password\_hash\_to\_encrypted.py](/migrations/versions/a1b2c3d4e5f6_rename_mail_password_hash_to_encrypted.py) | Python | 20 | 15 | 7 | 42 |
| [migrations/versions/bdb5548afc4c\_initial\_migration\_with\_all\_tables.py](/migrations/versions/bdb5548afc4c_initial_migration_with_all_tables.py) | Python | 292 | 12 | 29 | 333 |
| [requirements.txt](/requirements.txt) | pip requirements | 3 | 0 | 0 | 3 |
| [src/\_\_init\_\_ copy.py](/src/__init__%20copy.py) | Python | 91 | 21 | 41 | 153 |
| [src/\_\_init\_\_.py](/src/__init__.py) | Python | 70 | 22 | 22 | 114 |
| [src/controllers/announcements.py](/src/controllers/announcements.py) | Python | 108 | 13 | 35 | 156 |
| [src/controllers/courses/course\_instances.py](/src/controllers/courses/course_instances.py) | Python | -30 | -9 | -8 | -47 |
| [src/controllers/courses/course\_template.py](/src/controllers/courses/course_template.py) | Python | -33 | -8 | -7 | -48 |
| [src/controllers/courses/payable\_template.py](/src/controllers/courses/payable_template.py) | Python | -12 | 1 | 2 | -9 |
| [src/controllers/enrollment\_management.py](/src/controllers/enrollment_management.py) | Python | 142 | 18 | 45 | 205 |
| [src/controllers/flask\_mail/mail\_routes.py](/src/controllers/flask_mail/mail_routes.py) | Python | 167 | 16 | 38 | 221 |
| [src/controllers/flask\_mail/seed\_templates.py](/src/controllers/flask_mail/seed_templates.py) | Python | 320 | 11 | 68 | 399 |
| [src/controllers/payments/payment\_management.py](/src/controllers/payments/payment_management.py) | Python | 74 | 14 | 26 | 114 |
| [src/controllers/payments/stripe\_payments.py](/src/controllers/payments/stripe_payments.py) | Python | 23 | 1 | 1 | 25 |
| [src/controllers/routes.py](/src/controllers/routes.py) | Python | 2 | -1 | 5 | 6 |
| [src/controllers/users/admin.py](/src/controllers/users/admin.py) | Python | -283 | -49 | -70 | -402 |
| [src/controllers/users/auth.py](/src/controllers/users/auth.py) | Python | 127 | 19 | 23 | 169 |
| [src/controllers/users/instructor.py](/src/controllers/users/instructor.py) | Python | -26 | -5 | -9 | -40 |
| [src/controllers/users/student.py](/src/controllers/users/student.py) | Python | 149 | 24 | 41 | 214 |
| [src/controllers/users/superuser.py](/src/controllers/users/superuser.py) | Python | 83 | 4 | 22 | 109 |
| [src/dev/database.py](/src/dev/database.py) | Python | 116 | 16 | 20 | 152 |
| [src/models/announcements.py](/src/models/announcements.py) | Python | 34 | 13 | 17 | 64 |
| [src/models/app\_settings.py](/src/models/app_settings.py) | Python | 152 | 122 | 41 | 315 |
| [src/models/flask\_mail/email\_templates.py](/src/models/flask_mail/email_templates.py) | Python | 112 | 107 | 33 | 252 |
| [src/models/logs.py](/src/models/logs.py) | Python | 231 | 184 | 50 | 465 |
| [src/models/user\_folder/students.py](/src/models/user_folder/students.py) | Python | -4 | -1 | -1 | -6 |
| [src/services/admin\_service.py](/src/services/admin_service.py) | Python | 201 | 11 | 61 | 273 |
| [src/services/announcement\_service.py](/src/services/announcement_service.py) | Python | 100 | 59 | 31 | 190 |
| [src/services/course\_instance\_service.py](/src/services/course_instance_service.py) | Python | 134 | 81 | 29 | 244 |
| [src/services/course\_template\_service.py](/src/services/course_template_service.py) | Python | 167 | 84 | 35 | 286 |
| [src/services/database\_manipulation.py](/src/services/database_manipulation.py) | Python | 46 | 11 | 19 | 76 |
| [src/services/enrollment\_service.py](/src/services/enrollment_service.py) | Python | 228 | 110 | 59 | 397 |
| [src/services/flask\_mail/email\_config.py](/src/services/flask_mail/email_config.py) | Python | 100 | 8 | 8 | 116 |
| [src/services/flask\_mail/email\_service.py](/src/services/flask_mail/email_service.py) | Python | 98 | 57 | 30 | 185 |
| [src/services/flask\_mail/email\_template\_service.py](/src/services/flask_mail/email_template_service.py) | Python | 120 | 132 | 47 | 299 |
| [src/services/instructor\_service.py](/src/services/instructor_service.py) | Python | 38 | 35 | 17 | 90 |
| [src/services/payable\_template\_service.py](/src/services/payable_template_service.py) | Python | 40 | 52 | 19 | 111 |
| [src/services/payment\_service.py](/src/services/payment_service.py) | Python | 142 | 70 | 36 | 248 |
| [src/services/superuser\_service.py](/src/services/superuser_service.py) | Python | 197 | 110 | 49 | 356 |
| [src/static/css/bootstrap-overide.css](/src/static/css/bootstrap-overide.css) | PostCSS | 640 | 29 | 151 | 820 |
| [src/static/css/components/animations.css](/src/static/css/components/animations.css) | PostCSS | 223 | 16 | 53 | 292 |
| [src/static/css/components/buttons-badges.css](/src/static/css/components/buttons-badges.css) | PostCSS | 112 | 4 | 25 | 141 |
| [src/static/css/components/dashboard.css](/src/static/css/components/dashboard.css) | PostCSS | 247 | 14 | 47 | 308 |
| [src/static/css/components/navbar.css](/src/static/css/components/navbar.css) | PostCSS | 210 | 10 | 33 | 253 |
| [src/static/css/components/sticky-stack.css](/src/static/css/components/sticky-stack.css) | PostCSS | 48 | 11 | 11 | 70 |
| [src/static/css/components/student-dashboard.css](/src/static/css/components/student-dashboard.css) | PostCSS | 483 | 7 | 95 | 585 |
| [src/static/css/components/student-details.css](/src/static/css/components/student-details.css) | PostCSS | 303 | 8 | 60 | 371 |
| [src/static/css/components/student-enrollments.css](/src/static/css/components/student-enrollments.css) | PostCSS | 290 | 11 | 51 | 352 |
| [src/static/css/components/student-navbar.css](/src/static/css/components/student-navbar.css) | PostCSS | 162 | 15 | 33 | 210 |
| [src/static/css/email-forms.css](/src/static/css/email-forms.css) | PostCSS | 131 | 9 | 24 | 164 |
| [src/static/css/email-management.css](/src/static/css/email-management.css) | PostCSS | 161 | 9 | 36 | 206 |
| [src/static/css/main.css](/src/static/css/main.css) | PostCSS | 164 | 21 | 24 | 209 |
| [src/static/css/pages/landing.css](/src/static/css/pages/landing.css) | PostCSS | 690 | 30 | 134 | 854 |
| [src/static/css/utilities.css](/src/static/css/utilities.css) | PostCSS | 171 | 17 | 42 | 230 |
| [src/static/js/components/calendar/calendar-admin.js](/src/static/js/components/calendar/calendar-admin.js) | JavaScript | 5 | -3 | -2 | 0 |
| [src/static/js/main.js](/src/static/js/main.js) | JavaScript | 18 | 2 | 3 | 23 |
| [src/templates/bases/nonstudents.html](/src/templates/bases/nonstudents.html) | HTML | 184 | 0 | 29 | 213 |
| [src/templates/components/calendar\_base.html](/src/templates/components/calendar_base.html) | HTML | 401 | 2 | 69 | 472 |
| [src/templates/components/flash\_messages.html](/src/templates/components/flash_messages.html) | HTML | 129 | 0 | 15 | 144 |
| [src/templates/private/admins/announcements/index.html](/src/templates/private/admins/announcements/index.html) | HTML | 320 | 8 | 35 | 363 |
| [src/templates/private/admins/components/mobile\_calendar\_admin.html](/src/templates/private/admins/components/mobile_calendar_admin.html) | HTML | 473 | 1 | 67 | 541 |
| [src/templates/private/admins/components/navbar.html](/src/templates/private/admins/components/navbar.html) | HTML | 4 | 1 | 0 | 5 |
| [src/templates/private/admins/courses/index.html](/src/templates/private/admins/courses/index.html) | HTML | 4 | 1 | 1 | 6 |
| [src/templates/private/admins/courses/view\_instance.html](/src/templates/private/admins/courses/view_instance.html) | HTML | 179 | 6 | 20 | 205 |
| [src/templates/private/admins/dashboard/components/quick\_actions.html](/src/templates/private/admins/dashboard/components/quick_actions.html) | HTML | 283 | 2 | 39 | 324 |
| [src/templates/private/admins/dashboard/components/stats\_cards.html](/src/templates/private/admins/dashboard/components/stats_cards.html) | HTML | 301 | 5 | 35 | 341 |
| [src/templates/private/admins/dashboard/index.html](/src/templates/private/admins/dashboard/index.html) | HTML | 93 | 0 | 13 | 106 |
| [src/templates/private/admins/enrollments/create.html](/src/templates/private/admins/enrollments/create.html) | HTML | 218 | 9 | 28 | 255 |
| [src/templates/private/admins/logs/index.html](/src/templates/private/admins/logs/index.html) | HTML | 360 | 6 | 16 | 382 |
| [src/templates/private/admins/students/details.html](/src/templates/private/admins/students/details.html) | HTML | 108 | 0 | 0 | 108 |
| [src/templates/private/admins/students/details\_backup.html](/src/templates/private/admins/students/details_backup.html) | HTML | 851 | 3 | 86 | 940 |
| [src/templates/private/admins/students/index.html](/src/templates/private/admins/students/index.html) | HTML | 442 | 0 | 74 | 516 |
| [src/templates/private/components/calendar\_editable.html](/src/templates/private/components/calendar_editable.html) | HTML | -727 | -3 | -116 | -846 |
| [src/templates/private/components/mobile\_calendar.html](/src/templates/private/components/mobile_calendar.html) | HTML | 955 | 5 | 160 | 1,120 |
| [src/templates/private/components/nav/role\_switcher.html](/src/templates/private/components/nav/role_switcher.html) | HTML | 138 | 0 | 18 | 156 |
| [src/templates/private/flask\_mail/form.html](/src/templates/private/flask_mail/form.html) | HTML | 348 | 7 | 56 | 411 |
| [src/templates/private/flask\_mail/management.html](/src/templates/private/flask_mail/management.html) | HTML | 144 | 6 | 13 | 163 |
| [src/templates/private/flask\_mail/preview.html](/src/templates/private/flask_mail/preview.html) | HTML | 340 | 10 | 56 | 406 |
| [src/templates/private/instructors/components/mobile\_calendar\_instructor.html](/src/templates/private/instructors/components/mobile_calendar_instructor.html) | HTML | 418 | 2 | 70 | 490 |
| [src/templates/private/instructors/components/navbar.html](/src/templates/private/instructors/components/navbar.html) | HTML | -1 | 0 | 0 | -1 |
| [src/templates/private/students/components/calendar.html](/src/templates/private/students/components/calendar.html) | HTML | 334 | 4 | 46 | 384 |
| [src/templates/private/students/components/mobile\_calendar\_student.html](/src/templates/private/students/components/mobile_calendar_student.html) | HTML | 429 | 2 | 72 | 503 |
| [src/templates/private/students/components/navbar.html](/src/templates/private/students/components/navbar.html) | HTML | 39 | 3 | 5 | 47 |
| [src/templates/private/students/dashboard/index.html](/src/templates/private/students/dashboard/index.html) | HTML | 97 | 2 | 8 | 107 |
| [src/templates/private/students/enrollments/index.html](/src/templates/private/students/enrollments/index.html) | HTML | 43 | 3 | 5 | 51 |
| [src/templates/private/students/settings/index.html](/src/templates/private/students/settings/index.html) | HTML | 51 | 5 | 7 | 63 |
| [src/templates/private/students/settings/tabs/account.html](/src/templates/private/students/settings/tabs/account.html) | HTML | 62 | 1 | 2 | 65 |
| [src/templates/private/students/settings/tabs/password.html](/src/templates/private/students/settings/tabs/password.html) | HTML | 30 | 0 | 4 | 34 |
| [src/templates/private/students/settings/tabs/profile.html](/src/templates/private/students/settings/tabs/profile.html) | HTML | 35 | 0 | 5 | 40 |
| [src/templates/private/superusers/components/mobile\_calendar\_superuser.html](/src/templates/private/superusers/components/mobile_calendar_superuser.html) | HTML | 501 | 3 | 85 | 589 |
| [src/templates/private/superusers/components/navbar.html](/src/templates/private/superusers/components/navbar.html) | HTML | 2 | 1 | 0 | 3 |
| [src/templates/private/superusers/course\_templates/index.html](/src/templates/private/superusers/course_templates/index.html) | HTML | 53 | 0 | 13 | 66 |
| [src/templates/private/superusers/settings/index.html](/src/templates/private/superusers/settings/index.html) | HTML | 109 | 3 | 13 | 125 |
| [src/templates/private/superusers/settings/tabs/email.html](/src/templates/private/superusers/settings/tabs/email.html) | HTML | 100 | 0 | 11 | 111 |
| [src/templates/private/superusers/users/add\_to\_role.html](/src/templates/private/superusers/users/add_to_role.html) | HTML | 99 | 1 | 7 | 107 |
| [src/templates/private/superusers/users/index.html](/src/templates/private/superusers/users/index.html) | HTML | 86 | -1 | 10 | 95 |
| [src/templates/private/superusers/users/manage\_roles.html](/src/templates/private/superusers/users/manage_roles.html) | HTML | 136 | 4 | 8 | 148 |
| [src/templates/public/auth/dev.html](/src/templates/public/auth/dev.html) | HTML | 468 | 4 | 69 | 541 |
| [src/templates/public/auth/loginReg.html](/src/templates/public/auth/loginReg.html) | HTML | 450 | 1 | 79 | 530 |
| [src/templates/public/components/calendar.html](/src/templates/public/components/calendar.html) | HTML | 244 | 1 | 32 | 277 |
| [src/templates/public/components/navbar.html](/src/templates/public/components/navbar.html) | HTML | 15 | 0 | 0 | 15 |
| [src/templates/public/landing/components/FAQ.html](/src/templates/public/landing/components/FAQ.html) | HTML | 191 | 14 | 14 | 219 |
| [src/templates/public/landing/components/banner.html](/src/templates/public/landing/components/banner.html) | HTML | 66 | 0 | 9 | 75 |
| [src/templates/public/landing/components/hero.html](/src/templates/public/landing/components/hero.html) | HTML | 619 | 9 | 91 | 719 |
| [src/templates/public/landing/components/how\_it\_works.html](/src/templates/public/landing/components/how_it_works.html) | HTML | 142 | 10 | 9 | 161 |
| [src/templates/public/landing/components/social\_proof.html](/src/templates/public/landing/components/social_proof.html) | HTML | 539 | 5 | 55 | 599 |
| [src/templates/public/landing/index.html](/src/templates/public/landing/index.html) | HTML | 9 | 0 | 0 | 9 |
| [src/utils/custom\_decorators.py](/src/utils/custom_decorators.py) | Python | 5 | 1 | 1 | 7 |
| [src/utils/encryption.py](/src/utils/encryption.py) | Python | 28 | 29 | 12 | 69 |

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details