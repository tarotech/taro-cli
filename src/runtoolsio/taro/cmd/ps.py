import json

from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers.data import JsonLexer
from runtoolsio.runcore import client
from runtoolsio.runcore.job import JobRuns
from runtoolsio.runcore.util import MatchingStrategy

from runtoolsio.taro import printer, argsutil
from runtoolsio.taro.view import instance as view_inst


def run(args):
    run_match = argsutil.run_matching_criteria(args, MatchingStrategy.PARTIAL)
    active_runs = client.get_active_runs(run_match).responses
    runs = JobRuns(active_runs)

    if args.format == 'table': 
        columns = view_inst.DEFAULT_COLUMNS
        if args.show_params:
            columns.insert(2, view_inst.PARAMETERS)
        printer.print_table(runs, columns, show_header=True, pager=False)
    elif args.format == 'json':
        print(json.dumps(runs.to_dict()))
    elif args.format == 'jsonp':
        json_str = json.dumps(runs.to_dict(), indent=2)
        print(highlight(json_str, JsonLexer(), TerminalFormatter()))
    else:
        assert False, 'Unknown format: ' + args.format
