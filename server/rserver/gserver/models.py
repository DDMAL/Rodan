from django.db import models
from uuidfield import UUIDField

import urllib2
import os
from gamera.core import *
from gamera import plugin
init_gamera()

class Image(models.Model):
    url = models.URLField()
    id = UUIDField(auto = True, primary_key = True)
    localpath = models.CharField(max_length = 255)
    pixel_type = models.IntegerField(max_length = 1, null = True)
    


    def __unicode__(self):
        return u"\nURL:{0} \nID:{1} \nPIXEL TYPE:{2} \nLOCAL PATH:{3}".format(
            self.url, self.id, self.pixel_type, self.localpath)



    def save(self, *args, **kwargs):
        super(Image, self).save(*args, **kwargs)
        u = urllib2.urlopen(self.url)
        os.makedirs(os.path.join("images", self.id))
        image_folder = os.path.join("images", self.id)
        print "Image Folder:{0}".format(image_folder)
        localpath = os.path.join(image_folder, self.id)
        self.localpath = localpath
        print "LocalPath:{0}".format(self.localpath)
        f = open(localpath, 'w')
        f.write(u.read())
        f.close()
        image = load_image(self.localpath)
        pixel_type = image.data.pixel_type
        self.pixel_type = pixel_type
        print "\nIMAGE: {0}".format(self)
        # image_plugings = plugin.plugin_methods[self.pixel_type]
        print "IMAGE PLUGINS: {0}".format(plugin.plugin_methods[self.pixel_type])





    

class ImageTransformation(models.Model):
    it = models.CharField(max_length = 255)
    id = UUIDField(auto = True, primary_key = True)

    def __unicode__(self):
        return u"\nTransformation:{0} \nID:{1}".format(self.it, self.id)


# class GameraPlugin():
#   plugin_name = models.Charfield(max_length = 255)
#   plugin_settings = models.Charfield(max_length = 255)




# i = Image(url = "http://www.vigliensoni.com/resources/vigliensoni_com.png")