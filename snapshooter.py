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
days_to_keep = int(os.environ.get("DAYS_TO_KEEP") or 2)
days_to_analyse = int(os.environ.get("DAYS_TO_ANALYSE") or 30)
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
volume_whitelist = yaml.load(open(config_path, 'r'))["volume_info"]
volume_ids = [volume["id"] for volume in volume_whitelist]

# Get snapshot list
client = boto3.client('ec2', region_name=aws_region)
filter_params = [{'Name': 'volume-id', 'Values': volume_ids}] # Only get whitelisted snapshots
snapshot_list = client.describe_snapshots(OwnerIds=[aws_owner_id], Filters=filter_params)['Snapshots']
snapshot_list.sort(key=lambda x: x["StartTime"], reverse=True) # Sort

# Find snapshot ids applicable for removal
snapshot_ids_to_remove = get_removable_snapshots(snapshot_list, date_threshold, analysis_threshold)

# Remove snapshots
ec2 = boto3.resource('ec2', region_name=os.environ.get("AWS_REGION"))
print("A total of", len(snapshot_ids_to_remove), "snapshots will be deleted! Here is a summary:")
for snapshot_id in snapshot_ids_to_remove:
    snapshot = ec2.Snapshot(snapshot_id)
    print("============================================================")
    print("Snapshot name: " + snapshot.description)
    print("Snapshot Volume size (GB): " + str(snapshot.volume_size))
    print("Snapshot Volume ID: "+ str(snapshot.volume_id))
    print("Snapshot date: " + str(snapshot.start_time.date()))
    if not dryrun:
        response = client.delete_snapshot(SnapshotId=snapshot_id)
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            print("Snapshot with id", snapshot_id, "was not successfully deleted!")
        else:
            print("Snapshot with id", snapshot_id, "was successfully deleted!")
    else:
        print("However, dryrun is enabled, so not performing deletes")

