import urllib2
import urllib
import os.path
import json
import requests
from wox import Wox

kodi_host = "127.0.0.1"
kodi_port = "8080"

def post_data(url, post):
    url=url
    postdata = post
    # create the request object and set some headers
    req = urllib2.Request(url)
    req.add_header('Content-type','application/json')
    data = json.dumps(postdata)
    #print data
    # make the request and print the results
    res = urllib2.urlopen(req,data)
    return json.load(res)

def now_playing():
    play_info = post_data('http://' + kodi_host + ':' + kodi_port + '/jsonrpc',{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1})
    try:
        nplay = post_data('http://' + kodi_host + ':' + kodi_port + '/jsonrpc',{"jsonrpc": "2.0", "method": "Player.GetItem", "params": { "properties": ["title", "album", "artist", "season", "episode", "duration", "showtitle", "tvshowid", "thumbnail", "file", "fanart", "streamdetails"], "playerid": 1 }, "id": "VideoGetItem"})
        nplay.title = nplay["result"]["item"]["title"]
        results.append({
            "Title": nplay.title,
            "SubTitle": 'Currently playing video.',
            "IcoPath": icons_dir + "spell.png",
            "JsonRPCAction": {
                "method": "Wox.ChangeQuery",
                "parameters": ["ks tvshows", False],
                # hide the query wox or not
                "dontHideAfterAction": True
            }
        })
    except:
        pass


#title = results["result"]["movies"][i]["title"]
#subtext = results["result"]["movies"][i]["title"]
class Main(Wox):
    def request(self, url):
        if self.proxy and self.proxy.get("enabled") and self.proxy.get("server"):
            proxies = {
                "http": "http://{}:{}".format(self.proxy.get("server"), self.proxy.get("port")),
                "https": "http://{}:{}".format(self.proxy.get("server"), self.proxy.get("port"))}
            return requests.get(url, proxies=proxies)
        else:
            return requests.get(url)
    def context_menu(self, data):
        results = []
        results.append({
            "Title": 'Error: Could not connect to kodi!',
            "SubTitle": 'Please make sure Kodi is running and Web Server is on...',
            "IcoPath": icons_dir + "kodi_icon.png",
            "JsonRPCAction": {
                "method": "Wox.ChangeQuery",
                "parameters": ["kodi", False],
                # hide the query wox or not
                "dontHideAfterAction": True
            }
        })
        return results
    def start_movie(self, id):
        post_data('http://' + kodi_host + ':' + kodi_port + '/jsonrpc',{
         "jsonrpc": "2.0",
         "method": "Player.Open",
         "params": {
          "options": {
           "resume": 0
          },
          "item": {
           "movieid": id
          }
         },
         "id": 1
        })
    def start_tv(self, id):
        post_data('http://' + kodi_host + ':' + kodi_port + '/jsonrpc',{
         "jsonrpc": "2.0",
         "method": "Player.Open",
         "params": {
          "options": {
           "resume": 1
          },
          "item": {
           "episodeid": id
          }
         },
         "id": 1
        })
    def save_id(self, id):
        global global_tvshowid
        tvshowid = id
    def stop_kodi(self):
        post_data('http://' + kodi_host + ':' + kodi_port + '/jsonrpc',{"jsonrpc": "2.0", "method": "Player.Stop", "params": { "playerid": 1 }, "id": 1})
        post_data('http://' + kodi_host + ':' + kodi_port + '/jsonrpc',{"jsonrpc": "2.0", "method": "Player.Stop", "params": { "playerid": 0 }, "id": 1})
    def pause_kodi(self):
        post_data('http://' + kodi_host + ':' + kodi_port + '/jsonrpc',{"jsonrpc": "2.0", "method": "Player.PlayPause", "params": { "playerid": 1 }, "id": 1})
        post_data('http://' + kodi_host + ':' + kodi_port + '/jsonrpc',{"jsonrpc": "2.0", "method": "Player.PlayPause", "params": { "playerid": 0 }, "id": 1})
    def query(self, query):
        results = []
        icons_dir = './icons/'
        try:
            kodi_ping = post_data('http://' + kodi_host + ':' + kodi_port + '/jsonrpc',{"jsonrpc":"2.0","method":"JSONRPC.Ping","id":"1"})



            if query.startswith("movies"):
                shifted_query = query.replace("movies", "",1)
            elif query.startswith("tvshows"):
                shifted_query = query.replace("tvshows", "",1)
            if "stop" in query:
                results.append({
                    "Title": 'Stop Kodi',
                    "SubTitle": 'Stops any media playing on Kodi',
                    "JsonRPCAction":{
                      "method": "stop_kodi",
                      #you MUST pass parater as array
                      #hide the query wox or not
                      "dontHideAfterAction":True
                    }
                })
            if "pause" in query or "play" in query:
                results.append({
                    "Title": 'Play/Pause Kodi',
                    "SubTitle": 'Toggles pause on currently playing media.',
                    "JsonRPCAction":{
                      "method": "pause_kodi",
                      #you MUST pass parater as array
                      #hide the query wox or not
                      "dontHideAfterAction":True
                    }
                })
            if query.startswith("movies"):
                json.data = post_data('http://' + kodi_host + ':' + kodi_port + '/jsonrpc',{
                 "jsonrpc": "2.0",
                 "method": "VideoLibrary.GetMovies",
                 "id": "1484897668671",
                 "params": {
                  "properties": [
                   "title",
                   "plot",
                   "art",
                   "rating",
                   "year",
                   "thumbnail",
                   "tagline"
                  ],
                  "limits": {
                   "start": 0,
                   "end": 0
                  },
                  "sort": {
                   "method": "title",
                   "order": "ascending",
                  },
                  "filter": {
                   "operator": "contains",
                   "field": "title",
                   "value": shifted_query.strip()
                  }
                 }
                })
                total = int(json.data["result"]["limits"]["total"])
                #if query.startswith("movie"):
                for i in range(0, total):

                    try:
                        title = json.data["result"]["movies"][i]["title"]
                        rating = json.data["result"]["movies"][i]["rating"]
                        subtext = json.data["result"]["movies"][i]["plot"][:130] + (json.data["result"]["movies"][i]["plot"][130:] and '--')
                        tagline = json.data["result"]["movies"][i]["tagline"]
                        try:
                            year = json.data["result"]["movies"][i]["year"]
                        except:
                            year = "Unknown"
                        movieid = json.data["result"]["movies"][i]["movieid"]

                        if os.path.isfile("./cache/movie_" + str(movieid) + ".jpg"):
                            ico = "./cache/movie_" + str(movieid) + ".jpg"
                        else:
                            urllib.urlretrieve('http://' + kodi_host + ':' + kodi_port + '/image/' + urllib2.quote(json.data["result"]["movies"][i]["thumbnail"]),"./cache/movie_" + str(movieid) + ".jpg")
                            if os.path.isfile("./cache/movie_" + str(movieid) + ".jpg"):
                                ico = "./cache/movie_" + str(movieid) + ".jpg"
                            else:
                                ico = icons_dir + "movie_white.png"
                        #ico = urllib2.unquote(json.data["result"]["movies"][i]["thumbnail"]).replace("image://", "",1).rstrip('/')
                        #ico = json.data["result"]["movies"][i]["thumbnail"].replace("image://", "",1).rstrip('/')
                        #ico = icons_dir + "movie_white.png"
                        results.append({
                            #"Title": str(title) + " " + "(" + str(year) + ") - Rating: " + str(format(rating, '.1f')) + "/10",
                            "Title": str(title) + " --- \"" + tagline + '\" ' + '[' + str(year) + ']',
                            "SubTitle": subtext,
                            "IcoPath": ico,
                            "JsonRPCAction":{
                              "method": "start_movie",
                              #you MUST pass parater as array
                              "parameters":[movieid],
                              #hide the query wox or not
                              "dontHideAfterAction":False
                            }
                        })
                    except Exception, e:
                        results.append({
                            "Title": 'ERROR',
                            "SubTitle": 'Unable to display content!',
                            "IcoPath": icons_dir + "spell.png"
                        })
                return results

            elif query.startswith("tvshows") and not query.endswith("episodes"):
                json.data = post_data('http://' + kodi_host + ':' + kodi_port + '/jsonrpc',{
                 "jsonrpc": "2.0",
                 "method": "VideoLibrary.GetTvShows",
                 "id": "1484897668671",
                 "params": {
                  "properties": [
                   "title",
                   "plot",
                   "art",
                   "year",
                   "thumbnail"
                  ],
                  "limits": {
                   "start": 0,
                   "end": 0
                  },
                  "sort": {
                   "method": "title",
                   "order": "ascending",
                  },
                  "filter": {
                   "operator": "contains",
                   "field": "title",
                   "value": shifted_query.strip()
                  }
                 }
                })
                total = int(json.data["result"]["limits"]["total"])
                for x in range(0, total):
                    title = json.data["result"]["tvshows"][x]["title"]
                    subtext = json.data["result"]["tvshows"][x]["plot"].replace("\n", "")
                    tvshowid = json.data["result"]["tvshows"][x]["tvshowid"]
                    if os.path.isfile("./cache/tvshows_" + str(tvshowid) + ".jpg"):
                        ico = "./cache/tvshows_" + str(tvshowid) + ".jpg"
                    else:
                        urllib.urlretrieve('http://' + kodi_host + ':' + kodi_port + '/image/' + urllib2.quote(json.data["result"]["tvshows"][x]["thumbnail"]),"./cache/tvshows_" + str(tvshowid) + ".jpg")
                        if os.path.isfile("./cache/tvshows_" + str(tvshowid) + ".jpg"):
                            ico = "./cache/tvshows_" + str(tvshowid) + ".jpg"
                        else:
                            ico = icons_dir + "movie_white.png"
                    #subtext = json.data["result"]["tvshows"][x]["plot"]
                    results.append({
                        "Title": title,
                        "SubTitle": subtext,
                        "IcoPath": ico,
                        "JsonRPCAction": {
                            "method": "Wox.ChangeQuery",
                            "parameters": ["ks tvshows " + title + " episodes", False],
                            # hide the query wox or not
                            "dontHideAfterAction": True,
                        }
                    })
                return results
            elif query.endswith("episodes"):
                shifted_query = query.replace("episodes", "",1)
                shifted_query = shifted_query.replace("tvshows", "",1)
                shifted_query = shifted_query.replace("ks", "",1)
                json.data = post_data('http://' + kodi_host + ':' + kodi_port + '/jsonrpc',{
                 "jsonrpc": "2.0",
                 "method": "VideoLibrary.GetTvShows",
                 "id": "1484897668671",
                 "params": {
                  "properties": [
                   "title",
                   "plot",
                   "art",
                   "year",
                   "thumbnail"
                  ],
                  "limits": {
                   "start": 0,
                   "end": 0
                  },
                  "filter": {
                   "operator": "contains",
                   "field": "title",
                   "value": shifted_query.strip()
                  }
                 }
                })
                tvshowid = json.data["result"]["tvshows"][0]["tvshowid"]
                season = post_data('http://' + kodi_host + ':' + kodi_port + '/jsonrpc',{
                 "jsonrpc": "2.0",
                 "method": "VideoLibrary.GetSeasons",
                 "id": "1",
                 "params": {
                 "tvshowid": tvshowid
                 }
                })
                seasons = int(season["result"]["limits"]["total"])
                for s in range(0, seasons):

                    json.data = post_data('http://10.0.0.50:8080/jsonrpc',{
                     "jsonrpc": "2.0",
                     "method": "VideoLibrary.GetEpisodes",
                     "id": "1",
                     "params": {
                     "tvshowid":
                      tvshowid, "season": s,
                      "properties": [
                        "thumbnail",
                        "plot"
                      ]
                     }
                    })
                    episodes = int(json.data["result"]["limits"]["total"])
                    for e in range (0, episodes):
                        title = json.data["result"]["episodes"][e]["label"]
                        subtext = json.data["result"]["episodes"][e]["plot"].replace("\n", "")
                        episodeid = json.data["result"]["episodes"][e]["episodeid"]
                        if not subtext:
                            subtext = "N/A"
                        results.append({
                            "Title": title,
                            "SubTitle": subtext,
                            "IcoPath": icons_dir + "tv_white.png",
                            "JsonRPCAction":{
                              "method": "start_tv",
                              #you MUST pass parater as array
                              "parameters":[episodeid],
                              #hide the query wox or not
                              "dontHideAfterAction":False
                            }
                        })
                return results
            else:
                results.append({
                    "Title": 'Movie search',
                    "SubTitle": 'Search your Kodi movie library!',
                    "IcoPath": icons_dir + "movie_white.png",
                    "JsonRPCAction": {
                        "method": "Wox.ChangeQuery",
                        "parameters": ["ks movies", False],
                        # hide the query wox or not
                        "dontHideAfterAction": True,
                        "ContextData": "Movie"
                    }
                })
                results.append({
                    "Title": 'TV Show search',
                    "SubTitle": 'Search your Kodi TV show library!',
                    "IcoPath": icons_dir + "tv_white.png",
                    "JsonRPCAction": {
                        "method": "Wox.ChangeQuery",
                        "parameters": ["ks tvshows", False],
                        # hide the query wox or not
                        "dontHideAfterAction": True
                    }
                })
                nplay = post_data('http://' + kodi_host + ':' + kodi_port + '/jsonrpc',{"jsonrpc": "2.0", "method": "Player.GetItem", "params": { "properties": ["title", "album", "artist", "season", "episode", "duration", "showtitle", "tvshowid", "thumbnail", "file", "fanart", "streamdetails"], "playerid": 1 }, "id": "VideoGetItem"})
                results.append({
                    "Title": nplay["result"]["item"]["title"],
                    "SubTitle": 'Currently playing video.'
                })
                return results
        except:
            results.append({
                "Title": 'Error: Could not connect to kodi!',
                "SubTitle": 'Please make sure Kodi is running and Web Server is on...',
                "IcoPath": icons_dir + "kodi_icon.png",
                "JsonRPCAction": {
                    "method": "Wox.ChangeQuery",
                    "parameters": ["kodi", False],
                    # hide the query wox or not
                    "dontHideAfterAction": True
                }
            })
            return results
if __name__ == "__main__":
    Main()
