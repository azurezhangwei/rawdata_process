#!/bin/bash

# BIDS 目录路径
BIDS_DIR="/data05/weizhang_projects/rawdata-willimas"

# ORG Atlases 路径
ORG_ATLASES="/data01/software/ORG-Atlases"

# Slicer 及相关工具路径
SLICER_PATH="/data01/software/Slicer-5.2.2-linux-amd64/Slicer"
FIBER_TRACT_MEASUREMENTS="/data01/software/Slicer-5.2.2-linux-amd64/NA-MIC/Extensions-31382/SlicerDMRI/lib/Slicer-5.2/cli-modules/FiberTractMeasurements"

# 定义一个函数来处理每个会话
process_session() {
    ses=$1
    ORG_ATLASES=$2
    SLICER_PATH=$3
    FIBER_TRACT_MEASUREMENTS=$4

    ses_id=$(basename "$ses")  # 提取 ses-XX
    sub_id=$(basename "$(dirname "$ses")")  # 提取 sub-XX
    dwi_dir="$ses/dwi"
    echo "Processing subject: $sub_id, session: $ses_id"

    # 检查 DWI 目录是否存在
    if [ -d "$dwi_dir" ]; then
        ukf_dir="$dwi_dir/UKFTractography"
        wma_dir="$dwi_dir/WMA"

        # 如果 UKFTractography 目录存在，则查找 VTK 文件
        if [ -d "$ukf_dir" ]; then
            vtk_file=$(find "$ukf_dir" -name "*.vtk" | head -n 1)  # 获取第一个 .vtk 文件
            if [ -f "$vtk_file" ]; then
                echo "Processing VTK file: $vtk_file"
                echo "Output folder: $wma_dir"

                # 运行 wm_apply_ORG_atlas_to_subject.sh
                /data01/software/whitematteranalysis/bin/new_wm_apply_ORG_atlas_to_subject.sh \
                    -i "$vtk_file" \
                    -o "$wma_dir" \
                    -a "$ORG_ATLASES" \
                    -s "$SLICER_PATH" \
                    -d 1 \
                    -m "$FIBER_TRACT_MEASUREMENTS" \
                    -n 5
            else
                echo "No VTK file found in $ukf_dir, skipping..."
            fi
        else
            echo "No UKFTractography data for $sub_id $ses_id, skipping..."
        fi
    else
        echo "No DWI data for $sub_id $ses_id, skipping..."
    fi
}

export -f process_session

# 使用 GNU Parallel 并行处理所有受试者的会话
find "$BIDS_DIR" -type d -name "ses-*" | parallel --jobs 30 process_session {} "$ORG_ATLASES" "$SLICER_PATH" "$FIBER_TRACT_MEASUREMENTS"
