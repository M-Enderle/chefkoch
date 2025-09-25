import datetime
import isodate

from chefkoch import Recipe


def test_from_url_old():
    # This is an example of an older recipe format
    recipe = Recipe(url="https://www.chefkoch.de/rezepte/745721177147257/Lasagne.html")
    assert recipe is not None
    assert recipe.title == "Lasagne"

def test_from_url_new():
    # This is an example of the new recipe format
    recipe = Recipe(url="https://www.chefkoch.de/rezepte/4267801700467824/Frikadellen-aus-der-Heissluftfritteuse.html")
    assert recipe is not None
    assert recipe.title == "Frikadellen aus der Heißluftfritteuse"

def test_from_id():
    assert Recipe(id="745721177147257") is not None
    assert Recipe(id="4267801700467824") is not None


def test_old_format_attributes():
    recipe = Recipe(
        url="https://www.chefkoch.de/rezepte/745721177147257/Lasagne.html"
    )
    assert isinstance(recipe.title, str) and recipe.title
    assert isinstance(recipe.ingredients, list) and recipe.ingredients
    assert isinstance(recipe.instructions, str) and recipe.instructions
    assert isinstance(recipe.image_url, str) and recipe.image_url.startswith("https://")
    assert isinstance(recipe.date_published, datetime.datetime)
    assert isinstance(recipe.prep_time, isodate.duration.Duration)
    assert isinstance(recipe.difficulty, str) and recipe.difficulty
    assert isinstance(recipe.author, str) and recipe.author
    assert isinstance(recipe.keywords, list)
    assert isinstance(recipe.number_ratings, int)
    assert isinstance(recipe.rating, float)
    assert isinstance(recipe.total_time, isodate.duration.Duration)
    assert isinstance(recipe.cook_time, isodate.duration.Duration)
    assert "Hackfleisch" in " ".join(recipe.ingredients)

def test_new_format_attributes():
    recipe = Recipe(
        url="https://www.chefkoch.de/rezepte/4267801700467824/Frikadellen-aus-der-Heissluftfritteuse.html"
    )
    assert recipe.title == "Frikadellen aus der Heißluftfritteuse"
    assert isinstance(recipe.ingredients, list) and recipe.ingredients
    assert "Zwiebel" in " ".join(recipe.ingredients)
    assert isinstance(recipe.instructions, str) and recipe.instructions
    assert "braten" in recipe.instructions
    assert recipe.image_url.startswith("https://images.chefkoch-cdn.de/")
    assert isinstance(recipe.image_base64, bytes)
    assert isinstance(recipe.date_published, datetime.datetime)
    assert isinstance(recipe.prep_time, isodate.duration.Duration)
    assert recipe.prep_time.td.total_seconds() == 15 * 60
    assert recipe.difficulty == "simpel"
    assert recipe.author == "Fine579"
    assert isinstance(recipe.keywords, list) and "Heißluftfritteuse" in recipe.keywords
    assert isinstance(recipe.number_ratings, int)
    assert isinstance(recipe.rating, float)
    assert isinstance(recipe.total_time, isodate.duration.Duration)
    assert isinstance(recipe.cook_time, isodate.duration.Duration)
