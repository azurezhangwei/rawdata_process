#!/bin/bash

#source /data01/software/bashrc
python /data01/software/CNN-Diffusion-MRIBrain-Segmentation/pipeline/dwi_masking.py -i dwi_file_paths_1.txt -f /data01/software/CNN-Diffusion-MRIBrain-Segmentation/model_folder -nproc 16