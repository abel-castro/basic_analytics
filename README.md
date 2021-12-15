# Basic Analytics
I created this project as an alternative to Google Analytics for my side projects.

Provides an API for tracking web analytics data and an interface with different charts for visualizing them.
It is possible to see:
- Amount of page views for a domain and for the different paths of it
- Browser, Country, Device and OS data

![Basic Analytics](https://github.com/abel-castro/basic_analytics/blob/main/screenshot.png)

## API
POST: `/api/track/`
- required arguments:
  - domain_id: (str) the uuid of the Domain object in the Basic Analytics DB
  - request_meta: (json) at least HTTP_USER_AGENT and REMOTE_ADDR are required
  - url: (str) the visited url
  
## Project setup

Get the GeoLite2-City and GeoLite2-Country files from https://dev.maxmind.com/ and put them in to the /app/data directory.

### Development
- Create a .env file from the template env_template_dev with the desired values.

- Build the development image: ```docker-compose build ```

- Optional: create some test data with 
```docker-compose run django /app/manage.py create_test_data```
- Run ```docker-compose up``` and go to http://0.0.0.0:8000
to see your runserver.

### Production
- Create a .env file from the template env_template_prd with the desired values.

- Build the production image:
```
docker-compose -f docker-compose.prod.yml build
``` 

- Start your production server with: 
```
docker-compose -f docker-compose.prod.yml up
```

- Run migrations:
```
docker-compose -f docker-compose.prod.yml --rm django /app/manage.py migrate
```

### Getting started
- Create a superuser with `/app/manage.py createsuperuser`
- Create a Domain object in the django-admin
- Make requests to the provided API endpoint `/api/track/` (more details above)
- Now you will be able to see details about the tracked data in the charts