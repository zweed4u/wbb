#!/usr/bin/python3

import os
import re
import requests
import configparser
from bs4 import BeautifulSoup


class Warez:
    def __init__(self):
        self.session = requests.session()

    def _get_session_id(self):
        response = self.session.get('https://www.warez-bb.org/login.php', headers={'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'})
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        pattern = "var SID = '\w+'"
        matched_pattern = re.search(pattern, response.content.decode()).group()
        matched_pattern = re.search("'\w+'", matched_pattern).group()
        sid_from_js = re.search("\w+", matched_pattern).group()

        # Non-regex way
        # sid_from_js = [str(script_tagged_element.text.decode().strip()) for script_tagged_element in soup.find_all('script') if 'var SID' in script_tagged_element.text][0]        
        login_path = soup.find_all('form')[0]['action']
        sid_from_form_action = login_path.split('?sid=')[-1]
        assert sid_from_js == sid_from_form_action, 'Received mismatched session id between login form action url and javascript variable'
        return sid_from_js

    def login(self, username, password):
        payload = {
            'username': username,
            'password': password,
            'autologin': 'on',
            'redirect': '',
            'login': 'Log in'
        }
        response = self.session.post('https://www.warez-bb.org/login.php', params={'sid':self._get_session_id()}, data=payload, headers={'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'})
        response.raise_for_status()
        assert 'You have successfully logged in' in response.content.decode(), 'Unable to find successful log in notification after POSTing'

        response = self.session.get('https://www.warez-bb.org/index.php', headers={'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'})
        response.raise_for_status()
        regexp = re.compile(username)
        assert regexp.search(response.content.decode()), 'Unable to find supposed logged in username on main page'

    def default_search(self, keywords):
        # todo - flesh out payload and support better search/filtering
        payload = {
            'search_keywords': keywords,
            'search_terms': 'all',
            'search_author': '',
            # Multiple values - https://stackoverflow.com/a/23384253
            'search_forum[]': [2,108,40,112,3,5,28,4,57,88,6,38,7,8,91,83,105,106,20,113,15,17,16,18,19,11,76,30,10,92,102,85,12,22,118,63,97,79,26],
            'search_time': 0,
            'search_fields': 'titleonly',
            'sort_by': 0,
            'sort_dir': 'DESC',
            'show_results': 'topics',
            'return_chars': 200
        }
        response = self.session.post('https://www.warez-bb.org/search.php', params={'mode':'results'}, data=payload, headers={'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'})
        response.raise_for_status()
        print(response.content.decode())
        # todo check rows here and return urls to posts

root_directory = os.getcwd()
cfg = configparser.ConfigParser()
configFilePath = os.path.join(root_directory, 'config.cfg')
cfg.read(configFilePath)

wbb = Warez()
wbb.login(cfg.get('login', 'username'), cfg.get('login', 'password'))
keywords = input('Enter search keywords: ')
wbb.default_search(keywords)
