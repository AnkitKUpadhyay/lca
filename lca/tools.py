import pickle
import yaml
import json
import logging
import cluster_tools as ct
from init_logger import init_logger, get_formatter

init_logger()



def load_yaml(file_path):
    print(f"Loading config from path: {file_path}")
    with open(file_path, 'r') as file:
        config_dict = yaml.safe_load(file)

    return config_dict



def get_config(file_path):

    config_dict = load_yaml(file_path)

    return config_dict

def load_json(file_path):
    with open(file_path) as f:
        data = json.load(f)
    return data

def write_json(data, out_path):
    json_object = json.dumps(data, indent=4)
    with open(out_path, "w") as outfile:
        outfile.write(json_object)
        


def load_pickle(file):
    with open(file, 'rb') as f_file:
        result = pickle.load(f_file)
    return result


def generate_ga_params(config_ini):
    
    ga_params = dict()

    phc = float(config_ini['EDGE_WEIGHTS']['prob_human_correct'])
    assert 0 < phc < 1
    ga_params['prob_human_correct'] = phc
    s = config_ini['EDGE_WEIGHTS']['augmentation_names']
    ga_params['aug_names'] = s.strip().split()

    mult = float(config_ini['ITERATIONS']['min_delta_converge_multiplier'])
    ga_params['min_delta_converge_multiplier'] = mult

    s = float(config_ini['ITERATIONS']['min_delta_stability_ratio'])
    assert s > 1
    ga_params['min_delta_stability_ratio'] = s

    n = int(config_ini['ITERATIONS']['num_per_augmentation'])
    assert n >= 1
    ga_params['num_per_augmentation'] = n

    n = int(config_ini['ITERATIONS']['tries_before_edge_done'])
    assert n >= 1
    ga_params['tries_before_edge_done'] = n

    i = int(config_ini['ITERATIONS']['ga_iterations_before_return'])
    assert i >= 1
    ga_params['ga_iterations_before_return'] = i

    mw = int(config_ini['ITERATIONS']['ga_max_num_waiting'])
    assert mw >= 1
    ga_params['ga_max_num_waiting'] = mw

    ga_params['should_densify'] = config_ini['ITERATIONS'].getboolean(
        'should_densify', False
    )

    n = int(config_ini['ITERATIONS'].get('densify_min_edges', 1))
    assert n >= 1
    ga_params['densify_min_edges'] = n

    df = float(config_ini['ITERATIONS'].get('densify_frac', 0.0))
    assert 0 <= df <= 1
    ga_params['densify_frac'] = df

    log_level = config_ini['LOGGING']['log_level']
    ga_params['log_level'] = log_level
    log_file = config_ini['LOGGING']['log_file']
    ga_params['log_file'] = log_file

    ga_params['draw_iterations'] = config_ini['DRAWING'].getboolean('draw_iterations')
    ga_params['drawing_prefix'] = config_ini['DRAWING']['drawing_prefix']

    logger = logging.getLogger('lca')
    handler = logging.FileHandler(log_file, mode='w')
    handler.setLevel(log_level)
    handler.setFormatter(get_formatter())
    logger.addHandler(handler)

    return ga_params

def generate_gt_clusters(df, name_key):
    gt_node2cid = {}
    cids_unique = df[name_key].unique()
    cids = [f'ct{idx}' for idx in range(len(cids_unique))]
    gt_clustering = {cid: [] for cid in cids}
    
    for i, row in df.iterrows():
        cid = cids[list(cids_unique).index(row[name_key])]
        gt_clustering[cid].append(i)
        gt_node2cid[i] = cid

    gt_clustering = {
        cid: set(cluster) for cid, cluster in gt_clustering.items()
    }

    return gt_clustering, gt_node2cid


def print_intersect_stats(df,individual_key="name"):
    print("** cross-set stats **")
    print()
    print(' - Counts: ')
    names = df[individual_key].unique()
    
    
    print("     number of individuals: ", len(names))
    print("     number of annotations in train: ", len(df))
    print()
    avg_ratio_train = len(df) / len(names)
    print(f"    average number of annotations per individual: {avg_ratio_train:.2f}")
    print()

    
