# Curso interactivo de Python — v0.8

Esta versión añade persistencia de progreso con Google Sheets mediante una
Aplicación Web de Google Apps Script.

## Qué se guarda
- nombre
- matrícula
- código de grupo
- periodo
- lecciones completadas
- intentos por lección
- porcentaje de progreso
- fecha de inicio y última actividad
- estado de curso completado

## Flujo
1. El alumno abre Colab.
2. Colab descarga `python_economistas.py` desde GitHub.
3. El alumno introduce nombre, matrícula, grupo y periodo.
4. El curso consulta Google Sheets.
5. Si encuentra un registro, recupera el progreso.
6. Cada vez que termina una lección, el progreso se actualiza automáticamente.

## Configuración
Consulta `apps_script_registro.gs`, crea una Google Sheet y despliega el
Apps Script como aplicación web. Luego pega la URL `/exec` en la celda de Colab.


## Normalización de datos en v0.8
Los campos `nombre`, `matricula`, `grupo` y `periodo` se normalizan tanto en
Python como en Apps Script:

- se conservan los acentos y la letra ñ;
- se normaliza Unicode a NFC;
- se eliminan espacios al inicio y al final;
- varios espacios consecutivos se convierten en uno;
- el texto se almacena en mayúsculas.

Ejemplo: `  José   María Muñoz  ` se almacena como `JOSÉ MARÍA MUÑOZ`.

Esta doble normalización evita duplicados por diferencias de mayúsculas,
espacios o representación Unicode.


## Cambios en v0.8

- La URL de Apps Script ya está integrada en `python_economistas.py`.
- El alumno ya no necesita copiar ni conocer la URL de registro.
- Dentro de cualquier pregunta puede escribir `MENU` para volver al menú.
- Puede escribir `SALIR` o `0` para cerrar el curso.
- Si abandona una lección antes de terminarla, esa lección no se marca como completada.
- Antes de volver al menú o cerrar el curso se intenta guardar el progreso remoto.
- Durante el registro inicial también puede escribir `SALIR` o `0`.

URL de registro configurada internamente:
`https://script.google.com/macros/s/AKfycbwf6eJTMxSmTPHdMkTr-A1FJbh7gvSrvJxP8Jn8eZRaw6Q5zY-5ZPxtumf4lNOttL2hcw/exec`

## Celda recomendada para estudiantes

```python
!rm -f python_economistas.py

!wget -q -O python_economistas.py \
https://raw.githubusercontent.com/jimmyzac/Curso-Python-UAZ-2026/main/python_economistas.py

import sys
if "python_economistas" in sys.modules:
    del sys.modules["python_economistas"]

import python_economistas

python_economistas.iniciar_curso()
```


## Cambios en v0.8

- Se elimina la salida visual `<python_economistas.Curso at ...>` al terminar.
- Se añade una barra de progreso en el menú y al recuperar una sesión.
- Se muestra la siguiente lección sugerida.
- La fecha de última actividad se presenta en un formato más legible.
- Se mejora la explicación pedagógica de 1.1 y 1.2.
- Se agregan ejercicios sobre precedencia de operaciones y concatenación de strings.
- Se mantiene la persistencia automática en Google Sheets.
- Se conservan los comandos `MENU`, `SALIR` y `0`.


## Cambios en v0.8 — Módulo de Finanzas

Se incorpora un cuarto módulo con nueve lecciones:

- 4.1 Interés simple e interés compuesto
- 4.2 Capitalización m veces al año
- 4.3 Capitalización continua
- 4.4 Tasas efectivas y equivalentes
- 4.5 Valor presente
- 4.6 Anualidades
- 4.7 Perpetuidades
- 4.8 Precio de bonos
- 4.9 Precio de acciones

### Bloqueo pedagógico
El módulo 4 aparece en el menú, pero permanece bloqueado hasta que el alumno
complete todas las lecciones de los módulos 1, 2 y 3.

### Progreso
El curso muestra:
- progreso general;
- progreso por módulo;
- estado bloqueado/desbloqueado de Finanzas.

Los identificadores anteriores (1.1–3.3) se conservaron para no romper los
registros existentes en Google Sheets.


## Cambios en v0.8 — equivalencia Excel/Python y calificación privada

### Potencias
La lección 1.1 incorpora una tabla que contrasta la sintaxis de potencia:

    Operación             Excel                 Python
    --------------------------------------------------------
    5 elevado a 2         =5^2                  5**2
    (1+0.08) elevado a 5  =(1+0.08)^5           (1+0.08)**5

También incluye una pregunta automática para reforzar que `^` es potencia en
Excel, pero `**` es potencia en Python.

### Calificación privada basada en intentos
La calificación se calcula únicamente en Apps Script y se almacena en la hoja
del profesor. No se calcula ni se muestra en el código Python descargado por
los estudiantes.

Se añaden automáticamente tres columnas:
- intentos_minimos
- errores_adicionales
- calificacion_docente

La calificación considera solo las lecciones ya completadas y compara los
intentos realizados con el mínimo necesario si cada actividad se resolviera
correctamente al primer intento.

Fórmula actual, ubicada únicamente en Apps Script:
    calificación = 5 + 5 * (intentos_mínimos / intentos_totales)

Ejemplos aproximados:
- promedio de 1 intento por actividad -> 10.00
- promedio de 2 intentos -> 7.50
- promedio de 3 intentos -> 6.67

IMPORTANTE: para activar esta función hay que sustituir el Apps Script actual
por el archivo de esta versión y crear una NUEVA VERSIÓN de la implementación
web. La URL /exec puede mantenerse igual si se actualiza la implementación
existente.


## Cambios en v0.8 — calificación dinámica

Ya no existe un catálogo manual con el número de preguntas de cada lección.

Cada vez que una actividad se responde correctamente, Python incrementa
automáticamente `actividades_por_leccion`. Cada intento realizado antes de
completar una lección se registra en `intentos_calificables_por_leccion`.

Apps Script calcula la nota únicamente con las lecciones ya completadas:

    errores_adicionales =
        intentos_calificados - actividades_calificadas

    calificación =
        5 + 5 * (actividades_calificadas / intentos_calificados)

La fórmula permanece únicamente en Apps Script y la columna
`calificacion_docente` nunca se devuelve al alumno.

### Ventaja principal

Se pueden añadir o quitar preguntas dentro de una lección sin actualizar
Apps Script. El sistema detecta dinámicamente cuántas actividades resolvió
el alumno.

### Repetición de lecciones

Una vez que una lección está completada, repetirla puede seguir aumentando el
historial general de intentos, pero NO modifica los contadores usados para la
calificación. Así un alumno no puede subir o bajar su nota repitiendo una
lección ya terminada.

### Alumnos con progreso de versiones anteriores

Los registros anteriores siguen siendo reconocidos. Los nuevos campos se
crean automáticamente en la hoja. Para lecciones completadas antes de v0.8 no
hay información retrospectiva del número exacto de actividades correctas, por
lo que esas lecciones no aportarán a la nueva calificación hasta que se decida
una política de migración.
