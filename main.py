from Crawler.Crawler import Crawler
from Crawler.CSV_WRITER import CSV_WRITER
import os
# from datetime import datetime
import datetime
from Analyzer.Analyzer import Analyzer
from Analyzer.Reader import Reader
import numpy as np
from PostAutomat.PostAutomat import PostAutomat
import pandas as pd
from fpdf import FPDF
from tkinter import Tk
from tkinter.filedialog import askopenfilenames


def open_file_dialog():
    Tk().withdraw()  # Hides the root window
    file_path = askopenfilenames(title="Select CSV file", filetypes=[("CSV files", "*.csv")])
    return file_path

def filter_by_date(df, start_date, end_date):
    # Convert the 'day' column to datetime format
    df['day'] = pd.to_datetime(df['day'], format='%d.%m.%y')

    # Convert input dates to datetime
    start_date = datetime.datetime.strptime(start_date, '%d.%m.%Y')
    end_date = datetime.datetime.strptime(end_date, '%d.%m.%Y')

    # Filter the dataframe by the date range
    filtered_df = df[(df['day'] >= start_date) & (df['day'] <= end_date)]

    return filtered_df


# Function to perform statistical analysis on the filtered data
def analyze_data(df):
    # Group by subreddit and calculate statistics for upvotes
    stats = df.groupby('subreddit')['upvotes'].agg(['mean', 'min', 'max', 'median']).reset_index()

    # Find the caption with the most upvotes for each subreddit
    top_captions = df.loc[df.groupby('subreddit')['upvotes'].idxmax()][['subreddit', 'upvotes', 'caption']]

    return stats, top_captions


def generate_pdf(stats, top_captions, threshold, file_name):
    # Define the directory and file path
    directory = "/Users/justinwild/Downloads/Analysen/"
    file_path = os.path.join(directory, file_name)

    # Check if the directory exists, if not, create it
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Generate the PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Arial", 'B', 14)  # Set title font size
    pdf.cell(200, 10, txt="Reddit Upvotes Analysis Report", ln=True, align='C')

    # Add the statistics section
    pdf.set_font("Arial", 'B', 12)  # Set larger font for section title
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Statistical Analysis of Upvotes by Subreddit (Threshold: {threshold}):", ln=True, align='L')

    # Table Headers for statistics
    pdf.set_font("Arial", 'B', 10)  # Larger font for the table header
    cell_height = 6  # Define smaller cell height
    pdf.cell(30, cell_height, "Subreddit", 1)
    pdf.cell(30, cell_height, "Mean", 1)
    pdf.cell(30, cell_height, "Min", 1)
    pdf.cell(30, cell_height, "Max", 1)
    pdf.cell(30, cell_height, "Median", 1)
    pdf.ln()

    # Table rows for statistics, rounding values to integers
    pdf.set_font("Arial", '', 10)  # Larger font for the table rows
    for _, row in stats.iterrows():
        # Check if the mean is below the threshold
        if row['mean'] < threshold:
            # Set fill color to light red for cells that meet the condition
            pdf.set_fill_color(255, 102, 102)  # Light red
            fill = True
        else:
            # No fill for cells that don't meet the condition
            fill = False

        # Output the row with conditional coloring
        pdf.cell(30, cell_height, row['subreddit'], 1, 0, '', fill)
        pdf.cell(30, cell_height, f"{round(row['mean'])}", 1, 0, '', fill)  # Round to whole numbers
        pdf.cell(30, cell_height, f"{round(row['min'])}", 1, 0, '', fill)
        pdf.cell(30, cell_height, f"{round(row['max'])}", 1, 0, '', fill)
        pdf.cell(30, cell_height, f"{round(row['median'])}", 1, 0, '', fill)
        pdf.ln()

    # Add a new page for the captions
    pdf.add_page()

    # Add the captions with max upvotes for each subreddit
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Top Caption for Each Subreddit:", ln=True, align='L')

    # Table Headers for top captions
    pdf.set_font("Arial", 'B', 10)  # Larger font for the captions table
    pdf.cell(30, cell_height, "Subreddit", 1)
    pdf.cell(80, cell_height, "Top Caption", 1)  # Adjust width for longer captions
    pdf.cell(30, cell_height, "Upvotes", 1)
    pdf.ln()

    # Table rows for top captions, truncating long captions
    pdf.set_font("Arial", '', 10)  # Larger font for the table rows
    for _, row in top_captions.iterrows():
        pdf.cell(30, cell_height, row['subreddit'], 1)
        pdf.cell(80, cell_height, row['caption'][:60], 1)  # Truncate captions to 60 characters
        pdf.cell(30, cell_height, str(row['upvotes']), 1)
        pdf.ln()

    # Output the PDF to a file
    pdf.output(file_path)
    return file_path


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
    df = pd.DataFrame(posts, columns=['pinned', 'ID','day', 'time', 'subreddit', 'upvotes', 'caption', 'comments', 'host', 'link', 'type'])
    df.to_csv(os.path.join(folder, filename), index=False, sep=";", encoding="utf-8")
    #writer.create_user_posts()
    #writer.set_array(posts)
    #writer.write()

def get_captions_of_list_and_export(number):
    crawler = Crawler()
    reader = Reader()
    name = input("Für welches Model: ")
    # liste = reader.get_file_data()
    # array = np.array(liste)
    # subreddits = array[:, 0]
    # end_list = array[:, [0, 0]].tolist()
    df = pd.read_csv(reader.open_explorer()[0], sep=";")

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
    datanew.to_csv(os.path.join(folder, filename), index = False, sep = ";", encoding = "utf-8")
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
    eingabe = input("Gebe 0 ein, wenn du Subreddits nach der Größe sortieren willst: ")
    if (eingabe == "0"):
        sortieren = True
        size = int(input("Welche Größe soll ausgeschlossen werden: "))
        online = int(input("Wie viele sollen aktiv online sein: "))

    result = crawler.crawler_research(liste, count, cutstring)

    subs, members, online = crawler.checkSubredditsforSizeAndWords(result, size, online)
    links_only = []
    links_submit = []
    for sub in subs:
        links_only.append("https:www.reddit.com/r/" + sub)
        links_submit.append("https:www.reddit.com/r/" + sub + "/submit")
    df = pd.DataFrame(list(zip(subs, members, online, links_only, links_submit)), columns=["Subreddit","Größe", "Aktiv", "Link", "Submit"])
    now = datetime.datetime.now()
    folder = os.path.dirname(__file__)
    filename = "Research_" + model + "_" + datetime.datetime.strftime(now, "%d.%m.%y_%H%M") + ".csv"
    df.to_csv(os.path.join(folder, filename), sep = ";", index = False, encoding = "utf-8")

# Todo: Wenn eine Datei bereits besteht oder nur Daten angehänt werden sollen. Sodass zeitliche Analyse bei mehreren Läufen möglichen ist. Außerdem Unterscheidung bei mehreren Läufen täglich
# get_user_list_and_export(["FetishBabess", "FetishObscura", "SexSells", "NSFW_Selling", "hireagirlfriend", "SkypeShows", "BuyingContent", "SnapHoes"], "new", 1800, client = "Justin", filter = 3)
# get_user_posts_and_export("boastfullydead")
# automat = PostAutomat()
# links = automat.imgur_Upload()
# for link in links: print(link)


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
print("5 : Gifs konvertieren")
print("6 : Captions für user")
print("7 : Postingliste analysiseren")
print("8 : Captions in neuem Format")
print("9 : Captions mit API holen")
print("10: User Posts mit API")
print("11: Research mit API")
print("12: User von Subreddit")
choice = input("Welches Programm möchtest du ausführen: ")
if choice == "1":
    i = 0
    users = []
    while True:
        i = i + 1
        eingabe = input("Wie heißt der " + str(i) + ". User (0 zum Start): ")
        if eingabe == "0":
            break
        users.append(eingabe)
    for user in users:
        get_user_posts_and_export(user)
if choice == "2":
    automat = PostAutomat()
    links = automat.imgur_Upload()
    for link in links: print(link)
if choice == "3":
    do_research_for_model()
if choice == "4":
    number = int(input("Wie viele Captions pro subreddit: "))
    get_captions_of_list_and_export(number)
if choice == "5":
    crawler = Crawler()
    crawler.convertMultipleGifs()
if choice == "6":
    name = input("Wie heisst der User: ")
    count = int(input("Wie viele Captions pro Subreddit: "))
    crawler = Crawler()
    daten = crawler.get_captions_of_user(name, count)
    data_final = pd.DataFrame(daten, columns=['Subreddit', 'Caption'])
    now = datetime.datetime.now()
    folder = os.path.dirname(__file__)
    filename = "Captions" + "_" + name + "_" + datetime.datetime.strftime(now, "%d.%m.%y") + ".csv"
    folder = "/Users/justinwild/Downloads"
    data_final.to_csv(os.path.join(folder, filename), sep=";", index=False, encoding="utf-8")
if choice == "7":
    files = open_file_dialog()
    start_date = input("Startdatum eingeben: ")
    end_date = input("Enddatum eingeben: ")
    for file in files:
        file_name = file.split("/")[-1].split("_")[0]
        df = pd.read_csv(file, delimiter=';')
        threshold = int(input("Grenzwert nach unten für " + file_name + ": "))
        filtered_df = filter_by_date(df, start_date, end_date)
        now = datetime.datetime.now()
        # 2. Perform the analysis on the filtered data
        stats, top_captions = analyze_data(filtered_df)

        # 3. Generate the PDF and return the file path
        pdf_file_path = generate_pdf(stats, top_captions, threshold, file_name= file_name + "_" + datetime.datetime.strftime(now, "%d.%m.%y") + "_" + "report.pdf")
        print("PDF generated:", pdf_file_path)
if choice == "8":
    c = Crawler()
    c.getCaptionsFromListInRightFormat()
if choice == "9":
    c = Crawler()
    c.getCaptionsViaApi()
if choice == "10":
    c = Crawler()
    now = datetime.datetime.now()
    i = 0
    users = []
    while True:
        i = i + 1
        eingabe = input("Wie heißt der " + str(i) + ". User (0 zum Start): ")
        if eingabe == "0":
            break
        users.append(eingabe)
    for user in users:
        posts = c.getUserPostsViaAPI(user)
        folder = os.path.dirname(__file__)
        filename = user + "_" + datetime.datetime.strftime(now, "%d.%m.%y_%H%M") + ".csv"
        df = pd.DataFrame(posts,
                          columns=['pinned', 'ID', 'day', 'time', 'subreddit', 'upvotes', 'caption', 'comments', 'host',
                                   'link', 'type'])
        df.to_csv(os.path.join(folder, filename), index=False, sep=";", encoding="utf-8")
if choice == "11":
        crawler = Crawler()
        crawler.researchWithAPI()
if choice == "12":
        c = Crawler()
        c.getUserFromSubreddit("GermansGoneWild")