import logging
from pprint import pformat

import cosmotech_api
from click import argument
from click import command
from click import make_pass_decorator
from click import option
from cosmotech_api.api.solution_api import SolutionApi

from ......utils.api import get_api_file
from ......utils.decorators import env_requires_yaml_key
from ......utils.decorators import pass_environment
from ......utils.decorators import timing_decorator

logger = logging.getLogger("Babylon")

pass_solution_api = make_pass_decorator(SolutionApi)


@command()
@pass_solution_api
@pass_environment
@argument("solution_file")
@option("-e", "--use-environment-file", "use_environment_file", is_flag=True,
        help="Should the path be in the environment ?")
@env_requires_yaml_key("deploy.yaml", "organization_id", "organization_id")
@env_requires_yaml_key("deploy.yaml", "solution_id", "solution_id")
@timing_decorator
def update(environment,
           solution_api: SolutionApi,
           organization_id: str,
           solution_id: str,
           solution_file: str,
           use_environment_file: bool = False):
    """Send a JSON or YAML file to the API to update a solution"""

    if (converted_solution_content := get_api_file(api_file_path=solution_file,
                                                   use_environment_file=use_environment_file,
                                                   environment=environment,
                                                   logger=logger)) is not None:
        try:
            r = solution_api.update_solution(organization_id=organization_id,
                                             solution_id=solution_id,
                                             solution=converted_solution_content)
            logger.debug(pformat(r))
            logger.info(f"Updated solution with id: {r['id']}")
        except cosmotech_api.exceptions.NotFoundException as _e:
            logger.error(f"Solution {solution_id} does not exists in organization {organization_id}.")
        except cosmotech_api.exceptions.UnauthorizedException as _e:
            logger.error("Unauthorized access to the cosmotech api")
