# Data Quality Report

## Dataset

OpenFoodFacts Sample Dataset

## Data Quality Checks Implemented

The pipeline performs the following data quality checks:

1. Dataset should not be empty
2. product_name column must not contain null values
3. brand column must not contain null values
4. energy_100g values must be greater than or equal to 0
5. Duplicate product names should not exist

## Sample Results

Example output from pipeline execution:

- row_count_check: PASS
- product_name_not_null: PASS
- brand_not_null: PASS
- energy_positive: PASS
- duplicate_products: PASS

These checks ensure the dataset meets basic quality standards before metadata registration.