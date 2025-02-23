import os
import re


'''
This script is used to correct the names of files to BIDS standard.
'''

# 定义BIDS根目录
BIDS_DIR = "/data05/weizhang_projects/rawdata-willimas"

# 定义BIDS命名规范的正则表达式
BIDS_PATTERN = {
    "T1": re.compile(r"^(sub-[a-zA-Z0-9]+)_(ses-[a-zA-Z0-9]+)_(T1w\.nii\.gz)$"),
    "dwi": re.compile(r"^(sub-[a-zA-Z0-9]+)_(ses-[a-zA-Z0-9]+)_(dwi\.nii\.gz)$")
}

def check_and_rename_file(file_path, expected_pattern, modality):
    """
    检查文件命名是否符合BIDS规范，如果不符合则重命名
    """
    file_dir, file_name = os.path.split(file_path)

    # 检查文件扩展名
    if file_name.endswith(".nii"):
        # 如果文件是 .nii 格式，重命名为 .nii.gz
        new_name = file_name + ".gz"
        new_path = os.path.join(file_dir, new_name)
        os.rename(file_path, new_path)
        print(f"rename: {file_name} -> {new_name}")
        file_name = new_name  # 更新文件名以继续后续处理

    match = expected_pattern.match(file_name)

    if not match:
        # 提取被试和会话信息
        parts = file_name.split("_")
        if len(parts) >= 2:
            subject_part = parts[0]
            session_part = parts[1]
        else:
            print(f"无法解析文件名: {file_name}")
            return

        # 构建符合BIDS规范的新文件名
        if modality == "T1":
            new_name = f"{subject_part}_{session_part}_T1w.nii.gz"
        elif modality == "dwi":
            new_name = f"{subject_part}_{session_part}_dwi.nii.gz"
        else:
            print(f"unknown modality: {modality}")
            return

        # 重命名文件
        new_path = os.path.join(file_dir, new_name)
        os.rename(file_path, new_path)
        print(f"rename: {file_name} -> {new_name}")
    else:
        print(f"correct name: {file_name}")

def check_and_fix_bids_structure(bids_dir):
    """
    检查并修复BIDS文件夹结构中的命名错误
    """
    # 遍历所有被试
    for subject in os.listdir(bids_dir):
        if not subject.startswith("sub-"):
            continue

        subject_path = os.path.join(bids_dir, subject)

        # 遍历所有session
        for session in os.listdir(subject_path):
            if not session.startswith("ses-"):
                continue

            session_path = os.path.join(subject_path, session)

            # 检查anat文件夹
            anat_dir = os.path.join(session_path, "anat")
            if os.path.exists(anat_dir):
                for file_name in os.listdir(anat_dir):
                    if "nii" in file_name:
                        file_path = os.path.join(anat_dir, file_name)
                        check_and_rename_file(file_path, BIDS_PATTERN["T1"], "T1")

            # 检查dwi文件夹
            dwi_dir = os.path.join(session_path, "dwi")
            if os.path.exists(dwi_dir):
                for file_name in os.listdir(dwi_dir):
                    if "nii" in file_name:
                        file_path = os.path.join(dwi_dir, file_name)
                        check_and_rename_file(file_path, BIDS_PATTERN["dwi"], "dwi")

if __name__ == "__main__":
    check_and_fix_bids_structure(BIDS_DIR)