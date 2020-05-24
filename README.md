# cyfmazyr
Website for Club of Young Firefighters in Mazyr, Belarus

## Installation

Create directory for project
```
mkdir cyfmazyr
cd cyfmazyr
```

Create virtual environment with `virtualenv`
```
python -m venv venv
```

Open command prompt in current directory and activate `virtualenv`
```
source venv\Scripts\activate
```

Clone repository
```
git clone https://github.com/panwaclaw/cyfmazyr.git
```

Enter directory
```
cd cyfamzyr
```

Run migrations (before that, setup `DATABASES` in `cyfmazyr.settings` and create it)
```
python manage.py migrate
```

Create superuser
```
python manage.py createsuperuser
```

Run server
```
python manage.py runserver 0.0.0.0:80
```

Website will be available at ```http://localhost```, administration at ```http://localhost/admin```
