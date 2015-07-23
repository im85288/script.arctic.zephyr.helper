#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import xbmc
import xbmcplugin
import xbmcaddon
import xbmcgui
import threading
import xbmcvfs
import random
import xml.etree.ElementTree as etree
import base64
import json
from datetime import datetime
import Utils as utils


class LibraryMonitor(threading.Thread):
    
    event = None
    exit = False
    liPath = None
    liPathLast = None
    unwatched = 1
    delayedTaskInterval = 1800
    moviesetCache = {}
    extraFanartcache = {}
    allStudioLogos = list()
    allColourStudioLogos = list()
    studioLogosPath = None
    studioColourLogosPath = None
    LastStudioImagesPath = None
    LastColourStudioImagesPath = None
    
    win = None
    addon = None
    addondir = None
    
    def __init__(self, *args):
        
        self.win = xbmcgui.Window( 10000 )
        self.addon = xbmcaddon.Addon(id='script.arctic.zephyr.helper')
        self.addondir = xbmc.translatePath(self.addon.getAddonInfo('profile'))
        
        utils.logMsg("LibraryMonitor"," - started")
        self.event =  threading.Event()
        threading.Thread.__init__(self, *args)    
    
    def stop(self):
        utils.logMsg("LibraryMonitor"," - stop called")
        self.exit = True
        self.event.set()

    def run(self):

        lastListItemLabel = None

        while (xbmc.abortRequested == False and self.exit != True):

            #do some background stuff every 30 minutes
            if (xbmc.getCondVisibility("!Window.IsActive(videolibrary) + !Window.IsActive(fullscreenvideo)")):
                if (self.delayedTaskInterval >= 1800):
                     self.getStudioLogos()
                     self.getColourStudioLogos()
                     self.delayedTaskInterval = 0
            
            # monitor listitem props when videolibrary is active
            if (xbmc.getCondVisibility("[Window.IsActive(videolibrary) | Window.IsActive(movieinformation)] + !Window.IsActive(fullscreenvideo)")):
                
                self.liPath = xbmc.getInfoLabel("ListItem.Path")
                liLabel = xbmc.getInfoLabel("ListItem.Label")
                if ((liLabel != lastListItemLabel) and xbmc.getCondVisibility("!Container.Scrolling")):
                    
                    self.liPathLast = self.liPath
                    lastListItemLabel = liLabel
                    
                    # update the listitem stuff
                    try:
                        self.checkExtraFanArt()
                        self.setStudioLogo()
                    except Exception as e:
                        utils.logMsg("Error", "ERROR in LibraryMonitor ! --> " + str(e), 0)
  
                else:
                    xbmc.sleep(50)
            else:
                xbmc.sleep(1000)
                self.delayedTaskInterval += 1

    def setStudioLogo(self):
            studio = xbmc.getInfoLabel('ListItem.Studio')
            studiologo = None

            #find logo if multiple found
            if "/" in studio:
                studios = studio.split(" / ")
                count = 0
                for item in studios:
                    if item in self.allStudioLogos:
                        studiologo = self.studioLogosPath + studios[count]
                        break
                    count += 1

            #find logo normal
            if studio in self.allStudioLogos:
                studiologo = self.studioLogosPath + studio
            else:
                #find logo by substituting characters
                studio = studio.replace(" (US)","")
                studio = studio.replace(" (UK)","")
                studio = studio.replace(" (CA)","")
                for logo in self.allStudioLogos:
                    if logo.lower() == studio.lower():
                        studiologo = self.studioLogosPath + logo

            if studiologo:
                self.win.setProperty("ListItemStudioLogo", studiologo + ".png")
            else:
                self.win.clearProperty("ListItemStudioLogo")

            studio = xbmc.getInfoLabel('ListItem.Studio')
            studiologo = None

            #find logo if multiple found
            if "/" in studio:
                studios = studio.split(" / ")
                count = 0
                for item in studios:
                    if item in self.allColourStudioLogos:
                         studiologo = self.studioColourLogosPath + studios[count]
                         break
                    count += 1

            #find logo normal
            if studio in self.allColourStudioLogos:
                studiologo = self.studioColourLogosPath + studio
            else:
                #find logo by substituting characters
                studio = studio.replace(" (US)","")
                studio = studio.replace(" (UK)","")
                studio = studio.replace(" (CA)","")
                for logo in self.allColourStudioLogos:
                     if logo.lower() == studio.lower():
                         studiologo = self.studioColourLogosPath + logo

                     if studiologo:
                         self.win.setProperty("ListItemColourStudioLogo", studiologo + ".png")
                     else:
                         self.win.clearProperty("ListItemColourStudioLogo")

    def getStudioLogos(self):
            #fill list with all studio logos
            StudioImagesCustompath = xbmc.getInfoLabel("Skin.String(StudioImagesCustompath)")
            if StudioImagesCustompath:
                path = StudioImagesCustompath
                if not (path.endswith("/") or path.endswith("\\")):
                    path = path + os.sep()
            else:
                if xbmc.getCondVisibility("Skin.HasSetting(furniture.flags.colour)"):
                    path = "special://skin/extras/flags/colour/studios/"
                else:
                    path = "special://skin/extras/flags/studios/"

            if path != self.LastStudioImagesPath:
                self.LastStudioImagesPath = path
                allLogos = list()
                dirs, files = xbmcvfs.listdir(path)
                for file in files:
                    file = file.replace(".png","")
                    file = file.replace(".PNG","")
                    allLogos.append(file)

                self.studioLogosPath = path
                self.allStudioLogos = set(allLogos)

    def getColourStudioLogos(self):
                #fill list with all studio logos
                path = "special://skin/extras/flags/colour/studios/"
                if path != self.LastColourStudioImagesPath:
                    self.LastColourStudioImagesPath = path
                    allLogos = list()
                    dirs, files = xbmcvfs.listdir(path)
                    for file in files:
                        file = file.replace(".png","")
                        file = file.replace(".PNG","")
                        allLogos.append(file)

                    self.studioColourLogosPath = path
                    self.allColourStudioLogos = set(allLogos)
                                
    def checkExtraFanArt(self):
        
        lastPath = None
        efaPath = None
        efaFound = False
        liArt = None
        containerPath = xbmc.getInfoLabel("Container.FolderPath")
        
        if xbmc.getCondVisibility("Window.IsActive(movieinformation)"):
            return
        
        #get the item from cache first
        if self.extraFanartcache.has_key(self.liPath):
            if self.extraFanartcache[self.liPath] == "None":
                self.win.clearProperty("ExtraFanArtPath")
                return
            else:
                self.win.setProperty("ExtraFanArtPath",self.extraFanartcache[self.liPath])
                return
        
        if not xbmc.getCondVisibility("Skin.HasSetting(EnableExtraFanart) + [Window.IsActive(videolibrary) | Window.IsActive(movieinformation)] + !Container.Scrolling"):
            self.win.clearProperty("ExtraFanArtPath")
            return
        
        if (self.liPath != None and (xbmc.getCondVisibility("Container.Content(movies) | Container.Content(seasons) | Container.Content(episodes) | Container.Content(tvshows)")) and not "videodb:" in self.liPath):
                           
            if xbmc.getCondVisibility("Container.Content(episodes)"):
                liArt = xbmc.getInfoLabel("ListItem.Art(tvshow.fanart)")
            
            # do not set extra fanart for virtuals
            if (("plugin://" in self.liPath) or ("addon://" in self.liPath) or ("sources" in self.liPath) or ("plugin://" in containerPath) or ("sources://" in containerPath) or ("plugin://" in containerPath)):
                self.win.clearProperty("ExtraFanArtPath")
                self.extraFanartcache[self.liPath] = "None"
                lastPath = None
            else:

                if xbmcvfs.exists(self.liPath + "extrafanart/"):
                    efaPath = self.liPath + "extrafanart/"
                else:
                    pPath = self.liPath.rpartition("/")[0]
                    pPath = pPath.rpartition("/")[0]
                    if xbmcvfs.exists(pPath + "/extrafanart/"):
                        efaPath = pPath + "/extrafanart/"
                        
                if xbmcvfs.exists(efaPath):
                    dirs, files = xbmcvfs.listdir(efaPath)
                    if files.count > 1:
                        efaFound = True
                        
                if (efaPath != None and efaFound == True):
                    if lastPath != efaPath:
                        self.win.setProperty("ExtraFanArtPath",efaPath)
                        self.extraFanartcache[self.liPath] = efaPath
                        lastPath = efaPath       
                else:
                    self.win.clearProperty("ExtraFanArtPath")
                    self.extraFanartcache[self.liPath] = "None"
                    lastPath = None
        else:
            self.win.clearProperty("ExtraFanArtPath")
            lastPath = None

class Kodi_Monitor(xbmc.Monitor):
    
    WINDOW = xbmcgui.Window(10000)

    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)

    def onDatabaseUpdated(self, database):
        pass                                         