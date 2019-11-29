import os
import pickle
import logging

from botocore.exceptions import NoRegionError

from sundry import aws_scan_table, aws_get_client

from backupjca import __application_name__

log = logging.getLogger(__application_name__)


def dynamodb_local_backup(backup_directory: str, aws_profile: (str, None), dry_run: bool, excludes: (list, None)):

    try:
        dynamodb_client = aws_get_client("dynamodb", aws_profile)
    except NoRegionError as e:
        log.error(e)
        log.error("make sure your config follows the form in https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html")
        return

    tables = []
    all_tables_found = False
    response = dynamodb_client.list_tables()
    while not all_tables_found:
        tables_response = response["TableNames"]
        if tables_response is not None:
            tables.extend(tables_response)
        last_evaluated_table_name = response.get("LastEvaluatedTableName")
        if last_evaluated_table_name is None or len(last_evaluated_table_name) == 0:
            all_tables_found = True
        else:
            response = dynamodb_client.list_tables()
    tables.sort()

    print(f"backing up {len(tables)} DynamoDB tables")
    if dry_run:
        print("*** DRY RUN ***")
    for table_name in tables:
        print(table_name)
        if excludes is not None and table_name in excludes:
            print(f"excluding {table_name}")
        else:
            if not dry_run:
                table_contents = aws_scan_table(table_name, aws_profile)
                dir_path= os.path.join(backup_directory, "dynamodb")
                os.makedirs(dir_path, exist_ok=True)
                with open(os.path.join(dir_path, f"{table_name}.pickle"), "wb") as f:
                    pickle.dump(table_contents, f)
