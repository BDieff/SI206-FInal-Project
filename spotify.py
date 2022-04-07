import os
import time
import json
import sqlite3
import spotipy
import requests
from spotipy.oauth2 import SpotifyClientCredentials
from bs4 import BeautifulSoup

class SpotifyManager():

    def __init__(self):
        # api key information 
        CLIENT_ID = 'Your Client ID Here'
        CLIENT_SECRET = 'Your Client Secret Here'
        # create spotipy instance
        self.spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET))
        # get charts ids by country
        self.change_curdir()
        with open('country_top_charts.json', 'r') as json_handler:
            self.chart_ids = json.load(json_handler)
        # connect to sqlite db
        self.conn = sqlite3.connect('song_stats_by_country.db')
        self.cur = self.conn.cursor()
        # create country top chart tables
        self.init_db_tables()

    # create country top chart tables
    def init_db_tables(self):
        countries = self.chart_ids.keys()
        for country in countries:
            self.cur.execute(f'''CREATE TABLE IF NOT EXISTS {country}_top_chart (
                                 rank INTEGER, name TEXT, artist TEXT, streams INTEGER,  
                                 popularity INTEGER, length REAL, tempo REAL)''')
        self.conn.commit()

    # change current directory to file directory
    def change_curdir(self):
        file_path = os.path.abspath(__file__)
        dir_path = os.path.dirname(file_path)
        os.chdir(dir_path)

    # drops all country charts tables
    def erase_country_tables(self):
        countries = self.chart_ids.keys()
        for country in countries:
            self.cur.execute(f'DROP TABLE IF EXISTS {country}_top_chart')
            self.cur.execute(f'''CREATE TABLE {country}_top_chart 
                                 (rank INTEGER, name TEXT, artist TEXT, streams INTEGER,  
                                 popularity INTEGER, length REAL, tempo REAL)''')
        self.conn.commit()

    # use rank of song to get its stream
    # count from spotifycharts.com
    def get_stream_count(self, rank, charts_url):
        chart_page = requests.get(charts_url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(chart_page.text,'html.parser')
        table_body = soup.find('tbody')
        all_songs = table_body.find_all('tr')
        specific_song = all_songs[rank]
        streams_tag = specific_song.find('td', class_='chart-table-streams')
        streams_string = streams_tag.text.strip()
        streams_int = int(streams_string.replace(',',''))
        time.sleep(1)
        return streams_int

    # gets song tempo, duration, streams and popularity
    # from desired playlist - will start from a specified rank
    # with 0 representing rank #1, 1 representing rank #2, and so on
    def get_songs(self):
        countries = self.chart_ids.keys()
        for country in countries:
            curr_rank = self.cur.execute(f'SELECT MAX(rank) FROM {country}_top_chart').fetchone()[0]
            if curr_rank == None:
                curr_rank = 0
            plist_id = self.chart_ids[country]['playlist_id']
            chart_url = self.chart_ids[country]['charts_url']
            country_chart = self.spotify.playlist_items(playlist_id=plist_id, fields=None, limit=5, offset=curr_rank)
            for song in country_chart['items']:
                curr_rank += 1
                id = song['track']['id']
                name = song['track']['name']
                artist = song['track']['artists'][0]['name']
                popularity = song['track']['popularity']
                audio_analysis = self.spotify.audio_analysis(id)
                length = audio_analysis['track']['duration']
                tempo = audio_analysis['track']['tempo']
                streams = self.get_stream_count(curr_rank, chart_url)
                self.cur.execute(f'''INSERT OR IGNORE INTO {country}_top_chart
                                     (rank, name, artist, streams, popularity, length, tempo) VALUES (?,?,?,?,?,?,?)''', 
                                     (curr_rank, name, artist, streams, popularity, length, tempo))
            self.conn.commit()

def main():
    pass

main()