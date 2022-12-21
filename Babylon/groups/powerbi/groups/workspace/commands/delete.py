import logging
from typing import Optional

import requests
from azure.core.credentials import AccessToken
from click import Context
from click import command
from click import option
from click import pass_context

from ......utils.decorators import require_deployment_key
from ......utils.interactive import confirm_deletion
from ......utils.typing import QueryType
from ......utils.response import CommandResponse

logger = logging.getLogger("Babylon")


@command()
@pass_context
@option("-w", "--workspace", "override_workspace_id", help="PowerBI workspace ID", type=QueryType())
@require_deployment_key("powerbi_workspace_id", required=False)
@option(
    "-f",
    "--force",
    "force_validation",
    is_flag=True,
    help="Don't ask for validation before delete",
)
def delete(ctx: Context, powerbi_workspace_id: str, override_workspace_id: Optional[str],
           force_validation: bool) -> CommandResponse:
    """Delete WORKSPACE_NAME from Power Bi APP"""
    access_token = ctx.find_object(AccessToken).token
    workspace_id = override_workspace_id or powerbi_workspace_id
    if not workspace_id:
        logger.error("A workspace id is required either in your config or with parameter '-w'")
        return CommandResponse(status_code=CommandResponse.STATUS_ERROR)
    if not force_validation and not confirm_deletion("Power Bi Workspace", workspace_id):
        return CommandResponse(status_code=CommandResponse.STATUS_ERROR)
    url_delete = f'https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}'
    header = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
    response = requests.delete(url=url_delete, headers=header)
    if response.status_code != 200:
        logger.error(f"Request failed:{response.text}")
        return
    logger.info(f"{workspace_id} was successfully removed from power bi app")
    return CommandResponse()
