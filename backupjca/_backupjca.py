
import argparse

from balsa import Balsa

from backupjca import __application_name__, __author__, __version__, __description__, s3_local_backup


def main():

    parser = argparse.ArgumentParser(description=__description__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     epilog=f'v{__version__}, www.abel.co, see github.com/jamesabel/backupjca for LICENSE.')
    parser.add_argument('path', help='directory to back up to')
    parser.add_argument('-e', '--exclude', nargs='*', help="exclude these AWS S3 buckets")
    parser.add_argument('-p', '--profile', help="AWS profile (uses the default AWS profile if not given)")
    parser.add_argument('-d', '--dry_run', action='store_true', default=False,
                        help="Displays operations that would be performed using the specified command without actually running them")
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help="set verbose")
    args = parser.parse_args()

    balsa = Balsa(__application_name__, __author__)
    balsa.verbose = args.verbose
    balsa.log_directory = args.path
    balsa.delete_existing_log_files = True
    balsa.init_logger()

    s3_local_backup(args.path, args.profile, args.dry_run, args.exclude)
