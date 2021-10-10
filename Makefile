restart:
	sudo systemctl restart gunicorn

restart:
	sudo systemctl stop gunicorn

migrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate
