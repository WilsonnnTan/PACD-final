# PACD Final Project

## Identity

- Name: Wilson Angelie Tan
- NIM: 140810230024

## Project Description

This project is about transforming color space from RGB to LAB.

Source of information:

- https://medium.com/@alakhsharmacs/rgb-to-lab-color-space-conversion-formulas-insights-and-applications-7fd6efa519dd

## Setup

This project uses `uv` for dependency management.

If `uv` is not installed yet, run this PowerShell command:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After `uv` is installed, synchronize the project dependencies:

```powershell
uv sync
```

## Run the Project

To run the main program, use:

```powershell
uv run python main.py
```
