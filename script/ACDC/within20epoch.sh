#!/usr/bin/env bash
set -e

PROJECT_PATH="../../"

CC_WRAPPER_PATH="${PROJECT_PATH}script/CC_wrapper.sh"

source $CC_WRAPPER_PATH

cd "${PROJECT_PATH}"

time=0
minutes=20
account=def-chdesa
save_dir=checkpoint_within20epoch
declare -a StringArray=(
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.checkpoint=${save_dir}/jsd_0.2label_ramp0.8 Trainer.save_dir=${save_dir}/jsd_0.2label_ramp0.8 Lab_Partitions.partition_sets=0.2 Alpha_Scheduler.begin_epoch=50 Alpha_Scheduler.min_value=0.8 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.checkpoint=${save_dir}/jsd_0.2label_ramp0.5 Trainer.save_dir=${save_dir}/jsd_0.2label_ramp0.5 Lab_Partitions.partition_sets=0.2 Alpha_Scheduler.begin_epoch=50 Alpha_Scheduler.min_value=0.5 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.checkpoint=${save_dir}/jsd_0.2label_ramp0.2 Trainer.save_dir=${save_dir}/jsd_0.2label_ramp0.2 Lab_Partitions.partition_sets=0.2 Alpha_Scheduler.begin_epoch=50 Alpha_Scheduler.min_value=0.2 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.checkpoint=${save_dir}/jsd_0.2label_ramp0.1 Trainer.save_dir=${save_dir}/jsd_0.2label_ramp0.1 Lab_Partitions.partition_sets=0.2 Alpha_Scheduler.begin_epoch=50 Alpha_Scheduler.min_value=0.1 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.checkpoint=${save_dir}/jsd_0.2label_ramp0.0 Trainer.save_dir=${save_dir}/jsd_0.2label_ramp0.0 Lab_Partitions.partition_sets=0.2 Alpha_Scheduler.begin_epoch=50 Alpha_Scheduler.min_value=0.0 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.checkpoint=${save_dir}/jsd_0.2label_1.0 Trainer.save_dir=${save_dir}/jsd_0.2label_1.0 Lab_Partitions.partition_sets=0.2 Alpha_Scheduler.begin_epoch=200 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.checkpoint=${save_dir}/jsd_0.2label_0.8 Trainer.save_dir=${save_dir}/jsd_0.2label_0.8 Lab_Partitions.partition_sets=0.2 Alpha_Scheduler.begin_epoch=0 Alpha_Scheduler.max_epoch=0 Alpha_Scheduler.min_value=0.8 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.checkpoint=${save_dir}/jsd_0.2label_0.5 Trainer.save_dir=${save_dir}/jsd_0.2label_0.5 Lab_Partitions.partition_sets=0.2 Alpha_Scheduler.begin_epoch=0 Alpha_Scheduler.max_epoch=0 Alpha_Scheduler.min_value=0.5 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.checkpoint=${save_dir}/jsd_0.2label_0.2 Trainer.save_dir=${save_dir}/jsd_0.2label_0.2 Lab_Partitions.partition_sets=0.2 Alpha_Scheduler.begin_epoch=0 Alpha_Scheduler.max_epoch=0 Alpha_Scheduler.min_value=0.2 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.checkpoint=${save_dir}/jsd_0.2label_0.1 Trainer.save_dir=${save_dir}/jsd_0.2label_0.1 Lab_Partitions.partition_sets=0.2 Alpha_Scheduler.begin_epoch=0 Alpha_Scheduler.max_epoch=0 Alpha_Scheduler.min_value=0.1 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.checkpoint=${save_dir}/jsd_0.2label_0.0 Trainer.save_dir=${save_dir}/jsd_0.2label_0.0 Lab_Partitions.partition_sets=0.2 Alpha_Scheduler.begin_epoch=0 Alpha_Scheduler.max_epoch=0 Alpha_Scheduler.min_value=0.0 StartTraining.train_jsd=True"

#"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_0.1label_ramp0.8 Lab_Partitions.partition_sets=0.1 Alpha_Scheduler.begin_epoch=50 Alpha_Scheduler.max_epoch=150 Alpha_Scheduler.min_value=0.8 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.checkpoint=${save_dir}/jsd_0.1label_ramp0.5 Trainer.save_dir=${save_dir}/jsd_0.1label_ramp0.5 Lab_Partitions.partition_sets=0.1 Alpha_Scheduler.begin_epoch=50 Alpha_Scheduler.max_epoch=150 Alpha_Scheduler.min_value=0.5 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.checkpoint=${save_dir}/jsd_0.1label_ramp0.2 Trainer.save_dir=${save_dir}/jsd_0.1label_ramp0.2 Lab_Partitions.partition_sets=0.1 Alpha_Scheduler.begin_epoch=50 Alpha_Scheduler.max_epoch=150 Alpha_Scheduler.min_value=0.2 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.checkpoint=${save_dir}/jsd_0.1label_ramp0.1 Trainer.save_dir=${save_dir}/jsd_0.1label_ramp0.1 Lab_Partitions.partition_sets=0.1 Alpha_Scheduler.begin_epoch=50 Alpha_Scheduler.max_epoch=150 Alpha_Scheduler.min_value=0.1 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.checkpoint=${save_dir}/jsd_0.1label_ramp0.0 Trainer.save_dir=${save_dir}/jsd_0.1label_ramp0.0 Lab_Partitions.partition_sets=0.1 Alpha_Scheduler.begin_epoch=50 Alpha_Scheduler.max_epoch=150 Alpha_Scheduler.min_value=0.0 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.checkpoint=${save_dir}/jsd_0.1label_1.0 Trainer.save_dir=${save_dir}/jsd_0.1label_1.0 Lab_Partitions.partition_sets=0.1 Alpha_Scheduler.begin_epoch=200 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.checkpoint=${save_dir}/jsd_0.1label_0.8 Trainer.save_dir=${save_dir}/jsd_0.1label_0.8 Lab_Partitions.partition_sets=0.1 Alpha_Scheduler.begin_epoch=0 Alpha_Scheduler.max_epoch=0 Alpha_Scheduler.min_value=0.8 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.checkpoint=${save_dir}/jsd_0.1label_0.5 Trainer.save_dir=${save_dir}/jsd_0.1label_0.5 Lab_Partitions.partition_sets=0.1 Alpha_Scheduler.begin_epoch=0 Alpha_Scheduler.max_epoch=0 Alpha_Scheduler.min_value=0.5 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.checkpoint=${save_dir}/jsd_0.1label_0.2 Trainer.save_dir=${save_dir}/jsd_0.1label_0.2 Lab_Partitions.partition_sets=0.1 Alpha_Scheduler.begin_epoch=0 Alpha_Scheduler.max_epoch=0 Alpha_Scheduler.min_value=0.2 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.checkpoint=${save_dir}/jsd_0.1label_0.1 Trainer.save_dir=${save_dir}/jsd_0.1label_0.1 Lab_Partitions.partition_sets=0.1 Alpha_Scheduler.begin_epoch=0 Alpha_Scheduler.max_epoch=0 Alpha_Scheduler.min_value=0.1 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml Trainer.checkpoint=${save_dir}/jsd_0.1label_0.0 Trainer.save_dir=${save_dir}/jsd_0.1label_0.0 Lab_Partitions.partition_sets=0.1 Alpha_Scheduler.begin_epoch=0 Alpha_Scheduler.max_epoch=0 Alpha_Scheduler.min_value=0.0 StartTraining.train_jsd=True"

)

for cmd in "${StringArray[@]}"
do
echo ${cmd}
CC_wrapper "${time}" "${account}" "${cmd}" 16 "${minutes}"

done
