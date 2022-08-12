import logging
import shutil
import time
from functools import wraps
from typing import Optional

import click
import cosmotech_api

from .solution import Solution
from .configuration import Configuration

logger = logging.getLogger("Babylon")


def timing_decorator(func):
    """
    Decorator adding timings before and after the run of a function
    :param func: The function being decorated
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"{func.__name__} : Starting")
        start_time = time.time()
        func(*args, **kwargs)
        logger.debug(f"{func.__name__} : Ending ({time.time() - start_time:.2f}s)")

    return wrapper


def allow_dry_run(func):
    """
    Decorator adding dry_run parameter to the function call
    :param func: The function being decorated
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        solution: Solution = click.get_current_context().find_object(Solution)
        kwargs["dry_run"] = solution.dry_run
        func(*args, **kwargs)

    doc = wrapper.__doc__
    wrapper.__doc__ = doc + "\n\nAllows dry runs."
    return wrapper


def solution_requires_yaml_key(yaml_path: str, yaml_key: str, arg_name: Optional[str] = None):
    """
    Decorator allowing to check if the solution has specific key in a yaml file.
    If the check is failed the command won't run, and following checks won't be done
    :param yaml_path: the path in the solution to the yaml file
    :param yaml_key: the required key
    :param arg_name: optional parameter that will send the value of the yaml key to the given arg of the function
    """

    def wrap_function(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            solution: Solution = click.get_current_context().find_object(Solution)
            if solution.requires_yaml_key(yaml_path=yaml_path, yaml_key=yaml_key):
                if arg_name is not None:
                    kwargs[arg_name] = solution.get_yaml_key(yaml_path=yaml_path, yaml_key=yaml_key)
                    logger.debug(f"Adding parameter {arg_name} = {kwargs[arg_name]} to {func.__name__}")
                func(*args, **kwargs)
            else:
                logger.error(f"Key {yaml_key} can not be found in {yaml_path}")
                logger.error(f"{click.get_current_context().command.name} won't run without it.")
                raise click.Abort()

        doc = wrapper.__doc__
        wrapper.__doc__ = (doc +
                           f"\n\nRequires key `{yaml_key}` in `{yaml_path}` in the solution.")
        return wrapper

    return wrap_function


def solution_requires_file(file_path: str, arg_name: Optional[str] = None):
    """
    Decorator allowing to check if the solution has a specific file.
    If the check is failed the command won't run, and following checks won't be done
    :param file_path: the path in the solution to the required file
    :param arg_name: Optional parameter that if set will send the effective path of the required file to the given arg
    """

    def wrap_function(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            solution: Solution = click.get_current_context().find_object(Solution)
            if solution.requires_file(file_path=file_path):
                if arg_name is not None:
                    kwargs[arg_name] = solution.get_file(file_path=file_path)
                    logger.debug(f"Adding parameter {arg_name} = {kwargs[arg_name]} to {func.__name__}")
                func(*args, **kwargs)
            else:
                logger.error(f"Solution is missing {file_path}")
                logger.error(f"{click.get_current_context().command.name} won't run without it.")
                raise click.Abort()

        doc = wrapper.__doc__
        wrapper.__doc__ = (doc +
                           f"\n\nRequires the file `{file_path}` in the solution.")
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
                func(*args, **kwargs)
            else:
                logger.error(f"{program_name} is not installed.")
                logger.error(f"{click.get_current_context().command.name} won't run without it.")
                raise click.Abort()

        doc = wrapper.__doc__
        wrapper.__doc__ = (doc +
                           f"\n\nRequires the program `{program_name}` to run.")
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
            solution: Solution = click.get_current_context().find_object(Solution)
            config = solution.config
            if (key_value := config.get_platform_var(yaml_key)) is not None:
                if arg_name is not None:
                    kwargs[arg_name] = key_value
                    logger.debug(f"Adding parameter {arg_name} = {kwargs[arg_name]} to {func.__name__}")
                func(*args, **kwargs)
            else:
                logger.error(f"Key {yaml_key} can not be found in {config.get_platform_path()}")
                logger.error(f"{click.get_current_context().command.name} won't run without it.")
                raise click.Abort()

        doc = wrapper.__doc__
        wrapper.__doc__ = (doc +
                           f"\n\nRequires key `{yaml_key}` in the platform config file.")
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
            solution: Solution = click.get_current_context().find_object(Solution)
            config = solution.config
            if (key_value := config.get_deploy_var(yaml_key)) is not None:
                if arg_name is not None:
                    kwargs[arg_name] = key_value
                    logger.debug(f"Adding parameter {arg_name} = {kwargs[arg_name]} to {func.__name__}")
                func(*args, **kwargs)
            else:
                logger.error(f"Key {yaml_key} can not be found in {config.get_deploy_path()}")
                logger.error(f"{click.get_current_context().command.name} won't run without it.")
                raise click.Abort()

        doc = wrapper.__doc__
        wrapper.__doc__ = (doc +
                           f"\n\nRequires key `{yaml_key}` in the deployment config file.")
        return wrapper

    return wrap_function


pass_solution = click.make_pass_decorator(Solution)
pass_config = click.make_pass_decorator(Configuration)
pass_api_configuration = click.make_pass_decorator(cosmotech_api.Configuration)
