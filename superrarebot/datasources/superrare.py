import json
import logging
from dataclasses import dataclass, field
from multiprocessing.pool import Pool
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from superrarebot.config import BASE_DIR

DRIVER_OPTIONS = Options()
DRIVER_OPTIONS.headless = True
DB_JSON = Path(BASE_DIR).joinpath("db.json")

log = logging.getLogger(__name__)


@dataclass
class Action:
    description: str
    transaction_id: str


@dataclass
class Creation:
    name: str
    url: str
    image_url: str = ""
    actions: list[Action] = field(default_factory=lambda: [])

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    @staticmethod
    def from_dict(creation_dict):
        return Creation(
            name=creation_dict["name"],
            url=creation_dict["url"],
            actions=[
                Action(action["description"], action["transaction_id"])
                for action in creation_dict["actions"]
            ],
        )


class CreationEncoder(json.JSONEncoder):
    item_separator = ","
    key_separator = ":"

    def default(self, o):
        return o.__dict__


def _populate_image_and_actions(creation: Creation) -> Creation:
    with webdriver.Firefox(options=DRIVER_OPTIONS) as driver:
        actions = []
        driver.get(creation.url)

        log.debug(f"Populating image and actions for {creation.name}")

        try:
            image = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".collectible-detail-image")
                )
            )
            src = image.get_attribute("src")
            creation.image_url = src
        except TimeoutException:
            pass

        try:
            actions = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, ".collectible-history-item")
                )
            )
            actions.reverse()  # Sorts actions from oldest to newest
        except TimeoutException:
            return

        for action in actions:
            description = None
            transaction_id = None

            try:
                description = action.find_element(
                    By.CSS_SELECTOR, ".collectible-history-item-action"
                ).text
            except NoSuchElementException:
                continue

            try:
                transaction_url = action.find_element(
                    By.CSS_SELECTOR, ".collectible-history-item-link"
                ).get_attribute("href")
                _, transaction_id = transaction_url.split("https://etherscan.io/tx/")
            except NoSuchElementException:
                pass

            creation.actions.append(Action(description, transaction_id))

    return creation


def get_creations(superrare_artist):
    creations: list[Creation] = []

    log.debug(f"Fetching creations from {superrare_artist} on SuperRare")

    with webdriver.Firefox(options=DRIVER_OPTIONS) as driver:
        driver.get(f"https://superrare.com/{superrare_artist}/creations")

        try:
            creation_links = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, ".collectible-card .collectible-card__name")
                )
            )
            for link in creation_links:
                name = link.text
                url = link.get_attribute("href")
                creations.append(Creation(name, url))
        except TimeoutException:
            return None

    # When looking up the history for each creation, use multithreading
    # This will speed up the process
    pool = Pool(processes=len(creations))
    creations = pool.map(_populate_image_and_actions, creations)
    pool.close()
    pool.join()

    return creations


def get_local_creations() -> list[Creation]:
    if not DB_JSON.exists():
        return []

    with DB_JSON.open() as file:
        creation_list = json.load(file)
        return [Creation.from_dict(dict) for dict in creation_list]


def save_creations_to_file(creations: list[Creation]):
    creation_json = json.dumps(creations, cls=CreationEncoder)
    with DB_JSON.open("w", encoding="utf-8") as file:
        file.write(creation_json)
