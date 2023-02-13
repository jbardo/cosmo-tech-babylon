import logging
import pathlib
from string import Template

from azure.core.credentials import AccessToken
from click import command
from click import pass_context
from click import Context
from click import option
from click import argument
from click import Path

from ........utils.request import oauth_request
from ........utils.response import CommandResponse
from ........utils.environment import Environment

logger = logging.getLogger("Babylon")


@command()
@pass_context
@argument("registration_id")
@option("-f",
        "--file",
        "registration_file",
        type=Path(readable=True, dir_okay=False, path_type=pathlib.Path),
        required=True)
@option("-e",
        "--use-working-dir-file",
        "use_working_dir_file",
        is_flag=True,
        help="Should the parameter file path be relative to Babylon working directory ?")
def update(ctx: Context,
           registration_id: str,
           registration_file: str,
           use_working_dir_file: bool = False) -> CommandResponse:
    """
    Update an app registration in active directory
    https://learn.microsoft.com/en-us/graph/api/application-update
    """
    access_token = ctx.find_object(AccessToken).token
    route = f"https://graph.microsoft.com/v1.0/applications/{registration_id}"
    env = Environment()
    if use_working_dir_file:
        registration_file = env.working_dir.get_file(str(registration_file))
    details = ""
    with open(registration_file, "r") as _file:
        template = _file.read()
        data = {**env.configuration.get_deploy(), **env.configuration.get_platform()}
        try:
            details = Template(template).substitute(data)
        except Exception as e:
            logger.error(f"Could not fill parameters template: {e}")
            return CommandResponse.fail()
    response = oauth_request(route, access_token, type="PATCH", data=details)
    if response is None:
        return CommandResponse.fail()
    logger.info(f"Successfully updated registration {registration_id}")
    return CommandResponse.success()
