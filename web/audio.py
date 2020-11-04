import util
import sys
import re
import requests
import urllib.parse
import os
import json
#Util class for twitch-dl

#Fancy!
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#Declaring the headers just one time
def getHeaders():
    headers = {
        #Seems that this Client-ID is specific for the not-logged user?
    	'Client-ID': 'pnbcpj842zq89uy7hlhkakepr6xej7'
	}
    return headers

#Returns a JSON object for printing and naming the output file
def getVideoInfo(video_id):
    url="https://api.twitch.tv/kraken/videos/"+str(video_id)
    response = urllib.request.Request(url, headers = {"Client-ID": 'pnbcpj842zq89uy7hlhkakepr6xej7', "Accept" : "application/vnd.twitchtv.v5+json"})
    u = urllib.request.urlopen(response)
    c = u.read().decode('utf-8')
    js = json.loads(c)

    #Creating the object
    return {"title": js['title']}

#Returns a JSON object for token and sig key, used to create the playlist url
def getAccessToken(video_id):
    #unique_id can be anything 16 char long. Using this instead of random
    cookies = {'unique_id': '123456789012345'}
    response = urllib.request.Request('https://api.twitch.tv/api/vods/' + video_id + '/access_token', headers = {"Client-ID": 'kimne78kx3ncx6brgo4mv6wki5h1ko', "Accept" : "application/vnd.twitchtv.v5+json"})
    print(response)

    u = urllib.request.urlopen(response)
    c = u.read().decode('utf-8')
    js = json.loads(c)
    print('===')
    print(js)
    print('===')
    return {"token": js['token'], "sig": js['sig']}

#Formatting the download url
def getDownloadUrl(video_id):
    video_tokens = getAccessToken(video_id)
    download_url = "https://usher.ttvnw.net/vod/" + video_id + ".m3u8" + \
					"?allow_source=true" + \
					"&p=5760802" + \
					"&player_backend=mediaplayer" + \
					"&playlist_include_framerate=true" + \
					"&reassignments_supported=true" + \
					"&sig=" + video_tokens['sig'] + \
					"&token=" + urllib.parse.quote(video_tokens['token']) + \
					"&cdm=wv"
    return download_url

def downloadVideo(video_id):
    video_infos = getVideoInfo(video_id)
    video_title = "'" + video_infos['title'] + "'"
    command = "ffmpeg -i '"+ getDownloadUrl(video_id) +"' -ss {} -t {} -v quiet -stats -acodec copy -vcodec copy ".format()+ str(video_title) + ".mp4"
    os.system(command)

if __name__ == "__main__":

#Arrays for video queue
match = []

print(util.bcolors.WARNING + "\ntwitch-dl ~ https://github.com/0xf77/twitch-dl" + util.bcolors.ENDC + "\n")

if len(sys.argv) < 2:
 	print(util.bcolors.FAIL + "[e] No URL to download, use: https://www.twitch.tv/videos/..." + util.bcolors.ENDC)
 	quit()

for videos in sys.argv:
	if re.findall(r'\d+', videos):
		match.append(re.findall(r'\d+', videos)[0])
                #print(match)
print(util.bcolors.WARNING + "It could take some seconds to start the download!" + util.bcolors.ENDC)
for video_id in match:
	video_infos = util.getVideoInfo(video_id)
	print(util.bcolors.OKGREEN + "Downloading: " + video_infos['title'] + " from " +util.bcolors.ENDC)
	util.downloadVideo(video_id)

print(util.bcolors.FAIL + "Bye! ❤️" + util.bcolors.ENDC)
