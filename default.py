import xbmcaddon
import xbmcplugin
import os

__settings__ = xbmcaddon.Addon(id='script.arctic.zephyr.helper')
__cwd__ = __settings__.getAddonInfo('path')
BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )
sys.path.append(BASE_RESOURCE_PATH)
import MainModule
#script init
action = ""
argument1 = ""
argument2 = ""
argument3 = ""

# get arguments
try:
    action = str(sys.argv[1])
except: 
    pass

try:
    argument1 = str(sys.argv[2])
except:
    pass

try:
    argument2 = str(sys.argv[3])
except:
    pass

try:
    argument3 = str(sys.argv[4])
except: 
    pass  
    
if action == "COLORPICKER":
    from ColorPicker import ColorPicker
    colorPicker = ColorPicker("ColorPicker.xml", __cwd__, "default", "1080i")
    colorPicker.skinString = argument1
    colorPicker.doModal()
    del colorPicker
elif action == "SETVIEW":
    MainModule.setView()
elif action == "ENABLEVIEWS":
    MainModule.enableViews()


    
    