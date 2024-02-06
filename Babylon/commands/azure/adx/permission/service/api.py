import logging

from pprint import pformat
from uuid import uuid4
from azure.mgmt.kusto import KustoManagementClient
from Babylon.utils.interactive import confirm_deletion
from Babylon.utils.response import CommandResponse
from azure.mgmt.kusto.models import DatabasePrincipalAssignment


logger = logging.getLogger("Babylon")


class AdxPermissionService:

    def __init__(self, kusto_client: KustoManagementClient, state: dict = None) -> None:
        self.state = state
        self.kusto_client = kusto_client

    def set(
        self,
        principal_id: str,
        principal_type: str,
        role: str,
    ):
        resource_group_name = self.state["azure"]["resource_group_name"]
        adx_cluster_name = self.state["adx"]["cluster_name"]
        database_name = self.state["adx"]["database_name"]
        parameters = DatabasePrincipalAssignment(
            principal_id=principal_id, principal_type=principal_type, role=role
        )
        principal_assignment_name = str(uuid4())
        logger.info("Creating assignment...")
        poller = self.kusto_client.database_principal_assignments.begin_create_or_update(
            resource_group_name,
            adx_cluster_name,
            database_name,
            principal_assignment_name,
            parameters,
        )
        if poller.done():
            logger.info("Successfully created")

    def delete(
        self,
        principal_id: str,
        force_validation: bool,
    ):
        resource_group_name = self.state["azure"]["resource_group_name"]
        adx_cluster_name = self.state["adx"]["cluster_name"]
        database_name = self.state["adx"]["database_name"]
        assignments = self.kusto_client.database_principal_assignments.list(
            resource_group_name, adx_cluster_name, database_name
        )
        entity_assignments = [
            assign for assign in assignments if assign.principal_id == principal_id
        ]
        if not entity_assignments:
            logger.error(f"No assignment found for principal ID {principal_id}")
            return CommandResponse.fail()

        logger.info(
            f"Found {len(entity_assignments)} assignments for principal ID {principal_id}"
        )
        for assign in entity_assignments:
            if not force_validation and not confirm_deletion(
                "permission", str(assign.role)
            ):
                return CommandResponse.fail()

            logger.info(
                f"Deleting role {assign.role} to principal {assign.principal_type}:{assign.principal_id}"
            )
            assign_name: str = str(assign.name).split("/")[-1]
            self.kusto_client.database_principal_assignments.begin_delete(
                resource_group_name,
                adx_cluster_name,
                database_name,
                principal_assignment_name=assign_name,
            )

    def get(self, principal_id: str):
        resource_group_name = self.state["azure"]["resource_group_name"]
        adx_cluster_name = self.state["adx"]["cluster_name"]
        database_name = self.state["adx"]["database_name"]
        assignments = self.kusto_client.database_principal_assignments.list(
            resource_group_name, adx_cluster_name, database_name
        )
        entity_assignments = [
            assignment
            for assignment in assignments
            if assignment.principal_id == principal_id
        ]
        if not entity_assignments:
            logger.info(f"No assignment found for principal ID {principal_id}")
            return CommandResponse.fail()
        logger.info(
            f"Found {len(entity_assignments)} assignments for principal ID {principal_id}"
        )
        for ent in entity_assignments:
            logger.info(f"{pformat(ent.__dict__)}")
        return entity_assignments

    def get_all(self):
        logger.info("Getting assignments...")
        resource_group_name = self.state["azure"]["resource_group_name"]
        adx_cluster_name = self.state["adx"]["cluster_name"]
        database_name = self.state["adx"]["database_name"]
        assignments = self.kusto_client.database_principal_assignments.list(
            resource_group_name, adx_cluster_name, database_name
        )
        for ent in assignments:
            logger.info(f"{pformat(ent.__dict__)}")
        return assignments
