import threading
import requests
import bs4
import json

from typing import List

base_url = "https://www.chefkoch.de"


class CategoryNotFoundError(Exception):
    """ Thrown when a category is not valid """
    pass


class EndOfRecipeError(Exception):
    """ Raised when the end of the steps has been reached """
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
        self.url = self.soup.find("div", class_="recipe-servings ds-box").find("form")["action"].split("?")[0] #get portions right
        self.info_dict = json.loads(self.soup.findAll("script", type="application/ld+json")[1].text)

        self.title: str = self.info_dict["name"]
        self.author = self.info_dict["author"]["name"]
        self.keywords = self.info_dict["keywords"]
        self.date_published = self.info_dict["datePublished"]
        self.description = self.info_dict["description"]
        self.image = self.info_dict["image"]
        self.recipeCategory = self.info_dict["recipeCategory"]
        self.prep_time = self.info_dict["prepTime"].replace("P0DT0H", "")

        try:
            self.rating = self.info_dict["aggregateRating"]["ratingValue"]
        except KeyError:
            self.rating = None

        try:
            self.cook_time = self.info_dict["cookTime"].replace("P0DT0H", "")
        except KeyError:
            self.cook_time = None

        try:
            self.reviews = self.info_dict["reviews"]
        except KeyError:
            self.reviews = None

        self.difficulty: str = self.soup.find("span", class_="recipe-difficulty rds-recipe-meta__badge") \
            .text.replace("\ue202", "").replace("\n", "").strip()

        self.ingredients: dict = self.__get_ingredients()

        self.steps: list = [x.strip() for x in
                            self.info_dict["recipeInstructions"]
                                .replace("ca.", "circa")
                                .replace("min.", "mindestens")
                                .replace("mind.", "mindestens")
                                .replace("ggf.", "gegebenfalls")
                                .replace("o. ä.", "oder ähnlich")
                                .replace("o.ä.", "oder ähnliche")
                                .replace("z.b.", "zum beispiel")
                                .replace("u. u.", "unter umständen")
                                .replace("u.u.", "unter umständen")
                                .replace("tk", "tiefkühl")
                                .replace("z. b.", "zum beispiel")
                                .replace("usw.", "und so weiter")
                                .split(".") if x]

        self.nutritional_values: dict = self.__get_nutritions()

        self.current_step = -1

    @staticmethod
    def generate_multiple(urls: list, callback_list: list) -> None:
        """ Generates recipe objects for each url in list and appends it to the list callback. """

        def generate_to_list(_url, _callback_list):
            _callback_list.append(Recipe(_url))

        threads = []
        for url in urls:
            threads.append(threading.Thread(target=generate_to_list, args=(url, callback_list)))
            threads[-1].start()

        for thread in threads:
            thread.join()

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
        for table in self.soup.findAll("table", class_="ingredients table-header"):
            try:
                header = table.find("thead").find("th").text.replace("\n", "")
                ingredients[header] = "==="
            except:
                pass
            for ingredient in table.find("tbody").findAll("tr"):
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
                                                                      class_="recipe-nutrition_content ds-box ds-grid")
                .text.strip().split(
                "\n") if x.strip()]
            for i in range(0, len(nutritional_contents), 2):
                nutritional_values[nutritional_contents[i]] = nutritional_contents[i + 1]

        except AttributeError:
            nutritional_values = "Nothing found"

        return nutritional_values

    def get_next_step(self):
        self.current_step += 1
        if self.current_step < len(self.steps):
            return self.steps[self.current_step]
        raise EndOfRecipeError

    def __repr__(self):
        """ repr """
        return f"Recipe object '{self.title}'"

    def __str__(self) -> str:
        """ convert to string """
        return f"Recipe object '{self.title}' created by user '{self.author}':\n" \
               f"  preperation time: {self.prep_time}\n" \
               f"  difficulty: {self.difficulty}\n" \
               f"  nutritional_values: {self.nutritional_values}"


def search(search_term: str, frm: int = 0, to: int = 2, filters: dict = None, specifications: list = None) -> list:
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
            elif filters["sort"] == "rating":
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
        files = ["../src/specifications.json","./src/specifications.json"]
        category_dict = None
        for file in files:
            try:
                with open(file, "r", encoding="utf-8") as file_in:
                    category_dict = json.load(file_in)
                    break
            except Exception:
                pass
        if category_dict is None:
            print("File /src/specifications.json not found")

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
    Recipe.generate_multiple([get_attr(article, "href") for article in articles], recipes)

    return recipes


def get_specifications() -> List[Recipe]:
    """
    :return: A list of all possible specifications
    """
    files = ["../src/specifications.json","./src/specifications.json"]
    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as file_in:
                return list(json.load(file_in).keys())
        except Exception as e:
            pass
    print("File /src/specifications.json not found")
    return None


def get_daily_recommendations(frm: int = 0, to: int = 2, category: str = "koche") -> List[Recipe]:
    """
    Returns daily recommendations as a list of recipes.
    :param frm: first recipe to retrieve
    :param to: last recipe to retrieve -> max 8
    :param category: default: koche, possible values: koche, backe
    :return: list of all recipes retrieved
    """

    if category not in ["koche", "backe"]:
        raise CategoryNotFoundError

    r = requests.get(base_url + f"/rezepte/was-{category}-ich-heute/")
    soup = bs4.BeautifulSoup(r.text, features='html.parser')

    article_divs = soup.findAll("div", class_="ds-recipe-card")[frm:to+1]

    articles = list()
    for article_div in article_divs:
        if article_div.find("a", class_="ds-recipe-card__link"):
            articles.append(article_div.find("a", class_="ds-recipe-card__link")["href"])

    recipes = list()
    Recipe.generate_multiple(articles, recipes)

    return recipes


def get_categories() -> dict:
    """ :return: dictionary with a hirachy of all categories """
    files = ["../src/categories.json","./src/categories.json"]
    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as file_in:
                return json.load(file_in)
        except Exception:
            pass
    print("File /src/specifications.json not found")
    return None

def get_random_recipe() -> Recipe:
    return Recipe("https://www.chefkoch.de/rezepte/zufallsrezept/")
