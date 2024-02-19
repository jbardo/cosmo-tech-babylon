from click import command
from Babylon.utils.decorators import injectcontext
from Babylon.utils.response import CommandResponse
from Babylon.utils.credentials import pass_azure_token
from Babylon.utils.decorators import output_to_file, retrieve_state, timing_decorator
from Babylon.services.security.solution_security_service import SolutionSecurityService


@command()
@injectcontext()
@timing_decorator
@pass_azure_token("csm_api")
@output_to_file
@retrieve_state
def get_users(state: dict, azure_token: str) -> CommandResponse:
    """
    Get the Solution security users list
    """
    service_state = state["services"]
    service = SolutionSecurityService(azure_token=azure_token, state=service_state)
    response = service.get_users()
    return CommandResponse.success(response, verbose=True)
