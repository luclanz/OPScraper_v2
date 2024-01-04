import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import statistics
from PIL import Image, ImageOps

# data variables

link = "https://tcbscans.com/chapters/7451/one-piece-chapter-1089?date=4-1-2024-17"
chapter = "test"

def download_images(url, download_folder='images'):
    # Creare una cartella per salvare le immagini
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Effettuare la richiesta GET all'URL fornito
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Errore nella richiesta GET. Codice di stato: {response.status_code}")
        return

    # Utilizzare BeautifulSoup per analizzare l'HTML della pagina
    soup = BeautifulSoup(response.text, 'html.parser')

    # Trovare tutti i tag delle immagini
    img_tags = soup.find_all('img')

    i = 0

    # Scaricare ciascuna immagine
    for img_tag in img_tags:
        img_url = img_tag.get('src')

        # Creare l'URL completo utilizzando urljoin per gestire URL relativi
        img_url = urljoin(url, img_url)

        # Ottenere il nome del file dall'URL
        img_filename = os.path.join(download_folder, f'{i:03d}.png')
        i += 1

        # Scaricare e salvare l'immagine
        img_data = requests.get(img_url).content
        with open(img_filename, 'wb') as img_file:
            img_file.write(img_data)

        print(f"Immagine scaricata: {img_filename}")

# Esempio di utilizzo
download_images(link)

def process_images(folder='images'):
    data = []
    for filename in os.listdir(folder):
        if filename.endswith('.png'):
            img_path = os.path.join(folder, filename)
            im = Image.open(img_path, 'r').convert('P')
            data.append(tuple((im.size, len(Image.Image.getcolors(im)), filename)))
            im.close()

    return data

image_data = process_images()
print("Dati delle immagini:")
print(image_data)

# This func looks the data x and y and find the most likely dimension for the single page 
y_ = [image_data[j][0][1] for j in range(len(image_data))]
y_ = statistics.mode(y_)
print(f"una pagina avrà circa {y_} pixel di altezza")

x_ = [image_data[j][0][0] for j in range(len(image_data))]
x_ = statistics.mode(x_)
print(f"una pagina avrà circa {x_} pixel di larghezza (singola)")

filtered_data = list(filter(lambda y: y[0][1] > (y_ * 0.9) and y[0][1] < (y_ * 1.1), image_data))
filtered_data = sorted(filtered_data, key = lambda x: x[1], reverse=False)
print(f"dopo un filtro sulla dimensione di altezza sono rimaste: {len(filtered_data)} possibili immagini (comprese a colori)")

def is_color_image(image_path, color_threshold=20000):
    img = Image.open(image_path)

    # Converti l'immagine in una lista di colori distinti
    unique_colors = list(set(img.getdata()))
    #print(len(unique_colors))

    # Determina se l'immagine è a colori basandoti sul numero di colori distinti
    return len(unique_colors) > color_threshold

def look_for_pages(dataList, targetPages, singlePageWidth):
    nPages = 0
    for i in range(len(dataList)):
        img_path = os.path.join('images', dataList[i][2])
        if is_color_image(img_path):
            continue

        if dataList[i][0][0] < (singlePageWidth * 1.1) and dataList[i][0][0] > (singlePageWidth * 0.9):
            nPages += 1
            #print(f"{dataList[i][2]} counts as 1, {nPages}")

        if dataList[i][0][0] < (singlePageWidth * 2.2) and dataList[i][0][0] > (singlePageWidth * 1.8):
            nPages += 2
            #print(f"{dataList[i][2]} counts as 2, {nPages}")

        if nPages == targetPages:
            print(f"Trovate {targetPages} pagine")
            for j in range(0,i):
                img_path = os.path.join('images', dataList[j][2])
                if is_color_image(img_path):
                    return list()
            return dataList[:i+1]

    print(f"Ricerca di {targetPages} pagine fallita.")
    return list()

# ciclo per vedere quante pagine sono state trovate
for i in (17, 15, 13):
    a = look_for_pages(filtered_data, i, x_)
    if len(a) > 0:
        break

if len(a) == 0:
    raise Exception("Non son state trovare le pagine per un capitolo")

# eliminazione di tutte le immagini extra

b = list(os.listdir(path='images'))

for i in range(len(b)):

    pageFound = 0

    for j in range(len(a)):
        if b[i] == a[j][2]:
            pageFound = 1
            break
    
    if b[i] != a[j][2]:
        print(f"{b[i]} è spam")
        img = os.path.join('images', b[i])
        os.remove(img)

a = process_images()    # need to run this function again because the order was lost

# find first page
pageNumber = 1

if a[0][0][0] > (x_ * 1.1) and a[0][0][0] < (x_ * 0.9):
    raise Exception("Prima pagine non combacia. Errore nel motore di ricerca")

def addImage(list, name):
    item = os.path.join('images', name)
    imgg_ = Image.open(item)
    img_ = ImageOps.expand(imgg_, border=10, fill='white')
    imgg_ = img_.convert('RGB')
    list.append(imgg_)
    return list

def addDoubleImage(list, name1, name2):
    item1 = os.path.join('images', name1)
    item2 = os.path.join('images', name2)
    imgg1_ = Image.open(item1)
    imgg2_ = Image.open(item2)
    mergedImg = Image.new('RGB', (imgg1_.width + imgg2_.width, min(imgg1_.height, imgg2_.height)))
    mergedImg.paste(imgg1_, (0, 0))
    mergedImg.paste(imgg2_, (imgg1_.width, 0))
    list.append(mergedImg)
    return list

# pdf
imageListPdf = []

# loop for the other images (skip the first one since it will automatically added in the last step)
doubleTag = 0

for i in range(1, len(a)):
    if a[i][0][0] < (x_ * 2.2) and a[i][0][0] > (x_ * 1.8):
        print(f"added {a[i][2]} as single")
        imageListPdf = addImage(imageListPdf, a[i][2])
        doubleTag = 0
    else:
        if doubleTag == 0:
            imageListPdf = addDoubleImage(imageListPdf, a[i+1][2], a[i][2])
            print(f"added {a[i+1][2]} and {a[i][2]} as double")
            doubleTag = 1
        else:
            doubleTag = 0

item = os.path.join('images', a[0][2])
img = Image.open(item)
img.save(f'{chapter}.pdf', save_all=True, append_images=imageListPdf)

for item in os.listdir('images'):
    item = os.path.join('images', item)
    os.remove(item)