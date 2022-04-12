from spotify import SpotifyManager
import os
import unittest
import matplotlib.pyplot as plt

def avg_temp_hbar(data_dict, songs_per_country):
    '''
    Takes in...
        data_dict: dictionary with countries as keys and their average tempo for x songs as values
        songs_per_country: lets the title automatically update to reflect # of songs per country top chart
    Returns...
        nothing
    Creates...
        horizontal bar graph as .png file comparing average tempo for the top x songs in different countries
    '''
    countries = list(data_dict.keys())
    average_tempo = list(data_dict.values())

    fig, ax = plt.subplots()
    ax.barh(countries, average_tempo, color='green')
    ax.autoscale_view()
    ax.set(ylabel='Country', xlabel='Tempo', title=f'Average Tempo by Country for Top {songs_per_country} Streamed Songs on Spotify (March 18th to 25th)')
    fig.savefig('tempo_hbar.png')
    plt.tight_layout()
    plt.show()

class TestVisuals(unittest.TestCase):

    def setUp(self):
        self.testDB = SpotifyManager('test_spotify_api_db.db')
    
    def testHbar(self):
        self.testDB.get_songs()
        tempo_dict, num_songs = self.testDB.get_avg_tempo_by_country()
        avg_temp_hbar(tempo_dict, num_songs)
        os.remove('test_spotify_api_db.db')

if __name__ == '__main__':
    unittest.main(verbosity=2)