
import argparse
import boto3
import subprocess

from s3_local_backup import __version__, __description__


def s3_local_backup(destination_directory: str, aws_profile: str, dry_run: bool):

    if aws_profile is not None:
        session = boto3.Session(profile_name=aws_profile)
        s3_client = session.client('s3')
    else:
        s3_client = boto3.client('s3')

    buckets = s3_client.list_buckets()['Buckets']
    print(f"found {len(buckets)} buckets")
    for bucket in buckets:
        command_line = ['aws', 's3', 'sync', f"s3://{bucket['Name']}", destination_directory]
        if dry_run:
            command_line.append('--dryrun')
        print(command_line)
        subprocess.run(command_line)


def main():

    parser = argparse.ArgumentParser(description=__description__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     epilog=f'v{__version__}, www.abel.co, see github.com/jamesabel/backupjca for LICENSE.')
    parser.add_argument('path', help='directory to back up to')
    parser.add_argument('-p', '--profile', help="AWS profile (uses the default AWS profile if not given)")
    parser.add_argument('-d', '--dry_run', action='store_true', default=False,
                        help="Displays the operations that would be performed using the specified command without actually running them")
    args = parser.parse_args()

    s3_local_backup(args.path, args.profile, args.dry_run)
