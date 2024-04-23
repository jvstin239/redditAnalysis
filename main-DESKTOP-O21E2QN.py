from Crawler.Crawler import Crawler
from Crawler.CSV_WRITER import CSV_WRITER
import os
import datetime
from Analyzer.Analyzer import Analyzer
from Analyzer.Reader import Reader
import numpy as np
from PostAutomat.PostAutomat import PostAutomat
import pandas as pd

def get_user_list_and_export(subreddits, sort, number, client, filter):
    # filter = 1: OF or Insta or Twitter
    # fitler = 2: Insta or Twitter
    # filter = 3: Only Insta
    crawler = Crawler()
    now = datetime.datetime.now()
    all_users = crawler.getSubredditUsers(sort = sort, number = number, subreddits = subreddits)
    users_complete = crawler.getLinksandKarma(all_users, filter)
    folder = os.path.dirname(__file__)
    filename = client + "_" + datetime.datetime.strftime(now, "%d.%m.%y_%H%M") + ".csv"
    writer = CSV_WRITER(os.path.join(folder, filename))
    writer.create_user_list()
    writer.set_array(users_complete)
    writer.write()

def get_user_posts_and_export(username):
    crawler = Crawler()
    posts = crawler.getUserPosts(headless = 0, user = username)
    now = datetime.datetime.now()
    folder = os.path.dirname(__file__)
    filename = username + "_" + datetime.datetime.strftime(now, "%d.%m.%y_%H%M") + ".csv"
    writer = CSV_WRITER(os.path.join(folder, filename))
    writer.create_user_posts()
    writer.set_array(posts)
    writer.write()

def get_captions_of_list_and_export(number):
    crawler = Crawler()
    reader = Reader()
    name = input("Für welches Model: ")
    # liste = reader.get_file_data()
    # array = np.array(liste)
    # subreddits = array[:, 0]
    # end_list = array[:, [0, 0]].tolist()
    df = pd.read_csv(reader.open_explorer(), sep=";")

    # Die erste Spalte als Array ausgeben
    subreddits = df.iloc[:, 0].to_list()
    daten = crawler.get_top_captions_of_subreddit(subreddits, count = number)
    # i = 0
    # for element in end_list:
    #    for caption in daten[i]:
    #        element.append(caption)
    #    i += 1
    datanew = pd.DataFrame(daten, columns=['Subreddit', 'Caption'])
    now = datetime.datetime.now()
    folder = os.path.dirname(__file__)
    filename = "Captions" + "_"+ name + "_" + datetime.datetime.strftime(now, "%d.%m.%y") + ".csv"
    datanew.to_csv(os.path.join(folder, filename), index = False)
    # writer = CSV_WRITER(os.path.join(folder, filename))
    # writer.create_captions_list()
    # writer.set_array(end_list)
    # writer.write()

def do_research_for_model():
    liste = []
    model = input("Enter models name: ")
    while True:
        subreddit = input("Gib einen Subreddit ein oder 0 zum Start: ")
        if subreddit == "0":
            if len(liste) == 0:
                print("Es muss mindestens ein Subreddit eingegeben werden!")
            else:
                break
        else:
            liste.append(subreddit)

    count = input("Wie viele Profile sollen pro Subreddit gecrwalt werden: ")
    count = int(count)
    crawler = Crawler()

    cutstring = []

    while True:
        eingabe = input("Gib ein Stichwort zum ausschließen ein oder 0 zum beginnen: ")
        if (eingabe == "0"):
            break
        else:
            cutstring.append(eingabe)
    result = crawler.crawler_research(liste, count, cutstring)
    links_only = []
    links_submit = []
    for sub in result:
        links_only.append("https:www.reddit.com/r/" + sub)
        links_submit.append("https:www.reddit.com/r/" + sub + "/submit")
    df = pd.DataFrame(list(zip(result, links_only, links_submit)), columns=["Subreddit", "Link", "Submit"])
    now = datetime.datetime.now()
    folder = os.path.dirname(__file__)
    filename = "Research_" + model + "_" + datetime.datetime.strftime(now, "%d.%m.%y_%H%M") + ".csv"
    df.to_csv(os.path.join(folder, filename), sep = ";", index = False, encoding = "utf-8")

# Todo: Wenn eine Datei bereits besteht oder nur Daten angehänt werden sollen. Sodass zeitliche Analyse bei mehreren Läufen möglichen ist. Außerdem Unterscheidung bei mehreren Läufen täglich
get_user_list_and_export(["FetishBabess","FetishObscura", "SexSells", "NSFW_Selling", "hireagirlfriend"], "new", 900, client = "Robert", filter = 3)
# get_user_posts_and_export("boastfullydead")
# automat = PostAutomat()
# links = automat.imgur_Upload()
# for link in links: print(link)
# crawler = Crawler()
# pairs = crawler.get_top_captions_of_subreddit(["bigass", "collegesluts"], 15)
# print(pairs)

# crawler = Crawler()
# liste1, liste2 = crawler.checkSubReddits(["pawg", "asstastic", "gymgirls", "gymgirlsSFW", "amihotSFW", "thickwhitegirls"])
# print(liste1)
# print(liste2)
# get_captions_of_list_and_export(12)
print("1 : Userpost Liste")
print("2 : Imgur Posts hochladen")
print("3 : Research")
print("4 : Captions aus Postingliste holen")
choice = input("Welches Programm möchtest du ausführen: ")
if choice == "1":
    get_user_posts_and_export(input("Wie heißt der User: "))
if choice == "2":
    automat = PostAutomat()
    links = automat.imgur_Upload()
    for link in links: print(link)
if choice == "3":
    do_research_for_model()
if choice == "4":
    number = int(input("Wie viele Captions pro subreddit: "))
    get_captions_of_list_and_export(number)
