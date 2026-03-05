# Data Lakehouse

## Overview

The Data Lakehouse layer is responsible for ingesting, transforming, and organizing raw transaction data into structured datasets suitable for machine learning.

This project follows a **three-layer lakehouse architecture**:

- Raw Layer
- Processed Layer
- Curated Layer

This design ensures reproducibility, traceability, and efficient data access for downstream ML pipelines.

---

## Raw Layer

The raw layer stores the original transaction datasets without modification.

Characteristics:

- Immutable
- Source of truth
- Stored in original schema
- Used for auditing and reproducibility

Example location:

---

## Processed Layer

The processed layer applies basic transformations such as:

- data type normalization
- missing value handling
- basic cleaning

Example location:

---

## Curated Layer

The curated layer contains datasets optimized for machine learning.

This includes:

- feature-ready datasets
- selected variables
- cleaned records
- schema validation

Example location:

---

## Data Flow

Raw Data
↓
Processed Data
↓
Curated Dataset
↓
Machine Learning Pipeline

---

## Benefits of This Architecture

- Clear data lineage
- Reproducibility
- Scalable data management
- Separation of concerns between data engineering and ML