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
import unittest
import billboard

def get_global200():
    """
    Returns list of tuples formatted (song_rank, song_name, artist) from the Billboard Global 200 Chart. 
    """
    chart = billboard.ChartData("billboard-global-200")
    #print(chart)
    globaldata = []
    for i in range(0, len(chart)):
        song_name = chart[i].title
        song_rank = chart[i].rank 
        artist = chart[i].artist
        #print(artist)
        if ',' in artist: 
            artist = artist.split(', ')[0].strip()
        if re.search('(.+) [&xX] .+', artist):
            artist = re.findall('(.+) [&xX] .+', artist)[0].strip()
        if re.search('(.*)[Ff]eaturing', artist): 
            artist = re.findall('(.*)[Ff]eaturing', artist)[0].strip()
        globaldata.append((song_name, artist, song_rank))
    return globaldata

def setUpDatabase(db_name):
    """ 
    Sets up the parameters for making an SQL query to a database. 
    """

    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def setUpArtistDatabase(chart_data, cur, conn):
    """
    Load all data from the function 'get_global' into a table called 'SpotifyGlobal200'
    giving the artist and song name a unique ID with the following columns:
    
    # Artist (datatype: TEXT and PRIMARY KEY); if more than one artist for a song, grab ONLY the first artist
    # artist_id (datatype: INTEGER)
    # Song (datatype: TEXT)
    # song_id (datatype: INTEGER)
    """
    cur.execute("CREATE TABLE IF NOT EXISTS SpotifyGlobal200_Artist (id INTEGER PRIMARY KEY UNIQUE, artist TEXT UNIQUE)")
    cur.execute("CREATE TABLE IF NOT EXISTS SpotifyGlobal200_Song (song_id INTEGER PRIMARY KEY UNIQUE, artist_id INTEGER, song_rank INTEGER UNIQUE, song_name TEXT UNIQUE)")
    
    # COUNT FOR SONG TABLE:
    # AUTO INCREMENT INTEGER 
    count = 0
    for item in chart_data[0:25]:
        count += 1 
        #print(item)
        song_rank = item[2]
        song_name = item[0]
        artist_name = item[1]

        cur.execute(
            """
            INSERT OR IGNORE INTO SpotifyGlobal200_Artist (artist)
            VALUES (?)
            """, 

            (artist_name,)
        )

        artist_id = cur.execute(
            f'''
            SELECT id FROM SpotifyGlobal200_Artist 
            WHERE artist = "{artist_name}"
            '''
        ).fetchone()[0]
        
        cur.execute(
            """
            INSERT OR IGNORE INTO SpotifyGlobal200_Song (artist_id, song_rank, song_name)
            VALUES (?, ?, ?)
            """, 

            (artist_id, count, song_name)
        )

    results = cur.fetchall()
    conn.commit()

def getCountryTopSongRank(data, rank, cur, conn):
    """
    This function takes in the 'test_spotify_api_db.db', song rank of 1, the database cursor, 
    and the database connection. It selects the country's name, the country's top song rank, and the country's
    top song name. 
    
    The function returns a LIST OF TUPLES. 
    
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
    pass
    
def getCountrySpotifyRank(data, cur, conn):
    """
    This function takes in the 'test_spotify_api_db.db', the database cursor, 
    and the database connection. It selects the country's name, the country's top song rank, and the country's
    top song name, and the song's rank on the Spotify Global 200 Chart. 
    
    The function returns a LIST OF TUPLES. 
    
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
    pass

def getMostPopularArtist(data, cur, conn):
    """
    This function takes in the 'test_spotify_api_db.db', the database cursor, 
    and the database connection to find the rank of the most popular artist's song from each country. It selects 
    the country's name, the country's top song name, the song's rank, and the song's artist on the Spotify Global 200 Chart. 
    
    The function returns a LIST OF TUPLES. 
    
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
    pass

def main():
    BB200data = get_global200()
    cur, conn = setUpDatabase('final_project.db')
    setUpArtistDatabase(BB200data, cur, conn)

if __name__ == '__main__':
    main()
    unittest.main(verbosity=2)