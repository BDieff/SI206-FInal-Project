from xml.sax import parseString
from bs4 import BeautifulSoup
import requests
import re
import os
import json
import csv
import unittest
import sqlite3
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from textwrap import wrap
import datetime

def get_global(filename):
    """
    Write a function that creates a BeautifulSoup object on "SpotifyGlobal_0324.html". Parse
    through the object and return a list of tuples containing the artist name and their associated song. 

    [('Artist 1', 'Song 1'), ('Artist 2', 'Song 2')...]
    """
    source_dir = os.path.dirname(__file__) 
    full_path = os.path.join(source_dir, filename)
    file_object = open(full_path, 'r')
    data = file_object.read()
    file_object.close()

    soup = BeautifulSoup(data, 'html.parser')
    
    songlst = []
    song_data = soup.find_all('strong', None)
    for item in song_data:
        #print(item)
        song = item.text.strip()
        songlst.append(song)
    #print(songlst)
    
    artistlst = []
    artist_data = soup.find_all('td', class_ = "chart-table-track")
    for item in artist_data:
        #print(item)
        artisttag = item.find('span', None)
        artist = artisttag.text.strip("by ")
        if ',' in artist:
            single = artist.split(',')
            artistlst.append(single)
        else:
            artistlst.append([artist])
    #print(artistlst)
        
    spotify_data = []
    for i in range(0, len(songlst)):
        artist_song = {}
        artist = artistlst[i]
        song = songlst[i]
        artist_song['artists'] = artist
        artist_song['song'] = song
        # artist_song = (artistlst[i], songlst[i])
        # spotify_tuples.append(artist_song) 
        spotify_data.append(artist_song)
    #print(spotify_data)
    return spotify_data         

def setUpDatabase(db_name):
    """ 
    Sets up the parameters for making an SQL query to a database. 
    """

    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def setUpArtistDatabase(data, cur, conn):
    """
    Load all data from the function 'get_global' into a table called 'SpotifyGlobal200'
    giving the artist and song name a unique ID with the following columns:
    
    # Artist (datatype: TEXT and PRIMARY KEY); if more than one artist for a song, grab ONLY the first artist
    # artist_id (datatype: INTEGER)
    # Song (datatype: TEXT)
    # song_id (datatype: INTEGER)
    """
    cur.execute("CREATE TABLE IF NOT EXISTS SpotifyGlobal200_Artist (artist_id INTEGER PRIMARY KEY, artist TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS SpotifyGlobal200_Song (song_id INTEGER PRIMARY KEY AUTOINCREMENT, song_rank INTEGER, song_name TEXT)")
    
    # COUNT FOR SONG TABLE:
    # AUTO INCREMENT INTEGER 
    count = 0
    for item in data[0:25]:
        count += 1 
        #print(item)
        main_artist = item['artists'][0]
        song = item['song']

        cur.execute(
            """
            INSERT OR IGNORE INTO SpotifyGlobal200_Artist (artist_id, artist)
            VALUES (?, ?)
            """, 

            (count, main_artist)
        )

        cur.execute(
            """
            INSERT OR IGNORE INTO SpotifyGlobal200_Song (song_id, song_rank, song_name)
            VALUES (?, ?, ?)
            """, 

            (count, count, song)
        )

    results = cur.fetchall()
    conn.commit()
    # A FEW ARTISTS IN THE TABLE MULTIPLE TIMES W DIFFERENT SONGS?

def getCountryTopSongRank(data, rank, cur, conn):
    """
    This function takes in the 'test_spotify_api_db.db', song rank of 1, the database cursor, 
    and the database connection. It selects the country's name, the country's top song rank, and the country's
    top song name. The function returns a LIST OF TUPLES. 
    
    Each tuple contains (the COUNTRY, country's top song RANK, the country's top SONG NAME).

    """
    cur.execute(
        """
        SELECT country_ids.country, top_songs.rank, top_songs.name 
        FROM country_ids
        JOIN top_songs ON country_ids.id = top_songs.country_id
        WHERE top_songs.rank = ?

        """, 
        
        (rank,)
    )
    
    results = cur.fetchall()
    #print(results)
    return results 

def getCountrySpotifyRank(data, cur, conn):
    """
    This function takes in the 'test_spotify_api_db.db', the database cursor, 
    and the database connection. It selects the country's name, the country's top song rank, and the country's
    top song name, and the song's rank on the Spotify Global 200 Chart. The function returns a LIST OF TUPLES. 
    
    Each tuple contains (COUNTRY, country's top song RANK, top SONG NAME, country's top song RANK on Spotify200).

    """

    cur.execute(
        """
        SELECT country_ids.country, top_songs.rank, top_songs.name, SpotifyGlobal200_Song.rank 
        FROM country_ids
        JOIN top_songs ON country_ids.id = top_songs.country_id
        JOIN SpotifyGlobal200_Song ON top_songs.name = SpotifyGlobal200_Song.song_name
        """

    )
    results = cur.fetchall()
    #print(results)
    return results


def getMostPopularArtist(data, cur, conn):
    """
    This function takes in the 'test_spotify_api_db.db', the database cursor, 
    and the database connection to find the most popular artist from each country. It selects the country's name, 
    the country's top song name, and the song's artist on the Spotify Global 200 Chart. The function returns a LIST OF TUPLES. 
    
    Each tuple contains (COUNTRY, top SONG NAME, song's artist on Spotify200).

    """

    cur.execute(
        """
        SELECT country_ids.country, top_songs.name, SpotifyGlobal200_Artist.artist
        FROM country_ids
        JOIN top_songs ON country_ids.id = top_songs.country_id
        JOIN SpotifyGlobal200_Artist ON top_songs.artist = SpotifyGlobal200_Artist.artist
        """
    )
    results = cur.fetchall()
    #print(results)
    return results

def main():
    globaldata = get_global("SpotifyGlobal_0324.html")
    #get_global("SpotifyGlobal_0324.html")
    cur, conn = setUpDatabase('SpotifyGlobal200.db')
    setUpArtistDatabase(globaldata, cur, conn)
    #etCountryTopSongRank(test_spotify_api_db.db, 1, cur, conn)

if __name__ == '__main__':
    main()