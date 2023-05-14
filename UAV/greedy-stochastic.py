import argparse
import numpy as np
import matplotlib.pyplot as plt
import time 

class UAVManager:
    def __init__(self, file_path, seed):
        self.file_path = file_path
        self.seed = seed
        self.uav_data = []
        self.total_cost = 0
        self.read_file()
        self.solve_greedy_stochastic()

    def read_file(self):
        with open(self.file_path, 'r') as file:
            lines = file.readlines()
            D = int(lines[0].strip())
            current_line = 1

            for i in range(D):
                aterrizaje_info = list(map(float, lines[current_line].strip().split()))
                uav = {
                    'index': i,
                    'tiempo_aterrizaje_menor': aterrizaje_info[0],
                    'tiempo_aterrizaje_ideal': aterrizaje_info[1],
                    'tiempo_aterrizaje_maximo': aterrizaje_info[2],
                    'tiempos_aterrizaje': [],
                    'orden': None 
                }
                current_line += 1
                
                tiempos_aterrizaje = []
                while len(tiempos_aterrizaje) < D:
                    tiempos = list(map(float, lines[current_line].strip().split()))
                    tiempos_aterrizaje.extend(tiempos)
                    current_line += 1
                    
                uav['tiempos_aterrizaje'] = tiempos_aterrizaje
                self.uav_data.append(uav)

    """ 
    Ordenar los UAVs por su tiempo de aterrizaje preferente (tiempo_aterrizaje_ideal) en orden ascendente. De esta manera, nos aseguramos de que los UAVs con tiempos preferentes más cortos sean atendidos primero.
    Para cada UAV, intentar asignar el tiempo de aterrizaje lo más cercano posible al tiempo preferente sin violar los límites de tiempo mínimo y máximo. Al hacer esto, minimizamos las penalizaciones por unidad de tiempo sobre o bajo el tiempo preferente.
    Calcular el costo total sumando las penalizaciones por unidad de tiempo sobre o bajo el tiempo preferente para todos los UAVs.
    """

    def solve_greedy_stochastic(self):
        # Establecer la semilla para la generación de números aleatorios
        rng = np.random.default_rng(self.seed)

        # Ordenar los UAVs por su tiempo de aterrizaje ideal en orden ascendente
        sorted_uav_data = sorted(self.uav_data, key=lambda x: x['tiempo_aterrizaje_ideal'])

        # Inicializar variables
        self.total_cost = 0
        time = 0

        # Iterar sobre los UAVs
        for i in range(len(self.uav_data)):
            # Obtener el valor mínimo entre la longitud de la lista ordenada y un número fijo (p. ej., 3)
            k = min(len(sorted_uav_data), 3)

            # Crear una distribución de probabilidad exponencial para favorecer a los primeros UAVs
            probabilities = [np.exp(-0.5 * j) for j in range(k)]
            probabilities = [p / sum(probabilities) for p in probabilities]

            # Seleccionar uno de los k UAVs más cercanos al tiempo ideal actual
            idx = rng.choice(range(k), p=probabilities)
            selected_uav = sorted_uav_data.pop(idx)

            # Encontrar el tiempo de aterrizaje más cercano al tiempo ideal sin violar los límites de tiempo mínimo y máximo
            closest_time = max(selected_uav['tiempo_aterrizaje_menor'], min(selected_uav['tiempo_aterrizaje_maximo'], max(time, selected_uav['tiempo_aterrizaje_ideal'])))

            # Calcular la penalización asociada a este tiempo de aterrizaje
            penalty = abs(closest_time - selected_uav['tiempo_aterrizaje_ideal'])

            # Actualizar el tiempo de aterrizaje asignado y la penalización para este UAV
            selected_uav['tiempo_aterrizaje_asignado'] = closest_time
            selected_uav['penalizacion'] = penalty

            # Actualizar el costo total y el tiempo actual
            self.total_cost += penalty
            time = closest_time + selected_uav['tiempos_aterrizaje'][i]

            # Asignar el orden de aterrizaje
            selected_uav['orden'] = i


    def display_data(self):
        print("Costo total:", self.total_cost)
        sorted_uav_data = sorted(self.uav_data, key=lambda uav: uav['orden'])
        print("Orden de aterrizaje:", [uav['index'] for uav in sorted_uav_data])

    def plot_schedule(self):
        fig, ax = plt.subplots()

        for uav in self.uav_data:
            y = uav['orden']
            
            # Dibujar puntos en el tiempo minimo, tiempo ideal, tiempo maximo y tiempo de aterrizaje asignado
            ax.plot(uav['tiempo_aterrizaje_menor'], y, marker='o', markersize=6, color='red')
            ax.plot(uav['tiempo_aterrizaje_ideal'], y, marker='o', markersize=6, color='green')
            ax.plot(uav['tiempo_aterrizaje_maximo'], y, marker='o', markersize=6, color='blue')
            ax.plot(uav['tiempo_aterrizaje_asignado'], y, marker='o', markersize=8, color='black')
            
            # Mostrar los valores del tiempo minimo, tiempo ideal, tiempo maximo y tiempo de aterrizaje asignado
            ax.text(uav['tiempo_aterrizaje_menor'], y, f"{uav['tiempo_aterrizaje_menor']:.1f}", ha='right', va='bottom', color='red')
            ax.text(uav['tiempo_aterrizaje_ideal'], y, f"{uav['tiempo_aterrizaje_ideal']:.1f}", ha='right', va='bottom', color='green')
            ax.text(uav['tiempo_aterrizaje_maximo'], y, f"{uav['tiempo_aterrizaje_maximo']:.1f}", ha='left', va='bottom', color='blue')
            ax.text(uav['tiempo_aterrizaje_asignado'], y, f"{uav['tiempo_aterrizaje_asignado']:.1f}", ha='left', va='bottom', color='black')

        ax.set_xlabel('Tiempo')
        ax.set_ylabel('Orden de aterrizaje')
        ax.set_title('Programacion de aterrizaje de UAVs')
        plt.tight_layout()
        plt.show()

    def test_rng(self):
        rng = np.random.default_rng(self.seed)
        print(rng.choice(range(3), p=[0.1, 0.2, 0.7], size=10))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimizar el orden de aterrizaje de UAVs.")
    parser.add_argument("file_path", type=str, help="Ruta del archivo de datos de los UAVs")
    parser.add_argument("--seed", type=int, default=0, help="Semilla para la generacion de numeros aleatorios")

    """ Quiero un flag booleano que permita explorar distintas semillas para encontrar la mejor solución. """
    parser.add_argument("--explore", action="store_true", help="Explorar distintas semillas para encontrar la mejor solucion")
    parser.add_argument("--range", type=int, default=1000, help="Rango de semillas a explorar")
    args = parser.parse_args()

    """  
    La semilla influye en los resultados al controlar la secuencia de números aleatorios utilizada en el proceso de selección de UAVs,
    lo que a su vez afecta la solución encontrada por el algoritmo estocástico.
      Al cambiar la semilla, es posible explorar diferentes soluciones y encontrar aquellas que sean más adecuadas para el problema en cuestión. """
    

    if (args.explore):
        # Iterar sobre un rango de semillas

        seeds = range(args.range)
        results = []

        for seed in seeds:
            uav_manager = UAVManager(args.file_path, seed)
            results.append({
                'seed': seed,
                'total_cost': uav_manager.total_cost,
                'uav_data': uav_manager.uav_data
            })


        sorted_results = sorted(results, key=lambda x: x['total_cost'])
        # Muestra las 5 semillas que generaron los costos totales más bajos
        for i in range(5):
            print(f"Semilla: {sorted_results[i]['seed']}, Costo total: {sorted_results[i]['total_cost']}")

        # También puedes seleccionar y mostrar otras semillas de interés
        # Por ejemplo, podrías mostrar la semilla que generó el costo total más alto
        print(f"Semilla con el costo más alto: {sorted_results[-1]['seed']}, Costo total: {sorted_results[-1]['total_cost']}")

        # O la semilla que generó el costo total mediano
        median_index = len(sorted_results) // 2
        print(f"Semilla con el costo mediano: {sorted_results[median_index]['seed']}, Costo total: {sorted_results[median_index]['total_cost']}")


        """
        Spoilers (rango 0 al 5000):
            - Titan.txt: La mejor semilla es 291 con un costo total de 165.0
            - Deimos.txt: La mejor semilla es 3556 con un costo total de 14190.0
            - Europa.txt La mejor semilla es 1072 con un costo total de 2547.0
        """

    else:
        start_time = time.time()
        uav_manager = UAVManager(args.file_path, args.seed)
        end_time = time.time()
        print(f"Tiempo de ejecucion: {end_time - start_time:.4f} segundos")
        uav_manager.display_data()
        uav_manager.plot_schedule()
