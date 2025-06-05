import win32print

def adaptar_codigo(codigo_original):
    lineas = codigo_original.strip().split('\n')
    lineas_adaptadas = []
    for linea in lineas:
        linea = linea.strip()
        if linea:
            linea_adaptada = f"{linea}\r\n"
            lineas_adaptadas.append(linea_adaptada)
    return ''.join(lineas_adaptadas)

# Definimos las variables que se van a usar dentro del boleto
SECCION = "GENERAL"
ORDEN = "1A2B3C4D"  # Reemplaza por el código que necesites
PRECIO = "300"
TIPO = "PREVENTA"
FILA = "1"
ASIENTO = "1"


codigo_original = f""" 
^Q140,0,0
^W57
^H5
^P1
^S2
^AD
^C1
^R0
~Q+0
^O0
^D0
^E12
~R255
^XSET,ROTATION,0
^L
Dy2-me-dd
Th:m:s
Y192,464,WindowText25-14
Y46,286,WindowText22-5
Y143,315,WindowText20-33
Y210,264,WindowText18-68
Y267,335,WindowText16-10
Y334,269,WindowText14-76
Y69,466,WindowText12-94
Y166,489,WindowText11-37
Y45,934,WindowText10-2
Y142,963,WindowText9-96
Y209,912,WindowText8-9
Y266,983,WindowText7-8
Y333,917,WindowText6-7
W213,212,5,2,M,8,5,55,3
https://eventonist.com/checkin/?id=MTMzNS0xMzIxLTUxN1Qw
VD,67,376,1,1,0,3E,{PRECIO}
VD,169,396,1,1,0,3E,{ORDEN}
VD,234,397,1,1,0,3E,{SECCION}
VD,291,397,1,1,0,3E,{FILA}
VD,358,397,1,1,0,3E,{ASIENTO}
VD,66,1024,1,1,0,3E,{PRECIO}
VD,168,1044,1,1,0,3E,{ORDEN}
VD,233,1045,1,1,0,3E,{SECCION}
VD,290,1045,1,1,0,3E,{FILA}
VD,357,1045,1,1,0,3E,{ASIENTO}
Lo,4,864,452,875
E
"""

# Adaptar y codificar el código
comandos = adaptar_codigo(codigo_original)
comandos_bytes = comandos.encode('ascii')

# Nombre de impresora (verifica que sea correcto en tu sistema)
nombre_impresora = "BP500"
# Imprimir
manejador_impresora = win32print.OpenPrinter(nombre_impresora)
try:
    win32print.StartDocPrinter(manejador_impresora, 1, ("Etiqueta", None, "RAW"))
    win32print.StartPagePrinter(manejador_impresora)
    win32print.WritePrinter(manejador_impresora, comandos_bytes)
    win32print.EndPagePrinter(manejador_impresora)
    win32print.EndDocPrinter(manejador_impresora)
finally:
    win32print.ClosePrinter(manejador_impresora)