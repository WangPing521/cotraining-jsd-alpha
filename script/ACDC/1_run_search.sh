#!/usr/bin/env bash

wrapper(){
    la_ratio=$1
    max_epoch=$2
    hour=$3
    #echo "Running: ${model_num}"
    module load python/3.6
    source $HOME/torchenv36/bin/activate
    module load scipy-stack
    sbatch  --job-name="task1_${la_ratio}" \
     --nodes=1  \
     --gres=gpu:1 \
     --cpus-per-task=6  \
     --mem=32000M \
     --time=0-${hour}:00 \
     --account=def-chdesa \
     --mail-user=jizong.peng.1@etsmtl.net \
     --mail-type=ALL   \
     1_run.sh  $la_ratio $max_epoch
}

#wrapper 0.1  120 48

wrapper 0.2 120 48

#wrapper 0.3  120 48

wrapper 0.4 120 48

#wrapper 0.5  120 48

wrapper 0.6 120 48

#wrapper 0.7 120 48

wrapper 0.8 120 48

#wrapper 0.9 120 48
