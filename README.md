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
