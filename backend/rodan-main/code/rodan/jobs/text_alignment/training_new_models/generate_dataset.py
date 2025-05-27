import imgaug as ia
import os
import numpy as np
from imgaug import augmenters as iaa
from imgaug import parameters as iap
from skimage.color import rgb2gray
from skimage.filters import threshold_otsu
from skimage.util import img_as_ubyte
import cv2
from math import floor
from random import shuffle

AUGS_PER_IMAGE = 5

contrast = iaa.GammaContrast((0.8,1.3))
brightness = iaa.Multiply((0.8,1.3))
blur = iaa.GaussianBlur(sigma=(0,1.5))
noise = iaa.AdditiveGaussianNoise(scale=(0,0.2*255))
hueAndSat = iaa.AddToHueAndSaturation((-200,100))
pad = iaa.Pad(px= ((0,30),(0,10),(0,30),(0,2000)), pad_cval=255)

aug_some = iaa.SomeOf((0,None),[pad,contrast,brightness,blur,noise,hueAndSat])

scale = iaa.Affine(scale=(0.8, 1.3))
cutout = iaa.Cutout(nb_iterations=(110, 140), size=(0.1,0.15), squared=True,fill_mode="constant", cval=255)
dropout = iaa.ReplaceElementwise(0.2, 255)
aug_all = iaa.Sequential([scale,dropout,cutout])

pwd = os.getcwd() +"/"

#fixes old nump verion issue
np.bool = np.bool_

dirs = ["salzinnes","stgallen"]

images = []
labels = []

def augment_images(img, num):
    name = str(num)
    
    for j in range(AUGS_PER_IMAGE):
        file_name = name + "-" + str(j+1)
        # these are the optional augmentations that might not do anything
        img_aug = aug_some.augment_image(img)
        # these augmentations are essential
        img_aug = (aug_all.augment_image(img_aug))
        #write img_aig to file
        cv2.imwrite(file_name+".png",img_aug)
        text_file = open(file_name+".gt.txt", "w")
        text_file.write(labels[i-1])

# traverse files and aggregate images and text files
for dir in dirs:
    currdir = pwd+dir
    os.chdir(currdir)
    subdirs = os.listdir()
    for subdir in subdirs:
        datum_dir = currdir + "/" + subdir
        if os.path.isdir(datum_dir):
            os.chdir(datum_dir)
            files = os.listdir()
            for file in files:
                if file.endswith("png"):
                    try:
                        text_file = open(file[:-7]+"gt.txt", "r")
                        labels.append(text_file.read())
                        img = cv2.imread(file)
                        images.append(img)
                    except Exception as e:
                        print(e)
                    

# suffle data
temp = list(zip(images,labels))
shuffle(temp)

images, labels = zip(*temp)
images, labels = list(images), list(labels)

index= floor(len(images)*0.8)

# output train_aug
outupt_dir = pwd + "train_aug"
if(not os.path.isdir(outupt_dir)):
    os.mkdir(outupt_dir)
os.chdir(outupt_dir)
i = 1
for img in images[:index]:
    augment_images(img,i)
    i+=1

# output val_aug
os.chdir(pwd)
outupt_dir = pwd + "val_aug"
if(not os.path.isdir(outupt_dir)):
    os.mkdir(outupt_dir)
os.chdir(outupt_dir)
for img in images[index:]:
    augment_images(img,i)
    i+=1

# output train_same
os.chdir(pwd)
outupt_dir = pwd + "train_same"
if(not os.path.isdir(outupt_dir)):
    os.mkdir(outupt_dir)
os.chdir(outupt_dir)
i = 1
for img in images[:index]:
    cv2.imwrite(str(i)+".png",img)
    text_file = open(str(i)+".gt.txt", "w")
    text_file.write(labels[i-1])
    i+=1

# output val_same
os.chdir(pwd)
outupt_dir = pwd + "val_same"
if(not os.path.isdir(outupt_dir)):
    os.mkdir(outupt_dir)
os.chdir(outupt_dir)
for img in images[index:]:
    cv2.imwrite(str(i)+".png",img)
    text_file = open(str(i)+".gt.txt", "w")
    text_file.write(labels[i-1])
    i+=1
