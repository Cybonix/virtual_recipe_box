# Virtual Recipe Box

This is a Python-based menu-driven application to manage recipes using AWS DynamoDB and S3.  DynamoDB stores recipe metadata (e.g., ingredients, instructions, tags, etc..).
S3 stores uploaded PDF recipe files, images, and application generated PDFs for export.

## Features
- Add recipes manually or upload recipe PDFs.
- Search, edit, and delete recipes.
- Export recipes to S3 in PDF format.

## Prerequisites
1. Python 3.8 or higher
2. AWS CLI installed and configured
3. Access to an AWS account

## Setup Instructions
```bash
pip install -r requirements.txt
