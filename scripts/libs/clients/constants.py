HARDCODED_DOCKER_COMPOSE_HEADER = """
version: '3.9'
name: tp0
services:
  server:
    container_name: server
    image: server:latest
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - LOGGING_LEVEL=DEBUG
    networks:
      - testing_net
    volumes:
      - ./config/server/config.ini:/config.ini
"""

HARDCODED_DOCKER_COMPOSE_BOTTOM = """
networks:
  testing_net:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24

"""
