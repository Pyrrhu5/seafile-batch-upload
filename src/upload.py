import asyncio
import os

import aiohttp
import requests

from src.access_token import Token
from src.constants import CONCURRENT_UPLOAD, ERRORS_LOG_FILENAME, LIBRARY_ID, LOCAL_FOLDER, SEAFILE_SERVER, SUCCESS_LOG_FILENAME


def load_uploaded(logfile):
    if not os.path.exists(logfile):
        return set()
    with open(logfile, 'r') as f:
        return set(line.strip() for line in f)


def save_uploaded(logfile, filepath):
    with open(logfile, 'a') as f:
        f.write(filepath + '\n')


def save_error(logfile, error_msg):
    with open(logfile, "a") as f:
        f.write(error_msg + "\n")


def create_dir(token, repo_id, remote_path):
    if remote_path == "/":
        return
    url = f'{SEAFILE_SERVER}/api2/repos/{repo_id}/dir/'
    headers = {'Authorization': f'Token {token}'}

    params = {"path": remote_path}
    directory_exists_request = requests.get(
        url, headers=headers, params=params)
    for node in directory_exists_request.json():
        if node.get("type") == "dir":
            print("Folder already exists")
            return

    params = {'p': remote_path}
    payload = {"operation": "mkdir"}
    r = requests.post(url, headers=headers, params=params, data=payload)
    if r.status_code == 201:
        print(f'Created folder: {remote_path}')
    else:
        print(r.content)
        r.raise_for_status()


def get_upload_link(token, repo_id):
    url = f'{SEAFILE_SERVER}/api2/repos/{repo_id}/upload-link/'
    headers = {'Authorization': f'Token {token}'}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.text.strip('"')


async def upload_file(token, upload_link, remote_path, local_file_path):
    if remote_path != "/":
        remote_path = remote_path.lstrip("/")
    headers = {'Authorization': f'Token {token}'}
    files = {
        "file": open(local_file_path, 'rb'),
        "replace": "1",
        "parent_dir": "/",
        "relative_path": remote_path,
    }
    form = aiohttp.FormData()
    for name, value in files.items():
        form.add_field(name, value)
    async with aiohttp.ClientSession() as session:
        async with session.post(upload_link, headers=headers, data=form) as response:
            response.raise_for_status()
            print(f'Uploaded: {local_file_path} -> {remote_path}')


async def upload_file_wrapper(upload_link, remote_path, local_file_path, semaphore):
    async with semaphore:
        token = Token.get_token()
        try:
            await upload_file(token, upload_link, remote_path, local_file_path)
            save_uploaded(SUCCESS_LOG_FILENAME, local_file_path)
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 403:
                Token.renew_token()
                await upload_file_wrapper(upload_link, remote_path, local_file_path, semaphore)
            else:
                msg = f'HTTP error when uploading {local_file_path}: {e}'
                print(msg)
                save_error(ERRORS_LOG_FILENAME, msg)
        except Exception as e:
            msg = f'Failed to upload {local_file_path}: {e}'
            print(msg)
            save_error(ERRORS_LOG_FILENAME, msg)


async def upload_folder():
    upload_link = get_upload_link(Token.get_token(), LIBRARY_ID)
    uploaded = load_uploaded('uploaded_files.log')

    semaphore = asyncio.Semaphore(CONCURRENT_UPLOAD)

    for dirpath, _, filenames in os.walk(LOCAL_FOLDER):
        print(f"Uploading from directory {dirpath}")
        rel_path = os.path.relpath(dirpath, LOCAL_FOLDER)
        remote_path = '/' if rel_path == '.' else '/' + \
            rel_path.replace(os.sep, '/')
        create_dir(Token.get_token(), LIBRARY_ID, remote_path)

        to_upload = list()
        for filename in filenames:
            local_file_path = os.path.join(dirpath, filename)
            if local_file_path in uploaded:
                print(f'Skipping already uploaded: {local_file_path}')
                continue
            to_upload.append(upload_file_wrapper(
                upload_link, remote_path, local_file_path, semaphore))
        await asyncio.gather(*to_upload)
