import os
import json
from pkgutil import get_data
import sqlite3
import requests
import unittest


def setup_DB(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def get_data(year=2021):
    key = "b8e166b9af8ce6bb0efccbe04c65585b0cf05e16"
    base_url = f"http://api.census.gov/data/timeseries/idb/5year?get=NAME,POP,CBR,CDR,E0,AREA_KM2&YR={year}&key={key}"
    data1 = requests.get(base_url)
    data2 = data1.text
    data3 = json.loads(data2)
    return data3

def create_table(cur,conn):
    cur.execute('CREATE TABLE IF NOT EXISTS census_data (country_id INTEGER PRIMARY KEY, name TEXT, population INTEGER, crude_birth_rate INTEGER, crude_death_rate INTEGER, life_expectancy INTEGER, area INTEGER)')
    conn.commit()

def json_to_db(data,cur,conn):
    item_id = 0
    for item in data:
        var_id = item_id
        var_name = item[0]
        var_population = item[1]
        var_crude_birth_rate = item[2]
        var_crude_death_rate = item[3]
        var_life_expectancy = item[4]
        area = item[5]
        item_id += 1
        cur.execute("INSERT OR IGNORE INTO census_data (country_id, name,  population, crude_birth_rate, crude_death_rate, life_expectancy, area) VALUES (?,?,?,?,?,?,?)", (var_id, var_name,var_population,var_crude_birth_rate,var_crude_death_rate,var_life_expectancy,area))
    conn.commit()

def data_for_one_country(country, cur, conn):
    cur.execute(f"SELECT population FROM census_data WHERE name = \"{country}\"")
    res = cur.fetchall()
    conn.commit()
    out = [item for t in res for item in t]
    return out



def main():
    y,z = setup_DB("census_data")
    x = get_data()
    create_table(y,z)
    json_to_db(x,y,z)
    country_list = ["United States", "United Kingdom", "Nigeria", "Mexico", "India"]
    for country in country_list:
        data_for_one_country(country, y,z)
    

if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)
