import os

'''
any python environment
'''

def find_dwi_files(bids_root):
    dwi_files = []
    for root, dirs, files in os.walk(bids_root):
        for file in files:
            if file.endswith('dwi_QCed.nrrd'):
                dwi_files.append(os.path.join(root, file))
    return dwi_files

def export_to_txt(file_paths, output_file):
    with open(output_file, 'w') as f:
        for path in file_paths:
            f.write(path + '\n')

bids_root = '/data05/weizhang_projects/rawdata-willimas'  # 替换为你的BIDS目录路径
output_file = 'dwi_file_paths.txt'

dwi_files = find_dwi_files(bids_root)
export_to_txt(dwi_files, output_file)

print(f"Exproted {output_file}")