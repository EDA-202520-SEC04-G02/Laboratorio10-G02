from DataStructures.Graph import digraph as G
from DataStructures.Map import map_linear_probing as map
from DataStructures.Queue import queue as q
from DataStructures.Stack import stack as st
from DataStructures.List import single_linked_list as lt


def bfs(my_graph, source):
   
    # Crear el mapa de visitados con capacidad acorde al orden del grafo
    visited_map = map.new_map(
        num_elements=G.order(my_graph),
        load_factor=0.5
    )

    # Inicializar el vértice origen
    map.put(visited_map, source, {
        "edge_from": None,
        "dist_to": 0
    })

    # Delegar el recorrido a bfs_vertex
    visited_map = bfs_vertex(my_graph, source, visited_map)

    return visited_map




def bfs_vertex(my_graph, source, visited_map):
    
    
    to_visit = q.new_queue()
    q.enqueue(to_visit, source)

    
    while not q.is_empty(to_visit):
        v = q.dequeue(to_visit)

        
        v_info = map.get(visited_map, v)
        dist_v = v_info["dist_to"]

        
        adj_vertices = G.adjacents(my_graph, v)

        
        for w in adj_vertices:
            if not map.contains(visited_map, w):
                map.put(visited_map, w, {
                    "edge_from": v,
                    "dist_to": dist_v + 1
                })
                q.enqueue(to_visit, w)

    return visited_map



def has_path_to(key_v, visited_map):
    
    return map.contains(visited_map, key_v)



def path_to(key_v, visited_map):
    
    
    # Si no hay camino, retornamos None
    if not has_path_to(key_v, visited_map):
        return None

    # Pila para almacenar el camino
    path_stack = st.new_stack()

    # Reconstruir el camino desde key_v hacia atrás usando edge_from
    current = key_v
    while current is not None:
        st.push(path_stack, current)
        info = map.get(visited_map, current)
        current = info["edge_from"]

    return path_stack