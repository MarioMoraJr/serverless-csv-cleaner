# Serverless CSV Cleaner 🔧

**Live Demo:** [Add later when your CloudFront link is ready]  
**Tech Stack:** AWS Lambda (Python 3.12) | S3 Triggers | SNS | CloudWatch  

## Overview
When a CSV file is uploaded to the `raw` S3 bucket, this Lambda function:
- Validates and cleans the data  
- Removes duplicates  
- Sends clean rows to `clean` bucket and bad rows to `quarantine` bucket  
- Publishes an SNS notification  

## Architecture
flowchart LR
    A[User uploads CSV<br/>S3: csv-cleaner-raw] -->|ObjectCreated| B[Lambda: lambda_function.py]
    B -->|PutObject clean.csv| C[S3: csv-cleaner-clean]
    B -->|PutObject quarantine.csv| D[S3: csv-cleaner-quarantine]
    B -->|Publish| E[SNS: csv-cleaner-events]
    E --> F[(Email)]

