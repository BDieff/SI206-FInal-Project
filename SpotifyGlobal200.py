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
        artistlst.append(artist)
    #print(artistlst)

    spotify_tuples = []
    for i in range(0, len(songlst)):
        artist_song = (artistlst[i], songlst[i])
        spotify_tuples.append(artist_song) 
        #print(spotify_tuples) 
    return spotify_tuples         

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
    
    # Artist (datatype: TEXT and PRIMARY KEY)
    # artist_id (datatype: INTEGER)
    # Song (datatype: TEXT)
    # song_id (datatype: INTEGER)
    """
    
    cur.execute("CREATE TABLE IF NOT EXISTS SpotifyGlobal200_Artist (artist_id INTEGER PRIMARY KEY, Artist TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS SpotifyGlobal200_Song (song_id INTEGER PRIMARY KEY, Song TEXT)")
    
    count = 0
    for item in data[0:25]:
        count += 1
        artist = item[0]
        song = item[1]

        cur.execute(
            """
            INSERT OR IGNORE INTO SpotifyGlobal200_Artist (artist_id, Artist)
            VALUES (?, ?)
            """, 

            (count, artist)
        )

        cur.execute(
            """
            INSERT OR IGNORE INTO SpotifyGlobal200_Song (song_id, Song)
            VALUES (?, ?)
            """, 

            (count, song)
        )


    results = cur.fetchall()
    conn.commit()
    # A FEW ARTISTS IN THE TABLE MULTIPLE TIMES W DIFFERENT SONGS?

def main():
    globaldata = get_global("SpotifyGlobal_0324.html")
    cur, conn = setUpDatabase('SpotifyGlobal200.db')
    setUpArtistDatabase(globaldata, cur, conn)

if __name__ == '__main__':
    main()