import re
import os
from bs4 import BeautifulSoup
import platform
import csv
import itertools
import json

# Open config.json and fill in OPTIONAL information
json_config = json.load(open('config.json'))
json_global_settings = json_config["settings"]
export_type = json_global_settings["export_type"]
def parse_links(site_name, input_link):
    if site_name in {"onlyfans", "justforfans"}:
        username = input_link.rsplit('/', 1)[-1]
        return username

    if site_name == "4chan":
        if "catalog" in input_link:
            input_link = input_link.split("/")[1]
            print(input_link)
            return input_link
        if input_link[-1:] == "/":
            input_link = input_link.split("/")[3]
            return input_link
        if "4chan.org" not in input_link:
            return input_link


def reformat(directory, file_name, text, ext, date, username, format_path, date_format, text_length, maximum_length):
    path = format_path.replace("{username}", username)
    text = BeautifulSoup(text, 'html.parser').get_text().replace(
        "\n", " ").strip()
    filtered_text = re.sub(r'[\\/*?:"<>|]', '', text)
    path = path.replace("{text}", filtered_text)
    date = date.strftime(date_format)
    path = path.replace("{date}", date)
    path = path.replace("{file_name}", file_name)
    path = path.replace("{ext}", ext)
    directory2 = directory + path
    count_string = len(directory2)
    if count_string > maximum_length:
        num_sum = count_string - maximum_length
        directory2 = directory2.replace(
            filtered_text, filtered_text[:text_length])
    count_string = len(directory2)
    if count_string > maximum_length:
        num_sum = count_string - maximum_length
        directory2 = directory2.replace(
            filtered_text, filtered_text[:-num_sum])
        count_string = len(directory2)
        if count_string > maximum_length:
            directory2 = directory
    count_string = len(directory2)
    if count_string > maximum_length:
        num_sum = count_string - maximum_length
        directory2 = directory2.replace(
            filtered_text, filtered_text[:50])
        count_string = len(directory2)
        if count_string > maximum_length:
            directory2 = directory
    return directory2


def format_media_set(media_set):
    x = {}
    x["valid"] = []
    x["invalid"] = []
    for y in media_set:
        x["valid"].extend(y[0])
        x["invalid"].extend(y[1])
    return x


def format_image(directory, timestamp):
    os_name = platform.system()
    if os_name == "Windows":
        from win32_setctime import setctime
        setctime(directory, timestamp)


def export_archive(data, archive_directory):
    # Not Finished
    if export_type == "json":
        with open(archive_directory+".json", 'w') as outfile:
            json.dump(data, outfile)
    if export_type == "csv":
        with open(archive_directory+'.csv', mode='w',encoding='utf-8', newline='') as csv_file:
            fieldnames = []
            if data["valid"]:
                fieldnames.extend(data["valid"][0].keys())
            elif data["invalid"]:
                fieldnames.extend(data["invalid"][0].keys())
            header = [""]+fieldnames
            if len(fieldnames) > 1:
                writer = csv.DictWriter(csv_file, fieldnames=header)
                writer.writeheader()
                for item in data["valid"]:
                    writer.writerow({**{"": "valid"}, **item})
                for item in data["invalid"]:
                    writer.writerow({**{"": "invalid"}, **item})

def get_directory(directory):
    if directory:
        os.makedirs(directory, exist_ok=True)
        return directory+"/"
    else:
        return "/sites/"


def format_directory(j_directory, site_name, username, location):
    directory = j_directory

    user_directory = directory+"/"+site_name + "/"+username+"/"
    metadata_directory = user_directory+"/metadata/"
    directory = user_directory + location+"/"
    if "/sites/" == j_directory:
        user_directory = os.path.dirname(os.path.dirname(
            os.path.realpath(__file__))) + user_directory
        metadata_directory = os.path.dirname(os.path.dirname(
            os.path.realpath(__file__))) + metadata_directory
        directory = os.path.dirname(os.path.dirname(
            os.path.realpath(__file__))) + directory
    return [user_directory, metadata_directory, directory]
