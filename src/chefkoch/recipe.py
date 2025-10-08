""" This module provides a class to scrape recipes from chefkoch.de """

import datetime
import json
from functools import cached_property
from typing import List, Optional

import isodate
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.chefkoch.de/rezepte"


class Recipe:
    """
    Represents a recipe from Chefkoch website.

    Attributes:
        url (str): The URL of the recipe.
        id (str): The ID of the recipe.

    Properties:
        title (str): The title of the recipe.
        image_url (str): The URL of the recipe's image.
        image_base64 (bytes): The base64-encoded content of the recipe's image.
        image_urls (List[str]): The URLs of all images associated with the recipe.
        date_published (datetime.datetime): The date when the recipe was published.
        prep_time (isodate.Duration): The preparation time of the recipe.
        cookTime (isodate.Duration): The cooking time of the recipe.
        totalTime (isodate.Duration): The total time required to prepare the recipe.
        difficulty (str): The difficulty level of the recipe.
        ingredients (List[str]): The list of ingredients required for the recipe.
        instructions (List[str]): The list of instructions to prepare the recipe.
        publisher (str): The name of the publisher of the recipe.
        calories (str): The number of calories in the recipe.
        keywords (str): The keywords associated with the recipe.
        number_reviews (int): The number of reviews for the recipe.
        number_ratings (int): The number of ratings for the recipe.
        rating (float): The average rating of the recipe.
        category (str): The category of the recipe.
    """

    def __init__(self, url: Optional[str] = None, id: Optional[str] = None, allow_premium: bool = False):
        """
        Initializes a Recipe object. Will raise an error if the recipe is premium and allow_premium is False.

        Args:
            url (str, optional): The URL of the recipe. Defaults to None.
            id (str, optional): The ID of the recipe. Defaults to None.
            allow_premium (bool, optional): Whether to allow premium recipes. Defaults to False.

        Raises:
            ValueError: If neither url nor id is provided.
            ValueError: If the url is invalid.
        """

        if url is None and id is None:
            raise ValueError("Either url or id must be provided")

        if id is not None:
            url = f"{BASE_URL}/{id}"

        if not BASE_URL in url:
            raise ValueError("Invalid url")

        if id is None:
            id = url.split("/")[4]

        self.url: str = url
        self.id: str = id

        if not allow_premium and self.is_premium:
            raise ValueError("This is a premium recipe. Set allow_premium to True to allow premium recipes.")

    @cached_property
    def __info_dict(self):
        """
        Returns the information dictionary of the recipe.

        Returns:
            dict: The information dictionary of the recipe.
        """
        info_dict_str = self.__soup.findAll("script", type="application/ld+json")[1].text
        info_dict_str = info_dict_str.encode("utf-8").decode("utf-8")
        return json.loads(info_dict_str)

    @cached_property
    def __soup(self) -> BeautifulSoup:
        """
        Returns the BeautifulSoup object of the recipe's webpage.

        Returns:
            BeautifulSoup: The BeautifulSoup object of the recipe's webpage.
        """
        response = requests.get(self.url)
        return BeautifulSoup(response.content, "html.parser")

    @cached_property
    def title(self) -> str:
        """
        Returns the title of the recipe.

        Returns:
            str: The title of the recipe.

        Raises:
            ValueError: If the title is not found.
        """
        text: str = self.__soup.find("h1").text
        if text:
            return text
        raise ValueError("Title not found")

    @cached_property
    def is_premium(self) -> bool:
        """
        Returns whether the recipe is a premium recipe.

        Returns:
            bool: True if the recipe is a premium recipe, False otherwise.
        """
        plus_element = self.__soup.find(attrs={"aria-label": "Chefkoch PLUS"})
        return plus_element is not None

    @cached_property
    def image_url(self) -> str:
        """
        Returns the URL of the recipe's image.

        Returns:
            str: The URL of the recipe's image.

        Raises:
            ValueError: If the image is not found.
        """
        image: str = self.__soup.find("amp-img").find("img")["src"]
        if image:
            return image
        raise ValueError("Image not found")

    @cached_property
    def image_base64(self) -> bytes:
        """
        Returns the base64-encoded content of the recipe's image.

        Returns:
            bytes: The base64-encoded content of the recipe's image.
        """
        response = requests.get(self.image_url)
        return response.content

    @cached_property
    def image_urls(self) -> List[str]:
        """
        Returns the URLs of all images associated with the recipe.

        Returns:
            List[str]: The URLs of all images associated with the recipe.
        """
        response = requests.get(f"{BASE_URL}/bilderuebersicht/{self.id}")
        image_soup = BeautifulSoup(response.content, "html.parser")
        image_div = image_soup.find("div", {"class": "recipe-images"})
        return [img["src"] for img in image_div.find_all("amp-img")]

    @cached_property
    def date_published(self) -> datetime.datetime:
        """
        Returns the date when the recipe was published.

        Returns:
            datetime.datetime: The date when the recipe was published.
        """
        date_string = self.__info_dict["datePublished"]  # format 2014-04-13
        date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
        return date

    @cached_property
    def prep_time(self) -> isodate.Duration:
        """
        Returns the preparation time of the recipe.

        Returns:
            isodate.Duration: The preparation time of the recipe.
        """
        time_str = self.__info_dict["prepTime"]  # format P0DT0H5M
        return isodate.parse_duration(time_str)

    @cached_property
    def cook_time(self) -> isodate.Duration:
        """
        Returns the cooking time of the recipe.

        Returns:
            isodate.Duration: The cooking time of the recipe.
        """
        time_str = self.__info_dict["cookTime"]
        return isodate.parse_duration(time_str)

    @cached_property
    def total_time(self) -> isodate.Duration:
        """
        Returns the total time required to prepare the recipe.

        Returns:
            isodate.Duration: The total time required to prepare the recipe.
        """
        time_str = self.__info_dict["totalTime"]
        return isodate.parse_duration(time_str)

    @cached_property
    def difficulty(self) -> str:
        """
        Returns the difficulty level of the recipe.

        Returns:
            str: The difficulty level of the recipe.
        """
        return self.__soup.find("span", {"class": "recipe-difficulty"}).text.split()[-1]

    @cached_property
    def ingredients(self):
        """
        Returns the list of ingredients required for the recipe.

        Returns:
            List[str]: The list of ingredients required for the recipe.
        """
        return self.__info_dict.get("recipeIngredient", [])

    @cached_property
    def instructions(self):
        """
        Returns the list of instructions to prepare the recipe.

        Returns:
            List[str]: The list of instructions to prepare the recipe.
        """
        return self.__info_dict.get("recipeInstructions", [])

    @cached_property
    def publisher(self):
        """
        Returns the name of the publisher of the recipe.

        Returns:
            str: The name of the publisher of the recipe.
        """
        return self.__info_dict.get("publisher", {}).get("name", "")

    @cached_property
    def author(self):
        """
        Returns the name of the author of the recipe.

        Returns:
            str: The name of the author of the recipe.
        """
        author = self.__info_dict.get("author", {})
        if isinstance(author, dict):
            return author.get("name", "")
        elif isinstance(author, list) and author:
            # Sometimes 'author' can be a list of dicts
            return author[0].get("name", "")
        return ""

    @cached_property
    def calories(self):
        """
        Returns the number of calories in the recipe.

        Returns:
            str: The number of calories in the recipe.
        """
        return self.__info_dict.get("nutrition", {}).get("calories", "")

    @cached_property
    def keywords(self):
        """
        Returns the keywords associated with the recipe.

        Returns:
            str: The keywords associated with the recipe.
        """
        return self.__info_dict.get("keywords", "")

    @cached_property
    def number_reviews(self):
        """
        Returns the number of reviews for the recipe.

        Returns:
            int: The number of reviews for the recipe.
        """
        return self.__info_dict.get("aggregateRating", {}).get("reviewCount", 0)

    @cached_property
    def number_ratings(self):
        """
        Returns the number of ratings for the recipe.

        Returns:
            int: The number of ratings for the recipe.
        """
        return self.__info_dict.get("aggregateRating", {}).get("ratingCount", 0)

    @cached_property
    def rating(self):
        """
        Returns the average rating of the recipe.

        Returns:
            float: The average rating of the recipe.
        """
        return self.__info_dict.get("aggregateRating", {}).get("ratingValue", 0.0)

    @cached_property
    def category(self):
        """
        Returns the category of the recipe.

        Returns:
            str: The category of the recipe.
        """
        return self.__info_dict.get("recipeCategory", "")


if __name__ == "__main__":
    recipe = Recipe(url="https://www.chefkoch.de/rezepte/4168421666771617/Lammschulter-in-Wermutfond.html", allow_premium=False)
    print(recipe.title)
    print(recipe.is_premium)