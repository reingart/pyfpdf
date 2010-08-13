# ******************************************************************************
# * Utility to generate font definition files                                    *
# * Version: 1.13                                                                *
# * Date:    2004-12-31                                                          *
# *******************************************************************************/
from PHPutils import *
import os, re, struct, zlib

FPDF_FONT_DIR=os.path.join(os.path.dirname(__file__),'font')

def ReadMap(enc):
	#Read a map file
	filename=os.path.join(FPDF_FONT_DIR,strtolower(enc)+'.map')
	cc2gn={}
	for l in file(filename):
		if(l[0]=='!'):
			e=re.split('[ \\t]+',l.rstrip())
			cc=hexdec(substr(e[0],1))
			gn=e[2]
			cc2gn[cc]=gn
	for i in xrange(0,256):
		if not i in cc2gn:
			cc2gn[i]='.notdef'
	return cc2gn

def ReadAFM(filename,map):
	#Read a font metric file
	widths={}
	fm={}
	fix={'Edot':'Edotaccent','edot':'edotaccent','Idot':'Idotaccent','Zdot':'Zdotaccent','zdot':'zdotaccent',
		'Odblacute':'Ohungarumlaut','odblacute':'ohungarumlaut','Udblacute':'Uhungarumlaut','udblacute':'uhungarumlaut',
		'Gcedilla':'Gcommaaccent','gcedilla':'gcommaaccent','Kcedilla':'Kcommaaccent','kcedilla':'kcommaaccent',
		'Lcedilla':'Lcommaaccent','lcedilla':'lcommaaccent','Ncedilla':'Ncommaaccent','ncedilla':'ncommaaccent',
		'Rcedilla':'Rcommaaccent','rcedilla':'rcommaaccent','Scedilla':'Scommaaccent','scedilla':'scommaaccent',
		'Tcedilla':'Tcommaaccent','tcedilla':'tcommaaccent','Dslash':'Dcroat','dslash':'dcroat','Dmacron':'Dcroat','dmacron':'dcroat',
		'combininggraveaccent':'gravecomb','combininghookabove':'hookabovecomb','combiningtildeaccent':'tildecomb',
		'combiningacuteaccent':'acutecomb','combiningdotbelow':'dotbelowcomb','dongsign':'dong'}
	for l in file(filename):
		e=l.rstrip().split()
		if(count(e)<2):
			continue
		code=e[0]
		param=e[1]
		if(code=='C'):
			#Character metrics
			cc=int(e[1])
			w=e[4]
			gn=e[7]
			if(substr(gn,-4)=='20AC'):
				gn='Euro'
			if gn in fix:
				#Fix incorrect glyph name
				for c,n in map.iteritems():
					if(n==fix[gn]):
						map[c]=gn
			if(empty(map)):
				#Symbolic font: use built-in encoding
				widths[cc]=w
			else:
				widths[gn]=w
				if(gn=='X'):
					fm['CapXHeight']=e[13]
			if(gn=='.notdef'):
				fm['MissingWidth']=w
		elif(code=='FontName'):
			fm['FontName']=param
		elif(code=='Weight'):
			fm['Weight']=param
		elif(code=='ItalicAngle'):
			fm['ItalicAngle']=float(param)
		elif(code=='Ascender'):
			fm['Ascender']=int(param)
		elif(code=='Descender'):
			fm['Descender']=int(param)
		elif(code=='UnderlineThickness'):
			fm['UnderlineThickness']=int(param)
		elif(code=='UnderlinePosition'):
			fm['UnderlinePosition']=int(param)
		elif(code=='IsFixedPitch'):
			fm['IsFixedPitch']=(param=='true')
		elif(code=='FontBBox'):
			fm['FontBBox']=(e[1],e[2],e[3],e[4])
		elif(code=='CapHeight'):
			fm['CapHeight']=int(param)
		elif(code=='StdVW'):
			fm['StdVW']=int(param)
	if not 'FontName' in fm:
		die('FontName not found')
	if(not empty(map)):
		if(not '.notdef' in widths):
			widths['.notdef']=600
		if not 'Delta' in widths and 'increment' in widths:
			widths['Delta']=widths['increment']
		#Order widths according to map
		for i in xrange(0,256):
			if(not map[i] in widths):
				print 'Warning: character '+map[i]+' is missing'
				widths[i]=widths['.notdef']
			else:
				widths[i]=widths[map[i]]
	fm['Widths']=widths
	return fm

def MakeFontDescriptor(fm,symbolic):
	#Ascent
	asc=1000
	if 'Ascender' in fm:
		asc=fm['Ascender']
	fd="{'Ascent':"+str(asc)
	#Descent
	desc=-200
	if 'Descender' in fm:
		desc=fm['Descender']
	fd+=",'Descent':"+str(desc)
	#CapHeight
	if 'CapHeight' in fm:
		ch=fm['CapHeight']
	elif 'CapXHeight'in fm:
		ch=fm['CapXHeight']
	else:
		ch=asc
	fd+=",'CapHeight':"+str(ch)
	#Flags
	flags=0
	if 'IsFixedPitch' in fm and fm['IsFixedPitch']:
		flags+=1<<0
	if(symbolic):
		flags+=1<<2
	if(not symbolic):
		flags+=1<<5
	if 'ItalicAngle' in fm and fm['ItalicAngle']!=0:
		flags+=1<<6
	fd+=",'Flags':"+str(flags)
	#FontBBox
	if('FontBBox' in fm):
		fbb=fm['FontBBox']
	else:
		fbb=(0,des-100,1000,asc+100)
	fd+=",'FontBBox':'["+str(fbb[0])+' '+str(fbb[1])+' '+str(fbb[2])+' '+str(fbb[3])+"]'"
	#ItalicAngle
	ia=0
	if 'ItalicAngle' in fm and fm['ItalicAngle']:
		ia=1
	fd+=",'ItalicAngle':"+str(ia)
	#StemV
	if 'StdVW' in fm:
		stemv=fm['StdVW']
	elif('Weight' in fm and re.match('(bold|black)',fm['Weight'])):
		stemv=120
	else:
		stemv=70
	fd+=",'StemV':"+str(stemv)
	#MissingWidth
	if('MissingWidth' in fm):
		fd+=",'MissingWidth':"+fm['MissingWidth']
	fd+='}'
	return fd

def MakeWidthArray(fm):
	#Make character width array
	s="{\n\t"
	cw=fm['Widths']
	for i in xrange(0,256):
		if(chr(i)=="'"):
			s+="'\\''"
		elif(chr(i)=="\\"):
			s+="'\\\\'"
		elif(i>=32 and i<=126):
			s+="'"+chr(i)+"'"
		else:
			s+="chr(%d)"%i
		s+=':'+fm['Widths'][i]
		if(i<255):
			s+=','
		if((i+1)%22==0):
			s+="\n\t"
	s+='}'
	return s

def MakeFontEncoding(map):
	#Build differences from reference encoding
	ref=ReadMap('cp1252')
	s=''
	last=0
	for i in xrange(32,256):
		if(map[i]!=ref[i]):
			if(i!=last+1):
				s+=str(i)+' '
			last=i
			s+='/'+map[i]+' '
	return s.rstrip()

def SaveToFile(filename,s,mode='t'):
	f=file(filename,'w'+mode)
	if(not f):
		die('Can\'t write to file '+filename)
	f.write(s)
	f.close()

def ReadShort(f):
	return struct.unpack('>H',f.read(2))[0]

def ReadLong(f):
	return struct.unpack('>L',f.read(4))[0]

def CheckTTF(filename):
	#Check if font license allows embedding
	f=file(filename,'rb')
	if(not f):
		die('Error: Can\'t open '+filename)
	#Extract number of tables
	f.seek(4,SEEK_CUR)
	nb=ReadShort(f)
	f.seek(6,SEEK_CUR)
	#Seek OS/2 table
	found=0
	for i in xrange(0,nb):
		if(f.read(4)=='OS/2'):
			found=1
			break
		f.seek(12,SEEK_CUR)
	if(not found):
		f.close()
		return
	f.seek(4,SEEK_CUR)
	offset=ReadLong(f)
	f.seek(offset,SEEK_SET)
	#Extract fsType flags
	f.seek(8,SEEK_CUR)
	fsType=ReadShort(f)
	rl=(fsType & 0x02)!=0
	pp=(fsType & 0x04)!=0
	e=(fsType & 0x08)!=0
	f.close()
	if(rl and not pp and not e):
		print 'Warning: font license does not allow embedding'

# ******************************************************************************
# * fontfile : chemin du fichier TTF (ou chaine vide si pas d'incorporation)    *
# * afmfile :  chemin du fichier AFM                                            *
# * enc :      encodage (ou chaine vide si la police est symbolique)            *
# * patch :    patch optionnel pour l'encodage                                  *
# * type :     type de la police si $fontfile est vide                          *
# *******************************************************************************/
def MakeFont(fontfile,afmfile,enc='cp1252',patch={},type='TrueType'):
	#Generate a font definition file
	if(enc):
		map=ReadMap(enc)
		for cc,gn in patch.iteritems():
			map[cc]=gn
	else:
		map=[]
	if(not file_exists(afmfile)):
		die('Error: AFM file not found: '+afmfile)
	fm=ReadAFM(afmfile,map)
	if(enc):
		diff=MakeFontEncoding(map)
	else:
		diff=''
	fd=MakeFontDescriptor(fm,empty(map))
	#Find font type
	if(fontfile):
		ext=strtolower(substr(fontfile,-3))
		if(ext=='ttf'):
			type='TrueType'
		elif(ext=='pfb'):
			type='Type1'
		else:
			die('Error: unrecognized font file extension: '+ext)
	else:
		if(type!='TrueType' and type!='Type1'):
			die('Error: incorrect font type: '+type)
	#Start generation
	s=''+"\n"
	s+='type=\''+type+"'\n"
	s+='name=\''+fm['FontName']+"'\n"
	s+='desc='+fd+"\n"
	if not 'UnderlinePosition' in fm:
		fm['UnderlinePosition']=-100
	if not 'UnderlineThickness' in fm:
		fm['UnderlineThickness']=50
	s+='up='+str(fm['UnderlinePosition'])+"\n"
	s+='ut='+str(fm['UnderlineThickness'])+"\n"
	w=MakeWidthArray(fm)
	s+='cw='+str(w)+"\n"
	s+='enc=\''+enc+"'\n"
	s+='diff=\''+diff+"'\n"
	base=substr(basename(afmfile),0,-4)
	if(fontfile):
		#Embedded font
		if(not file_exists(fontfile)):
			die('Error: font file not found: '+fontfile)
		if(type=='TrueType'):
			CheckTTF(fontfile)
		f=file(fontfile,'rb')
		if(not f):
			die('Error: Can\'t open '+fontfile)
		filecnt=f.read()
		f.close()
		if(type=='Type1'):
			#Find first two sections and discard third one
			header=(ord(filecnt[0])==128)
			if(header):
				#Strip first binary header
				filecnt=substr(filecnt,6)
			pos=strpos(filecnt,'eexec')
			if(not pos):
				die('Error: font file does not seem to be valid Type1')
			size1=pos+6
			if(header and ord(filecnt[size1])==128):
				#Strip second binary header
				filecnt=substr(filecnt,0,size1)+substr(filecnt,size1+6)
			pos=strpos(filecnt,'00000000')
			if(not pos):
				die('Error: font file does not seem to be valid Type1')
			size2=pos-size1
			filecnt=substr(filecnt,0,size1+size2)
		if(1):
			cmp=base+'.z'
			SaveToFile(cmp,zlib.compress(filecnt),'b')
			s+='filename=\''+cmp+"'\n"
			print 'Font file compressed ('+cmp+')'
		else:
			s+='filename=\''+basename(fontfile)+"'\n"
			print 'Notice: font file could not be compressed (zlib extension not available)'
		if(type=='Type1'):
			s+='size1='+str(size1)+"\n"
			s+='size2='+str(size2)+"\n"
		else:
			s+='originalsize='+str(filesize(fontfile))+"\n"
	else:
		#Not embedded font
		s+='file='+"''\n"
	s+="\n"
	SaveToFile(base+'.py',s)
	print 'Font definition file generated ('+base+'.py'+')'

if __name__ == '__main__':
	MakeFont('font/calligra.ttf','font/calligra.afm')
	MakeFont('font/a010013l.pfb','font/a010013l.afm')
