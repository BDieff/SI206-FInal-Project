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

def placement_difference_catplot(country_specific_rank, global_rank):
    '''
    Takes in...
        country_specific_rank: rank of songs in each country's top chart
        global_rank: rank of songs in global top_chart
    Returns...
        nothing
    Creates...
        catplot mapping the difference between the global rank and the country specific rank
    '''
    countries = country_specific_rank.keys()
    data_table = []
    data_table.append(('Country','Song','Rank Difference'))
    for country in countries:
        songs = global_rank.keys()
        for song in songs:
            country_rank = country_specific_rank[country][song]
            tchart_rank = global_rank[song]
            rank_diff = country_rank-tchart_rank
            data_table.append((country, song, rank_diff))
    with open('rank_diff.csv','w') as file_handler:
        writer = csv.writer(file_handler)
        for row in data_table:
            writer.writerow(row)
    rank_data = pd.read_csv('rank_diff.csv')
    sns.swarmplot(x='Country', y='Rank Difference', hue='Song', data=rank_data, size=7)
    lgnd = plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
    plt.savefig('rank_diff.png', bbox_extra_artists=(lgnd,) ,bbox_inches='tight')

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

    def testRankDiffCatPlot(self):
        top_fifteen_daily = {
            "As It Was":1,
            "First Class":2,
            "Heat Waves":3,
            "STAY (with Justin Bieber)":4,
            "Enemy (with JID)":5,
            "Envolver":6,
            "Bam Bam (feat. Ed Sheeran)":7,
            "Cold Heart - PNAU Remix":8,
            "INDUSTRY BABY (feat. Jack Harlow":9,
            "abcdefu":10,
            "Una Noche en Medellín":11,
            "MIDDLE OF THE NIGHT":12,
            "Ghost":13,
            "MAMIII":14,
            "Desesperados":15
        }
        country_specific_ranks = {}
        United_States = {
                "As It Was":2,
                "First Class":1,
                "Heat Waves":3,
                "STAY (with Justin Bieber)":5,
                "Enemy (with JID)":7,
                "Envolver":148,
                "Bam Bam (feat. Ed Sheeran)":20,
                "Cold Heart - PNAU Remix":29,
                "INDUSTRY BABY (feat. Jack Harlow":4,
                "abcdefu":41,
                "Una Noche en Medellín":201,
                "MIDDLE OF THE NIGHT":39,
                "Ghost":12,
                "MAMIII":47,
                "Desesperados":172
        }
        Mexico = {
                "As It Was":1,
                "First Class":201,
                "Heat Waves":103,
                "STAY (with Justin Bieber)":201,
                "Enemy (with JID)":138,
                "Envolver":8,
                "Bam Bam (feat. Ed Sheeran)":142,
                "Cold Heart - PNAU Remix":34,
                "INDUSTRY BABY (feat. Jack Harlow":201,
                "abcdefu":201,
                "Una Noche en Medellín":5,
                "MIDDLE OF THE NIGHT":201,
                "Ghost":201,
                "MAMIII":12,
                "Desesperados":6
        }
        country_specific_ranks['Mexico'] = Mexico
        country_specific_ranks['United States'] = United_States
        placement_difference_catplot(country_specific_ranks, top_fifteen_daily)

if __name__ == '__main__':
    unittest.main(verbosity=2)