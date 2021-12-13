#!/bin/sh

PROJECT_NAME=$1

if [ $# -eq 0 ]
then
  echo "No argument supplied"
else
  # change image names
  sed -i "" "s/ddst/$PROJECT_NAME/g" docker-compose.yml
  sed -i "" "s/ddst/$PROJECT_NAME/g" docker-compose.prod.yml
  # change docstrings
  sed -i "" "s/ddst/$PROJECT_NAME/g" app/urls.py
  sed -i "" "s/ddst/$PROJECT_NAME/g" app/wsgi.py
  echo "OK"
fi