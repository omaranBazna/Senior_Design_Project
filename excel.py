import pandas as pd


def makeExcel(data):
    # Convert the array of arrays to a DataFrame
    df = pd.DataFrame(data)
    # Write the DataFrame to an Excel file
    df.to_excel('output.xlsx', index=False, header=False)
