release: python manage.py migrate
web: gunicorn -c barcode_app/gunicorn_server.py barcode_app.wsgi --log-file -
