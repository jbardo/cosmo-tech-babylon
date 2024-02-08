import logging

from typing import Any, Optional
from Babylon.utils.typing import QueryType
from click import argument, command, option
from Babylon.utils.decorators import wrapcontext
from Babylon.utils.environment import Environment
from azure.mgmt.kusto import KustoManagementClient
from Babylon.utils.response import CommandResponse
from Babylon.utils.clients import pass_kusto_client
from Babylon.utils.decorators import retrieve_state, timing_decorator
from Babylon.commands.azure.adx.database.service.api import AdxDatabaseService

logger = logging.getLogger("Babylon")
env = Environment()


@command()
@wrapcontext()
@pass_kusto_client
@timing_decorator
@argument("name", type=QueryType(), required=False)
@option(
    "--retention", "retention", default=365, help="Retention days", show_default=True
)
@retrieve_state
def create(
    state: Any,
    kusto_client: KustoManagementClient,
    retention: int,
    name: Optional[str] = None,
) -> CommandResponse:
    """
    Create database in ADX cluster
    """
    service = AdxDatabaseService(kusto_client=kusto_client, state=state)
    service.create(name=name, retention=retention)
    return CommandResponse.success()
