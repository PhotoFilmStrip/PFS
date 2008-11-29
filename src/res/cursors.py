
import wx

DATA    = [[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], 
           [2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 2, 0, 0, 0, 0],
           [2, 2, 2, 2, 2, 2, 2, 2, 0, 1, 0, 2, 0, 1, 1, 0],
           [2, 2, 2, 2, 2, 2, 2, 0, 1, 1, 0, 2, 0, 1, 1, 0],
           [2, 2, 2, 2, 2, 2, 0, 1, 1, 1, 0, 2, 0, 1, 1, 0],
           [2, 2, 2, 2, 2, 0, 1, 1, 1, 1, 0, 2, 0, 1, 1, 0],
           [2, 2, 2, 2, 0, 1, 1, 1, 1, 1, 0, 2, 0, 1, 1, 0],
           [2, 2, 2, 0, 1, 1, 1, 1, 1, 1, 0, 2, 0, 1, 1, 0],
           [2, 2, 0, 1, 1, 1, 1, 1, 1, 1, 0, 2, 0, 1, 1, 0],
           [2, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 2, 0, 1, 1, 0],
           [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1, 1, 0],
           [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1, 1, 0],
           [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
           [2, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
           [2, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
           [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

__CURSORS = {}

def __MakeCursor(data):
    img = wx.EmptyImage(16, 16)
    img.SetMaskColour(255, 0, 0)
    for px in range(len(data)):
        for py in range(len(data[px])):
            val = data[px][py]
            if val == 2:
                img.SetRGB(px, py, 255, 0, 0)
            elif val == 1:
                img.SetRGB(px, py, 0, 0, 0)
            elif val == 0:
                img.SetRGB(px, py, 255, 255, 255)
    img.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 8)
    img.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 8)
    return wx.CursorFromImage(img)

def GetNW():
    if __CURSORS.has_key('NW'):
        return __CURSORS['NW']
    
    result = []
    for line in DATA:
        tmp = []
        for value in line:
            tmp.insert(0, value)
        result.insert(0, tmp)
    cursor = __MakeCursor(result)
    __CURSORS['NW'] = cursor
    return cursor

def GetSE():
    if __CURSORS.has_key('SE'):
        return __CURSORS['SE']
    
    cursor = __MakeCursor(DATA)
    __CURSORS['SE'] = cursor
    return cursor

def GetSW():
    if __CURSORS.has_key('SW'):
        return __CURSORS['SW']
    
    result = []
    for line in DATA:
        tmp = []
        for value in line:
            tmp.append(value)
        result.insert(0, tmp)
    cursor = __MakeCursor(result)
    __CURSORS['SW'] = cursor
    return cursor

def GetNE():
    if __CURSORS.has_key('NE'):
        return __CURSORS['NE']
    
    result = []
    for line in DATA:
        tmp = []
        for value in line:
            tmp.insert(0, value)
        result.append(tmp)
    cursor = __MakeCursor(result)
    __CURSORS['NE'] = cursor
    return cursor

