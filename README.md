# YaMDb API
# About.

**YaMDb** is a rating platform & social network.

Developed from the Pre-Code by Yandex.Practicum as a Part of Education Process.

Development Team:
+ Pavel Kirsanov, paul.kirsanov@yandex.ru;
+ Alexander Mikhailov, extroper@yandex.ru;
+ Nikita Poruchikov, nickitkavolf@yandex.ru.

The YaMDb project collects users' **reviews** on **titles**. The titles themselves are not stored in YaMDb; you cannot watch a movie or listen to music here.

The titles are divided into **categories** such as "Books", "Movies", "Music". For instance, in the "Books" category there may be the titles "Winnie-The-Pooh and All, All, All" and "The Martian Chronicles", and in the "Music" category there may be the song "Давеча" by the group "Жуки" and Bach's Suite No. 2 in B minor BWV 1067. The list of categories can be expanded (for example, you can add the category "Fine Arts" or "Jewelry").

The title can be attributed to a **genre** from the predefined list (for example, "Fairy Tale", "Rock" or "Arthouse").

Only the administrator can add titles, categories and genres.

Both grateful and outraged users leave text **reviews** for titles and give the title a rating in the range from 1 to 10 (integer); from user ratings, an average rating of the title is formed - a **rating** (an integer). A user can leave only one review per title.

Users can leave **comments** on reviews.

Only authenticated users can add reviews, comments and give ratings.

**API YaMDb** is a REST API for **YaMDb** project.

**YaMDb API Resources**:

+ **auth**: authentication.
+ **users**: users.
+ **titles**: titles for which reviews are written (a certain film, book or song).
+ **categories**: categories (types) of titles (“Movies”, “Books”, “Music”). One piece can only be assigned to one category.
+ **genres**: genres of titles. One title can be tied to several genres.
+ **reviews**: reviews of titles. The review is tied to a specific title.
+ **comments**: comments to reviews. The comment is tied to a specific review.

# Deployment.
You may deploy this locally by prompting the following commands into your machine's terminal:
```
$ python3 -m venv venv
$ source venv/bin/activate
$ python3 -m pip install --upgrade pip
$ pip install -r requirements.txt
$ cd api_yamdb
$ python3 manage.py migrate
$ python3 manage.py runserver
```
# Showcase.
GET request to [Title Endpoint](http://127.0.0.1:8000/api/v1/titles/) would get you the like API response:
```
{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "id": 0,
      "name": "string",
      "year": 0,
      "rating": 0,
      "description": "string",
      "genre": [
        {
          "name": "string",
          "slug": "^-$"
        }
      ],
      "category": {
        "name": "string",
        "slug": "^-$"
      }
    }
  ]
}
```
And many more.
