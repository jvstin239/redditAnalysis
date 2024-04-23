from Analyzer.Reader import Reader
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup

class PostAutomat():
    def imgur_Upload(self):
        links = []
        reader = Reader()
        options = Options()
        options.add_argument("--headless")
        file = reader.open_explorer()
        count = input("Wie oft soll die Datei hochgeladen werden: ")
        driver = webdriver.Chrome(options = options)

        for i in range(0, int(count)):
            driver.get("https://imgur.com/upload")
            driver.implicitly_wait(3)
            try:
                input_field = driver.find_element(By.ID, "file-input")
                input_field.send_keys(file)
                time.sleep(1)
            except:
                print("File upload war nicht möglich!")
                break

            try:
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "DisableAudioDialog-remove"))).click()
                time.sleep(15)
            except:
                print("Remove Audio Button konnte nicht gedrückt werden")
                # Todo: Überprüfen, wann die Datei hochgeladen ist. Dann link holen und mit .gifv austauschen und printen
            try:
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "PostVideo")))
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                link = soup.select_one("source")["src"]
                links.append(link[:-3] + "gifv")
            except:
                print("Upload Timeout!")
        # print(links)
        return links
