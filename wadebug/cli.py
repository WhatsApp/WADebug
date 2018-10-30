# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from wadebug import results
from wadebug import ui
from wadebug import wa_actions
from wadebug import cli_utils
from wadebug.cli_param import wadebug_option, ReusableParam

import json
import os
import pkg_resources
import sys
import yaml

import click


# Change to True to enable easier investigation of wadebug issues
DEVELOPMENT_MODE = False

# Disabling warning as using unicode_literals is considered ok
# when back-porting Python3 to Python2/3
# http://python-future.org/imports.html#should-i-import-unicode-literals
click.disable_unicode_literals_warning = True

SAMPLE_CONFIG_FILE = 'wadebug.conf.yml.SAMPLE'
CONFIG_FILE = 'wadebug.conf.yml'


def safe_main():
    try:
        main()
    except Exception as e:
        if DEVELOPMENT_MODE:
            raise

        print(
            'An error occurred with WADebug:\n{}\n'.format(e),
            'Please report this via Direct Support (https://business.facebook.com/direct-support) ',
            'and paste this full error message.'
        )


opt_out = ReusableParam(
    '--do-not-send-usage',
    'opt_out',
    help='Pass this flag to opt out from sending usage to WhatsApp. Sending '
         'usage to WhatsApp could accelerate Direct Support ticket resolve time.',
    is_flag=True,
    default=False,
)

json_output = ReusableParam(
    '--json',
    'json',
    help='Pass this flag to output results in json format. This enables '
    'automation and integration with other applications if needed.',
    is_flag=True,
    default=False,
)

send_logs = ReusableParam(
    '--send-logs',
    'send_logs',
    help='Pass this flag to send WhatsApp Business API container logs '
    'to WhatsApp. Not available in json mode.',
    is_flag=True,
    default=False,
)


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(pkg_resources.get_distribution('wadebug').version)
@wadebug_option(opt_out)
@wadebug_option(json_output)
@wadebug_option(send_logs)
def main(ctx, **kwargs):
    """Investigate issues with WhatsApp Business API setup."""

    # Program entry point. When no arguments, executes full_debug.
    # Else execute specific command (click handles this case implicitly)

    # used to pass variables between commands and sub-commands
    if ctx.invoked_subcommand is None:
        ctx.invoke(full_debug)


@main.command()
@click.pass_context
@wadebug_option(json_output)
def ls(ctx, **kwargs):
    """Print a list of possible debug actions."""
    acts = wa_actions.get_all_actions()
    if ctx.obj.get('json', False):
        click.echo(
            json.dumps({
                'actions': [act.user_facing_name for act in acts]
            }))
        return

    click.secho('{:<20}  {}'.format('Action', 'Description'), bold=True)
    for act in acts:
        click.secho('{:<20}  {}'.format(act.user_facing_name,
                                        act.short_description))
    click.echo()


@main.command('full')
@click.pass_context
@wadebug_option(opt_out)
@wadebug_option(json_output)
@wadebug_option(send_logs)
def full_debug(ctx, **kwargs):
    """Execute all debug routines, executed by default."""
    acts = wa_actions.get_all_actions()

    debug_implementation(
        acts,
        json_output=ctx.obj.get('json', False),
        opt_out=ctx.obj.get('opt_out', False),
        send_logs=ctx.obj.get('send_logs', False),
    )


@main.command('partial')
@click.pass_context
@click.argument(
    'actions',
    default=None,
    required=True,
    nargs=-1,
)
@wadebug_option(opt_out)
@wadebug_option(json_output)
@wadebug_option(send_logs)
def partial_debug(ctx, actions, **kwargs):
    """Execute debug routines provided. "wadebug ls" to actions available."""
    acts, acts_not_found = process_input_actions(actions)

    if acts_not_found:
        if ctx.obj.get('json', False):
            handle_invalid_actions(acts_not_found)
        else:
            handle_invalid_actions_interactive(acts_not_found)
        sys.exit(-1)

    debug_implementation(
        acts,
        json_output=ctx.obj.get('json', False),
        opt_out=ctx.obj.get('opt_out', False),
        send_logs=ctx.obj.get('send_logs', False),
    )


def process_input_actions(actions):
    acts = []
    acts_not_found = []
    for act in actions:
        try:
            acts.append(wa_actions.get_action_by_name(act))
        except KeyError:
            acts_not_found.append(act)

    return acts, acts_not_found


def handle_invalid_actions(acts_not_found):
    click.echo(
        json.dumps({
            'error': 'Can\'t find action(s) requested.',
            'actions_not_found': acts_not_found,
        }))


def handle_invalid_actions_interactive(acts_not_found):
    click.echo(
        'Can\'t find the following action(s) requested:\n\t',
        nl=False,
    )
    click.echo('\n\t'.join(acts_not_found))
    click.echo('Please run wadebug ls to list all available actions.')


def debug_implementation(acts, json_output, opt_out, send_logs):
    if json_output:
        debug_json(acts, opt_out)
    elif send_logs:
        debug_send_logs()
    else:
        debug_interactive(acts, opt_out)


def debug_json(acts, opt_out):
    result = execute_actions(acts)

    if not opt_out:
        cli_utils.send_results_to_fb(result)


def debug_send_logs():
    click.echo('Collecting and uploading logs...')
    cli_utils.send_logs_to_fb(
        success_callback=handle_upload_logs_success_interactive,
        failure_callback=handle_upload_logs_failure_interactive)


def debug_interactive(acts, opt_out):
    result, has_problem = execute_actions_interactive(acts)

    if not opt_out:
        cli_utils.send_results_to_fb(
            result,
            success_callback=handle_upload_results_success_interactive,
            failure_callback=handle_upload_results_failure_interactive)

    if has_problem:
        click.secho(
            'There is at least one problem detected. '
            'Please use the results and details provided to troubleshoot. '
            'Additionally, you can run wadebug --send-logs to send '
            'container logs to WhatsApp for further troubleshooting.',
            fg='yellow',
        )


def execute_actions(actions):
    result = {}
    config = load_config()

    for act in actions:
        res = act.run(config)
        result[res.action.user_facing_name] = res.to_dict()

    click.echo(json.dumps(result))

    return result


def load_config():
    try:
        return cli_utils.get_config_from_file(CONFIG_FILE)
    except Exception:
        return {}


def execute_actions_interactive(actions):
    config = load_config_interactive()

    # execution logic is duplicated so that we print results as they appear
    # this way, if something gets stuck, users can ctrl+c or take other actions
    ui.print_program_header()

    result = {}
    problems = []

    ui.print_table_header('Action', 'Result')

    for act in actions:
        res = act.run(config)
        result[res.action.user_facing_name] = res.to_dict()

        ui.print_table_result_line(res)
        if isinstance(res, results._NotOK):
            problems.append(res)

    click.echo()
    if problems:
        ui.print_line_break()
        click.secho('More details on the investigation:', bold=True)
        ui.print_line_break()
        for problem in problems:
            ui.print_details_header(problem)
            click.echo(problem)

    return result, len(problems) > 0


def load_config_interactive():
    try:
        return cli_utils.get_config_from_file(CONFIG_FILE)
    except yaml.parser.ParserError as e:
        ui.print_invalid_config_message(CONFIG_FILE, e)
        sys.exit(-1)
    except Exception as e:
        handle_config_missing()
        return {}


def handle_upload_results_success_interactive(result):
    click.secho(
        'A report of this run has been uploaded to Facebook.  '
        'You can reference run_id ({}) in Direct Support '
        '(https://business.facebook.com/direct-support) '
        'tickets'.format(result['run_id']),
        fg='yellow',
    )


def handle_upload_results_failure_interactive(e):
    click.secho('Could not send report to Facebook:\n{}'.format(e), fg='red')


def handle_upload_logs_success_interactive(run_id):
    click.secho(
        'Container logs have been uploaded to Facebook.  '
        'You can reference run_id ({}) in Direct Support '
        '(https://business.facebook.com/direct-support) '
        'tickets'.format(run_id),
        fg='yellow',
    )


def handle_upload_logs_failure_interactive(e):
    click.secho('Could not send logs to Facebook:\n{}'.format(e), fg='red')


def handle_config_missing():
    permission_granted = click.confirm(
        click.style(
            '\nWADebug requires a config file: wadebug.conf.yml '
            'in the current directory in order to run full checks, '
            'but none has been found. '
            'Do you want to create the file now?',
            fg='yellow',
        ))

    if permission_granted:
        try:
            cli_utils.create_default_config_file(SAMPLE_CONFIG_FILE)

            click.echo(
                'The config file has been created at {}. '
                'Please fill in the values and run wadebug commands again\n'.
                format(os.getcwd()))

            sys.exit(0)
        except Exception as e:
            click.secho(
                '\nUnable to create config file at {}. Error: {}\n'
                'Some checks will be skipped as a result.\n'.format(
                    os.getcwd(), e),
                fg='yellow')

    else:
        click.secho(
            '\nYou have chosen not to create the config file. '
            'Some checks will be skipped as a result.\n',
            fg='yellow')


if __name__ == '__main__':
    safe_main()
