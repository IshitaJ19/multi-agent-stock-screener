from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.utils import new_agent_text_message, new_task
from a2a.types import TaskState, TextPart

from google.genai import types as genai_types
from a2a.types import Part

from stock_screener.a2a_server.technical_analyst_agent import TechnicalAnalystAgent


class TechAnalystAgentExecutor(AgentExecutor):
    """Executor class for the Technical Analyst Agent"""

    def __init__(self):

        self.agent = None
        self.runner = None

        print("Initialized agent.")

    def _init_agent(self):

        agent_obj = TechnicalAnalystAgent()

        self.agent = agent_obj._agent
        self.runner = agent_obj._runner
        self.status_message = "Processing request..."
        self.artifact_name = "response"

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Cancel the execution of a specific task."""
        raise NotImplementedError(
            'Cancellation is not implemented for ADKAgentExecutor.'
        )

    async def execute(
            self, 
            context: RequestContext,
            event_queue: EventQueue
    ) -> None:
        """Execute the agent executor"""

        if not self.agent:
            self._init_agent()

        query = context.get_user_input()
        task = context.current_task or new_task(context.message)
        
        await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, task.context_id)

        if context.call_context:
            user_id = context.call_context.user.user_name
        else:
            user_id = 'a2a_user'

        try:
            # Update status with custom message
            await updater.update_status(
                TaskState.working,
                new_agent_text_message(
                    self.status_message, task.context_id, task.id
                ),
            )

            content = genai_types.Content(role='user', parts=[genai_types.Part(text=query)])
            session = await self.runner.session_service.get_session(
                app_name=self.runner.app_name,
                user_id=user_id,
                session_id=task.context_id,
            ) or await self.runner.session_service.create_session(
                app_name=self.runner.app_name,
                user_id=user_id,
                session_id=task.context_id,
            )

            response_text = ''

            events_async = self.runner.run_async(
                session_id=session.id, user_id=user_id, new_message=content
            )

            async for event in events_async:
                
                if (
                        event.is_final_response()
                        and event.content
                        and event.content.parts
                    ):
                      
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                response_text += part.text + '\n'
                            elif hasattr(part, 'function_call'):
                                # Log or handle function calls if needed
                                pass  # Function calls are handled internally by ADK

            # Add response as artifact with custom name
            await updater.add_artifact(
                [Part(root=TextPart(text=response_text))],
                name=self.artifact_name,
            )
            
            await updater.complete()

        except Exception as e:
            await updater.update_status(
                TaskState.failed,
                new_agent_text_message(
                    f'Error: {e!s}', task.context_id, task.id
                ),
                final=True,
            )
            