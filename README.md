### Simulador de requerimientos de disco v1.01    

Requisitos Minimos:

 - Python 2.6.6 hasta 2.7.7
 - setuptools
 - PyGame
 - Pyttk

Opcionales minimos para que el graficador funcione:


	a. matplotlib
	b. Numpy
	c. argparser (defecto en Python 2.6.6 o superior)

Vinculo para descargar paquete:
	https://www.dropbox.com/s/rcios1o3dk0lb6m/redistx86.zip

Por favor leer el 'Simulator_User_Manual.pdf' correspondiente a su versión del programa.

Pasos basicos de ejecucion:

	a. Descomprimir en una carpeta el archivo 'simulador.zip'
	b. Instalar las dependencias necesarias segun se especifica en el Manual de Usuario
	c. Ubicarse en la carpeta simulador que se encuentra en la
	carpeta principal donde se descomprimio el programa
	{carpeta_seleccionada}/simulador/
	d. Ejecutar la verificacion del simulador (opcional), invocando al modulo test.py desde
	la consola.
	Si bien se puede ejecutar desde cualquier sitio, existen algunos inconvenientes
	al utilizar los archivos, ya que el sistema los ubica en la carpeta desde donde se ejecuto
	el programa y no en la carpeta raiz del mismo. (Se corregira en versiones futuras)
	e. Ejecutar: python __init__.py
	
FAQ y Problemas conocidos:

	a. Los paquetes que se encuentran en la carpeta redistx86.zip puede que no se instalen correctamente en Linux, es recomendable obtener las ultimas versiones de los paquetes disponibles
    desde el Universe

	b. La ejecucion del programa fallo por permiso denegado. En Linux es recomendable ejecutar como administrador
	c. Hay errores de archivo, no se encuentran los archivos de configuracion o de lenguaje. Esto es o porque se editaron los archivos incorrectamente (o movieron), o porque no se esta ejecutando el programa desde la carpeta raiz

	d. El archivo de lenguaje no pudo ser cargado, y el programa colapsa. Esto se debe a que se ha editado incorrectamente el archivo de lenguaje o no existe dicho archivo. Por defecto el lenguaje es ingles ('eng'), si no esta seguro de como editar el lenguaje no lo utilice

	e. La edicion de archivos de texto en Windows puede generar el incorrecto funcionamiento en Linux, por favor edite los archivos de configuracion y lenguaje unicamente desde el sistema operativo donde se ejecutara el programa.

	f. La opcion paso a paso no esta disponible en Linux. Esto se debe a que existen problemas de compatibilidad entre Tkinter (interfaz) y Pygame en Linux. Se esta buscando corregir este problema para las versiones futuras.

	g. No se pudo guardar el ambiente de simulacion. Esto se debe a que no tiene permisos de escritura o el simulador esta funcionando

	h. La pantalla del grafico esta completamente gris y unicamente se mueve al simular. Esto es un error conocido en algunos Linux.
	

El programa fue probado en los siguientes SOs:

- Windows x32 ---> Funcionamiento Correcto
- Windows x64 ---> Funcionamiento Correcto
- Linux Huayra x32 ---> Funcionamiento Correcto
- Linux Ubuntu x32 ---> Funcionamiento Correcto
- Linux Lihuen ---> Funcionamiento Incorrecto*

**(1): En algunos Linux Lihuen se ha detectado que la pantalla se torna gris luego de terminar la 
animacion.*

*05/08/2013*

	