from PIL import Image, ImageOps
import os
import requests
from bs4 import BeautifulSoup

link = "https://onepiecechapters.com/chapters/212/one-piece-chapter-1030"
chapter = 1030
colortol = (30, 35, 40, 45, 50)
widthtol = (2, 4, 6, 8, 10, 12, 14)
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


#filter the stuff
for i in range(len(colortol)):

    #filter the images with too many colours
    data_filtered = filter(lambda ncolor: ncolor[1] < colortol[i] , data)
    new_data = list(data_filtered)
    #print(f'try colortol: {colortol[i]}')

    if len(new_data) >= 9:
        
        #get data from images
        x_width = [new_data[j][0][0] for j in range(len(new_data))]
        names = [new_data[j][2] for j in range(len(new_data))]
        xavg = sum(x_width) / 17

        #loop for counting the pages
        for z in range(len(widthtol)):
            #print(f'    try widthtol: {widthtol[z]}')
            npages = 0

            pages = []

            for j in range(len(x_width)):
                if (x_width[j] < (xavg + widthtol[z])) and (x_width[j] > (xavg - widthtol[z])):
                    npages +=1
                    pages.append(tuple((1, new_data[j][2])))
                    #print('single', new_data[j][2])
                    if npages == 17:
                        break
                elif (x_width[j] < (xavg + 3*widthtol[z])*2) and (x_width[j] > (xavg - 3*widthtol[z])*2):
                    npages += 2
                    pages.append(tuple((2, new_data[j][2])))
                    #print('double', new_data[j][2])
                    if npages == 17:
                        break
                else:
                    #print(f'        ERROR width page not within parameters, !({(xavg - 3*widthtol[z])*2:.0f} < {x_width[j]} < {(xavg + 3*widthtol[z])*2:.0f}): index {j}')
                    break

            if npages == 17:
                break
        
        if npages == 17:
            print(f'FOUND DATA! COLORTOL:{colortol[i]}, WIDTHTOL:{widthtol[z]}')
            break

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