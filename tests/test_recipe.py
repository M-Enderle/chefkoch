import datetime

from chefkoch import Recipe


def test_from_url():
    assert Recipe(url="https://www.chefkoch.de/rezepte/2307061368085964s") is not None
    assert (
        Recipe(url="https://www.chefkoch.de/rezepte/448991137121794/Waffeln.html")
        is not None
    )


def test_from_id():
    assert Recipe(id="745721177147257") is not None
    assert Recipe(id="815071185883117") is not None


def test_attributes():
    recipe = Recipe(
        url="https://www.chefkoch.de/rezepte/2307061368085964/Maultaschen-Sauerkraut-Pfanne.html"
    )
    assert type(recipe.title) == str
    assert recipe.title

    assert type(recipe.ingredients) == list
    assert recipe.ingredients

    assert type(recipe.instructions) == str
    assert recipe.instructions

    assert type(recipe.image_urls) == list
    assert recipe.image_urls

    assert type(recipe.image_base64) == bytes
    assert recipe.image_base64

    assert type(recipe.date_published) == datetime.datetime
    assert recipe.date_published

    assert type(recipe.prep_time) == datetime.timedelta
    assert recipe.prep_time

    assert type(recipe.category) == str
    assert recipe.category

    assert type(recipe.difficulty) == str
    assert recipe.difficulty

    assert type(recipe.publisher) == str
    assert recipe.publisher

    assert type(recipe.keywords) == list
    assert recipe.keywords

    assert type(recipe.number_reviews) == int
    assert recipe.number_reviews

    assert type(recipe.number_ratings) == int
    assert recipe.number_ratings

    assert type(recipe.rating) == float
    assert recipe.rating

    assert type(recipe.total_time) == datetime.timedelta
    assert recipe.total_time

    assert type(recipe.cook_time) == datetime.timedelta
    assert recipe.total_time
