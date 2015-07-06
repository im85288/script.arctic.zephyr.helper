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
from xml.dom.minidom import parse
import base64
import json

import Utils as utils


class BackgroundsUpdater(threading.Thread):
    
    event = None
    exit = False
    allBackgrounds = {}
    tempBlacklist = set()
    defBlacklist = set()
    lastPicturesPath = None
    smartShortcuts = {}
    cachePath = None
    SmartShortcutsCachePath = None
    win = None
    addondir = None
    
    def __init__(self, *args):
        
        self.win = xbmcgui.Window( 10000 )  
        addon = xbmcaddon.Addon(id='script.arctic.zephyr.helper')
        self.addondir = xbmc.translatePath(addon.getAddonInfo('profile'))
        
        self.SmartShortcutsCachePath = os.path.join(self.addondir,"smartshotcutscache.json")

        utils.logMsg("BackgroundsUpdater"," - started")
        self.event =  threading.Event()
        threading.Thread.__init__(self, *args)    
    
    def stop(self):
        utils.logMsg("BackgroundsUpdater"," - stop called")
        self.saveCacheToFile()
        self.exit = True
        self.event.set()

    def run(self):

        backgroundDelay = 30000
            
        #first run get backgrounds immediately from filebased cache and reset the cache in memory to populate all images from scratch
        try:
            self.getCacheFromFile()
            self.UpdateBackgrounds()
        except Exception as e:
            utils.logMsg("ERROR in BackgroundsUpdater ! --> " + str(e), 0)
        
        self.allBackgrounds = {}
        self.smartShortcuts = {}
         
        while (self.exit != True):
            
            if not xbmc.Player().isPlayingVideo(): 
                try:
                    self.UpdateBackgrounds()
                except Exception as e:
                    utils.logMsg("ERROR in UpdateBackgrounds ! --> " + str(e), 0)
            
            xbmc.sleep(backgroundDelay)
                               
    def saveCacheToFile(self):
        #safety check: does the config directory exist?
        if not xbmcvfs.exists(self.addondir + os.sep):
            xbmcvfs.mkdir(self.addondir)
        
        json.dump(self.smartShortcuts, open(self.SmartShortcutsCachePath,'w'))
        

    def getCacheFromFile(self):
        if xbmcvfs.exists(self.cachePath):
            with open(self.cachePath) as data_file:    
                data = json.load(data_file)
                
                self.defBlacklist = set(data["blacklist"])
                self.allBackgrounds = data
        
        if xbmcvfs.exists(self.SmartShortcutsCachePath):
            with open(self.SmartShortcutsCachePath) as data_file:    
                self.smartShortcuts = json.load(data_file)    
                
       
    def UpdateBackgrounds(self):
            
        #smart shortcuts --> netflix nodes
        if xbmc.getCondVisibility("System.HasAddon(plugin.video.netflixbmc)"):
            
            utils.logMsg("","Processing netflix nodes.... ")
            
            if self.smartShortcuts.has_key("netflix"):
                utils.logMsg("","get netflix entries from cache.... ")
                nodes = self.smartShortcuts["netflix"]
                for node in nodes:
                    key = node[0]
                    label = node[1]
                    path = node[2]
                    self.win.setProperty(key + ".title", label)
                    self.win.setProperty(key + ".path", path)
            else:
                utils.logMsg("","no cache - Get netflix entries from addon.... ")    
            
                #wait for max 5 seconds untill the plex nodes are available
                count = 0
                while (count < 20 and not self.win.getProperty("plexbmc.0.title")):
                    xbmc.sleep(250)
                    count += 1
                    
                totalNodes = 14
                nodes = []
                for i in range(totalNodes):
                    plextitle = self.win.getProperty("plexbmc.%s.title"%str(i))
                    if plextitle:
                        plexcontent = self.win.getProperty("plexbmc.%s.all"%str(i))
                        if not plexcontent:
                            plexcontent = self.win.getProperty("plexbmc.%s.path"%str(i))
                        plextype = self.win.getProperty("plexbmc.%s.type" %str(i))
                        key = "plexbmc.%s"%str(i)
                        nodes.append( (key, plextitle, plexcontent ) )
                    else:
                        break
                
                self.smartShortcuts["netflix"] = nodes