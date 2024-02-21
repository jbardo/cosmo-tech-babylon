import json
import pathlib

from logging import getLogger
from Babylon.utils.environment import Environment
from azure.core.exceptions import HttpResponseError
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import Deployment
from azure.mgmt.resource.resources.models import DeploymentMode
from azure.mgmt.resource.resources.models import DeploymentProperties

from Babylon.utils.interactive import confirm_deploy_arm_mode
from Babylon.utils.response import CommandResponse

logger = getLogger("Babylon")
env = Environment()


class ArmService:

    def __init__(self, state: dict, arm_client: ResourceManagementClient) -> None:
        self.state = state
        self.arm_client = arm_client

    def run(self, deployment_name: str, deploy_mode_complete: bool = False):
        resource_group_name = self.state["azure"]["resource_group_name"]
        deploy_file = pathlib.Path(
            env.convert_template_path("%templates%/arm/eventhub_deploy.json")
        )
        mode = DeploymentMode.INCREMENTAL
        if deploy_mode_complete:
            logger.warn(
                """Warning: In complete mode\n
                        Resource Manager deletes resources that exist in the resource group,\n
                        but aren't specified in the template."""
            )
            if confirm_deploy_arm_mode():
                mode = DeploymentMode.COMPLETE

        if not deploy_file:
            logger.error("Deploy file not found")
            return CommandResponse.fail()
        arm_template = env.fill_template(deploy_file)
        arm_template = json.loads(arm_template)
        parameters = {
            k: {"value": v["defaultValue"]}
            for k, v in dict(arm_template["parameters"]).items()
        }
        logger.info("Starting deployment")
        try:
            poller = self.arm_client.deployments.begin_create_or_update(
                resource_group_name=resource_group_name,
                deployment_name=deployment_name,
                parameters=Deployment(
                    properties=DeploymentProperties(
                        mode=mode, template=arm_template, parameters=parameters
                    )
                ),
            )
            poller.wait()
            if not poller.done():
                return CommandResponse.fail()
        except HttpResponseError as _e:
            logger.error(f"An error occurred : {_e.message}")
            return CommandResponse.fail()
        logger.info("Provisioning state: successful")
        return CommandResponse.success()
