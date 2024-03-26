# TP0: Docker + Comunicaciones + Concurrencia - Ramos Federico 101640
## Ejercicio 1

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
