# python-chefkoch

[![Downloads](https://static.pepy.tech/badge/python-chefkoch)](https://pepy.tech/project/python-chefkoch)
[![PyPI version](https://badge.fury.io/py/python-chefkoch.svg)](https://badge.fury.io/py/python-chefkoch)

A simple Python retrieval tool for recipes from chefkoch.de

---

## 🐍 Installation

```bash
pip install python-chefkoch
```

**Requirements:**
- Python 3.7+
- [requests](https://pypi.org/project/requests/)
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
- [isodate](https://pypi.org/project/isodate/)

---

## 🚀 Quickstart

```python
from chefkoch.recipe import Recipe

recipe = Recipe('https://www.chefkoch.de/rezepte/745721177147257/Lasagne.html')
print(recipe.title)
```

---

## 🍽️ Recipe Attributes

| Attribute         | Type                   | Description                                      |
|-------------------|------------------------|--------------------------------------------------|
| title             | str                    | The title of the recipe.                         |
| image_url         | str                    | The URL of the recipe's main image.              |
| image_base64      | bytes                  | The raw bytes of the recipe's image.             |
| image_urls        | List[str]              | URLs of all images associated with the recipe.   |
| date_published    | datetime.datetime      | The date when the recipe was published.          |
| prep_time         | isodate.Duration       | The preparation time of the recipe.              |
| cook_time         | isodate.Duration       | The cooking time of the recipe.                  |
| total_time        | isodate.Duration       | The total time required to prepare the recipe.   |
| difficulty        | str                    | The difficulty level of the recipe.              |
| ingredients       | List[str]              | The list of ingredients required.                |
| instructions      | List[str]              | The list of instructions to prepare the recipe.  |
| publisher         | str                    | The name of the publisher of the recipe.         |
| author            | str                    | The name of the author of the recipe.            |
| calories          | str                    | The number of calories in the recipe.            |
| keywords          | str                    | The keywords associated with the recipe.         |
| number_reviews    | int                    | The number of reviews for the recipe.            |
| number_ratings    | int                    | The number of ratings for the recipe.            |
| rating            | float                  | The average rating of the recipe.                |
| category          | str                    | The category of the recipe.                      |

---

## 🕵️ Retrievers

### RandomRetriever
Retrieve one or more random recipes from chefkoch.de.

```python
from chefkoch.retrievers import RandomRetriever

retriever = RandomRetriever()
recipes = retriever.get_recipes(n=3)  # Get 3 random recipes
retriever.close()  # Always close when done
```

### DailyRecipeRetriever
Retrieve daily recommended recipes ("kochen" or "backen").

```python
from chefkoch.retrievers import DailyRecipeRetriever

retriever = DailyRecipeRetriever()
recipes = retriever.get_recipes(type="kochen")  # or type="backen"
retriever.close()
```

### SearchRetriever
Search for recipes with advanced filters.

```python
from chefkoch.retrievers import SearchRetriever

retriever = SearchRetriever(
    properties=["Einfach"],
    health=["Vegan"],
    categories=["Pizza"],
    countries=["Italien"],
    meal_type=["Hauptspeise"],
    prep_times="30",
    ratings="4",
    sort="Bewertung"
)
recipes = retriever.get_recipes(search_query="Lasagne", page=1)
retriever.close()
```

#### **Available Filter Options**
- **properties:** Einfach, Schnell, Basisrezepte, Preiswert
- **health:** Vegetarisch, Vegan, Kalorienarm, Low Carb, Ketogen, Paleo, Fettarm, Trennkost, Vollwert
- **categories:** Auflauf, Pizza, Reis- oder Nudelsalat, Salat, Salatdressing, Tarte, Fingerfood, Dips, Saucen, Suppe, Klöße, Brot und Brötchen, Brotspeise, Aufstrich, Süßspeise, Eis, Kuchen, Kekse, Torte, Confiserie, Getränke, Shake, Gewürzmischung, Pasten, Studentenküche
- **countries:** Deutschland, Italien, Spanien, Portugal, Frankreich, England, Osteuropa, Skandinavien, Griechenland, Türkei, Russland, Naher Osten, Asien, Indien, Japan, Amerika, Mexiko, Karibik, Lateinamerika, Afrika, Marokko, Ägypten, Australien
- **meal_type:** Hauptspeise, Vorspeise, Beilage, Dessert, Snack, Frühstück
- **prep_times:** 15, 30, 60, 120, Alle
- **ratings:** Alle, 2, 3, 4, Top
- **sort:** Empfehlung, Bewertung, Neuheiten

---

## 🧹 Session Management
All retrievers (`RandomRetriever`, `DailyRecipeRetriever`, `SearchRetriever`) use a persistent HTTP session. **Always call `close()`** when done to free resources.

---

## 💁 Contributing

As an open-source initiative in a rapidly evolving domain, I welcome contributions, be it through the addition of new features or the improvement of existing ones. If you have any suggestions, bug reports, or annoyances, please report them to the issue tracker.

---

## 📃 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.