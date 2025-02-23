import os
import conversion

# 定义BIDS根目录
bids_root = '/data05/weizhang_projects/rawdata-willimas'

# 遍历所有个体（sub-*）
for subject in os.listdir(bids_root):
    if subject.startswith('sub-'):
        subject_dir = os.path.join(bids_root, subject)

        # 遍历所有 session（ses-*）
        for session in os.listdir(subject_dir):
            if session.startswith('ses-'):
                session_dir = os.path.join(subject_dir, session, 'dwi')

                # 检查是否存在 dwi 目录
                if os.path.exists(session_dir):
                    # 定义输入文件路径
                    dwi_nii = os.path.join(session_dir, f'{subject}_{session}_dwi.nii.gz')
                    dwi_bval = os.path.join(session_dir, f'{subject}_{session}_dwi.bval')
                    dwi_bvec = os.path.join(session_dir, f'{subject}_{session}_dwi.bvec')

                    # 定义输出文件路径
                    dwi_nhdr = os.path.join(session_dir, f'{subject}_{session}_dwi.nhdr')

                    # 检查所有必需文件是否存在
                    if all(os.path.exists(f) for f in [dwi_nii, dwi_bval, dwi_bvec]):
                        # 执行转换
                        conversion.nhdr_write(dwi_nii, dwi_bval, dwi_bvec, dwi_nhdr)
                        print(f"Conversion done: {dwi_nhdr}")
                    else:
                        print(f"miss necessary files, jump it: {session_dir}")
                else:
                    print(f"didn't find dwi，jump it: {session_dir}")