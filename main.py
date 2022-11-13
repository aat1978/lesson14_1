import json
import sqlite3
import flask


def run_sql(_sql):
    with sqlite3.connect("netflix.db") as connection:
        connection.row_factory = sqlite3.Row
        return connection.execute(_sql).fetchall()


app = flask.Flask(__name__)


@app.get("/movie/<title>")
def search_by_name(title):
    """
    поиск по названию
    :param title:
    :return:
    """
    _sql = f'''SELECT title, country, release_year, listed_in as genre, description
               FROM netflix 
               WHERE title='{title}'
               ORDER BY date_added desc
               LIMIT 1'''
    result = None
    for item in run_sql(_sql=_sql):
        result = dict(item)
    return flask.jsonify(result)
#    return app.response_class(json.dumps(result, ensure_ascii=False, indent=4), mimetypes="application/json")


@app.get("/movie/<int:year_min>/to/<int:year_max>")
def search_by_release_year(year_min, year_max):
    """
    поиск по диапазону лет выпуска
    :param year_max:
    :param year_min:
    :return:
    """
    _sql = f'''
        SELECT title, release_year
        FROM netflix 
        WHERE release_year BETWEEN {year_min} AND {year_max}
        LIMIT 100
    '''
    result = []
    for item in run_sql(_sql=_sql):
        result.append(dict(item))
    return flask.jsonify(result)
#    return app.response_class(json.dumps(result, ensure_ascii=False), mimetypes="application/json")


@app.get("/rating/<rating>")
def search_by_rating(rating):
    """
    поиск по рейтингу
    :param rating:
    :return:
    """
    my_dict = {
        "children": ("G", "G"),
        "family": ("G", "PG", "PG-13"),
        "adult": ("R", "NC-17")
    }
    sql = f'''SELECT title, rating, description 
               FROM netflix 
               WHERE rating in {my_dict.get(rating, ('PG-B', 'NC-17'))}
            '''
    return flask.jsonify(run_sql(sql))


@app.get("/genre/<genre>")
def search_by_genre(genre):
    """
    поиск по жанру
    :param genre:
    :return:
    """
    sql = f'''SELECT * 
              FROM netflix
              WHERE listed_in LIKE '%{genre.title()}%'
              ORDER BY release_year desc
              LIMIT 10
            '''
    return flask.jsonify(run_sql(sql))


def search_by_actors(name1='Rose McIver', name2='Ben Lamp'):
    """
    функция, которая получает в качестве аргумента имена двух актеров
    :return:
    """
    sql = f'''
        SELECT "cast" 
        FROM netflix
        WHERE "cast" like '%{name1}%' and "cast" like '%{name2}%'
    '''
    result = run_sql(sql)

    main_name = {}
    for item in result:
        names = item.get('cast').split(", ")
        for name in names:
            if name in main_name.keys():
                main_name[name] += 1
            else:
                main_name = 1
    for item in main_name:
        if item not in (name1, name2) and main_name[item] >= 2:
            result.append(item)
    return result


def type_film(types='TV Show', release_year=2021, genre='TV'):
    """
    функция, с помощью которой можно будет передавать тип картины
    :return:
    """
    sql = f'''
        SELECT *
        FROM netflix 
        WHERE type = '{types}' 
        and release_year = '{release_year}'
        and listed_in like '%{genre}%'
    '''

    return json.dumps(run_sql(sql), indent=4, ensure_ascii=False)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=True)
#    print(search_by_genre('R'))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
