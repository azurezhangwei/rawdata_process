import os
import subprocess

# 设置 FreeSurfer 输出目录
SUBJECTS_DIR = "./freesurfer_output"
os.environ["SUBJECTS_DIR"] = SUBJECTS_DIR

# 获取所有个体列表（排除 fsaverage 和目录不存在的个体）
all_subjects = [s for s in os.listdir(SUBJECTS_DIR) if os.path.isdir(os.path.join(SUBJECTS_DIR, s))]

# 检查每个个体是否包含所需的 stats 文件
valid_subjects = []
skipped_subjects = {}

for subject in all_subjects:
    stats_dir = os.path.join(SUBJECTS_DIR, subject, "stats")
    lh_stats = os.path.join(stats_dir, "lh.aparc.stats")
    rh_stats = os.path.join(stats_dir, "rh.aparc.stats")
    aseg_stats = os.path.join(stats_dir, "aseg.stats")

    missing_files = []
    if not os.path.exists(lh_stats):
        missing_files.append("lh.aparc.stats")
    if not os.path.exists(rh_stats):
        missing_files.append("rh.aparc.stats")
    if not os.path.exists(aseg_stats):
        missing_files.append("aseg.stats")

    if missing_files:
        skipped_subjects[subject] = missing_files
    else:
        valid_subjects.append(subject)

# 将有效个体写入文件
subject_list_file = "valid_subjects.txt"
with open(subject_list_file, "w") as f:
    for subject in valid_subjects:
        f.write(subject + "\n")

# 记录被跳过的个体及原因
skipped_list_file = "skipped_subjects.txt"
with open(skipped_list_file, "w") as f:
    for subject, missing_files in skipped_subjects.items():
        f.write(f"{subject}: missing {', '.join(missing_files)}\n")

# 确保至少有一个有效个体
if not valid_subjects:
    print("No valid subjects found. Please check your data.")
    print(f"See details in {skipped_list_file}")
    exit()

# 运行 FreeSurfer 命令导出数据
def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Command executed successfully: {command}")
    except subprocess.CalledProcessError:
        print(f"Error executing: {command}")

# 1. 导出所有个体的皮层厚度
run_command(f"aparcstats2table --subjectsfile {subject_list_file} --hemi lh --meas thickness --tablefile lh_thickness.csv --delimiter ','")
run_command(f"aparcstats2table --subjectsfile {subject_list_file} --hemi rh --meas thickness --tablefile rh_thickness.csv --delimiter ','")

# 2. 导出所有个体的皮层各区域体积
run_command(f"aparcstats2table --subjectsfile {subject_list_file} --hemi lh --meas volume --tablefile lh_volume.csv --delimiter ','")
run_command(f"aparcstats2table --subjectsfile {subject_list_file} --hemi rh --meas volume --tablefile rh_volume.csv --delimiter ','")

# 3. 导出所有个体的皮层下结构体积
run_command(f"asegstats2table --subjectsfile {subject_list_file} --meas volume --tablefile aseg_volumes.csv --delimiter ','")

print("所有统计数据导出完成！")
print(f"Skipped subjects recorded in {skipped_list_file}")