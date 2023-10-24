from logging import raiseExceptions
from PIL import Image, ImageOps
import os
import requests
from bs4 import BeautifulSoup
import statistics

link = "https://tcbscans.com/chapters/7521/one-piece-chapter-1095?date=24-10-2023-19"
chapter = "1095 - A World Where You're Better-Off Dead"
tot_pages = 17

widthtol = (6, 10, 14, 18, 25, 50, 100)
npages = 0

#get the soup from the url
def getdata(url):
	r = requests.get(url)
	return r.text

htmldata = getdata(link)	
soup = BeautifulSoup(htmldata, 'html.parser')

#save all the relevant images
i = 1
for item in soup.find_all('img'):
    try:
        image = requests.get(soup.find_all('img')[i]['src'])
    except IndexError:
        break
    file = open('{0}.png'.format(i), "wb")
    file.write(image.content)
    file.close()
    i += 1

#get the data
data = []
for i in os.listdir():
   if i.endswith('.png'):
      im = Image.open(i, 'r').convert('P')
      data.append(tuple((im.size, len(Image.Image.getcolors(im)), i)))
      im.close()

#start engine ------------------------

#filter 1 - based on y dimensions
y_ = [data[j][0][1] for j in range(len(data))]
y_ = statistics.mode(y_)
print(y_)

data_filtered = filter(lambda y: y[0][1] > (y_ * 0.85) and y[0][1] < (y_ * 1.3), data)
data = list(data_filtered)

#filter 2 - based on number of colours
data = sorted(data, key = lambda x: x[1], reverse=False)

for i in range(18)[8:]:

    data_filtered = data[0:i]
    #print(f'try firts: {i} pages')

    x_width = [data_filtered[j][0][0] for j in range(len(data_filtered))]
    names = [data_filtered[j][2] for j in range(len(data_filtered))]
    xavg = sum(x_width) / (tot_pages)

    #loop for counting the pages
    for z in range(len(widthtol)):
        #print(f'    try widthtol: {widthtol[z]}')
        npages = 0

        pages = []

        for j in range(len(x_width)):
            if (x_width[j] < (xavg + widthtol[z])) and (x_width[j] > (xavg - widthtol[z])):
                npages +=1
                pages.append(tuple((1, data_filtered[j][2])))
                #print('single', new_data[j][2])
                if npages == tot_pages:
                    break
            elif (x_width[j] < (xavg + 3*widthtol[z])*2) and (x_width[j] > (xavg - 3*widthtol[z])*2):
                npages += 2
                pages.append(tuple((2, data_filtered[j][2])))
                #print('double', new_data[j][2])
                if npages == tot_pages:
                    break
            else:
                #print(f'        ERROR width page not within parameters, !({(xavg - 3*widthtol[z])*2:.0f} < {x_width[j]} < {(xavg + 3*widthtol[z])*2:.0f}): index {j}')
                break

        if npages == tot_pages:
            print(f'Found all {tot_pages} pages!')
            break

    if npages == tot_pages:
        break

if npages != tot_pages:
    raise Exception('Engine Failed')

#End Engine -------------------------------

#sort images (remove the '.png' at the end and sort as integers)
pages_sorted = sorted(pages, key = lambda tup: int(tup[1][:-4]))

#remove junk
for i in os.listdir():
    if i.endswith('.png') and i not in names:
        os.remove(i)

#merge func
def get_concat_h(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, min(im1.height, im2.height)))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst

#rename images
i = 0
for item in pages_sorted:
    os.rename(item[1], f'{i}.png')
    if item[0] == 2:
        i += 2
    else:
        i += 1

#merge
for i in map(lambda x: 2*x + 1, range(8)):
    if f'{i+1}.png' not in os.listdir():
        continue
    else:
        imDX = Image.open(f'{i}.png')
        imSX = Image.open(f'{i+1}.png')
        get_concat_h(imSX, imDX).save(f'{i}.png')
        os.remove(f'{i+1}.png')

#pdf
image_list = []

for item in sorted(list(filter(lambda x: x.endswith('.png'), os.listdir())), key = lambda str: int(str[:-4])):
    if item == '0.png':
        imgg_ = Image.open(item)
        img_ = ImageOps.expand(imgg_, border=25, fill='white')
        imgg_ = img_.convert('RGB')
        #imgg_.save(item)
        continue
    img = Image.open(item)
    img_ = ImageOps.expand(img, border=25, fill='white')
    img_ = img_.convert('RGB')
    image_list.append(img_)
    #img_.save(item)

imgg_.save(f'{chapter}.pdf', save_all=True, append_images=image_list)

#remove junk
for item in os.listdir():
    if item.endswith('png'):
        os.remove(item)
