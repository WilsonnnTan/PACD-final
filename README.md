# PACD Final Project

## Identity

- Name: Wilson Angelie Tan
- NIM: 140810230024

## Project Description

This project focuses on transforming color space from RGB to LAB and converting the
LAB result back into RGB for previewing. The interface shows:

- the original RGB image
- the LAB image after it is converted back into RGB
- live sliders to adjust the `L`, `a`, and `b` values before the round-trip back to RGB

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
