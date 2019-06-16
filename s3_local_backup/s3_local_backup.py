
import argparse
import boto3
import subprocess
import os
import re

from balsa import Balsa, get_logger

from s3_local_backup import __application_name__, __author__, __version__, __description__

log = get_logger(__application_name__)


# sundry candidate
def get_dir_size(dir_path):
    dir_size = 0
    file_count = 0
    for dir_path, _, file_names in os.walk(dir_path):
        for file_name in file_names:
            file_count += 1
            dir_size += os.path.getsize(os.path.join(dir_path, file_name))
    return dir_size, file_count


def s3_local_backup(backup_directory: str, aws_profile: str, dry_run: bool):

    os.makedirs(backup_directory, exist_ok=True)
    log_file_path = os.path.join(backup_directory, )

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

    for bucket in buckets:
        bucket_name = bucket['Name']

        # do the sync
        log.info(f"bucket : {bucket_name}")
        destination = os.path.join(backup_directory, bucket_name)
        os.makedirs(destination, exist_ok=True)
        s3_bucket_path = f"s3://{bucket_name}"
        # we use --delete so we don't confuse the check with old files that are still hanging around (see below for the check)
        sync_command_line = ['aws', 's3', 'sync', s3_bucket_path, destination, '--delete']
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
        if s3_object_count != local_count or s3_total_size != local_size:
            log.warning(f"{bucket_name} not yet fully backed up (s3_count={s3_object_count}, local_count={local_count}; s3_total_size={s3_total_size}, local_size={local_size})")
        else:
            log.info(f"{bucket_name} : s3_count={s3_object_count}, s3_total_size={s3_total_size}")


def main():

    parser = argparse.ArgumentParser(description=__description__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     epilog=f'v{__version__}, www.abel.co, see github.com/jamesabel/backupjca for LICENSE.')
    parser.add_argument('path', help='directory to back up to')
    parser.add_argument('-p', '--profile', help="AWS profile (uses the default AWS profile if not given)")
    parser.add_argument('-d', '--dry_run', action='store_true', default=False,
                        help="Displays the operations that would be performed using the specified command without actually running them")
    args = parser.parse_args()

    balsa = Balsa(__application_name__, __author__)
    balsa.verbose = True
    balsa.log_directory = args.path
    balsa.delete_existing_log_files = True
    balsa.init_logger()

    s3_local_backup(args.path, args.profile, args.dry_run)
