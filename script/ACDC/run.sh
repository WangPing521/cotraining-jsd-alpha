#!/usr/bin/env bash
cd ../../
save_dir=deep_cotraining_jsd_alpha
declare -a StringArray=(
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/baseline_f Lab_Partitions.partition_sets=1.0 "
#"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/baseline_p "
#"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd StartTraining.train_jsd=True "
#"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/adv StartTraining.train_adv=True "
#"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_adv StartTraining.train_jsd=True StartTraining.train_adv=True "

"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/baseline_p "
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_1.0 Alpha_Scheduler.begin_epoch=300 StartTraining.train_jsd=True "
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_0.8 Alpha_Scheduler.min_value=0.8 StartTraining.train_jsd=True "
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_0.6 Alpha_Scheduler.min_value=0.6 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_0.5 Alpha_Scheduler.min_value=0.5 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_0.4 Alpha_Scheduler.min_value=0.4 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_0.2 Alpha_Scheduler.min_value=0.2 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_0.1 Alpha_Scheduler.min_value=0.1 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_0.0 Alpha_Scheduler.min_value=0.0 StartTraining.train_jsd=True"

"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_ramp0.8 Alpha_Scheduler.begin_epoch=90 Alpha_Scheduler.max_epoch=250 Alpha_Scheduler.min_value=0.8 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_ramp0.5 Alpha_Scheduler.begin_epoch=90 Alpha_Scheduler.max_epoch=250 Alpha_Scheduler.min_value=0.5 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_ramp0.2 Alpha_Scheduler.begin_epoch=90 Alpha_Scheduler.max_epoch=250 Alpha_Scheduler.min_value=0.2 StartTraining.train_jsd=True"
"python train_ACDC_cotraining.py  config=config/ACDC_config_cotraing.yaml  Trainer.save_dir=${save_dir}/jsd_ramp0.0 Alpha_Scheduler.begin_epoch=90 Alpha_Scheduler.max_epoch=250 Alpha_Scheduler.min_value=0.0 StartTraining.train_jsd=True"
)
# just using 0 and 1 gpus for those jobs
gpuqueue "${StringArray[@]}" --available_gpus 0 5 6