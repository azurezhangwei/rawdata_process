import os
import nibabel as nib
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import pandas as pd
'''
check center slicer image of dwi and T1 and T2 with BIDS standard
'''
# 定义BIDS根目录
BIDS_DIR = "/data05/weizhang_projects/rawdata-willimas"
OUTPUT_DIR = "/data05/weizhang_projects/rawdata_willimas_process/quality_control_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 定义图像输出文件夹
IMAGE_DIR = os.path.join(OUTPUT_DIR, "images")
os.makedirs(IMAGE_DIR, exist_ok=True)

# 定义模态和对应的文件名模式
MODALITIES = {
    "T1": "T1w.nii.gz",
    "T2": "T2w.nii.gz",
    "dwi": "dwi.nii.gz"
}

# 定义轴向切片名称
AXES = ["Sagittal", "Coronal", "Axial"]


def extract_center_slices(data, axis):
    """从3D数据中提取中心切片"""
    if axis == "Sagittal":
        return data[data.shape[0] // 2, :, :]
    elif axis == "Coronal":
        return data[:, data.shape[1] // 2, :]
    elif axis == "Axial":
        return data[:, :, data.shape[2] // 2]
    else:
        raise ValueError("Invalid axis")


def plot_slices(data, subject, session, modality):
    """绘制三个轴向的中心切片"""
    fig = plt.figure(figsize=(10, 4))
    gs = GridSpec(1, 3, figure=fig)

    for i, axis in enumerate(AXES):
        ax = fig.add_subplot(gs[0, i])
        slice_data = extract_center_slices(data, axis)
        ax.imshow(slice_data.T, cmap="gray", origin="lower")
        ax.set_title(f"{axis} View")
        ax.axis("off")

    plt.suptitle(f"Subject: {subject}, Session: {session}, Modality: {modality}")
    plt.tight_layout()

    # 保存图像
    output_path = os.path.join(IMAGE_DIR, f"{subject}_{session}_{modality}.png")
    plt.savefig(output_path)
    plt.close(fig)  # 显式关闭图像，避免内存泄漏
    return output_path


def generate_qc_report(subjects):
    """生成QC报告网页"""
    html_content = "<html><body>"
    html_content += "<h1>Quality Control Report</h1>"

    for subject, sessions in subjects.items():
        html_content += f"<h2>Subject: {subject}</h2>"
        for session, modalities in sessions.items():
            html_content += f"<h3>Session: {session}</h3>"
            for modality, image_info in modalities.items():
                image_path = image_info["image_path"]
                resolution = image_info["resolution"]
                html_content += f"<h4>Modality: {modality}</h4>"
                html_content += f"<p>Resolution: {resolution}</p>"
                html_content += f'<img src="images/{os.path.basename(image_path)}" alt="{subject}_{session}_{modality}" style="width:100%;">'

    html_content += "</body></html>"

    # 保存HTML文件
    html_path = os.path.join(OUTPUT_DIR, "qc_report.html")
    with open(html_path, "w") as f:
        f.write(html_content)

    return html_path


def generate_statistics_csv(subjects, output_csv):
    """生成统计信息CSV文件"""
    statistics = []

    for subject, sessions in subjects.items():
        for session, modalities in sessions.items():
            session_data = {
                "Subject": subject,
                "Session": session,
                "Has_T1": "No",
                "T1_Resolution": "N/A",
                "Has_T2": "No",
                "T2_Resolution": "N/A",
                "Has_dwi": "No",
                "dwi_Resolution": "N/A"
            }

            # 检查每个模态
            for modality in ["T1", "T2", "dwi"]:
                if modality in modalities:
                    session_data[f"Has_{modality}"] = "Yes"
                    session_data[f"{modality}_Resolution"] = modalities[modality]["resolution"]

            statistics.append(session_data)

    # 转换为DataFrame并保存
    df = pd.DataFrame(statistics)

    # 优化列顺序
    columns = ["Subject", "Session",
               "Has_T1", "T1_Resolution",
               "Has_T2", "T2_Resolution",
               "Has_dwi", "dwi_Resolution"]

    df = df[columns]
    df.to_csv(output_csv, index=False)


def main():
    subjects = {}

    # 遍历BIDS目录
    for subject in os.listdir(BIDS_DIR):
        if not subject.startswith("sub-"):
            continue

        subject_path = os.path.join(BIDS_DIR, subject)
        subjects[subject] = {}

        for session in os.listdir(subject_path):
            if not session.startswith("ses-"):
                continue

            session_path = os.path.join(subject_path, session)
            subjects[subject][session] = {}

            # 检查anat文件夹
            anat_dir = os.path.join(session_path, "anat")
            if os.path.exists(anat_dir):
                for modality, pattern in MODALITIES.items():
                    if modality in ["T1", "T2"]:
                        target_file = f"{subject}_{session}_{pattern}"
                        file_path = os.path.join(anat_dir, target_file)

                        if os.path.exists(file_path):
                            try:
                                img = nib.load(file_path)
                                data = img.get_fdata()
                                image_path = plot_slices(data, subject, session, modality)
                                zooms = img.header.get_zooms()[:3]  # 获取分辨率
                                res_str = f"{zooms[0]:.2f}x{zooms[1]:.2f}x{zooms[2]:.2f} mm"

                                # 保存图像路径和分辨率
                                subjects[subject][session][modality] = {
                                    "image_path": image_path,
                                    "resolution": res_str
                                }
                            except Exception as e:
                                print(f"Error processing {file_path}: {str(e)}")

            # 检查dwi文件夹
            dwi_dir = os.path.join(session_path, "dwi")
            if os.path.exists(dwi_dir):
                modality = "dwi"
                target_file = f"{subject}_{session}_{MODALITIES[modality]}"
                file_path = os.path.join(dwi_dir, target_file)

                if os.path.exists(file_path):
                    try:
                        img = nib.load(file_path)
                        # 对于DWI数据，取第一个b0图像
                        data = img.get_fdata()[..., 0]  # 取第一个b0图像
                        image_path = plot_slices(data, subject, session, modality)
                        zooms = img.header.get_zooms()[:3]  # 获取分辨率
                        res_str = f"{zooms[0]:.2f}x{zooms[1]:.2f}x{zooms[2]:.2f} mm"

                        # 保存图像路径和分辨率
                        subjects[subject][session][modality] = {
                            "image_path": image_path,
                            "resolution": res_str
                        }
                    except Exception as e:
                        print(f"Error processing {file_path}: {str(e)}")

    # 生成QC报告
    html_path = generate_qc_report(subjects)
    print(f"QC report generated: {html_path}")

    # 生成统计信息CSV文件
    csv_path = os.path.join(OUTPUT_DIR, "detailed_statistics.csv")
    generate_statistics_csv(subjects, csv_path)
    print(f"Detailed statistics CSV generated: {csv_path}")


if __name__ == "__main__":
    main()