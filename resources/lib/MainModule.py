import xbmcplugin
import xbmcgui
import xbmc
import xbmcaddon
import shutil
import xbmcaddon
import xbmcvfs
import os, sys
import time
import urllib
import xml.etree.ElementTree as etree
from xml.dom.minidom import parse
import json
import random

from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.etree import ElementTree
from xml.dom import minidom
import xml.etree.cElementTree as ET

doDebugLog = False

win = xbmcgui.Window( 10000 )
addon = xbmcaddon.Addon(id='script.arctic.zephyr.helper')
addondir = xbmc.translatePath(addon.getAddonInfo('profile'))

__language__ = xbmc.getLocalizedString
__cwd__ = addon.getAddonInfo('path')

def enableViews():
    import Dialogs as dialogs
    
    allViews = []   
    views_file = xbmc.translatePath( 'special://skin/extras/views.xml' ).decode("utf-8")
    if xbmcvfs.exists( views_file ):
        doc = parse( views_file )
        listing = doc.documentElement.getElementsByTagName( 'view' )
        for count, view in enumerate(listing):
            label = xbmc.getLocalizedString(int(view.attributes[ 'languageid' ].nodeValue))
            id = view.attributes[ 'value' ].nodeValue
            type = view.attributes[ 'type' ].nodeValue
            listitem = xbmcgui.ListItem(label=label)
            listitem.setProperty("id",id)
            if not xbmc.getCondVisibility("Skin.HasSetting(View.Disabled.%s)" %id):
                listitem.select(selected=True)
            allViews.append(listitem)
    
    w = dialogs.DialogSelectSmall( "DialogSelect.xml", __cwd__, listing=allViews, windowtitle=xbmc.getLocalizedString(31487),multiselect=True )
    w.doModal()
    
    selectedItems = w.result
    if selectedItems != -1:
        itemcount = len(allViews) -1
        while (itemcount != -1):
            viewid = allViews[itemcount].getProperty("id")
            if itemcount in selectedItems:
                #view is enabled
                xbmc.executebuiltin("Skin.Reset(View.Disabled.%s)" %viewid)
            else:
                #view is disabled
                xbmc.executebuiltin("Skin.SetBool(View.Disabled.%s)" %viewid)
            itemcount -= 1    
    del w        

def setForcedView(contenttype):
    currentView = xbmc.getInfoLabel("Skin.String(ForcedViews.%s)" %contenttype)
    selectedItem = selectView(contenttype, currentView, True)
    
    if selectedItem != -1 and selectedItem != None:
        xbmc.executebuiltin("Skin.SetString(ForcedViews.%s,%s)" %(contenttype, selectedItem))
    
def setView():
    #sets the selected viewmode for the container
    import Dialogs as dialogs
    
    #get current content type
    contenttype="other"
    if xbmc.getCondVisibility("Container.Content(episodes)"):
        contenttype = "episodes"
    elif xbmc.getCondVisibility("Container.Content(movies) + !substring(Container.FolderPath,setid=)"):
        contenttype = "movies"  
    elif xbmc.getCondVisibility("[Container.Content(sets) | StringCompare(Container.Folderpath,videodb://movies/sets/)] + !substring(Container.FolderPath,setid=)"):
        contenttype = "sets"
    elif xbmc.getCondVisibility("substring(Container.FolderPath,setid=)"):
        contenttype = "setmovies" 
    elif xbmc.getCondVisibility("Container.Content(tvshows)"):
        contenttype = "tvshows"
    elif xbmc.getCondVisibility("Container.Content(seasons)"):
        contenttype = "seasons"
    elif xbmc.getCondVisibility("Container.Content(musicvideos)"):
        contenttype = "musicvideos"
    elif xbmc.getCondVisibility("Container.Content(artists)"):
        contenttype = "artists"
    elif xbmc.getCondVisibility("Container.Content(songs)"):
        contenttype = "songs"
    elif xbmc.getCondVisibility("Container.Content(albums)"):
        contenttype = "albums"
    elif xbmc.getCondVisibility("Container.Content(songs)"):
        contenttype = "songs"
    elif xbmc.getCondVisibility("Window.IsActive(tvchannels) | Window.IsActive(radiochannels)"):
        contenttype = "tvchannels"
    elif xbmc.getCondVisibility("Window.IsActive(tvrecordings) | Window.IsActive(radiorecordings)"):
        contenttype = "tvrecordings"
    elif xbmc.getCondVisibility("Window.IsActive(programs) | Window.IsActive(addonbrowser)"):
        contenttype = "programs"
    elif xbmc.getCondVisibility("Window.IsActive(pictures)"):
        contenttype = "pictures"
    
    currentView = xbmc.getInfoLabel("Container.Viewmode")
    selectedItem = selectView(contenttype, currentView)
    currentForcedView = xbmc.getInfoLabel("Skin.String(ForcedViews.%s)" %contenttype)
    
    #also store forced view    
    if currentForcedView != "None":
        xbmc.executebuiltin("Skin.SetString(ForcedViews.%s,%s)" %(contenttype, selectedItem))
    
    #set view
    if selectedItem != -1 and selectedItem != None:
        xbmc.executebuiltin("Container.SetViewMode(%s)" %selectedItem)
  
    
def selectView(contenttype="other", currentView=None, displayNone=False):
    import Dialogs as dialogs
    currentViewSelectId = None

    allViews = []
    if displayNone:
        listitem = xbmcgui.ListItem(label="None")
        listitem.setProperty("id","None")
        allViews.append(listitem)
        
    views_file = xbmc.translatePath( 'special://skin/extras/views.xml' ).decode("utf-8")
    if xbmcvfs.exists( views_file ):
        doc = parse( views_file )
        listing = doc.documentElement.getElementsByTagName( 'view' )
        itemcount = 0
        for count, view in enumerate(listing):
            label = __language__(int(view.attributes[ 'languageid' ].nodeValue))
            id = view.attributes[ 'value' ].nodeValue
            type = view.attributes[ 'type' ].nodeValue
            if label.lower() == currentView.lower() or id == currentView:
                currentViewSelectId = itemcount
                if displayNone == True:
                    currentViewSelectId += 1
            if (type == "all" or contenttype in type):
                image = "special://skin/extras/viewthumbs/%s.jpg" %id
                listitem = xbmcgui.ListItem(label=label, iconImage=image)
                listitem.setProperty("id",id)
                listitem.setProperty("icon",image)
                allViews.append(listitem)
                itemcount +=1
    w = dialogs.DialogSelectBig( "BigDialogSelect.xml", __cwd__, listing=allViews, windowtitle="Select View",multiselect=False )
    w.autoFocusId = currentViewSelectId
    w.doModal()
    selectedItem = w.result
    del w
    if selectedItem != -1:
        id = allViews[selectedItem].getProperty("id")
        return id
    