# TP0: Docker + Comunicaciones + Concurrencia - Ramos Federico 101640
# Ejercicio 1

Para la primer parte del ejercicio, se agrego un nuevo cliente al archivo `docker-compose`. Para esto
se agrego las siguientes líneas:

```
  client2:
    container_name: client2
    image: client:latest
    entrypoint: /client
    environment:
      - CLI_ID=2
      - CLI_LOG_LEVEL=DEBUG
    networks:
      - testing_net
    depends_on:
      - server
```

La diferencia entre el primer cliente y el segundo son los cambios de `tag` de `yaml`, el nombre del container
especificado con `container_name` y el environmet variable `CLI_ID` que especifica el ID del cliente.

Para la segunda parte del ejercicio, se desarrollo el script `variable-clients.py`, que permite crear dinámicamente
un nuevo archivo `docker-compose` con un `N` cantidad de clientes. El script se encuentra en `scripts/variable-clients.py`
y se ejecuta de la siguiente manera:

```
python3 scripts/variable-clients.py N
```

Donde `N` es la cantidad de clientes a crear. Este script genera un archivo en la carpeta `scripts` con el siguiente
formato `docker-compose-clients{N}.yaml` donde `N` es la cantidad de clientes. Ejemplo: Si se ejecuta con `N=5` entonces
el nombre del nuevo archivo es `docker-compose-clients5.yaml`

# Ejercicio 2
Para el segundo ejercicio se agregaron volumenes y mount binds para mapear la configuración dentro del host con
los contenidos dentro del container de la siguiente manera:

```
  server:
    container_name: server
    ...
    volumes:
      - ./config/server/config.ini:/config.ini

  client2:
    container_name: client2
    ...
    volumes:
      - ./config/client/config.yaml:/config.yaml
```

El mount bind nos permite inyectar la configuración de cada uno de los containers sin la necesidad
de rebuildear la imagen, al igual que nos permite hacer la aplicación más segura debido a que la configuración
no queda persistida en la imagen a la hora de buildearla.

# Ejercicio 3
Para el ejercicio 3 se creo el script `scripts/netcat-script.sh`:

```
RESPONSE=$(echo "Testing Message" | nc "server:12345")
echo "$RESPONSE"

```

El script se encarga de enviar un mensaje al servidor e imprimir el resultado que devuelve el servidor. Para ejecutar
este script dentro de la red que levanta `docker` se agrego un nuevo servicio a la definición del `docker-compose`:

```
  netcat:
    container_name: netcat
    image: alpine:latest
    entrypoint: [ "/bin/sh", "./netcat-script.sh" ]
    profiles: [netcat]
    networks:
      - testing_net
    depends_on:
      - server
    volumes:
      - ./scripts/netcat-script.sh:/netcat-script.sh
```

Este servicio usa como imagen base `alpine:latest`. Se utilizo esta imagen debido a que tiene todas
las funcionalidades necesarias y solo pesa `5MB`, haciendola ideal para la ejecución de scripts de este
estilo. Además se utilizo un mount bind para mappear el script en la maquina host con el container y asi
poder probar el script sin necesidad de rebuildear la imagen.

Tambien se agregaron nuevos targets en el `Makefile` para el manejo de docker compose con el profile `netcat`. Los
nuevos targets son los siguientes:
- `docker-compose-netcat-up`: Equivalente a `docker-compose-up` pero usando el `profile` netcat.
- `docker-compose-netcat-logs`: Equivalente a `docker-compose-logs` pero usando el `profile` netcat.
- `docker-compose-netcat-down`: Equivalente a `docker-compose-down` pero usando el `profile` netcat.

> Aclaración: Si se utiliza `docker-compose-netcat-up` para levantar el ambiente, se debe utilizar los targets
> que incluyen el `profile` netcat para acceder a los logs y para terminar su ejecución y remover los
> respectivos containers, networks, volumenes, e imágenes.


# Ejercicio 4
### Cliente
Para el caso del cliente se agrego un `channel` encargado de recibir un mensaje cuando se triggerea un `SIGTERM`:

```
	// Channel that is notified on SIGTERM
	sigTermChannel := make(chan os.Signal, 1)
	signal.Notify(sigTermChannel, syscall.SIGTERM)
```

Una vez seteado el channel, se le pasa a la función `StartClientLoop` donde se utiliza un `select` para
responder al primer "evento" que ocurra primero. Hay 3 posibles eventos:
- Timeout Loop: El primer evento es triggereado cuando se pasa el tiempo configurado en `loop.lapse` que especifica
  la duración del loop del cliente.
- signalChan: El segundo evento es triggereado cuando se recibe la notificación del `SIGTERM`.
- Timeout LoopPeriod: El tercer evento es triggeread cuando se pasa el tiempo configurado en `loop.period` que determina
  el periodo de tiempo a esperar entre cada mensaje.

```
		select {
		case <-timeout:
			log.Infof("action: timeout_detected | result: success | client_id: %v",
				c.config.ID,
			)
			break loop
		case <-signalChan:
			log.Infof("action: sigterm_detected | result: shutdown | client_id: %v",
				c.config.ID,
			)
			break loop

		// Wait a time between sending one message and the next one
		case <-time.After(c.config.LoopPeriod):
```

### Servidor
En el caso del server se agregaron las siguientes lineas:

```
        # Define signal handlers
        signal.signal(signal.SIGINT, self.__handle_signal)
        signal.signal(signal.SIGTERM, self.__handle_signal)
```

Esto define `handlers` para cuando llegue las `signals` `SIGINT` y `SIGTERM`. El método `__handle_signal`
se encarga de cerrar todos los sockets activos de clientes, luego el socket del servidor y finalmente dar
de baja el mismo.

# Ejercicio 5
Se agrega un protocolo que se compone de la siguiente manera:
- Header: Un número de 2 bytes que representa el tamaño del payload.
- Payload: El contenido del mensaje

Este estructura para el protocolo nos permite mandar mensajes de un tamaño variable , permitiendo al servidor
conocer este tamaño al leer los primeros 2 bytes del mensaje. Un mensaje del procolo se ve
de la siguiente manera:
```go
// Ejemplo de estructura de un mensaje
type Message struct {
	header  uint16
	payload []byte
}
```

En el caso del ejercicio 5 el `payload` esta compuesto por los campos de un `Bet`. En el protocolo, el orden de los
campos es el siguiente, donde cada campo es separado por un separador, en este caso `,`:

```
nombre,apellido,documento,cumpleaños,numero
```

Que bet envia cada cliente es seteado utilizando `env` variables de la siguiente manera:
```
  client2:
    container_name: client2
    image: client:latest
    entrypoint: /client
    environment:
      - CLI_ID=2
      - CLI_LOG_LEVEL=DEBUG
      - NOMBRE=Federico
      - APELLIDO=Ramos
      - DOCUMENTO=40566677
      - NACIMIENTO=1997-09-19
      - NUMERO=6000
```

Una vez que el `Bet` es enviado por socket, el cliente espera un `ACK` (compuesto principalmente por un mensaje
que retorna `1` o `0` dependiendo de si hay un error o no).

En el caso del servidor, al recibir un mensaje del cliente, leer los primeros 2 bytes para obtener el tamaño del `payload`.
Una vez obtenido el tamaño `N`, lee los proximos `N` bytes para obtener el mensaje completo, separa los fields
utilizando el separador y obtiene el bet que luego almacena utilizando `store_bets`. Una vez almacenado, manda un ACK
al cliente.

## Manejo de Short Read/ Short Write

Para el manejo de este tipo de errores se creo una abstracción, tanto en el cliente como en el servidor. Para esta explicación
vamos a usar de ejemplo el código del servidor. En el caso de la lectura, se valida la cantidad de bytes enviados y se
vuelve a enviar hasta que se alcanza la cantidad esperada. En el caso de la escritura, se pasa un expected size y se
lee del socket hasta recibir la cantidad de bytes esperados, como se muestra en el código:

```python
    def send(self, msg: bytes):
        data_sent = 0
        while data_sent < len(msg):
            bytes_sent = self._internal_socket.send(msg)
            if bytes_sent == 0:
                raise OSError("connection was closed")

            data_sent += bytes_sent

    def recv(self, size: int) -> bytes:
        buffer = []
        data_read = 0

        while data_read < size:
            expected_size = size - data_read
            data = self._internal_socket.recv(expected_size)
            if data == b'':
                raise OSError("connection was closed")

            data_read += len(data)
            buffer.append(data)
```

> En el caso del cliente, tambien se debe tener en cuenta que al utilizar `Write`, este devuelve el error `ErrShortWrite`
> en caso de un short write y se debe tener en cuenta este error para replicar la misma lógica que se usa en el server.

# Ejercicio 6
En el ejercicio 6 se agrego un nuevo separador para poder varios bets. Este separador separada los distintos
bets de la siguiente manera:
```
header bet|bet|bet|bet
```

De este manera el servidor simplemente debe seguir la misma lógica que el ejercicio anterior, pero primero separar
por el nuevo separador e ir obteniendo cada uno de los bets individualmente. Tambien se agrega un nuevo mensaje para
señalizar al servidor que se termino el envio de bets.

## Batch Size variable

El batch size es configurable a traves de una nueva `env` variable:

```
  client2:
    container_name: client2
    image: client:latest
    entrypoint: /client
    environment:
      - CLI_ID=2
      - CLI_LOG_LEVEL=DEBUG
      - BETFILE=/agency.csv
      - BATCHSIZE=8000
```

`BATCHSIZE` especifica el tamaño máximo de un batch y este mismo puede tener un valor de hasta `8KB`, por esta
razón el `header` es representado por un `uint16` que ocupa 2 bytes y puede representar números
mayores a `8192 (8KB en bytes)`

## Cambios en el protocolo

Se cambio la estructura del protocolo para poder abarcar distintos tipos de mensajes. Ahora el protocolo puede tener 2
formatos:
```
# Mensaje con contenido
msgType (1 byte) | header (2 byte) | payload (variable)

# Mensaje para señalizar un cambio (Ej: fin de envio de batches, cerrado de conexión)
msgType (1 byte)
```

Al agregar el byte que representa el `msgType` podemos manejar distintos tipos de mensajes y distintos tipos de paquetes
para no tener que usar el formato `header | payload` para mensajes que solo sirven para señalizar algun evento al
servidor.

# Ejercicio 7

Se agregan varios tipos de mensajes para consultar los winners al servidor:
- Request Winner: Utilizado por el cliente para pedirle los winners a el servidor.
- Available Winners: Utilizado por el servidor para responder con una lista de DNI de los winners de la agencia.
- Unavailable Winners: Utilizado por el servidor para notificar al cliente que todavia no estan disponibles los ganadores

Una vez que el cliente termina de enviar todos los bets, empieza un loop en el que le pide al servidor la información de 
los winners. En caso de que esta información no esta disponible, espera un tiempo y se vuelve a pedir la información. El
tiempo de espera va creciendo a lo largo del tiempo, como se muestra en el siguiente código:
```go
timeToSleep := 0.5

for true {
	c.createClientSocket()
    result, err := sendRequestWinner(c.conn, c.id)
    if err != nil && err != NotAvailableWinnersErr {
        log.Errorf("action: consulta_ganadores | result: fail | msg: %v", err)
        sendCloseConnection(c.conn)
        c.conn.Close()
        return
    }

  
    if err != NotAvailableWinnersErr {
        log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %v", len(result))
        sendCloseConnection(c.conn)
        c.conn.Close()
        return
    } else {
        log.Infof("action: consulta_ganadores | result: not_available | msg: retrying in %v seconds",
        timeToSleep)
        time.Sleep(time.Duration(timeToSleep) * time.Second)
        timeToSleep *= 2
	}


    sendCloseConnection(c.conn)
    c.conn.Close()
}
```

> Aclaración: Debido que para el ej7 todavia se utiliza un servidor que solo puede manejar 1 cliente a la vez
> el cliente cierra la conexion y vuelve a conectarse para cada request de winners. Esta lógica es reemplazada para el ej8
> donde el servidor puede manejar varios clientes al mismo tiempo.

# Ejercicio 8

Para el ejercicio 8 se utilizo la libreria de `multiprocessing` de Python. Los principales 2 componentes de la solución
son:
- Pool: Se utiliza un pool de procesos para la creación de nuevos procesos. Cuando se conecta un nuevo cliente al servidor
este crea un proceso en el pool. Se utiliza el `Context Manager` del pool para manejar el shutdown de los procesos y del
pool de manera automática una vez que se sale del contexto.
- Manager: Debido a que tenemos 2 funciones que no pueden ser accedidas concurrentemente (`store_bets` y `load_bets`),
se utiliza un Manager para poder compartila entre varios procesos. Este Manager se encarga de garantizar que no haya 2
procesos utilizando el `StoreManager` al mismo tiempo, permitiendo compartir el recurso entre varios procesos.

El `StorageManager` se encarga de manejar todo lo relacionado a los bets, al igual que mantener el conteo de cuantos
agentes enviaron sus bets para validar si se puede acceder o no a los winners:

```python
class StoreManager:
    def __init__(self, number_of_agencies: int):
        self._expected_agencies = number_of_agencies
        self._finished_agencies = 0

    def winners_available(self) -> bool:
        return self._expected_agencies == self._finished_agencies

    def notify_agency_finished(self):
        self._finished_agencies += 1

        if self.winners_available():
            logging.info("action: sorteo | result: success")

    def store_bet(self, bets: List[Bet]):
        store_bets(bets)

    def get_winners(self, agency_id) -> List[Bet]:
        bets = load_bets()
        winners = list(filter(lambda x: has_won(x) and x.agency == agency_id, bets))
        return winners

```