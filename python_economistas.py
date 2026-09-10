"""
Curso interactivo de Python — v0.8
Persistencia opcional mediante Google Sheets + Apps Script Web App.
"""

from datetime import date, datetime, timedelta
import json
import urllib.parse
import urllib.request

VERSION = "0.8.0"
REGISTRO_URL_PREDETERMINADA = "https://script.google.com/macros/s/AKfycbwf6eJTMxSmTPHdMkTr-A1FJbh7gvSrvJxP8Jn8eZRaw6Q5zY-5ZPxtumf4lNOttL2hcw/exec"

LESSONS = [
    ("1.1", "Introducción y operaciones básicas"),
    ("1.2", "Objetos: strings y numéricos"),
    ("1.3", "Variables de tiempo y fecha"),
    ("1.4", "Listas"),
    ("1.5", "Librerías; funciones y métodos"),
    ("1.6", "Tuplas y diccionarios"),
    ("2.0", "NumPy: arrays y operaciones vectorizadas"),
    ("3.1", "pandas: Series"),
    ("3.2", "pandas: DataFrame"),
    ("3.3", "pandas: slicing y filtrado"),
    ("4.1", "Interés simple e interés compuesto"),
    ("4.2", "Capitalización m veces al año"),
    ("4.3", "Capitalización continua"),
    ("4.4", "Tasas efectivas y equivalentes"),
    ("4.5", "Valor presente"),
    ("4.6", "Anualidades"),
    ("4.7", "Perpetuidades"),
    ("4.8", "Precio de bonos"),
    ("4.9", "Precio de acciones"),
]

MODULES = [
    ("1", "Fundamentos de Python", ["1.1","1.2","1.3","1.4","1.5","1.6"]),
    ("2", "NumPy", ["2.0"]),
    ("3", "pandas", ["3.1","3.2","3.3"]),
    ("4", "Python aplicado a Finanzas", ["4.1","4.2","4.3","4.4","4.5","4.6","4.7","4.8","4.9"]),
]

PRERREQUISITOS_FINANZAS = {"1.1","1.2","1.3","1.4","1.5","1.6","2.0","3.1","3.2","3.3"}


class VolverAlMenu(Exception):
    """Interrumpe una actividad y regresa al menú sin completarla."""
    pass

class SalirDelCurso(Exception):
    """Finaliza el curso desde cualquier pregunta."""
    pass

def _comando_control(texto):
    comando = str(texto).strip().upper()
    if comando in {"MENU", "MENÚ"}:
        raise VolverAlMenu()
    if comando in {"SALIR", "0"}:
        raise SalirDelCurso()

class RegistroRemoto:
    def __init__(self, url=None):
        self.url = (url or "").strip()

    @property
    def activo(self):
        return self.url.startswith("http")

    def cargar(self, matricula, grupo, periodo):
        if not self.activo:
            return None
        params = urllib.parse.urlencode({
            "action": "get",
            "matricula": matricula,
            "grupo": grupo,
            "periodo": periodo,
        })
        try:
            with urllib.request.urlopen(self.url + "?" + params, timeout=15) as r:
                data = json.loads(r.read().decode("utf-8"))
            if data.get("ok") and data.get("found"):
                return data.get("record")
        except Exception as e:
            print(f"⚠ No fue posible recuperar el progreso remoto: {e}")
        return None

    def guardar(self, payload):
        if not self.activo:
            return False
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            self.url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read().decode("utf-8"))
            return bool(data.get("ok"))
        except Exception as e:
            print(f"⚠ No fue posible guardar el progreso remoto: {e}")
            return False


class Curso:
    def __init__(self, registro_url=None):
        self.alumno = {}
        self.completadas = set()
        # intentos: historial general para el reporte del alumno/profesor.
        self.intentos = {}
        # Estos dos contadores se usan para la calificación privada.
        # Solo acumulan mientras la lección aún NO ha sido completada.
        self.intentos_calificables = {}
        self.actividades_resueltas = {}
        self.env = {"date": date, "datetime": datetime, "timedelta": timedelta}
        self.inicio = datetime.now()
        self.registro = RegistroRemoto(registro_url or REGISTRO_URL_PREDETERMINADA)

    def titulo(self, texto):
        print("\n" + "=" * 68)
        print(texto.center(68))
        print("=" * 68)

    def barra_progreso(self, codigos=None):
        codigos = codigos or [c for c, _ in LESSONS]
        total = len(codigos)
        hechas = sum(1 for c in codigos if c in self.completadas)
        ancho = 20
        llenas = round(ancho * hechas / total) if total else 0
        barra = "█" * llenas + "░" * (ancho - llenas)
        porcentaje = 100 * hechas / total if total else 0
        return f"[{barra}] {hechas}/{total} ({porcentaje:.0f}%)"

    def finanzas_desbloqueadas(self):
        return PRERREQUISITOS_FINANZAS.issubset(self.completadas)

    def progreso_modulos(self):
        for numero, nombre, codigos in MODULES:
            estado = self.barra_progreso(codigos)
            if numero == "4" and not self.finanzas_desbloqueadas():
                print(f"🔒 MÓDULO {numero} · {nombre}: {estado}")
            else:
                print(f"   MÓDULO {numero} · {nombre}: {estado}")

    def siguiente_leccion(self):
        for code, name in LESSONS:
            if code not in self.completadas:
                return code, name
        return None, None

    def mensaje_control(self):
        print("Comandos disponibles: MENU = volver al menú | SALIR = cerrar curso\n")

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
        # Historial total de intentos.
        self.intentos[leccion] = self.intentos.get(leccion, 0) + 1

        # Intentos usados para calificación: dejan de cambiar cuando la
        # lección ya fue completada. Así repetir una lección no altera la nota.
        if leccion not in self.completadas:
            self.intentos_calificables[leccion] = (
                self.intentos_calificables.get(leccion, 0) + 1
            )

    def _actividad_correcta(self, leccion):
        # Cuenta automáticamente cada actividad superada. No hay que mantener
        # manualmente un catálogo del número de preguntas por lección.
        if leccion not in self.completadas:
            self.actividades_resueltas[leccion] = (
                self.actividades_resueltas.get(leccion, 0) + 1
            )

    def opcion(self, leccion, pregunta, validas, pista=None):
        n = 0
        validas = {str(v).strip().lower() for v in validas}
        while True:
            r_raw = input(pregunta + "\n>>> ").strip()
            _comando_control(r_raw)
            r = r_raw.lower()
            self._intento(leccion)
            if r in validas:
                self._actividad_correcta(leccion)
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
            _comando_control(codigo)
            self._intento(leccion)
            try:
                valor = eval(codigo, {"__builtins__": __builtins__}, self.env)
                if verificador(valor, codigo, self.env):
                    self._actividad_correcta(leccion)
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
            _comando_control(codigo)
            self._intento(leccion)
            try:
                exec(codigo, {"__builtins__": __builtins__}, self.env)
                if verificador(self.env, codigo):
                    self._actividad_correcta(leccion)
                    print("✓ Correcto.\n")
                    return
                print("✗ El código se ejecutó, pero no cumple lo solicitado.")
            except Exception as e:
                print(f"✗ Python reportó {type(e).__name__}: {e}")
            n += 1
            if pista and n >= 2:
                print("Pista:", pista)
            print()

    def estado(self):
        return {
            **self.alumno,
            "version": VERSION,
            "inicio": self.inicio.isoformat(timespec="seconds"),
            "ultima_actividad": datetime.now().isoformat(timespec="seconds"),
            "lecciones_completadas": sorted(self.completadas),
            "intentos_por_leccion": self.intentos,
            "intentos_calificables_por_leccion": self.intentos_calificables,
            "actividades_por_leccion": self.actividades_resueltas,
            "progreso_pct": round(100 * len(self.completadas) / len(LESSONS), 1),
            "curso_completado": len(self.completadas) == len(LESSONS),
        }

    def guardar_remoto(self):
        if self.registro.activo:
            ok = self.registro.guardar(self.estado())
            if ok:
                print("☁ Progreso guardado.")
            else:
                print("⚠ El progreso no pudo guardarse en este momento.")

    def completar(self, codigo, resumen):
        self.completadas.add(codigo)
        print("-" * 68)
        print(f"✓ LECCIÓN {codigo} COMPLETADA")
        print(resumen)
        print("Progreso:", self.barra_progreso())
        sig, nombre = self.siguiente_leccion()
        if sig:
            print(f"Siguiente lección sugerida: {sig} · {nombre}")
        else:
            print("🎉 Has completado todas las lecciones disponibles.")
        print("-" * 68)
        self.guardar_remoto()

    def identificacion(self):
        self.titulo("CURSO INTERACTIVO DE PYTHON")
        print("Registra tus datos para recuperar y guardar tu progreso.\n")
        def normalizar(texto):
            # Conserva acentos, normaliza espacios y convierte a mayúsculas.
            import unicodedata
            texto = unicodedata.normalize("NFC", str(texto or ""))
            return " ".join(texto.strip().split()).upper()

        print("Puedes escribir SALIR o 0 para cerrar el curso.\n")

        valor = input("Nombre completo: ")
        _comando_control(valor)
        self.alumno["nombre"] = normalizar(valor)

        valor = input("Matrícula: ")
        _comando_control(valor)
        self.alumno["matricula"] = normalizar(valor)

        valor = input("Código del grupo: ")
        _comando_control(valor)
        self.alumno["grupo"] = normalizar(valor)

        valor = input("Periodo (ej. Ago-Dic 2026): ")
        _comando_control(valor)
        self.alumno["periodo"] = normalizar(valor)

        previo = self.registro.cargar(
            self.alumno["matricula"],
            self.alumno["grupo"],
            self.alumno["periodo"]
        )
        if previo:
            self.completadas = set(previo.get("lecciones_completadas", []))
            self.intentos = {
                str(k): int(v)
                for k, v in previo.get("intentos_por_leccion", {}).items()
            }
            print("\n✓ Se encontró progreso anterior.")
            print("Progreso recuperado:", self.barra_progreso())
            ultima = str(previo.get("ultima_actividad", "sin fecha"))
            try:
                dt = datetime.fromisoformat(ultima.replace("Z", "+00:00"))
                ultima = dt.strftime("%d/%m/%Y %H:%M")
            except Exception:
                pass
            print(f"Última actividad: {ultima}")
            code, name = self.siguiente_leccion()
            if code:
                print(f"Siguiente lección sugerida: {code} · {name}")
        elif self.registro.activo:
            print("\n✓ Registro nuevo creado.")
            print("Progreso inicial:", self.barra_progreso())
            self.guardar_remoto()
        else:
            print("\n⚠ Registro remoto desactivado. El progreso no persistirá entre sesiones.")

    # ---------- Lecciones ----------
    def l11(self):
        L="1.1"; self.titulo("1.1 · INTRODUCCIÓN Y OPERACIONES BÁSICAS")
        self.explicar("""Python es un lenguaje de programación interpretado. En un cuaderno
como Google Colab escribimos instrucciones en celdas y Python las ejecuta de
arriba hacia abajo.

Una instrucción indica a Python qué debe hacer. Una de las primeras funciones
que aprenderemos es print(), que muestra información en pantalla.

Python distingue entre mayúsculas y minúsculas: print y Print son nombres
diferentes. También importa escribir correctamente paréntesis, comillas y
operadores.

Si ya trabajaste con Excel, observa una diferencia importante al escribir
potencias:

Operación             Excel                 Python
--------------------------------------------------------
5 elevado a 2         =5^2                  5**2
(1+0.08) elevado a 5  =(1+0.08)^5           (1+0.08)**5

En Excel usamos ^ para una potencia. En Python usamos **.
El símbolo ^ en Python tiene otro significado y NO debe utilizarse como
potencia.""")
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
        self.expresion(L, "Calcula (12 + 3) dividido entre 5.",
                       lambda v,c,e: abs(float(v)-3)<1e-12 and "(" in c and "/" in c,
                       "Usa paréntesis para sumar primero.")
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
        self.explicar("""El operador + depende del tipo de objeto. Con números suma;
con strings concatena texto. Por eso 2 + 3 produce 5, mientras que
"2" + "3" produce "23".""")
        self.expresion(L, 'Concatena "Eco" y "nomía" usando +.',
                       lambda v,c,e: v=="Economía" and "+" in c,
                       'Escribe "Eco" + "nomía".')
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
        self.ejemplo('coordenada = (10, 20)\nalumno = {"nombre":"Ana", "edad":21}')
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


    # ---------- Módulo 4: Python aplicado a Finanzas ----------
    def l41(self):
        L="4.1"; self.titulo("4.1 · INTERÉS SIMPLE E INTERÉS COMPUESTO")
        self.explicar("""El interés permite medir cómo cambia el valor del dinero a través
del tiempo.

Con interés simple, los intereses se calculan únicamente sobre el capital
inicial:

    VF = VP(1 + r n)

Con interés compuesto, los intereses generados se reinvierten:

    VF = VP(1 + r)^n

En Python, la potencia se escribe con **.""")
        self.ejemplo("VP = 10000\nr = 0.08\nn = 5\nVF = VP * (1 + r)**n\nVF", "14693.28")
        self.codigo(L, "Crea VP=10000, r=0.08 y n=5 en una sola línea separada por punto y coma.",
                    lambda e,c: e.get("VP")==10000 and e.get("r")==0.08 and e.get("n")==5,
                    "Ejemplo: VP=10000; r=0.08; n=5")
        self.expresion(L, "Calcula el valor futuro con interés compuesto.",
                       lambda v,c,e: abs(float(v)-14693.280768)<1e-6 and "**" in c,
                       "Usa VP * (1 + r)**n.")
        self.expresion(L, "Calcula el valor futuro con interés simple para los mismos datos.",
                       lambda v,c,e: abs(float(v)-14000)<1e-6,
                       "Usa VP * (1 + r*n).")
        self.completar(L, "Distingues interés simple y compuesto y puedes calcular ambos en Python.")

    def l42(self):
        L="4.2"; self.titulo("4.2 · CAPITALIZACIÓN m VECES AL AÑO")
        self.explicar("""Si una tasa nominal anual r se capitaliza m veces por año durante
t años, el valor futuro es:

    VF = VP(1 + r/m)^(m t)

En Python:

    VF = VP * (1 + r/m)**(m*t)

Cuando m aumenta, la capitalización se aproxima al caso continuo.""")
        self.ejemplo("VP=10000\nr=0.12\nm=12\nt=2\nVP*(1+r/m)**(m*t)", "12697.35")
        self.codigo(L, "Crea m=12 y t=2.",
                    lambda e,c: e.get("m")==12 and e.get("t")==2,
                    "Puedes escribir m=12; t=2")
        self.expresion(L, "Con VP=10000 y r=0.12, calcula VF con capitalización mensual durante 2 años.",
                       lambda v,c,e: abs(float(v)-12697.3466)<0.02 and "/m" in c,
                       "Usa VP * (1 + r/m)**(m*t).")
        self.completar(L, "Aprendiste capitalización periódica m veces al año.")

    def l43(self):
        L="4.3"; self.titulo("4.3 · CAPITALIZACIÓN CONTINUA")
        import math
        self.env["math"] = math
        self.explicar("""En capitalización continua, el número de periodos de capitalización
tiende a infinito. La expresión es:

    VF = VP e^(r t)

En Python podemos usar math.exp():

    VF = VP * math.exp(r*t)""")
        self.ejemplo("import math\nVP=10000\nr=0.08\nt=5\nVP*math.exp(r*t)", "14918.25")
        self.expresion(L, "Calcula el valor futuro continuo de VP=10000, r=0.08, t=5.",
                       lambda v,c,e: abs(float(v)-14918.24698)<0.02 and "exp" in c,
                       "Usa 10000 * math.exp(0.08*5).")
        self.opcion(L, "¿Qué función representa e elevado a x?\nA) math.exp(x)   B) math.log(x)   C) math.sqrt(x)",
                    ["a","math.exp(x)"], "La función se llama exp.")
        self.completar(L, "Aprendiste a trabajar con capitalización continua mediante math.exp().")

    def l44(self):
        L="4.4"; self.titulo("4.4 · TASAS EFECTIVAS Y EQUIVALENTES")
        self.explicar("""Una tasa nominal r capitalizable m veces al año puede transformarse
en tasa efectiva anual:

    TEA = (1 + r/m)^m - 1

Dos tasas son equivalentes cuando producen el mismo factor de acumulación
durante el mismo horizonte.""")
        self.ejemplo("r=0.12\nm=12\ntea=(1+r/m)**m - 1\ntea", "0.126825...")
        self.codigo(L, "Crea r_nominal=0.12 y m_anual=12.",
                    lambda e,c: e.get("r_nominal")==0.12 and e.get("m_anual")==12,
                    "Usa r_nominal=0.12; m_anual=12")
        self.expresion(L, "Calcula la tasa efectiva anual.",
                       lambda v,c,e: abs(float(v)-0.12682503)<1e-6,
                       "Usa (1+r_nominal/m_anual)**m_anual - 1.")
        self.completar(L, "Puedes convertir una tasa nominal capitalizable a tasa efectiva anual.")

    def l45(self):
        L="4.5"; self.titulo("4.5 · VALOR PRESENTE")
        self.explicar("""El valor presente permite traer un flujo futuro al día de hoy.

Si recibiremos VF dentro de n periodos y la tasa por periodo es r:

    VP = VF / (1 + r)^n

Es el proceso inverso de la capitalización.""")
        self.ejemplo("VF=15000\nr=0.10\nn=3\nVP=VF/(1+r)**n\nVP", "11269.72")
        self.codigo(L, "Crea VF=15000, r=0.10 y n=3.",
                    lambda e,c: e.get("VF")==15000 and e.get("r")==0.10 and e.get("n")==3,
                    "Usa VF=15000; r=0.10; n=3")
        self.expresion(L, "Calcula el valor presente.",
                       lambda v,c,e: abs(float(v)-11269.7220)<0.02 and "/" in c,
                       "Usa VF / (1 + r)**n.")
        self.completar(L, "Aprendiste a descontar flujos futuros mediante valor presente.")

    def l46(self):
        L="4.6"; self.titulo("4.6 · ANUALIDADES")
        self.explicar("""Una anualidad ordinaria consiste en pagos iguales C al final de cada
periodo. Su valor presente es:

    VP = C * (1 - 1/(1+r)^n) / r

Y su valor futuro:

    VF = C * ((1+r)^n - 1) / r

Estas fórmulas aparecen en préstamos, créditos, ahorro periódico y valuación
de flujos regulares.""")
        self.ejemplo("C=5000\nr=0.01\nn=24\nVP=C*(1-1/(1+r)**n)/r\nVP", "106216.94 aprox.")
        self.codigo(L, "Crea C=5000, r=0.01 y n=24.",
                    lambda e,c: e.get("C")==5000 and e.get("r")==0.01 and e.get("n")==24,
                    "Usa C=5000; r=0.01; n=24")
        esperado_vp = 5000*(1-1/(1+0.01)**24)/0.01
        esperado_vf = 5000*((1+0.01)**24-1)/0.01
        self.expresion(L, "Calcula el valor presente de la anualidad.",
                       lambda v,c,e,ev=esperado_vp: abs(float(v)-ev)<0.02,
                       "Usa C*(1-1/(1+r)**n)/r.")
        self.expresion(L, "Calcula el valor futuro de la anualidad.",
                       lambda v,c,e,ev=esperado_vf: abs(float(v)-ev)<0.02,
                       "Usa C*((1+r)**n-1)/r.")
        self.completar(L, "Aprendiste valor presente y valor futuro de una anualidad ordinaria.")

    def l47(self):
        L="4.7"; self.titulo("4.7 · PERPETUIDADES")
        self.explicar("""Una perpetuidad es una corriente de pagos constantes que continúa
indefinidamente. Si el primer pago C ocurre dentro de un periodo:

    VP = C / r

Si los pagos crecen a una tasa constante g:

    VP = C1 / (r - g)

siempre que r > g.""")
        self.ejemplo("C=1000\nr=0.08\nVP=C/r\nVP", "12500.0")
        self.codigo(L, "Crea C=1000 y r=0.08.",
                    lambda e,c: e.get("C")==1000 and e.get("r")==0.08,
                    "Usa C=1000; r=0.08")
        self.expresion(L, "Calcula el valor presente de la perpetuidad.",
                       lambda v,c,e: abs(float(v)-12500)<1e-6,
                       "Usa C/r.")
        self.expresion(L, "Si C1=1000, r=0.10 y g=0.04, calcula una perpetuidad creciente.",
                       lambda v,c,e: abs(float(v)-16666.6667)<0.02,
                       "Usa 1000/(0.10-0.04).")
        self.completar(L, "Aprendiste perpetuidades constantes y crecientes.")

    def l48(self):
        L="4.8"; self.titulo("4.8 · PRECIO DE BONOS")
        self.explicar("""El precio de un bono es el valor presente de sus cupones más el valor
presente de su valor nominal.

Para un bono con cupón C, valor nominal VN, rendimiento r y n periodos:

    P = sum(C/(1+r)^t, t=1,...,n) + VN/(1+r)^n

Python permite expresar esta suma con sum() y range().""")
        self.ejemplo("C=80\nVN=1000\nr=0.10\nn=3\nP=sum(C/(1+r)**t for t in range(1,n+1)) + VN/(1+r)**n", "950.26 aprox.")
        self.codigo(L, "Crea C=80, VN=1000, r=0.10 y n=3.",
                    lambda e,c: e.get("C")==80 and e.get("VN")==1000 and e.get("r")==0.10 and e.get("n")==3,
                    "Usa C=80; VN=1000; r=0.10; n=3")
        esperado = sum(80/(1+0.10)**t for t in range(1,4)) + 1000/(1+0.10)**3
        self.expresion(L, "Calcula el precio del bono usando sum() y range().",
                       lambda v,c,e,ev=esperado: abs(float(v)-ev)<0.02 and "sum" in c and "range" in c,
                       "Usa sum(C/(1+r)**t for t in range(1,n+1)) + VN/(1+r)**n.")
        self.opcion(L, "Si el cupón es menor que el rendimiento requerido, normalmente el bono cotiza:\nA) Sobre par   B) Bajo par   C) Exactamente a par",
                    ["b","bajo par"], "Compara la tasa cupón con el rendimiento requerido.")
        self.completar(L, "Puedes valuar un bono descontando cupones y valor nominal.")

    def l49(self):
        L="4.9"; self.titulo("4.9 · PRECIO DE ACCIONES")
        self.explicar("""Una acción puede valuarse como el valor presente de los dividendos
esperados. En el modelo de Gordon, si el dividendo del próximo periodo es D1,
la tasa requerida es r y el crecimiento perpetuo es g:

    P0 = D1 / (r - g)

con r > g.

También podemos valorar una acción durante un horizonte finito descontando
dividendos y un precio esperado de venta.""")
        self.ejemplo("D1=5\nr=0.12\ng=0.04\nP0=D1/(r-g)\nP0", "62.5")
        self.codigo(L, "Crea D1=5, r=0.12 y g=0.04.",
                    lambda e,c: e.get("D1")==5 and e.get("r")==0.12 and e.get("g")==0.04,
                    "Usa D1=5; r=0.12; g=0.04")
        self.expresion(L, "Calcula el precio de la acción con el modelo de Gordon.",
                       lambda v,c,e: abs(float(v)-62.5)<1e-6,
                       "Usa D1/(r-g).")
        self.expresion(L, "Si D1=4, D2=4.2, P2=55 y r=0.10, calcula P0 descontando los tres flujos.",
                       lambda v,c,e: abs(float(v)-(4/1.1 + (4.2+55)/(1.1**2)))<0.02,
                       "Usa 4/(1.10) + (4.2+55)/(1.10**2).")
        self.completar(L, "Aprendiste valoración básica de acciones por dividendos.")

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
        print(f"\nProgreso general: {hechas}/{total} ({pct:.1f}%)\n")
        self.progreso_modulos()
        print(f"\nIntentos registrados: {sum(self.intentos.values())}")

    def menu(self):
        acciones = {
            "1": ("1.1 Introducción y operaciones", self.l11, "1.1"),
            "2": ("1.2 Strings y numéricos", self.l12, "1.2"),
            "3": ("1.3 Fechas y tiempo", self.l13, "1.3"),
            "4": ("1.4 Listas", self.l14, "1.4"),
            "5": ("1.5 Librerías, funciones y métodos", self.l15, "1.5"),
            "6": ("1.6 Tuplas y diccionarios", self.l16, "1.6"),
            "7": ("2.0 NumPy", self.l20, "2.0"),
            "8": ("3.1 pandas: Series", self.l31, "3.1"),
            "9": ("3.2 pandas: DataFrame", self.l32, "3.2"),
            "10": ("3.3 pandas: slicing y filtrado", self.l33, "3.3"),
            "11": ("4.1 Interés simple e interés compuesto", self.l41, "4.1"),
            "12": ("4.2 Capitalización m veces al año", self.l42, "4.2"),
            "13": ("4.3 Capitalización continua", self.l43, "4.3"),
            "14": ("4.4 Tasas efectivas y equivalentes", self.l44, "4.4"),
            "15": ("4.5 Valor presente", self.l45, "4.5"),
            "16": ("4.6 Anualidades", self.l46, "4.6"),
            "17": ("4.7 Perpetuidades", self.l47, "4.7"),
            "18": ("4.8 Precio de bonos", self.l48, "4.8"),
            "19": ("4.9 Precio de acciones", self.l49, "4.9"),
        }

        while True:
            self.titulo("MENÚ DEL CURSO")
            print("PROGRESO GENERAL:", self.barra_progreso())
            print()
            self.progreso_modulos()

            code_sig, name_sig = self.siguiente_leccion()
            if code_sig:
                if code_sig.startswith("4.") and not self.finanzas_desbloqueadas():
                    print("\nCompleta los módulos 1, 2 y 3 para desbloquear Finanzas.")
                else:
                    print(f"\nSiguiente sugerida: {code_sig} · {name_sig}")
            else:
                print("\n✓ Curso completado")

            print("\n" + "-" * 68)
            for k,(nombre,_,code) in acciones.items():
                marca="✓" if code in self.completadas else " "
                if code.startswith("4.") and not self.finanzas_desbloqueadas():
                    print(f"[🔒] {k}. {nombre}")
                else:
                    print(f"[{marca}] {k}. {nombre}")

            print("\n[P] Ver progreso   [0] Salir")
            print("Dentro de una actividad: MENU = volver al menú | SALIR = cerrar curso")
            r=input("\nSelecciona una opción: ").strip().lower()

            if r in {"0", "salir"}:
                self.reporte()
                self.guardar_remoto()
                print("\nCurso finalizado.")
                return

            if r=="p":
                self.reporte()
                input("\nEnter para continuar...")
                continue

            if r in acciones:
                nombre, funcion, code = acciones[r]

                if code.startswith("4.") and not self.finanzas_desbloqueadas():
                    faltantes = [c for c in sorted(PRERREQUISITOS_FINANZAS) if c not in self.completadas]
                    print("\n🔒 MÓDULO 4 BLOQUEADO")
                    print("Para acceder a Finanzas debes completar primero los módulos 1, 2 y 3.")
                    print("Lecciones pendientes:", ", ".join(faltantes))
                    input("\nEnter para volver al menú...")
                    continue

                if code in self.completadas:
                    repetir = input("Esta lección ya está completada. ¿Deseas repetirla? (s/n): ").strip().lower()
                    if repetir != "s":
                        continue

                try:
                    funcion()
                    input("\nEnter para volver al menú...")
                except VolverAlMenu:
                    self.guardar_remoto()
                    print("\n↩ Regresando al menú. La lección no se marcó como completada.")
                    continue
                except SalirDelCurso:
                    self.guardar_remoto()
                    print("\n✓ Progreso guardado. Curso finalizado.")
                    return
            else:
                print("Opción no válida.")


def iniciar_curso(registro_url=None):
    curso = Curso(registro_url=registro_url)
    try:
        curso.identificacion()
        curso.menu()
    except SalirDelCurso:
        if curso.alumno.get("matricula"):
            curso.guardar_remoto()
        print("\nCurso finalizado.")
    except VolverAlMenu:
        # Durante el registro no existe todavía un menú utilizable.
        print("\nRegistro cancelado. Curso finalizado.")
    return None
