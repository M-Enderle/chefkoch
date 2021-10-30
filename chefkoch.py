import threading
import requests
import bs4
import json

from typing import List

base_url = "https://www.chefkoch.de"


class CategoryNotFoundError(Exception):
    """ Thrown when a category is not valid """
    pass


class Recipe:
    """ Class to save all information for a recipe """

    def __init__(self, url: str, portions: int = 4):
        """
        Creates an object of the class Recipe and retrieves all info from chefkoch.
        :param url: Url of the recipe
        :param portions: Optionally modify the portions
        """

        self.portions: int = portions
        self.soup: bs4.BeautifulSoup = self.__generate_soup(url)
        self.url = self.soup.find("div", class_="recipe-servings ds-box").find("form")["action"]

        self.title: str = self.soup.find("article", class_="recipe-header") \
            .find("div", class_="ds-mb ds-mb-col").find("h1").text

        try:
            self.author: str = self.soup.findAll("a", class_="ds-copy-link bi-profile")[1].find("span").text
        except IndexError:
            self.author = "Unbekannt"

        self.prep_time: str = self.soup.find("span", class_="recipe-preptime rds-recipe-meta__badge") \
            .text.replace("\ue192", "").replace("\n", "").strip()
        self.difficulty: str = self.soup.find("span", class_="recipe-difficulty rds-recipe-meta__badge") \
            .text.replace("\ue202", "").replace("\n", "").strip()

        self.ingredients: dict = self.__get_ingredients()

        self.steps: list = [x.strip() for x in
                            self.soup.find("article", class_="ds-box ds-grid-float ds-col-12 ds-col-m-8 "
                                                             "ds-or-3")
                                .find("div").text.replace("\n", "").lower().replace("ca.", "circa")
                                .replace("min.", "mindestens").replace("ggf.", "gegebenfalls")
                                .replace("o. ä.", "oder ähnlich").replace("o.ä.", "oder ähnliche")
                                .replace("z.b.", "zum beispiel").replace("u. u.", "unter umständen").replace("u.u.",
                                                                                                             "unter umständen")
                                .replace("tk", "tiefkühl").replace("z. b.", "zum beispiel").replace("usw.",
                                                                                                    "und so weiter")
                                .split(".") if x]

        self.nutritional_values: dict = self.__get_nutritions()

    @staticmethod
    def generate(url: str, callback: list) -> None:
        """ Generates a Recipe object and appends it to the list callback. Used for threads. """
        recipe = Recipe(url)
        callback.append(recipe)

    def modify_portions(self, portions: int) -> dict:
        """
        Modifies the portions ( example 3 -> 3 portions ) and returns the new ingredients
        :param portions: New amount of portions
        :return: new ingredient dict
        """
        self.portions = portions
        self.soup = self.__generate_soup()
        self.ingredients = self.__get_ingredients()
        return self.ingredients

    def __generate_soup(self, url: str = None) -> bs4.BeautifulSoup:
        """ Generate new soup """
        if url is None:
            url = self.url
        r = requests.get(url + f"?portionen={self.portions}")
        return bs4.BeautifulSoup(r.text, features="html.parser")

    def __get_ingredients(self) -> dict:
        """
        Retrieves the ingredients
        :return: Dict with ingredients
        """
        ingredients = dict()
        for ingredient in self.soup.find("table", class_="ingredients table-header").find("tbody").findAll("tr"):
            ingredient_name = ingredient.findAll("td")[1].find("span").text
            try:
                ingredients[ingredient_name] = ingredient.findAll("td")[0].find("span").text \
                    .replace("\n", "").replace(" ", "")
            except AttributeError:
                ingredients[ingredient_name] = "etwas"
        return ingredients

    def __get_nutritions(self) -> dict:
        """
        Retrieves the nutritions from chefkoch
        :return: Dict of nutritions
        """
        nutritional_values = dict()
        try:
            nutritional_contents = [x.strip() for x in self.soup.find("div",
                                                                      class_="recipe-nutrition_content ds-box ds-grid").text.strip().split(
                "\n") if x.strip()]
            for i in range(0, len(nutritional_contents), 2):
                nutritional_values[nutritional_contents[i]] = nutritional_contents[i + 1]

        except AttributeError:
            nutritional_values = "Nothing found"

        return nutritional_values

    def __repr__(self) -> str:
        """ convert to string """
        return f"Recipe object '{self.title}' created by '{self.author}'"


def print_dict(my_dict: dict) -> None:
    """
    Beauty print a dict
    :param my_dict: dict to print
    """
    print(json.dumps(my_dict, sort_keys=True, indent=4, ensure_ascii=False))


def get_specific(search_term: str, frm: int = 0, to: int = 2, filters: dict = None,
                 specifications: list = None) -> list:
    """
    Search for a specific term optionally with categories and filters enabled.
    :param search_term: what to search for
    :param frm: first recipe on page to get
    :param to: last recipe on page to get
    :param filters: {
                        "page": 1/2/3/...,                                              | default: 1
                        "sort" : "date"/"rating"/"relevance" ,                          | default: relevance
                        "duration": "all"/15/30/45/60 ,                                 | default: all
                        "difficulty": {"easy": True, "medium": True, "hard": True}      | default: all True
                    }
           ! invalid inputs will be ignored !
    :param specifications: list of all specifications. Throws CategoryNotFoundError when one category is invalid
                           to see all specifications use get_specifications()
    :return: returns a list of search results
    """
    url_addon = ""
    if filters:
        # page number
        if "page" in filters:
            url_addon += "s" + str((int(filters["page"]) - 1) * 30)
        else:
            url_addon += "s0"

        # sort by date / rating / relevance
        if "sort" in filters:
            if filters["sort"] == "date":
                url_addon += "o3"
            elif filters["sort" == "rating"]:
                url_addon += "o8"

        url_addon += "e1n1z1b0i0"

        # filter by minutes
        if "duration" in filters and filters["duration"] != "all":
            url_addon += "m" + str(filters["duration"])

        # filter by difficulty
        if "difficulty" in filters:
            url_addon += "d"
            if "easy" not in filters["difficulty"] or filters["difficulty"]["easy"]:
                url_addon += "1,"
            if "medium" not in filters["difficulty"] or filters["difficulty"]["medium"]:
                url_addon += "2,"
            if "hard" not in filters["difficulty"] or filters["difficulty"]["hard"]:
                url_addon += "3,"
            url_addon = url_addon[:-1]
    else:
        url_addon += "s0"

    if specifications:

        url_addon += "t"

        with open("specifications.json", "r", encoding="utf-8") as file_in:
            category_dict = json.load(file_in)

        for specification in specifications:
            if specification.lower() not in category_dict:
                raise CategoryNotFoundError(f"Category {specification} not found")
            url_addon += str(category_dict[specification.lower()]) + ","
        url_addon = url_addon[:-1]

    r = requests.get(base_url + f"/rs/{url_addon}/{search_term}/Rezepte.html")
    soup = bs4.BeautifulSoup(r.text, features='html.parser')

    articles = soup.findAll('article')[frm:to + 1]

    def get_attr(_article, _attr_name: str):
        return _article.find('a')[_attr_name]

    recipes = list()

    threads = []
    for article in articles:
        threads.append(threading.Thread(target=Recipe.generate,
                                        args=(get_attr(article, "href"), recipes)))
        threads[-1].start()

    for thread in threads:
        thread.join()

    return recipes


def get_specifications() -> List[Recipe]:
    """
    :return: A list of all possible specifications
    """
    with open("specifications.json", "r", encoding="utf-8") as file_in:
        return list(json.load(file_in).keys())


def get_daily_recommendation(frm: int = 0, to: int = 2, url_addon: str = "koche") -> List[Recipe]:
    """
    Returns daily recommendation
    :param frm:
    :param to:
    :param url_addon: default: koche, possible values: koche, backe
    :return:
    """
    r = requests.get(base_url + f"/rezepte/was-{url_addon}-ich-heute/")
    soup = bs4.BeautifulSoup(r.text, features='html.parser')

    articles = soup.findAll("div", class_="inspiration__entry")[frm:to + 1]

    recipes = list()

    for article in articles:
        article = article.find("a", class_="card__link")
        recipes.append(Recipe(article["href"]))

    return recipes


def get_categories() -> dict:
    """ :return: dictionary with a hirachy of all categories """
    with open("categories.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_random_recipe() -> Recipe:
    return Recipe("https://www.chefkoch.de/rezepte/zufallsrezept/")