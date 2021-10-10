restart:
	sudo systemctl restart gunicorn

stop:
	sudo systemctl stop gunicorn

migrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate
