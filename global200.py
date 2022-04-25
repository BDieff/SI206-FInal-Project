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
    
    - Artist (datatype: TEXT and PRIMARY KEY); if more than one artist for a song, grab ONLY the first artist
    - artist_id (datatype: INTEGER)
    - Song (datatype: TEXT)
    - song_id (datatype: INTEGER)
    """
    cur.execute("CREATE TABLE IF NOT EXISTS SpotifyGlobal200_Artist (id INTEGER PRIMARY KEY UNIQUE, artist TEXT UNIQUE)")
    cur.execute("CREATE TABLE IF NOT EXISTS SpotifyGlobal200_Song (song_id INTEGER PRIMARY KEY UNIQUE, artist_id INTEGER, song_rank INTEGER UNIQUE, song_name TEXT UNIQUE)")
    
    try:
        cur.execute(
            """
            SELECT song_id 
            FROM SpotifyGlobal200_Song
            WHERE song_id = (SELECT MAX(song_id) FROM SpotifyGlobal200_Song)       
            """
        )
    # SELECTS THE MAX SONG_ID AND ADDS BY 25 (RUN 8X TO GET TO 200)
        start = cur.fetchone()
        start = start[0]
        print(start)        
    except:
        start = 0

    for item in chart_data[start:start+25]:
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

            (artist_id, song_rank, song_name)
        )
    conn.commit()
    
def api_limit(cur, conn):
    cur.execute(
        """
        SELECT MAX(song_id) FROM SpotifyGlobal200_Song
        """
    )
    max = cur.fetchone()        
    if max[0] >= 200:
        print(True)
        return True

def getMostPopularArtist(cur, conn):
    """
    This function takes in the 'test_spotify_api_db.db', the database cursor, 
    and the database connection to find the rank of the most popular artist's song from each country. It selects 
    the country's name, the country's top song name, the song's rank, and the song's artist on the Spotify Global 200 Chart. 
    
    The function returns a LIST OF TUPLES. 
    
    Each tuple contains (COUNTRY, top SONG NAME, song's artist on Spotify200).

    """

    cur.execute(
        '''
        SELECT SpotifyGlobal200_Artist.artist, COUNT(SpotifyGlobal200_Song.artist_id) AS cnt FROM SpotifyGlobal200_Song
        JOIN SpotifyGlobal200_Artist
        ON SpotifyGlobal200_Artist.id = SpotifyGlobal200_Song.artist_id
        GROUP BY artist_id
        ORDER BY cnt DESC;
        '''

    )
    results = cur.fetchall()[0:5]
    #print(results)
    y_axis = [str(tup[0]) for tup in results]        
    x_axis = [tup[1] for tup in results]          
    fig, ax = plt.subplots()
    ax.barh(y_axis, x_axis)
    ax.set(ylabel='Artist', xlabel='Frequency', title='Most popular artists on Billboard 200')
    plt.tight_layout()
    plt.show()
    fig.savefig('most_popular_artist_bboard.png', bbox_inches='tight')

def main():
    BB200data = get_global200()
    cur, conn = setUpDatabase('final_project.db')
    setUpArtistDatabase(BB200data, cur, conn)
    api_limit(cur, conn)
    getMostPopularArtist(BB200data, cur, conn)

if __name__ == '__main__':
    main()
    unittest.main(verbosity=2)