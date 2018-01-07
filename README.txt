#Práctica Docker.
El servicio  tweetanalysis esta creado por la imagen javier162380/twitter_emr_sentiment_analysis disponible en dockerhub compuesto por el siguiente dockerfile:
FROM python:3.6-alpine
RUN mkdir /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache -r app/requirements.txt
COPY ./twitter.py /app/twitter.py
COPY ./jobmanager.py /app/jobmanager.py
COPY ./mrjob.conf /app/mrjob.conf
COPY ./mrjobplaces.py /app/mrjobplaces.py
COPY ./diccionaries.py /app/diccionaries.py
COPY ./states.py /app/states.py
#twitter enviroment variables
ENV DOWNLOAD_TIME="0.001"
ENV TWEETER_ACCOUNT=""
ENV API_KEY="rfEyBrskP5FHtxBpdVnWfXoT9"
ENV API_SECRET="YhHr20cYWbr0c996aiILnzmM9b0ombCgGOPdnerxuu4RDcWBPG"
ENV API_TOKEN="1451037732-hyu3XFKQWX9hL66hDqm2C3WDLGOUVnyPUkj0CPp"
ENV API_TOKEN_SECRET="TzcvxYXuRVXcA71oVi1x0bEBehseSLW2HcQoJniNvDGva"
#emr enviroment variables
ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""
ENV INSTANCE_TYPE="c1.medium"
ENV NUM_CORE_INSTANCES="1"
#mongodb enviroment variables
ENV MONGODB_HOST="mongo"
ENV MONGODB_PORT="27017"


CMD ["python" , "/app/jobmanager.py"]

Hemos escogido la imagen de python 3.6 de la distribucion alpine al ser la mas ligera.
por otro lado hemos preferido crearnos un directorio app donde guardaremos el codigo.
En primer lugar instalamos los paquetes de los que depende nueestra aplicacion que se encuentran en el fichero requirements.txt, usando la opcion de no cache pues al realizar la aplicacion hemos tenido que crear muchas imagens distintas y no queriamos que hubiera dependencias entre varios contenedores pues nos dimos cuenta que docker de los contrario usaba la cache al hacer el build. Posteriomente hemos copiado los archivos de codigo a la carpeta donde cada uno se encarga de lo siguiente.

twitter.py--> este archivo es el encargado de realizar la descarga de los tweets. Es una clase que hemos creado donde usaremos el metodo streamingapi que nos permite descargar tweets hasta un momento del tiempo dado que queramos y nos otorga la opcion de subir el archivo autonamitcamente a s3 en caso de que queramos.

mrjobplaces.py --> este archivo contiene el job de hadoop, nos hemos apoyado en la libreria mrjob, este script nos devuelve la satisfaccion por division federal de EEUU relativa a la busqueda que hayamos realizado, y el top ten de hastags relacionados con esa busqueda. Para lograr este objetivo hemos tenido que realizar dos reducers, uno para agrupar en primer lugar por el tipo de objetivo que queremos analizar (geolocalizacion o hastag) y en segundo  para desagrupar los resultados dentro de de cada objetivo.

diccionaries.py --> este archivo es un hash que otorga a cada palabra una puntacion, le llamamos en mrjobplaces.py para sacar la valoracion de cada tweet.

states.py--> este archivo consiste en dos hashes que nos permiten obtener la geolocalizacion del tweet por estado. El primer hash otorga para cada estado una lista de coordenadas que delimitan el permitro del mismo, posteriormente en mrjobplaces.py comprobamos si las coordendas del tweet se encuentran dentro del poligono.El segundo hash nos otoroga para cada estado el nombre de las ciudades que contiene asi en caso de no poder geolocalizar al usuario por las coordenadas lo podriamos localizar por la ubicacion.

jobmanager.py --> este script sirve de orquestador, y sera el que ejecute el contendor, de este modo en primer lugar el script hace una llamada a la api de twitter en streaming ( a traves de la clase twitter y el metodo streamingapi.pypara recoger los tweets), estos son guardados en un archivo llamado ficherotemp con la extension .json. Una vez recogidos los tweets el archivo es cerrado y se vuelve abrir, en este caso para cada json invocamos a la clase MRJOB creada en el archivo mrjobplaces.py donde le pasamos en el comando arg( por lista ) los siguienteS argumentos:
	- fichero a analizar en este caso ficherotemp.json
	- cluser con el formato -r emr pues lo analizaremos en el cloud de amazon.
	- --no-output pues no queremos que nos devuelva los resultados en ningun bucket de s3.
	- -c mrjob.conf en este caso hace alusion al fichero de configuracion donde solo nombramos los archivos diccionaries.py , states.py pues son archivos que llamaremos en la clase de mrjob.----instance-type seguido de la variable de entorno con el tipo de instancias de nuestro cluster y --num-core-instances seguido de la variable de entorno con el numerode instancias de nuestro cluster.
	
Para realizar el job llamamos a los metodos make_runner() y run() que nos otorga la libreria MRJOB y nos permite ejecutar desde otro script, un job realizado sobre esta libreria.Una vez realizado el job de map reduce llamamos al metodo cat_output(), que nos deja capturar el output imprimido por pantalla. Anteriormente hemos creado gracias a la libreria pymongo un cliente de mongodb, a su vez llamamos a una base de datos "hadoop_sentiment_analysis" (en caso de no existir dicha base de datos se creara), y posteriormente una coleccion que se llamara del mismo modo al que ayamos llamado a la variable de entorno TWEETER_ACCOUNT. Sobre este output recogido crearmos una lista de hashes siendo la clave el primer elemento de la tupla devolvida por el output y el valor el segundo. Una vez recogida la lista insertaremos en un batch todos los hashes sirviendonos del metodo insertamny.

mrjob.conf--> este archivo recoge la configuracion basica del job, que procesaremos en s3, archivos a tener en cuenta. Hay que destacer que en este caso hemos preferido no introducir nuestras credenciales de s3 y configurarlas como variables de entorno lo que entendemos que nos permite un mayor control sobre nuestra cuenta por si llegado a un punto el coste nos hiciera cambiarlas seria mas comodo y no habria que volver a reahacer la imagen.

Posteriormente nos encontramos con las variables de entorno que se pueden diferenciar en tres grandes grupos:
#twitter,
en este caso estan las pedidas por la practica  ademas de las de una cuenta de twitter.
#emr,
estas variables son las relativas ala cluster de emr, Destacar que hemos dejado vacio el valor de AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY pues al ejecutarlos sobre nuestra cuenta nos daba miedo perder el control de nuestro gasto, asi pues aunque no haya sido pedido asi en la practica posteriomente para ejecutar o la imagen o el docker compose deberemos añadir a la ejecucion los siguientes parametros -e AWS_ACCESS_KEY_ID='<<<<<nombre credencial>>>' -e AWS_SECRET_ACCESS_KEY='<<<<<nombre credencial>>>'
#mongo
en cuanto a estas variables nos permiten crear posteriomente el cliente de mongo donde insertaremos, en el host elegimos mongo pues es el que viene por defecto en la imagen y el puerto 27017 que tambien es el que la propia imagen hace el EXPOSE del puerto. Destacar en este caso que hemos elegido mongo por su flexibilidad a la hora de insertar datos puees dentro de la misma coleccion los documentos no dan de porque tener la misma longuitud ni las mismas claves, y ademas no es necesario especificar el tipo de dato cosa que si hubieramos eleguido cualquier base de datos SQL  tendriamos que haber definido previamente.

una vez definidas las variables de entorno con el comando CMD  decimos al contenedor que ejecute la siguiente instruccion "python  /app/jobmanager.py" asi pues lanzara el script guardado en la carpeta escogida. Destacar que usamos CMD  ya que hemos escogido por la practica usar variables de entorno, pero con ENTRYPOINT podria a ver sido otra solucion para pasar los argumentos del script en orden ya no como variables de entorno.

Una vez definido el servicio principal vamos a analizar la ejecuccion de la aplicacio. El archivo docker compose es el siguiente.


version: '3'
services:
  mongo:
    image: mongo
  tweetanalysis:
    image: javier162380/twitter_emr_sentiment_analysis
    depends_on:
      - mongo
    volumes:
      - /tmp:/tmp
    links:
      - mongo:db

En primer lugar hemos elegido la version:'3' de dockercompose al ser la mas actual y no encontrar problemas (aunque no hemos probado con la 2 tambien podria haber funcionado)
 como podemos observar definimos dos servicios. El primero es mongo, que viene de la imagen mongo la cual proviene del repositorio oficial en dockerhub. la segunda imagen del servicio tweetanalysis es 'javier162380/twitter_emr_sentiment_analysis' se puede encontrar tambien en dockerhub ya creada con el contenedor antes descrito. El argumento depends_on impide ejecutar el servicio tweetanalysis sin que el contenedor de mongo este levantado lo que nos evita errores a la hora de insertar. Posteriomente hemos creado un volumen dentro de /tmp (hemos escogido al ser unas de las ubicaciones que nos permitia MAC OS X) donde alojaremos los datos entre nuestra maquina y el contendor y nos permitira que al pausar no perdamos los datos analizados. Por ultimo el atributo links segun la doc de docker nos va a permitir que nos podamos conectar siempre en el puerto 27017 del contenedor con nuestra maquina y no tengamos ningun cambio.
