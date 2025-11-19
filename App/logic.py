"""
 * Copyright 2020, Departamento de sistemas y Computación
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * Contribución de:
 *
 * Dario Correal
 *
 """

# ___________________________________________________
#  Importaciones
# ___________________________________________________

from DataStructures.List import single_linked_list as lt
from DataStructures.List import array_list as al
from DataStructures.Map import map_linear_probing as m
from DataStructures.Graph import digraph as G
from DataStructures.Graph import dfs as DFS
from DataStructures.Stack import stack as st
from DataStructures.Queue import queue as q
from DataStructures.Priority_queue import priority_queue as pq

import csv
import time
import os

data_dir = os.path.dirname(os.path.realpath('__file__')) + '/Data/'


"""
El controlador se encarga de mediar entre la vista y el modelo.
Existen algunas operaciones en las que se necesita invocar
el modelo varias veces o integrar varias de las respuestas
del modelo en una sola respuesta.  Esta responsabilidad
recae sobre el controlador.
"""

# ___________________________________________________
#  Inicializacion del catalogo
# ___________________________________________________


def init():
    """
    Llama la funcion de inicializacion  del modelo.
    """
    # analyzer es utilizado para interactuar con el modelo
    analyzer = new_analyzer()
    return analyzer


def new_analyzer():
    """ Inicializa el analizador

   stops: Tabla de hash para guardar la información de las paradas
   connections: Grafo para representar las rutas entre estaciones
   paths: Estructura que almancena los caminos de costo minimo desde un
           vertice determinado a todos los otros vértices del grafo
    """
    try:
        analyzer = {
            'stops': None,
            'connections': None,
            'paths': None
        }

        analyzer['stops'] = m.new_map(
            num_elements=8000, load_factor=0.7, prime=109345121)

        analyzer['connections'] = G.new_graph(order=20000)
        return analyzer
    except Exception as exp:
        return exp

# ___________________________________________________
#  Funciones para la carga de datos y almacenamiento
#  de datos en los modelos
# ___________________________________________________


def load_services(analyzer, servicesfile, stopsfile):
    """
    Carga los datos de los archivos CSV en el modelo.
    Se crea un arco entre cada par de estaciones que
    pertenecen al mismo servicio y van en el mismo sentido.

    addRouteConnection crea conexiones entre diferentes rutas
    servidas en una misma estación.
    """
    stopsfile = data_dir + stopsfile
    stops_input_file = csv.DictReader(open(stopsfile, encoding="utf-8"),
                                      delimiter=",")

    for stop in stops_input_file:
        add_stop(analyzer, stop)

    servicesfile = data_dir + servicesfile
    input_file = csv.DictReader(open(servicesfile, encoding="utf-8"),
                                delimiter=",")
    lastservice = None
    for service in input_file:
        if not G.contains_vertex(analyzer['connections'], format_vertex(service)):
            add_stop_vertex(analyzer, format_vertex(service))
        add_route_stop(analyzer, service)

        if lastservice is not None:
            sameservice = lastservice['ServiceNo'] == service['ServiceNo']
            samedirection = lastservice['Direction'] == service['Direction']
            samebusStop = lastservice['BusStopCode'] == service['BusStopCode']
            if sameservice and samedirection and not samebusStop:
                add_stop_connection(analyzer, lastservice, service)

        add_same_stop_connections(analyzer, service)
        lastservice = service

    return analyzer

# ___________________________________________________
#  Funciones para consultas
# ___________________________________________________


def total_stops(analyzer):
    """
    Total de paradas de autobus en el grafo
    """
    return G.order(analyzer['connections'])


def total_connections(analyzer):
    """
    Total de enlaces entre las paradas
    """
    return G.size(analyzer['connections'])


# Funciones para la medición de tiempos

def get_time():
    """
    devuelve el instante tiempo de procesamiento en milisegundos
    """
    return float(time.perf_counter()*1000)


def delta_time(end, start):
    """
    devuelve la diferencia entre tiempos de procesamiento muestreados
    """
    elapsed = float(end - start)
    return elapsed


# Funciones para agregar informacion al grafo

def add_stop_connection(analyzer, lastservice, service):
    """
    Adiciona las estaciones al grafo como vertices y arcos entre las
    estaciones adyacentes.

    Los vertices tienen por nombre el identificador de la estacion
    seguido de la ruta que sirve.  Por ejemplo:

    75009-10

    Si la estacion sirve otra ruta, se tiene: 75009-101
    """
    try:
        origin = format_vertex(lastservice)
        destination = format_vertex(service)
        clean_service_distance(lastservice, service)
        distance = float(service['Distance']) - float(lastservice['Distance'])
        distance = abs(distance)
        add_connection(analyzer, origin, destination, distance)
        return analyzer
    except Exception as exp:
        return exp


def add_stop(analyzer, stop):
    """
    Adiciona una parada (BusStopCode) en los stops del sistema de transporte
    """
    stop['services'] = lt.new_list()
    m.put(analyzer['stops'], stop['BusStopCode'], stop)
    return analyzer

def add_stop_vertex(analyzer, stopid):
    """
    Adiciona una estación como un vertice del grafo
    """

    G.insert_vertex(analyzer['connections'], stopid, stopid)
    return analyzer

'''
def add_route_stop(analyzer, service):
    """
    Agrega a una estacion, una ruta que es servida en ese paradero
    """
    stop_info = m.get(analyzer['stops'], service['BusStopCode'])
    stop_services = stop_info['services']
    if lt.is_present(stop_services, service['ServiceNo'], lt.default_function) == -1:
        lt.add_last(stop_services, service['ServiceNo'])

    return analyzer
'''
def add_route_stop(analyzer, service):
    """
    Agrega a una estación una ruta servida en ese paradero.
    """
    stop_info = m.get(analyzer['stops'], service['BusStopCode'])
    stop_services = stop_info['services']

    # Función de comparación correcta para is_present
    cmp_fn = lambda a, b: 0 if a == b else 1

    if lt.is_present(stop_services, service['ServiceNo'], cmp_fn) == -1:
        lt.add_last(stop_services, service['ServiceNo'])

    return analyzer


def add_connection(analyzer, origin, destination, distance):
    """
    Adiciona un arco entre dos estaciones
    """

    G.add_edge(analyzer['connections'], origin, destination, distance)



def add_same_stop_connections(analyzer, service):
    stop_1 = format_vertex(service)
    stop_buses_lt = m.get(analyzer['stops'], service['BusStopCode'])['services']

    if lt.size(stop_buses_lt) > 1:
        pass

    node = stop_buses_lt['first']
    for _ in range(lt.size(stop_buses_lt)):
        stop_2 = format_vertex({'BusStopCode': service['BusStopCode'], 'ServiceNo': node['info']})
        if stop_1 != stop_2:
            add_connection(analyzer, stop_1, stop_2, 0)
        node = node['next']
    return analyzer


# ___________________________________________________
#  Funciones de resolución de requerimientos
# ___________________________________________________

def get_most_concurrent_stops(analyzer):
    graph = analyzer["connections"]

    # 1. Obtener todas las llaves de vértices (array_list)
    vkeys = G.vertices(graph)

    degree_list = lt.new_list()  # esta sí será single linked list

    # Recorrer array_list mediante índices
    for i in range(al.size(vkeys)):
        key = al.get_element(vkeys, i)
        deg = G.degree(graph, key)
        lt.add_last(degree_list, {"stop": key, "degree": deg})

    # 2. Ordenar usando merge_sort del curso (descendente)
    def cmp(a, b):
        return a["degree"] > b["degree"]

    degree_list = lt.merge_sort(degree_list, cmp)

    # 3. Tomar los 5 primeros
    top5 = lt.new_list()
    total = min(5, lt.size(degree_list))
    for i in range(total):
        lt.add_last(top5, lt.get_element(degree_list, i))

    return top5

def get_route_between_stops_dfs(analyzer, start, goal):
    """
    DFS especial para la opción 3:
    Construye el camino hasta encontrar el destino.
    """
    graph = analyzer["connections"]
    visited = set()
    path = lt.new_list()

    found = _dfs_path(graph, start, goal, visited, path)

    if found:
        return path
    else:
        return None


def _dfs_path(graph, current, goal, visited, path):
    visited.add(current)
    lt.add_last(path, current)

    if current == goal:
        return True

    adj = G.adjacents(graph, current)  # array_list de claves
    for i in range(al.size(adj)):
        nxt = al.get_element(adj, i)
        if nxt not in visited:
            if _dfs_path(graph, nxt, goal, visited, path):
                return True

    # Backtracking real: si no lleva al destino, retrocedemos
    path["last"] = path["last"]["prev"] if path["last"] else None
    return False


def get_route_between_stops_bfs(analyzer, stop1, stop2):
    """
    Obtener la ruta entre dos parada usando bfs
    """
    # TODO: Obtener la ruta entre dos parada usando bfs
    
    grafo = analyzer["connections"]

    # Validar existencia
    if not G.contains_vertex(grafo, stop1) or not G.contains_vertex(grafo, stop2):
        return None

    order = G.order(grafo)
    visited = m.new_map(order, 0.7)
    parent = m.new_map(order, 0.7)

    cola = q.new_queue()

    # Inicialización
    q.enqueue(cola, stop1)
    visited = m.put(visited, stop1, True)

    found = False

    
    while not q.is_empty(cola) and not found:
        u = q.dequeue(cola)

        
        if u == stop2:
            found = True

        adj = G.adjacents(grafo, u)
        deg = al.size(adj)

        
        if not found:
            for i in range(deg):
                v = al.get_element(adj, i)

                if not m.contains(visited, v):
                    visited = m.put(visited, v, True)
                    parent = m.put(parent, v, u)
                    q.enqueue(cola, v)

    if not found:
        return None

    
    caminho_stack = st.new_stack()
    actual = stop2
    while actual is not None:
        st.push(caminho_stack, actual)
        actual = m.get(parent, actual)

    path = lt.new_list()
    while not st.is_empty(caminho_stack):
        lt.add_last(path, st.pop(caminho_stack))

    return path

def get_shortest_route_between_stops(analyzer, stop1, stop2):
    """
    Obtener la ruta mínima entre dos paradas
    """
    # TODO: Obtener la ruta mínima entre dos paradas
    # Nota: Tenga en cuenta que el debe guardar en la llave
    #       analyzer['paths'] el resultado del algoritmo de Dijkstra
    
    grafo = analyzer["connections"]

    
    if not G.contains_vertex(grafo, stop1) or not G.contains_vertex(grafo, stop2):
        analyzer["paths"] = None
        return None

    order = G.order(grafo)

    dist = m.new_map(order, 0.7)
    prev = m.new_map(order, 0.7)

    INF = float("inf")

    
    vertices = G.vertices(grafo)
    n = al.size(vertices)

    for i in range(n):
        v = al.get_element(vertices, i)
        dist = m.put(dist, v, INF)
        prev = m.put(prev, v, None)

    dist = m.put(dist, stop1, 0.0)

    
    heap = pq.new_heap(is_min_pq=True)
    pq.insert(heap, 0.0, stop1)

    found = False

    
    while not pq.is_empty(heap) and not found:

        u = pq.remove(heap)
        du = m.get(dist, u)

        
        if u == stop2:
            found = True

       
        if du != INF and not found:

            adj = G.adjacents(grafo, u)
            edge_map = G.edges_vertex(grafo, u)
            deg = al.size(adj)

            i = 0
            while i < deg:
                v = al.get_element(adj, i)
                edge = m.get(edge_map, v)

                
                if edge is not None:
                    w = edge["weight"]
                    alt = du + w
                    dv = m.get(dist, v)

                    if alt < dv:
                        dist = m.put(dist, v, alt)
                        prev = m.put(prev, v, u)

                        if pq.contains(heap, v):
                            pq.improve_priority(heap, v, alt)
                        else:
                            pq.insert(heap, alt, v)

                i += 1

    analyzer["paths"] = {
        "source": stop1,
        "dist": dist,
        "prev": prev
    }

    final_dist = m.get(dist, stop2)
    if final_dist == INF:
        return None

    
    caminho_stack = st.new_stack()
    actual = stop2
    while actual is not None:
        st.push(caminho_stack, actual)
        actual = m.get(prev, actual)

    path = lt.new_list()
    while not st.is_empty(caminho_stack):
        lt.add_last(path, st.pop(caminho_stack))

    return path, final_dist

def show_calculated_shortest_route(analyzer, destination_stop):
    # (Opcional) TODO: Mostrar en un mapa la ruta mínima entre dos paradas usando folium
    ...




# ___________________________________________________
# Funciones Helper
# ___________________________________________________

def clean_service_distance(lastservice, service):
    """
    En caso de que el archivo tenga un espacio en la
    distancia, se reemplaza con cero.
    """
    if service['Distance'] == '':
        service['Distance'] = 0
    if lastservice['Distance'] == '':
        lastservice['Distance'] = 0


def format_vertex(service):
    """
    Se formatea el nombrer del vertice con el id de la estación
    seguido de la ruta.
    """
    name = service['BusStopCode'] + '-'
    name = name + service['ServiceNo']
    return name
