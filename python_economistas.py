"""
Curso interactivo de Python
Bloque I: fundamentos de Python, NumPy y pandas.
Pensado para ejecutarse desde Google Colab.
"""

from datetime import date, datetime, timedelta
import json
import os

VERSION = "0.1.0"

LESSONS = [
    ("1.1", "Introducción y operaciones básicas"),
    ("1.2", "Objetos: strings y numéricos"),
    ("1.3", "Variables de tiempo y fecha"),
    ("1.4", "Listas"),
    ("1.5", "Librerías; funciones y métodos"),
    ("1.6", "Tuplas y diccionarios"),
    ("2.0", "NumPy"),
    ("3.1", "pandas: Series"),
    ("3.2", "pandas: DataFrame"),
    ("3.3", "pandas: slicing y filtrado"),
]

class Curso:
    def __init__(self):
        self.alumno = {}
        self.completadas = set()
        self.intentos = {}
        self.env = {"date": date, "datetime": datetime, "timedelta": timedelta}
        self.inicio = datetime.now()

    def titulo(self, texto):
        print("\n" + "=" * 68)
        print(texto.center(68))
        print("=" * 68)

    def explicar(self, texto):
        print("\n" + texto.strip() + "\n")

    def ejemplo(self, codigo, salida=None):
        print("Ejemplo:")
        for x in codigo.strip().splitlines():
            print("    " + x)
        if salida is not None:
            print("\nResultado:")
            for x in str(salida).splitlines():
                print("    " + x)
        print()

    def _intento(self, leccion):
        self.intentos[leccion] = self.intentos.get(leccion, 0) + 1

    def opcion(self, leccion, pregunta, validas, pista=None):
        n = 0
        validas = {str(v).strip().lower() for v in validas}
        while True:
            r = input(pregunta + "\n>>> ").strip().lower()
            self._intento(leccion)
            if r in validas:
                print("✓ Correcto.\n")
                return
            n += 1
            print("✗ Todavía no.")
            if pista and n >= 2:
                print("Pista:", pista)
            print()

    def expresion(self, leccion, pregunta, verificador, pista=None):
        n = 0
        while True:
            codigo = input(pregunta + "\n>>> ").strip()
            self._intento(leccion)
            try:
                valor = eval(codigo, {"__builtins__": __builtins__}, self.env)
                if verificador(valor, codigo, self.env):
                    print(f"✓ Correcto. Resultado: {valor}\n")
                    return valor
                print(f"✗ La expresión se ejecutó, pero produjo {valor!r}.")
            except Exception as e:
                print(f"✗ Python reportó {type(e).__name__}: {e}")
            n += 1
            if pista and n >= 2:
                print("Pista:", pista)
            print()

    def codigo(self, leccion, pregunta, verificador, pista=None):
        n = 0
        while True:
            codigo = input(pregunta + "\n>>> ").strip()
            self._intento(leccion)
            try:
                exec(codigo, {"__builtins__": __builtins__}, self.env)
                if verificador(self.env, codigo):
                    print("✓ Correcto.\n")
                    return
                print("✗ El código se ejecutó, pero no cumple lo solicitado.")
            except Exception as e:
                print(f"✗ Python reportó {type(e).__name__}: {e}")
            n += 1
            if pista and n >= 2:
                print("Pista:", pista)
            print()

    def completar(self, codigo, resumen):
        self.completadas.add(codigo)
        print("-" * 68)
        print(f"✓ LECCIÓN {codigo} COMPLETADA")
        print(resumen)
        print("-" * 68)

    def identificacion(self):
        self.titulo("CURSO INTERACTIVO DE PYTHON")
        print("Antes de comenzar registra tus datos.\n")
        self.alumno["nombre"] = input("Nombre completo: ").strip()
        self.alumno["matricula"] = input("Matrícula: ").strip()
        self.alumno["grupo"] = input("Código del grupo: ").strip()
        self.alumno["periodo"] = input("Periodo (ej. Ago-Dic 2026): ").strip()

    def l11(self):
        L="1.1"; self.titulo("1.1 · INTRODUCCIÓN Y OPERACIONES BÁSICAS")
        self.explicar("""Python es un lenguaje de programación. Una instrucción indica a
Python qué debe hacer. Una de las primeras funciones que aprenderemos es
print(), que permite mostrar información en pantalla.

Python distingue entre mayúsculas y minúsculas: print y Print son nombres
diferentes.""")
        self.ejemplo('print("Hola Python")', "Hola Python")
        self.codigo(L, 'Escribe una instrucción que muestre: Hola Python',
                    lambda e,c: "print" in c and "Hola Python" in c,
                    'Usa print("texto").')
        self.explicar("""Python también puede utilizarse como calculadora.

+  suma       -  resta
*  producto   /  división
** potencia

Los paréntesis permiten controlar el orden de las operaciones.""")
        self.ejemplo("(10 + 5) * 2", 30)
        self.expresion(L, "Multiplica 8 por 5 usando Python.",
                       lambda v,c,e: v==40 and "*" in c, "Usa *.")
        self.expresion(L, "Calcula 5 elevado al cuadrado.",
                       lambda v,c,e: v==25 and "**" in c, "La potencia se escribe **.")
        self.explicar("""Un comentario comienza con #. Python ignora el texto que aparece
después de # en esa línea. Los comentarios sirven para documentar el código.""")
        self.opcion(L, "¿Qué símbolo inicia un comentario?\nA) //   B) #   C) **",
                    ["b","#"], "Es el símbolo numeral.")
        self.completar(L, "Ya puedes usar print(), operadores, potencias y comentarios.")

    def l12(self):
        L="1.2"; self.titulo("1.2 · OBJETOS: STRINGS Y NUMÉRICOS")
        self.explicar("""En Python trabajamos con objetos. Un string (str) representa texto
y se escribe normalmente entre comillas. Los números enteros pertenecen al
tipo int y los números con decimales al tipo float.

Una variable es un nombre que referencia un objeto. El signo = asigna un
objeto a una variable.""")
        self.ejemplo('universidad = "UAZ"\ntype(universidad)', "<class 'str'>")
        self.codigo(L, 'Crea universidad con el texto "UAZ".',
                    lambda e,c: e.get("universidad")=="UAZ" and type(e.get("universidad")) is str,
                    'Escribe universidad = "UAZ".')
        self.expresion(L, "Consulta el tipo de universidad con type().",
                       lambda v,c,e: v is str, "Usa type(universidad).")
        self.codigo(L, "Crea edad con el entero 20.",
                    lambda e,c: e.get("edad")==20 and type(e.get("edad")) is int,
                    "No uses comillas ni decimal.")
        self.codigo(L, "Crea tasa con el valor decimal 0.08.",
                    lambda e,c: e.get("tasa")==0.08 and type(e.get("tasa")) is float,
                    "Escribe tasa = 0.08.")
        self.opcion(L, "¿Qué tipo es 2.5?\nA) int   B) float   C) str",
                    ["b","float"])
        self.completar(L, "Aprendiste str, int, float, variables, = y type().")

    def l13(self):
        L="1.3"; self.titulo("1.3 · VARIABLES DE TIEMPO Y FECHA")
        self.explicar("""El módulo datetime permite representar fechas y tiempo.
date(año, mes, día) crea una fecha. Restar dos fechas produce un objeto
timedelta; su atributo .days devuelve el número de días.""")
        self.ejemplo("fecha = date(2026, 9, 15)", "2026-09-15")
        self.codigo(L, "Crea fecha_clase con el 15 de septiembre de 2026.",
                    lambda e,c: e.get("fecha_clase")==date(2026,9,15),
                    "Usa date(2026, 9, 15).")
        self.expresion(L, "Calcula los días entre date(2026,9,20) y date(2026,9,15), usando .days.",
                       lambda v,c,e: v==5 and ".days" in c,
                       "Resta las fechas entre paréntesis y agrega .days.")
        self.completar(L, "Aprendiste date(), timedelta y operaciones sencillas con fechas.")

    def l14(self):
        L="1.4"; self.titulo("1.4 · LISTAS")
        self.explicar("""Una lista almacena varios objetos y se escribe con corchetes.
Python comienza a contar los índices desde cero: el primer elemento tiene
índice 0, el segundo índice 1, etc. Las listas son mutables.""")
        self.ejemplo("numeros = [10, 20, 30]\nnumeros[0]", 10)
        self.codigo(L, "Crea numeros = [10, 20, 30].",
                    lambda e,c: e.get("numeros")==[10,20,30],
                    "Usa corchetes.")
        self.expresion(L, "Obtén el segundo elemento de numeros mediante su índice.",
                       lambda v,c,e: v==20 and "[" in c, "El segundo índice es 1.")
        self.explicar("""append() es un método de las listas. Agrega un elemento al final.
Por ejemplo: numeros.append(40).""")
        self.codigo(L, "Agrega 40 al final de numeros usando append().",
                    lambda e,c: e.get("numeros")==[10,20,30,40] and ".append" in c,
                    "Usa numeros.append(40).")
        self.completar(L, "Aprendiste creación, índices, mutabilidad y append().")

    def l15(self):
        L="1.5"; self.titulo("1.5 · LIBRERÍAS, FUNCIONES Y MÉTODOS")
        self.explicar("""Una librería o módulo contiene herramientas reutilizables.
Se carga mediante import. Una función puede recibir un objeto:
len(texto). Un método pertenece a un objeto y usa punto:
texto.upper().

Esta diferencia será muy importante en NumPy y pandas.""")
        self.ejemplo('texto = "python"\nlen(texto)\ntexto.upper()', "6\n'PYTHON'")
        self.expresion(L, 'Obtén la longitud de "economia" usando len().',
                       lambda v,c,e: v==8 and "len" in c, "Usa len(...).")
        self.expresion(L, 'Convierte "python" a mayúsculas con .upper().',
                       lambda v,c,e: v=="PYTHON" and ".upper" in c,
                       'Usa "python".upper().')
        self.opcion(L, "¿Cuál es un método?\nA) len(texto)   B) texto.upper()",
                    ["b","texto.upper()"])
        self.completar(L, "Distingues librerías, funciones y métodos.")

    def l16(self):
        L="1.6"; self.titulo("1.6 · TUPLAS Y DICCIONARIOS")
        self.explicar("""Una tupla es una colección ordenada que normalmente tratamos como
inmutable y se escribe con paréntesis. Un diccionario almacena pares
clave: valor y se escribe con llaves.""")
        self.ejemplo('coordenada = (10, 20)\nalumno = {"nombre":"Ana", "edad":21}', "")
        self.codigo(L, "Crea coordenada como la tupla (10, 20).",
                    lambda e,c: e.get("coordenada")== (10,20) and type(e.get("coordenada")) is tuple,
                    "Usa paréntesis.")
        self.codigo(L, 'Crea alumno con la clave "nombre" y el valor "Ana".',
                    lambda e,c: isinstance(e.get("alumno"),dict) and e["alumno"].get("nombre")=="Ana",
                    'Usa {"nombre": "Ana"}.')
        self.expresion(L, 'Obtén el valor asociado a "nombre" en alumno.',
                       lambda v,c,e: v=="Ana", 'Usa alumno["nombre"].')
        self.completar(L, "Aprendiste tuplas, diccionarios, claves y valores.")

    def l20(self):
        L="2.0"; self.titulo("2 · NUMPY")
        import numpy as np
        self.env["np"]=np
        self.explicar("""NumPy es una librería especializada en cálculo numérico.
Su estructura fundamental es el array. A diferencia de una lista ordinaria,
un array facilita operaciones vectorizadas sobre todos sus elementos.""")
        self.ejemplo("import numpy as np\nx = np.array([1, 2, 3])\nx * 2", "[2 4 6]")
        self.codigo(L, "Crea datos como un array con 1, 2, 3 y 4.",
                    lambda e,c: hasattr(e.get("datos"),"tolist") and e["datos"].tolist()==[1,2,3,4],
                    "Usa np.array([...]).")
        self.expresion(L, "Calcula la media de datos usando .mean().",
                       lambda v,c,e: abs(float(v)-2.5)<1e-12 and ".mean" in c,
                       "Usa datos.mean().")
        self.expresion(L, "Multiplica todos los elementos de datos por 3.",
                       lambda v,c,e: hasattr(v,"tolist") and v.tolist()==[3,6,9,12],
                       "NumPy permite escribir datos * 3.")
        self.completar(L, "Aprendiste arrays, métodos y operaciones vectorizadas.")

    def l31(self):
        L="3.1"; self.titulo("3.1 · PANDAS: SERIES")
        import pandas as pd
        self.env["pd"]=pd
        self.explicar("""pandas es una librería para manipulación y análisis de datos.
Una Series es una estructura unidimensional que contiene valores y un índice.""")
        self.ejemplo("s = pd.Series([10, 20, 30])", "0    10\n1    20\n2    30")
        self.codigo(L, "Crea s como una Series con 10, 20 y 30.",
                    lambda e,c: isinstance(e.get("s"),pd.Series) and e["s"].tolist()==[10,20,30],
                    "Usa pd.Series([...]).")
        self.expresion(L, "Obtén el primer elemento de s usando iloc.",
                       lambda v,c,e: v==10 and ".iloc" in c, "Usa s.iloc[0].")
        self.completar(L, "Aprendiste Series, índices e iloc.")

    def l32(self):
        L="3.2"; self.titulo("3.2 · PANDAS: DATAFRAME")
        import pandas as pd
        self.env["pd"]=pd
        self.explicar("""Un DataFrame representa datos tabulares organizados en filas y
columnas. Puede construirse a partir de un diccionario, donde las claves
se convierten en nombres de columnas.""")
        self.ejemplo('df = pd.DataFrame({"nombre":["Ana","Luis"], "edad":[20,22]})',
                     "  nombre  edad\n0    Ana    20\n1   Luis    22")
        self.codigo(L, 'Crea df con una columna "x" que contenga 1, 2 y 3.',
                    lambda e,c: isinstance(e.get("df"),pd.DataFrame) and e["df"]["x"].tolist()==[1,2,3],
                    'Usa pd.DataFrame({"x":[1,2,3]}).')
        self.expresion(L, 'Selecciona la columna "x" de df.',
                       lambda v,c,e: isinstance(v,pd.Series) and v.tolist()==[1,2,3],
                       'Usa df["x"].')
        self.completar(L, "Aprendiste a crear DataFrames y seleccionar columnas.")

    def l33(self):
        L="3.3"; self.titulo("3.3 · PANDAS: SLICING Y FILTRADO")
        import pandas as pd
        self.env["pd"]=pd
        self.env["tabla"]=pd.DataFrame({
            "nombre":["Ana","Luis","Sofía","Carlos"],
            "edad":[19,22,25,20],
            "calificacion":[8,6,9,7]
        })
        self.explicar("""Slicing consiste en seleccionar una parte de una estructura.
iloc selecciona por posición. También podemos filtrar filas usando
condiciones que producen True o False.""")
        print(self.env["tabla"], "\n")
        self.expresion(L, "Selecciona las dos primeras filas con iloc.",
                       lambda v,c,e: isinstance(v,pd.DataFrame) and v["nombre"].tolist()==["Ana","Luis"],
                       "Usa tabla.iloc[0:2].")
        self.expresion(L, "Filtra tabla para conservar edades mayores de 20.",
                       lambda v,c,e: isinstance(v,pd.DataFrame) and v["nombre"].tolist()==["Luis","Sofía"],
                       'Usa tabla[tabla["edad"] > 20].')
        self.completar(L, "Aprendiste slicing con iloc y filtrado condicional.")

    def reporte(self):
        total=len(LESSONS); hechas=len(self.completadas)
        pct=100*hechas/total
        self.titulo("PROGRESO")
        print(f"Alumno:    {self.alumno.get('nombre','')}")
        print(f"Matrícula: {self.alumno.get('matricula','')}")
        print(f"Grupo:     {self.alumno.get('grupo','')}")
        print(f"Periodo:   {self.alumno.get('periodo','')}\n")
        for code,name in LESSONS:
            marca="✓" if code in self.completadas else "○"
            print(f"{marca} {code} {name}")
        print(f"\nProgreso total: {hechas}/{total} ({pct:.1f}%)")
        print(f"Intentos registrados: {sum(self.intentos.values())}")

    def guardar_reporte(self):
        datos = {
            **self.alumno,
            "version": VERSION,
            "inicio": self.inicio.isoformat(timespec="seconds"),
            "ultima_actividad": datetime.now().isoformat(timespec="seconds"),
            "lecciones_completadas": sorted(self.completadas),
            "intentos_por_leccion": self.intentos,
            "progreso_pct": round(100*len(self.completadas)/len(LESSONS),1),
            "curso_completado": len(self.completadas)==len(LESSONS)
        }
        mat = self.alumno.get("matricula","sin_matricula").replace(" ","_")
        archivo=f"progreso_python_{mat}.json"
        with open(archivo,"w",encoding="utf-8") as f:
            json.dump(datos,f,ensure_ascii=False,indent=2)
        print(f"\n✓ Reporte local generado: {archivo}")
        print("En una siguiente versión este mismo registro puede enviarse al registro central del profesor.")

    def menu(self):
        acciones = {
            "1": ("1.1 Introducción y operaciones", self.l11),
            "2": ("1.2 Strings y numéricos", self.l12),
            "3": ("1.3 Fechas y tiempo", self.l13),
            "4": ("1.4 Listas", self.l14),
            "5": ("1.5 Librerías, funciones y métodos", self.l15),
            "6": ("1.6 Tuplas y diccionarios", self.l16),
            "7": ("2.0 NumPy", self.l20),
            "8": ("3.1 pandas: Series", self.l31),
            "9": ("3.2 pandas: DataFrame", self.l32),
            "10": ("3.3 pandas: slicing y filtrado", self.l33),
        }
        while True:
            self.titulo("MENÚ DEL CURSO")
            for k,(nombre,_) in acciones.items():
                code=LESSONS[int(k)-1][0]
                marca="✓" if code in self.completadas else " "
                print(f"[{marca}] {k}. {nombre}")
            print("\n[P] Ver progreso   [G] Generar reporte   [0] Salir")
            r=input("\nSelecciona una opción: ").strip().lower()
            if r=="0":
                self.reporte()
                return
            if r=="p":
                self.reporte(); input("\nEnter para continuar...")
            elif r=="g":
                self.guardar_reporte(); input("\nEnter para continuar...")
            elif r in acciones:
                acciones[r][1](); input("\nEnter para volver al menú...")
            else:
                print("Opción no válida.")

_curso = None

def iniciar_curso():
    global _curso
    _curso = Curso()
    _curso.identificacion()
    _curso.menu()
