import random as rm
from collections import deque
from naipe import Naipe, palo, numero
from jugadores import Jugador
import os
import unicodedata

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def pausar():
    input("Presiona Enter para continuar...")

def normalizar_carta(texto):
    # Quitar tildes y pasar a minúsculas
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto.lower()) if unicodedata.category(c) != 'Mn')
    # Normalizar variantes de palos
    reemplazos = {
        'trebol': 'treboles', 'treboles': 'treboles', 'trevoles': 'treboles', 'trebols': 'treboles',
        'pica': 'picas', 'picas': 'picas',
        'corazon': 'corazones', 'corazones': 'corazones',
        'diamante': 'diamantes', 'diamantes': 'diamantes',
    }
    partes = texto.split(' de ')
    if len(partes) == 2:
        valor, palo = partes
        palo = palo.strip()
        for k, v in reemplazos.items():
            if palo.startswith(k):
                palo = v
                break
        return f"{valor.strip()} de {palo}"
    return texto.strip()

class ColaNaipes:
    def __init__(self):
        self.mazo = deque()
    
    def _intercambio_direccional(self, jugadores):
        """
        Intercambio obligatorio simultáneo y direccional.
        Cada jugador elige una carta y la pasa a su vecino (derecha/izquierda).
        Las cartas recibidas no se muestran hasta que comience el juego.
        """
        if len(jugadores) < 2:
            return

        # Elegir dirección del pase
        limpiar_pantalla()
        print("Intercambio obligatorio: elige la dirección del pase")
        print("1. Derecha (al siguiente jugador)")
        print("2. Izquierda (al jugador anterior)")
        opcion = input("Opción (1/2, por defecto 1): ").strip()
        derecha = True if opcion != '2' else False

        # Recoger elecciones sin aplicar aún los pases
        elecciones = [None] * len(jugadores)
        for i, jugador in enumerate(jugadores):
            while True:
                try:
                    limpiar_pantalla()
                    vecino_idx = (i + 1) % len(jugadores) if derecha else (i - 1) % len(jugadores)
                    nombre_vecino = jugadores[vecino_idx].nombre
                    print(f"{jugador.nombre}, selecciona una carta para pasar a {nombre_vecino}:")
                    print(f"Tu mazo: {jugador.mano_cartas[0]}")
                    entrada = input("Escribe la carta (ej: 'A de Picas'): ")
                    carta_norm = normalizar_carta(entrada)
                    carta = next((c for c in jugador.mano_cartas[0] if normalizar_carta(str(c)) == carta_norm), None)
                    if carta is None:
                        print("Carta no válida. Intenta de nuevo.")
                        pausar()
                        continue
                    elecciones[i] = carta
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    pausar()

        # Aplicar pases simultáneamente: primero quitar, luego entregar
        for i, jugador in enumerate(jugadores):
            carta = elecciones[i]
            if carta in jugador.mano_cartas[0]:
                jugador.mano_cartas[0].remove(carta)
        for i in range(len(jugadores)):
            carta = elecciones[i]
            receptor_idx = (i + 1) % len(jugadores) if derecha else (i - 1) % len(jugadores)
            jugadores[receptor_idx].mano_cartas[0].append(carta)

        # Mensaje final sin revelar cartas recibidas
        limpiar_pantalla()
        lado = 'derecha' if derecha else 'izquierda'
        print(f"Intercambio completado hacia la {lado}. Las cartas recibidas permanecerán ocultas hasta el inicio del juego.")
        pausar()
    
    def generar_mazo(self):
        """Genera un mazo completo de 52 cartas."""
        self.mazo = deque([Naipe(p, n) for p in palo for n in numero])
    
    def revolver_mazo(self):
        """Revuelve el mazo."""
        mazo_list = list(self.mazo)  # Convertimos la cola en una lista para mezclar
        rm.shuffle(mazo_list)
        self.mazo = deque(mazo_list)  # Volvemos a convertirlo en una cola
    
    def repartir_cartas(self, jugadores):
        """Reparte 9 cartas a cada jugador desde el mazo."""
        for jugador in jugadores:
            if len(self.mazo) >= 9:
                cartas = [self.mazo.popleft() for _ in range(9)]  # Sacar 9 cartas de la cola
                jugador.asignar_carta(cartas)
            else:
                raise ValueError("No hay suficientes cartas en el mazo para repartir.")
    
    def intercambio_obligatorio(self, jugadores):
        """
        Gestiona el intercambio obligatorio de cartas entre jugadores al inicio del juego.
        El juego no puede continuar hasta que todos hayan intercambiado una carta.
        """
        # Nueva implementación: realizar intercambio direccional y simultáneo
        return self._intercambio_direccional(jugadores)
        for i, jugador in enumerate(jugadores):
            limpiar_pantalla()
            siguiente_jugador = jugadores[(i + 1) % len(jugadores)]  # El siguiente jugador en la lista
            print(f"{jugador.nombre}, selecciona una carta para intercambiar con {siguiente_jugador.nombre}:")
            print(f"Tu mazo: {jugador.mano_cartas[0]}")
            while True:
                try:
                    carta_seleccionada = input(f"Escribe la carta a intercambiar (ejemplo: 'A de Picas'): ")
                    carta_seleccionada_norm = normalizar_carta(carta_seleccionada)
                    carta = next((c for c in jugador.mano_cartas[0] if normalizar_carta(str(c)) == carta_seleccionada_norm), None)
                    if carta:
                        jugador.intercambiar_carta(carta, siguiente_jugador)
                        print(f"{jugador.nombre} ha intercambiado {carta} con {siguiente_jugador.nombre}.")
                        pausar()
                        break
                    else:
                        print("Carta no válida. Intenta de nuevo.")
                        pausar()
                except ValueError as e:
                    print(e)
                    pausar()
    
    def sacar_cartas_por_turno(self, jugadores):
        turno = 0
        primer_turno = True
        while len(self.mazo) > 0:
            jugador_actual = jugadores[turno % len(jugadores)]
            if primer_turno:
                num_cartas = 2
                primer_turno = False
            else:
                num_cartas = 1
            for _ in range(num_cartas):
                if len(self.mazo) == 0:
                    break
                carta = self.mazo[0]  # Carta visible en la cima del mazo general
                print(f"Turno de {jugador_actual.nombre}. Carta visible en la cima del mazo: {carta}")
                
                # Regla de extensión obligatoria
                idx_juego = jugador_actual.puede_agregar_a_juego_existente(carta, numero)
                if idx_juego is not None:
                    print(f"{jugador_actual.nombre} está obligado a tomar la carta {carta} para extender su juego.")
                    jugador_actual.agregar_a_juego_existente(idx_juego, carta)
                    self.mazo.popleft()
                    
                    # Condición de victoria
                    if jugador_actual.ha_ganado():
                        print(f"{jugador_actual.nombre} ha ganado el juego con 10 cartas en juegos y 0 en mano!")
                        return
                    
                    # Pago de carta
                    if (not jugador_actual.ha_ganado()) and len(jugador_actual.mano_cartas[0]) > 0:
                        print(f"{jugador_actual.nombre} debe pagar una carta de su mazo personal.")
                        print(f"Cartas en mano: {jugador_actual.mano_cartas[0]}")
                        while True:
                            carta_a_soltar = input(f"¿Qué carta quieres pagar? (Ej: A de Picas): ")
                            carta_paga = next((c for c in jugador_actual.mano_cartas[0] if str(c) == carta_a_soltar), None)
                            if carta_paga:
                                jugador_actual.mano_cartas[0].remove(carta_paga)
                                self.mazo.appendleft(carta_paga)
                                print(f"Pagaste {carta_paga} al mazo general.")
                                break
                            else:
                                print("Carta no encontrada en la mano. Intenta de nuevo.")
                else:
                    # Intentar crear juego con la carta del mazo general
                    print(f"{jugador_actual.nombre} puede intentar usar la carta {carta} para formar un juego.")
                    carta_usada = self.crear_juego(jugador_actual, carta)

                    if carta_usada:
                        self.mazo.popleft()  # Eliminar carta del mazo si fue usada

                        # Condición de victoria
                        if jugador_actual.ha_ganado():
                            print(f"{jugador_actual.nombre} ha ganado el juego con 10 cartas en juegos y 0 en mano!")
                            return

                        # Pago de carta
                        if (not jugador_actual.ha_ganado()) and len(jugador_actual.mano_cartas[0]) > 0:
                            print(f"{jugador_actual.nombre} usó la carta del mazo general y debe pagar una carta.")
                            print(f"Cartas en mano: {jugador_actual.mano_cartas[0]}")
                            while True:
                                carta_a_soltar = input(f"¿Qué carta quieres pagar? (Ej: A de Picas): ")
                                carta_paga = next((c for c in jugador_actual.mano_cartas[0] if str(c) == carta_a_soltar), None)
                                if carta_paga:
                                    jugador_actual.mano_cartas[0].remove(carta_paga)
                                    self.mazo.appendleft(carta_paga)
                                    print(f"Pagaste {carta_paga} al mazo general.")
                                    break
                                else:
                                    print("Carta no encontrada en la mano. Intenta de nuevo.")
                    else:
                        # Si no fue usada, se descarta
                        print(f"Nadie usó la carta {carta}. Se descarta del mazo.")
                        self.mazo.popleft()
                
                # Condición de victoria global al final del turno
                if jugador_actual.ha_ganado():
                    print(f"{jugador_actual.nombre} ha ganado el juego con 10 cartas en juegos y 0 en mano!")
                    return
            turno += 1
        print("El mazo está vacío. Fin del juego. Si nadie ganó, es empate.")

    
    def buscar_pares(self , cartas):
        pares = {}
        for carta in cartas:
            if not hasattr(carta , 'numero'):
                continue

            if carta.numero not in pares:
                pares[carta.numero] = []
            pares[carta.numero].append(carta) #Agregar la carta al grupo
        for numero , grupo in pares.items():
            if len(grupo) >=3:
                return grupo[:min(len(grupo), 10)] # Devolver las 3 primeras cartas del grupo / o juegos de hasta 10 cartas
        return None
    
    def es_seguidilla_completa(self, cartas):
        """
        Verifica si una lista de cartas forma una seguidilla completa y continua.
        :param cartas: Lista de cartas a verificar.
        :return: True si las cartas forman una seguidilla completa, False en caso contrario.
        """
        if len(cartas) < 3:
            return False
        indices = [numero.index(carta.numero) for carta in cartas]
        indices.sort()
        # Verificar que no falte ninguna carta en la secuencia
        for i in range(indices[0], indices[-1] + 1):
            if i not in indices:
                return False
        return True
    
    def buscar_seguidillas(self, cartas):
        """
        Busca seguidillas completas y continuas en una lista de cartas.
        Permite que la A funcione como 1 y como 14 (después de K).
        """
        cartas_por_palo = {}
        for carta in cartas:
            if not hasattr(carta , 'numero'):
                continue
            palo_norm = normalizar_carta(f"A de {carta.palo}").split(' de ')[1]
            if palo_norm not in cartas_por_palo:
                cartas_por_palo[palo_norm] = []
            cartas_por_palo[palo_norm].append(carta)
        # Buscar seguidillas en cada palo
        for palo, grupo in cartas_por_palo.items():
            # Generar dos listas de índices: A como 1 y A como 14
            indices_normales = [numero.index(c.numero) for c in grupo]
            # Si hay una A, agregar un valor 13 extra para ella (después de K)
            indices_dual = []
            for c in grupo:
                idx = numero.index(c.numero)
                indices_dual.append(idx)
                if c.numero == 'A':
                    indices_dual.append(13)  # A como 14 (después de K)
            # Buscar seguidillas normales (A como 1)
            grupo_ordenado = [x for _, x in sorted(zip(indices_normales, grupo), key=lambda pair: pair[0])]
            seguidilla = []
            for i in range(len(grupo_ordenado)):
                if i == 0 or numero.index(grupo_ordenado[i].numero) == numero.index(grupo_ordenado[i - 1].numero) + 1:
                    seguidilla.append(grupo_ordenado[i])
                else:
                    if len(seguidilla) >= 3:
                        if self.es_seguidilla_completa(seguidilla):
                            return seguidilla[:min(len(seguidilla), 10)]
                    seguidilla = [grupo_ordenado[i]]
            if len(seguidilla) >= 3:
                if self.es_seguidilla_completa(seguidilla):
                    return seguidilla[:min(len(seguidilla), 10)]
            # Buscar seguidillas con A como 14 (Q-K-A)
            # Reemplazar el índice de la A por 13 si hay Q y K
            grupo_kq_a = []
            for c in grupo:
                if c.numero in ['Q', 'K', 'A']:
                    grupo_kq_a.append(c)
            if len(grupo_kq_a) >= 3:
                # Ordenar Q-K-A como 11-12-13
                grupo_kq_a_ordenado = sorted(grupo_kq_a, key=lambda c: {'Q':11, 'K':12, 'A':13}[c.numero])
                indices_kq_a = [{'Q':11, 'K':12, 'A':13}[c.numero] for c in grupo_kq_a_ordenado]
                if indices_kq_a == list(range(min(indices_kq_a), max(indices_kq_a)+1)):
                    return grupo_kq_a_ordenado
        return None
    
    def crear_juego_par(self, jugador, carta_externa=None):
        print("\n--- Crear juego de PAR ---")
        if carta_externa:
            print(f"Carta externa disponible: {carta_externa}")
        print(f"Tu mazo: {jugador.mano_cartas[0]}")
        seleccion = input("Escribe los números de las cartas de tu mazo personal a usar, separados por coma (ejemplo: '4 de Picas, 4 de Corazones'): ")

        try:
            cartas_usuario = []
            for s in seleccion.split(","):
                s = s.strip()
                s_norm = normalizar_carta(s)
                carta = next((c for c in jugador.mano_cartas[0] if normalizar_carta(str(c)) == s_norm), None)
                if carta:
                    cartas_usuario.append(carta)
                else:
                    print(f"La carta '{s}' no está en tu mazo personal.")
            if not cartas_usuario:
                print("No seleccionaste cartas válidas")
                return
            cartas_juego = cartas_usuario.copy()
            if carta_externa is not None:
                cartas_juego.append(carta_externa)
            # Validar que todas sean del mismo número
            if len(cartas_juego) >= 3 and all(c.numero == cartas_juego[0].numero for c in cartas_juego):
                if len(set(c.palo for c in cartas_juego)) == len(cartas_juego):  # Palos distintos
                    self.actualizar_mazo_personal(jugador, cartas_juego, carta_externa)
                    jugador.agregar_juego(cartas_juego)
                    print(f"Juego de pares creado: {cartas_juego}")
                else:
                    print("Todos los palos deben ser distintos.")
            else:
                print("Debes seleccionar al menos 3 cartas del mismo número.")
        except Exception:
            print("Alguna carta no está en tu mazo personal.")
    
    def crear_juego_seguidilla(self, jugador, carta_externa=None):
        print("\n--- Crear juego de SEGUIDILLA ---")
        if carta_externa:
            print(f"Carta externa disponible: {carta_externa}")
        print(f"Tu mazo: {jugador.mano_cartas[0]}")
        seleccion = input("Escribe los números de las cartas de tu mazo personal a usar, separados por coma (ejemplo: '5 de Corazones, 6 de Corazones'): ")
        try:
            cartas_usuario = []
            for s in seleccion.split(","):
                s = s.strip()
                s_norm = normalizar_carta(s)
                carta = next((c for c in jugador.mano_cartas[0] if normalizar_carta(str(c)) == s_norm), None)
                if carta:
                    cartas_usuario.append(carta)
                else:
                    print(f"La carta '{s}' no está en tu mazo personal.")
            if not cartas_usuario:
                print("No seleccionaste cartas válidas")
                return
            cartas_juego = cartas_usuario.copy()
            if carta_externa is not None:
                cartas_juego.append(carta_externa)
            # Validar que todas sean del mismo palo y consecutivas (A puede ser 1 o 14)
            if len(cartas_juego) >= 3 and all(c.palo == cartas_juego[0].palo for c in cartas_juego):
                idxs = sorted([numero.index(c.numero) for c in cartas_juego])
                es_contigua_normal = idxs == list(range(min(idxs), max(idxs)+1))
                es_contigua_alta = False
                if not es_contigua_normal and any(c.numero == 'A' for c in cartas_juego):
                    def rank_alto(c):
                        return 13 if c.numero == 'A' else numero.index(c.numero)
                    idxs_altos = sorted(rank_alto(c) for c in cartas_juego)
                    es_contigua_alta = idxs_altos == list(range(min(idxs_altos), max(idxs_altos)+1))
                if es_contigua_normal or es_contigua_alta:
                    self.actualizar_mazo_personal(jugador, cartas_juego, carta_externa)
                    jugador.agregar_juego(cartas_juego)
                    print(f"Juego de seguidilla creado: {cartas_juego}")
                else:
                    print("Las cartas no son consecutivas.")
            else:
                print("Debes seleccionar al menos 3 cartas del mismo palo.")
        except Exception:
            print("Alguna carta no está en tu mazo personal.")
    
    def crear_juego(self, jugador, carta_externa):
        print(f"Intentando crear un juego para {jugador.nombre} con la carta externa: {carta_externa}")
        print(f"Mazo personal de {jugador.nombre}: {jugador.mano_cartas[0]}")
        posibles_cartas = jugador.mano_cartas[0] + [carta_externa]
        juegos_pares = self.buscar_pares(posibles_cartas)
        if juegos_pares:
            print(f"Juego de pares creado: {juegos_pares}")
            self.actualizar_mazo_personal(jugador, juegos_pares, carta_externa)
            jugador.agregar_juego(juegos_pares)
            return True
        juegos_seguidillas = self.buscar_seguidillas(posibles_cartas)
        if juegos_seguidillas:
            print(f"Juego de seguidillas creado: {juegos_seguidillas}")
            self.actualizar_mazo_personal(jugador, juegos_seguidillas, carta_externa)
            jugador.agregar_juego(juegos_seguidillas)
            return True
        print(f"No se pudo crear un juego para {jugador.nombre} con la carta externa: {carta_externa}")
        return False
    
    def actualizar_mazo_personal(self , jugador , cartas_juego , carta_externa):
        # Elimina las cartas usadas del mazo personal
        for carta in cartas_juego:
            if carta in jugador.mano_cartas[0]:
                jugador.mano_cartas[0].remove(carta)
        # Si se usó carta externa, el jugador debe soltar una carta de su mano
        if carta_externa is not None and carta_externa in cartas_juego:
            # Verificar condición de victoria antes de pedir pago
            if jugador.ha_ganado():
                print(f"{jugador.nombre} ha ganado el juego con 10 cartas en juegos y 0 en mano!")
                return
            if (not jugador.ha_ganado()) and len(jugador.mano_cartas[0]) > 0:
                print(f"{jugador.nombre} debe soltar una carta de su mazo personal")
                print(f"Mazo personal actual: {jugador.mano_cartas[0]}")
                while True:
                    carta_a_soltar = input(f"¿Qué carta quieres soltar de tu mano {jugador.nombre}? (Ej: A de Picas): ")
                    carta_a_soltar_norm = normalizar_carta(carta_a_soltar)
                    carta_paga = next((c for c in jugador.mano_cartas[0] if normalizar_carta(str(c)) == carta_a_soltar_norm), None)
                    if carta_paga:
                        jugador.mano_cartas[0].remove(carta_paga)
                        self.mazo.appendleft(carta_paga)
                        print(f"{jugador.nombre} ha soltado la carta {carta_paga} al tope del mazo general.")
                        break
                    else:
                        print("Carta no encontrada en la mano. Intenta de nuevo.")
