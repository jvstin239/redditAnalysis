import csv

class CSV_WRITER():
    def __init__(self, datei):
        self.datei = datei
        self.array = []

    def create_user_posts(self):
        with open(self.datei,"w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f, delimiter = ";", quotechar= '"')
            writer.writerow(["Pinned", "ID", "day", "time", "subreddit", "upvotes", "caption", "comments", "domain", "post-link", "nsfw"])

    def create_user_list(self):
        with open(self.datei, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f, delimiter = ";", quotechar= '"')
            writer.writerow(["username", "link", "karma", "Onlyfans", "Instagram", "Twitter"])

    def write(self):
        with open(self.datei,"a", encoding="utf-8", newline='') as f:
            writer = csv.writer(f, delimiter=";", quotechar='"')
            for line in self.array:
                writer.writerow(line)

    def set_array(self, array):
        self.array = array

    def create_captions_list(self):
        with open(self.datei, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f, delimiter = ";", quotechar= '"')
            writer.writerow(["username", "Subreddit", "Captions"])


    # def anhängen(self, wkn, aktie):
    #     self.daten.append([wkn, aktie, "https://www.ariva.de/hebelprodukte/" + wkn])

