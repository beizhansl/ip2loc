import os
from datetime import datetime

def convert_unix_timestamp_to_date(file_name):
    # 将文件名中的扩展名提取出来
    base_name, extension = os.path.splitext(file_name)
    pref_name = str.split(base_name, '_')[0]
    base = str.split(base_name, '_')[1]
    after_name = str.split(base_name, '_')[2]
    # 将Unix时间戳转换为日期格式
    timestamp = int(base) / 1e9
    date_object = datetime.utcfromtimestamp(timestamp)
    formatted_date = date_object.strftime("%Y-%m-%d")

    # 构建新的文件名
    new_name = pref_name+'_'+formatted_date+'_'+after_name
    new_file_name = f"{new_name}{extension}"

    return new_file_name

# 示例用法
# old_file_name = "Aiops站点-前端日志_1696953600000000000_day.json"  # 替换为实际的文件名
# new_file_name = convert_unix_timestamp_to_date(old_file_name)
# print(new_file_name)

def rename_files_in_directory(directory_path):
    # 遍历目录下的所有文件
    for filename in os.listdir(directory_path):
        # 构建文件的完整路径
        file_path = os.path.join(directory_path, filename)

        # 检查是否是文件
        if os.path.isfile(file_path):
            # 对文件名进行转换
            new_file_name = convert_unix_timestamp_to_date(filename)

            # 构建新的文件路径
            new_file_path = os.path.join(directory_path, new_file_name)

            # 重命名文件
            os.rename(file_path, new_file_path)
            print(f"Renamed: {filename} -> {new_file_name}")

# 示例用法
directory_path = "./loc/day/"  # 替换为实际的目录路径
rename_files_in_directory(directory_path)
