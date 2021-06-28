import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import re

page1 = "https://www.sejm.gov.pl/sejm9.nsf/wypowiedzi.xsp"
page2 = "https://www.sejm.gov.pl/sejm9.nsf/wypowiedzi.xsp?page=2"
main_address = "https://www.sejm.gov.pl/sejm9.nsf/"

interj_regex = re.compile(r"\([^\)]+\)")
whitespace_regex = re.compile(r"\s+")

seating_links = []
for page in [page1, page2]:
    response = requests.get(page)
    soup = BeautifulSoup(response.text)
    seatings = soup.findAll("a", {"class": "icon-text"}) 
    seating_links.extend([s.get("href") for s in seatings])


speech_links = []
for sl in seating_links:
    response = requests.get(main_address + sl) 
    soup = BeautifulSoup(response.text)
    speeches = [link for link in soup.findAll("a") if link.text.startswith("Poseł")]
    speech_links.extend([s.get("href") for s in speeches if s.get("href").startswith("wypowiedz")])

speeches = []
for i, sp in enumerate(speech_links):
    print(i)
    response = requests.get(main_address + sp)
    soup = BeautifulSoup(response.text)
    author_el = soup.find("h2", {"class": "mowca"})
    author = author_el.text
    speech_text = author + "\n" 
    element = author_el
    while element:
        if type(element) != Tag:
            element = element.next_element
        else:
            if not element.get("class") or "przebieg" not in element.get("class"):
                speech_text += element.text
                element = element.next_element
            else:
                element = None
    speeches.append(speech_text)  

cleaned_speeches = []
for speech in speeches:
    author, speech_text = speech.split("\n", 1)
    interj_cleaned = interj_regex.sub("", speech_text)
    whitespace_cleaned = whitespace_regex.sub(" ", interj_cleaned)
    three_dots_cleaned = whitespace_cleaned.replace("... ...", " ")
    clean_speech = "\n".join([author, three_dots_cleaned])
    cleaned_speeches.append(clean_speech)

full_text = "\n\n".join(cleaned_speeches)
with open("speeches.txt", "w") as f:
    f.write(full_text)





