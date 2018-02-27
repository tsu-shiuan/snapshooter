import os
import argparse
import boto3
from helper_methods import get_date_threshold, validate_aws_variables, get_removable_snapshots
import yaml

# Validate AWS variables
aws_region, aws_owner_id = validate_aws_variables()


# Due to possible irregularities, we specify a analysis threshold,
# which asssumes snapshots are cleaned up to X days ago

# Define some variable defaults
days_to_keep = os.environ.get("DAYS_TO_KEEP") or 2
days_to_analyse = os.environ.get("DAYS_TO_ANALYSE") or 30
date_threshold = get_date_threshold(days_to_keep)
analysis_threshold = get_date_threshold(days_to_analyse)
dryrun = False

# Parse some args
parser = argparse.ArgumentParser()
parser.add_argument('--dry_run', default="false")
parser.add_argument('--config_file_location')
args = parser.parse_args()

if args.dry_run == "true":
    dryrun = True
elif args.dry_run == "false":
    dryrun = False

# Load config for volume information
default_config_path = os.getcwd() + "/config.yml"
config_path = args.config_file_location or default_config_path
snapshot_dict = yaml.load(open(config_path, 'r'))["volume_info"]

# Get snapshot list
client = boto3.client('ec2', region_name=aws_region)
snapshot_info = client.describe_snapshots(OwnerIds=[aws_owner_id])
snapshot_list = snapshot_info['Snapshots']

# Find snapshot ids applicable for removal
snapshot_ids_to_remove = get_removable_snapshots(snapshot_info, date_threshold, analysis_threshold, snapshot_dict)

# Remove snapshots
ec2 = boto3.resource('ec2', region_name=os.environ.get("AWS_REGION"))
print("A total of", len(snapshot_ids_to_remove), "snapshots will be deleted! Here is a summary:")
for snapshot_id in snapshot_ids_to_remove:
    snapshot = ec2.Snapshot(snapshot_id)
    print("=========")
    print("Snapshot name: " + snapshot.description)
    print("Snapshot Volume size (GB): " + str(snapshot.volume_size))
    print("Snapshot Volume ID: "+ str(snapshot.volume_id))
    print("Snapshot date: " + str(snapshot.start_time.date()))

if not dryrun:
    for snapshot_id in snapshot_ids_to_remove:
        response = client.delete_snapshot(SnapshotId=snapshot_id)
        if not response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print("Snapshot with id", snapshot_id, "was not successfully deleted!")
