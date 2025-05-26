import io
import os
import zipfile

from werkzeug.utils import secure_filename

from configs.static import PATH


def allowed_file(filename, postfixes):
    """检查文件后缀"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in postfixes


def save_file(file):
    """存储文件"""
    filename = secure_filename(file.filename)
    path = os.path.join(PATH, filename)
    file.save(path)

    return path


def upload_files(files, allowed_extensions_mat=None):
    """接收前端上传的多个文件，分别存入文件系统，并依次返回存储路径"""
    paths = []

    if allowed_extensions_mat is None:
        for file in files:
            paths.append(save_file(file))
    else:
        if len(files) != len(allowed_extensions_mat):
            raise ValueError('文件列表长度与允许扩展名列表长度不匹配！')
        for (file, allowed_extensions) in zip(files, allowed_extensions_mat):
            if allowed_extensions and not allowed_file(file.filename, allowed_extensions):
                raise ValueError(f'\'{file.filename}\'的扩展名不是{allowed_extensions}之一')
            paths.append(save_file(file))

    return paths


def download_files(paths):
    """将多个文件打包提，以供给前端下载"""
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for data, path in paths.items():
            if path:
                with open(path, 'rb') as f:
                    zip_file.writestr(f'{data}.{os.path.splitext(os.path.basename(path))[-1]}', f.read())

    # 重置文件指针
    zip_buffer.seek(0)
    return zip_buffer
