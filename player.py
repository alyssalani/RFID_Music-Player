#!/usr/bin/env python
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from time import sleep
import requests

GPIO.setmode(GPIO.BOARD)

skipPin = 12
VolUpPin = 16
VolDownPin = 13
PlayPausePin = 31

GPIO.setup(skipPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(VolUpPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(VolDownPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PlayPausePin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#DEVICE_ID, CLIENT_ID, and CLIENT_SECRET values have been removed from this code due to them being sensitive information

#SPOTIFY_GET_CURRENT_STATUS_URL = 'https://api.spotify.com/v1/me/player'
SPOTIFY_ADD_TO_QUEUE_URL = 'https://api.spotify.com/v1/me/player/queue'

AUTH_URL = 'https://accounts.spotify.com/api/token'
auth_response = requests.post(AUTH_URL, {
    'grant_type' : 'client_credentials',
    'client_id' : CLIENT_ID,
    'client_secret' : CLIENT_SECRET,})

auth_response_data = auth_response.json()
access_token = auth_response_data['access_token']

headers = {'Authorization' : 'Bearer {token}'.format(token=access_token)}

def add_to_queue(songID):
    response = requests.post(
        SPOTIFY_ADD_TO_QUEUE_URL,
        "spotify:track:" + songID, headers=headers
     )
     resp_json = response.json()
     #if bad code is given, tell user
###Functions for when buttons are pressed###
def skipSong():
    response = requests.post(
        'https://api.spotify.com/v1/me/player/next', DEVICE_ID, headers=headers)
    resp_json = response.json()

def volumeUp(volume):
    volume += 10
    response = requests.put('https://api.spotify.com/v1/me/player/volume', volume, headers=headers)
    resp_json = response.json()
    
def volumeDown(volume):
    volume -= 10
    response = requests.put('https://api.spotify.com/v1/me/player/volume', volume, headers=headers)
    resp_json = response.json()
    
def pausePlay():
    response = requests.put('https://api.spotify.com/v1/me/player/pause', headers=headers)
    
###start player###
    
while True:
    try:
        reader=SimpleMFRC522()
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                       client_secret=CLIENT_SECRET,
                                                       redirect_uri="http://localhost:8080",
                                                       scope="user-read-playback-state,user-modify-playback-state"))
        # create an infinite while loop that will always be waiting for a new scan
        first = True
        volumeUp(20) # preset the volume value to 30 (20+10 because the volumeUp function adds 10.)
        volume = 30 #volume is a percentage that the API takes in 
        while True:
            print("Waiting for record scan...")
            id= reader.read()
            sp.transfer_playback(device_id=DEVICE_ID, force_play=False)
            
            songID=id[1] #index 0 is the default value stored on the card, index 1 is the value I added to the card
            
            #imageID=id[2] to be implemented with lcd screen
            # playing a song
            if(first): # if it is the first card scanned, then play instantly. Otherwise, just add to queue
                sp.start_playback(device_id=DEVICE_ID, uris=['spotify:track:' + songID])
                first=False
                sleep(2)
            else: # if playing add to queue. If first song ends, not sure how this will be handled
                add_to_queue(songID)
                
            skipState = GPIO.input(skipPin)
            VolUpState = GPIO.input(VolUpPin)
            VolDownState = GPIO.input(VolDownPin)
            PlayPauseState = GPIO.input(PlayPausePin)
            
            if (skipState == False): # Means that button is pressed
                skipSong()
            if (VolUpState == False):
                volumeUp(volume)
            if (VolDownState == False):
                volumeDown(volume)
            if (PlayPauseState == False):
                pausePlay()


    # if there is an error, skip it and try the code again (i.e. timeout issues, no active device error, etc)
    except Exception as e:
        print(e)
        pass

    finally:
        print("Cleaning  up...")
        GPIO.cleanup()
