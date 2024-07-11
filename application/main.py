import os
import time
import ftplib
import xml.etree.ElementTree as ET
import shutil

FTP_HOST = 'localhost'
FTP_USER = 'nybsys'
FTP_PASS = '12345'
TEMP_FOLDER = 'temp'
LOCAL_FOLDER = 'local'
TRASH_FOLDER = 'trash'

def connect_ftp():
    ftp = ftplib.FTP()
    ftp.connect(FTP_HOST, 21)
    ftp.login(FTP_USER, FTP_PASS)

    return ftp

def get_ftp_files(ftp):
    ftp_files = ftp.nlst()

    return ftp_files

def download_file(ftp, filename):
    local_temp_path = os.path.join(TEMP_FOLDER, filename)
    with open(local_temp_path, 'wb') as f:
        ftp.retrbinary(f'RETR {filename}', f.write)

    return local_temp_path

def move_file_to_local(filename):
    local_path = os.path.join(LOCAL_FOLDER, filename)
    temp_path = os.path.join(TEMP_FOLDER, filename)
    os.rename(temp_path, local_path)

def file_in_trash(filename):
    return os.path.exists(os.path.join(TRASH_FOLDER, filename))

def process_xml_file(filepath):
    tree = ET.parse(filepath)
    root = tree.getroot()

    namespace = {'ns': 'http://www.3gpp.org/ftp/specs/archive/32_series/32.435#measCollec'}

    data_dict = {}
    for measType in root.findall('.//ns:measType', namespace):
        param_name = measType.text.strip()
        param_value = int(measType.attrib['p'])
        data_dict[param_value] = param_name

    return data_dict

def move_file_to_trash(filepath):
    filename = os.path.basename(filepath)
    trash_path = os.path.join(TRASH_FOLDER, filename)
    shutil.move(filepath, trash_path)

def ftp_files_watch_and_download():
    try:
        ftp = connect_ftp()
        ftp_files = get_ftp_files(ftp)
        
        for filename in ftp_files:
            if not file_in_trash(filename):
                download_file(ftp, filename)
                move_file_to_local(filename)

        ftp.quit()
    except ftplib.all_errors as e:
        print(f"FTP error: {e}")

def monitor_local_folder():
    files = os.listdir(LOCAL_FOLDER)

    for filename in files:
        file_path = os.path.join(LOCAL_FOLDER, filename)
        data_dict = process_xml_file(file_path)
        print(f"Processed data from {filename}: {data_dict}")
        move_file_to_trash(file_path)

def main():
    if not os.path.exists(TEMP_FOLDER):
        os.makedirs(TEMP_FOLDER)
    if not os.path.exists(LOCAL_FOLDER):
        os.makedirs(LOCAL_FOLDER)
    if not os.path.exists(TRASH_FOLDER):
        os.makedirs(TRASH_FOLDER)

    while True:
        ftp_files_watch_and_download()

        monitor_local_folder()

        time.sleep(10)
    
if __name__ == "__main__":
    main()
