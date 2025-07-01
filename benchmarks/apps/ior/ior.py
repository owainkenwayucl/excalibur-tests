# Import modules from reframe and excalibur-tests
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.backends import getlauncher
from benchmarks.modules.utils import SpackTest

@rfm.simple_test
class StreamBenchmark(SpackTest):

    # Run configuration
    block_size = variable(str, value="8k")
    transfer_size = variable(str, value="8k")
    patterns = {
        "read":r'read\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)',
        "write":r'write\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)'
    }

    ## Mandatory ReFrame setup
    valid_systems = ['-gpu']
    valid_prog_environs = ['default']

    spack_spec = 'ior openmpi'

    ## Executable
    executable = 'ior'
    executable_opts = [f"-b={self.block_size}", f"-t={self.transfer_size}"]

    ## Scheduler options
    tasks = parameter([1, 2])  # Used to set `num_tasks` in `__init__`.
    cpus_per_task = 1

    time_limit = '5m'
    use_multithreading = False

    ## Reference performance values
    reference = {

    }

    def __init__(self):
        # The number of tasks and CPUs per task need to be set here because
        # accessing a test parameter from the class body is not allowed.
        self.num_tasks = self.tasks
        self.num_cpus_per_task = self.cpus_per_task


    @run_after('setup')
    def setup_variables(self):
        # With `env_vars` you can set environment variables to be used in the
        # job.  For example with `OMP_NUM_THREADS` we set the number of OpenMP
        # threads (not actually used in this specific benchmark).  Note that
        # this has to be done after setup because we need to add entries to
        # ReFrame built-in `env_vars` variable.
        self.env_vars['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'


    # Function defining a sanity check.  See
    # https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html
    # for the API of ReFrame tests, including performance ones.
    @run_before('sanity')
    def set_sanity_patterns(self):
        # Check that the string `[RESULT][0]` appears in the standard output of
        # the program.
        self.sanity_patterns = sn.assert_found(r'Finished.*', self.stdout)

    # A performance benchmark.
    @run_before('performance')
    def set_perf_patterns(self):
        # This performance pattern parses the output of the program to extract
        # the desired figure of merit.
        self.perf_patterns = {
            'flops': sn.extractsingle(
                r'\[RESULT\]\[0\] Case 1 (\S+) Gflops/seconds',
                self.stdout, 1, float),
        }