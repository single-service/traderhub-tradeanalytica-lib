import json

from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver

import requests
from bs4 import BeautifulSoup
from string import digits





SELENIUM_URL = "http://0.0.0.0:4444/wd/hub" # 7900


class EconomicCalendar:

    def __init__(self, selenium_url):
        self.base_url = "https://alfaforex.ru/economic-calendar/"
        self.selenium_url = selenium_url
        print("Инициируем драйвер")
        self.driver = self._initialize_driver()
        print("Драйвер инициализирован")

    def get_default_chrome_options(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        return options

    def _initialize_driver(self):
        """Инициализация Selenium WebDriver в headless-режиме."""
        driver = None
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            # Подключение к удаленному chromedriver
            driver = webdriver.Remote(
                command_executor=self.selenium_url,
                options=chrome_options
            )
        except WebDriverException as e:
            print(f"Ошибка инициализации драйвера: {e}")
        return driver
    
    def parse(self):
        html_content = self.downlad_html()
        news_data = self.parse_html_news(html_content)
        return news_data
    
    def downlad_html(self):
        try:
            # Переходим на сайт
            print("Переходим по ссылке", self.base_url)
            self.driver.get(self.base_url)
            print("Ждем появления")
            # Ожидаем появление видимых элементов td с классом trading-table__cell
            wait = WebDriverWait(self.driver, 10)  # таймаут ожидания 10 секунд
            try:
                cells = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "td.trading-table__cell")))
            except Exception:
                print("не дождались")
            # Получаем полный HTML-код страницы
            print("Скачиваем страницу")
            page_html = self.driver.page_source
            
            # Сохраняем в файл
            print("Страница скачана")
                
        finally:
            # Закрываем браузер
            self.driver.quit()
        return page_html
    
    def _parse_month(self, month_name):
        monthes = [
            "января", "февраля", "декабря", 
            "марта", "апреля", "мая", 
            "июня", "июля", "августа", 
            "сентября", "октября", "ноября", 
        ]
        month_index = monthes.index(month_name.lower()) + 1
        if month_index < 10:
            month_index = f"0{month_index}"
        return month_index
    
    def _get_children(self, element):
        return [child for child in element.contents if child != "\n"]
    
    def get_value_data(self, value):
        uom = ""
        for i in range(len(value) -1, -1, -1):
            char = value[i]
            if char not in digits:
                uom += char
            else:
                break
        uom = uom[::-1]
        value = float(value[:len(value)-len(uom)].replace(",", "."))
        return uom, value
    
    def _get_volatility_index(self, volatility_name):
        names = [
            "Ожидается низкая волатильность",
            "Ожидается умеренная волатильность",
            "Ожидается высокая волатильность"
        ]
        if not volatility_name in names:
            return 0
        return names.index(volatility_name) + 1
    
    def parse_html_news(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        tbody = soup.select_one('tbody.trading-table__body')
        news_rows = tbody.select("tr")
        current_date = None
        news = []
        for element in news_rows:
            # print(element)
            class_attribute_value = element.get("class")
            if "trading-table__date-row" in class_attribute_value:
                datefield = element.select_one("td").text.split(",")[1].strip().split(" ")
                month_day = int(datefield[0])
                if month_day < 10:
                    month_day = f"0{month_day}"
                year = datefield[2]
                month = self._parse_month(datefield[1])
                current_date = f"{year}-{month}-{month_day}"
            elif "trading-table__row" in class_attribute_value:
                news_id = element.get("data-idecocalendar")
                cells = element.select("td")
                time_value = self._get_children(cells[0])[1].text.strip()
                symbol = self._get_children(cells[2])[1].text.strip()
                volatilyty = self._get_volatility_index(
                    self._get_children(cells[3])[1].get("title")
                )
                event_name = self._get_children(cells[4])[1].text.strip()
                fact_value = self._get_children(cells[5])[1].text.strip()
                uom = ""
                if fact_value == "-":
                    fact_value = None
                else:
                    c_uom, fact_value = self.get_value_data(fact_value)
                    if not uom and c_uom:
                        uom = c_uom
                predict_value = self._get_children(cells[6])[1].text.strip()
                if predict_value == "-":
                    predict_value = None
                else:
                    c_uom, predict_value = self.get_value_data(predict_value)
                    if not uom and c_uom:
                        uom = c_uom
                previous_value = self._get_children(cells[7])[1].text.strip()
                if previous_value == "-":
                    previous_value = None
                else:
                    c_uom, previous_value = self.get_value_data(previous_value)
                    if not uom and c_uom:
                        uom = c_uom
                news.append({
                    "internal_id": news_id,
                    "news_dt": f"{current_date} {time_value}:00",
                    "symbol": symbol,
                    "volatilyty": volatilyty,
                    "event_name": event_name,
                    "uom": uom,
                    "fact_value": fact_value,
                    "predict_value": predict_value,
                    "previous_value": previous_value,
                })
            else:
                print("new class", class_attribute_value)
        return news


    def close_driver(self):
        try:
            self.driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    parser = EconomicCalendar(SELENIUM_URL)
    news_data = parser.parse()
    with open("news.json", "w") as json_file:
        json.dump(news_data, json_file, ensure_ascii=False, indent=3)