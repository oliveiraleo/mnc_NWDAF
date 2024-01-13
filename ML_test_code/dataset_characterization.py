import csv
import traceback
import sys
import pandas as pd

def read_csv(file_path):
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        print(f"[ERROR] File not found at path {file_path}")
        exit()
    except Exception as e:
        # printing stack trace 
        traceback.print_exception(*sys.exc_info())
        print("[ERROR]", type(e).__name__, e)
        exit()

def extract_frequency_info(data_frames, column_names):
    freq_data_list = []
    
    for df in data_frames:
        try:
            # Use value_counts to get the frequency of each unique value in the specified columns
            frequency_info = {column: df[column].value_counts() for column in column_names}
            freq_data_list.append(frequency_info)
        except KeyError as ke:
            missing_columns = [col for col in column_names if col not in df.columns]
            print(f"Error: Columns {missing_columns} not found in the DataFrame.")
            exit()
        except Exception as e:
            # printing stack trace 
            traceback.print_exception(*sys.exc_info())
            print("[ERROR]", type(e).__name__, e)
            exit()

    return freq_data_list

def print_frequency_data(freq_data_list):
    for counter, item in enumerate(freq_data_list, start=1):
        print("[INFO] Frequency data extracted from data frame number", counter)
        for column_name, freq_series in item.items():
            print(f"Frequency information for {column_name}:")
            print(freq_series)
        print("[INFO] Finished printing data frame", counter)

# File paths
train_paths = ["./train/1ping-capture-intervals.csv", "./train/2video-capture-1k.csv", "./train/3web-capture-1k.csv"]
inference_paths = ["./inference/1ping-capture-intervals-inference.csv", "./inference/2video-capture-inference.csv", "./inference/3web-capture-inference.csv"]

# Read CSV files
train_dfs = [read_csv(path) for path in train_paths]
inference_dfs = [read_csv(path) for path in inference_paths]

# Extract frequency information
# as the features are the same on all files, no need to do that for all of them
column_names = train_dfs[0].columns.tolist()
# removes some columns from the frequency calculation because they almost always have only unique values
columns_to_remove = ["No.", "Time", "Info"]

for col in columns_to_remove:
    column_names.remove(col)

train_freq_data_list = extract_frequency_info(train_dfs, column_names)
inference_freq_data_list = extract_frequency_info(inference_dfs, column_names)

# Print frequency information
print("[INFO] Printing training data frequency information")
print_frequency_data(train_freq_data_list)
print("[INFO] Finished printing training data frequency information")
print("[INFO] Printing inference data frequency information")
print_frequency_data(inference_freq_data_list)
print("[INFO] Finished printing inference data frequency information")
