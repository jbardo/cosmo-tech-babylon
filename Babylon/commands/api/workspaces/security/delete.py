import logging

from click import argument, command
from Babylon.commands.api.workspaces.security.service.api import ApiWorkspaceSecurityService
from Babylon.utils.decorators import wrapcontext
from Babylon.utils.environment import Environment
from Babylon.utils.response import CommandResponse
from Babylon.utils.credentials import pass_azure_token
from Babylon.utils.decorators import output_to_file, retrieve_state, timing_decorator

logger = logging.getLogger("Babylon")
env = Environment()


@command()
@wrapcontext()
@timing_decorator
@pass_azure_token("csm_api")
@output_to_file
@argument("id", type=str)
@retrieve_state
def delete(state: dict, azure_token: str, id: str) -> CommandResponse:
    """
    Delete workspace users RBAC access
    """
    service_state = state["services"]
    service = ApiWorkspaceSecurityService(azure_token=azure_token, state=service_state)
    response = service.delete(id=id)
    return CommandResponse.success(response, verbose=True)
