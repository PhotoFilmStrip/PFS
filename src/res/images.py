#----------------------------------------------------------------------
# This file was generated by /usr/bin/img2py
#
from wx import ImageFromStream, BitmapFromImage
import cStringIO


catalog = {}
index = []

class ImageClass:

    def getBitmap(self):
        return self.GetBitmap()
    def getImage(self):
        return self.GetImage()
    def getData(self):
        return self.GetData()



def getALIGN_BOTTOMData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x02\
\x00\x00\x00\x90\x91h6\x00\x00\x00\x03sBIT\x08\x08\x08\xdb\xe1O\xe0\x00\x00\
\x005IDAT(\x91c\xfc\xff\xff?\x03)\x80\x89$\xd5\xa3\x1a\x06\x8d\x06\x16\x08\
\xc5\xc8\xc8HP)$M0\xc2\x93F]]\x1d\x1e\xd5MMMP\xa3IMK\x83\xd0I\x00\xa8\t\x1b\
\x11\xc6\n\xa4\xf8\x00\x00\x00\x00IEND\xaeB`\x82' 

def getALIGN_BOTTOMBitmap():
    return BitmapFromImage(getALIGN_BOTTOMImage())

def getALIGN_BOTTOMImage():
    stream = cStringIO.StringIO(getALIGN_BOTTOMData())
    return ImageFromStream(stream)

index.append('ALIGN_BOTTOM')
catalog['ALIGN_BOTTOM'] = ImageClass()
catalog['ALIGN_BOTTOM'].GetData = getALIGN_BOTTOMData
catalog['ALIGN_BOTTOM'].GetImage = getALIGN_BOTTOMImage
catalog['ALIGN_BOTTOM'].GetBitmap = getALIGN_BOTTOMBitmap


#----------------------------------------------------------------------
def getALIGN_MIDDLEData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x02\
\x00\x00\x00\x90\x91h6\x00\x00\x00\x03sBIT\x08\x08\x08\xdb\xe1O\xe0\x00\x00\
\x008IDAT(\x91c\xfc\xff\xff?\x03)\x80\x89$\xd5\xc3D\x03\x0b\x84bdd$\xa8\x14\
\x12\x9e\x8c\xf0`\xad\xab\xab\xc3\xa3\xba\xa9\xa9\tj4\xa9\xf10\x08\x9d4\x08#\
\x8ed\r\x00\xff\xe7\x1b\x11\x8b\x08\xd3\x10\x00\x00\x00\x00IEND\xaeB`\x82' 

def getALIGN_MIDDLEBitmap():
    return BitmapFromImage(getALIGN_MIDDLEImage())

def getALIGN_MIDDLEImage():
    stream = cStringIO.StringIO(getALIGN_MIDDLEData())
    return ImageFromStream(stream)

index.append('ALIGN_MIDDLE')
catalog['ALIGN_MIDDLE'] = ImageClass()
catalog['ALIGN_MIDDLE'].GetData = getALIGN_MIDDLEData
catalog['ALIGN_MIDDLE'].GetImage = getALIGN_MIDDLEImage
catalog['ALIGN_MIDDLE'].GetBitmap = getALIGN_MIDDLEBitmap


#----------------------------------------------------------------------
def getALIGN_TOPData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x02\
\x00\x00\x00\x90\x91h6\x00\x00\x00\x03sBIT\x08\x08\x08\xdb\xe1O\xe0\x00\x00\
\x002IDAT(\x91c\xfc\xff\xff?\x03)\x80\x05B122\x12T\n1\x9a\x11nC]]\x1d\x1e\
\xd5MMMP\xa3\x87\x81\x93\x98HR=\xaaa\xd0h\x00\x00\xed\xc4\x1b\x11\xc3\x86\
\x15l\x00\x00\x00\x00IEND\xaeB`\x82' 

def getALIGN_TOPBitmap():
    return BitmapFromImage(getALIGN_TOPImage())

def getALIGN_TOPImage():
    stream = cStringIO.StringIO(getALIGN_TOPData())
    return ImageFromStream(stream)

index.append('ALIGN_TOP')
catalog['ALIGN_TOP'] = ImageClass()
catalog['ALIGN_TOP'].GetData = getALIGN_TOPData
catalog['ALIGN_TOP'].GetImage = getALIGN_TOPImage
catalog['ALIGN_TOP'].GetBitmap = getALIGN_TOPBitmap


#----------------------------------------------------------------------
def getALIGN_LEFTData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x02\
\x00\x00\x00\x90\x91h6\x00\x00\x00\x03sBIT\x08\x08\x08\xdb\xe1O\xe0\x00\x00\
\x00ZIDAT(\x91c\xfc\xff\xff?\x03)\x80\x89$\xd5\xe4h`\x81P\x8c\x8c\x8c\x04\
\x95B\x1c\xcf\x08\xf7C]]\x1d\x1e\xd5MMMP\xa3I\xf54\x16\'\xe17\x82\t\xae\xa8\
\xb6\xb6\xb6\xb6\xb6\x96\xa0\x85\xd4p\x12&@6\x94p(\xc1\xc3\x87\xdaN\xc2e\x10\
v\'\xa19\x83"\'\x91\x9c\xf8\x00L\xb05\xf1\xd13Ja\x00\x00\x00\x00IEND\xaeB`\
\x82' 

def getALIGN_LEFTBitmap():
    return BitmapFromImage(getALIGN_LEFTImage())

def getALIGN_LEFTImage():
    stream = cStringIO.StringIO(getALIGN_LEFTData())
    return ImageFromStream(stream)

index.append('ALIGN_LEFT')
catalog['ALIGN_LEFT'] = ImageClass()
catalog['ALIGN_LEFT'].GetData = getALIGN_LEFTData
catalog['ALIGN_LEFT'].GetImage = getALIGN_LEFTImage
catalog['ALIGN_LEFT'].GetBitmap = getALIGN_LEFTBitmap


#----------------------------------------------------------------------
def getALIGN_CENTERData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x02\
\x00\x00\x00\x90\x91h6\x00\x00\x00\x03sBIT\x08\x08\x08\xdb\xe1O\xe0\x00\x00\
\x00dIDAT(\x91\xa5\x92\xc1\n\xc0 \x0cC\xd7\xe1o\xa7\x07\x7f<\x1e\x1c\xa5\x9b\
\xd5Q\xf5"H\x9a\xbc\x06\x85\xe4\x959wJ\xbd3P\xfa%"\xbf\xd2\x0e/\xb6\x83\xaa.\
\xd4\xb5\xd6\xc7:\xbbt\x19\x9f<\xdeh\x17,M\x12\x00\x800\xfc\x00i]\x94\xf9\
\xbe\x12fEYEgH3\xb0\x8fc\x90\xe0\xc1<\xcc&R\xfa\xf35u\xc15\xf1k\xf5]\xeb\x00\
\x00\x00\x00IEND\xaeB`\x82' 

def getALIGN_CENTERBitmap():
    return BitmapFromImage(getALIGN_CENTERImage())

def getALIGN_CENTERImage():
    stream = cStringIO.StringIO(getALIGN_CENTERData())
    return ImageFromStream(stream)

index.append('ALIGN_CENTER')
catalog['ALIGN_CENTER'] = ImageClass()
catalog['ALIGN_CENTER'].GetData = getALIGN_CENTERData
catalog['ALIGN_CENTER'].GetImage = getALIGN_CENTERImage
catalog['ALIGN_CENTER'].GetBitmap = getALIGN_CENTERBitmap


#----------------------------------------------------------------------
def getALIGN_RIGHTData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x02\
\x00\x00\x00\x90\x91h6\x00\x00\x00\x03sBIT\x08\x08\x08\xdb\xe1O\xe0\x00\x00\
\x00^IDAT(\x91\xb5\x92\xc1\x0e\x800\x08C\xad\xd9o\x97\x03?^\x0f\x98\xc5\xa8c\
aF.\x1c(\xe4\xb5\x01\x92\xb6J\xed%\xf5\xcaB\x8b\x06`*\rxt\x0ff\x96\xa8\xdd\
\xfd<]5\xdd\xf2\xf1\x155NOLK"I\xb2\x83|C\xca\xb3\xba\xa7\x145\xca\xea\x87\
\x94\x9ex\xefH#\xbcu\xa4\xf2\xf3\x1d\x9e\xd25\xf1N\xb7\xdbU\x00\x00\x00\x00I\
END\xaeB`\x82' 

def getALIGN_RIGHTBitmap():
    return BitmapFromImage(getALIGN_RIGHTImage())

def getALIGN_RIGHTImage():
    stream = cStringIO.StringIO(getALIGN_RIGHTData())
    return ImageFromStream(stream)

index.append('ALIGN_RIGHT')
catalog['ALIGN_RIGHT'] = ImageClass()
catalog['ALIGN_RIGHT'].GetData = getALIGN_RIGHTData
catalog['ALIGN_RIGHT'].GetImage = getALIGN_RIGHTImage
catalog['ALIGN_RIGHT'].GetBitmap = getALIGN_RIGHTBitmap


#----------------------------------------------------------------------
def getICON_32Data():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00 \x00\x00\x00 \x08\x02\x00\
\x00\x00\xfc\x18\xed\xa3\x00\x00\x00\x03sBIT\x08\x08\x08\xdb\xe1O\xe0\x00\
\x00\x06RIDATH\x89\xd5\x96K\x8f[I\x15\xc7\xcf\xa3\xaa\xee\xcb\xbev?\xdc\xedn\
w\xba;\x19\x02IfB4 \r\x02$\x86l\x90X\xb0\xe0;\xf0\x01X\xf2e\xf8\x0e,\x10b\
\x83\x10\x12BB\xa3Q&\x1aF"Q\xde$\x99n\xb7\xdbm\xfb\xda\xbe\xf7\xd6\xeb\xb0\
\xb0fX"\x16\x19\x89\xdf\xa6\xce\xa2\xaa\xce\xd1\xbf\xfeut\x00\xde1\x08\x00"\
\x82\xf8?\x04\xd3\xdf\xe2\xe6\xf0\xce\xaf\xe0\xbfn\x86\xff,\xef2\xf8\x7f\x06\
\xb3,\x1b\x0c\x86\x848\xb9\x1c\xe7y\xa1\x14\x1313\x89@\xd3\xb4E\x91[k\x99Q\
\xabd{{\xbb\xae\xeb\xd9\xd5\xac\xe8tV\xab\xaaZV\xcc\xec\x9cSJ\x19c\x12\xad\
\x01Q\x13\xf5\xfa;\x93\xc9Y\x14 \xe6f]sY\x96\xeb\xd5jgw\xcf{\x07 \xc1{\x00`&\
\xe7\\\x08\xde{O\x88!F\xeb\x9d\xd1\x86\x08\xeb\xb6v\xce\x86\x18\xea\xba\x16\
\x11"r\xce\x15EQd)D\xd8\x1f\x8e\x9a\xf5\\\xa2\xb06i\x92\x00\x01\xf5z\xdb\xfd\
~\x7f\xb5Z\x1e\x8dN\xd3$%\xe6\x10\x82\xb5\xce9\xe7\xbdo\xdb\x06\t\xbd\xf7\
\xc1\xb9u]gif\x94&\xc4\xaf}\x02\x00\x88@\xc4\x00\xd2\xef\xf5\x14#\x91\n\x88\
\xc1\xfb\xbanL\x92P\xf0\xa1\xdb\xeb[\xdbT\xcb\xc5\xfep\x14cd\xe6\x10\x023{\
\xefc\x8c\xde\xfb<\xcfEb\x0c!FD"&\x1dc\x8c1\x02\x80\x88\x88\x00!6\x8d\xcd\
\x8a\xeex|\xd6\xb665\x89\xd2Z\x99\x04\x81Y\x1b\xe5\x9d\xbbvt}\xb5\x9cy\x1f\
\xb6\xfa\xdb\x93\xc98\x84\xa0\x94\xda\xdc\x92eY\x96v\x10\xa1m\xdbN\xd1\x8d\
\x12Y\xf1j\xb5r\xce\x12\x91\xc4\x08\x80Y\x96\xe7\x9d\xee\xba\x9a\xb7\xd6\nR\
\x92\xe6\xcb\xd5r\xa39\xf7\xb7\xb6\x08q\xb1\x98\x8fF\xc7\xebUe\xd2\xac\xaekk\
\xdb\x10\x82\x88x\xefE\xa4\xect;y7I\x93\x93\xe3\x1b\x00\xb0Z/\x97\xcbE\x08\
\x01\x11D\x84\x98\x01\x84\x15/W\xabn\xb7\x07 \xf3j\xde\xb4\r\x12\x10+\xca\
\xd2Tk\x9d\xa7\xe9\xe5\xe4|\x7f8\x9a\xcf\xa6\xa3\xd1\x89\x08\x84\x10\x00\x04\
\x00\x9cs>\x84^\xd97&\xdb?88\xd8\x1f%&eV\xb2Q\x07D \xd6\xf5z6\xbdJ\xd2l\xb1\
\x98W\x8b\xb9\xb7-#H\x14\x10 \xa5\x0c!\x01Jk\x9b\xa7O\x1f\xf5\xb7v\xde\xbey\
\xd5\xedv7\xfa \xa2R\xaai\xda\xd1\xd1\x89\x080q\x04<\x1c\x8e\x08\x91\x88\x10\
\x11\x01\t\t\x11\x93,Y\xaf\x96!F\xd6F\x19\x93fE\xaf\xec\xed\xee\xee*\xadLb\
\x12\xa5\x14\x00\\^^\xbcx\xf1\xa4\xd3\xe9V\x8b\x05\x00\x80\x00\x02x\x1f\x9av\
=\x9b\xcfww\x87\xc3\x83\x83eU#\x821\x89\xf3\xbem[\xadu\x0c\x11\x10\x9a\xbaaf\
\xf1!K3\x80\x08HD\xd8\xc9\x88\xcb\xb2\\\xd7+o\xad\xb3\x8d\xd1Fi\xb3\x98\xcf\
\x90\xc8Z\x8b\x08\x02\x18c\xd8x\xa9\xd7\xeb\xdf~\xffV\x9af\x17\x17g\xd3\xe9\
\x85\xb5\xd6{\x0f\x00!\x06f\xd6Z\x07\x1f\xf2<\xcf\xd2|\x7f8b\r\x07\xfb\xc9\
\xc7?\xbeC\xact\x08\xd1\xf9P\xadV\xd3\xd9dY\xcdE\xa4m[\x00\x08QDDk\xed\xbd\
\x9fN\xc7Y^L\xa7\xf3\xbc\xc8\x8e\x8fO\x942\x00\xb0I,"!\x04\x00`\xc5E\xa7\xbb\
wp8\x9eN\x8a\x92O\xaf\x1f\xde\xfa\xf6u\xee\x95%\x11\x8a\x08\x080+V\x1cB\xdcX\
\xe8k\x00 \xcdr\xad\xcc\xde`o8<D\x89\xd3\xe9eUU\xeb\xf5j\xf3\xe3L\x92h\xa5ze\
y\xff\xfe\xdd{\xf7\x06\xe3\xcb\xf5\xdd\xdb\x077\xdf;\xbdyr\xa8\x8c1D\x1c\xa2\
_-+\xef\xbd\x08\xe0\xe6\xf1\xbe"\xc6\x88HJ)f\xb4\xd6\r\x0f\x06\xe7goF\x87\
\xd7&\x93\x8b\xc9\xe5\x18\x00\x880\xfa\xd0\xdb\xc9\x7f\xf3\xeb_\xee\x1f\xed>\
y\xf6\xaf_\xfc\xec\x83\xb2H\xbeur\xed\xaf\x7f~\xa0\x889\xd5\x86t\xbe\xb33X\
\xcc\xa7\xcbj\xe9\xbc\x8d\xc1\xc7\xaf@D\x00!d\x11l\x9a\x1a\x89\xf3<\x1f\x8f\
\xcf\xab\xe5bS\x07!&\xc6\xfc\xe0\xa3\x1f\x1a\xac;\x1a\xbe\x7f\xf7\x86\xf3\
\xce\xd6\xf1\xc1\'_\xfc\xeeO\x0fU\xdb\xd4e\xc7\xbcw\xba\xfd\xf8\xf9$\n\xa4E\
\x07\xea:\x15 \xb6m\xdbz\xef7\xed\xa0(:\xc1{\xad\xf5|vU\x96%"\x96e\x7fQ\xcd\
\xdb\xb6a\xa2\xac\xe8|\xef\xa3\x8f_Lg_<y4\xdcU\x11\xc2\'\x9f>{\xf0\xf9\xeb\
\xda:U\xf6z\xfdr\xe7G\x1f\x1e\x1d\x1f\xef\xbc|;~\xf9z\x9a\xe7;\x83\xdd\xe2\
\xf1?\xdf\xbcz\xf5\xe5j\xb9\x02\x80\x10\xa3\x0fn<9\xaf\xdb\xf6\xe1g\xff\xb8q\
\xe3FVd\x80\xb0i\xbdH\xc4\x8c\x7f\xfc\xc3\xef\xcbrk|~v5=s\xae\xf6!\xb4\xd69\
\xefyo\xb0\x97wJ\x8a\xf1\xfeO\xef\xf6\xfb\xdd\xfd\xdd\xec\xf6w\x86\xf7>8\xfd\
\xf9O\xeel\x15\xea\xed%\xac\xd7\x15\x086m\xad\x95F\xc0j\xb1\xf0\xde\x85\x10^\
<{BD\xb6m\x88P\xb1b\x08\xd3\xcb\xf3u\xbd\x10\x88\xd6z\x01t\xce\'I\xc6\xfb\
\xc3!\x08,j|\xfd\xf2\xcd\x87\xb7\x8e\x8e\x0ew\x8f\x0f\xb63\xe2\xc9\xd9\xd5\
\xc3\xa7r\xfd\xe6\xfbO\x9f<\n\xc1\x03b\xd3\xd4>x\x04\xb2m;\xbd\xbc<\x1f\xbf\
\xad\x96U\x94HD\x89I\xcaN\x17\x95\n1\xb4\xad\x8d1 \xab,\xcb{\xe5\x16\x0f\x06\
C\xc5L\x8c\xf3\xa5\xff\xcb\xdf\x1e\xa3>}\xfd\xe5\xfa\xd3\xcf\x9e\xff\xfd\xf3\
\xabg\xcf^>\x7f\xfa\xb8i\xd6\xd69\xef\xbd\x80x\xef\x89h]\xaf\x89\xf1\xe2\xe2\
Lk\x1dcPJeY\xeaE\xb4\xd2.\x84\xba\xae\x89U\x9eu\xd243:\xc1;\xb7\xbf\x8b\x04\
\x8aU\xaf_*\xc5\xd5\xa2\n\xdeG\x89JkD\x94\x10\xe7\x8b\xd9\xe4r\xd24-\x000\
\xb3R\xfa`xT-\x17\xde\xb7\x1b\x170s\xa7\xd3QJ\x0f\x06\x03\x04h\xadE\xe0N\xb7\
,\xf2b6\xbbR\x02BH\xce\xf9\xd9\xd5<MS J\xd2D\x9b\xc4;\xeb\xbc\x07BD2&\xd9$\
\x00\x00\x91\x18\xa2\x17\t\x1bb\x8cD\x14c4\xc6\x88\xa01I\x92\xe6\x08\xa8\x94\
\xf2\xde&&\xe1\xa2\xc8\xda\xb6%&\xa5T\x14\x90(\x80dm\xcb\xaclk\t\xa9i[\xef\
\xbd\xb5VD\x98YD\xbcwe\xd9k\x9a\x9a\x886\xfd\x1c\x00\x8a\xa2\xa3\x94FB\xad\
\x8dD\xa9\xeb\x15\xb3j\x9a\xf5\xbb\x9eZ\xbe\x19\xde\xe9\xe8H\xef\xae\xeeo\
\x88\x7f\x03\xb7a5\xeb\xe2\xe6\x01J\x00\x00\x00\x00IEND\xaeB`\x82' 

def getICON_32Bitmap():
    return BitmapFromImage(getICON_32Image())

def getICON_32Image():
    stream = cStringIO.StringIO(getICON_32Data())
    return ImageFromStream(stream)

index.append('ICON_32')
catalog['ICON_32'] = ImageClass()
catalog['ICON_32'].GetData = getICON_32Data
catalog['ICON_32'].GetImage = getICON_32Image
catalog['ICON_32'].GetBitmap = getICON_32Bitmap


#----------------------------------------------------------------------
def getICON_48Data():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x000\x00\x00\x000\x08\x02\x00\
\x00\x00\xd8`n\xd0\x00\x00\x00\x03sBIT\x08\x08\x08\xdb\xe1O\xe0\x00\x00\x0cM\
IDATX\x85\xedXI\x8f$\xd7q\x8e\x88\xf7\xf2\xe5^KWu\xf5:\xd3\xd3\xa3\xe1h(Q\
\x94(\t\x84\x00K\x80a\xc37\xfb\xe2\xa3\xaf\x96\x7f\x94\x01\xff\x00\x19\xf0\
\xcd\x10$\x1fd\x03&M[\x80EA\xf4pH\x89\xcbt\x0f\xa7\xd7\xea\xb5\xb2ryk\xf8\
\x90\xa56\xe0\x83\x08\xc8:\xf80\xdf\xa1P\xaf*\xeb\xd5\x97\xf1\xbe\xf8""\x01^\
\xe1w\x03\x01\x80\x99\x01\x00\x11\xfb\x8f~\xef\xe5\xe5\xdf\xad6\x9d\xfc\x10~\
\xff\xad\xfe\x80\x84\xfe K\xfa\xf2 \xbe\xc2+\xfcN \x00\xa4iZ\x96\xc3\x9d\x9d\
\xfb/\x8f\x0e\xba\xb6U*\x1e\r\x87uS\x13\tD`\x86(Ru\xbdD\xc44M\x00\xb0\xeb\
\xda(\x8a\xac\xb5\xeb\xd3\xf5"/\x00\xf1\xe0\xe0\xb9\x8aT\x1c\xc7Zw\xd6\xbb\
\xe5r)\xa5\x0c!\xf4:\x95R\x0e\x87C\x0cA\xeb.\xcb\xcbD\xa9\xe1p\xed\xfc\xec\
\xa85\x86\x90\x18!K\xd3j\xb1p!\x9c\xcf\xe7\x02\x00\x86\xc3a\xd7u\xd6\xba\xed\
\xed\x9d\xb6\xad\xaduD\xd4u\x1d"\xa4i\xc2\xcc\xceY\xe6\x10B@D\xef\xbc\x90\
\xb2_\x02R\x9a\xa6\xd6\xd9\xe5\xb2Rq\xdc\xe9\xce\x07\x1f\x02k\xad\x01\x80\
\x88\x00 \x84\x00\x00\xa3\xd1HE\x12\x98\x11p{\xfb^\xb5\xb8d\xef\x90\x10\xa5\
\x1c\x94\xa5\xd1\xc6q(\x8b\xf2\xea\xea\x8a\x00 M\xb3\xc9d\xa2uk\x8d__\xdf\
\x1e\x94\x85u6\x8a"\xef}\xd3\xb4\xce9c\x8c\xf7.\x84\xd0\xd4u\x14\t\xef\x9d\
\xd6Z\x10\xb5\xed\xd28\x17EQ\x91e\x84\x90\xa6)\x11\xe1\xff:\x02\xc4\x10X\x08\
\xe1\xbd\xcf\xd3l}:\x03\x0c@\x18\x90\x18e\xf0\xa1\xaa*\xeb\xdd`0\xb0\xceA\
\x9f\xf6Y\x96\x1bc\xd6\xd6&u[\xa5I^\x16\xe3~\xeb,\xcb\xbd\xf7RJ"\xf2>8\xe7\
\x18\xc03\x0b\xa2\xfe\xc8\x9cu\xd6\xd8,\xc9\x02c\x08\xc1h\r\x00\xdah\x00\x08\
\xcc\x88\xd8{\x8c\x94\x92}p\xce\x06\x80\xac,\xaf./0\x80gDd)I\xc513\xd4u\x13E\
\xd1\x8a\x90\xb5~g\xe7\x9e1\x9dw\xe6\xea\xfab}\xb6\xc1\x8c\xd6\xda\xaek\x89\
\xc8\x18#\x84\xe8\x83\x1fB\xd0]\x07\x88e9\x10R\x04\x0e\x84\xe4\x1ckc\xcab(\
\x84\n!\x00\x033\x033"\x06\xef{\x8d.\xeb\xa5\xb3a\xba\xb1u\xfa\xf2e\xdb\xd4m\
\xd7F\x91L\xa2\x18Q\xf8\x00B\xaaA1\x94B\x02@\xffO\xce\x18\xbb\xff\xe0Q\xd7v\
\xccn>\x9f\x7f\xeb\xad\xef\x9e\x1c\x1d9k\xb4\xd6D$\x84@D\xe7\x9c\x10"\x8a\
\xa2X\xc5I\x92\x87\xe0\xadu\xc0\x18GJ\n\xd2F\xcbH\xb5m\xeb\xbcs\xce!\xa2 \
\xe1\x83\x07\x80\xd1xR-n\xf3b\x90%\xc9\xc5\xe5\x19\x03\x06\xe0(JE\x14\xb5mk\
\xb4f\x0e\xdat\xcc\xe1\xfa\xe6\x86\x00`mm\xc2\xec_\x1e\xbd\x98\xcd6\x8b\xbcd\
o?\xfb\xf4\x93\xc7\x8f_\xef\xc3\xae\xb5v\xce\xf5\xda\xb4\xd6:\xe7H\x08\x81B\
\xc9D\x92\x18\x0c\xca\x8d\xcdM\x15g\x82\x14\x11\xdee\x16"p\xf0\xbcZ\xa2\xf3a\
\xbc6yq\xf4\x05 \xba\x10\x8ar\xcc\x1cnn\xae\xbb\xaeu\xde\x11a\x1c\'\x81a\x15\
\xa1\xa2(B\x08\xde\xbb\xea\xf6f\xb6\xbe5\x9dN//NPH\xa5\xd2\xe5r\x81\x88\xde\
\xfb\xbe\xd4\xf4\xa7\x86Hq\x12O\'\xb3\xaa^>y\xf2\xfa \x1f\xaeO7\xe6W\x17MSu]\
\xeb\xbd\xf3> \x92 \x0c\x81\x91\xc8[\xabb\xb5X\xdc8k\xb3\xbc\x18\x8e\xc6\x8b\
\xdb\x9b\xae]v\xda\xf8\xe0\xbd\xf7D\xe4\xbd\x8f\xe3\xe4\xea\xea\x92\x00\xa0(\
\x06i\x9aeiV\x94\xc5\xf5\xf5\x85gX_\xdf\xbe\xba:\x9b\xcd6\xb2\xac\xe8c\xd3\
\xdfw\xff\xc6\x18\x1dIE\x80i\x9c J\x92r6\x9bno\xee\x02S\x1c\xc7\x88tw=\x03\
\x13Q\xa7\xbb\xb6i\xb4\xd6*N\x84\x8c\x8e\x8f\xbe\xe8\xda:0\x03\xfbH\x90 B\
\x00A\x82}X\x89\xfa\xe6\xe6\xca9m\x8d\xb6FW\xf5\xed\xd1\xcbC@\x1c\x8ff\xbf\
\xfe\xf8\xd9lc\x93\x19\xbc\xf7\x1c\x02\x02 \xa2\x94\xd2Z\xcb\x80\xdb\xdb\xf7\
\x87\x83a\xdbvR\xa8\xb3\xf9|c}6(\x06\xb1\x8a\x89h\x95^\x08\x04HH!\x04)\xe5p8\
p\xd6\xde\xde^\x91@F\x04D$b\x00AB\nY\x16E\x96\x17+B;;\xf7G\xc3\xe9\xfa\xfa\
\xa6R\x89$\xa1M\xf3\xfc\xf9\'.\xd8$Qg\'\xc7I\x920C\xe0\xc0\xcc=\xa78N\xce\
\xcf\xcf\x02C\x9a\r\x00\xc4kO\xbeb\xac=?\xbbx\xed\xf1\x13\x19I"\x81\x88\xcc\
\xc0@$d\xafn\x06^,*c\x0c\x02!\x88H*"\x99$iY\x0eg\x1b\x1b\xa3\xf1\xb8\x1c\x0c\
\x94\x84\x15\xa1\xb6m\xad5m\xd7fy\xb9\xb9\xb5;\x18\x8cC\x08\'\xc7/\x91\x90\
\x04\x19\xa3\x018\x04 ""\xd4\xba_\xda\xcb\xabKm\xf5\xbd\xfb\x0f\x84\x88\xe28\
\xdd\xdc\xde\xc9\xf3\x82P\xc4\xb1\x12B0\xb3\xb56R\x91u6p\x08> "\t\xeat\xe7\
\xbc\x8f\xe38\xcfR%E\x08\xbe\xae\x97\xde\x998\xe2\xaf?^[\x89z0\x18v\xba5\xba\
\xf3\xceT7\xb7*R\xc3\xf1\x98\x10oo\xaf\xa38v\xd6z\xe7\x85\xc0^\xaa\x00`\x8c\
\x15\x82\xda\xb6\x1d\x8f&i\x9a\xec\xed\xdf\xf3\x8e\xee\xdd\xdfz\xfa_\x1f4\
\xcd\xd29k\xad\xbds\xea\xde\x02\xa4\x94\xbdY\x13Q\x9a&Q\xa4\x08\xa3\xe1x2\
\x1c\r\x81\xbb\xad\xad\xec\x8d\xaf\xdd\xfb\xe6\xe3\xfb?\xfe\xd9/\xa8ww\x06\
\x88\xe34\x04\x16\x11-\x97\xd7\xf3\xb3\x93\xb6k\x91hYU\xce9@\xf0\x8e\x111\
\x84 \x84\x00`\xad\xf5\xa2\xba\xf6^w\xdaJ\x95X\xd3\xde\xdf\xdb\xdd\xde\xde\
\x01\x80\xa6m\xfb|df\xad53\xf7IDD\xc0\xac\x94\x12$\xe38{\xe3\xcdo2\xfb\xa3\
\xa3\xc3\x87\x8f&\xdb\xdb\x1bO\x1e=\xd8\xff\xca\x0e\x00H\x00\xf0>\x04\x1f\
\xda\xae\r\xce\x86\xc0\xde[\x00\x0c\xd6r\x00D\xbc\xcb\x97>\xdd\xa2(r\xce13"\
\x1c\xbex\xf1\xc6\x9b\xdf\x9d\x9f\x9du\xda&\xf9 \x8e\x93\xf1hRU\xd52T\xc6\
\xf0]\x90\xac\xb5q\x1c33\x03\x10\x8a\xf1d:\x1c\r~\xf5\xf4\xa9\x07\xbf\xbb\
\xbf\xbb\xbb\xb3>,\xcb\xe9\xe6\xd4\x19^\x11"\x04"\n!\x88H\t\xe6\x98bf`\xe0\
\xa6i\x82\rw\xfb\xf6\xcc\x8c1\xcc\x8cHJ%R\xe0\xf3\xcf>#\xe0\xbd\xfd}\xf6\xbe\
,\x8a\xf1xr\xbb\xb8\xb1\xce\xb6ms\xe7\x14Q\x14EQ\xd4\x0bk:\x1d\x7f\xef\xed\
\xbd\'\xaf\xaf\x7f\xf0\xe1\xe8\x9d\x7f\xff\xf4\xf1\xa3\xf5\xe9`\xb4\xb6\xb1\
\xb5\xbd>\xfe\xc9?\xbe\xbb"$#\x99\xa6\xa9\x0f\xbeZ,\x8c\xd1\x1c\xd8{\x8f\x84\
\x88$\xa5\xf4\xde\xdf\xf9/3\xf7\x9a@\xc4X%u]\x95e\x06\x80[\x9b3"X\xd6\xcd\
\xfe\x83}\xefL\xd7\xb4\xb77WH\xc4\xcc}}\xf5\xde\x13\xd2\x9b_{\xfc\xc3\xbf\
\xfe3\xeb\xcc\xe5\xc5\xc5\xde\xeep\xf7/\xbf!\x80\xcaA\xf9\xe4\xc1V}q\xf9/\
\xef>[\x11\x8ad$H\x08!\x07\x83\x81\xb5\xc6:\x0b\x0c\xd6\xb9\xb6m\x9d\xb3\xde\
{\xf8-\x1b\xf8\x9fQ\x81\x9d7E1h\xda\xfa\xec\xec\xcc8;\x1e\x8f\x94R!\xf8j\xb9\
$!\x91\xa8?bB\xe0\x10\x80yow\xe3o\xfe\xea;\xf7\xb6G.\xc8$V\xd7\xd7\x8b$K\xd6\
\x8a\xa4,\x12\xe5\xf5\xdf\xfe\xfd\xbfuL+B\xce\xb9,OX`\x9aeq\x1c_]\xce\xad\
\xd6!pY\xe6m\xdd \x92\xb5\xb6/\xaeww\xcc\xcc\xc1\xf3`<\xf6\x16Z\xdf"r\x9cdJ\
\xc9\x83\xc3\xe3\x93\xd3\x97B\xca\xfe2"B\x04B*\xcb\xd1[\xdf\xf9\xc1\xe7\x877\
e~<\x98L\xf7\xb6\xc6\xbb\x1b\xa5\x0f\xbc\xb8\xd5\xd5u\xf5\xa3\x1f\xbd\xf3\
\xe1\xc1\x15 \xac\x08\x19\xab\xb5\x91;\xdb\xe3\xebEWU\x86\x84Pi\xa6\xb2\xac^\
V\x80]\x12\xc7BH\xe7\xeco\x0b\x19p\xdf` mnm,n\x9b\xfd\x87\x0f\xbd\xe7\xeb\
\xeb\xab\xe9l:??\x03\xa6\xf1hrss\xbd\\V\xbd:I\x88\xe1h\xfa\xf6\xf7\xbe\x7f~v\
\xfa\xd3w~\xf9\xd5\xfb\x17;[\xe3(\xcf\x98\xedG\x1f\x9d\xfc\xf8\'\xbf:\xbd\\z\
\xe0U\xbf\x0b\x00\xd3\xe9z\x99\xca?\xfd\xa3\xfd\xcf\x8f\x97\xcf~s\\U\xba\xd3\
\xfa\xfc\xbc)\x07\x83\xf1z\xd2\xd65\xea.\x04\x8f\x88\x82\x88W\xbf\xc4$N..\
\xe7\xcc\xe2v\xb18?=\xad\xabz\xb26S\xd1g\x83rx1\x9f\x0b\x12\x00\x00H\x84$\
\xa5D\x08\x1f\x7f\xf4\xeb\xfd\x87{*\xfe\xe3\x7f~\xef\xbd\xa6\xf9\xc85\x97\
\xd5\xa2Y4\x8d\x0fh\xbd\xd3\xc6\xf4G,\x00`o\xef\xa1\x10\xe9\xd6\x08\xdf|\xe3\
\xe1\xde\x83\xe9x-\x9f\xac%I\x16on\x0c\xfe\xe2\xcf\xbf\xb1{o\x96\xc6\xca\xda\
`\x8c]\x19.\x113\xabHi\xddEJ\xed\xec\xdc\xeb\x9a& \x18\xed\xcaa\xfa\xcb\xf7\
\xdf\x9f\xac\xaf\x1d\x9f\x1c13!\x12!\tY\x14\xd9\xe9\xf1\xcbg\x1f>}\xff\x17?\
\x9f\x9f=\xafn\xae\xab\xbam\x8c\xb16X\xe7\xbd\xf3\x0c\x8cH\xcbe%\x00`\xb6>\
\x9bL\xa6\x87\x87\xd7\x7f\xf2\x83\xfdb\xb4\x96g12oo\xe6\xfb\x0f&y^>y4\xfb\
\xfe\xb7_\xfb\xd6W\xa7\xf3\xcb\xa6\xb5Q\xd75\x82\x88\x19\xda\xae\x15B\x10\
\x89$I\x0e\x0e\x9e\x0b\x12y\x9e^]]\x9e\x9f\x9dV\xd5"\xcb\xf3\xaa\xbaE\x04$\
\x14$"!\x04!{k\x9d\x16R\x92 m\xad\xb3!R\x91\xb3\xd6sP*\x1e\x0cF\xf3\xf9\xb9\
\x00\x80\x8d\x8dM\x00\x1e\xac\xad\xbd\xfb\xde\xb3\xaf?\x18\xcd\xa6k\xa3\xc9p\
:\xce\xf7\xef\xad\x0f\xf38\x8fs\xf2\xee\xe4\x8b\xf9Y\xb7\xfd\xf0\xe1\xa3\x17\
\x87\xcf9\xb8\x10B\xe0@\x84F\x9b$VMS#\x8a<O\x9f\x7f~\x10Iqp\xf8i\xd36\x00\
\xabF\x16\x91b\xa5\xd6\x06C\x12\xd23;\xe7\xac\xb5\x10|o\x07\x8c\x18\xc7q\x9a\
\xe4I\x9a\x9c\x9c\x1c\xf7\x11\xda\x00`\x0eA\xa8\xfc?\xfe\xf33\xdb\xd4\xbb\
\xb3i\x1a\xe7R\xca4\x167\xe7\xd7\xbf\xf9\xe4\xe2_?\xe8\x06\xc3\x89\xb5\xfa\
\xe5\xd1\xa1s&\x84\xc0\x00B\x08m\xdaEU\xe5y\xd9v\xad\xd1\xa6n\xaa\x93\xd3\
\xe3\xb6]Zg\xfbk\x08E\xacT$\xa5R\xb1\x07 !\\\xf0\xd6Y\xe7\xbd\x0b\x81H\x8d\
\xc7C\xa5\xb2\xd1x\x12\x82?>~)\x01 R\t\x006]\x97#Q\x14\xff\xec\xe7\x07O\x9f\
\xf3[\xdf~[ws`\xff\xf1\xc7O\x99\x86_\xbc8p\x1f\x7f`\xacA\x0e\xce\xf7\xdd&\
\xf4\x1d\xb7\xb5fY/\xa6\x93\x8d\xc3/\x0e766H``V*\x06`c\x0c\t""\x92\xf2\xa6^\
\x16y!\x85\x0c>\x18\xad\x11)I\xd24)\xbc\x0fR\xa0\xd1\xadw~\x95eM]\x93@)"k\
\xcch4\x1a\xad\x8d\x9a\xee\xe2\xa7\xff\xf4\x0f\xcc\xde9\x0f\x10dt)\x15\x94\
\xe5\xb0m[\xc4\xb2ik\xee\'\xc5\x10\x10\x11 \xdc\xde^q\xe0\xc9dZU\x8b\xeb\xeb\
\x8b<\xcf\xdb\xb6\x95R233{\x0e\xce;\xf0\x08\x08BR\xa4\xe40\x1ay\x1f\x98\x11\
\t&\xe3i\xac\xd4\xc5|\x9e\xe7\xf9\x8aP\x9c(k\x8c\x0f\x0e\x9cXTuQ\xe4M\xab\
\x19\xbc\x14$\x88\xf2\xbc\xb0\xd6,\xeb\x1aS!\xa4\\VU\x96\xe5]\xd7y\xef{\xf7\
\xeb_\xdb\xae\xf6~\xadm\xeb\xbe\xde\x85\x10\xba\xae\xeb\x8d\x94\x88\x04\t$\
\xb2\xc6\xa5iV\x96C\xad5\x00\x16E\xa1T\x8cH]\xdb\x12\n)\xc5\x8aP\xd7uB\x08B\
\xa9M\xc7\xcc\x1c\x98\x04\xc6I*\x10\x99\x99\x84`\xcbB\nff@\x19ERF!4\xbd_\xf7\
\xe8\xa76mZ\xe7L?3\xf5\xd3\x9cs\xce;\xdfu]\x92$\xb1T$\x84\x942xH\xd3<\x04\
\xb6\xc69\xeb\xa5\x90DX\x14E\x9c\xa8\x95\x0f\x8dF\xc3z\xd9H)B\x08HD$\x82\x07\
\xef\xac\xf3\xcc\xc0\xd5\xb2\x8a"%\x04uM+\xa3\xc8\x18c\x8cf\xe6\xbe\xe8R\xdf\
G"2\x07k\xf5\xda\xda\x94Hh\xdd\t!V\xcf\x02\x82\xef\x8bq\x9e\xe7\x84\x84\x84D\
\x14<\xe7E\xee\xacs\xceh\xa3U\x9cT\x8b\xdb\xdb\xc5\xcd\xe9\xd9\xa9\x00\x00\
\xa5\xe2(\x92]\xd7\xaaXYk;\xdd\x12\x81\x94\x12\t\x9d\x0b\xb1\x8a\xb3<\xaf\
\x97u`\xee\xa7tk\xad1\xfa\xae\xf9\xea\xb5\xd23\xd3\xba\xeb\xba\xc6{\x7f7\xd8\
[k\xfbo\xb3,\x95Q\x84\x88\xd6\x9ar0\xa8\x16\x0b\xeb\xac6\x86\x88\x8cn\xdb\
\xae5\xd6\\\\\\\xc0+\xbc\xc2\xff\x11\xaf\x9eS\x7f\x19\xfe\xdf\x11z\x85/\xc3\
\x7f\x03\xc2\x84=\xd0H\x1a\xe7\x02\x00\x00\x00\x00IEND\xaeB`\x82' 

def getICON_48Bitmap():
    return BitmapFromImage(getICON_48Image())

def getICON_48Image():
    stream = cStringIO.StringIO(getICON_48Data())
    return ImageFromStream(stream)

index.append('ICON_48')
catalog['ICON_48'] = ImageClass()
catalog['ICON_48'].GetData = getICON_48Data
catalog['ICON_48'].GetImage = getICON_48Image
catalog['ICON_48'].GetBitmap = getICON_48Bitmap


