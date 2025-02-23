#!/bin/bash

# BIDS 目录路径
BIDS_DIR="/data05/weizhang_projects/rawdata-willimas"

# ORG Atlases 路径
ORG_ATLASES="/data01/software/ORG-Atlases"

# Slicer 及相关工具路径
SLICER_PATH="/data01/software/Slicer-5.2.2-linux-amd64/Slicer"
FIBER_TRACT_MEASUREMENTS="$SLICER_PATH --launch /data01/software/Slicer-5.2.2-linux-amd64/NA-MIC/Extensions-31382/SlicerDMRI/lib/Slicer-5.2/cli-modules/FiberTractMeasurements"

# 遍历所有受试者
for sub in "$BIDS_DIR"/sub-*; do
    sub_id=$(basename "$sub")  # 提取 sub-XX

    # 遍历该受试者的所有 session
    for ses in "$sub"/ses-*; do
        ses_id=$(basename "$ses")  # 提取 ses-XX
        dwi_dir="$ses/dwi"
        echo $dwi_dir

        # 检查 DWI 目录是否存在
        if [ -d "$dwi_dir" ]; then
            ukf_dir="$dwi_dir/UKFTractography"
            echo "$ukf_dir"
            wma_dir="$dwi_dir/WMA"

            # 如果 UKFTractography 目录存在，则查找 VTK 文件
            if [ -d "$ukf_dir" ]; then
                for vtk_file in "$ukf_dir"/*.vtk; do
                    if [ -f "$vtk_file" ]; then
                        echo "Processing VTK file: $vtk_file"
                        echo "Output folder: $wma_dir"

                        # 运行 wm_apply_ORG_atlas_to_subject.sh
                        /data01/software/whitematteranalysis/bin/wm_apply_ORG_atlas_to_subject.sh \
                            -i "$vtk_file" \
                            -o "$wma_dir" \
                            -a "$ORG_ATLASES" \
                            -s "$SLICER_PATH" \
                            -d 1 \
                            -m "$FIBER_TRACT_MEASUREMENTS" \
                            -n 40
                    fi
                done
            else
                echo "No UKFTractography data for $sub_id $ses_id, skipping..."
            fi
        else
            echo "No DWI data for $sub_id $ses_id, skipping..."
        fi


    done
done