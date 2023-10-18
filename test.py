import pandas as pd

if __name__ == '__main__':
    # Read data from CSV file without headers
    data = pd.read_csv('test.csv', header=None, names=['time', 'total_time', 'spd'])

    # Group data based on the 'spd' column
    grouped_data = data.groupby('spd').agg({'time': 'mean', 'total_time': 'mean'}).reset_index()

    # grouped_data now contains the grouped data based on the 'spd' column
    print(grouped_data)
