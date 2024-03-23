import argparse

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

"""

HARDCODED_DOCKER_COMPOSE_BOTTOM = """
networks:
  testing_net:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24

"""


class IndentedWithSpacesString:
    def __init__(self, string: str, indentations: int):
        self._string = string
        self._indentations = indentations

    def __str__(self):
        return ' ' * self._indentations + self._string


class ClientStrBuilder:
    def build(self, id: int):
        dynamic_lines = [
            IndentedWithSpacesString(f'client{id}:', 2),
            IndentedWithSpacesString(f'container_name: client{id}', 4),
            IndentedWithSpacesString('image: client:latest', 4),
            IndentedWithSpacesString('entrypoint: /client', 4),
            IndentedWithSpacesString('environment:', 4),
            IndentedWithSpacesString(f'- CLI_ID={id}', 6),
            IndentedWithSpacesString('- CLI_LOG_LEVEL=DEBUG', 6),
            IndentedWithSpacesString('networks:', 4),
            IndentedWithSpacesString('- testing_net', 6),
            IndentedWithSpacesString('depends_on:', 4),
            IndentedWithSpacesString('- server', 6)
        ]

        final_result = "\n".join(map(lambda x: str(x), dynamic_lines))
        return final_result


def check_if_positive(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError(f"The value {value} is not a positive number")
    return number


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Dynamic client builder")
    parser.add_argument("clients", type=check_if_positive, help="A positive integer greater than 0 that represents the "
                                                                "number of clients to add")
    args = parser.parse_args()

    text_to_add = [HARDCODED_DOCKER_COMPOSE_HEADER]
    client_builder = ClientStrBuilder()
    for i in range(1, args.clients + 1):
        text_to_add.append(str(client_builder.build(i)))
    text_to_add.append(HARDCODED_DOCKER_COMPOSE_BOTTOM)

    with open(f'docker-compose-clients{args.clients}.yaml', 'w') as file:
        file.write('\n'.join(text_to_add))

