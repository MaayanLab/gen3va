import json
import MySQLdb
import pymongo
from bson.objectid import ObjectId
from ConfigParser import ConfigParser


config = ConfigParser()
config.read('migrations/config.ini')


def main():
    heat_map_and_clustergrammer_ids = get_heat_map_and_clustergrammer_ids()
    ids_and_networks = get_networks_from_ids(heat_map_and_clustergrammer_ids)
    insert_networks(ids_and_networks)


def insert_networks(ids_and_networks):
    conn = gen3va_connect()
    cur = conn.cursor()
    for heat_map_id, network in ids_and_networks:
        network = json.dumps(network)
        sql = 'UPDATE heat_map ' \
              'SET network = %%s ' \
              'WHERE id = %s' % heat_map_id
        print(sql)
        cur.execute(sql, (network,))
    conn.commit()
    conn.close()


def get_networks_from_ids(ids):
    results = []
    host = config.get('mongodb', 'host')
    client = pymongo.MongoClient(host)
    for heat_map_id, clustergrammer_id in ids:
        cursor = client.clustergrammer.networks\
            .find({'_id': ObjectId(clustergrammer_id)})
        for r in cursor:
            network = r.get('viz')
            tpl = (heat_map_id, network)
            results.append(tpl)
        cursor.close()
    return results


def get_heat_map_and_clustergrammer_ids():
    conn = gen3va_connect()
    cur = conn.cursor()
    cur.execute('SELECT id FROM heat_map')
    heat_map_ids = []
    for row in cur.fetchall():
        heat_map_ids.append(row[0])
    heat_map_and_clustergrammer_ids = []
    counts = []
    for heat_map_id in heat_map_ids:
        sql = 'SELECT heat_map.link ' \
              'FROM heat_map ' \
              'WHERE id = %s'
        cur.execute(sql, (heat_map_id,))
        row = cur.fetchone()
        if row:
            link = row[0]
            if not link:
                continue
            clustergrammer_id = link\
                .replace('http://amp.pharm.mssm.edu/clustergrammer/gen3va/', '')\
                .replace('http://amp.pharm.mssm.edu/clustergrammer/viz/', '')\
                .split('/')[0]\
                .split('?')[0]
            counts.append(clustergrammer_id)
            heat_map_and_clustergrammer_ids.append(
                (heat_map_id, clustergrammer_id)
            )
    print(len(counts))
    conn.close()
    return heat_map_and_clustergrammer_ids


def gen3va_connect():
    return MySQLdb.connect(
        host=config.get('dev', 'host'),
        user=config.get('dev', 'user'),
        passwd=config.get('dev', 'passwd'),
        db=config.get('dev', 'db')
    )


if __name__ == '__main__':
    main()
