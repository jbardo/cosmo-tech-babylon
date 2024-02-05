import logging

from typing import Any, Optional
from click import Choice
from click import argument
from click import command
from click import option
from Babylon.commands.powerbi.workspace.user.service.api import (
    AzurePowerBIWorkspaceUserService,
)
from Babylon.utils.decorators import inject_context_with_resource, wrapcontext
from Babylon.utils.typing import QueryType
from Babylon.utils.response import CommandResponse
from Babylon.utils.credentials import pass_powerbi_token

logger = logging.getLogger("Babylon")


@command()
@wrapcontext()
@pass_powerbi_token()
@option("--workspace-id", "workspace_id", type=QueryType(), help="Workspace Id PowerBI")
@argument("email", type=QueryType())
@argument("type", type=Choice(["App", "Group", "User", "None"], case_sensitive=False))
@argument(
    "right",
    type=Choice(
        ["Admin", "Contributor", "Member", "Viewer", "None"], case_sensitive=False
    ),
)
@inject_context_with_resource({"powerbi": ["workspace"]})
def update(
    context: Any,
    powerbi_token: str,
    workspace_id: Optional[str],
    email: str,
    type: str,
    right: str,
) -> CommandResponse:
    """
    Updates an existing user in the power bi workspace
    """
    api_powerbi_work_user = AzurePowerBIWorkspaceUserService(
        powerbi_token=powerbi_token, state=context
    )
    response = api_powerbi_work_user.update(
        workspace_id=workspace_id, right=right, type=type, email=email
    )
    response = response.json()
    return CommandResponse.success(response)
