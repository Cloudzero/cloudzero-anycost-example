#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2016-2024, CloudZero, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
# An example script showcasing the structure of an AnyCost Stream adaptor.
# An adaptor generally performs the following steps:
#   1. Query data from a given cloud provider for a billing month
#   2. Transform that cloud provider data into Common Billing Format (CBF)
#   3. Send that CBF data into the CloudZero platform through an AnyCost Stream connection
#
# When uploading to AnyCost Stream:
# - A billing month (or multiple months) must be specified in ISO 8601 format (e.g., "2024-08")
# - Supports batch processing for multiple months with range or comma-separated formats
# - An operation type can be specified to control how data is handled:
#   - replace_drop: Replace all existing data for the month (default)
#   - replace_hourly: Replace data with overlapping hours
#   - sum: Append data to existing records

import csv
import decimal
import getpass
import json
import sys
import argparse
import re
from datetime import datetime
from typing import List

import requests

# Check for Python version 3.9 or newer
if sys.version_info < (3, 9):
    sys.exit("This script requires Python 3.9 or newer.")

def read_csv(file_path: str) -> list[dict[str, str]]:
    """Read a CSV file and return a list of rows as dictionaries."""
    with open(file_path, "r") as file:
        return list(csv.DictReader(file))


def process_usage_data(file_path: str) -> list[dict[str, str]]:
    """Process usage data and return transformed CBF rows."""
    usage_rows = read_csv(file_path)
    cbf_rows = []
    for usage in usage_rows:
        discounted_cost = str(decimal.Decimal(usage["cost"]) - abs(decimal.Decimal(usage["discount"])))
        cbf_rows.append({
            "lineitem/type": "Usage",
            "resource/service": usage["sku"],
            "resource/id": f"instance-{usage['instance_id']}",
            "time/usage_start": usage["usage_date"],
            "cost/cost": usage["cost"],
            "cost/discounted_cost": discounted_cost,
        })
    return cbf_rows


def process_purchase_commitments(file_path: str) -> list[dict[str, str]]:
    """Process purchase commitments data and return transformed CBF rows."""
    purchase_commitment_rows = read_csv(file_path)
    cbf_rows = []
    for purchase_commitment in purchase_commitment_rows:
        cbf_rows.append({
            "lineitem/type": "CommittedUsePurchase",
            "resource/service": "CommittedUse",
            "resource/id": f"commit-{purchase_commitment['commitment_id']}",
            "time/usage_start": purchase_commitment["commitment_date"],
            "cost/cost": purchase_commitment["cost"],
            "cost/discounted_cost": purchase_commitment["cost"],
        })
    return cbf_rows


def process_discounts(file_path: str) -> list[dict[str, str]]:
    """Process discounts data and return transformed CBF rows."""
    discount_rows = read_csv(file_path)
    cbf_rows = []
    for discount in discount_rows:
        cbf_rows.append({
            "lineitem/type": "Discount",
            "resource/service": discount["discount_type"],
            "resource/id": f"discount-{discount['discount_id']}",
            "time/usage_start": discount["usage_date"],
            "cost/cost": discount["discount"],
            "cost/discounted_cost": discount["discount"],
        })
    return cbf_rows


def write_cbf_rows_to_csv(cbf_rows: list[dict[str, str]], output_file_path: str):
    """Write CBF rows to a CSV file."""
    with open(output_file_path, "w") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "lineitem/type",
                "resource/service",
                "resource/id",
                "time/usage_start",
                "cost/cost",
                "cost/discounted_cost",
            ],
        )
        writer.writeheader()
        writer.writerows(cbf_rows)


def parse_month_range(month_input: str) -> List[str]:
    """Parse month input and return list of months.
    
    Supports:
    - Single month: "2024-08"
    - Month range: "2024-08:2024-10" (inclusive)
    - Comma-separated: "2024-08,2024-09,2024-11"
    """
    if not month_input or not month_input.strip():
        raise ValueError("Month input cannot be empty")
    
    month_pattern = re.compile(r'^\d{4}-\d{2}$')
    
    if ':' in month_input:
        # Handle range format: "2024-08:2024-10"
        parts = month_input.split(':')
        if len(parts) != 2:
            raise ValueError("Month range must have exactly one ':' separator")
        
        start_str, end_str = parts
        start_str, end_str = start_str.strip(), end_str.strip()
        
        if not month_pattern.match(start_str) or not month_pattern.match(end_str):
            raise ValueError("Month format must be YYYY-MM (e.g., '2024-08')")
        
        try:
            start_date = datetime.strptime(start_str + "-01", "%Y-%m-%d")
            end_date = datetime.strptime(end_str + "-01", "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid date format: {e}")
        
        if start_date > end_date:
            raise ValueError("Start month cannot be after end month")
        
        months = []
        current = start_date
        while current <= end_date:
            months.append(current.strftime("%Y-%m"))
            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        return months
    elif ',' in month_input:
        # Handle comma-separated format: "2024-08,2024-09,2024-11"
        months = [month.strip() for month in month_input.split(',')]
        for month in months:
            if not month_pattern.match(month):
                raise ValueError(f"Invalid month format '{month}'. Must be YYYY-MM (e.g., '2024-08')")
        return months
    else:
        # Single month
        month = month_input.strip()
        if not month_pattern.match(month):
            raise ValueError(f"Invalid month format '{month}'. Must be YYYY-MM (e.g., '2024-08')")
        return [month]


def upload_to_anycost(cbf_rows: list[dict[str, str]]):
    """Upload CBF rows to an AnyCost Stream connection.
    
    Supports both single month and batch processing for multiple months.
    
    Required parameters:
    - month(s): Single month, range, or comma-separated list in ISO 8601 format
      - Single: "2024-08"
      - Range: "2024-08:2024-10" (uploads to Aug, Sep, Oct)
      - List: "2024-08,2024-09,2024-11"
    - data: List of CBF rows to upload
    
    Optional parameters:
    - operation: How to handle existing data for each month
      - "replace_drop" (default): Replace all existing data for the month
      - "replace_hourly": Replace data with overlapping hours
      - "sum": Append data to existing records
    """
    anycost_stream_connection_id = input("Enter your AnyCost Stream Connection ID: ")
    cloudzero_api_key = getpass.getpass("Enter your CloudZero API Key: ")
    
    # Ask user for processing mode
    print("\nProcessing mode:")
    print("1. Single month")
    print("2. Batch processing (multiple months)")
    mode_choice = input("Choose processing mode (1-2, default: 1): ").strip()
    
    if mode_choice == "2":
        print("\nBatch processing options:")
        print("- Single month: 2024-08")
        print("- Month range: 2024-08:2024-10 (inclusive)")
        print("- Comma-separated: 2024-08,2024-09,2024-11")
        month_input = input("Enter month(s): ")
        months = parse_month_range(month_input)
        print(f"\nWill process {len(months)} months: {', '.join(months)}")
    else:
        # Single month mode
        month_input = input("Enter the billing month (YYYY-MM format, e.g., 2024-08): ")
        months = [month_input]
    
    # Get the operation type from user
    print("\nOperation types:")
    print("1. replace_drop (default) - Replace all existing data for the month")
    print("2. replace_hourly - Replace data with overlapping hours")
    print("3. sum - Append data to existing records")
    operation_choice = input("Enter operation type (1-3, default: 1): ").strip()
    
    operation_map = {
        "1": "replace_drop",
        "2": "replace_hourly", 
        "3": "sum",
        "": "replace_drop"  # default
    }
    operation = operation_map.get(operation_choice, "replace_drop")
    
    # Validate months before processing
    try:
        for month in months:
            parse_month_range(month)  # Validate each month format
    except ValueError as e:
        print(f"✗ Invalid month format: {e}")
        return
    
    # Process each month
    successful_uploads = 0
    failed_uploads = 0
    
    for i, month in enumerate(months, 1):
        print(f"\n[{i}/{len(months)}] Uploading data for {month}...")
        
        try:
            response = requests.post(
                f"https://api.cloudzero.com/v2/connections/billing/anycost/{anycost_stream_connection_id}/billing_drops",
                headers={"Authorization": cloudzero_api_key},
                json={
                    "month": month,
                    "operation": operation,
                    "data": cbf_rows
                },
                timeout=30
            )
            
            response.raise_for_status()  # Raises HTTPError for bad HTTP status codes
            
            response_json = response.json()
            print(f"Response for {month}:")
            print(json.dumps(response_json, indent=2))
            
            if response.status_code == 200:
                successful_uploads += 1
                print(f"✓ Successfully uploaded data for {month}")
            else:
                failed_uploads += 1
                print(f"✗ Failed to upload data for {month} (HTTP {response.status_code})")
                
        except requests.exceptions.Timeout:
            failed_uploads += 1
            print(f"✗ Timeout error uploading data for {month}: Request timed out after 30 seconds")
        except requests.exceptions.ConnectionError:
            failed_uploads += 1
            print(f"✗ Connection error uploading data for {month}: Unable to connect to CloudZero API")
        except requests.exceptions.HTTPError as e:
            failed_uploads += 1
            print(f"✗ HTTP error uploading data for {month}: {e}")
            try:
                error_detail = response.json()
                print(f"Error details: {json.dumps(error_detail, indent=2)}")
            except (ValueError, AttributeError):
                pass
        except requests.exceptions.RequestException as e:
            failed_uploads += 1
            print(f"✗ Network error uploading data for {month}: {e}")
        except Exception as e:
            failed_uploads += 1
            print(f"✗ Unexpected error uploading data for {month}: {str(e)}")
    
    # Summary
    if len(months) > 1:
        print(f"\n=== Batch Upload Summary ===")
        print(f"Total months processed: {len(months)}")
        print(f"Successful uploads: {successful_uploads}")
        print(f"Failed uploads: {failed_uploads}")
        if failed_uploads > 0:
            print("⚠️  Some uploads failed. Check the error messages above.")
        else:
            print("✅ All uploads completed successfully!")


def main():
    parser = argparse.ArgumentParser(description="Process and upload cloud billing data.")
    parser.add_argument("--usage", required=True, help="Path to the usage data CSV file.")
    parser.add_argument("--commitments", help="Path to the purchase commitments CSV file.")
    parser.add_argument("--discounts", help="Path to the discounts CSV file.")
    parser.add_argument("--output", default="cbf_output.csv", help="Path to the output CBF CSV file. (default: cbf_output.csv)")
    args = parser.parse_args()

    cbf_rows = []
    cbf_rows.extend(process_usage_data(args.usage))
    
    if args.commitments:
        cbf_rows.extend(process_purchase_commitments(args.commitments))
    
    if args.discounts:
        cbf_rows.extend(process_discounts(args.discounts))

    write_cbf_rows_to_csv(cbf_rows, args.output)

    should_continue = input("Would you like to upload the example CBF to an AnyCost Stream connection? (y/n) ")
    if should_continue.lower() == "y":
        upload_to_anycost(cbf_rows)
    else:
        sys.exit()


if __name__ == "__main__":
    main()
