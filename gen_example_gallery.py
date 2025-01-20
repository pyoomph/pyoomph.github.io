from bs4 import BeautifulSoup
import requests
import pathlib
from PIL import Image
import os
pathlib.Path("_generated/media/tutorial").mkdir(parents=True, exist_ok=True)


skip_image_download=False

html_doc="https://pyoomph.readthedocs.io/en/latest/"


html_code=requests.get(html_doc).text
soup = BeautifulSoup(html_code, 'html.parser')

tables=soup.find_all("table")
if len(tables)!=1:
    raise RuntimeError("Expected one table")
table=tables[0]
for cap in table.find_all("caption"):
    cap.decompose()

def download_img_and_patch(img,skip_download=False):
    img_url=img["src"]
    img_name=img_url.split("/")[-1]
    img_path=os.path.join("_generated","media","tutorial",img_name)
    
    img_size=(200,150)
    
    if not skip_download:
        with open(img_path, 'wb') as f:
            f.write(requests.get(img_url).content)
        image = Image.open(img_path)
        image.thumbnail(img_size)
        image.save(img_path, "png")
    img_path=img_path.lstrip("_generated/")
    img["src"]=img_path

imgs=[]
titles=[]    
for a in table.find_all("a"):
    a["href"]=html_doc+a["href"]
    if len(a.find_all("img"))==0:        
        titles.append(a)
  
for img in table.find_all("img"):
    img["src"]=html_doc+img["src"]
    download_img_and_patch(img,skip_download=skip_image_download)
    imgs.append(img)
print("<center><h1>Tutorial</h1></center>")
print('The <a href="'+html_doc+'">full tutorial can be found here</a>, but below please find some examples to start with:<br>')

print('<ul class="horizontal-media-scroller">')
for img,title in zip(imgs,titles):
    print('<li>')
    print('<a href='+title["href"]+'>')
    print("<figure>")
    print("<picture>")
    print('<img  loading="lazy" src="'+img["src"]+'">') #alt="..."          
    print("</picture>")
    print("<figcaption>")
    print(title.get_text())
    print("</figcaption>")
    print("</figure>")
    print("</a>")
    print("</li>")
print('</ul>')
print("<br>")