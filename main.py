import json
import re

import os
from dotenv import load_dotenv

from pymongo import MongoClient

import datetime
import subprocess

import pandas as pd

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

client: MongoClient = MongoClient(MONGO_URI)

try:
    print("Estableciendo conexión...⏳")
    client.admin.command("ping")
    print("Conexión establecida 😊")
except:
    print("❌ ERROR EN LA CONEXIÓN")
    exit(code=1)
db = client["prueba3"]
# ──────────────────────────────────────────────────────────────────
#  UTILIDADES DE PRESENTACIÓN
# ──────────────────────────────────────────────────────────────────

LINEA  = "-" * 62
DOBLE  = "=" * 62

def titulo(texto):
    print(f"\n{DOBLE}")
    print(f"  {texto}")
    print(DOBLE)

def subtitulo(texto):
    print(f"\n  {texto}")
    print(f"  {LINEA}")

def ok(texto):
    print(f"\n  [OK]  {texto}")

def error(texto):
    print(f"\n  [ERROR]  {texto}")

def info(texto):
    print(f"  [i]  {texto}")

def separador():
    print(f"  {LINEA}")

def mostrar_tabla(datos, columnas=None):
    """
    Muestra una lista de diccionarios como tabla usando pandas,
    con columnas bien separadas por '|' y una linea divisoria
    bajo el encabezado para que se vea ordenada.
    - datos: lista de dicts
    - columnas: lista opcional con el orden/nombre de columnas a mostrar
    """
    if not datos:
        info("No hay datos para mostrar.")
        return

    df = pd.DataFrame(datos)

    if columnas:
        columnas_existentes = [c for c in columnas if c in df.columns]
        df = df[columnas_existentes]

    # Ancho de cada columna = el mayor entre el titulo y el dato mas largo
    anchos = {
        col: max(len(str(col)), df[col].astype(str).map(len).max())
        for col in df.columns
    }

    sep = "  |  "

    encabezado = sep.join(str(col).center(anchos[col]) for col in df.columns)
    linea_div  = sep.join("-" * anchos[col] for col in df.columns)

    print()
    print(f"  {encabezado}")
    print(f"  {linea_div}")
    for _, fila in df.iterrows():
        linea = sep.join(str(fila[col]).ljust(anchos[col]) for col in df.columns)
        print(f"  {linea}")

def pausa():
    input("\n  Presiona Enter para volver al menu...")

# ──────────────────────────────────────────────────────────────────
#  CARGA DE DATOS
# ──────────────────────────────────────────────────────────────────

def cargar_datos():
    titulo("CARGANDO BASE DE DATOS")
    try:
        with open("eventos.json", "r", encoding="utf-8") as f:
            db["eventos"].drop()
            db["eventos"].insert_many(json.load(f))

        with open("invitados.json", "r", encoding="utf-8") as f:
            db["invitados"].drop()
            db["invitados"].insert_many(json.load(f))

        ok("Conexion exitosa con MongoDB — Base de datos: prueba3")
        print(f"\n  {'Coleccion':<20} {'Documentos':>10}")
        separador()
        print(f"  {'eventos':<20} {db['eventos'].count_documents({}):>10}")
        print(f"  {'invitados':<20} {db['invitados'].count_documents({}):>10}")
        separador()
    except FileNotFoundError as e:
        error(f"Archivo no encontrado: {e.filename}")
        error("Asegurate de tener eventos.json e invitados.json en la misma carpeta.")
        exit()

# ══════════════════════════════════════════════════════════════════
#  ACTIVIDAD 1 - FILTROS
# ══════════════════════════════════════════════════════════════════

def listar_todos_eventos():
    titulo("LISTADO COMPLETO DE EVENTOS")
    eventos = list(db["eventos"].find({}, {"_id": 0}))
    info(f"Se encontraron {len(eventos)} eventos registrados.")
    separador()

    filas = [{
        "Nombre": e["nombre"],
        "Codigo": e["codigo"],
        "Fecha": e["fecha"][:10],
        "Lugar": e["lugar"],
        "Categoria": e["categoria"].capitalize(),
        "Invitados": len(e.get("invitados", []))
    } for e in eventos]

    mostrar_tabla(filas)
    separador()
    pausa()

def filtrar_eventos_por_categoria():
    titulo("FILTRAR EVENTOS POR CATEGORIA")
    print("  Selecciona una categoria:\n")
    print("    1  ->  Charla")
    print("    2  ->  Workshop")
    print("    3  ->  Meetup")
    separador()
    op = input("  Opcion: ").strip()
    categorias = {"1": "charla", "2": "workshop", "3": "meetup"}
    categoria = categorias.get(op)
    if not categoria:
        error("Opcion invalida. Intenta nuevamente.")
        pausa()
        return

    eventos = list(db["eventos"].find({"categoria": categoria},
                                       {"_id": 0, "codigo": 1, "nombre": 1,
                                        "fecha": 1, "lugar": 1}))
    subtitulo(f"Eventos de categoria: {categoria.upper()}  ({len(eventos)} resultados)")

    filas = [{
        "Codigo": e["codigo"],
        "Nombre": e["nombre"],
        "Fecha": e["fecha"][:10],
        "Lugar": e["lugar"]
    } for e in eventos]

    mostrar_tabla(filas)
    separador()
    pausa()

def listar_invitados_activos():
    titulo("INVITADOS CON ESTADO ACTIVO")
    invitados = list(db["invitados"].find({"estado": "activo"},
                                           {"_id": 0, "rut": 1, "nombre": 1,
                                            "empresa": 1, "correo": 1}))
    info(f"Se encontraron {len(invitados)} invitados activos.")
    separador()

    filas = [{
        "Nombre": inv["nombre"],
        "RUT": inv["rut"],
        "Empresa": inv["empresa"],
        "Correo": inv["correo"]
    } for inv in invitados]

    mostrar_tabla(filas)
    separador()
    pausa()

def listar_invitados_bloqueados():
    titulo("INVITADOS CON ESTADO BLOQUEADO")
    invitados = list(db["invitados"].find({"estado": "bloqueado"},
                                           {"_id": 0, "rut": 1, "nombre": 1,
                                            "empresa": 1, "correo": 1}))
    info(f"Se encontraron {len(invitados)} invitados bloqueados.")
    separador()

    filas = [{
        "Nombre": inv["nombre"],
        "RUT": inv["rut"],
        "Empresa": inv["empresa"],
        "Correo": inv["correo"]
    } for inv in invitados]

    mostrar_tabla(filas)
    separador()
    pausa()

# ══════════════════════════════════════════════════════════════════
#  ACTIVIDAD 2 - EXPRESIONES REGULARES
# ══════════════════════════════════════════════════════════════════

def buscar_invitado_por_nombre():
    titulo("BUSCAR INVITADO POR NOMBRE  (regex)")
    termino = input("  Ingresa nombre o parte del nombre: ").strip()
    if not termino:
        error("Debes ingresar un termino de busqueda.")
        pausa()
        return

    patron = {"$regex": termino, "$options": "i"}
    resultados = list(db["invitados"].find({"nombre": patron},
                                            {"_id": 0, "rut": 1, "nombre": 1,
                                             "empresa": 1, "correo": 1, "estado": 1}))
    subtitulo(f"Resultados para: \"{termino}\"  ({len(resultados)} encontrados)")

    filas = [{
        "Estado": "ACTIVO" if inv["estado"] == "activo" else "BLOQUEADO",
        "Nombre": inv["nombre"],
        "RUT": inv["rut"],
        "Empresa": inv["empresa"],
        "Correo": inv["correo"]
    } for inv in resultados]

    mostrar_tabla(filas)
    separador()
    pausa()

def buscar_por_dominio_correo():
    titulo("BUSCAR POR DOMINIO DE CORREO  (regex)")
    info("Dominios disponibles: empresa.cl  |  contratista.cl  |  inacap.cl")
    separador()
    dominio = input("  Ingresa el dominio (sin @): ").strip()
    if not dominio:
        error("Debes ingresar un dominio.")
        pausa()
        return

    patron = {"$regex": f"@{re.escape(dominio)}$", "$options": "i"}
    resultados = list(db["invitados"].find({"correo": patron},
                                            {"_id": 0, "rut": 1, "nombre": 1,
                                             "correo": 1, "empresa": 1, "estado": 1}))
    subtitulo(f"Invitados con correo @{dominio}  ({len(resultados)} encontrados)")

    filas = [{
        "Estado": "ACTIVO" if inv["estado"] == "activo" else "BLOQUEADO",
        "Nombre": inv["nombre"],
        "Correo": inv["correo"],
        "Empresa": inv["empresa"]
    } for inv in resultados]

    mostrar_tabla(filas)
    separador()
    pausa()

def buscar_eventos_por_nombre():
    titulo("BUSCAR EVENTOS POR PALABRA CLAVE  (regex)")
    termino = input("  Ingresa la palabra clave: ").strip()
    if not termino:
        error("Debes ingresar un termino.")
        pausa()
        return

    patron = {"$regex": termino, "$options": "i"}
    resultados = list(db["eventos"].find({"nombre": patron},
                                          {"_id": 0, "codigo": 1, "nombre": 1,
                                           "fecha": 1, "lugar": 1, "categoria": 1}))
    subtitulo(f"Eventos que contienen: \"{termino}\"  ({len(resultados)} encontrados)")

    filas = [{
        "Nombre": e["nombre"],
        "Codigo": e["codigo"],
        "Fecha": e["fecha"][:10],
        "Lugar": e["lugar"],
        "Categoria": e["categoria"].capitalize()
    } for e in resultados]

    mostrar_tabla(filas)
    separador()
    pausa()

# ══════════════════════════════════════════════════════════════════
#  ACTIVIDAD 3 - SUBDOCUMENTOS
# ══════════════════════════════════════════════════════════════════

def validar_acceso_invitado():
    titulo("VALIDAR ACCESO DE INVITADO A EVENTO")
    info("Se verificara el estado en el evento y en el sistema.")
    separador()
    rut    = input("  RUT del invitado  (ej: 11.118.512-6) : ").strip()
    codigo = input("  Codigo del evento (ej: EVT-2025-001)  : ").strip()

    invitado = db["invitados"].find_one({"rut": rut}, {"_id": 0, "nombre": 1, "estado": 1})
    evento_confirmado = db["eventos"].find_one(
        {"codigo": codigo, "invitados": {"$elemMatch": {"rut": rut, "estado": "confirmado"}}},
        {"_id": 0, "nombre": 1}
    )
    evento_existe = db["eventos"].find_one({"codigo": codigo}, {"_id": 0, "nombre": 1})

    subtitulo("Resultado de validacion")

    if not invitado:
        error("El RUT ingresado no existe en la base de datos.")
        pausa()
        return

    if not evento_existe:
        error("El codigo de evento ingresado no existe.")
        pausa()
        return

    if invitado["estado"] == "bloqueado":
        acceso = "DENEGADO"
        motivo = "El invitado tiene estado BLOQUEADO en el sistema."
    elif evento_confirmado:
        acceso = "PERMITIDO"
        motivo = "El invitado esta CONFIRMADO y ACTIVO en el sistema."
    else:
        acceso = "DENEGADO"
        motivo = "El invitado no esta confirmado para este evento."

    filas = [{
        "Invitado": invitado["nombre"],
        "Evento": evento_existe["nombre"],
        "Acceso": acceso,
        "Motivo": motivo
    }]

    mostrar_tabla(filas)
    separador()
    pausa()

def ver_invitados_de_evento():
    titulo("INVITADOS DE UN EVENTO")
    codigo = input("  Codigo del evento (ej: EVT-2025-001): ").strip()
    evento = db["eventos"].find_one({"codigo": codigo}, {"_id": 0, "nombre": 1, "invitados": 1})

    if not evento:
        error("Evento no encontrado. Verifica el codigo ingresado.")
        pausa()
        return

    subtitulo(f"Evento: {evento['nombre']}")
    confirmados = pendientes = rechazados = 0
    filas = []

    for inv in evento.get("invitados", []):
        estado = inv["estado"]
        datos  = db["invitados"].find_one({"rut": inv["rut"]}, {"_id": 0, "nombre": 1})
        nombre = datos["nombre"] if datos else "Desconocido"

        if estado == "confirmado":
            confirmados += 1
        elif estado == "pendiente":
            pendientes += 1
        else:
            rechazados += 1

        filas.append({
            "Estado": estado.upper(),
            "Nombre": nombre,
            "RUT": inv["rut"]
        })

    mostrar_tabla(filas)
    separador()
    print(f"\n  Resumen  ->  {confirmados} confirmados  |  {pendientes} pendientes  |  {rechazados} rechazados")
    separador()
    pausa()

def buscar_eventos_de_invitado():
    titulo("EVENTOS EN LOS QUE APARECE UN INVITADO")
    rut      = input("  RUT del invitado (ej: 11.118.512-6): ").strip()
    invitado = db["invitados"].find_one({"rut": rut}, {"_id": 0, "nombre": 1, "estado": 1})

    if not invitado:
        error("Invitado no encontrado. Verifica el RUT ingresado.")
        pausa()
        return

    eventos = list(db["eventos"].find(
        {"invitados.rut": rut},
        {"_id": 0, "codigo": 1, "nombre": 1, "fecha": 1, "invitados.$": 1}
    ))

    subtitulo(f"Invitado: {invitado['nombre']}  |  Estado global: {invitado['estado'].capitalize()}")
    info(f"Aparece en {len(eventos)} evento(s).")
    separador()

    filas = []
    for e in eventos:
        estado_inv = e["invitados"][0]["estado"]
        filas.append({
            "Estado": estado_inv.upper(),
            "Evento": e["nombre"],
            "Codigo": e["codigo"],
            "Fecha": e["fecha"][:10]
        })

    mostrar_tabla(filas)
    separador()
    pausa()

# ══════════════════════════════════════════════════════════════════
#  ACTIVIDAD 4 - $LOOKUP Y AGREGACIONES
# ══════════════════════════════════════════════════════════════════

def top3_eventos_mas_confirmados():
    titulo("TOP 3 EVENTOS CON MAS CONFIRMADOS")
    pipeline = [
        {"$unwind": "$invitados"},
        {"$match": {"invitados.estado": "confirmado"}},
        {"$group": {
            "_id":       "$codigo",
            "nombre":    {"$first": "$nombre"},
            "lugar":     {"$first": "$lugar"},
            "categoria": {"$first": "$categoria"},
            "total":     {"$sum": 1}
        }},
        {"$sort": {"total": -1}},
        {"$limit": 3}
    ]
    resultados = list(db["eventos"].aggregate(pipeline))
    puestos    = ["1er lugar", "2do lugar", "3er lugar"]

    filas = []
    for i, r in enumerate(resultados):
        filas.append({
            "Puesto": puestos[i],
            "Nombre": r["nombre"],
            "Codigo": r["_id"],
            "Lugar": r["lugar"],
            "Categoria": r["categoria"].capitalize(),
            "Confirmados": r["total"]
        })

    mostrar_tabla(filas)
    separador()
    pausa()

def lookup_invitados_confirmados_por_evento():
    titulo("LOOKUP — CONFIRMADOS CON DATOS COMPLETOS")
    info("Combina las colecciones 'eventos' e 'invitados' con $lookup.")
    separador()
    codigo = input("  Codigo del evento (ej: EVT-2025-001): ").strip()

    pipeline = [
        {"$match": {"codigo": codigo}},
        {"$unwind": "$invitados"},
        {"$match": {"invitados.estado": "confirmado"}},
        {"$lookup": {
            "from":         "invitados",
            "localField":   "invitados.rut",
            "foreignField": "rut",
            "as":           "datos"
        }},
        {"$unwind": "$datos"},
        {"$project": {
            "_id":           0,
            "evento":        "$nombre",
            "nombre":        "$datos.nombre",
            "correo":        "$datos.correo",
            "empresa":       "$datos.empresa",
            "estado_global": "$datos.estado"
        }}
    ]

    resultados = list(db["eventos"].aggregate(pipeline))

    if not resultados:
        error("Evento no encontrado o sin invitados confirmados.")
        pausa()
        return

    subtitulo(f"Evento: {resultados[0]['evento']}  ({len(resultados)} confirmados)")

    filas = [{
        "Estado": "ACTIVO" if r["estado_global"] == "activo" else "BLOQUEADO",
        "Nombre": r["nombre"],
        "Empresa": r["empresa"],
        "Correo": r["correo"]
    } for r in resultados]

    mostrar_tabla(filas)
    separador()
    pausa()

def resumen_por_empresa():
    titulo("RESUMEN DE INVITADOS POR EMPRESA")
    pipeline = [
        {"$group": {"_id": "$empresa", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}}
    ]
    resultados = list(db["invitados"].aggregate(pipeline))
    info(f"{len(resultados)} empresas registradas.")
    separador()

    filas = [{
        "Empresa": r["_id"],
        "Invitados": r["total"]
    } for r in resultados]

    mostrar_tabla(filas)
    separador()
    pausa()

# ══════════════════════════════════════════════════════════════════
#  MENU PRINCIPAL
# ══════════════════════════════════════════════════════════════════

def menu():
    while True:
        print(f"\n{DOBLE}")
        print("     SISTEMA DE GESTION DE EVENTOS   -   TI3032")
        print(DOBLE)
        print()
        print("   Filtros")
        print("    1 . Listar todos los eventos")
        print("    2 . Filtrar eventos por categoria")
        print("    3 . Listar invitados activos")
        print("    4 . Listar invitados bloqueados")
        print()
        print("   Expresiones regulares")
        print("    5 . Buscar invitado por nombre")
        print("    6 . Buscar invitados por dominio de correo")
        print("    7 . Buscar eventos por palabra clave")
        print()
        print("   Subdocumentos")
        print("    8 . Validar acceso de invitado a evento")
        print("    9 . Ver invitados de un evento")
        print("   10 . Ver eventos de un invitado")
        print()
        print("   $lookup y agregaciones")
        print("   11 . Top 3 eventos con mas confirmados")
        print("   12 . Lookup: datos completos de confirmados")
        print("   13 . Resumen de invitados por empresa")
        print()
        print("    0 . Salir")
        print(DOBLE)

        opcion = input("   Selecciona una opcion: ").strip()
        acciones = {
            "1":  listar_todos_eventos,
            "2":  filtrar_eventos_por_categoria,
            "3":  listar_invitados_activos,
            "4":  listar_invitados_bloqueados,
            "5":  buscar_invitado_por_nombre,
            "6":  buscar_por_dominio_correo,
            "7":  buscar_eventos_por_nombre,
            "8":  validar_acceso_invitado,
            "9":  ver_invitados_de_evento,
            "10": buscar_eventos_de_invitado,
            "11": top3_eventos_mas_confirmados,
            "12": lookup_invitados_confirmados_por_evento,
            "13": resumen_por_empresa,
        }
        if opcion == "0":
            print(f"\n  Hasta luego.\n")
            break
        elif opcion in acciones:
            acciones[opcion]()
        else:
            error("Opcion invalida. Por favor elige un numero del 0 al 13.")

# ──────────────────────────────────────────────────────────────────
#  INICIO
# ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cargar_datos()
    menu()