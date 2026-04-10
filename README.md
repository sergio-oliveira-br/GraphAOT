# GraphAOT – Predicting Java AOT Migration Complexity

This project is part of an ongoing MSc research focused on understanding and correlate the complexity of migrating Java applications to GraalVM Native Image.

The main goal is to investigate whether Maven dependency graph structures can provide early indicators of migration difficulty, reducing trial-and-error during AOT compilation.

---

## Overview

Migrating Java applications to native binaries using GraalVM can significantly improve performance. However, the process is often complex due to dependency-related issues that only surface during compilation.

This project explores a **Shift-Left approach**, analyzing dependency structures *before* compilation to estimate migration effort.

The system is built as a data pipeline composed of two main stages:

1. **Data Collection (Harvester)**
2. **Graph Analysis & Metrics Extraction**

---

## Architecture

### 1. Data Collection Pipeline (`data_collection.py`)

Responsible for building the **data lake**.

#### What it does:
- Clones Java projects from GitHub
- Extracts dependency data using Maven
- Generates:
  - `bom.json` (dependency tree)
  - `effective-pom.xml`
- Uploads artifacts to AWS S3
- Tracks execution status via a manifest file

#### Output:
Structured raw data for further analysis.

---

### 2. Graph Processing Pipeline (`graph_processor.py`)

Responsible for transforming raw data into **graph-based insights**.

#### What it does:
- Downloads BOM data from S3
- Builds dependency graphs using NetworkX
- Extracts structural metrics:
  - Graph size
  - Depth
  - Connectivity
- Analyzes AOT-related metadata:
  - Reflection usage
  - Proxy usage
  - JNI requirements
- Computes migration complexity indicators
- Stores results in a structured dataset

#### Output:
- Processed metrics (`analysis_results.csv`)
- Detailed logs for further inspection

---

## Key Concepts

This project combines ideas from:

- Dependency Graph Analysis  
- Software Composition Analysis (SCA)  
- Shift-Left Engineering  
- Cloud-native Java optimization (GraalVM)  

---

## Research Focus

The project aims to answer:

> Can dependency graph structure predict the difficulty of migrating Java applications to native binaries?

### Investigated aspects:
- Graph topology (depth, density, coupling)
- Dependency composition
- Required configuration effort (reflection, JNI, proxies)
- Correlation with build complexity signals

---

## Current Status

Work in progress...

Preliminary analysis includes:
- Multiple Java projects processed
- Dependency graphs generated and analyzed
- Early signals observed between:
  - Graph complexity
  - Configuration overhead for AOT builds

A prototype pipeline is fully functional and being iteratively improved.

---

## Tech Stack

- Python (data pipelines, analysis)
- Java / Maven (dependency extraction)
- AWS S3 (data storage)
- NetworkX (graph analysis)
- GitHub (project sourcing)
