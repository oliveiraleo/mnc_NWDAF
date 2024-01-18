import datetime as dt
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import pickle
import os
import traceback 
import sys
import hashlib
import time1 as t

from datetime import datetime
from glob import glob
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix


def hash_ip(ip):
    return int(hashlib.md5(ip.encode('utf-8')).hexdigest(), 16)

def train(model):
    files = glob("./train/*.csv")
    
    df=[]
    labels = ["ping","video","web"]

    try:
        for f in range(len(files)):
            df.append(pd.read_csv(files[f]))
            df[f]["label"] = [labels[f] for i in range(len(df[f]))]
    except IndexError:
        print("\n[ERROR] IndexError: list index out of range")
        print("[INFO] Labels loaded:", labels)
        print(f"[INFO] Make sure you have {len(files)} labels instead of {len(labels)}")
        print("[INFO] because they must match as each file belongs to one class (label)")
        exit()
    
    df = pd.concat(df,ignore_index=True)

    df.drop(columns=["Info",
                     "No.",
                     # "Source",
                     # "Destination"
                     ], 
                     axis=1,
                     inplace=True)
    
    df["Time"] = pd.to_datetime(df["Time"])

    # Adding a "Duration" column in seconds
    df["Duration"] = df["Time"].diff().dt.total_seconds()

    # Dropping rows with missing values
    df = df.dropna()

    # Encoding categorical features using Label Encoding
    protocol_encoder = LabelEncoder()
    label_encoder = LabelEncoder()
    
    for col in df.columns:
        if df[col].dtype == "object":
            if col == "Protocol":
                df[col] = protocol_encoder.fit_transform(df[col])
            elif col == "Source"  or col == "Destination":
                df[col] = df[col].apply(hash_ip)
            else:
                df[col] = label_encoder.fit_transform(df[col])

    # Normalizing features using standardization
    scaler = StandardScaler()
    scaler.fit(df[["Length", "Duration","Source","Destination"]])
    df[["Length", "Duration","Source","Destination"]] = scaler.transform(df[["Length", "Duration","Source","Destination"]])

    # Splitting the data into training and testing sets
    X = df.drop(columns=["Time",
                        "label",
                        ])
    y_str = df["label"]

    y_label_encoder = LabelEncoder()
    y_label_encoder.fit(y_str)
    y = y_label_encoder.transform(y_str)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

    if model == "1": 
        from sklearn.ensemble import RandomForestClassifier

        # Creating a Random Forest Classifier
        model = RandomForestClassifier(n_estimators=100,max_depth=2000)

    elif model == "2": 
        # Creating a Mult Layer Perceptron Classifier
        from sklearn.neural_network import MLPClassifier

        model = MLPClassifier(hidden_layer_sizes=(100, 100,50),solver="adam",max_iter=200)

    elif model == "3": 
        # Creating a Decision Tree Classifier
        from sklearn.tree import DecisionTreeClassifier

        model = DecisionTreeClassifier()

    else: 
        print(f"[ERROR] Option {model} for model doesn't exist")
        main() # returns to the main menu

    # Training the model on the training data
    model.fit(X_train, y_train)
    
    # print()
    # importance_with_columns = pd.DataFrame({'feature': X_train.columns, 'importance': model.feature_importances_})
    # print(importance_with_columns)
    # print()
    
    # Predicting the class labels for the test data
    y_pred = model.predict(X_test)

    # Evaluating the model performance
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Precision:", precision_score(y_test, y_pred, average="weighted"))
    print("Recall:", recall_score(y_test, y_pred, average="weighted"))
    print("F1-score:", f1_score(y_test, y_pred, average="weighted"))

    conf_matrix = confusion_matrix(y_test, y_pred)
    print("[DEBUG] Confusion Matrix:") #DEBUG
    print(conf_matrix) #DEBUG

    # Plot confusion matrix as a heatmap
    sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues", xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")

    plt.savefig("results/training_confusion_matrix.pdf")
    # plt.show() # DEBUG
    
    # File name to save data
    save_file = "model.pkl"

    # Save variables to file
    with open(save_file, "wb") as file:
        pickle.dump(label_encoder, file)
        pickle.dump(protocol_encoder, file)
        pickle.dump(scaler, file)
        pickle.dump(model, file)
    return  label_encoder,protocol_encoder, scaler, model


def load_model(path):
    try:
        # save_file = "model.pkl"
        # Load variables from file
        with open(path, "rb") as file:
            label_encoder = pickle.load(file)
            protocol_encoder = pickle.load(file)
            scaler = pickle.load(file)
            model = pickle.load(file)
              
        return  label_encoder,protocol_encoder, scaler, model
   
    except:
        print("[ERROR] Import error, check if the file exists on", path)


def inference(file, label_encoder,protocol_encoder, scaler, model):

    df = pd.read_csv(file)

    df.drop(columns=["Info",
                     "No.",
                     #"Source",
                     #"Destination"
                     ], axis=1, inplace=True)
    
    df["Time"] = pd.to_datetime(df["Time"])

    # Adding a "Duration" column in seconds
    df["Duration"] = df["Time"].diff().dt.total_seconds()

    df.drop(columns=["Time"],axis=1,inplace=True)

    # Dropping rows with missing values
    df = df.dropna()
    
    # Encoding categorical features using Label Encoding
    for col in df.columns:
        if df[col].dtype == "object":
            if col == "Protocol":
                df[col] = protocol_encoder.transform(df[col])
            elif col == "Source"  or col == "Destination":
                df[col] = df[col].apply(hash_ip)
            else:
                df[col] = label_encoder.transform(df[col])
    
    # df[["Length", "Duration"]] = scaler.transform(df[["Length", "Duration"]])
    df[["Length", "Duration","Source","Destination"]] = scaler.transform(df[["Length", "Duration","Source","Destination"]])

    # Getting the names of the LabelEncoder classes
    class_names = label_encoder.classes_

    # Extracting probabilities for the instances in the test set
    probabilities = model.predict_proba(df)

    # Creating a new DataFrame with the probabilities
    probabilities_df = pd.DataFrame(probabilities, columns=[f"{class_names[i]}" for i in range(len(class_names))])

    # Replacing NaN with 0 in the probability DataFrame
    probabilities_df.fillna(0, inplace=True)

    # Converting floating point values to percentage
    probabilities_df *= 100

    # Converting the predicted classes back to the original categories
    predicted_classes = label_encoder.inverse_transform(model.predict(df))

    probabilities_df = pd.concat([probabilities_df,pd.Series(predicted_classes, name="predicted_class")], axis=1)

    # Calculate the frequency of each label
    probabilities_count_df = probabilities_df.value_counts(subset="predicted_class")
    print("[DEBUG] Labels and their occurrences:\n", probabilities_count_df)

    # Calculate the total number of occurrences of all labels on input data
    total_occurrences = probabilities_count_df.sum()

    # Print the label of the class with the highest number of occurrences
    most_frequent_class_label = probabilities_count_df.idxmax()
    #probability_of_class = TODO calculate this, if necessary
    print("[INFO] Inference: The class of the input probably is", most_frequent_class_label) #TODO save this result somewhere
    # print(f"[INFO] with {probability_of_class}% of chance")
    
    # Get the current date and time
    current_time = datetime.now()

    # Format and print the current time
    formatted_time = current_time.strftime("%Y-%m-%d_%H-%M-%S")
    
    probabilities_df.to_csv(f"./results/inference_class_probability_{type(model).__name__}_{formatted_time}.csv", index_label="line_num") # save the probabilities

def main():
    working_dir = os.getcwd() # get the current working directory where the script was called

    while True:
        print("\nChoose an option:")
        print("1 - Train and save model")
        print("2 - Load model")
        print("3 - Inference")
        print("4 - Exit the program")

        e = input("Your input: ")

        if e == '1': 
            print("\nChoose a model:")
            print("1 - Random Forest Classifier")
            print("2 - Mult Layer Perceptron Classifier")
            print("3 - Decision Tree Classifier")
            m = input("Input: ")
            start = t.time()
            label_encoder,protocol_encoder, scaler, model = train(m)
            end = t.time()
            print("Execution time:",dt.timedelta(seconds=end - start))
            
        if e == '2': 
            # p = working_dir + "/ML_test_code/model.pkl"
            p = working_dir + "/model.pkl"
            print("\n[INFO] Loading the model file located at")
            print("[INFO] ", p)
            label_encoder,protocol_encoder, scaler, model = load_model(p)
            print("[INFO] Model successfully loaded")

        if e == '3': 
            print()
            print("Provide the name to the CSV file located on the inference folder:")
            p = input("Input: ")
            p = working_dir + "/inference/" + p
            try:
                start = t.time()
                inference(p,label_encoder,protocol_encoder, scaler, model)
                end = t.time()
                print("Execution time:",dt.timedelta(seconds=end - start))
            except ValueError as valueErr:
                print("[ERROR]", type(valueErr).__name__, valueErr)
                print("[ERROR] Could not find some labels")
                print("[INFO] Check the labels from the training data and inference to make sure they match")
            except Exception as error:
                print("[INFO] Read the file from: ", p)
                # printing stack trace 
                traceback.print_exception(*sys.exc_info())
                print("[ERROR]", type(error).__name__, error)

        if e == '4': 
            print("\n[INFO] Exiting the program...\n")
            exit()


if __name__ == "__main__":
    main()