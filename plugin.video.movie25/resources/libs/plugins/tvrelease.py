import urllib, urllib2, re, string, urlparse, sys,   os
import xbmc, xbmcgui, xbmcaddon, xbmcplugin, HTMLParser
from resources.libs import main
from t0mm0.common.addon import Addon

addon_id = 'plugin.video.movie25'
selfAddon = xbmcaddon.Addon(id=addon_id)
addon = Addon(addon_id, sys.argv)

    
art = main.art
error_logo = art+'/bigx.png'

try:
    import urllib, urllib2, re, string, urlparse, sys, os
    
    from t0mm0.common.net import Net
    from metahandler import metahandlers
    from sqlite3 import dbapi2 as database
    from universal import playbackengine, watchhistory
    import urlresolver
except Exception, e:
    addon.log_error(str(e))
    addon.show_small_popup('MashUP: Tv-Release','Failed To Import Modules', 5000, error_logo)
    addon.show_ok_dialog(['Failed To Import Modules','Please Post Logfile In MashUP Forum @','http://www.xbmchub.com'],
                          'MashUP: TV-Release')
net = Net()
BASEURL = 'http://www.tv-release.net/'
wh = watchhistory.WatchHistory(addon_id)

def MAINMENU():
    main.addDir('TV 480',               BASEURL+'category/tvshows/tv480p/',       1001,art+'/TV480.png')
    main.addDir('TV 720',               BASEURL+'category/tvshows/tv720p/',       1001,art+'/TV720.png')
    main.addDir('TV MP4',               BASEURL+'category/tvshows/tvmp4/',        1001,art+'/TVmp4.png')
    main.addDir('TV Xvid',              BASEURL+'category/tvshows/tvxvid/',       1001,art+'/TVxvid.png')
    main.addDir('TV Packs',             BASEURL+'category/tvshows/tvpack/',       1001,art+'/TVpacks.png')
    main.addDir('TV Foreign',           BASEURL+'category/tvshows/tv-foreign/',   1001,art+'/TVforeign.png')
    main.addDir('Movies 480',           BASEURL+'category/movies/movies480p/',    1001,art+'/Movies480.png')
    main.addDir('Movies 720',           BASEURL+'category/movies/movies720p/',    1001,art+'/Movies720.png')
    main.addDir('Movies Xvid',          BASEURL+'category/movies/moviesxvid/',    1001,art+'/Moviesxvid.png')
    main.addDir('Movies Foreign',       BASEURL+'category/movies/moviesforeign/', 1001,art+'/Moviesforeign.png')
    main.addDir('Search Tv-Release',    BASEURL+'?s=',                            1001,art+'/tvrsearch1.png')#change mode number
    main.addSpecial('Resolver Settings',BASEURL,                                  1004,art+'/tvrresolver.png')
    main.VIEWSB()

def INDEX(url):
    types = []
    if '/tvshows/' in url:
        types = 'tv'
    elif '/movies/' in url:
        types = 'movie'
    html = GETHTML(url)
    if html == None:
        return
    pattern = 'text-align:left;">\n<a href="(.+?)"><b><font size="\dpx">(.+?)</font>'
    r = re.findall(pattern, html, re.I|re.M|re.DOTALL)
    dialogWait = xbmcgui.DialogProgress()
    ret = dialogWait.create('Please wait until list is cached.')
    totalLinks = len(r)
    loadedLinks = 0
    remaining_display = 'Media loaded :: [B]'+str(loadedLinks)+' / '+str(totalLinks)+'[/B].'
    dialogWait.update(0,'[B]Will load instantly from now on[/B]',remaining_display)
    for url, name in r:
        if re.findall('\ss\d+e\d+\s', name, re.I|re.DOTALL):
            r = re.findall('(.+?)\ss(\d+)e(\d+)\s', name, re.I)
            for name, season, episode in r:
                name = name+' Season '+season+' Episode '+episode+' ('+season+'x'+episode+')'
        elif re.findall('\s\d{4}\s\d{2}\s\d{2}\s', name):
            r = re.findall('(.+?)\s(\d{4})\s(\d{2})\s(\d{2})\s',name)
            for name, year, month, day in r:
                name = name+' '+year+' '+month+' '+day
        elif re.findall('\d+p\s', name):
            r = re.findall('(.+?)\s\d+p\s', name)
            for name in r:
                pass
        elif re.findall('\shdtv\sx', name, re.I):
            r = re.findall('(.+?)\shdtv\sx',name, re.I)
            for name in r:
                pass
        if types == 'tv':
            url = url+'+'+types
            main.addDirTE(name,url,1003,'','','','','','')
        elif types == 'movie':
            if re.findall('\s\d+\s',name):
                r = name.rpartition('\s\d{4}\s')
                url = url+'+'+types
            main.addDirM(name,url,1003,'','','','','','')
        loadedLinks = loadedLinks + 1
        percent = (loadedLinks * 100)/totalLinks
        remaining_display = 'Media loaded :: [B]'+str(loadedLinks)+' / '+str(totalLinks)+'[/B].'
        dialogWait.update(percent,'[B]Will load instantly from now on[/B]',remaining_display)
        if (dialogWait.iscanceled()):
            return False
    dialogWait.close()
    del dialogWait
    if '<!-- Zamango Pagebar 1.3 -->' in html:
        r = re.findall('<span class=\'zmg_pn_current\'>(\d+)</span>\n<span class=\'zmg_pn_standar\'><a href=\'(http://tv-release.net/category/.+?/\d+)\' title=\'Page \d+ of (\d+)\'>\d+</a>',html, re.I|re.DOTALL|re.M)
        for current, url, total in r:
            name = '[COLOR green]Page '+current+' of '+total+', Next Page >>>[/COLOR]'
            main.addDir(name, url, 1001, art+'/nextpage.png')
            url = url+':'+total
            name = '[COLOR green]Goto Page[/COLOR]'
            main.addDir(name, url, 1002, art+'/gotopagetr.png')
    main.VIEWS()

def LISTHOSTERS(name,url):
    html = main.OPENURL(url)
    if html == None: return
    main.addLink("[COLOR red]For Download Options, Bring up Context Menu Over Selected Link.[/COLOR]",'','')
    r = re.findall(r'class="td_cols"><a target=\'_blank\'.+?href=\'(.+?)\'>',html, re.M|re.DOTALL)
    sources = []
    for url in r:
        media = urlresolver.HostedMediaFile(url=url)
        sources.append(media)
    sources = urlresolver.filter_source_list(sources)
    r = re.findall(r'\'url\': \'(.+?)\', \'host\': \'(.+?)\'', str(sources), re.M)
    for url, host in r:
        r = re.findall(r'(.+?)\.',host)
        if 'www.real-debrid.com' in host:
            host = re.findall(r'//(.+?)/', url)
            host = host[0].replace('www.','')
            host = host.rpartition('.')
            host = host[0]
        else:
            host = r[0]
        main.addDown2(name+"[COLOR blue] :"+host.upper()+"[/COLOR]",url,1005,art+'/hosts/'+host+'.png',art+'/hosts/'+host+'.png')

                
def GOTOP(url):
    default = url
    r = url.rpartition(':')
    url = re.findall('(.+page\/)\d+',r[0])
    url = url[0]
    total = r[2]
    keyboard = xbmcgui.Dialog().numeric(0, '[B][I]Goto Page Number[/B][/I]')
    if keyboard > total or keyboard == '0':
        addon.show_ok_dialog(['Please Do Not Enter a Page Number bigger than',''+total+', Enter A Number Between 1 and '+total+'',
                              ''], 'MashUP: TV-Release')
        GOTOP(default)
    url = url+keyboard
    INDEX(url)
        
        
def PLAYMEDIA(name,url):
    r = url.rpartition('+')
    url = r[0]
    types = r[2]
    ok = True
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    r = re.findall(r'(.+?)\[COLOR', name)
    name = r[0]
    r=re.findall('Season(.+?)Episode([^<]+)',name)
    if r:
        infoLabels =main.GETMETAEpiT(name,'','')
        video_type='episode'
        season=infoLabels['season']
        episode=infoLabels['episode']
    else:
        infoLabels =main.GETMETAT(name,'','','')
        video_type='movie'
        season=''
        episode=''
    img=infoLabels['cover_url']
    fanart =infoLabels['backdrop_url']
    imdb_id=infoLabels['imdb_id']
    infolabels = { 'supports_meta' : 'true', 'video_type':video_type, 'name':str(infoLabels['title']), 'imdb_id':str(infoLabels['imdb_id']), 'season':str(season), 'episode':str(episode), 'year':str(infoLabels['year']) }
    source = urlresolver.HostedMediaFile(url)
    try:
        if source:
            xbmc.executebuiltin("XBMC.Notification(Please Wait!,Resolving Link,3000)")
            stream_url = source.resolve()
        else:
            stream_url = False
            return
                
        infoL={'Title': infoLabels['title'], 'Plot': infoLabels['plot'], 'Genre': infoLabels['genre']}
        # play with bookmark
        player = playbackengine.PlayWithoutQueueSupport(resolved_url=stream_url, addon_id=addon_id, video_type=video_type, title=str(infoLabels['title']),season=str(season), episode=str(episode), year=str(infoLabels['year']),img=img,infolabels=infoL, watchedCallbackwithParams=main.WatchedCallbackwithParams,imdb_id=imdb_id)
        #WatchHistory
        if selfAddon.getSetting("whistory") == "true":
            wh.add_item(hname+' '+'[COLOR green]iWatchonline[/COLOR]', sys.argv[0]+sys.argv[2], infolabels=infolabels, img=str(img), fanart=str(fanart), is_folder=False)
        player.KeepAlive()
        return ok
    except:
        return ok



    
    

def GETHTML(url):
    try:
        h = net.http_GET(url).content
        h=h.encode("ascii", "ignore")
        if '<h2>Under Maintenance</h2>' in h:
            addon.show_ok_dialog(['[COLOR green][B]TV-Release is Down For Maintenance,[/COLOR][/B]',
                                  '[COLOR green][B]Please Try Again Later[/COLOR][/B]',''],'MashUP: TV-Release')
            return MAINMENU()
        return h.encode("utf-8")
    except urllib2.URLError, e:
        addon.show_small_popup('MashUP: Tv-Release','TV-Release Web Site Failed To Respond, Check Log For Details', 9000, error_logo)
        addon.log_notice(str(e))
        return MAINMENU()
    
def GETMETA(name,types):
    type = types


