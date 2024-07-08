import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    if os.environ.get('APP_MODE') == 'production':
        app.config.from_object('config.ProductionConfig')
        app.run(host='0.0.0.0', port=5000)
    else:
        app.config.from_object('config.DevelopmentConfig')
        app.run(debug=True)