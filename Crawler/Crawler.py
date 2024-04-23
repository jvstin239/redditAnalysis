import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import datetime
from tkinter import *
from tkinter import messagebox

class Crawler():
    def getUserPosts(self, headless, user):
        options = Options()
        if headless == 1:
            options.add_argument("--headless")
        driver = webdriver.Chrome(options = options)
        url = "https://old.reddit.com/user/" + user + "/submitted/?sort=new"
        posts = []

        driver.get(url)

        # Todo: Fehler abfangen, wenn falscher Username eingegeben wurde

        if len(driver.find_elements(By.XPATH, "//button[@value='yes']")) != 0:
            button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//button[@value='yes']")))
            button.click()
            time.sleep(0.5)
        # reiter = WebDriverWait(driver,3).until(EC.element_to_be_clickable((By.XPATH, "//link[@text='Eingereicht'")))

        html = driver.page_source

        while True:
            soup = BeautifulSoup(html, "html.parser")
            for post in soup.select(".thing"):
                if post['data-type'] == "link":
                    subreddit = post['data-subreddit']
                    caption = post.select(".title")[1].text
                    upvotes = post["data-score"]
                    domain = post.select_one(".domain").select_one("a").text
                    if post["data-nsfw"] == "true":
                        nsfw = "NSFW"
                    else:
                        nsfw = "SFW"
                    zeittest = post["data-timestamp"]
                    date = datetime.datetime.fromtimestamp(int(zeittest)/1e3)
                    day = date.strftime("%d.%m.%y")
                    hours = date.strftime("%H:%M")
                    id = post["id"]
                    comments = post["data-comments-count"]
                    post_link = "https://www.reddit.com" + post["data-permalink"]
                    if len(post.select(".pinned-tagline")) == 0:
                        pinned = False
                    else:
                        pinned = True
                    posts.append([pinned, id, str(day),str(hours), subreddit, upvotes, caption, comments, domain, post_link, nsfw])
            if len(driver.find_elements(By.CLASS_NAME, "next-button")) == 0:
                break
            next_button = driver.find_element(By.CLASS_NAME, "next-button")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            next_button.click()
            time.sleep(0.8)
            html = driver.page_source
        return posts

    def getSubredditUsers (self, sort , number, subreddits):
        # sort ist für neu oder beliebt
        # span soll die Zeitspanne in Monaten sein, bis zu der gescraped werden soll
        driver = webdriver.Chrome()
        users = {}
        for subreddit in subreddits:
            url = "https://old.reddit.com/r/" + subreddit + "/" + sort
            # Todo: Rechtschreibung Community abfangen
            driver.get(url)
            if len(driver.find_elements(By.XPATH, "//button[@value='yes']")) != 0:
                button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//button[@value='yes']")))
                button.click()
                time.sleep(0.5)
            while len(users) < number:
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                for post in soup.select(".thing"):
                    try:
                        author = post.select_one(".author").text
                        if author not in users:
                            users[author] = "https://www.reddit.com/user/" + author
                    except AttributeError:
                        print("Das folgende Element hat keinen Author:")
                        print(post)
                        time.sleep(1)
                try:
                    next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "next-button")))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                    next_button.click()
                    time.sleep(0.8)
                except:
                    print("Next-Button nicht mehr auffindbar. Scraping bei " + subreddit + " abgeschlossen. User in der Liste: " + str(len(users)))
                    break
        return users

    def getLinksandKarma(self, users, filter):
        i = 1
        options = Options()
        # options.add_argument("--headless")
        driver = webdriver.Chrome(options = options)
        user_neu = []
        driver.get("https://www.reddit.com/login/")
        login_username = "purplegiraffe239"
        login_password = "dragonfire5"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "loginUsername")))
        driver.find_element(By.ID, "loginUsername").send_keys(login_username)
        time.sleep(3.4)
        driver.find_element(By.ID, "loginPassword").send_keys(login_password)
        time.sleep(5)
        driver.find_element(By.CLASS_NAME, "AnimatedForm__submitButton").click()
        time.sleep(7)

# anpassen auf liste und dictionary
        if type(users) is list:
            for user in users:
                time.sleep(2)
                driver.get(user[1])
                time.sleep(2)
                karma = 0
                element = user
                if len(driver.find_elements(By.XPATH, "//button[@value='yes']")) != 0:
                    button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@value='yes']")))
                    button.click()
                    time.sleep(0.5)
                WebDriverWait(driver, 2.5).until(EC.presence_of_element_located((By.CLASS_NAME, "_1lOZXPReVOD51n7jOVp3q4")))
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                try:
                    linklist = soup.select("._3hew1NnzwygOKDNQDKp6R4 ")
                    karma = int(soup.select_one("._1hNyZSklmcC7R_IfCUcXmZ").text.replace(",", ""))
                    element.append(karma)
                    for link in linklist:
                        onlyfans = ""
                        insta = ""
                        twitter = ""
                        if "onlyfans" in link.select_one("a")["href"]:
                            onlyfans = link.select_one("a")["href"]
                        if "instagram" in link.select_one("a")["href"]:
                            insta = link.select_one("a")["href"]
                        if "twitter" in link.select_one("a")["href"]:
                            twitter = link.select_one("a")["href"]
                        element.append(onlyfans)
                        element.append(insta)
                        element.append(twitter)
                except:
                    # print("Es ist ein Fehler aufgetreten bei folgendem Element: " + soup.text)
                    # print(user[0])
                    continue

                if filter == 1:
                    if element[3] != "" or element[4] != "" or element[5] != "":
                        user_neu.append(element)
                elif filter == 2:
                    if element[4] != "" or element[5] != "":
                        user_neu.append(element)
                elif filter == 3:
                    if element[4] != "":
                        user_neu.append(element)

                if i % 50 == 0:
                    print(str(i) + " von " + str(len(users)))
                i += 1

        if type(users) is dict:
            for key, value in users.items():
                time.sleep(2)
                driver.get(value)
                time.sleep(2)
                karma = 0
                element = [key, value]
                if len(driver.find_elements(By.XPATH, "//button[@value='yes']")) != 0:
                    button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@value='yes']")))
                    button.click()
                    time.sleep(0.5)
                try:
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "_1lOZXPReVOD51n7jOVp3q4")))
                    html = driver.page_source
                    soup = BeautifulSoup(html, "html.parser")
                    try:
                        linklist = soup.select("._3hew1NnzwygOKDNQDKp6R4 ")
                        karma = int(soup.select_one("._1hNyZSklmcC7R_IfCUcXmZ").text.replace(",", ""))
                        element.append(karma)
                        of = ""
                        insta = ""
                        twitter = ""
                        for link in linklist:
                            if "onlyfans" in link.select_one("a")["href"]:
                                of = link.select_one("a")["href"]
                            if "instagram" in link.select_one("a")["href"]:
                                insta = link.select_one("a")["href"]
                            if "twitter" in link.select_one("a")["href"]:
                                twitter = link.select_one("a")["href"]
                        element.append(of)
                        element.append(insta)
                        element.append(twitter)
                    except:
                        print("Es ist ein Fehler aufgetreten bei folgendem Element: " + soup.text)
                        continue
                except selenium.common.exceptions.TimeoutException:
                    # print("Keine Links vorhanden bei folgendem User:")
                    # print(key)
                    continue

                if filter == 1:
                    if element[3] != "" or element[4] != "" or element[5] != "":
                        user_neu.append(element)
                elif filter == 2:
                    if element[4] != "" or element[5] != "":
                        user_neu.append(element)
                elif filter == 3:
                    if element[4] != "":
                        user_neu.append(element)

                if i % 50 == 0:
                    print(str(i) + " von " + str(len(users)))
                i += 1

        window = Tk()
        window.eval("tk::PlaceWindow %s center" % window.winfo_toplevel())
        window.withdraw()
        messagebox.showinfo("Fertig", "Die User wurden erfolgreich gescraped!")
        return user_neu

    def get_top_captions_of_subreddit(self, subreddits, count):
        driver = webdriver.Chrome()
        # daten = []
        captions = []
        for subreddit in subreddits:
            driver.get("https://old.reddit.com/r/" + subreddit + "/top/?t=month")
            time.sleep(0.5)
            if len(driver.find_elements(By.XPATH, "//button[@value='yes']")) != 0:
                button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@value='yes']")))
                button.click()
                time.sleep(0.5)
            while len(captions) < count*(subreddits.index(subreddit)+1):
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                for post in soup.select(".thing"):
                    # captions.append(post.select(".title")[1].text)
                    caption = post.select(".title")[1].text
                    captions.append([subreddit, caption])
                    if len(captions) >= count*(subreddits.index(subreddit)+1):
                        break
                try:
                    next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "next-button")))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                    next_button.click()
                    time.sleep(0.8)
                except:
                    print("Next-Button nicht mehr auffindbar. Scraping bei " + subreddit)
                    break
            # daten.append(captions)

        return captions

    def crawler_research(self, subredditlist, profilecount, cutstring):
        research_list = []
        driver = webdriver.Chrome()
        profiles = []
        cutstring.append("u_")
        cutstring.append("fan")
        cutstring.append("dick")
        cutstring.append("arab")
        cutstring.append("spread")
        cutstring.append("pussy")
        cutstring.append("vagina")
        cutstring.append("hole")
        cutstring.append("asshole")
        cutstring.append("labia")
        cutstring.append("beef")
        cutstring.append("trans")
        cutstring.append("gay")
        cutstring.append("couple")
        cutstring.append("asian")
        cutstring.append("anal")
        cutstring.append("hardcore")
        cutstring.append("blowjob")
        cutstring.append("sex")
        cutstring.append("gone")
        cutstring.append("cum")
        cutstring.append("public")
        cutstring.append("riding")
        cutstring.append("bdsm")
        cutstring.append("fetish")
        cutstring.append("grool")
        cutstring.append("hair")
        cutstring.append("clit")
        cutstring.append("porn")
        cutstring.append("fuck")
        for sub in subredditlist:
            i = 0
            driver.get("https://old.reddit.com/r/" + sub + "/top/?t=month")
            if len(driver.find_elements(By.XPATH, "//button[@value='yes']")) != 0:
                button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@value='yes']")))
                button.click()
                time.sleep(0.5)
            while i <= profilecount*(subredditlist.index(sub)+1):
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                for post in soup.select(".thing"):
                    try:
                        user = post.select_one(".author").text
                    except:
                        continue
                    if user not in profiles:
                        profiles.append(user)
                        i = i + 1
                try:
                    next_button = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.CLASS_NAME, "next-button")))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                    next_button.click()
                    time.sleep(0.8)
                except:
                    break

        for profile in profiles:
            driver.get("https://old.reddit.com/user/" + profile + "/submitted/?sort=new")

            if len(driver.find_elements(By.XPATH, "//button[@value='yes']")) != 0:
                button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@value='yes']")))
                button.click()
                time.sleep(0.5)

            for i in range(1, 5):

                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")

                for post in soup.select(".thing"):
                    sr = post['data-subreddit']
                    if sr not in research_list:
                        research_list.append(sr)
                    for word in cutstring:
                        if word in sr:
                            research_list.remove(sr)
                            break
                try:
                    next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "next-button")))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                    next_button.click()
                    time.sleep(0.8)
                except:
                    break
        return research_list

    def checkSubReddits(self, subreddits):
        driver = webdriver.Chrome()
        verified_list = []
        new_list = []
        for subreddit in subreddits:
            driver.get("https://old.reddit.com/r/" + subreddit)
            if len(driver.find_elements(By.XPATH, "//button[@value='yes']")) != 0:
                button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@value='yes']")))
                button.click()
            html = driver.page_source
            if "verify" in html or "verification" in html or "approved" in html or "verified" in html:
                verified_list.append(subreddit)
                continue
            soup = BeautifulSoup(html, "html.parser")
            number = soup.select_one(".number").text
            number = number.replace(".", "")
            if int(number) < 40000:
                continue
            new_list.append(subreddit)

        return new_list, verified_list

    def checkSubredditsforSizeAndWords(self, subreddits, size, active):
        cutstring = []
        cutstring.append("u_")
        cutstring.append("fan")
        cutstring.append("dick")
        cutstring.append("arab")
        cutstring.append("spread")
        cutstring.append("pussy")
        cutstring.append("vagina")
        cutstring.append("hole")
        cutstring.append("asshole")
        cutstring.append("labia")
        cutstring.append("beef")
        cutstring.append("trans")
        cutstring.append("gay")
        cutstring.append("couple")
        cutstring.append("asian")
        cutstring.append("anal")
        cutstring.append("hardcore")
        cutstring.append("blowjob")
        cutstring.append("sex")
        cutstring.append("gone")
        cutstring.append("cum")
        cutstring.append("public")
        cutstring.append("riding")
        cutstring.append("bdsm")
        cutstring.append("fetish")
        cutstring.append("grool")
        cutstring.append("hair")
        cutstring.append("clit")
        cutstring.append("porn")
        cutstring.append("fuck")
        cutstring.append("veri")
        cutstring.append("cuck")
        cutstring.append("black")
        cutstring.append("BBC")
        cutstring.append("Fans")
        result_list = []
        numbers = []
        onlines = []
        driver = webdriver.Chrome()

        for subreddit in subreddits:
            for string in cutstring:
                if string in subreddit:
                    subreddits.remove(subreddit)

        for subreddit in subreddits:
            url = "https://old.reddit.com/r/" + subreddit
            driver.get(url)
            if len(driver.find_elements(By.XPATH, "//button[@value='yes']")) != 0:
                button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@value='yes']")))
                button.click()
                time.sleep(0.5)
            try:
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                number = int(soup.select(".number")[0].text.strip().replace(".", ""))
                online = int(soup.select(".number")[1].text.strip().replace(".", ""))
                if number < size:
                    continue
                if online < active:
                    continue
                numbers.append(number)
                onlines.append(online)
                result_list.append(subreddit)
            except:
                subreddits.remove(subreddit)
                continue
            time.sleep(0.2)
        return result_list, numbers, onlines