# TheyDo S3 Upload Integration - Product & Sales Guide

## Overview

TheyDo provides a secure S3 integration that enables customers to upload structured JSON data directly into their TheyDo workspace. This integration supports automated import of three core data types: **Solutions**, **Insights**, and **Metrics**.

### Key Benefits
- **Automated Data Import**: Streamline the process of getting data into TheyDo
- **Data Validation**: Built-in schema validation ensures data integrity
- **Secure Transfer**: Industry-standard AWS security with IAM role-based access
- **Simple CLI Tool**: Easy-to-use command-line interface for testing and uploading

## Supported Data Types

### 1. Solutions (`THEYDO_SOLUTIONS_V1`)
Import solution data including:
- **Required**: Unique identifier, title
- **Optional**: Descriptions (Markdown support), external links, status, tags, groups, type, priority levels

**Use Cases**: Importing existing solution libraries, migrating from other platforms, bulk solution updates

### 2. Insights (`THEYDO_INSIGHTS_V1`) 
Import customer insights including:
- **Required**: Unique identifier, title
- **Optional**: Descriptions (Markdown support), icons, empathy scores, external links, types, status, tags, groups, weights

**Use Cases**: Research data import, customer feedback integration, insight consolidation

### 3. Metrics (`THEYDO_METRICS_V1`)
Import structured metrics data with support for:
- **CES (Customer Effort Score)**: Score-based measurements with respondent counts
- **CSAT (Customer Satisfaction)**: Five-point satisfaction scale measurements
- **NPS (Net Promoter Score)**: Promoter/passive/detractor classifications
- **Custom Metrics**: Flexible "OTHER" and "RATIO" types with custom aggregation
- **Time-series Data**: All metrics include date-based measurements

**Use Cases**: Performance dashboard integration, survey data import, KPI tracking

## Security & Setup

### Recommended Approach: IAM Role (Preferred)
**Customer Provides**: AWS Account ID  
**TheyDo Configures**: Predefined IAM role with minimal required permissions  
**Benefits**: 
- No credential rotation required
- Enhanced security through temporary credentials
- Follows AWS security best practices

### Alternative: Static Credentials
**TheyDo Provides**: AccessKeyId & SecretAccessKey  
**Use When**: Customer security policies require static credentials  
**Note**: Requires periodic credential rotation

### What TheyDo Handles
- S3 bucket configuration and permissions
- IAM role setup and trust relationships
- Schema validation rules
- Upload endpoint configuration

## CLI Tool Features

The S3TCLI tool provides three main commands:

### 1. Data Validation (`test-format`)
- Validates JSON files against TheyDo schemas
- Ensures data compatibility before upload
- Provides clear error messages for data issues

### 2. Connection Testing (`test-role`)
- Verifies AWS credential configuration
- Tests IAM role assumption process
- Confirms connectivity to AWS services

### 3. Upload & Validation (`test-upload`)
- Combines validation and upload in one step
- Generates unique file keys with timestamps
- Provides upload confirmation

## Customer Requirements

### Technical Prerequisites
- AWS Account (for IAM role setup)
- Basic command-line familiarity
- JSON data formatted according to TheyDo schemas

### Setup Process
1. **Initial Contact**: Customer expresses interest in S3 integration
2. **Account Setup**: Customer provides AWS Account ID to TheyDo
3. **Configuration**: TheyDo engineering configures IAM role and S3 bucket
4. **Credentials Sharing**: TheyDo provides role ARN, external ID, and bucket details
5. **Testing**: Customer downloads CLI tool and tests connection
6. **Go-Live**: Customer begins regular data uploads

### Typical Implementation Timeline
- **Setup & Configuration**: 1-2 business days
- **Testing & Validation**: 1-3 days (customer-dependent)
- **Total Time to Go-Live**: 3-5 business days

## Use Case Examples

### Enterprise Data Migration
*"Customer migrating from legacy CX platform with 500+ solutions and 1000+ insights"*
- Bulk export from existing system
- Format data according to TheyDo schemas
- Validate and upload in batches
- Verify import completion in TheyDo workspace

### Survey Data Integration
*"Customer with monthly NPS/CSAT surveys wanting automated reporting"*
- Export survey results to JSON format
- Configure automated upload pipeline
- Set up regular data refresh schedule
- Monitor metrics in TheyDo dashboards

### Research Repository Consolidation
*"Customer consolidating insights from multiple research tools"*
- Standardize insight formatting across sources
- Map existing categories to TheyDo taxonomy
- Migrate historical data in phases
- Establish ongoing integration workflows

## Competitive Advantages

- **Schema-First Approach**: Built-in data validation prevents import errors
- **Security Focus**: IAM role-based authentication exceeds industry standards
- **Flexibility**: Supports multiple data types and custom metric formats
- **Simplicity**: CLI tool eliminates need for custom development
- **Speed**: Setup completed in days, not weeks

## Common Questions & Responses

**Q: "How secure is the data transfer?"**  
A: We use AWS IAM roles with minimal permissions and encrypted transfer. No long-term credentials stored.

**Q: "What if our data doesn't match the schema exactly?"**  
A: The CLI tool provides clear validation errors. Our team can assist with data mapping and transformation guidance.

**Q: "Can we automate this process?"**  
A: Yes, the CLI tool can be integrated into automated workflows, scheduled tasks, or CI/CD pipelines.

**Q: "What about data privacy and compliance?"**  
A: Data remains in customer's AWS account until upload. Transfer uses encrypted channels. Supports compliance requirements for GDPR, SOC2, etc.

## Getting Started

1. **Repository Access**: https://github.com/theydo/theydo-s3-integrations
2. **Schema Reference**: Available in `/schema` directory
3. **Example Data**: Sample files provided in `/examples`
4. **Support**: Engineering team available for setup assistance

---

*This integration enables seamless data flow into TheyDo, reducing manual data entry and ensuring consistent, validated imports for better customer experience management.*