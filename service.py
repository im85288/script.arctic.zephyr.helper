#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import xbmc
import xbmcaddon


__settings__ = xbmcaddon.Addon(id='script.arctic.zephyr.helper')
__cwd__ = __settings__.getAddonInfo('path')
__addonversion__ = __settings__.getAddonInfo('version')
BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )
sys.path.append(BASE_RESOURCE_PATH)

from LibraryMonitor import LibraryMonitor
from LibraryMonitor import Kodi_Monitor
from BackgroundsUpdater import BackgroundsUpdater

class Main:
    
    KodiMonitor = Kodi_Monitor()
    
    def __init__(self):
                   
        #start the extra threads
        libraryMonitor = LibraryMonitor()
        libraryMonitor.start()
        
        backgroundsUpdater = BackgroundsUpdater()
        backgroundsUpdater.start()
        
        while not self.KodiMonitor.abortRequested():
                     
            if self.KodiMonitor.waitForAbort(1):
                # Abort was requested while waiting. We should exit
                xbmc.log('Arctic Zephyr Script --> shutdown requested !')         
        else:
            #stop the extra threads
            libraryMonitor.stop()

xbmc.log('arctic zephyr helper version %s started' % __addonversion__)
Main()
xbmc.log('arctic zephyr helper version %s stopped' % __addonversion__)
