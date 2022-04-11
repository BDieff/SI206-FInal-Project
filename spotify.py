import os
import time
import json
import sqlite3
import spotipy
import requests
import unittest
from spotipy.oauth2 import SpotifyClientCredentials
from bs4 import BeautifulSoup

class SpotifyManager():

    def __init__(self, db_name='song_stats_by_country.db'):
        # api key information 
        CLIENT_ID = 'c126e9db4b244678b224ad4d6ba4477c'
        CLIENT_SECRET = '713cc4c51d1042aeb6e08d58791b5fac'
        # create spotipy instance
        self.spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET))
        # get charts ids by country
        self.change_curdir()
        with open('country_top_charts.json', 'r') as json_handler:
            self.chart_ids = json.load(json_handler)
        # connect to sqlite db
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        # create country top chart tables
        self.init_country_ids()
        self.init_db_tables()

    # change current directory to file directory
    def change_curdir(self):
        file_path = os.path.abspath(__file__)
        dir_path = os.path.dirname(file_path)
        os.chdir(dir_path)
    
    # create country id table
    def init_country_ids(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS country_ids (id INTEGER PRIMARY KEY, country TEXT)')
        countries = self.chart_ids.keys()
        for country in countries:
            self.cur.execute('INSERT OR IGNORE INTO country_ids (country) VALUES (?)', (country,))
        self.conn.commit()

    # create country top chart table
    def init_db_tables(self):
        self.cur.execute(f'''CREATE TABLE IF NOT EXISTS top_songs (country_id INTEGER,
            rank INTEGER, name TEXT, artist TEXT, streams INTEGER, popularity INTEGER, 
            length REAL, tempo REAL)''')
        self.conn.commit()

    # drops specified table
    def erase_table(self, table_title):
        self.cur.execute(f'DROP TABLE IF EXISTS {table_title}')
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
        time.sleep(0.5)
        return streams_int

    # gets song tempo, duration, streams and popularity
    # from desired playlist - will start from a specified rank
    # with 0 representing rank #1, 1 representing rank #2, and so on
    def get_songs(self):
        country_ids = self.cur.execute('SELECT id, country FROM country_ids').fetchall()
        for country in country_ids:
            curr_rank = self.cur.execute(f'SELECT MAX(rank) FROM top_songs WHERE country_id = {country[0]}').fetchone()[0]
            if curr_rank == None:
                curr_rank = 0
            plist_id = self.chart_ids[country[1]]['playlist_id']
            chart_url = self.chart_ids[country[1]]['charts_url']
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
                self.cur.execute(f'''INSERT OR IGNORE INTO top_songs (country_id, rank, name, artist, streams, popularity, length, tempo) 
                    VALUES (?,?,?,?,?,?,?,?)''', (country[0], curr_rank, name, artist, streams, popularity, length, tempo))
            self.conn.commit()

    def get_avg_tempo_by_country(self):
        country_ids = self.cur.execute('SELECT id, country FROM country_ids').fetchall()
        avg_tempo_by_country = {}
        num_songs = 0
        for country in country_ids:
            country_name = country[1]
            country_id = country[0]
            song_list = self.cur.execute(f'SELECT tempo FROM top_songs WHERE country_id = {country_id}').fetchall()
            num_songs = len(song_list)
            tempo_sum = 0
            for song in song_list:
                tempo_sum += song[0]
            avg_tempo = tempo_sum/num_songs
            avg_tempo_by_country[country_name] = avg_tempo
        return avg_tempo_by_country, num_songs

class testManager(unittest.TestCase):

    def setUp(self):
        self.testDB = SpotifyManager('test_spotify_api_db')

    def testGetSongs(self):
        for i in range(0,5):
            self.testDB.get_songs()
        conn = sqlite3.connect('test_spotify_api_db')
        cur = conn.cursor()
        for i in range(1,6):
            max_rank = cur.execute(f'SELECT MAX(rank) FROM top_songs WHERE country_id = {i}').fetchall()[0][0]
            self.assertEqual(max_rank, 25)
        os.remove('test_spotify_api_db')

if __name__ == '__main__':
    unittest.main(verbosity=2)