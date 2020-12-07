Chat data
===================
## Collect Chat data 

 1. twitch_chatlog.py
Collect chatlog using Twitch API, Twitch URL
 2.  metadata.ipynb & dataset.ipynb
Crop collected chat log, following the games
	 *there are serveral LoL games in one Twitch URL, so we need to crop
	 *metadata is pre-required
## Train Chat data
 1. chat_exp.ipynb
 Train Chat data using 3 simple layer LSTM

## Dataset
 1. result
Croped chat log
 2. data
clipchat.txt : collected chat data
metadata.csv : metadata of game 
chat.json : cropped chat data
