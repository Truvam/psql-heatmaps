

import psycopg2


def db_connect(dbname, user):
    try:
        db = psycopg2.connect("dbname=" + dbname + " user=" + user + "")
        return db
    except psycopg2.OperationalError:
        print("ERROR:")
        print("Failed to connect to database.")
        print("Make sure you have postgresql service running.")


def db_query(db, query):
    cursor = db.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def db_print(result):
    for row in result:
        print(row[0], row[1])


def get_centroid(db):
    centroid_q = 'select st_y(st_transform(st_centroid(st_collect(location)), 4326)), ' \
                 'st_x(st_transform(st_centroid(st_collect(location)), ' \
                 '4326)) from taxi_stands;'
    centroid = db_query(db, centroid_q)
    centroid = centroid[0]
    return centroid


def get_taxi_stands(db):
    query = "select st_y(st_transform(location, 4326)), " \
            "st_x(st_transform(location, 4326)), name from taxi_stands;"

    result = db_query(db, query)
    return result


def get_taxi_services(db, limit=-1):
    query = "select st_y(st_transform(initial_point, 4326)), " \
            "st_x(st_transform(initial_point, 4326)) from taxi_services;"

    result = db_query(db, query)
    if limit == -1:
        return result
    else:
        return result[0:limit]


def get_taxi_services_count(db, locations):
    count = list()
    for x, y in locations:
        query = "select count(*) from taxi_services " \
                "where st_x(st_transform(initial_point, 3763)) >= " + str(x) + " and " \
                 "st_x(st_transform(final_point, 3763)) <= " + str(x) + " and " \
                 "st_y(st_transform(initial_point, 3763)) >= " + str(y) + " and " \
                 "st_y(st_transform(final_point, 3763)) <= " + str(y) + ""
        count.append(db_query(db, query)[0][0])
    return count


def get_freguesia_count(db, distrito, concelho):
    query1 = "select freguesia, count(*) from caop, taxi_services where " \
             "st_contains(geom, final_point) and distrito like '" + distrito + "' " \
             "and concelho like '" + concelho + "' group by 1 order by 2 desc;"
    query2 = "select distinct freguesia from caop where distrito like '" + distrito + "' " \
             "and concelho like '" + concelho + "';"
    result1 = db_query(db, query1)
    result2 = db_query(db, query2)

    for row2 in range(0, len(result2)):
        if result2[row2][0] not in [n1[0] for n1 in result1]:
            result1.append(tuple((result2[row2][0], 0)))
    
    return result1


def get_freguesia_locations(db, distrito, concelho, freguesia):
    query = "select st_x(st_astext((g).geom)), st_y(st_astext((g).geom)) " \
            "from (select st_dumpPoints(geom) as g from caop where " \
            "distrito like '" + distrito + "' and concelho like '" + concelho + "' " \
            "and freguesia like '" + freguesia + "') as a;"
    result = db_query(db, query)
    return result


def get_centroid_freguesia(db, distrito, concelho, freguesia):
    query = "select st_y(st_centroid(st_collect(geom))), st_x(st_centroid(st_collect(geom))) " \
            "from caop where distrito like '" + distrito + "' and concelho like '" + concelho + "' " \
            "and freguesia like '" + freguesia + "';"
    centroid = db_query(db, query)
    centroid = centroid[0]
    return centroid


def help():
    """
    Prints available functions currently available in this module.
    """
    print("   database.db_connect(dbname, user)")
    print("   database.db_query(db, query)")
    print("   database.db_print(result)")
    print("   database.get_centroid(db)")
    print("   database.get_taxi_stands(db)")
    print("   database.get_taxi_services(db, limit=-1)")
    print("   database.get_freguesia_count(db, distrito, concelho)")
    print("   database.get_freguesia_locations(db, distrito, concelho, freguesia)")
    print("   database.get_centroid_freguesia(db, distrito, concelho, "
          "freguesia)")
