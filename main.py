import os
import visualizations
import sqlite3
import census
import global200
import spotify
import visualizations

# final_project.db is the dtabase name when we connect with sqlite3

if __name__ == '__main__':
    y,z = census.setup_DB('final_project.db')
    x = census.get_data()
    census.create_table(y,z)
    census.json_to_db(x,y,z)
    pulled_all_from_census = census.db_full_bool(y)
    # adding artists, songs, and top x song data from billboard
    BB200data = global200.get_global200()
    bbcur, bbconn = global200.setUpDatabase('final_project.db')
    global200.setUpArtistDatabase(BB200data, bbcur, bbconn)
    pulled_all_from_bboard = global200.api_limit(bbcur,bbconn)
    # adding tables to db with top x song data from spotify api
    if pulled_all_from_census and pulled_all_from_bboard:
        country_list = ["United States", "United Kingdom", "Nigeria", "Mexico", "India"]
        country_id_list = census.get_country_ids(country_list,y,z)
        spotify_api_mngr = spotify.SpotifyManager('final_project.db')
        spotify_api_mngr.get_songs(country_id_list)
        conn = sqlite3.connect('final_project.db')
        cur = conn.cursor()
        num_spotify_api_songs = cur.execute('SELECT MAX(rank) FROM top_songs').fetchone()[0]
        if num_spotify_api_songs >= 20:
            #visualization code here
            temp_dict, num_songs_tempo = spotify_api_mngr.get_avg_tempo_by_country(country_id_list)
            visualizations.avg_temp_hbar(temp_dict, num_songs_tempo)
            country_pop_dict = census.pop_dict(country_id_list, y, z)
            listen_time_dict, num_songs_listen_time = spotify_api_mngr.get_total_stream_time_for_top(country_id_list)
            visualizations.minutes_per_person_hbar(listen_time_dict, country_pop_dict, num_songs_listen_time)
            #visualizations.last_visualization
        else:
            print('Not enough data pulled from Spotify Api yet - please run again...')
    else:
        print('Not enough data to pull from Spotify Api yet - please run again...')
    

