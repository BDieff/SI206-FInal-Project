import os
import time
import json
import sqlite3
import spotipy
import requests
import unittest
from spotipy.oauth2 import SpotifyClientCredentials
from bs4 import BeautifulSoup

# This file should be run after census.py and SpotifyGlobal200.py

class SpotifyManager():

    def __init__(self, db_name='test_spotify_api.db', json_file='country_top_charts.json'):
        # api key information 
        CLIENT_ID = 'c126e9db4b244678b224ad4d6ba4477c'
        CLIENT_SECRET = '713cc4c51d1042aeb6e08d58791b5fac'
        # create spotipy instance
        self.spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET))
        # get charts ids by country
        self.change_curdir()
        with open(json_file, 'r') as json_handler:
            self.chart_ids = json.load(json_handler)
        # connect to sqlite db
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        # create country top chart tables
        #self.init_country_ids()
        self.init_db_table()

    # change current directory to file directory
    def change_curdir(self):
        file_path = os.path.abspath(__file__)
        dir_path = os.path.dirname(file_path)
        os.chdir(dir_path)
    
    '''
    # create country id table
    def init_country_ids(self):
        self.cur.execute('CREATE TABLE IF NOT EXISTS country_ids (id INTEGER PRIMARY KEY, country TEXT)')
        countries = self.chart_ids.keys()
        for country in countries:
            self.cur.execute('INSERT OR IGNORE INTO country_ids (country) VALUES (?)', (country,))
        self.conn.commit()
    '''

    # create country top chart table
    def init_db_table(self):
        self.cur.execute(f'''CREATE TABLE IF NOT EXISTS top_songs (country_id INTEGER,
            rank INTEGER, song_id INTEGER, artist_id INTEGER, streams INTEGER, popularity INTEGER, 
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
    def get_songs(self, country_id_list):
        #country_ids = self.cur.execute('SELECT country_id, name FROM census_data').fetchall()
        for country in country_id_list:
            country_name = self.cur.execute(f'SELECT name FROM census_data WHERE country_id = {country}').fetchone()[0]
            curr_rank = self.cur.execute(f'SELECT MAX(rank) FROM top_songs WHERE country_id = {country}').fetchone()[0]
            if curr_rank == None:
                curr_rank = 0
            plist_id = self.chart_ids[country_name]['playlist_id']
            chart_url = self.chart_ids[country_name]['charts_url']
            country_chart = self.spotify.playlist_items(playlist_id=plist_id, fields=None, limit=5, offset=curr_rank)
            for song in country_chart['items']:
                curr_rank += 1
                id = song['track']['id']
                name = song['track']['name']
                name_id_in_list = self.cur.execute(f'SELECT song_id FROM SpotifyGlobal200_Song WHERE song_name = "{name}"').fetchall()
                if len(name_id_in_list) == 0:
                    self.cur.execute(f'INSERT INTO SpotifyGlobal200_Song (song_name) VALUES (?)', (name,))
                    self.conn.commit()
                    name_id = self.cur.execute(f'SELECT MAX(song_id) FROM SpotifyGlobal200_Song').fetchone()[0]
                else:
                    name_id = name_id_in_list[0]
                artist = song['track']['artists'][0]['name']
                artist_id_in_list = self.cur.execute(f'SELECT artist_id FROM SpotifyGlobal200_Artist WHERE artist = "{name}"').fetchall()
                if len(artist_id_in_list) == 0:
                    self.cur.execute(f'INSERT INTO SpotifyGlobal200_Artist (artist) VALUES (?)', (artist,))
                    self.conn.commit()
                    artist_id = self.cur.execute(f'SELECT MAX(id) FROM SpotifyGlobal200_Artist').fetchone()[0]
                else:
                    artist_id = artist_id_in_list[0]
                popularity = song['track']['popularity']
                audio_analysis = self.spotify.audio_analysis(id)
                length = audio_analysis['track']['duration']
                tempo = audio_analysis['track']['tempo']
                streams = self.get_stream_count(curr_rank, chart_url)
                self.cur.execute(f'''INSERT OR IGNORE INTO top_songs (country_id, rank, song_id, artist_id, streams, popularity, length, tempo) 
                    VALUES (?,?,?,?,?,?,?,?)''', (country, curr_rank, name_id, artist_id, streams, popularity, length, tempo))
            self.conn.commit()

    def get_avg_tempo_by_country(self, country_id_list):
        #country_ids = self.cur.execute('SELECT id, country FROM country_ids').fetchall()
        avg_tempo_by_country = {}
        num_songs = 0
        for country in country_id_list:
            country_name = self.cur.execute(f'SELECT name FROM census_data WHERE country_id = {country}').fetchone()[0]
            song_list = self.cur.execute(f'SELECT tempo FROM top_songs WHERE country_id = {country}').fetchall()
            num_songs = len(song_list)
            tempo_sum = 0
            for song in song_list:
                tempo_sum += song[0]
            avg_tempo = tempo_sum/num_songs
            avg_tempo_by_country[country_name] = avg_tempo
        return avg_tempo_by_country, num_songs

    def get_total_stream_time_for_top(self, country_id_list):
        #country_ids = self.cur.execute('SELECT id, country FROM country_ids').fetchall()
        total_streams_by_country = {}
        num_songs = 0
        for country in country_id_list:
            country_name = self.cur.execute(f'SELECT name FROM census_data WHERE country_id = {country}').fetchone()[0]
            song_list = self.cur.execute(f'SELECT (streams*length)/60 FROM top_songs WHERE country_id = {country}').fetchall()
            num_songs = len(song_list)
            total_dur = 0
            for song in song_list:
                total_dur += song[0]
            total_streams_by_country[country_name] = total_dur
        return total_streams_by_country, num_songs

class testManager(unittest.TestCase):

    isSetUp = False

    def setUp(self):
        if not self.isSetUp:
            self.setupClass()
            self.__class__.isSetUp = True

    def setupClass(self):
        try:
            os.remove('test_spotify_api.db')
        except:
            pass
        self.__class__.testDB = SpotifyManager()
        self.testDB.get_songs()
        self.__class__.conn = sqlite3.connect('test_spotify_api.db')
        self.__class__.cur = self.conn.cursor()

    #this wont work anymore because I changed function
    def testGetSongs(self):
        for i in range(1,6):
            max_rank = self.cur.execute(f'SELECT MAX(rank) FROM top_songs WHERE country_id = {i}').fetchall()[0][0]
            self.assertEqual(max_rank, 5)

    #this wont work anymore because I changed function
    def testGetAvgTempoByCountry(self):
        avg_temp_by_country, num_songs = self.testDB.get_avg_tempo_by_country()
        self.assertEqual(num_songs, 5)
        self.assertAlmostEqual(avg_temp_by_country['US'], 148.3486, 4)
        self.assertAlmostEqual(avg_temp_by_country['UK'], 120.7402, 4)
        self.assertAlmostEqual(avg_temp_by_country['Nigeria'], 114.6592, 4)
        self.assertAlmostEqual(avg_temp_by_country['Mexico'], 143.7192, 4)
        self.assertAlmostEqual(avg_temp_by_country['India'], 101.4396, 4)    

    #this wont work anymore because I changed function
    def testGetTotalStreamTimeForTop(self):
        dur_by_country, num_songs = self.testDB.get_total_stream_time_for_top()
        self.assertEqual(num_songs, 5)
        self.assertAlmostEqual(dur_by_country['US'], 71739193.829, 3)
        self.assertAlmostEqual(dur_by_country['UK'], 31311652.982, 3)
        self.assertAlmostEqual(dur_by_country['Nigeria'], 1674480.039, 3 )
        self.assertAlmostEqual(dur_by_country['Mexico'], 61257668.254, 3)
        self.assertAlmostEqual(dur_by_country['India'], 43229876.402, 3) 

if __name__ == '__main__':
    unittest.main(verbosity=2)
    os.remove('test_spotify_api.db')