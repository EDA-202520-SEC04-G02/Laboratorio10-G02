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

from DataStructures.List import single_linked_list as lt
from DataStructures.List import array_list as al
from DataStructures.Stack import stack as st
from DataStructures.Queue import queue as q

import sys
import threading
from App import logic

"""
La vista se encarga de la interacción con el usuario.
Presenta el menu de opciones  y  por cada seleccion
hace la solicitud al controlador para ejecutar la
operación seleccionada.
"""

# ___________________________________________________
#  Variables
# ___________________________________________________


servicefile = 'bus_routes_14000.csv'
stopsfile = 'bus_stops.csv'
initialStation = None

# ___________________________________________________
#  Menu principal
# ___________________________________________________


def print_menu():
    print("\n")
    print("*******************************************")
    print("Bienvenido")
    print("1- Cargar información de buses de singapur") # Clase 1: Implementar digraph básico
    print("2- Encontrar las paradas más concurridas") # Casa 1: Implementar digraph completo
    print("3- Encontrar una ruta entre dos paradas (DFS)") # Casa 1: Implementar funcionalidad dfs
    print("4- Encontrar una ruta entre dos paradas (BFS)") # Clase 2: Implementar funcionalidad bfs
    print("5- Encontrar la ruta mínima entre dos paradas") # Casa 2: Implementar dijkstra
    print("6- Mostrar en un mapa la ruta mínima entre dos paradas") # Trabajo Complementario: Mostrar ruta con folium
    print("0- Salir")
    print("*******************************************")


def option_one(cont):
    print("\nCargando información de transporte de singapur ....")
    logic.load_services(cont, servicefile, stopsfile)
    numedges = logic.total_connections(cont)
    numvertex = logic.total_stops(cont)
    print('Numero de vertices: ' + str(numvertex))
    print('Numero de arcos: ' + str(numedges))
    print('El limite de recursion actual: ' + str(sys.getrecursionlimit()))
    
def option_two(cont):
    # TODO: Imprimir los resultados de la opción 2
    ...
    print("\nConsultando paradas más concurridas...\n")

    top5 = logic.get_most_concurrent_stops(cont)

    if lt.size(top5) == 0:
        print("No hay información disponible.")
        return

    print("=== TOP 5 PARADAS MÁS CONCURRIDAS ===")

    pos = 1
    node = top5["first"]

    while node is not None:
        data = node["info"]  # {"stop": ..., "degree": ...}
        print(f"{pos}. Paradero: {data['stop']}  →  {data['degree']} conexiones")
        pos += 1
        node = node["next"]

    print("======================================\n")


def option_three(cont):
    # TODO: Imprimir los resultados de la opción 3
    ...
    print("\n--- OPCIÓN 3 (DFS) ---")
    start = input("Parada inicial: ")
    goal = input("Parada destino: ")

    route = logic.get_route_between_stops_dfs(cont, start, goal)

    if route is None:
        print("No hay ruta DFS entre las paradas dadas.\n")
        return

    print("\nRuta DFS encontrada:")
    node = route["first"]
    while node is not None:
        print(node["info"], end=" -> ")
        node = node["next"]
    print("FIN\n")

def option_four(cont):
    # TODO: Imprimir los resultados de la opción 4

    print("\n--- OPCIÓN 4 (BFS) ---")
    start = input("Parada inicial: ")
    goal = input("Parada destino: ")

    
    path_list = logic.get_route_between_stops_bfs(cont, start, goal)

    if path_list is None or lt.size(path_list) == 0:
        print("No hay ruta BFS entre las paradas dadas.\n")
        return

    print("\n--- RUTA BFS ---\n")

    
    first_code = lt.get_element(path_list, 0)

    
    if "-" in first_code:
        first_stop, current_bus = first_code.split("-", 1)
    else:
        first_stop = first_code
        current_bus = "N/A"

    
    print(f"--- Tomar bus '{current_bus}' desde '{first_code}' ---")

    
    n = lt.size(path_list)
    for i in range(n):
        code = lt.get_element(path_list, i)   
        
        if "-" in code:
            stop, bus = code.split("-", 1)
        else:
            stop, bus = code, current_bus

        # Si cambia el bus
        if bus != current_bus:
            print(f"\n--- Cambiar a bus '{bus}' en la parada '{stop}' ---")
            current_bus = bus

        # Imprimir parada
        if i < n - 1:
            print(stop, end=" -> ")
        else:
            print(stop)

    print()

def option_five(cont):
    # TODO: Imprimir los resultados de la opción 5

    print("\n----- OPCIÓN 5 ----")
    start = input("Parada inicial: ").strip()
    goal = input("Parada destino: ").strip()

    
    path_list = logic.get_shortest_route_between_stops(cont, start, goal)

    
    if path_list is None:
        print("No hay ruta mínima entre las paradas dadas.\n")
        return

   

    
    codes = al.new_list()
    node = path_list["first"]
    while node is not None:
        al.add_last(codes, node["info"])
        node = node["next"]

    n = al.size(codes)
    if n == 0:
        print("No hay ruta mínima entre las paradas dadas.\n")
        return

    first_code = al.get_element(codes, n - 1)

    print(f"Origen: '{start}'")
    print(f"Destino: '{goal}'")

    
    if "-" in first_code:
        first_stop, current_bus = first_code.split("-", 1)
    else:
        first_stop = first_code
        current_bus = "N/A"

    print(f"--- Tomar bus '{current_bus}' desde '{first_code}' ---")

    
    idx = n - 1
    while idx >= 0:
        code = al.get_element(codes, idx)

        if "-" in code:
            stop, bus = code.split("-", 1)
        else:
            stop, bus = code, current_bus

        
        if bus != current_bus:
            print(f"\n--- Cambiar a bus '{bus}' en la parada '{stop}' ---")
            current_bus = bus

       
        if idx > 0:
            print(stop, end=" -> ")
        else:
            print(stop)

        idx -= 1

    print()  
    
    
def option_six(cont):
    # (Opcional) TODO: Imprimir los resultados de la opción 6
    ...


"""
Menu principal
"""


def main():
    working = True
    while working:
        print_menu()
        inputs = input('Seleccione una opción para continuar\n>')

        if int(inputs[0]) == 1:
            print("\nInicializando....")
            cont = logic.new_analyzer()
            option_one(cont)
        elif int(inputs[0]) == 2:
            option_two(cont)
        elif int(inputs[0]) == 3:
            option_three(cont)
        elif int(inputs[0]) == 4:
            option_four(cont)
        elif int(inputs[0]) == 5:
            option_five(cont)
        elif int(inputs[0]) == 6:
            option_six(cont)
        else:
            working = False
            print("Saliendo...")
    sys.exit(0)


if __name__ == "__main__":
    threading.stack_size(67108864)  # 64MB stack
    sys.setrecursionlimit(2 ** 20)
    thread = threading.Thread(target=main)
    thread.start()
