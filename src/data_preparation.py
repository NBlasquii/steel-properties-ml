from pathlib import Path

import pandas as pd


COMPOSITION_COLUMNS = [
    "Al",
    "Cu",
    "Mn",
    "N",
    "Ni",
    "Ti",
    "S",
    "Fe",
    "Zr",
    "P",
    "Si",
    "V",
    "Mo",
    "Co",
    "C",
    "Nb",
    "B",
    "Cr",
]

PROPERTY_COLUMNS = [
    "(Ultimate) Tensile strength (MPa)",
    "Yield strength (MPa)",
    "Ductility (%)",
]

def load_raw_data(file_path: Path) -> pd.DataFrame:
    """
    Load the raw steel dataset from an Excel file.

    Parameters
    ----------
    file_path : Path
        Path to the raw Excel dataset.

    Returns
    -------
    pd.DataFrame
        Raw dataset loaded into memory.

    Raises
    ------
    FileNotFoundError
        If the Excel file does not exist.
    """
        
    if file_path.exists() == False:
        raise FileNotFoundError(f"Dataset not found: {file_path}")
    
    df = pd.read_excel(
        file_path,
        sheet_name="Sheet1",
        engine="openpyxl",
    )

    return df

def validate_required_columns(df: pd.DataFrame) -> None:
    """
    Check that all columns required by the cleaning workflow exist.

    Raises
    ------
    ValueError
        If one or more required columns are missing.
    """
    
    required_columns = (
        COMPOSITION_COLUMNS
        + PROPERTY_COLUMNS
        + [
            "Entry",
            "Name",
            "Processing condition",
            "Cluster Number (0 to 11)",
            "Cluster label",
        ]
    )

    missing_columns = []

    for column in required_columns:
        if column not in df.columns:
            missing_columns.append(column)
    
    if len(missing_columns) > 0:
        raise ValueError("Required columns are missing from the dataset: "f"{missing_columns}")


def convert_required_columns_to_numeric (df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Convert required columns to numeric and record failed conversions.
    """
    df_numeric = df.copy()
    numeric_columns = COMPOSITION_COLUMNS + PROPERTY_COLUMNS

    issues_list = []

    for column in numeric_columns:
        original = df_numeric[column].copy()

        df_numeric[column] = pd.to_numeric(
            original,
            errors="coerce",
        )

        failed_mask = (
            original.notna()
            & df_numeric[column].isna()
        )

        if failed_mask.any():
            column_issues = pd.DataFrame(
                {
                    "Entry": df_numeric.loc[
                        failed_mask,
                        "Entry",
                    ],
                    "problematic_column": column,
                    "original_value": original.loc[
                        failed_mask
                    ],
                }
            )

            issues_list.append(column_issues)

    if issues_list:
        conversion_issues = pd.concat(
            issues_list,
            ignore_index=True,
        )
    else:
        conversion_issues = pd.DataFrame(
            columns=[
                "Entry",
                "problematic_column",
                "original_value",
            ]
        )

    return df_numeric, conversion_issues






