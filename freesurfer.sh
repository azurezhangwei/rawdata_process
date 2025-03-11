#!/bin/bash

# source /data01/software/bashrc

BIDS_DIR="/data05/weizhang_projects/rawdata-willimas"
SUBJECTS_DIR="/data05/weizhang_projects/rawdata_willimas_process/freesurfer_output"
mkdir SUBJECTS_DIR
export SUBJECTS_DIR

# 定义并行任务数（根据系统 CPU 核心数调整）
PARALLEL_JOBS=50

# 获取所有被试和会话的任务列表
TASKS=()
for subject in $(ls $BIDS_DIR | grep sub-); do
    for session in $(ls $BIDS_DIR/$subject | grep ses-); do
        T1w=$(ls $BIDS_DIR/$subject/$session/anat/*T1w.nii.gz)
        output_dir="${subject}_${session}"
        echo "${output_dir}"
        TASKS+=("recon-all -i $T1w -s $output_dir -all")
    done
done

# 使用 GNU Parallel 并行运行任务
printf "%s\n" "${TASKS[@]}" | parallel -j $PARALLEL_JOBS