from libs.clients.client_builder import ClientStrBuilder
from libs.clients.constants import HARDCODED_DOCKER_COMPOSE_HEADER, HARDCODED_DOCKER_COMPOSE_BOTTOM
from libs.clients.cli_args import parser


if __name__ == '__main__':
    args = parser.parse_args()

    text_to_add = [HARDCODED_DOCKER_COMPOSE_HEADER]
    client_builder = ClientStrBuilder()
    for i in range(1, args.clients + 1):
        text_to_add.append(str(client_builder.build(i)))
    text_to_add.append(HARDCODED_DOCKER_COMPOSE_BOTTOM)

    with open(f'docker-compose-clients{args.clients}.yaml', 'w') as file:
        file.write('\n'.join(text_to_add))

