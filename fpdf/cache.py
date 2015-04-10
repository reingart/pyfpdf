#******************************************************************************
# Caching classes
# 
# This classes are provided to maintain caching mechanism for python FPDF port
# and allow to extend standard behaviour.
# 
# Version:  1.00
# Date:     2015-03-24
# Author:   Roman Kharin <romiq.kh@gmail.com>
# License:  LGPL
# Copyright (c) Roman Kharin, 2015
#******************************************************************************

import os, sys

from .py3k import pickle, hashpath

CACHE_VERSION = 3 # This constant will be updated with any format changes

def instance_cache(cache_mode, cache_dir = None): # match with FPDF_CACHE_MODE
    if cache_mode == 0: # 
        return StdCache()
    elif (cache_mode == 1) or (cache_mode == 2 and not cache_dir):
        return NoneCache()
    elif cache_mode == 2:
        return HashCache(cache_dir = cache_dir)
    else:
        raise Exception("Unknown FPDF_CACHE_MODE mode")

class NoneCache:
    """Do not store file cache (FPDF_CACHE_MODE == 1)"""

    def cache_for(self, fname, ext = ".pkl"):
        return None
        
    def load_cache(self, filename, ttf = None):
        return None
        
    def save_cache(self, filename, data, ttf = None):
        return
        
class StdCache(NoneCache):
    """Store cache files in pickle format in same folder with fonts 
    (FPDF_CACHE_MODE == 0)"""

    def load_cache(self, filename, ttf = None):
        "Load raw object, or None if no cache found or incompatible"
        if not filename:
            return None
        try:
            with open(filename, "rb") as fh:
                data = pickle.load(fh)
                assert data.get("CACHE_VERSION", 0) == CACHE_VERSION
                assert data.get("SYS_VERSION", 0) == tuple(sys.version_info)
                if ttf:
                    assert data.get("TTF_PATH", "") == ttf
                return data
        except (IOError, pickle.UnpicklingError, ValueError, AssertionError):
            return None

    def save_cache(self, filename, data, ttf = None):
        "Save raw object"
        if not filename:
            return None
        try:
            with open(filename, "wb") as fh:
                data["CACHE_VERSION"] = CACHE_VERSION
                data["SYS_VERSION"] = tuple(sys.version_info)
                if ttf:
                    data["TTF_PATH"] = ttf
                pickle.dump(data, fh)
        except Exception as e:  
            return None
        
    def cache_for(self, fname, ext = ".pkl"):
        return os.path.splitext(fname)[0] + ext
        
class HashCache(StdCache):
    "Store cache files in specified folder (FPDF_CACHE_MODE == 2)"
    def __init__(self, cache_dir = None):
        self.cache_dir = cache_dir
        assert self.cache_dir is not None, "Cache dir must be specified"
    
    def cache_for(self, fname, ext = ".pkl"):
        fname = os.path.abspath(fname)
        return os.path.join(self.cache_dir, \
                    hashpath(fname) + ext)

