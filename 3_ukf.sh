#!/bin/bash

# source /data01/software/bashrc

# 设置 Slicer 相关库路径
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/data01/software/Slicer-5.2.2-linux-amd64/lib/Slicer-5.2
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/data01/software/Slicer-5.2.2-linux-amd64/NA-MIC/Extensions-31382/UKFTractography/lib/Slicer-5.2/qt-loadable-modules
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/data01/software/Slicer-5.2.2-linux-amd64/lib
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/data01/software/Slicer-5.2.2-linux-amd64/lib/Teem-1.12.0

# UKFTractography 可执行文件路径
UKFTractography=/data01/software/Slicer-5.2.2-linux-amd64/NA-MIC/Extensions-31382/UKFTractography/lib/Slicer-5.2/cli-modules/UKFTractography

# BIDS 数据目录
BIDS_DIR="/data05/weizhang_projects/rawdata-willimas"

# 遍历所有 sub-* 目录
for subject_dir in ${BIDS_DIR}/sub-*; do
    subject=$(basename "$subject_dir")
    echo "$subject"

    # 查找 ses-* 目录
    for session_dir in ${subject_dir}/ses-*; do
        session=$(basename "$session_dir")

        # 查找 DWI 目录
        dwi_dir="${session_dir}/dwi"
        if [ ! -d "$dwi_dir" ]; then
            continue
        fi

        # 查找 QCed.nrrd 文件
        DWIQCed_nrrd=$(find "$dwi_dir" -name "*_dwi_QCed.nrrd" | head -n 1)
        if [ -z "$DWIQCed_nrrd" ]; then
            echo "No QCed DWI file found for $subject $session"
            continue
        fi

        # 设定输出文件夹
        data_dwi_space_folder="$dwi_dir"
        RGVP_mask="${data_dwi_space_folder}/${subject}_${session}_dwi_QCed_bse-multi_BrainMask.nhdr"
        if [ ! -f "$RGVP_mask" ]; then
          #转换nii.gz to .nrrd
          echo "conversion ${RGVP_mask}"
          RGVP_mask_nii="${data_dwi_space_folder}/${subject}_${session}_dwi_QCed_bse-multi_BrainMask.nii.gz"
          nhdr_write.py --nifti "$RGVP_mask_nii" --nhdr "$RGVP_mask"
        fi

        outputdir="$data_dwi_space_folder/UKFTractography"
        mkdir -p "$outputdir"

        # 设置输出文件
        output_file="$outputdir/${subject}_${session}_dwi_tractography.vtk"

        # 如果文件还未处理，则进行处理
        if [ ! -f "$output_file" ]; then
            echo "Processing $DWIQCed_nrrd"
            $UKFTractography --dwiFile "$DWIQCed_nrrd" \
                             --maskFile "$RGVP_mask" \
                             --seedsFile "$RGVP_mask" \
                             --numTensor 2 \
                             --seedsPerVoxel 7 \
                             --stoppingThreshold 0.06 \
                             --stoppingFA 0.08 \
                             --seedingThreshold 0.1 \
                             --tracts "$output_file" \
                             --recordFA \
                             --recordTrace \
                             --recordTensors \
                             --numThreads 50
        fi

#        exit
    done
done