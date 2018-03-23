import datetime
import os


def get_date_threshold(days):
    return datetime.date.today() - datetime.timedelta(days=days)


def validate_aws_variables():
    aws_region = os.environ.get("AWS_REGION")
    aws_owner_id = os.environ.get("AWS_OWNER_ID")
    if not aws_region:
        raise RuntimeError("No AWS_REGION supplied")
    if not aws_owner_id:
        raise RuntimeError("No AWS_OWNER_ID supplied")

    return [aws_region, aws_owner_id]


def get_removable_snapshots(snapshot_list, date_threshold, analysis_threshold):
    snapshot_ids_to_remove = []
    for snapshot in snapshot_list:
        snapshot_date = snapshot["StartTime"].date()
        # A snapshot is applicable for removal if it:
        # 1) Falls within the days_to_analysis threshold
        # 2) Falls out of the days_to_keep threshold
        # 3) If it is not the first day of the month (by default we keep 1 snapshot per month)
        # 4) If it exists in the whitelist given in the config.yml
        if snapshot_date > analysis_threshold and \
           snapshot_date <= date_threshold and \
           snapshot_date.day != 1:
              snapshot_ids_to_remove.append(snapshot["SnapshotId"])

    return snapshot_ids_to_remove
