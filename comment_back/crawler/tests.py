from django.test import TestCase
from .crawler.selenium_crawler import *
from .crawler.crawler import *
from pprint import pprint

# get_title_with_selenium(59071959)
# pprint(test_get_all_episodes_by_series(59071959))
# pprint(get_episode_count_by_series(59071959))
# print(get_episode_by_series(59071959).get('totalCount'))

pprint(get_comments_by_episode(series_id=59071959, product_id=59114404))
