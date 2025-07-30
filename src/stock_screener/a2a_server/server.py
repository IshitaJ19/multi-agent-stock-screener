import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

from stock_screener.a2a_server.agent_card import public_agent_card
from stock_screener.a2a_server.agent_executor import TechAnalystAgentExecutor

from stock_screener.utils.read_env_vars import ENV


ENV.export_google_api_key()

def main():

    request_handler = DefaultRequestHandler(
        agent_executor=TechAnalystAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler,
        extended_agent_card=public_agent_card,
    )

    uvicorn.run(server.build(), host='0.0.0.0', port=9999)


if __name__ == "__main__":

    main()

