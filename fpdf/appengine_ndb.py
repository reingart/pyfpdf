#-*- coding: utf-8 -*-
###############################################################################
# Google Appengine NDB Class                                                  #
# Author: Lee Ji-ho <search5@gmail.com>                                       #
# File: appengine_ndb.py                                                      #
# Description: Model declaration for the font metadata stored on GAE          #
###############################################################################
__author__ = 'jiho <search5@gmail.com>'

from google.appengine.ext import ndb

class FontDB(ndb.Model):
    name = ndb.StringProperty()
    type = ndb.StringProperty()
    desc = ndb.JsonProperty()
    up = ndb.FloatProperty()
    ut = ndb.FloatProperty()
    ttffile = ndb.StringProperty()
    fontkey = ndb.StringProperty()
    originalsize = ndb.IntegerProperty()
    cw = ndb.PickleProperty()

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

class FontCWDB(ndb.Model):
    cw_name = ndb.StringProperty()
    rangeid = ndb.IntegerProperty()
    prevcid = ndb.IntegerProperty()
    prevwidth = ndb.IntegerProperty()
    interval = ndb.BooleanProperty()
    range_interval = ndb.JsonProperty()
    range = ndb.JsonProperty()

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)
