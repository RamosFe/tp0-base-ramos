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
conocer este tamaño al leer los primeros 2 bytes del mensaje, evitando `short reads`. Un mensaje del procolo se ve
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

# Ejercicio 6
En el ejercicio 6 se agrego un nuevo separador para poder varios bets. Este separador separada los distintos
bets de la siguiente manera:
```
header bet|bet|bet|bet
```

De este manera el servidor simplemente debe seguir la misma lógica que el ejercicio anterior, pero primero separar
por el nuevo separador e ir obteniendo cada uno de los bets individualmente. Además se agrego un nuevo `env` variable:

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
mayores a `8192 (8KB en bytes)`.

# Ejercicio 7

Se modifica el protocolo para manejar distintos tipos de mensajes, cambiando la estructura a la siguiente:

```
msgType | header | payload
```

El `msgType` puede tomar varios valores:
- BetMsg: Representa un mensaje que contiene las apuestas de una agencia. Usado por el cliente para
enviar las apuestas.
- EndMsg: Representa un mensaje que señaliza la finalización del envio de apuestas. Usado por el cliente
para notificar al servidor que no se va a mandar más nuevas apuestas.
- WinnerMsg: Representa un mensaje con los documentos de los ganadores. Utilizado por el servidor para enviar
la información de los ganadores al cliente.

De esta manera, a la hora de decodificar, primero se leen los primers 2 bytes del mensaje para luego, dependiendo
del tipo, procesar la data de manera distinta. En el caso de el nuevo mensaje `WinnerMsg`, se trabaja igual que el
`BetMsg` nada más que en vez de leer bets en el payload, lee una lista de documentos.

## Flujo del cliente

El cliente empieza a leer los bets del archivo y enviando batches al servidor. Una vez que termina de enviar todas
las apuestas, envia un mensaje del tipo `EndMsg` para notificarle al servidor que ya no va a enviar más información.
Finalmente, el cliente se pone a esperar un mensaje del tipo `WinnerMsg` con los ganadores del sorteo.

## Flujo del servidor
Una vez que establece la conexión con el cliente, va recibiendo y parseando cada uno de los batches. Una vez que
recibe el mensaje con de tipo `EndMsg`, agrega 1 al contador interno del servidor y termina de esperar data del cliente.
Una vez que el contador llega al máximo, el servidor procesa los ganadores y va iterando por cada una de sus conexiones
para enviar un mensaje del tipo `WinnerMsg` con la información de los ganadores.
