from typing import Any
from uuid import uuid4

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
)


base_url = 'http://localhost:9999'

async def main() -> None:

    async with httpx.AsyncClient(timeout=60) as httpx_client:
        # Initialize A2ACardResolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
            # agent_card_path uses default, extended_agent_card_path also uses default
        )

        # Fetch Public Agent Card and Initialize Client
        final_agent_card_to_use: AgentCard | None = None

        try:

            _public_card = (
                    await resolver.get_agent_card()
                ) 
            print(_public_card.model_dump_json(indent=2, exclude_none=True))

            final_agent_card_to_use = _public_card

        except Exception as e:
            print(
                f'Critical error fetching public agent card: {e}'
            )
            raise RuntimeError(
                'Failed to fetch the public agent card. Cannot continue.'
            ) from e

        client = A2AClient(
            httpx_client=httpx_client, agent_card=final_agent_card_to_use
        )
        print('A2AClient initialized.')

        send_message_payload: dict[str, Any] = {
            'message': {
                'role': 'user',
                'parts': [
                    {'kind': 'text', 'text': 'Perform technical analysis on: TSLA, INTC, GOOGL, META.'}
                ],
                'messageId': uuid4().hex,
            },
        }
        request = SendMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )

        response = await client.send_message(request)
        print(response.model_dump(
            mode='json', 
            exclude_none=True
        ).get("result").get("artifacts")[0].get("parts")[0].get("text")
        )


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
