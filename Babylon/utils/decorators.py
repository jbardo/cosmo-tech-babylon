import logging
import shutil
import time
from functools import wraps
from typing import Optional

import click
import cosmotech_api

from .configuration import Configuration
from .environment import Environment
from .working_dir import WorkingDir
from ..version import get_version

logger = logging.getLogger("Babylon")


def prepend_doc_with_ascii(func):
    """
    Decorator used to add a babylon ascii art in the documentation of a function
    :param func: The function being decorated
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    babylon_ascii = ("\b", r" ____              __                 ___  ",
                     r"/\  _`\           /\ \               /\_ \  ",
                     r"\ \ \L\ \     __  \ \ \____   __  __ \//\ \      ___     ___  ",
                     r" \ \  _ <'  /'__`\ \ \ '__`\ /\ \/\ \  \ \ \    / __`\ /' _ `\  ",
                     r"  \ \ \L\ \/\ \L\.\_\ \ \L\ \\ \ \_\ \  \_\ \_ /\ \L\ \/\ \/\ \  ",
                     r"   \ \____/\ \__/.\_\\ \_,__/ \/`____ \ /\____\\ \____/\ \_\ \_\  ",
                     r"    \/___/  \/__/\/_/ \/___/   `/___/> \\/____/ \/___/  \/_/\/_/  ",
                     r"                                  /\___/  ", r"                                  \/__/  ",
                     f"                                                           v{get_version()}\n", "")
    doc = wrapper.__doc__
    wrapper.__doc__ = "\n".join(babylon_ascii) + doc
    return wrapper


def timing_decorator(func):
    """
    Decorator adding timings before and after the run of a function
    :param func: The function being decorated
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"{func.__name__} : Starting")
        start_time = time.time()
        resp = func(*args, **kwargs)
        logger.debug(f"{func.__name__} : Ending ({time.time() - start_time:.2f}s)")
        return resp

    return wrapper


def describe_dry_run(description: str):
    """
    Add a dry run description for the decorated call
    :param description: description to de displayed during dry runs (accepts markdown content)
    """

    def wrap_function(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper.dry_run = description
        return wrapper

    return wrap_function


def working_dir_requires_yaml_key(yaml_path: str, yaml_key: str, arg_name: Optional[str] = None):
    """
    Decorator allowing to check if the working_dir has specific key in a yaml file.
    If the check is failed the command won't run, and following checks won't be done
    :param yaml_path: the path in the working_dir to the yaml file
    :param yaml_key: the required key
    :param arg_name: optional parameter that will send the value of the yaml key to the given arg of the function
    """

    def wrap_function(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            working_dir: WorkingDir = click.get_current_context().find_object(Environment).working_dir
            if working_dir.requires_yaml_key(yaml_path=yaml_path, yaml_key=yaml_key):
                if arg_name is not None:
                    kwargs[arg_name] = working_dir.get_yaml_key(yaml_path=yaml_path, yaml_key=yaml_key)
                    logger.debug(f"Adding parameter {arg_name} = {kwargs[arg_name]} to {func.__name__}")
                return func(*args, **kwargs)

            logger.error(f"Key {yaml_key} can not be found in {yaml_path}")
            logger.error(f"{click.get_current_context().command.name} won't run without it.")
            raise click.Abort()

        doc = wrapper.__doc__ or ""
        wrapper.__doc__ = "\n\n".join([doc, f"Requires key `{yaml_key}` in `{yaml_path}` in the working_dir."])
        return wrapper

    return wrap_function


def working_dir_requires_file(file_path: str, arg_name: Optional[str] = None):
    """
    Decorator allowing to check if the working_dir has a specific file.
    If the check is failed the command won't run, and following checks won't be done
    :param file_path: the path in the working_dir to the required file
    :param arg_name: Optional parameter that if set will send the effective path of the required file to the given arg
    """

    def wrap_function(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            working_dir: WorkingDir = click.get_current_context().find_object(Environment).working_dir
            if working_dir.requires_file(file_path=file_path):
                if arg_name is not None:
                    kwargs[arg_name] = working_dir.get_file(file_path=file_path)
                    logger.debug(f"Adding parameter {arg_name} = {kwargs[arg_name]} to {func.__name__}")
                return func(*args, **kwargs)

            logger.error(f"Working_dir is missing {file_path}")
            logger.error(f"{click.get_current_context().command.name} won't run without it.")
            raise click.Abort()

        doc = wrapper.__doc__ or ""
        wrapper.__doc__ = "\n\n".join([doc, f"Requires the file `{file_path}` in the working_dir."])
        return wrapper

    return wrap_function


def requires_external_program(program_name: str):
    """
    Decorator allowing to check if a specific executable is available.
    If the check is failed the command won't run, and following checks won't be done
    :param program_name: the name of the required program
    """

    def wrap_function(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            if shutil.which(program_name) is not None:
                return func(*args, **kwargs)

            logger.error(f"{program_name} is not installed.")
            logger.error(f"{click.get_current_context().command.name} won't run without it.")
            raise click.Abort()

        doc = wrapper.__doc__ or ""
        wrapper.__doc__ = "\n\n".join([doc, f"Requires the program `{program_name}` to run."])
        return wrapper

    return wrap_function


def require_platform_key(yaml_key: str, arg_name: Optional[str] = None):
    """
    Decorator allowing to check if the platform in config has specific key
    If the check is failed the command won't run, and following checks won't be done
    :param yaml_key: the required key
    :param arg_name: optional parameter that will send the value of the yaml key to the given arg of the function
    """

    def wrap_function(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            config = click.get_current_context().find_object(Environment).configuration
            if (key_value := config.get_platform_var(yaml_key)) is not None:
                if arg_name is not None:
                    kwargs[arg_name] = key_value
                    logger.debug(f"Adding parameter {arg_name} = {kwargs[arg_name]} to {func.__name__}")
                return func(*args, **kwargs)

            logger.error(f"Key {yaml_key} can not be found in {config.get_platform_path()}")
            logger.error(f"{click.get_current_context().command.name} won't run without it.")
            raise click.Abort()

        doc = wrapper.__doc__ or ""
        wrapper.__doc__ = "\n\n".join([doc, f"Requires key `{yaml_key}` in the platform config file."])
        return wrapper

    return wrap_function


def require_deployment_key(yaml_key: str, arg_name: Optional[str] = None):
    """
    Decorator allowing to check if the deployment in config has specific key
    If the check is failed the command won't run, and following checks won't be done
    :param yaml_key: the required key
    :param arg_name: optional parameter that will send the value of the yaml key to the given arg of the function
    """

    def wrap_function(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            config = click.get_current_context().find_object(Environment).configuration
            if (key_value := config.get_deploy_var(yaml_key)) is not None:
                if arg_name is not None:
                    kwargs[arg_name] = key_value
                    logger.debug(f"Adding parameter {arg_name} = {kwargs[arg_name]} to {func.__name__}")
                return func(*args, **kwargs)

            logger.error(f"Key {yaml_key} can not be found in {config.get_deploy_path()}")
            logger.error(f"{click.get_current_context().command.name} won't run without it.")
            raise click.Abort()

        doc = wrapper.__doc__ or ""
        wrapper.__doc__ = "\n\n".join([doc, f"Requires key `{yaml_key}` in the deployment config file."])
        return wrapper

    return wrap_function


pass_working_dir = click.make_pass_decorator(WorkingDir)
pass_config = click.make_pass_decorator(Configuration)
pass_environment = click.make_pass_decorator(Environment)
pass_api_configuration = click.make_pass_decorator(cosmotech_api.Configuration)
