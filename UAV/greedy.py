import argparse

class UAVManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.uav_data = []
        self.total_cost = 0
        self.read_file()
        self.solve_greedy()

    def read_file(self):
        with open(self.file_path, 'r') as file:
            lines = file.readlines()
            D = int(lines[0].strip())
            current_line = 1

            for _ in range(D):
                aterrizaje_info = list(map(float, lines[current_line].strip().split()))
                uav = {
                    'tiempo_aterrizaje_menor': aterrizaje_info[0],
                    'tiempo_aterrizaje_ideal': aterrizaje_info[1],
                    'tiempo_aterrizaje_maximo': aterrizaje_info[2],
                    'tiempos_aterrizaje': [],
                    'orden': 0 
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
    
    def solve_greedy(self):
        sorted_uav_data = sorted(self.uav_data, key=lambda x: x['tiempo_aterrizaje_ideal'])

        for i, uav in enumerate(sorted_uav_data):
            menor = uav['tiempo_aterrizaje_menor']
            ideal = uav['tiempo_aterrizaje_ideal']
            maximo = uav['tiempo_aterrizaje_maximo']
            tiempos_aterrizaje = uav['tiempos_aterrizaje']

            best_time = None
            best_penalty = float('inf')
            for tiempo in tiempos_aterrizaje:
                if menor <= tiempo <= maximo:
                    penalty = abs(tiempo - ideal)
                    if penalty < best_penalty:
                        best_time = tiempo
                        best_penalty = penalty

            if best_time is not None:
                self.total_cost += best_penalty
                uav['orden'] = i + 1

    def display_data(self):
        for uav in self.uav_data:
            print(f"UAV orden {uav['orden']}:", uav)
        print("Costo total:", self.total_cost)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimizar el orden de aterrizaje de UAVs.")
    parser.add_argument("file_path", type=str, help="Ruta del archivo de datos de los UAVs")
    args = parser.parse_args()

    uav_manager = UAVManager(args.file_path)
    uav_manager.display_data()
