from functools import cached_property
import sys
from loguru import logger
from pyqtgraph.parametertree.parameterTypes import SimpleParameter
from scipy.optimize import NonlinearConstraint
import time
import zmq


from fvgp.gp_kernels import get_distance_matrix, matern_kernel_diff1, periodic_kernel

import numpy as np
from scipy import linalg
from gpcam.gp_optimizer import GPOptimizer
from tsuchinoko.adaptive import Data
from tsuchinoko.adaptive.gpCAM_in_process import GPCAMInProcessEngine
from tsuchinoko.adaptive.grid import Grid
from tsuchinoko.core import ZMQCore, CoreState
from tsuchinoko.execution.simple import SimpleEngine
from tsuchinoko.graphs.common import Table, image_grid, GPCamHyperparameterPlot, Score
from tsuchinoko.utils import threads
from tsuchinoko.graphs.specialized import ReconstructionGraph, ProjectionOperatorGraph, ProjectionMask, sirt
import PIL

try:
    from yaml import CLoader as Loader, CDumper as Dumper, dump, load
except ImportError:
    from yaml import Loader, Dumper

from uuid import uuid4
try:
    #Queue_PATH='/nsls2/data/cms/legacy/xf11bm/data/2024_3/KChen-Wiegart6/'
    Queue_PATH='../'
    Queue_PATH in sys.path or sys.path.append(Queue_PATH)
    from CustomQueue import Queue_decision
except ImportError:
    logger.critical('Falling back to built-in zmq Queue module; this is bad outside of test cases')
    from tsuchinoko.utils.zmq_queue import Queue_decision


session_id = uuid4()


# motor speed in x, x here is the "other" dimension (in 2d) that we can freely move through
v = 3.  # in unit [x per second]

# bounds x (=temp.),time
# the theoretical bounds extend way beyond the end_of_time for stability reasons
# the experiment will still be killed at the end_of_time
end_of_time = 60*60.  # [seconds]

bounds = np.array([[0, 30], [0, 2. * end_of_time]])
# why is end_of_time and bounds[1,1] not the same? Easy, the optimizer does not like to be pushed into
# a corner when the the volume between the constraint and the bound gets too small. Instability results.

time_buffer = 5.  # [seconds] We need a time buffer to account for the optimization time of the acquisition function

#init_N = 10  # don't go too low here, 10 minimum

measurement_cost = 15  # how long does one measurement take, with alignment# Initial data

#x_init = np.random.uniform(low=bounds[:, 0], high=np.array([1., 5.]), size=(init_N, 2))

# single task:
#hps_initial = np.ones(5)
hps_initial = [1e3, 2, 2, 4, 4]
hps_bounds = np.array([[0.001, 1e7],  # signal variance
                       [0.1, 40.],  # length scale in x
                       [0.1, 10. * end_of_time],  # length scale in time
                       [2., 10. * end_of_time],  ## length scale periodic kernel
                       [2., 10. * end_of_time],  ##period
                       ]
                      )  ##set up the hyperparameter bounds


time_before_training = time.time()
########my_gpo.train_gp(hps_bounds, max_iter = 50)
########my_gpo.init_cost(cost, dict({}))   ##init costs with a dict if necessary

########print("hyperparameters after 1st training: ", my_gpo.hyperparameters)
training_time = 0 #time.time() - time_before_training
current_position =  0 #x_data[-1] + training_time

def g(x):
    current_time = adaptive.optimizer.x_data[-1, 1] + training_time
    # print(training_time)
    current_x = adaptive.optimizer.x_data[-1, 0]
    time = x[1]
    pos = x[0]
    if ((time - (current_time + time_buffer)) * v) ** 2 - (pos - current_x) ** 2 < 0.0:
        return -1.
    elif time - (current_time + time_buffer) < 0.:
        return -1.
    else:
        return np.sqrt(((time - (current_time + time_buffer)) * v) ** 2 - (pos - current_x) ** 2)


nlc = NonlinearConstraint(g, 0, np.inf)


def stat_kernel(x1, x2, hps):
    distance_matrix = 0
    time_d = abs(np.subtract.outer(x1[:, 1], x2[:, 1]))
    for i in range(len(x1[0])):
        distance_matrix += abs(np.subtract.outer(x1[:, i], x2[:, i]) / hps[1 + i]) ** 2

    d = np.sqrt(distance_matrix)
    k = hps[0] * matern_kernel_diff1(d, 1.) * periodic_kernel(time_d, hps[3], hps[4])
    return k

# we may set up a user-defined acquisition function,
# but we can also use a standard one provided by gpCAM

def optional_acq_func(x, obj):  ##for single task
    #    a = 3.0 #3.0 for 95 percent confidence interval
    #    mean = obj.posterior_mean(x)["f(x)"]
    # print("acq func called with input: ", x)
    cov = obj.posterior_covariance(x)["v(x)"]
    return np.sqrt(cov)


def uniform_acq_func(x, obj):
    return np.ones((x.shape[0]))

# Constrained optimization sometimes fails and so, as a safety net, we assign really high costs to past measurements.
# Otherwise costs just rise with how long we have to wait for the measurement to occur
def cost(origin, x, arguments=None):
    ##has to be vecorized
    # print("cost called with input", x)
    time = np.abs(x[:, 1] - origin[1]) + measurement_cost
    ind = np.where(origin[1] > x[:, 1])
    time[ind] = (end_of_time * 10.)
    return time


def push_to_queue(pos):
    global session_id
    # start with no measurements
    measurements = []

    # until a measurement is retreived
    while not measurements:
        # send target to decision queue
        logger.info(f'publishing: {pos}')
        decision_queue.publish([{'session': session_id,
                                 'position': pos,
                                 'measured': False}])
        time_last_measurement_received = time.monotonic()
        while True:
            try:
                # try to get measurement back
                measurements = decision_queue.get(flags=zmq.NOBLOCK, use_flags=True)
            except zmq.Again:
                if time.monotonic() - time_last_measurement_received > 60 * 5:
                    # if no measurement was received within the last 5 minutes, then break with measurements empty,
                    # sending flow back to sending the target again
                    logger.error('No measurement was received in the last 5 minutes. The target will be resent.')
                    # Resetting client uid so that measurements from previous targets are ignored
                    session_id = uuid4()
                    break
                else:
                    # if no measurement was received but it hasn't been long, sleep a bit and try again.
                    time.sleep(.1)
                    continue
            if len(measurements) > 1:
                logger.critical(f'More than 1 point retrieved from decision queue: {measurements}')
            elif measurements[0]['session'] != session_id:
                logger.critical('Stale data received; the target was from from a different session and will be ignored.')
            else:
                break

    return measurements[0]['position'], measurements[0]['value'], measurements[0]['variance'], {}


class BackgroundTraining(GPCAMInProcessEngine):
    def __init__(self, start_training_at: int = 4, *args, **kwargs):
        self.training_thread = None
        self.start_training_at = start_training_at
        super().__init__(*args, **kwargs)

    def train(self):
        if not self.training_thread or self.training_thread.done:
            if len(self.optimizer.y_data) >= self.start_training_at:
                # pull values from optimizer
                with core.data.r_lock():
                    x = np.asarray(core.data.positions.copy())
                    y = np.asarray(core.data.scores.copy())
                    v = np.asarray(core.data.variances.copy())

                # pull parameters
                hyperparameters_bounds = np.asarray([[self.parameters[('hyperparameters', f'hyperparameter_{i}_{edge}')]
                                                      for edge in ['min', 'max']]
                                                     for i in range(self.num_hyperparameters)])
                hyperparameters = np.asarray([self.parameters[('hyperparameters', f'hyperparameter_{i}')]
                                              for i in range(self.num_hyperparameters)])
                parameter_bounds = np.asarray([[self.parameters[('bounds', f'axis_{i}_{edge}')]
                                                for edge in ['min', 'max']]
                                               for i in range(self.dimensionality)])

                self.training_thread = threads.QThreadFuture(self._background_train,
                                                             x,
                                                             y,
                                                             v,
                                                             parameter_bounds,
                                                             hyperparameters,
                                                             hyperparameters_bounds,
                                                             {'method': 'global'})
                self.training_thread.start()

        return True

    def _background_train(self, x, y, v, parameter_bounds, hyperparameters, hyperparameter_bounds, training_kwargs):
        logger.info('Training asynchronously...')
        # newstyle
        optimizer = GPOptimizer(x,
                                  y,
                                  noise_variances=v,
                                  init_hyperparameters=hyperparameters,
                                  **self.gp_opts.copy())

        optimizer.train(hyperparameter_bounds=hyperparameter_bounds,
                        init_hyperparameters=hyperparameters,
                        **training_kwargs)

        self.optimizer.set_hyperparameters(optimizer.hyperparameters)
        logger.info(f'Hyperparameters set from asynchronous training: {optimizer.hyperparameters}')
        # TODO: obsolete this hack
        if 'hyperparameter training log' not in core.data.states:
            core.data.states['hyperparameter training log'] = []
        core.data.states['hyperparameter training log'].append([len(core.data), self.optimizer.hyperparameters])


class AggressiveBackup(GPCAMInProcessEngine):
    backup_file = '/tmp/backup.yml'

    def update_measurements(self, data):
        super().update_measurements(data)

        with data.r_lock():
            dump(data.as_dict(), open(self.backup_file, 'w'), Dumper=Dumper)




class EmptyOptimizer():
    pass


class SessionReset(GPCAMInProcessEngine):
    def reset(self):
        global session_id
        session_id = uuid4()
        super().reset()


class AdaptiveEngine(AggressiveBackup, BackgroundTraining, SessionReset):
    pass

if __name__ == "__main__":
    decision_queue = Queue_decision(check_interrupted=False)

    # angles = np.linspace(0.0, np.pi, n_angles)

    #the following line will replaced by starting data, a sinogram with the right shape but only measured data non-zero
    # gt_A = np.array([projection_operator(x, phi, l_x) for x in range(l_det) for phi in range(n_angles)]).reshape(l_det * n_angles, -1)
    # domain_sinograms = {}
    # for domain_angle, domain_map in domain_maps.items():
    #     domain_sinograms[domain_angle] = (gt_A @ domain_map.ravel()).reshape(l_det, n_angles).T

    # name = r'C:\data\gitomo\run2-checkpoint1.yml'
    # data = Data(**load(open(name, 'r'), Loader=Loader))
    # positions = np.asarray(data.positions)
    # x, y = positions.T
    execution = SimpleEngine(measure_func=push_to_queue)

    # print(f'values: {min(data.scores), max(data.scores)}')

    # NB: Allowed acquisition functions:
    # https://gpcam.readthedocs.io/en/latest/api/gpOptimizer.html

    # Define a gpCAM adaptive engine with initial parameters
    adaptive = AdaptiveEngine(dimensionality=2,
#                         grid_until_N=4,
                         parameter_bounds=bounds,
                         hyperparameters=hps_initial,
                         hyperparameter_bounds=hps_bounds,
                         gp_opts=dict(gp_kernel_function=stat_kernel,
                                      #cost_function=cost,
                                      #gp_noise_function=noise, # newstyle
                                      ),
                         ask_opts=dict(constraints=(nlc,),
                                       vectorized=False),
                         acquisition_functions={'Shannon IG': "relative information entropy",
                                                'Uniform': uniform_acq_func})

    # adaptive = ProjectionOperatorGrid(parameter_bounds=[(0, l_x), (0, 180)])

    # x_data = np.empty((l_x ** 2, 2))
    # y_data = np.zeros((n_angles * l_det))

    # for i in range(l_x):
    #     for j in range(l_x):
    #         x_data[i+j*l_x] = np.array([float(i), float(j)])

    # v_data = 0.01 * np.ones((n_angles * l_det))

    # Construct a core server
    core = ZMQCore()
    core.set_adaptive_engine(adaptive)
    core.set_execution_engine(execution)
    # core.initialize_data(x_data, y_data, v_data)

    # Start the core server
    #core.state = CoreState.Starting # Forces it to start on its own, immediately, as soon as you start the script.
    core.main()

