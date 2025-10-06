# 🧾 Serverless CSV Cleaner

![Python](https://img.shields.io/badge/Python-3.12-blue)
![AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20S3%20%7C%20SNS-orange)
![License: MIT](https://img.shields.io/badge/License-MIT-green)

### **Live Demo:** Coming soon  
### **Source:** [This GitHub Repository](https://github.com/YOUR-USERNAME/serverless-csv-cleaner)

---

## 🚀 Overview
**Serverless CSV Cleaner** is an event-driven AWS pipeline that automatically validates, cleans, and de-duplicates CSV files.  
When a new file is uploaded to an S3 bucket, it triggers a Lambda function that:
- Removes duplicates  
- Validates required fields  
- Quarantines invalid rows  
- Writes the clean and bad files to separate S3 buckets  
- Sends an SNS notification summarizing the results  

Built with **Python 3.12**, **AWS Lambda**, **S3 Events**, **SNS**, and **CloudWatch Logs** — all following best practices for security and observability.

---

## 🧱 Architecture

```mermaid
flowchart LR
  A[S3 Bucket: raw] -- ObjectCreated event --> B[Lambda: CSV Cleaner]
  B --> C[S3 Bucket: clean]
  B --> D[S3 Bucket: quarantine]
  B --> E[SNS Topic: csv-cleaner-events]
  E --> F[(Email Subscriber)]
