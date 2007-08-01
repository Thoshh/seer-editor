#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#Preferences

#LongLineCol from Chris McDonough
#Changed "doc.longlinecol" to "doc.long.line.col"

import sPreferences
import re

def  GetPrefValue(preflabel, text):
    restart = re.compile('^<' + preflabel + '>', re.M)
    reend = re.compile('</' + preflabel + '>$', re.M)
    start = restart.search(text)
    end = reend.search(text)

    if start is None or end is None:
        return None

    return text[start.end():end.start()]

def ConvertRawPreference(preference, type, default):
    if type == 0:
        if preference:
            return preference
        else:
            return default
    elif type == 1:
        try:
            return int(preference)
        except:
            return 0
    elif type == 2:
        return preference

def ExtractPreferenceFromText(text, pref):
    try:
        start = text.index("<" + pref + ">") + len(pref) + 2
        end = text.index("</" + pref + ">")

        return text[start:end]
    except:
        return ""

def ReadPreferences(prefs, prefsfile):
    #Handle exceptions in parent function.
    #sets prefs for parent frame.
    #Use GetPrefFromText(oldpref, text, prefstring) for string prefs
    #Use GetPrefFromText(oldpref, text, prefstring, True) for int prefs
    #Use ExtractPreferenceFromText(text, prefstring) for prefs where and empty
    #string is a valid value.

    fin = open(prefsfile, 'r')
    text = fin.read()
    fin.close()

    PreferencesDictionary = sPreferences.GetPreferencesDictionary()

    for Entry in PreferencesDictionary:
        for Preference in PreferencesDictionary[Entry]:
            value = GetPrefValue(Preference[1], text)
            if value is not None:
                prefs[Preference[0]] = ConvertRawPreference(value, Preference[2], prefs[Preference[0]])

def WritePreferences(prefs, prefsfile):
    fin = open(prefsfile, 'w')

    PreferencesDictionary = sPreferences.GetPreferencesDictionary()

    for Entry in PreferencesDictionary:
        for Preference in PreferencesDictionary[Entry]:
            if Preference[2] == 1:
                fin.write('<' + Preference[1] + '>' + str(prefs[Preference[0]]) + '</' + Preference[1] + '>\n')
            else:
                fin.write('<' + Preference[1] + '>' + prefs[Preference[0]] + '</' + Preference[1] + '>\n')
    fin.close()


#*****************************
#Old Functions (Still Used In Plugins)

def GetPreference(pref, prefsfile):
    #Handle exceptions in parent function.
    fin = open(prefsfile, 'r')
    text = fin.read()
    fin.close()

    #Test File:
    if text.find("seer") < 0:
        return -1

    return ExtractPreferenceFromText(text, pref)

def GetPrefFromText(oldvalue, text, targetpref, integer = False):
    if integer:
        pref = ExtractPreferenceFromText(text, targetpref)
        if pref:
            return SafeInt(pref)
    else:
        pref = ExtractPreferenceFromText(text, targetpref)
        if pref:
            return pref
    return oldvalue

def SafeInt(string):
    if string:
        try:
            return int(string)
        except:
            return 0
    return 0