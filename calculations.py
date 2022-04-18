import os
import time
import json
import sqlite3
import spotipy
import requests
import unittest
import census
import global200
from spotipy.oauth2 import SpotifyClientCredentials
from bs4 import BeautifulSoup

def get_avg_tempo_by_country(self, country_id_list):
        # country_ids = self.cur.execute('SELECT id, country FROM country_ids').fetchall()
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
    # country_ids = self.cur.execute('SELECT id, country FROM country_ids').fetchall()
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