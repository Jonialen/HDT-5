import random
import simpy
import numpy as np
import csv
import os

np.random.seed(10)
random.seed(10)

PROCESOS = (25, 50, 100, 150, 200)
lista_tiempos = []
MAX_RAM = 100
MAX_CPU = 1
MAX_PROCESS = 3
INTERVAL = 10


class Proceso:
    def __init__(self, name, env, ram, cpu, data):
        self.env = env
        self.name = name
        self.instrucciones = data[0]
        self.ram = ram
        self.cpu = cpu
        self.memoria = data[1]
        self.hora_inicio = None
        self.hora_fin = None

    def run(self):
        print(f"{self.hora_inicio} Inicia proceso {self.name}.")
        # Solicita memoria
        ram = self.get_ram()
        # espera por memoria
        yield ram
        # solicita cpu
        while self.instrucciones > 0:
            with self.cpu.request() as cpu:
                self.hora_inicio = self.env.now
                yield cpu
                # ejecuta sus instrucciones
                for _ in range(min(MAX_PROCESS, self.instrucciones)):
                    self.instrucciones -= 1
                    print(self.name, self.instrucciones)
                    if self.instrucciones == 0:
                        break
                yield self.env.timeout(random.expovariate(1.0 / INTERVAL))
        self.put_ram()
        self.hora_fin = self.env.now
        print("Termino")

    def get_ram(self):
        return self.ram.get(self.memoria)

    def put_ram(self):
        self.ram.put(self.memoria)


def crear_procesos(env, ram, cpu, max_num, lista_procesos):
    for i in range(max_num):
        print(f"{env.now} -- {i}")
        name = f"Proceso({i})"
        # ram/processos
        data = [np.random.randint(1, 10), np.random.randint(1, 10)]
        new_process = Proceso(name, env, ram, cpu, data)
        env.process(new_process.run())  # yield the process
        lista_procesos.append(new_process)


for proceso in PROCESOS:
    env = simpy.Environment()
    ram_total = simpy.Container(env, capacity=MAX_RAM, init=MAX_RAM)
    cpu_total = simpy.Resource(env, capacity=MAX_CPU)
    print("Llamada a simular")

    lista_procesos = []
    crear_procesos(env, ram_total, cpu_total, proceso, lista_procesos)
    env.run()
    lista_tiempos.append(lista_procesos)

n = -1
for lista_procesos in lista_tiempos:
    n += 1
    for proceso in lista_procesos:
        print(
            f"Con {PROCESOS[n]}: {proceso.hora_inicio} -- {proceso.hora_fin} -- {proceso.hora_fin-proceso.hora_inicio}")


# Define el nombre base del archivo CSV
nombre_base_archivo = 'tiempos_procesos.csv'

# Inicializar un contador para agregar un número al nombre del archivo en caso de existir
contador = 0
nombre_archivo = nombre_base_archivo

# Verificar si el archivo ya existe y cambiar el nombre si es necesario
while os.path.exists(nombre_archivo):
    contador += 1
    nombre_archivo = f"{nombre_base_archivo.split('.')[0]}_{contador}.csv"

# Abrir el archivo CSV en modo de escritura
with open(nombre_archivo, mode='w', newline='') as file:
    writer = csv.writer(file)

    # Escribir la cabecera del archivo CSV
    writer.writerow(['Cantidad de Procesos', 'Hora de Inicio', 'Hora de Fin'])

    # Escribir los datos de cada proceso en el archivo CSV
    for i, lista_procesos in enumerate(lista_tiempos):
        for proceso in lista_procesos:
            writer.writerow(
                [PROCESOS[i], proceso.hora_inicio, proceso.hora_fin])

print(f"Los datos se han exportado correctamente en '{nombre_archivo}'.")
