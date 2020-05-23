#!/usr/bin/env bash
set -e

PROJECT_PATH="../../"

CC_WRAPPER_PATH="${PROJECT_PATH}script/CC_wrapper.sh"

source $CC_WRAPPER_PATH

cd "${PROJECT_PATH}"


time=12
account=def-chdesa
save_dir=ladder_jsd_alpha_self_paced
declare -a StringArray=(
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_0.2label_ramp0.8 Lab_Partitions.partition_sets=0.2 Alpha_Scheduler.name=selfpacedScheduler Alpha_Scheduler.begin_epoch=100 Alpha_Scheduler.min_value=0.8 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_0.2label_ramp0.5 Lab_Partitions.partition_sets=0.2 Alpha_Scheduler.name=selfpacedScheduler Alpha_Scheduler.begin_epoch=100 Alpha_Scheduler.min_value=0.5 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_0.2label_ramp0.0 Lab_Partitions.partition_sets=0.2 Alpha_Scheduler.name=selfpacedScheduler Alpha_Scheduler.begin_epoch=100 Alpha_Scheduler.min_value=0.0 StartTraining.train_jsd=True"

"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_0.1label_ramp0.8 Lab_Partitions.partition_sets=0.1 Alpha_Scheduler.name=selfpacedScheduler Alpha_Scheduler.begin_epoch=100 Alpha_Scheduler.min_value=0.8 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_0.1label_ramp0.5 Lab_Partitions.partition_sets=0.1 Alpha_Scheduler.name=selfpacedScheduler Alpha_Scheduler.begin_epoch=100 Alpha_Scheduler.min_value=0.5 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_0.1label_ramp0.0 Lab_Partitions.partition_sets=0.1 Alpha_Scheduler.name=selfpacedScheduler Alpha_Scheduler.begin_epoch=100 Alpha_Scheduler.min_value=0.0 StartTraining.train_jsd=True"
)

for cmd in "${StringArray[@]}"
do
echo ${cmd}
CC_wrapper "${time}" "${account}" "${cmd}" 16

done