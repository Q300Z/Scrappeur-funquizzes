import datetime
import json
import os
import shutil
import time
from os import popen, truncate
from time import gmtime, strftime
from traceback import print_tb

import requests
from bs4 import BeautifulSoup

start = time.time()

fichier = 'data_beta_2.json'

ifnotfolder = ["1", "001", "0001", "0", "00"]

def save(manga):
    with open(fichier, 'w', encoding='utf-8') as file:
        data = json.dump(manga, file, ensure_ascii=False, indent=4)

    return  # print("Sauvegarde !")

def read():
    with open(fichier, encoding='utf-8') as data_file:
        data = json.load(data_file)

    return data

def autosave(data):
    save(data)
    time.sleep(1)
    data = read()
    return data

def aff(nb, i, string):
    pourcentage = i / nb * 100
    return print(string + " {:.2f}".format(pourcentage) + "% Manga : " + data[str(i)]["manga"])

def recup(url):
    response = requests.get(url)
    if response.ok:
        soup = BeautifulSoup(response.text, 'html5lib')
        list = soup.findAll("a", href=True)
        del list[0:5]
        links = []
        for a in list:
            b = a["href"]
            if b is not None:
                f = url + b
                links.append(f)
        # time.sleep(1)
        return links

def init(url):
    response = requests.get(url)
    i = -1
    if response.ok:
        soup = BeautifulSoup(response.text, 'html5lib')
        list = soup.findAll("a", href=True)
        del list[0:5]
        nb = len(list)
        data = ({"nombre": nb, })
        for a in list:
            b = a["href"]
            if b is not None:
                f = url + b
                i = i + 1
                data.update({
                    i: {
                        "manga": a.text,
                        "link_nomManga": f,
                        "last_update": None,
                        "last_check": None,
                        "tcheck": False,
                        "folder": False,
                        "link_folder": None,
                        "nb_chap": 0,
                        "link_chapter": {},
                    },
                })
    return data


def p2(x):
    last_update(url)
    url_nomManga = data[str(x)]["link_nomManga"]
    folder_tcheck = False
    links_nomManga = recup(url_nomManga)

    if str(len(links_nomManga)) == "1":

        for link in links_nomManga:
            url_split = link.split("/")
            url_part = url_split[-2]

            for notfolder in ifnotfolder:
                if str(url_part) == str(notfolder):
                    data[str(x)]["link_chapter"] = links_nomManga
                    data[str(x)]["nb_chap"] = str(
                        len(data[str(x)]["link_chapter"]))
                    folder_tcheck = True
                    data[str(x)]["tcheck"] = True

                elif folder_tcheck == False:
                    data[str(x)]["folder"] = True
                    data[str(x)]["link_folder"] = links_nomManga
                    data[str(x)]["tcheck"] = True
                    for g in data[str(x)]["link_folder"]:
                        url_g = recup(g)
                        data[str(x)]["link_chapter"] = url_g
                        data[str(x)]["nb_chap"] = str(
                            len(data[str(x)]["link_chapter"]))

    else:
        data[str(x)]["link_chapter"] = links_nomManga
        data[str(x)]["nb_chap"] = str(len(data[str(x)]["link_chapter"]))
        data[str(x)]["tcheck"] = True
    return data

def p3(x):
    data = update_now(x)
    if data[str(x)]["tcheck"] == True:
        for url_chapters in data[str(x)]["link_chapter"]:
            links_chapters = recup(url_chapters)
            url_split = url_chapters.split("/")
            url_part = url_split[-2]
            if str(len(links_chapters)) > "0":
                data[str(x)]["link_chapter_" + str(url_part)] = links_chapters
    return data

def update_now(x):
    now = datetime.datetime.now()
    data[str(x)]["last_check"] = now.strftime("%Y-%m-%d %H:%M")
    return data

def recup_update(url):
    response = requests.get(url)
    if response.ok:
        soup = BeautifulSoup(response.text, 'html5lib')
        list = soup.findAll("td")
        del list[0:5]
        links = []
        for a in list:
            b = a.text.strip()
            links.append(b)
        time.sleep(1)
        links = [x for x in links if x != ""]
        links = fusion_update(links)
        return links

def fusion_update(data_update):
    i = 0
    c = ""
    list = []
    for x in data_update:
        if i <= 3:
            i = i + 1
            c = x + "|" + c
            if i == 3:
                list.append(c)
                i = 0
                c = ""
    return list

def last_update(url):
    list_data_update = recup_update(url)
    for date in list_data_update:
        r = date.split("|")
        name = r[2]
        update = r[1]
        for x in range(nb):
            n = 0 
            if str(data[str(x)]["manga"]) == str(name):
                data[str(x)]["last_update"] = update
            elif n == data["nombre"]:
                print("Nombre d'erreur pour le manga : " + data[str(x)]["manga"] + " : " + str(n))
            else:
                n = n + 1  
    return update

def update_chap(x):
    if str(data[str(x)]["last_update"]) > str(data[str(x)]["last_check"]):
        #aff(nb, x, "Nouvelle mise à jour : ")
        if data[str(x)]["folder"] == True:
            p2_update_recup(x, data[str(x)]["link_folder"])
        else:
            p2_update_recup(x, data[str(x)]["link_nomManga"])
    else:
        aff(nb, x, "Aucune mise à jour : ")

def p2_update_recup(x, list):
    if not type(str()) == type(list):
        print("type(str()) == type(list)")
        for notfolder in ifnotfolder:
            url_split = list.split("/")
            url_part = url_split[-2]
            if str(url_part) == str(notfolder):
                for g in list:
                    url_g = recup(g)
                    for h in url_g:
                        for link_chap in data[str(x)]["link_chapter"]:
                            if h == link_chap:
                                url_g.remove(h)
                        data[str(x)]["link_chapter"] = url_g
                        data[str(x)]["nb_chap"] = str(
                            len(data[str(x)]["link_chapter"]))
                        dat = p3_update_recup(x, url_g)
                dat = update_now(x)
                return dat
            else:
                url_g = recup(list)
                for h in url_g:
                    for link_chap in data[str(x)]["link_chapter"]:
                        if h == link_chap:
                            url_g.remove(h)
                    data[str(x)]["link_chapter"] = url_g
                    data[str(x)]["nb_chap"] = str(
                        len(data[str(x)]["link_chapter"]))
                    dat = p3_update_recup(x, url_g)
                dat = update_now(x)
                return dat

def p3_update_recup(x, list):
    for url_chapters in list:
        links_chapters = recup(url_chapters)
        url_split = url_chapters.split("/")
        url_part = url_split[-2]
        if str(len(links_chapters)) > "0":
            data[str(x)]["link_chapter_" + str(url_part)] = links_chapters
    return data

url = 'http://funquizzes.fun/uploads/manga/'
data = {}

if not os.path.exists(fichier):
    print("Partie 1")
    print("Initialisation ...")

    data = init(url)
    data = autosave(data)

    nb = data["nombre"]
    print("Partie 2 et 3")

    for x in range(nb):
        aff(nb, x, "Grab en cours : ")
        data = p2(x)
        data = autosave(data)
        data = p3(x)
        data = autosave(data)
        save(data)

else:
    data = read()
    print("Update check : ")
    nb = data["nombre"]
    for x in range(nb):
        data = last_update(url)
        data = update_chap(x)
    save(data)


end = time.time()
elapsed = end - start
print("Temps d'excution : " + strftime("%H:%M:%S", gmtime(elapsed)))
