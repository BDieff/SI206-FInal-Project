import pandas as pd
import sqlite3
import csv
import unittest
import matplotlib.pyplot as plt
import seaborn as sns

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
    with open('avg_tempo_by_country.txt', 'w') as fh:
        fh.write(f"Average Tempo for Each Country's Top {songs_per_country} Songs on Spotify\n")
        for country in countries:
            fh.write(f'{country}: {data_dict[country]} BPM on Average\n')
    fig, ax = plt.subplots()
    ax.barh(countries, average_tempo, color='green')
    ax.autoscale_view()
    ax.set(ylabel='Country', xlabel='Tempo (BPM)', title=f'Average tempo for top {songs_per_country} songs on Spotify')
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
    with open('mins_per_person_by_country.txt', 'w') as fh:
        fh.write(f"Minutes per Person Streamed on Spotify for Each Country's Top {songs_per_country} Songs\n")
        for country in countries:
            fh.write(f'{country}: {time_per_person_by_country[country]} minutes per person\n')
    minutes_per_person = list(time_per_person_by_country.values())
    ax.barh(countries_axis, minutes_per_person, color='green')
    ax.autoscale_view()
    ax.set(ylabel='Country', xlabel='Minutes per Person', title=f'Total listen time for top {songs_per_country} songs on Spotify')
    fig.savefig('minutes_pperson_hbar.png', bbox_inches='tight')
    plt.tight_layout()
    plt.show()

class TestVisuals(unittest.TestCase):

    def testTempoHbar(self):
        num_songs = 5
        tempo_dict = {'Nigeria':110, 'Mexico':130, 'India':99}
        avg_temp_hbar(tempo_dict, num_songs)

    def testMinutesHbar(self):
        num_songs = 5
        population_dict = {'United States': 331893745, 'Mexico': 131333546, 'United Kingdom': 68515161, 'Nigeria': 215189366, 'India': 1404050703}
        minutes_by_country = {'United States': 10292938871, 'Mexico': 2723652, 'United Kingdom': 12381317236, 'Nigeria': 237276562, 'India': 1231312345}
        minutes_per_person_hbar(minutes_by_country, population_dict, num_songs)

if __name__ == '__main__':
    unittest.main(verbosity=2)