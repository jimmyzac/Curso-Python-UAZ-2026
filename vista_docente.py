"""
Vista docente — Curso interactivo de Python para Economistas, UAZ.
Colocar junto a python_economistas.py.
"""
import python_economistas as curso_base

class VistaDocente(curso_base.Curso):
    def __init__(self):
        super().__init__(registro_url="")
        self.alumno = {
            "nombre":"PRUEBA DOCENTE",
            "matricula":"TEST0001",
            "grupo":"PRUEBA",
            "periodo":"TEST-2026"
        }

    def guardar_remoto(self):
        return False

    def completar(self, codigo, resumen):
        print("-"*68)
        print(f"[FIN DE LECCIÓN {codigo} — VISTA DOCENTE]")
        print("-"*68)

    def opcion(self, leccion, pregunta, validas, pista=None):
        print("\n[PREGUNTA DE OPCIÓN]")
        print(pregunta)
        if pista: print("Pista:", pista)

    def expresion(self, leccion, pregunta, verificador, pista=None):
        print("\n[EJERCICIO / EXPRESIÓN]")
        print(pregunta)
        if pista: print("Pista:", pista)

    def codigo(self, leccion, pregunta, verificador, pista=None):
        print("\n[EJERCICIO DE CÓDIGO]")
        print(pregunta)
        if pista: print("Pista:", pista)

def iniciar_vista_docente():
    c = VistaDocente()
    acciones = [
        ("1.1","Introducción y operaciones básicas",c.l11),
        ("1.2","Objetos: strings y numéricos",c.l12),
        ("1.3","Variables de tiempo y fecha",c.l13),
        ("1.4","Listas",c.l14),
        ("1.5","Librerías, funciones y métodos",c.l15),
        ("1.6","Tuplas y diccionarios",c.l16),
        ("2.0","NumPy",c.l20),
        ("3.1","pandas: Series",c.l31),
        ("3.2","pandas: DataFrame",c.l32),
        ("3.3","pandas: slicing y filtrado",c.l33),
        ("4.1","Interés simple e interés compuesto",c.l41),
        ("4.2","Capitalización m veces al año",c.l42),
        ("4.3","Capitalización continua",c.l43),
        ("4.4","Tasas efectivas y equivalentes",c.l44),
        ("4.5","Valor presente",c.l45),
        ("4.6","Anualidades",c.l46),
        ("4.7","Perpetuidades",c.l47),
        ("4.8","Precio de bonos",c.l48),
        ("4.9","Precio de acciones",c.l49),
    ]
    while True:
        print("\n"+"="*68)
        print("VISTA DOCENTE — CURSO PYTHON UAZ".center(68))
        print("="*68)
        for i,(cod,nombre,_) in enumerate(acciones,1):
            print(f"{i:>2}. {cod} · {nombre}")
        print("\nT. Ver TODO el curso")
        print("0. Salir")
        op=input("\nSelecciona: ").strip().upper()
        if op=="0": return
        if op=="T":
            for cod,nombre,fn in acciones:
                print("\n\n"+"#"*76)
                print(f"### {cod} · {nombre}")
                print("#"*76)
                fn()
            continue
        try:
            i=int(op)
            if 1 <= i <= len(acciones):
                acciones[i-1][2]()
            else:
                print("Opción no válida.")
        except ValueError:
            print("Opción no válida.")
