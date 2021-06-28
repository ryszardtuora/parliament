from bs4 import BeautifulSoup
import re
import os

author_regex = re.compile(r"(Marszałek)|(Sprawozdawca)|(Wicemarszałek)|(Poseł)|(Podsekretarz)")
interj_regex = re.compile(r"\([^\)]+\)")

header_regex = re.compile(r"(\d+\. posiedzenie Sejmu w dniu)|(Projekt (ustawy? o|uchwał?))|(Pytania w sprawach bieżących)|(Pytania w sprawach bieżących)|(Punkty? \d+\.)|(Oświadczenia poselskie)|(Powołanie Rzecznika)|(Sprawy formalne)|(Wnioski o)|(Wniosek o)")

data_folder = "data"
index_table =  [
                ("30_a_ksiazka.html", 6, -1),
                ("30_b_ksiazka.html", 8, 121),
                ("30_c_ksiazka.html", 6, -3),
                ("30_d_ksiazka.html", 4, 29),
                ("31_ksiazka.html", 4, 75),
                ("32_ksiazka.html", 4, 48),
                ("33_a_ksiazka.html", 6, 156),
                ("33_b_ksiazka.html", 7, 195),
               ]

def get_content_pages(filename, start_page, end_page):
    path = os.path.join(data_folder, filename)
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    soup = BeautifulSoup(txt, parser="html.parser")
    pages = soup.findAll("div", class_="page")
    content_pages = pages[start_page:end_page]
    return content_pages

def is_header(paragraph):
    if header_regex.match(paragraph):
        return True
    else:
        return False

def filter_pars(pages):
    paragraphs = []
    trash = []
    for page in pages:
        pars = page.findAll("p")
        clean_pars = [par for par in pars[2:] if par.text and not is_header(par.text)]# odcinanie nagłówków
        dirty_pars = [par for par in pars if par not in clean_pars]
        paragraphs.extend(clean_pars)
        trash.extend(dirty_pars)# odrzucane paragrafy (do wglądu)
    return paragraphs

def clean_speech(speech):
  speech = speech.replace("\n", " ")
  speech = speech.replace("…", "")
  speech = speech.replace("- ", "")
  cleaned = interj_regex.sub("", speech)
  return cleaned

def join_subsequent_speeches(speeches):
  joined_speeches = []
  prev_author = None
  for author, speech in speeches:
    if author == prev_author:
      index = len(joined_speeches) -1 
      _, prev_speech = joined_speeches[index]
      prev_speech += speech
      joined_speeches[index] = (prev_author, prev_speech)
    else:
      joined_speeches.append((author, speech))
    prev_author = author
  return joined_speeches

def get_speeches(paragraphs):
    speeches = []
    speech = ""
    deputy = False
    for par in paragraphs:
      author_match =  author_regex.match(par.text)
      print(par)
      if author_match:
        if speech:
          cleaned = clean_speech(speech)
          speeches.append((author, cleaned))
        speech = ""
        start_index = author_match.end()
        author = par.text[start_index:].split("\n")[0].strip().strip(":") # sprawozdawca
        print(author)
        author = author.replace("Sprawozdawca ", "")
        if author_match.group() == "Poseł":
          deputy = True
        else:
          deputy = False
      else:
        if deputy:
          speech += par.text
    joined = join_subsequent_speeches(speeches)
    return joined

speeches = []
for entry in index_table:
    filename, start_page, end_page = entry
    content_pages = get_content_pages(filename, start_page, end_page)
    paragraphs = filter_pars(content_pages)
    file_speeches = get_speeches(paragraphs)
    speeches.extend(file_speeches)

with open("speeches.txt", "w") as f:
  txt = "\n\n".join([f"{a}\n{t}" for a, t in speeches])
  f.write(txt)
