# Seafile batch upload

From the filesystem of the server running Seafile, uploads a folder, it subfolders and all its files, to a library

Features:

- asynchronous (configurable)
- resilient: the script can be restarted if it has been interrupted, without uploading twice a file already present

:warning: It is configure to replace files already present. This is intentional, if the script has been interrupted some files might be corrupted and need to be reuploaded.

It is intended for a Linux server.

## Installation

```bash
# Download the source code
git clone https://github.com/Pyrrhu5/seafile-batch-upload.git
cd seafile-batch-upload
# Install the dependencies
# Python venv is highly recommended, needs to be install:
# apt install python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Setup

Copy and fill a `.env` file

```bash
cp env_template .env
```

Variable | Mandatory? | Description
--- | :---: | ---
SEAFILE_SERVER | :heavy_check_mark: | The complete address to the Seafile server (but not the route to the API), including `http`
SEAFILE_ADMIN_USER | :heavy_check_mark: | The email address of a user having access to both the API and the target library
SEAFILE_ADMIN_PWD | :heavy_check_mark: | The password of the user mentioned above
SEAFILE_LIBRARY_ID | :heavy_check_mark: | The ID of the target library. It can be found in the url when visiting the library on the web UI. For example `http://<MY_SERVER>/library/<MY_LIBRARY_ID>/`
LOCAL_FOLDER= | :heavy_check_mark: | The absolute path to the local folder to upload
CONCURRENT_UPLOAD | :heavy_multiplication_x: | The number of concurrent uploads. Default to 20. Lower this value if a lot of Gateway error occurs

## Usage

:warning: Use at your own risks, the license does not provide any guarantees.

Once the `.env` is set

```bash
# if not already activated
source .venv/bin/activate

python ./seafile_batch_upload.py
```

The execution will create two files. It is recommended to delete them between uploads to different library and local folder.

Filename | Description
--- | ---
uploaded_files.log | A list of local path for the files successfully uploaded. Delete from this list the item which need to be re-uploaded. Used in the retry process
error.log | Present only in case of errors. A list of error messages for each file which failed to upload. It is not used in the script, can be safely deleted or modified. Only present to inform the user
