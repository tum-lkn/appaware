import os
import logging
import time
import json
import numpy as np
import networkx as nx
import copy
import csv
from os.path import join as pjoin

from run_simple import run_simple, gen_id, load_model

log = logging.getLogger(__name__)


def create_cfg(data, app_mix, mixscale, args, out_folder):

    data = copy.deepcopy(data)

    apps = {m: w * mixscale for m, w in app_mix.items()}

    data['flows'] = {}
    idx = 0

    for m, cnt in apps.items():
        for i in range(int(np.floor(cnt))):
            a = {'model': m}
            data['flows'][str(idx)] = a
            idx += 1

    # There has to be at least one flow
    assert(len(data['flows']) > 0)

    # Generate a unique run_id
    cfg = {'run_id': gen_id(),
           'plotting': False, # Overwrites all the other plotting settings
           'create_topo_plot': True, # plot flags un-used at the moment
           'create_app_list': True,
           'create_path_delay_plots': True,
           'create_delay_plot': True,
           'create_model_plots': True,
           'model_dir': args.model_dir,
           'scenario': data,
           'delay_approx': args.delay_approx,
           'time_limit': args.time_limit}

    cfg['run_folder'] = pjoin(out_folder, "runs", cfg['run_id'])

    return cfg


def write_results(sresultf, results):

    log.info("Writing search result to %s." % sresultf)

    with open(pjoin(sresultf), 'w') as f:

        headers = sorted([str(k) for k in results[0].keys()])

        csvw = csv.DictWriter(f, fieldnames=headers)

        csvw.writeheader()

        for r in results:
            csvw.writerow(r)


if __name__ == "__main__":

    import argparse

    logconf = {'format': '[%(asctime)s.%(msecs)-3d: %(name)-16s - %(levelname)-5s] %(message)s', 'datefmt': "%H:%M:%S"}
    logging.basicConfig(level=logging.DEBUG, **logconf)

    parser = argparse.ArgumentParser(description="Searches for a minimum and maximum number of clients for a given application max and bottleneck throughput.")
    parser.add_argument('-v', '--verbose', help="Enable debug log.", dest='verbose', action='store_true')
    parser.add_argument('-n', '--no-plots', help="Disable result plotting.", dest='no_plots', action='store_true')
    parser.add_argument('--search-folder',
                        help="Where to store the result of the search. (default: %(default)s)",
                        default="runs_searches")
    parser.add_argument('--model_dir', '-m',
                        help="Where the application models are stored. (default: %(default)s)",
                        default="models/postprocessing/models")
    parser.add_argument('--delay-approx',
                        help="Which delay approx. to use. (default: %(default)s)",
                        default="samples/simple/max95perc.npy")
#                        default="samples/simple/mm1.npy")
    parser.add_argument('--time-limit',
                        help="Time limit for solving one scenario in seconds. (default: %(default)s)",
                        default=3600, type=int)
    parser.add_argument('--capacity', '-c',
                        help="Capacity of the bottleneck link in Kbps. (default: %(default)s)",
                        default=100000, type=int)
    parser.add_argument('--search-cnt',
                        help="How many searches to perform starting from min (default: %(default)s)",
                        default=12, type=int)
    parser.add_argument('--search-step',
                        help="Step size for searching. (default: %(default)s)",
                        default=1, type=int)
    parser.add_argument('--search-min',
                        help="Where to start searching. (default: %(default)s)",
                        default=1, type=int)
    parser.add_argument('--model_ssh_weight', '-s',
                        help="Weight in the application mix of model_ssh. (default: %(default)f)",
                        default=2.0, type=float)
    parser.add_argument('--model_web_weight', '-w',
                        help="Weight in the application mix of model_web. (default: %(default)f)",
                        default=2.0, type=float)
    parser.add_argument('--model_webdl_weight', '-d',
                        help="Weight in the application mix of model_webdl. (default: %(default)f)",
                        default=2.0, type=float)
    parser.add_argument('--model_video_weight', '-i',
                        help="Weight in the application mix of model_video. (default: %(default)f)",
                        default=1, type=float)
    parser.add_argument('--model_video_live_weight', '-l',
                        help="Weight in the application mix of model_video_live. (default: %(default)f)",
                        default=1, type=float)
    parser.add_argument('--model_voip_weight', '-p',
                        help="Weight in the application mix of model_voip. (default: %(default)f)",
                        default=2.0, type=float)
    parser.add_argument

    args = parser.parse_args()


    # Create a folder for the search
    search_id = gen_id()
    out_folder = pjoin(args.search_folder, search_id)
    os.makedirs(out_folder, exist_ok=True)

    # Configure capacity and application weights
    data = {'app_mix': {
                'model_ssh': args.model_ssh_weight,
                'model_web': args.model_web_weight,
                'model_webdl': args.model_webdl_weight,
                'model_video': args.model_video_weight,
                'model_video_live': args.model_video_live_weight,
                'model_voip': args.model_voip_weight},
            'capacity': args.capacity
           }

    # Gather necessary information from the models
    data['flows'] = {}

    data['app_tp'] = {}
    data['app_d'] = {}
    data['min_d'] = 0
    data['max_d'] = 0

    for model in data['app_mix'].keys():
        a = {}
        load_model(a, args.model_dir, model)
        data['app_tp'][model] = {'min': a['TP'][0], 'max': a['TP'][-1]}
        data['app_d'][model] = {'min': a['D'][0], 'max': a['D'][-1]}

    data['min_d'] = min([md['min'] for m, md in data['app_d'].items()])
    data['max_d'] = min([md['max'] for m, md in data['app_d'].items()])

    # Load delay approximation and scale to capacity
    DelayApprox = np.load(args.delay_approx)
    DelayApprox.T[:, 0] = DelayApprox.T[:, 0] * data['capacity']
    # Delay Approximations are stored as seconds, convert here to ms.
    DelayApprox.T[:, 1] = DelayApprox.T[:, 1] * 1000

    # Find capacity for delay requirements
    data['relaxed_D_capacity'] = np.interp(data['max_d'],
                                           DelayApprox.T[:, 1],
                                           DelayApprox.T[:, 0])

    # Which scale factors to search through
    search_scales = [(args.search_min + x) * args.search_step\
                     for x in range(args.search_cnt)]

    results = []

    for scale in search_scales:

        cfg = create_cfg(data, data['app_mix'], scale, args, out_folder)

        sumdict = run_simple(cfg, pjoin(out_folder, "summary_%s.json" %
                                        cfg['run_id']),
                             no_grb_print=True)

        r = {'scale': scale,
             'min_U': sumdict['solved']['min_utility'],
             'min_U1': sumdict['stage_first']['solved']['min_utility'],
             'grb_opt_dur': sumdict['solved']['optimization_duration'],
             'flow_cnt': len(cfg['scenario']['flows'])}

        for m, w in data['app_mix'].items():
            r["%s_cnt" % m] = int(np.round(w * scale))

        r['capacity'] = args.capacity
        r['used_capacity'] = sum([flow['TP'] for flow in
                                  sumdict['flows'].values()])
        r['approx_D'] = sumdict['flows'][0]['approx_D']

        results.append(r)

    sresultf = pjoin(args.search_folder, 'result_%s.csv' % search_id)

    write_results(sresultf, results)

    if not args.no_plots:
        from vis.search import create_plots_from_file
        create_plots_from_file(sresultf, out_folder)
