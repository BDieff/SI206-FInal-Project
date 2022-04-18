import os
import visualizations
import census
import global200
import spotify
import visualizations

# final_project.db is the dtabase name when we connect with sqlite3

if __name__ == '__main__':
    #try:
        #os.remove('final_project.db')
    #except:
        #pass
    # setting up db with data from census api
    y,z = census.setup_DB('final_project.db')
    x = census.get_data()
    census.create_table(y,z)
    census.json_to_db(x,y,z)
    country_list = ["United States", "United Kingdom", "Nigeria", "Mexico", "India"]
    country_id_list = census.get_country_ids(country_list,y,z)
    # adding artists, songs, and top x song data from spotifycharts
    BB200data = global200.get_global200()
    cur, conn = global200.setUpDatabase('final_project.db')
    global200.setUpArtistDatabase(BB200data, cur, conn)
    # adding tables to db with top x song data from spotify api
    spotify_api_mngr = spotify.SpotifyManager('final_project.db')
    spotify_api_mngr.get_songs(country_id_list)
    

