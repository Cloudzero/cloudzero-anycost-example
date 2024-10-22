# AnyCost Stream Example

[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE-OF-CONDUCT.md)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
![GitHub release](https://img.shields.io/github/release/cloudzero/template-cloudzero-open-source.svg)

This repository contains a Python script that serves as an example of an Adaptor for an [AnyCost Stream](https://docs.cloudzero.com/docs/anycost-stream-getting-started) connection. The script transforms cost data into the [Common Bill Format (CBF)](https://docs.cloudzero.com/docs/anycost-common-bill-format-cbf) and sends the CBF data to the [CloudZero REST API](https://docs.cloudzero.com/reference/createoneanycoststreamconnectionbillingdrop).

You can use this Adaptor as a model for structuring your own AnyCost Stream Adaptor, modifying it to fit your use case.

**Note:** The AnyCost Stream feature is in beta. Contact your CloudZero representative to request access.

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

An AnyCost Stream Adaptor typically performs three actions:

1. [Retrieve data from a cloud provider for a billing month.](#step-1-retrieve-cost-data-from-cloud-provider)
2. [Transform the data into the Common Bill Format (CBF).](#step-2-transform-cost-data-to-cbf)
3. [Send the CBF data to the CloudZero API.](#step-3-send-the-cbf-data-to-cloudzero)

You can write an Adaptor in any language, but this example uses Python.

### Step 1: Retrieve Cost Data From Cloud Provider

Your Adaptor should start by retrieving cost data from your cloud provider. Follow your provider's instructions to retrieve the data you need. For example, this could involve sending requests to the provider's APIs to retrieve billing records for one or more accounts, or downloading a CSV of all cost data from the provider.

Because every provider makes its cost data available in a different way, the example Adaptor skips this step. Instead, we've provided you with three CSVs representing the data your Adaptor could retrieve from this step:

- `cloud_usage.csv`: Data related to cloud resource usage
- `cloud_purchase_commitments.csv`: Data for discounts related to committed-use contracts
- `cloud_discounts.csv`: Data for other discounts received

The dummy data is taken from the [CBF example](https://docs.cloudzero.com/docs/anycost-common-bill-format-cbf#examples) in the CloudZero documentation.

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
- `--commitments`: Path to the CSV file containing purchase commitments data. This file should include columns like `commitment_id`, `commitment_date`, and `cost`.
- `--discounts`: Path to the CSV file containing discounts data. This file should include columns like `discount_type`, `discount_id`, `usage_date`, and `discount`.
- `--output`: Path to the output CSV file where transformed CBF data will be saved.

### Example

```bash
python anycost_example.py --usage example_cloud_provider_data/cloud_usage.csv --commitments example_cloud_provider_data/cloud_purchase_commitments.csv --discounts example_cloud_provider_data/cloud_discounts.csv --output cbf/cloud_cbf.csv
```

### Uploading Data

After processing the data, the script will prompt you to upload the CBF data to an AnyCost Stream connection:

1. Enter `y` if you want to upload the data.
2. Provide your AnyCost Stream Connection ID.
3. Enter your CloudZero API key when prompted.

### Viewing Results

Once uploaded, you can view the processed data within the CloudZero platform. Navigate to [Settings](https://app.cloudzero.com/organization/connections) and select your connection from the **Billing Connections** table. The **Status** of your connection will update once CloudZero processes the data.

## Usage Examples

To use the `anycost_example.py` script to transform the cost data to CBF, run the command as described in the [Running the Script](#running-the-script) section.

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