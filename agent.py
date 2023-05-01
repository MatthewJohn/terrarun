from argparse import ArgumentParser

from terrarun.agent import AgentProcessHandler, Agent, AgentConfig


parser = ArgumentParser('terrareg')

parser.add_argument('--address', dest='address',
                    help='Terrarun server address, e.g. https://my-terrarun.example.com',
                    required=True)
parser.add_argument('--token', dest='token',
                    help='Agent pool token to register agent',
                    required=True)

args = parser.parse_args()

agent_config = AgentConfig(address=args.address, token=args.token)

agent = Agent(agent_config=agent_config)

agent_runtime = AgentProcessHandler(agent=agent)
agent_runtime.start()
