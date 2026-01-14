# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project relates to **Habilitación de Servicios de Salud** (Healthcare Services Accreditation) in Colombia, based on **Resolución 3100 de 2019** from the Ministry of Health. The project contains reference documents for healthcare facility self-evaluation and accreditation standards.

## Environment Setup

- Python 3.13.7 with virtual environment in `.venv`
- Activate virtual environment:
  - Windows: `.venv\Scripts\activate`
  - Linux/Mac: `source .venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt` (once created)

## Reference Documents

- `autoevaluacion-_resolucion-3100-2019-anexo-estandar.xlsx` - Self-evaluation spreadsheet with accreditation standards
- `Debes de Habilitacion - Vs 2.docx` - Accreditation requirements ("deberes")
- `resolucion-3100-de-2019-versión-copias-y-pegar.pdf` - Full text of Resolution 3100 of 2019

## Domain Context

Resolución 3100 de 2019 establishes the procedures and conditions for registration and accreditation of healthcare service providers in Colombia. Key concepts:
- **Estándares de habilitación**: Minimum quality standards healthcare facilities must meet
- **Autoevaluación**: Self-assessment process against the standards
- **Servicios de salud**: Healthcare services being evaluated
