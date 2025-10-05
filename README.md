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
+--------------------+            S3 Event: ObjectCreated
|  S3 (raw uploads)  |  ──────────────────────────────────►  +---------------------+
|  csv-cleaner-raw   |                                       |  AWS Lambda         |
+---------▲----------+                                       |  lambda_function.py |
          |                                                  +-----+-----------+---+
          |                                                        |           |
          |  PutObject (cleaned.csv)                               |           |
          |                                                        |           |
          |                                                        | Publish   |
          |                                   PutObject (bad.csv)  | SNS       |
+---------+----------+                                       +-----v-----------v---+
|  S3 (clean output) |                                       |  Amazon SNS         |
| csv-cleaner-clean  |                                       |  csv-cleaner-events |
+--------------------+                                       +---------+-----------+
                                                                       |
                                                                       | Email
+-------------------------+                                            v
|  S3 (quarantine/bad)   |
| csv-cleaner-quarantine |
+-------------------------+
