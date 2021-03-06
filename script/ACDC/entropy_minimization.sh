#!/usr/bin/env bash
set -e

PROJECT_PATH="../../"

CC_WRAPPER_PATH="${PROJECT_PATH}script/CC_wrapper.sh"

source $CC_WRAPPER_PATH

cd "${PROJECT_PATH}"

time=6
account=def-chdesa
save_dir=entropy_minimization_results
declare -a StringArray=(
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/baseline_f Lab_Partitions.partition_sets=1.0"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/baseline_0.2p Lab_Partitions.partition_sets=0.2"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/baseline_0.1p Lab_Partitions.partition_sets=0.1"

"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/0.2label_entropy_0.5_5 Lab_Partitions.partition_sets=0.2 StartTraining.entropy_min=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/0.2label_entropy_0.3_5 Cot_Scheduler.max_value=0.3 Lab_Partitions.partition_sets=0.2 StartTraining.entropy_min=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/0.2label_entropy_0.2_5 Cot_Scheduler.max_value=0.2 Lab_Partitions.partition_sets=0.2 StartTraining.entropy_min=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/0.2label_entropy_0.1_5 Cot_Scheduler.max_value=0.1 Lab_Partitions.partition_sets=0.2 StartTraining.entropy_min=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/0.2label_entropy_0.01_5 Cot_Scheduler.max_value=0.01 Lab_Partitions.partition_sets=0.2 StartTraining.entropy_min=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/0.2label_entropy_0.5_10 Cot_Scheduler.begin_epoch=10 Lab_Partitions.partition_sets=0.2 StartTraining.entropy_min=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/0.2label_entropy_0.3_10 Cot_Scheduler.max_value=0.3 Cot_Scheduler.begin_epoch=10 Lab_Partitions.partition_sets=0.2 StartTraining.entropy_min=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/0.2label_entropy_0.2_10 Cot_Scheduler.max_value=0.2 Cot_Scheduler.begin_epoch=10 Lab_Partitions.partition_sets=0.2 StartTraining.entropy_min=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/0.2label_entropy_0.1_10 Cot_Scheduler.max_value=0.1 Cot_Scheduler.begin_epoch=10 Lab_Partitions.partition_sets=0.2 StartTraining.entropy_min=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/0.2label_entropy_0.01_10 Cot_Scheduler.max_value=0.01 Cot_Scheduler.begin_epoch=10 Lab_Partitions.partition_sets=0.2 StartTraining.entropy_min=True"

"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/0.1label_entropy_0.5_5 Lab_Partitions.partition_sets=0.1 StartTraining.entropy_min=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/0.1label_entropy_0.3_5 Cot_Scheduler.max_value=0.3 Lab_Partitions.partition_sets=0.1 StartTraining.entropy_min=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/0.1label_entropy_0.2_5 Cot_Scheduler.max_value=0.2 Lab_Partitions.partition_sets=0.1 StartTraining.entropy_min=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/0.1label_entropy_0.1_5 Cot_Scheduler.max_value=0.1 Lab_Partitions.partition_sets=0.1 StartTraining.entropy_min=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/0.1label_entropy_0.01_5 Cot_Scheduler.max_value=0.01 Lab_Partitions.partition_sets=0.1 StartTraining.entropy_min=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/0.1label_entropy_0.5_10 Cot_Scheduler.begin_epoch=10 Lab_Partitions.partition_sets=0.1 StartTraining.entropy_min=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/0.1label_entropy_0.3_10 Cot_Scheduler.max_value=0.3 Cot_Scheduler.begin_epoch=10 Lab_Partitions.partition_sets=0.1 StartTraining.entropy_min=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/0.1label_entropy_0.2_10 Cot_Scheduler.max_value=0.2 Cot_Scheduler.begin_epoch=10 Lab_Partitions.partition_sets=0.1 StartTraining.entropy_min=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/0.1label_entropy_0.1_10 Cot_Scheduler.max_value=0.1 Cot_Scheduler.begin_epoch=10 Lab_Partitions.partition_sets=0.1 StartTraining.entropy_min=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.save_dir=${save_dir}/0.1abel_entropy_0.01_10 Cot_Scheduler.max_value=0.01 Cot_Scheduler.begin_epoch=10 Lab_Partitions.partition_sets=0.1 StartTraining.entropy_min=True"

)

for cmd in "${StringArray[@]}"
do
echo ${cmd}
CC_wrapper "${time}" "${account}" "${cmd}" 16

done
