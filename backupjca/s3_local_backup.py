
import boto3
import subprocess
import os
import re
from multiprocessing import freeze_support
from typeguard import typechecked

from balsa import get_logger
from pressenter2exit import PressEnter2ExitGUI

from backupjca import __application_name__, __version__

log = get_logger(__application_name__)

freeze_support()


# sundry candidate
def get_dir_size(dir_path):
    dir_size = 0
    file_count = 0
    for dir_path, _, file_names in os.walk(dir_path):
        for file_name in file_names:
            file_count += 1
            dir_size += os.path.getsize(os.path.join(dir_path, file_name))
    return dir_size, file_count


@typechecked
def s3_local_backup(backup_directory: str, aws_profile: (str, None), dry_run: bool, excludes: (list, None)):

    os.makedirs(backup_directory, exist_ok=True)

    log.info(f"{__application_name__} : {__version__}")

    if aws_profile is not None:
        session = boto3.Session(profile_name=aws_profile)
        s3_client = session.client('s3')
    else:
        s3_client = boto3.client('s3')

    decoding = "utf-8"

    # we delete all whitespace below
    ls_re = re.compile(r"TotalObjects:([0-9]+)TotalSize:([0-9]+)")

    buckets = s3_client.list_buckets()['Buckets']
    s = f"found {len(buckets)} buckets"
    log.info(s)
    print(s)

    press_enter_to_exit = PressEnter2ExitGUI(title="S3 local backup")

    for bucket in buckets:

        if not press_enter_to_exit.is_alive():
            break

        # do the sync
        bucket_name = bucket['Name']

        if excludes is not None and bucket_name in excludes:
            s = f"excluding bucket : {bucket_name}"
            log.info(s)
            print(s)
        else:
            s = f"bucket : {bucket_name}"
            log.info(s)
            print(s)

            destination = os.path.join(backup_directory, bucket_name)
            os.makedirs(destination, exist_ok=True)
            s3_bucket_path = f"s3://{bucket_name}"
            # Don't use --delete.  We want to keep 'old' files locally.
            sync_command_line = ['aws', 's3', 'sync', s3_bucket_path, destination]
            if dry_run:
                sync_command_line.append('--dryrun')
            log.info(str(sync_command_line))
            sync_result = subprocess.run(sync_command_line, stdout=subprocess.PIPE)
            for line in sync_result.stdout.decode(decoding).splitlines():
                log.info(line.strip())

            # check the results
            ls_command_line = ['aws', 's3', 'ls', '--summarize', '--recursive', s3_bucket_path]
            log.info(str(ls_command_line))
            ls_result = subprocess.run(ls_command_line, stdout=subprocess.PIPE)
            ls_stdout = ''.join([c for c in ls_result.stdout.decode(decoding) if c not in ' \r\n'])  # remove all whitespace
            ls_parsed = ls_re.search(ls_stdout)
            s3_object_count = int(ls_parsed.group(1))
            s3_total_size = int(ls_parsed.group(2))
            local_size, local_count = get_dir_size(destination)
            # rough check that the sync worked
            if s3_total_size > local_size:
                # we're missing files
                message = "not all files backed up"
                error_routine = log.error
            elif s3_total_size != local_size:
                # don't compare number of files since aws s3 sync does not copy files of zero size
                message = "mismatch"
                error_routine = log.warning
            else:
                message = "match"
                error_routine = log.info
            if error_routine is not None:
                error_routine(f"{bucket_name} : {message} (s3_count={s3_object_count}, local_count={local_count}; s3_total_size={s3_total_size}, local_size={local_size})")
