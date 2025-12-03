from src import create_app
import os

# Get config from environment or default to production in Docker
# config_name = os.environ.get('FLASK_CONFIG', 'production')
config_name = os.environ.get('FLASK_CONFIG', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # Only use debug mode when running directly with python
    app.run(debug=True, host='0.0.0.0', port=5199)
else:
    # Log startup when running with gunicorn
    app.logger.info("Application event", event_type="startup", config=config_name)