from lib2to3.pytree import generate_matches
import os
import json
from pkgutil import get_data
import sqlite3
from unicodedata import name
from webbrowser import get
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
    try:
        cur.execute('SELECT country_id FROM census_data WHERE country_id  = (SELECT MAX(country_id) FROM census_data)')
        start = cur.fetchone()
        start = start[0]
    except:
        start= 0
    item_id = 1
    for item in data[start:start+25]:
        var_id = item_id+start
        var_name = item[0]
        var_population = item[1]
        var_crude_birth_rate = item[2]
        var_crude_death_rate = item[3]
        var_life_expectancy = item[4]
        area = item[5]
        cur.execute("INSERT OR IGNORE INTO census_data (country_id, name,  population, crude_birth_rate, crude_death_rate, life_expectancy, area) VALUES (?,?,?,?,?,?,?)", (var_id, var_name,var_population,var_crude_birth_rate,var_crude_death_rate,var_life_expectancy,area))
        item_id += 1
    conn.commit()



def get_country_ids(country_list, cur, conn):
    country_ids_list = []
    for country in country_list:
        cur.execute(f"SELECT country_id FROM census_data WHERE name = \"{country}\"")
        res = cur.fetchall()[0][0]
        country_ids_list.append(res)
    conn.commit()
    return country_ids_list

def get_country_populations(country_list, cur, conn):
    country_populations_list = []
    for country in country_list:
        cur.execute(f"SELECT population FROM census_data WHERE name = \"{country}\"")
        res = cur.fetchall()[0][0]
        country_populations_list.append(res)
    conn.commit()
    return country_populations_list

def pop_dict(id_list, cur, conn):
    name_pop_dict = {}
    for x in id_list:
        cur.execute(f"SELECT name, population FROM census_data WHERE country_id = \"{x}\"")
        res = cur.fetchall()
        country = (res[0][0])
        population = (res[0][1])
        name_pop_dict[country] = population
    conn.commit()
    return name_pop_dict

def extra_credit(y,z):
    base_url = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?date=2020&format=json"
    data1 = requests.get(base_url)
    data2 = data1.text
    data3 = json.loads(data2)
    y.execute('CREATE TABLE IF NOT EXISTS mean_consumption (id INTEGER PRIMARY KEY, country TEXT, gdp INTEGER)')
    z.commit()
    item_id = 0
    for item in data3[1]:
        var_id = item_id
        var_country = item["country"]["value"]
        var_gdp = item["value"]
        item_id += 1
        y.execute("INSERT OR IGNORE INTO mean_consumption (id, country, gdp) VALUES (?,?,?)", (var_id, var_country,var_gdp,))
    z.commit()
    y.execute("SELECT gdp FROM mean_consumption")
    res = y.fetchall()
    total = 0
    count = 0
    for x in res:
        total_temp = x[0]
        if total_temp:
            total += total_temp
            count += 1
    average_gdp = total / count
    return average_gdp

def db_full_bool(cur):
    cur.execute('SELECT country_id FROM census_data WHERE country_id  = (SELECT MAX(country_id) FROM census_data)')
    start = cur.fetchone()
    start = start[0]
    if start >= 200:
        return True

        



def main():
    y,z = setup_DB("census_data")
    x = get_data()
    create_table(y,z)
    json_to_db(x,y,z)
    country_list = ["United States", "United Kingdom", "Nigeria", "Mexico", "India"]
    get_country_ids(country_list,y,z)
    get_country_populations(country_list,y,z)
    id_list = [209, 68, 148, 142, 92]
    pop_dict(id_list, y, z)
    a,b = setup_DB("mean_consumption")
    final = extra_credit(a,b)
    print(final)
    db_full_bool(y)


    
    
    
    

if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)
