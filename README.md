# Virtual Recipe Box

The Virtual Recipe Box is a Python application designed to help users manage their favorite recipes with ease, leveraging the power of SQLite for the database and local file system for storage. The application provides a seamless way to organize, search, edit, delete, and export recipes, whether they are entered manually or uploaded as PDFs.

This is a Python-based menu-driven application to manage recipes using SQLite for the database and local file system for storage. SQLite stores recipe metadata (e.g., ingredients, instructions, tags, etc.). Local file system stores uploaded PDF recipe files, images, and application-generated PDFs for export.

## Features
- Add recipes manually or upload recipe PDFs.
- Search, edit, and delete recipes.
- Export recipes to a nicely formatted PDF file.

## Prerequisites
1. Python 3.8 or higher
2. SQLite installed

## Setup Instructions
```bash
pip install -r requirements.txt
```

## Changes Made
- Switched from AWS DynamoDB and S3 to SQLite for the database and local file system for storage.
- Removed the AWS CLI installation and configuration from the Dockerfile and setup_resources.py.
- Removed the setup_resources.py file as it is no longer needed.
- Added the `export_recipe_to_pdf` function to export recipes to a nicely formatted PDF file.
- Updated the Dockerfile to reflect the changes made to the application.
