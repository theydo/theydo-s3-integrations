# TheyDo S3 Upload Integration - Product & Sales Guide

## Overview

TheyDo's S3 integration provides a **universal connector** that enables customers to upload structured JSON data from virtually any system into their TheyDo workspace. This powerful integration currently supports automated import of three core data types: **Solutions**, **Insights**, and **Metrics**.

**🚀 Real-World Success**: Our #1 customer Siemens has successfully implemented this integration to connect Polarion, Adlytics, and Adobe Analytics - demonstrating the flexibility to integrate platforms that don't have native TheyDo connectors.

### Key Benefits
- **Universal Data Ingestion**: Connect any system that can export JSON files
- **Rapid Implementation**: Setup completed in days/hours, not weeks
- **Data Validation**: Built-in schema validation ensures data integrity before import
- **Enterprise Security**: Industry-standard AWS IAM role-based access with encryption
- **Simple CLI Tool**: Battle-tested command-line interface for easy setup and testing

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

### Enterprise Security Architecture
TheyDo uses a **dedicated AWS account** specifically for external integrations, ensuring complete isolation from production systems. Each customer receives their own IAM role with permissions scoped only to their designated S3 prefix.

### Recommended Approach: IAM Role (Preferred)
**Customer Provides**: 
- AWS Account ID
- External ID (for secure role assumption)

**TheyDo Configures**: 
- Dedicated IAM role with minimal required permissions
- Unique S3 prefix for customer data isolation
- Permission boundary policies for additional security

**Benefits**: 
- **Zero Credential Management**: No keys to store, rotate, or secure
- **Enhanced Security**: Temporary credentials with automatic expiration
- **AWS Best Practices**: Follows enterprise security standards
- **Audit Trail**: Complete CloudTrail logging of all access

### Alternative: Static Credentials (Not Recommended)
**Available When**: Customer compliance requirements mandate static credentials  
**Note**: Requires periodic credential rotation and additional security overhead

### What TheyDo Handles
- **Infrastructure Setup**: Dedicated S3 bucket and IAM configuration
- **Security Implementation**: Role creation with permission boundaries
- **Data Validation**: Schema enforcement and error reporting
- **Monitoring**: Upload success/failure tracking

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
2. **Requirements Gathering**: Customer provides AWS Account ID and External ID
3. **TheyDo Configuration**: Engineering team creates dedicated IAM role and S3 prefix (1-2 business days)
4. **Credentials Delivery**: TheyDo provides:
   - IAM Role ARN for assumption
   - S3 bucket name and unique prefix
   - External ID for secure authentication
5. **Customer Testing**: Download CLI tool and validate connection
6. **Data Mapping**: Customer maps their data to TheyDo schemas using provided templates
7. **Go-Live**: Customer implements automated data uploads

### Proven Implementation Timeline
Based on real customer implementations:
- **Setup & Configuration**: 1-2 business days (TheyDo side)
- **Customer Integration**: Hours to days (depending on data complexity)
- **Total Time to Go-Live**: 2-5 business days

**Success Story**: "The basic implementation of pushing any data to TheyDo using S3 is matter of days if not hours" - *Jaanus Kivistik, Head of Engineering*

## Real Customer Success Stories

### 🏭 Siemens: Multi-Platform Integration
**Challenge**: Connect Polarion (requirements management), Adlytics, and Adobe Analytics to TheyDo
**Solution**: Custom S3 integration for each platform
**Results**: 
- Successful data flow from 3 previously unconnected systems
- Became TheyDo's #1 customer during implementation
- Demonstrates S3 integration's flexibility for any platform

**Implementation**: Siemens developed custom exporters for each platform that format data according to TheyDo schemas and upload via S3

### 📊 Generic Survey Data Integration
*"Customer with monthly NPS/CSAT surveys wanting automated reporting"*
- Export survey results to JSON format matching TheyDo metrics schemas
- Supports all major survey types: CES, CSAT, NPS, custom metrics
- Configure automated upload pipeline with timestamp-based file naming
- Monitor metrics in TheyDo dashboards with full historical data

### 🔄 Legacy Platform Migration
*"Enterprise customer migrating from legacy CX platform"*
- Bulk export of 500+ solutions and 1000+ insights
- Data validation ensures clean import without errors
- Batch processing with progress tracking
- Complete historical data preservation in TheyDo

### 🛠️ Internal Tool Integration
**Real Example**: TheyDo's internal Linear integration
- Automatically syncs Linear projects and tickets as TheyDo solutions
- Built in ~30 minutes using existing S3 infrastructure
- Demonstrates rapid prototyping capabilities for custom integrations

## Competitive Advantages

### Why S3 Integration is a Game-Changer

- **Universal Connectivity**: Acts as an "open API" that connects ANY system capable of JSON export
- **Enterprise Security**: Dedicated AWS account isolation with permission boundaries exceeds compliance requirements
- **Proven at Scale**: Successfully implemented by Fortune 500 companies with complex tech stacks
- **Rapid Prototyping**: New integrations can be built in hours/days rather than months
- **No Vendor Lock-in**: Standard S3 interface works with any cloud provider or on-premises system
- **Cost-Effective**: Eliminates need for expensive custom API development

### Target Customer Profile
**Ideal Fit**: Companies with engineering resources and complex tool ecosystems
- Large enterprises with custom/legacy systems
- Organizations using platforms without native TheyDo connectors
- Teams requiring high security standards and audit compliance
- Companies with existing AWS infrastructure

## Common Questions & Responses

**Q: "How secure is the data transfer?"**  
A: We use AWS IAM roles with minimal permissions and encrypted transfer. No long-term credentials stored.

**Q: "What if our data doesn't match the schema exactly?"**  
A: The CLI tool provides clear validation errors. Our team can assist with data mapping and transformation guidance.

**Q: "Can we automate this process?"**  
A: Yes, the CLI tool can be integrated into automated workflows, scheduled tasks, or CI/CD pipelines.

**Q: "What about data privacy and compliance?"**  
A: We use a dedicated AWS account for integrations with complete isolation from production. Data is encrypted in transit and at rest. Full audit trails via CloudTrail. Supports GDPR, SOC2, and enterprise compliance requirements.

**Q: "Our platform doesn't have direct S3 export - can we still use this?"**  
A: Yes! Any system that can export JSON files can use this integration. Examples include Polarion (via custom SDK exporters), survey platforms, databases, or even manual file uploads. The key is formatting your data according to our schemas.

**Q: "How complex is the setup compared to other integrations?"**  
A: Much simpler than custom API development. Once we provide your role ARN and bucket details, it's a matter of configuring your export process. Our CLI tool handles all the validation and upload logic.

## Getting Started

### For Customers
1. **Contact Sales**: Express interest in S3 integration capabilities
2. **Provide Credentials**: Share AWS Account ID and External ID with TheyDo
3. **Receive Setup**: TheyDo engineering provides role ARN and S3 bucket details
4. **Download CLI**: Get the validation and upload tool from our public repository
5. **Test Connection**: Validate your setup using the `test-role` command
6. **Map Data**: Format your export data according to TheyDo schemas
7. **Go Live**: Begin automated uploads to TheyDo

### Resources
- **Public Repository**: Available at GitHub (theydo/theydo-s3-integrations)
- **Schema Documentation**: Complete JSON schemas for all supported data types
- **Example Files**: Sample data formats and CLI usage examples
- **Data Mapping Templates**: Spreadsheet templates for data structure planning

### Support & Next Steps
- **Customer Success**: Dedicated support during implementation
- **Engineering Consultation**: Available for complex data mapping scenarios
- **Future Roadmap**: Additional data types and enhanced automation features planned

---

*This integration enables seamless data flow into TheyDo, reducing manual data entry and ensuring consistent, validated imports for better customer experience management.*
