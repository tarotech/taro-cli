import sys

from runtoolsio.runcore import client
from runtoolsio.runcore.criteria import compound_metadata_filter, EntityRunCriteria
from runtoolsio.runcore.listening import InstanceOutputReceiver, InstanceOutputObserver
from runtoolsio.runcore.run import PhaseMetadata, InstanceMetadata
from runtoolsio.runcore.util import MatchingStrategy
from runtoolsio.taro import argsutil
from runtoolsio.taro import printer, style, cliutil
from runtoolsio.taro.theme import Theme

HIGHLIGHT_TOKEN = (Theme.separator, ' ---> ')


def run(args):
    metadata_criteria = argsutil.metadata_criteria(args, MatchingStrategy.PARTIAL)
    if args.follow:
        receiver = InstanceOutputReceiver(compound_metadata_filter(metadata_criteria))
        receiver.add_observer_output(TailPrint(receiver))
        receiver.start()
        cliutil.exit_on_signal(cleanups=[receiver.close_and_wait])
        receiver.wait()  # Prevents 'exception ignored in: <module 'threading' from ...>` error message
    else:
        # TODO output parameters (mode, size, ..)
        for output_resp in client.fetch_output(EntityRunCriteria(metadata_criteria=metadata_criteria)).responses:
            printer.print_styled(HIGHLIGHT_TOKEN, *style.entity_instance_id_styled(output_resp.instance_metadata))
            for line, is_err in output_resp.output:
                print(line, file=sys.stderr if is_err else sys.stdout)
            sys.stdout.flush()


class TailPrint(InstanceOutputObserver):

    def __init__(self, receiver):
        self._receiver = receiver
        self.last_printed_job_instance = None

    def new_instance_output(self, instance_meta: InstanceMetadata, phase: PhaseMetadata, output: str, is_err: bool):
        # TODO It seems that this needs locking
        try:
            if self.last_printed_job_instance != instance_meta:
                printer.print_styled(HIGHLIGHT_TOKEN, *style.entity_instance_id_styled(instance_meta))
            self.last_printed_job_instance = instance_meta
            print(output, flush=True, file=sys.stderr if is_err else sys.stdout)
        except BrokenPipeError:
            self._receiver.close_and_wait()
            cliutil.handle_broken_pipe(exit_code=1)
