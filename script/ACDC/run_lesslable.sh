#!/usr/bin/env bash
cd ../../
save_dir=deep_cotraining_jsd_alpha_lesslabel
declare -a StringArray=(
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/baseline_f Lab_Partitions.partition_sets=1.0 "

"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/baseline_p Lab_Partitions.partition_sets=0.1"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_1.0 Lab_Partitions.partition_sets=0.1 Alpha_Scheduler.begin_epoch=200 StartTraining.train_jsd=True "
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_0.8 Alpha_Scheduler.min_value=0.8 Lab_Partitions.partition_sets=0.1 StartTraining.train_jsd=True "
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_0.5 Alpha_Scheduler.min_value=0.5 Lab_Partitions.partition_sets=0.1 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_0.0 Alpha_Scheduler.min_value=0.0 Lab_Partitions.partition_sets=0.1 StartTraining.train_jsd=True"

"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_ramp0.5 Lab_Partitions.partition_sets=0.1 Alpha_Scheduler.begin_epoch=50 Alpha_Scheduler.max_epoch=150 Alpha_Scheduler.min_value=0.5 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_ramp0.0 Lab_Partitions.partition_sets=0.1 Alpha_Scheduler.begin_epoch=50 Alpha_Scheduler.max_epoch=150 Alpha_Scheduler.min_value=0.0 StartTraining.train_jsd=True"
)
# just using 0 and 1 gpus for those jobs
gpuqueue "${StringArray[@]}" --available_gpus 0 5 6