#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

def convertStyleToColorArray(StyleString):
    ''' Returns a two arrays, one for the foreground, and one for the background '''
    #Returns the Red, Green Blue Values for a string formatted: #00FF33
    return (convertColorPropertyToColorArray(getStyleProperty("fore", StyleString)), convertColorPropertyToColorArray(getStyleProperty("back", StyleString)))

def convertColorPropertyToColorArray(ColorString):
    #Returns the Red, Green Blue Values for a string formatted: #00FF33
    return int(ColorString[1:3], 16), int(ColorString[3:5], 16), int(ColorString[5:7], 16)

def convertStyleStringToWXFontArray(StyleString):
    #This returns an array to be used as arguments in the wx.Font constructor,
    #Face, Size, Underline, Bold, Italic

    t = getStyleProperty("size", StyleString)
    size = int(t)

    t = getStyleProperty("italic", StyleString)
    italic = (len(t) > 0)

    t = getStyleProperty("bold", StyleString)
    bold = (len(t) > 0)

    t = getStyleProperty("underline", StyleString)
    underline = (len(t) > 0)

    t = getStyleProperty("face", StyleString)
    face = t

    return face, size, underline, bold, italic


def getStyleProperty(Property, StyleString):

    if (Property == "bold") or (Property == "italic") or (Property == "underline"):
        if StyleString.find(Property) != -1:
            return Property
        else:
            return ""

    i = StyleString.find(Property)
    if i != -1:
        lindex = i + len(Property) + 1
        rindex = StyleString[lindex:].find(",")
        if rindex == -1:
            return StyleString[lindex:]
        rindex = rindex + lindex
        return StyleString[lindex:rindex]
    return ""

def setStyleProperty(Property, StyleString, newValue):

    i = StyleString.find(Property)
    if Property == "bold":
        if i != -1:
            return StyleString[0:i] + "," + newValue + StyleString[(i + len(Property)):]
        else:
            prop = getStyleProperty("face", StyleString)
            i = StyleString.find(prop) + len(prop)
            return StyleString[0:i] + "," + newValue + StyleString[i:]
    if Property == "italic":
        if i != -1:
            return StyleString[0:i] + "," + newValue + StyleString[(i + len(Property)):]
        else:
            prop = getStyleProperty("face", StyleString)
            i = StyleString.find(prop) + len(prop)
            return StyleString[0:i] + "," + newValue + StyleString[i:]
    if Property == "underline":
        if i != -1:
            return StyleString[0:i] + "," + newValue + StyleString[(i + len(Property)):]
        else:
            prop = getStyleProperty("face", StyleString)
            i = StyleString.find(prop) + len(prop)
            return StyleString[0:i] + "," + newValue + StyleString[i:]

    if i != -1:
        lindex = i + len(Property) + 1
        rindex = StyleString[lindex:].find(",")
        if rindex == -1:
            return StyleString[0:lindex] + newValue
        rindex = rindex + lindex
        return StyleString[0:lindex] + newValue + StyleString[rindex:]
    return ""
