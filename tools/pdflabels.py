#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ******************************************************************************
# * Software: Labels for pyfpdf                                                *
# * Date:     2010-09-10                                                       *
# * License:  LGPL v3.0                                                        *
# *                                                                            *
# * Original Author (PHP):  Copyright (C) 2003 Laurent PASSEBECQ (LPA)         *
# * Published at http://www.fpdf.org/en/script/script29.php                    *
# *                                                                            *
# * Ported to Python 2.6 by jredrejo (jredrejo@debian.org)   September-2011    *
# *****************************************************************************/
from fpdf import FPDF

#List of label formats:
commercial_labels={
'Avery-5160':{'paper-size':'letter', 'metric':'mm', 'marginLeft':1.762,'marginTop':10.7,'NX':3,'NY':10,'SpaceX':3.175,'SpaceY':0, 'width':66.675,'height':25.4,'font-size':8},
'Avery-5161':{'paper-size':'letter','metric':'mm','marginLeft':0.967,'marginTop':10.7,'NX':2,'NY':10,'SpaceX':3.967,'SpaceY':0,'width':101.6,'height':25.4,'font-size':8},
'Avery-5162':{'paper-size':'letter','metric':'mm','marginLeft':0.97,'marginTop':20.224,'NX':2,'NY':7,'SpaceX':4.762,'SpaceY':0,'width':100.807,'height':35.72,'font-size':8},
'Apli-01277':{'paper-size':'A4','metric':'mm','marginLeft':10.0,'marginTop':12.0,'NX':2,'NY':7,'SpaceX':0,'SpaceY':0,'width':105,'height':42.4,'font-size':10},
'Avery-5163':{'paper-size':'letter','metric':'mm','marginLeft':1.762,'marginTop':10.7, 'NX':2,'NY':5,'SpaceX':3.175,'SpaceY':0,'width':101.6,'height':50.8,'font-size':8},
'Avery-5164':{'paper-size':'letter','metric':'in','marginLeft':0.148,'marginTop':0.5, 'NX':2,'NY':3,'SpaceX':0.2031,'SpaceY':0,'width':4.0,'height':3.33,'font-size':12},
'Avery-8600':{'paper-size':'letter','metric':'mm','marginLeft':7.1, 'marginTop':19, 'NX':3, 'NY':10, 'SpaceX':9.5, 'SpaceY':3.1, 'width':66.6, 'height':25.4,'font-size':8},
'Avery-L7163':{'paper-size':'A4','metric':'mm','marginLeft':5,'marginTop':15, 'NX':2,'NY':7,'SpaceX':25,'SpaceY':0,'width':99.1,'height':38.1,'font-size':9},
'Avery-3422':{'paper-size':'A4','metric':'mm','marginLeft':0,'marginTop':8.5, 'NX':3,'NY':8,'SpaceX':0,'SpaceY':0,'width':70,'height':35,'font-size':9}
}


class PDFLabel(FPDF):
    
    def convert_metric(self,value,src):
        """convert units (in to mm, mm to in)
           src must be 'in' or 'mm'"""
        dest=self.metric_doc
        
        if src != dest:
            a={'in':39.37008,'mm':1000}
            return value*a[dest]/a[src]
        else:
            return value

    def get_height_chars(self,pt):
        """Give the line height for a given font size"""
        a={6:2,7:2.5,8:3,9:4,10:5,11:6,12:7,13:8,14:9,15:10}
        if pt in a:
            return self.convert_metric(a[pt],'mm')
        else:
            raise NameError('Invalid font size: %s' % str(pt))

                
    def __init__(self,format, unit='mm',posX=1,posY=1):
        if  isinstance(format,str):
            if format in commercial_labels:
                type_format=commercial_labels[format]
            else:
                raise NameError('Model %s is not in the database' % format)
        else:
            type_format=format

        super(PDFLabel, self).__init__('P',unit,type_format['paper-size'])        
        self.metric_doc = unit        

        self.margin_left = self.convert_metric(type_format['marginLeft'], type_format['metric']) # Left margin of labels
        self.margin_top = self.convert_metric(type_format['marginTop'], type_format['metric']) # Top margin of labels
        self.space_x = self.convert_metric(type_format['SpaceX'], type_format['metric']) # Horizontal space between 2 labels
        self.space_y = self.convert_metric(type_format['SpaceY'], type_format['metric']) # Vertical space between 2 labels
        self.number_x = type_format['NX'] # Number of labels horizontally
        self.number_y = type_format['NY'] # Number of labels vertically
        self.width = self.convert_metric(type_format['width'], type_format['metric']) # Width of label
        self.height = self.convert_metric(type_format['height'], type_format['metric']) # Height of label
        self.line_height = self.get_height_chars(type_format['font-size']) # Line height
        self.set_font_size( type_format['font-size'])      
        self.padding = self.convert_metric(3, 'mm')  # padding
          
        self.set_font('Arial')
        self.set_margins(0,0)
        self.set_auto_page_break(False) 
        self.countX = posX-2
        self.countY = posY-1          

    def add_label(self,text):
        """Print a label"""
        self.countX += 1
        if self.countX == self.number_x:
            #Row full, we start a new one
            self.countX=0
            self.countY+=1
            if self.countY == self.number_y:
                #End of page reached, we start a new one
                self.countY=0
                self.add_page()

        posX = self.margin_left + self.countX * (self.width + self.space_x) + self.padding
        posY = self.margin_top + self.countY * (self.height + self.space_y) + self.padding
        self.set_xy(posX,posY)
        self.multi_cell(self.width - self.padding,self.line_height,text,0,'L')

    def put_catalog(self):
        super(PDFLabel,self)._putcatalog()
        # Disable the page scaling option in the printing dialog
        self._out('/ViewerPreferences <</PrintScaling /None>>')
