import os
import pickle
import logging

from sundry import aws_dynamodb_scan_table, aws_get_dynamodb_table_names

from backupjca import __application_name__

log = logging.getLogger(__application_name__)


def dynamodb_local_backup(backup_directory: str, aws_profile: (str, None), dry_run: bool, excludes: (list, None)):

    tables = aws_get_dynamodb_table_names(aws_profile)
    print(f"backing up {len(tables)} DynamoDB tables")
    if dry_run:
        print("*** DRY RUN ***")
    for table_name in tables:
        print(table_name)
        if excludes is not None and table_name in excludes:
            print(f"excluding {table_name}")
        else:
            if not dry_run:
                table_contents = aws_dynamodb_scan_table(table_name, aws_profile)
                dir_path = os.path.join(backup_directory, "dynamodb")
                os.makedirs(dir_path, exist_ok=True)
                with open(os.path.join(dir_path, f"{table_name}.pickle"), "wb") as f:
                    pickle.dump(table_contents, f)
