# -*- coding: utf-8 -*-

# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import, division, print_function, unicode_literals

import os

import click
from wadebug import results
from wadebug.config import Config


table_left_alignment = 63
table_right_aligment = 17

color_map = {
    results.OK: "green",
    results.Warning: "yellow",
    results.Problem: "red",
    results.Skipped: "blue",
    results.WADebugError: "red",
}

indicator_icon_map = {
    results.OK: "✓",
    results.Warning: "!",
    results.Problem: "✗",
    results.Skipped: "-",
    results.WADebugError: "✗",
}


def print_program_header():
    click.secho("WADebug summary: ", bold=True, nl=False)


def print_dev_mode_header():
    click.secho("(DEV mode enabled)")


def print_result_header(result):
    result_type = result.__class__
    indicator_icon = get_result_indicator_icon(result_type)
    indicator_color = get_result_color(result_type)

    click.secho("[{}] ".format(indicator_icon), fg=indicator_color, nl=False)

    click.secho(
        "{} - {}".format(
            result.action.user_facing_name, result.action.short_description
        )
    )


def get_result_color(result_type):
    color = color_map.get(result_type)
    if not color:
        color = "white"
    return color


def get_result_indicator_icon(result_type):
    indicator_icon = indicator_icon_map.get(result_type)
    if not indicator_icon:
        indicator_icon = " "
    return indicator_icon


def print_result_details(result):
    for field in [result.message, result.details, result.remediation]:
        click.echo(add_indentation_to_result_field(field))

    if Config().development_mode and hasattr(result, "traceback"):
        click.echo(add_indentation_to_result_field(result.traceback))


def add_indentation_to_result_field(str):
    return "\n".join(["    " + line for line in str.split("\n")])


def print_invalid_config_message(config_file_path, ex):
    """Message to print when invalid yaml file is provided as config."""
    click.secho(
        "\nConfig file at {config_file_path} is invalid.".format(
            config_file_path=os.path.join(os.getcwd(), config_file_path)
        ),
        fg="red",
    )
    click.secho(
        "Make sure file contains valid yaml or rename it and wadebug will "
        "create a new empty config file. Execute command below to make a backup:\n"
    )
    click.secho(
        "\tmv {config_file_path} {config_file_path}.bak\n".format(
            config_file_path=config_file_path
        ),
        bold=True,
    )
    click.secho("Exception found:", bold=True)
    click.secho("{parsing_ex}\n".format(parsing_ex=ex))
