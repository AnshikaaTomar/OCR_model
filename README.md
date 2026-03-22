# OCR model for text extraction
This project implements a Python-based Optical Character Recognition (OCR) pipeline for extracting and processing text from scanned documents. It is designed to handle both English and Hindi content, with a focus on improving text quality through preprocessing and structured cleaning.

## Overview
The system processes input files (PDFs and images), enhances their quality using image preprocessing techniques, extracts text using Tesseract OCR, and applies multiple layers of cleaning to produce structured and readable output.

## Key Features
- Support for multiple input formats: PDF, JPG, JPEG, PNG  
- OCR using Tesseract with bilingual support (English and Hindi)  
- Image preprocessing for improved OCR accuracy:
  - Grayscale conversion  
  - Image scaling  
  - Noise reduction  
  - Deskewing  
  - Adaptive thresholding  
- Automatic removal of headers from the first page  
- Intelligent detection of document termination (signatures, distribution lists)  
- Removal of predefined unwanted phrases  
- Structured output with page-wise segmentation

## Project Structure
project/
- 
- inputs/            # Directory for input files
- outputs/           # Directory for processed output files
- training.py        # Main script for OCR processing

## Dependencies
Install the required python libraries
- pdf2images
- openCV
- Tesseract 
- Poppler
- Pillow

## Workflow
### File Loading
- Identifies file type and converts PDFs into images
### Image Preprocessing
- Enhances image quality using scaling, filtering, denoising, and deskewing
### Text Extraction
- Applies Tesseract OCR with optimized configuration for structured text
### Text Cleaning
- Removes unwanted phrases and noise
### Filters out low-quality lines
- Detects logical end of document content
### Output Generation
- Saves cleaned text into structured .txt files with page-wise separation
