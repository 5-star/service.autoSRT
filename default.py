#!/usr/bin/python
import os
import sys
import xbmc
import xbmcaddon
import xbmcvfs

__addon__ = xbmcaddon.Addon()
__author__ = __addon__.getAddonInfo('author')
__scriptid__ = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__cwd__ = __addon__.getAddonInfo('path')
__version__ = __addon__.getAddonInfo('version')
__language__ = __addon__.getLocalizedString
debug = __addon__.getSetting("debug")
__cwd__ = xbmcvfs.translatePath(__addon__.getAddonInfo('path'))
__profile__ = xbmcvfs.translatePath(__addon__.getAddonInfo('profile'))
__resource__ = xbmcvfs.translatePath(os.path.join(__cwd__, 'resources'))

__settings__ = xbmcaddon.Addon("service.autoSRT")

ignore_words = (__settings__.getSetting('ignore_words').split(','))
ExcludeTime = int((__settings__.getSetting('ExcludeTime')))*60
ExcludeExt1 = (__settings__.getSetting('ExcludeExt1'))
ExcludeExt2 = (__settings__.getSetting('ExcludeExt2'))
ExcludeExt3 = (__settings__.getSetting('ExcludeExt3'))
ExcludeExt4 = (__settings__.getSetting('ExcludeExt4'))
ExcludeExt5 = (__settings__.getSetting('ExcludeExt5'))

sys.path.append(__resource__)


player_monitor = xbmc.Monitor()


def Debug(msg, force = False):
    if(debug == "true" or force):
        xbmc.log("#####[AutoSRT]##### " + msg,3)

Debug("Loading '%s' version '%s'" % (__scriptname__, __version__))

# helper function to get string type from settings
def getSetting(setting):
    return __addon__.getSetting(setting).strip()

# helper function to get bool type from settings
def getSettingAsBool(setting):
    return getSetting(setting).lower() == "true"

# check exclusion settings for filename passed as argument
def isExcluded(movieFullPath):
    if not movieFullPath:
        return False

    movieFile = movieFullPath.rsplit(".", 1)[0]
    if xbmcvfs.exists(movieFile + ExcludeExt1):
        return False
    if xbmcvfs.exists(movieFile + ExcludeExt2):
        return False
    if xbmcvfs.exists(movieFile + ExcludeExt3):
        return False
    if xbmcvfs.exists(movieFile + ExcludeExt4):
        return False
    if xbmcvfs.exists(movieFile + ExcludeExt5):
        return False
	
    Debug("isExcluded(): Checking exclusion settings for '%s'." % movieFullPath, True)

    if (movieFullPath.find("pvr://") > -1) and getSettingAsBool('ExcludeLiveTV'):
        Debug("isExcluded(): Video is playing via Live TV, which is currently set as excluded location.")
        return False

    if (movieFullPath.find("http://") > -1) and getSettingAsBool('ExcludeHTTP'):
        Debug("isExcluded(): Video is playing via HTTP source, which is currently set as excluded location.")
        return False

    ExcludePath = getSetting('ExcludePath')
    if ExcludePath and getSettingAsBool('ExcludePathOption'):
        if (movieFullPath.find(ExcludePath) > -1):
            Debug("isExcluded(): Video is playing from '%s', which is currently set as excluded path 1." % ExcludePath)
            return False

    ExcludePath2 = getSetting('ExcludePath2')
    if ExcludePath2 and getSettingAsBool('ExcludePathOption2'):
        if (movieFullPath.find(ExcludePath2) > -1):
            Debug("isExcluded(): Video is playing from '%s', which is currently set as excluded path 2." % ExcludePath2)
            return False

    ExcludePath3 = getSetting('ExcludePath3')
    if ExcludePath3 and getSettingAsBool('ExcludePathOption3'):
        if (movieFullPath.find(ExcludePath3) > -1):
            Debug("isExcluded(): Video is playing from '%s', which is currently set as excluded path 3." % ExcludePath3)
            return False

    ExcludePath4 = getSetting('ExcludePath4')
    if ExcludePath4 and getSettingAsBool('ExcludePathOption4'):
        if (movieFullPath.find(ExcludePath4) > -1):
            Debug("isExcluded(): Video is playing from '%s', which is currently set as excluded path 4." % ExcludePath4)
            return False

    ExcludePath5 = getSetting('ExcludePath5')
    if ExcludePath5 and getSettingAsBool('ExcludePathOption5'):
        if (movieFullPath.find(ExcludePath5) > -1):
            Debug("isExcluded(): Video is playing from '%s', which is currently set as excluded path 5." % ExcludePath5)
            return False

    return True


class KodiPlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        Debug("Initalized")
        self.run = True

    def onPlayBackStopped(self):
        Debug("Stopped")
        self.run = True

    def onPlayBackEnded(self):
        Debug("Ended")
        self.run = True

    def onPlayBackStarted(self):
        Debug("Started")
        try:
            xbmc.sleep(3000)
            if self.getSubtitles(): self.run = false
        except: pass
        if self.run:
            movieFullPath = xbmc.Player().getPlayingFile()
            Debug("movieFullPath '%s'" % movieFullPath)
            xbmc.sleep(1000)
            availableLangs = xbmc.Player().getAvailableSubtitleStreams()
            Debug("availableLangs '%s'" % availableLangs)
            totalTime = xbmc.Player().getTotalTime()
            Debug("totalTime '%s'" % totalTime)
            videoclip = False
            if getSettingAsBool('ExcludeVideoClip'):
                videoType = xbmc.Player().getVideoInfoTag().getMediaType()
                Debug("videoType '%s'" % str(videoType))
                if videoType == 'musicvideo':  videoclip = True
            if (xbmc.Player().isPlayingVideo() and totalTime > ExcludeTime and (not videoclip) and all(movieFullPath.find (v) <= -1 for v in ignore_words) and (isExcluded(movieFullPath)) ):
                self.run = False
                xbmc.sleep(1000)
                Debug('Started: AutoSearching for Subs')
                xbmc.executebuiltin('ActivateWindow(SubtitleSearch)')
                Debug('Started: AutoSearch completed')
            else:
                Debug('Started: Subs found or Excluded')
                self.run = False

class KodiRunner:
    player = KodiPlayer()

    while not player_monitor.abortRequested():
        player_monitor.waitForAbort(1)

    del player

