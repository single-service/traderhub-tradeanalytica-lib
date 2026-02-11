import json

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md


class ForexAnalyse:

    def __init__(self):
        self.host = "https://www.fxclub.org"

    def collect(self):
        resp = requests.get(f"{self.host}/markets-data")
        articles = self.parse_base_html(resp.content)
        for article in articles:
            article["content"] = self.collect_article(article["url"])
        return articles

    def parse_base_html(self, content):
        articles = []
        soup = BeautifulSoup(content, 'html.parser')
        views_element_container = soup.select_one('div.views-element-container')
        div_analytic_news = views_element_container.select_one('div.analytic-news')
        analitics_containers = div_analytic_news.select('div.space-y-2')
        for cont in analitics_containers:
            link = cont.select_one('a')
            title = link.text.strip()
            article_url = link.get("href")
            article_dt = cont.select_one('time').get("datetime")
            childs = [child for child in cont.contents if child != "\n"]
            summary = childs[-1].text.strip().replace("\n", " ")
            articles.append({
                "title": title,
                "url": article_url,
                "article_dt": article_dt,
                "summary": summary
            })
        return articles
    
    def collect_article(self, url):
        resp = requests.get(f"{self.host}{url}")
        return self.parse_article(resp.content)

    def parse_article(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        article_block = soup.select_one("div.layout__region.layout__region--first")
        md_article = md(str(article_block))
        return md_article



if __name__ == "__main__":
    analyser = ForexAnalyse()
    articles = analyser.collect()
    with open("articles.json", "w") as json_file:
        json.dump(articles, json_file, ensure_ascii=False, indent=4)
    print(f"Готово, собрано {len(articles)} статей")



