
# Foodgram


### Domain address: https://rufoodgram.duckdns.org/

## Description
Foodgram is a web application designed for food enthusiasts to share and discover recipes. Users can create accounts to upload their own recipes, complete with ingredients, step-by-step instructions, and photos. Users can interact with recipes by saving them to their personal collections. Foodgram fosters a vibrant community of food lovers who exchange culinary ideas and inspiration.

## Usage
Go to **/backend** folder, install requirements, migrate and run server:
```bash
  cd backend
  pip install -r requirements.txt
  python manage.py migrate
  python manage.py runserver
```

### Docker Compose setup
To run with Docker Compose place _.env_ file to **/infra** folder and run:
```bash
  docker compose up
```
_.env_ file example can be located in **/infra**.

### Fill database
You can use fixture.json in **/backend**:
```bash
  python manage.py loaddata fixture.json
```
And for ingredients you have command:
```bash
  python manage.py load_ingredients
```
Ingredients json file located in **/backend/core/data**.

## Documentation
Go to /api/docs/ to see API docs.

## Authors
- [Soslan Khutinaev](https://github.com/ruki-qq)

## Technology stack:
➡️ 🐍 [Python 3.11](https://www.python.org)\
➡️ 🦄 [Django 4.2](https://www.djangoproject.com//)\
➡️ 🦄 [Django REST Framework 3.11](https://www.django-rest-framework.org/)\
➡️ 🐉 Some other libraries (see backend/requirements.txt)




## API requests examples

### Request

GET /recipes/

    curl -i -H 'Accept: application/json' http://localhost:8000/api/recipes/

### Response

    HTTP/1.1 200 OK
    Server: nginx/1.25.4
    Date: Tue, 26 Mar 2024 20:58:37 GMT
    Content-Type: application/json
    Connection: keep-alive
    Vary: Accept, origin
    Allow: GET, POST, HEAD, OPTIONS
    X-Frame-Options: DENY
    X-Content-Type-Options: nosniff
    Referrer-Policy: same-origin
    Cross-Origin-Opener-Policy: same-origin

    {
      "count": 5,
      "next": null,
      "previous": null,
      "results": [<data>]
    }

### Request

GET /recipes/{recipe_id}/

    curl -i -H 'Accept: application/json' http://localhost:8000/api/recipes/1/

### Response

    HTTP/1.1 200 OK
    Server: nginx/1.25.4
    Date: Tue, 26 Mar 2024 21:03: 29 GMT
    Content-Type: application/json
    Connection: keep-alive
    Vary: Accept, origin
    Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
    X-Frame-Options: DENY
    X-Content-Type-Options: nosniff
    Referrer-Policy: same-origin
    Cross-Origin-Opener-Policy: same-origin
            
    {
      "id": 1,
      "image": "http://localhost/media/api/imgs/5f9b4f7b-37ef-4861-93c7-1cbaf33bc98f.webp",
      "ingredients": [
        {
          "id": 1,
          "name": "Лосось",
          "measurement_unit": "грамм",
          "amount": 300
        }
      ],
      "tags": [
        {
          "id": 6,
          "name": "Лосось",
          "color": "#FF6E44",
          "slug": "salmon"
        }
      ],
      "author": {
        "email": "ramsay@google.com",
        "id": 3,
        "username": "ramsay",
        "first_name": "Гордон",
        "last_name": "Рамзи",
        "is_subscribed": false
      },
      "is_favorited": false,
      "is_in_shopping_cart": false,
      "name": "Паста с лососем",
      "text": "Просто паста",
      "cooking_time": 20
    }
