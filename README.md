# AnyCost Stream Example

[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE-OF-CONDUCT.md)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
![GitHub release](https://img.shields.io/github/release/cloudzero/template-cloudzero-open-source.svg)

This repository contains a Python script that serves as an example of an Adaptor for an [AnyCost Stream](https://docs.cloudzero.com/docs/anycost-stream-getting-started) connection. The script transforms cost data into the [Common Bill Format (CBF)](https://docs.cloudzero.com/docs/anycost-common-bill-format-cbf) and sends the CBF data to the [CloudZero REST API](https://docs.cloudzero.com/reference/createoneanycoststreamconnectionbillingdrop).

You can use this Adaptor as a model for structuring your own AnyCost Stream Adaptor, modifying it to fit your use case.


## Table of Contents

- [Documentation](#documentation)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Running the Script](#running-the-script)
- [Usage Examples](#usage-examples)
- [Contributing](#contributing)
- [Support + Feedback](#support--feedback)
- [Vulnerability Reporting](#vulnerability-reporting)
- [What is CloudZero?](#what-is-cloudzero)
- [License](#license)

## Documentation

- [Getting Started with AnyCost Stream](https://docs.cloudzero.com/docs/anycost-stream-getting-started)
- [Creating AnyCost Custom Adaptors](https://docs.cloudzero.com/docs/anycost-custom-adaptors)
- [Sending AnyCost Stream Data to CloudZero](https://docs.cloudzero.com/docs/anycost-send-stream-data)
- [CloudZero Common Bill Format](https://docs.cloudzero.com/docs/anycost-common-bill-format-cbf)
- [CloudZero API Authorization](https://docs.cloudzero.com/reference/authorization)
- [AnyCost Stream API](https://docs.cloudzero.com/reference/createoneanycoststreamconnectionbillingdrop)

## Installation

### Prerequisites

- Python 3.9 or newer

### Install Dependency

Consider using the [venv](https://docs.python.org/3/library/venv.html) system module to create a virtual environment:

```bash
python3 -m venv venv
```

Activate the virtual environment, if you chose to create it:

```bash
source venv/bin/activate
```

Install the required dependency, which is the Python [requests](https://requests.readthedocs.io/en/latest/) module:

```bash
pip install requests
```

## Getting Started

An [AnyCost Stream connection](https://docs.cloudzero.com/docs/anycost-stream-getting-started) automates the flow of cost data into CloudZero by allowing you to send data from _any_ cost source to the CloudZero REST API.

An [AnyCost Stream Adaptor](https://docs.cloudzero.com/docs/anycost-custom-adaptors) is the code that queries data from the provider, transforms it to fit the required format, and sends the transformed data to CloudZero.

### Quick Start for New Users

1. **Prerequisites**: Ensure you have Python 3.9+ installed and access to your cost data in CSV format
2. **Setup**: Clone this repository and install dependencies ([Installation](#installation))
3. **Prepare Data**: Format your CSV files or use the provided examples
4. **Run Script**: Execute with your data files and follow the interactive prompts
5. **Upload**: Choose single month or batch processing to upload to CloudZero

### Three Core Steps

An AnyCost Stream Adaptor typically performs three actions:

1. [Retrieve data from a cloud provider for a billing month.](#step-1-retrieve-cost-data-from-cloud-provider)
2. [Transform the data into the Common Bill Format (CBF).](#step-2-transform-cost-data-to-cbf)
3. [Send the CBF data to the CloudZero API.](#step-3-send-the-cbf-data-to-cloudzero)

You can write an Adaptor in any language, but this example uses Python and can be easily customized for different cloud providers.

### Step 1: Retrieve Cost Data From Cloud Provider

Your Adaptor should start by retrieving cost data from your cloud provider. This step varies by provider:

**Common Data Sources:**
- **AWS**: Cost and Usage Reports (CUR), billing CSV exports
- **Azure**: Cost Management exports, billing data APIs
- **GCP**: Billing export to BigQuery, Cloud Billing API
- **Other Clouds**: Billing APIs, cost management dashboards, CSV exports

**For This Example:**
Because every provider makes cost data available differently, this example uses three sample CSV files:

- `cloud_usage.csv`: Resource usage and compute costs
- `cloud_purchase_commitments.csv`: Reserved instances, savings plans
- `cloud_discounts.csv`: Volume discounts, credits, promotions

**Customizing for Your Provider:**
To adapt this script for your cloud provider:
1. Replace the CSV reading logic with API calls to your provider
2. Modify the data processing functions to match your provider's data structure
3. Update the column mappings in the transformation functions

See [Customization Guide](#customizing-for-different-cloud-providers) below for detailed instructions.

### Step 2: Transform Cost Data to CBF

The next step is for the Adaptor to remap the existing cost data to the [Common Bill Format (CBF)](https://docs.cloudzero.com/docs/anycost-common-bill-format-cbf). Conforming to a standard format allows CloudZero to process cost data from any source.

This example Adaptor takes the following actions:

- Reads the data from each of the three sample CSV files.
- Maps each CSV's data to the appropriate CBF data type.
- Combines the CBF data into a single CSV.

### Step 3: Send the CBF Data to CloudZero

The final step is for the Adaptor to send the CBF data to the AnyCost Stream connection using CloudZero's [/v2/connections/billing/anycost/{connection_id}/billing_drops](https://docs.cloudzero.com/reference/createoneanycoststreamconnectionbillingdrop) API.

## Running the Script

The Python script processes cloud billing data and uploads it to an AnyCost Stream connection. You can specify input and output file paths as command-line arguments. Below are the steps and usage instructions:

### Prerequisites

- Ensure you have Python 3.9 or newer installed.
- Prepare your CSV files for usage data, purchase commitments, and discounts.
- Create an [AnyCost Stream connection](https://docs.cloudzero.com/docs/anycost-stream-getting-started#step-1-register-the-connection-in-the-ui).
- Have your [CloudZero API key](https://app.cloudzero.com/organization/api-keys) ready for uploading data.

### Usage

Run the script from the command line with the following syntax:

```bash
python anycost_example.py --usage <path_to_usage_csv> --commitments <path_to_commitments_csv> --discounts <path_to_discounts_csv> --output <path_to_output_csv>
```

### Arguments

- `--usage`: Path to the CSV file containing usage data. This file should include columns like `cost`, `discount`, `sku`, `instance_id`, and `usage_date`.
- `--commitments` (Optional): Path to the CSV file containing purchase commitments data. This file should include columns like `commitment_id`, `commitment_date`, and `cost`.
- `--discounts` (Optional): Path to the CSV file containing discounts data. This file should include columns like `discount_type`, `discount_id`, `usage_date`, and `discount`.
- `--output` (Optional): Path to the output CSV file where transformed CBF data will be saved. Defaults to `cbf_output.csv`

### Example

The minimum parameter set is `--usage`. With only `--usage` specified, the script will process the usage data, skip discounts and purchase commitments, and save the CBF to an output file called `cbf_output.csv` in the current working directory.
```bash
python anycost_example.py --usage example_cloud_provider_data/cloud_usage.csv
```

With `--commitments`, `--discounts`, and `--output` specified, the script will process all three data types and save the output to the file specified in `--output`.
```bash
python anycost_example.py --usage example_cloud_provider_data/cloud_usage.csv --commitments example_cloud_provider_data/cloud_purchase_commitments.csv --discounts example_cloud_provider_data/cloud_discounts.csv --output cbf/cloud_cbf.csv
```

### Uploading Data

After processing the data, the script will prompt you to upload the CBF data to an AnyCost Stream connection:

1. Enter `y` if you want to upload the data.
2. Provide your AnyCost Stream Connection ID.
3. Enter your CloudZero API key when prompted.
4. Choose processing mode:
   - **Single month**: Upload data for one billing month
   - **Batch processing**: Upload data for multiple months
5. Specify the billing month(s):
   - **Single month**: `2024-08`
   - **Month range**: `2024-08:2024-10` (uploads to Aug, Sep, Oct)
   - **Comma-separated**: `2024-08,2024-09,2024-11`
6. Choose an operation type:
   - **replace_drop** (default): Replace all existing data for the month
   - **replace_hourly**: Replace data with overlapping hours  
   - **sum**: Append data to existing records

#### Batch Processing Benefits

- **Time-saving**: Upload historical data for multiple months in one session
- **Progress tracking**: See upload progress and success/failure status for each month
- **Error resilience**: Failed uploads for individual months won't stop the entire process
- **Flexible input**: Support for ranges, lists, or individual months
- **Input validation**: Comprehensive error checking with helpful suggestions
- **Retry logic**: Multiple attempts for invalid input with clear error messages

#### Error Handling

The script provides comprehensive error handling and validation:

**Month Format Validation**:
- Validates YYYY-MM format (e.g., "2024-08")
- Checks for valid date ranges in batch mode
- Provides specific error messages for invalid formats

**File Processing Errors**:
- Clear messages for missing or inaccessible CSV files
- Validation of required CSV columns
- Row-by-row error reporting with line numbers

**Network and API Errors**:
- Timeout handling (30-second limit per request)
- Connection error detection
- HTTP status code reporting with error details
- JSON parsing error handling

### Viewing Results

Once uploaded, you can view the processed data within the CloudZero platform. Navigate to [Settings](https://app.cloudzero.com/organization/connections) and select your connection from the **Billing Connections** table. The **Status** of your connection will update once CloudZero processes the data.

## Usage Examples

To use the `anycost_example.py` script to transform the cost data to CBF, run the command as described in the [Running the Script](#running-the-script) section.

## Testing

This repository includes a comprehensive test suite to ensure code quality and reliability.

### Running Tests

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install test dependencies:
   ```bash
   pip install -r tests/requirements-dev.txt
   ```

3. Run the test suite:
   ```bash
   python -m pytest tests/ -v
   ```

### Test Coverage

The test suite includes 11 test cases covering:
- CSV reading and processing functions
- Data transformation for usage, commitments, and discounts
- CBF output generation
- AnyCost Stream API upload functionality with mocked requests
- All operation types (replace_drop, replace_hourly, sum)

All tests use proper mocking to isolate functionality and avoid external dependencies.

## Customizing for Different Cloud Providers

This script can be easily adapted for different cloud providers by modifying the data processing functions:

### Step-by-Step Customization

1. **Identify Your Data Source**
   ```python
   # Replace CSV reading with API calls
   def get_provider_data(start_date, end_date):
       # Example: Call your provider's billing API
       # response = provider_client.get_billing_data(start=start_date, end=end_date)
       # return response.data
   ```

2. **Update Data Processing Functions**
   ```python
   def process_usage_data(raw_data):
       # Map your provider's fields to CBF format
       cbf_rows = []
       for item in raw_data:
           cbf_rows.append({
               "lineitem/type": "Usage",
               "resource/service": item["service_name"],        # Your field
               "resource/id": item["resource_identifier"],      # Your field  
               "time/usage_start": item["billing_period"],      # Your field
               "cost/cost": str(item["total_cost"]),           # Your field
               "cost/discounted_cost": str(item["net_cost"]),  # Your field
           })
       return cbf_rows
   ```

3. **Common Provider Mappings**

   **AWS CUR Fields:**
   - `lineItem/LineItemType` → `lineitem/type`
   - `product/ProductName` → `resource/service`
   - `lineItem/ResourceId` → `resource/id`
   - `lineItem/UsageStartDate` → `time/usage_start`
   - `lineItem/UnblendedCost` → `cost/cost`

   **Azure Billing Fields:**
   - `MeterCategory` → `resource/service`
   - `InstanceId` → `resource/id`
   - `UsageDateTime` → `time/usage_start`
   - `ExtendedCost` → `cost/cost`

   **GCP Billing Fields:**
   - `service.description` → `resource/service`
   - `resource.name` → `resource/id`
   - `usage_start_time` → `time/usage_start`
   - `cost` → `cost/cost`

4. **Test Your Changes**
   ```bash
   python -m pytest tests/ -v
   ```

### Common Troubleshooting

**Issue: "Missing required columns in CSV"**
- Solution: Update the `required_columns` list in processing functions to match your data

**Issue: "Invalid cost/discount value"**  
- Solution: Check your provider's number format (currency symbols, decimals)

**Issue: "Invalid month format"**
- Solution: Ensure dates are in YYYY-MM format, convert if needed

**Issue: "Connection timeout"**
- Solution: Increase timeout in upload function or implement retry logic

## Contributing

We appreciate feedback and contributions to this repo! Before you get started, see [this repo's contribution guide](CONTRIBUTING.md).

## Support + Feedback

To submit code-level feedback, create a GitHub Issue. Direct all other questions to support@cloudzero.com.

## Vulnerability Reporting

Do not report security vulnerabilities on the public GitHub issue tracker. Email [security@cloudzero.com](mailto:security@cloudzero.com) instead.

## What is CloudZero?

CloudZero is the only cloud cost intelligence platform that puts engineering in control by connecting technical decisions to business results:

- [Cost Allocation And Tagging](https://www.cloudzero.com/tour/allocation): Organize and allocate cloud spend in new ways, increase tagging coverage, or work on showback.
- [Kubernetes Cost Visibility](https://www.cloudzero.com/tour/kubernetes): Understand your Kubernetes spend alongside total spend across containerized and non-containerized environments.
- [FinOps And Financial Reporting](https://www.cloudzero.com/tour/finops): Operationalize reporting on metrics such as cost per customer, COGS, gross margin. Forecast spend, reconcile invoices, and easily investigate variance.
- [Engineering Accountability](https://www.cloudzero.com/tour/engineering): Foster a cost-conscious culture, where engineers understand spend, proactively consider cost, and get immediate feedback with fewer interruptions and faster and more efficient innovation.
- [Optimization And Reducing Waste](https://www.cloudzero.com/tour/optimization): Focus on immediately reducing spend by understanding where we have waste, inefficiencies, and discounting opportunities.

Learn more about [CloudZero](https://www.cloudzero.com/) on our website [www.cloudzero.com](https://www.cloudzero.com/).

## License

This project is licensed under the Apache 2.0 [LICENSE](LICENSE).