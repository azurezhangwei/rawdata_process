#!/bin/bash

# 设置环境变量
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/weizhang/Slicer-5.2.2-linux-amd64/NA-MIC/Extensions-31382/SlicerDMRI/lib/Slicer-5.2/qt-loadable-modules
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/weizhang/Slicer-5.2.2-linux-amd64/lib/Slicer-5.2
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/weizhang/Slicer-5.2.2-linux-amd64/lib/Teem-1.12.0
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/weizhang/Slicer-5.2.2-linux-amd64/lib
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/weizhang/Slicer-5.2.2-linux-amd64/lib/Python/lib
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/weizhang/Slicer-5.2.2-linux-amd64/lib/Slicer-5.2/cli-modules
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/weizhang/Desktop/Slicer-4.8.1-linux-amd64/lib/Slicer-4.8

# 设置 DTIPrep 工具路径
DTIPrep=/home/weizhang/DTIPrep1.2/DTIPrep

# BIDS 目录路径
BIDS_DIR="../rawdata-willimas"

# 遍历所有受试者
for sub in "$BIDS_DIR"/sub-*; do
    sub_id=$(basename "$sub")  # 提取 sub-XX

    # 遍历该受试者的所有 session
    for ses in "$sub"/ses-*; do
        ses_id=$(basename "$ses")  # 提取 ses-XX
        dwi_dir="$ses/dwi"

        # 检查 DWI 目录是否存在
        if [ -d "$dwi_dir" ]; then
            for dwi_file in "$dwi_dir"/*.nhdr; do
                if [ -f "$dwi_file" ]; then
                    base_name=$(basename "$dwi_file" .nhdr)
                    QCed_nrrd="${dwi_dir}/${base_name}_QCed.nrrd"

                    # 运行 DTIPrep 进行质量控制
                    if [ ! -f "$QCed_nrrd" ]; then
                        echo "Running DTIPrep on $dwi_file..."
                        "$DTIPrep" --DWINrrdFile "$dwi_file" --check --xmlProtocol ./dtiprepprotocalonlyeddy.xml
                    else
                        echo "DTIPrep already processed $QCed_nrrd. Skipping."
                    fi
                fi
            done
        else
            echo "No DWI data for $sub_id $ses_id, skipping..."
        fi
    done
done