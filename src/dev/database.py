from flask import Blueprint, redirect, url_for, flash, request
from src.models.main import db
from src.utils.custom_decorators import login_required, role_required
import os

# Create blueprint
database_bp = Blueprint('database', __name__, url_prefix='/dev/database')


@database_bp.route('/rebuild', methods=['POST'])
@login_required
@role_required('superuser')
def rebuild_database():
    """
    Drop all tables and recreate them from models.
    WARNING: This will delete ALL data!
    
    Requires confirmation parameter: confirm=REBUILD
    """
    confirmation = request.form.get('confirm') or request.args.get('confirm')
    
    if confirmation != 'REBUILD':
        flash('Database rebuild cancelled. Confirmation required.', 'warning')
        return redirect(request.referrer or url_for('main.index'))
    
    try:
        # Drop all tables
        db.drop_all()
        flash('All tables dropped successfully.', 'success')
        
        # Recreate all tables
        db.create_all()
        flash('All tables recreated successfully.', 'success')
        
        flash('⚠️ Database has been completely rebuilt. All data was deleted.', 'warning')
        
    except Exception as e:
        flash(f'Error rebuilding database: {str(e)}', 'danger')
        db.session.rollback()
    
    return redirect(url_for('auth.loginReg'))


@database_bp.route('/rebuild-form')
@login_required
@role_required('superuser')
def rebuild_form():
    """Show a form to confirm database rebuild."""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Rebuild Database</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-6">
                    <div class="card border-danger">
                        <div class="card-header bg-danger text-white">
                            <h4 class="mb-0">
                                <i class="bi bi-exclamation-triangle-fill"></i>
                                Rebuild Database
                            </h4>
                        </div>
                        <div class="card-body">
                            <div class="alert alert-danger" role="alert">
                                <strong>⚠️ WARNING!</strong>
                                <p class="mb-0">This action will:</p>
                                <ul class="mt-2 mb-0">
                                    <li>Drop ALL tables in the database</li>
                                    <li>Delete ALL data permanently</li>
                                    <li>Recreate empty tables from models</li>
                                    <li>Bypass all migrations</li>
                                </ul>
                            </div>
                            
                            <p class="mb-3">
                                This is intended for development/staging environments only. 
                                <strong>DO NOT use this in production!</strong>
                            </p>
                            
                            <form method="POST" action="/dev/database/rebuild" onsubmit="return confirmRebuild()">
                                <div class="mb-3">
                                    <label for="confirm" class="form-label">
                                        Type <code>REBUILD</code> to confirm:
                                    </label>
                                    <input 
                                        type="text" 
                                        class="form-control" 
                                        id="confirm" 
                                        name="confirm" 
                                        placeholder="REBUILD"
                                        required
                                    >
                                </div>
                                
                                <div class="d-grid gap-2">
                                    <button type="submit" class="btn btn-danger">
                                        Rebuild Database
                                    </button>
                                    <a href="/" class="btn btn-secondary">
                                        Cancel
                                    </a>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
        function confirmRebuild() {
            const input = document.getElementById('confirm').value;
            if (input !== 'REBUILD') {
                alert('Please type REBUILD exactly to confirm.');
                return false;
            }
            return confirm('Are you absolutely sure? This cannot be undone!');
        }
        </script>
    </body>
    </html>
    '''
