# Overview

This is a Spanish-language loan amortization calculator built with Streamlit. The application allows users to calculate loan payment schedules with various payment frequencies (daily, weekly, biweekly, monthly, etc.) and different payment types (level payments or declining balance). It includes features for insurance calculations and generates both interactive displays and PDF reports of the amortization schedules.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit for web-based user interface
- **Language**: Spanish interface for Latin American users
- **Design Pattern**: Single-page application with centered layout
- **UI Components**: Custom HTML/CSS for branding with external icon integration

## Core Calculation Engine
- **Payment Frequencies**: Supports 10 different payment frequencies from daily to annual, plus "at maturity" option
- **Payment Types**: Two calculation methods - level payments (Nivelada) and declining balance (Saldos Insolutos)
- **Insurance Integration**: Optional insurance calculation based on percentage per thousand
- **Data Structure**: Uses pandas DataFrames for structured amortization schedule storage

## Report Generation
- **PDF Generation**: ReportLab library for creating formatted PDF documents
- **Export Formats**: PDF download capability with professional table formatting
- **Data Visualization**: Tabular presentation of payment schedules with color-coded styling

## Business Logic
- **Interest Calculations**: Supports various compounding frequencies matching payment schedules
- **Amortization Methods**: Implements standard financial formulas for loan amortization
- **Edge Cases**: Special handling for "at maturity" payments and insurance calculations

# External Dependencies

## Python Libraries
- **streamlit**: Web application framework for the user interface
- **pandas**: Data manipulation and analysis for amortization tables
- **reportlab**: PDF generation and document formatting
- **io/base64**: File handling and encoding for downloads

## External Assets
- **Flaticon**: Icon hosting service for application branding (https://cdn-icons-png.flaticon.com)

## File System
- Local file system access for temporary PDF generation and storage
- No database dependencies - all calculations performed in-memory

## Browser Dependencies
- Modern web browser with JavaScript support for Streamlit functionality
- PDF viewing capabilities for generated reports