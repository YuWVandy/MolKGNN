import multiprocessing as mp
from multiprocessing import Pool, Value
import os
from tqdm import tqdm
import shutil, errno
import itertools
import time

branch = 'lr-optimization' # Change this

def gitclone(dir_name):
    cwd = os.getcwd()
    os.chdir(dir_name)
    os.system('git clone git@github.com:LanceKnight/kgnn.git')
    os.chdir('kgnn')
    os.system(f'git checkout {branch}') 
    os.chdir(cwd)

def gitupdate(dir_name):
    cwd = os.getcwd()
    os.chdir(dir_name+'/kgnn')
    os.system('git gc')
    os.system(f'git checkout {branch}') 
    os.system('git pull')
    os.chdir(cwd)

def run_command(exp_id, dataset, num_layers): # Change this
    # Model=kgnn
    os.system(f'python -W ignore entry.py \
        --task_name experiments{exp_id}\
        --dataset_name {dataset} \
        --seed 26\
        --num_workers 8 \
        --dataset_path ../../../dataset/ \
        --enable_oversampling_with_replacement \
        --warmup_iterations 300 \
        --max_epochs 20\
        --peak_lr 5e-2 \
        --end_lr 1e-9 \
        --batch_size 17 \
        --default_root_dir actual_training_checkpoints \
        --gpus 1 \
        --num_layers {num_layers} \
        --num_kernel1_1hop 10 \
        --num_kernel2_1hop 20 \
        --num_kernel3_1hop 30 \
        --num_kernel4_1hop 50 \
        --num_kernel1_Nhop 10 \
        --num_kernel2_Nhop 20 \
        --num_kernel3_Nhop 30 \
        --num_kernel4_Nhop 50 \
        --node_feature_dim 27 \
        --edge_feature_dim 7 \
        --hidden_dim 32')\

def copyanything(src, dst):
    # If dst exits, remove it first
    if os.path.exists(dst):
        shutil.rmtree(dst)
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno in (errno.ENOTDIR, errno.EINVAL):
            shutil.copy(src, dst)
        else: raise

def run(exp_id, dataset, num_layers):
    exp_name = f'exp{exp_id}_dataset{dataset}_layers_{num_layers}' # Change this
    print(f'=====running {exp_name}')

    # Go to correct folder
    dir_name = f'../experiments/{exp_name}' 
    # if not os.path.exists(dir_name):
    #   os.mkdir(dir_name)
    #   gitclone(dir_name)
    # gitupdate(dir_name)

    global github_repo_dir
    copyanything(github_repo_dir, dir_name)
    cwd = os.getcwd()
    os.chdir(dir_name+'/kgnn')

    # # Task
    run_command(exp_id, dataset, num_layers) # Change this
    # time.sleep(3)
    print(f'----{exp_name} finishes')
    os.chdir(cwd)
    

def attach_exp_id(input_tuple, tuple_id):
    # Add experiment id in front of the input hyperparam tuple
    record = [tuple_id]
    record.extend(list(input_tuple))
    return record


# Global variable
# Github repo template
github_repo_dir = f'../experiments/template_dataset_layers'# Change this

if __name__ == '__main__':
    mp.set_start_method('spawn')


    dataset_list = [ '1798' ]
    warmup = [200, 2000, 20000]
    # # num_epochs = [20, 25, 30]
    peak_lr = [5e-1, 5e-2, 5e-3]
    end_lr = [1e-8, 1e-9, 1e-10]
    # num_layers = [3]
    data_pair = list(itertools.product(dataset_list, warmup, peak_lr, end_lr ))
    print(f'num data_pair:{len(data_pair)}')
    data_pair_with_exp_id = list(map(attach_exp_id, data_pair, range(len(data_pair))))
    print(f'data_pair_with_exp_id:{data_pair_with_exp_id}')
    with open('logs/scheduler.log', "w+") as out_file:
        out_file.write(f'num data_pair:{len(data_pair)}\n\n')
        out_file.write(f'data_pair_with_exp_id:{data_pair_with_exp_id}')


    # Clone once from github
    
    if not os.path.exists(github_repo_dir):
        os.mkdir(github_repo_dir)
        gitclone(github_repo_dir)
    gitupdate(github_repo_dir)

    
    # with Pool(processes = 1) as pool:
    #     pool.starmap(run, data_pair_with_exp_id)

   
    
    print(f'finish')

