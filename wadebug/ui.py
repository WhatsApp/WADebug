# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

import click

from wadebug import results

table_left_alignment = 63
table_right_aligment = 17


def print_line_break(color=None):
    click.secho('-'*80, bold=True, fg=color)


def print_program_header():
    click.secho('-'*80, bold=True)
    click.secho(
        'This tool will do some checks on the health '
        'of WhatsApp Business API setup',
        bold=True
    )
    click.secho('-'*80, bold=True)


def print_dev_mode_header():
    click.secho(
        'WADebug dev mode enabled. '
        'You will see full stacktrace when things go wrong',
        bold=True
    )
    print_line_break()


def get_result_color(result):
    color_map = {
        results.OK: 'green',
        results.Warning: 'yellow',
        results.Problem: 'red',
        results.Skipped: 'blue',
        results.WADebugError: 'red',
    }

    color = color_map.get(result.__class__)
    if not color:
        color = 'white'
    return color


def print_table_result_line(result):
    click.secho('{content:<{table_left_alignment}}'.format(
            content=result.action.user_facing_name,
            table_left_alignment=table_left_alignment,
        ),
        nl=False,
    )
    color = get_result_color(result)
    click.secho('{status:>{table_right_aligment}}'.format(
            status=result.result,
            table_right_aligment=table_right_aligment,
        ),
        fg=color,
    )


def print_table_header(column_1, column_2):
    fmt = '{column_1:<{table_left_alignment}}{column_2:>{table_right_aligment}}'
    click.secho(
        fmt.format(
            column_1=column_1,
            column_2=column_2,
            table_right_aligment=table_right_aligment,
            table_left_alignment=table_left_alignment,
        ),
        bold=True,
    )


def print_details_header(result):
    color = get_result_color(result)
    click.secho('-'*80, fg=color)
    click.secho(
        'PROBLEM: Details for {}'.format(result.action.user_facing_name),
        fg=color,
    )
    click.secho('-'*80, fg=color)


def print_invalid_config_message(config_file_path, ex):
    """Message to print when invalid yaml file is provided as config."""
    click.secho(
        '\nConfig file at {config_file_path} is invalid.'.format(
            config_file_path=os.path.join(os.getcwd(), config_file_path)
        ),
        fg='red')
    click.secho(
        'Make sure file contains valid yaml or rename it and wadebug will '
        'create a new empty config file. Execute command below to make a backup:\n')
    click.secho(
        '\tmv {config_file_path} {config_file_path}.bak\n'.format(
            config_file_path=config_file_path),
        bold=True)
    click.secho('Exception found:', bold=True)
    click.secho('{parsing_ex}\n'.format(parsing_ex=ex))


def print_dummy_tests():
    # Print a list of sample rows to a results table. Used for testing the UI
    print_table_result_line('Check MySQL - Not Implemented', status='warning')
    print_table_result_line(
        'Container can access internet - Not Implemented', status='warning')
    print_table_result_line('Get Logs - Not Implemented', status='ok')
    print_table_result_line(
        'Send a text message - Not Implemented', status='ok')
    print_table_result_line('Send an HSM - Not Implemented', status='ok')
    print_table_result_line('Send an image - Not Implemented', status='ok')
    print_table_result_line('Load Test - Not Implemented', status='problem')
