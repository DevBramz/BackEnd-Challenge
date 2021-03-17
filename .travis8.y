language: python

python:
  - 3.6

services: postgresql

addons:
  postgresql: "9.6"

install:
  - pip install -r requirements.txt

before_script:
  - psql -c "CREATE DATABASE orders;" -U postgres
  - python manage.py migrate --noinput
  - python manage.py collectstatic

script:
  - pytest

  