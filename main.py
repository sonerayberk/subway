""" Playing with Graph structure via networkx package.

    Data set: Station longitude & latitudes from Yandex.Metro
"""

import codecs
import json
import typing

import networkx as nx
import matplotlib.pyplot as plt


class Point(typing.NamedTuple):
    longitude: float
    latitude: float


data = json.loads(
    codecs.open('data/data.json', 'r', 'utf_8_sig').read()
)
l10n = json.loads(
    codecs.open('data/l10n.json', 'r', 'utf_8_sig').read()
)


NodeStationIdMapping = {}

for stop in data['stops']['items']:
    NodeStationIdMapping[stop['nodeId']] = stop['stationId']


NodeCoordinatesMapping = {}
for node in data['nodes']['items']:
    NodeCoordinatesMapping[node['id']] = Point(
        node['attributes']['geoPoint']['lon'],
        node['attributes']['geoPoint']['lat']
    )


latitudes = []
longitudes = []


for coordinate in NodeCoordinatesMapping.values():
    latitudes.append(coordinate.latitude)
    longitudes.append(coordinate.longitude)


for node_id, point in NodeCoordinatesMapping.items():
    NodeCoordinatesMapping[node_id] = (
        (point.longitude - min(longitudes)) / (max(longitudes)-min(longitudes)),
        (point.latitude - min(latitudes)) / (max(latitudes)-min(latitudes)),
    )


def get_station_name_from_node_id(node_id: str) -> typing.Optional[str]:
    station_id = NodeStationIdMapping[node_id]
    try:
        return l10n['keysets']['generated'][station_id + '-name']['ru']
    except KeyError:
        return None


G = nx.Graph()

StationCoordinatesMapping = {}

for node, point in NodeCoordinatesMapping.items():
    if node in NodeStationIdMapping:
        station = get_station_name_from_node_id(node)
        G.add_node(
            station,
            pos=point
        )
        StationCoordinatesMapping[station] = point


for link in data['links']['items']:
    if {
        link['fromNodeId'], 
        link['toNodeId']
    } <= set(NodeStationIdMapping.keys()):
        station1 = get_station_name_from_node_id(link['fromNodeId'])
        station2 = get_station_name_from_node_id(link['toNodeId'])
        G.add_edge(
            station1,
            station2,
            length=link['attributes']['time']
        )


if __name__ == '__main__':
    nx.draw(G, with_labels=True, pos=StationCoordinatesMapping, font_size=8)
    plt.show()
