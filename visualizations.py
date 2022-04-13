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
    ax.set(ylabel='Country', xlabel='Tempo (BPM)', title=f'Average tempo for top {songs_per_country} songs on Spotify (March 18-25)')
    fig.savefig('tempo_hbar.png', bbox_inches='tight')
    plt.tight_layout()
    plt.show()

def minutes_per_person_hbar(minutes_by_country, population, songs_per_country):
    '''
    Takes in...
        minutes_by_country: dictionary with countries as key and total listening time for top x songs in minutes as values
        population: dictionary with countries as key and total population as values
        songs_per_country: lets the title automatically update to reflect # of songs per country top chart
    Returns...
        nothing
    Creates...
        horizontal bar graph as .png file comparing listening time per person for top x songs in different countries
    '''
    countries = list(minutes_by_country.keys())
    time_per_person_by_country = {}
    for country in countries:
        minutes_total = minutes_by_country[country]
        country_pop = population[country]
        time_per_person_by_country[country] = minutes_total/country_pop
    fig, ax = plt.subplots()
    countries_axis = list(time_per_person_by_country.keys())
    minutes_per_person = list(time_per_person_by_country.values())
    ax.barh(countries_axis, minutes_per_person, color='green')
    ax.autoscale_view()
    ax.set(ylabel='Country', xlabel='Minutes per Person', title=f'Total listen time for top {songs_per_country} songs on Spotify (March 18-25)')
    fig.savefig('minutes_pperson_hbar.png', bbox_inches='tight')
    plt.tight_layout()
    plt.show()

class TestVisuals(unittest.TestCase):

    isSetUp = False

    def setUp(self):
        if not self.isSetUp:
            self.setupClass()
            self.__class__.isSetUp = True

    def setupClass(self):
        try:
            os.remove('test_spotify_api.db')
            os.remove('minutes_pperson_hbar.png')
            os.remove('tempo_hbar.png')
        except:
            pass
        self.__class__.testDB = SpotifyManager()
        self.testDB.get_songs()

    def testTempoHbar(self):
        tempo_dict, num_songs = self.testDB.get_avg_tempo_by_country()
        avg_temp_hbar(tempo_dict, num_songs)

    def testMinutesHbar(self):
        population_dict = {'US': 331893745, 'Mexico': 131333546, 'UK': 68515161, 'Nigeria': 215189366, 'India': 1404050703}
        minutes_by_country, num_songs = self.testDB.get_total_stream_time_for_top()
        minutes_per_person_hbar(minutes_by_country, population_dict, num_songs)

if __name__ == '__main__':
    unittest.main(verbosity=2)