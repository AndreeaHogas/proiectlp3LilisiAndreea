import json
import re
import time
from bs4 import BeautifulSoup
import requests

# https://youtube.com/playlist?list=PLzMcBGfZo4-n40rB1XaJ0ak1bemvlqumQ
# https://realpython.com/beautiful-soup-web-scraper-python/
# https://pypi.org/project/beautifulsoup4/
# https://docs.python.org/3/library/json.html
# https://www.routech.ro/tutorial-web-scraping-python-cum-sa-scrapati-datele-de-pe-un-site-web/
#  https://docs.python-requests.org/en/latest/
#  https://www.crummy.com/software/BeautifulSoup/bs4/doc/
#  https://docs.python.org/3/library/time.html
#  https://docs.python.org/3/library/re.html


# se setează URL-ul de bază pentru site-ul Elefant.ro cu filtrul de căutare pentru produsele "star wars"
base_url = "https://www.elefant.ro/filter/1?PageNumber={}&PageSize=60&SortingAttribute=bestseller-desc&ViewType=&SearchTerm=star+wars&SearchParameter=%26%40QueryTerm%3Dstar%2Bwars%26AvailableFlag%3D1%26isMaster%3D0"

# se inițializează numărul paginii curente
current_page = 1

# se definește o listă goală în care vor fi stocate cărțile
cartii = []

# incepând de la prima pagină și continuând până la a 13-a pagină
while current_page <= 13:
     # Se realizează o cerere HTTP către URL-ul formatat cu pagina curentă
    page = requests.get(base_url.format(current_page))
     # se utilizează biblioteca BeautifulSoup pentru a extrage conținutul paginii
    soup = BeautifulSoup(page.content, "html.parser")
    # se găsește elementul script care conține datele despre produse
    script_element = soup.find_all("script", {"type": "text/javascript"})[22]
    script_data = script_element.string
    # se folosește o expresie regulată pentru a găsi toate obiectele JSON din script_data
    regex = r"\{([^}]*)\}"
    matches = re.findall(regex, script_data)
      # funcție pentru formatarea informațiilor
    def format_info(info):
        return info.split(":")[-1].replace(",", "")
    
     # funcție pentru extragerea datelor despre o carte
    def extract_data(product):
        result = {}
        for info in product.split("\n"):
            if info.startswith("'name'"):
                result["title"] = format_info(info)
            elif info.startswith("'price'"):
                result["price"] = format_info(info)
            elif info.startswith("'brand'"):
                result["brand"] = format_info(info)
            elif info.startswith("'<div>author</div>==$0'"):
                result["<div>author</div>==$0"] = format_info(info)
            elif "'category'" in info and "'Carti\\/Carte straina\\/Fiction & related items\\/Science fiction'" in info:
                result["category"] = format_info(info)
            elif "'category'" in info and "'Carti\\/Carte straina\\/Fiction & related items'" in info:
                result["category"] = "Carti/Carte straina/Fiction & related items"
            elif "'category'" in info and "'Carti\\/Carte straina\\/Children\\'s, Teenage & Educational'" in info:
                result["category"] = "Carti/Carte straina/Children's, Teenage & Educational"
            elif "'product-sold-out'" in info:
                return Non

        return result
     # se extrag informațiile potrivite despre carti
    for match in matches:
        book = extract_data(match)
        if book is not None and "category" in book:
            if book not in cartii:
                cartii.append(book)
# se afișează mesajul pentru verificarea paginii curente
    print(f"Verifying page: {current_page}")
 # se incrementează numărul paginii curente
    current_page += 1
 # se adaugă o pauză de 1 secundă între cereri pentru a nu suprasolicita serverul
    time.sleep(1) 
# se găsește linkul către pagina următoare
    next_page_link = soup.find("a", title="La pagina următoare")
  # dacă nu există link către pagina următoare, se încheie bucla
    if next_page_link is None:
        break
  # se extrage URL-ul paginii următoare
    next_page_url = next_page_link["href"]
    # Extragem numărul paginii următoare din URL
    current_page = int(re.search(r"PageNumber=(\d+)", next_page_url).group(1))
  # se salvează informațiile despre cărți într-un fișier JSON
with open("star_wars_cartii.json", "w+", encoding="utf8") as json_file:
    json.dump({"cartii": cartii}, json_file, indent=4)

# se afișează un mesaj de finalizare a execuției codului
print("Codul a fost executat cu succes și fișierul JSON a fost generat.")
