import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import pickle
from glob import glob
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix


def train(model):
    files = glob('./train/*.csv')
    
    df=[]
    labels = ['ping','video','web']
    for f in range(len(files)):
        df.append(pd.read_csv(files[f]))
        df[f]['label'] = [labels[f] for i in range(len(df[f]))]
    df = pd.concat(df,ignore_index=True)

    df.drop(columns=['Info',
                     'No.',
                     "Source",
                     "Destination"], 
                     axis=1,
                     inplace=True)
    
    df['Time'] = pd.to_datetime(df['Time'])

    # Adding a 'Duration' column in seconds
    df['Duration'] = df['Time'].diff().dt.total_seconds()

    # Dropping rows with missing values
    df = df.dropna()

    # Encoding categorical features using Label Encoding
    protocol_encoder = LabelEncoder()
    label_encoder = LabelEncoder()
    
    for col in df.columns:
        if df[col].dtype == 'object':
            if col == 'Protocol':
                df[col] = protocol_encoder.fit_transform(df[col])
            else:
                df[col] = label_encoder.fit_transform(df[col])

    # Normalizing features using standardization
    scaler = StandardScaler()
    scaler.fit(df[['Length', 'Duration']])
    df[['Length', 'Duration']] = scaler.transform(df[['Length', 'Duration']])

    # Splitting the data into training and testing sets
    X = df.drop(columns=['Time',
                        'label',
                        ])
    y_str = df['label']

    y_label_encoder = LabelEncoder()
    y_label_encoder.fit(y_str)
    y = y_label_encoder.transform(y_str)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

    if model == '1': 
        from sklearn.ensemble import RandomForestClassifier

        # Creating a Random Forest Classifier
        model = RandomForestClassifier(n_estimators=100,max_depth=2000)

    elif model == '2': 
        # Creating a Mult Layer Perceptron Classifier
        from sklearn.neural_network import MLPClassifier

        model = MLPClassifier(hidden_layer_sizes=(100, 100,50),solver='adam',max_iter=200)

    elif model == '3': 
        # Creating a Decision Tree Classifier
        from sklearn.tree import DecisionTreeClassifier

        model = DecisionTreeClassifier()

    else: 
        print("Modelo Inexistente!")
        exit()

    # Training the model on the training data
    model.fit(X_train, y_train)

    # Predicting the class labels for the test data
    y_pred = model.predict(X_test)

    # Evaluating the model performance
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Precision:", precision_score(y_test, y_pred, average='weighted'))
    print("Recall:", recall_score(y_test, y_pred, average='weighted'))
    print("F1-score:", f1_score(y_test, y_pred, average='weighted'))

    conf_matrix = confusion_matrix(y_test, y_pred)
    print("Confusion Matrix:")
    print(conf_matrix)

    # Plot confusion matrix as a heatmap
    sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues", xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")

    plt.savefig("results/training_confusion_matrix.pdf")
    plt.show()
    
    # File name to save data
    save_file = 'model.pkl'

    # Save variables to file
    with open(save_file, 'wb') as file:
        pickle.dump(label_encoder, file)
        pickle.dump(protocol_encoder, file)
        pickle.dump(scaler, file)
        pickle.dump(model, file)
    return  label_encoder,protocol_encoder, scaler, model


def load_model(path):
    try:
        # save_file = 'model.pkl'
        # Load variables from file
        with open(path, 'rb') as file:
            label_encoder = pickle.load(file)
            protocol_encoder = pickle.load(file)
            scaler = pickle.load(file)
            model = pickle.load(file)
              
        return  label_encoder,protocol_encoder, scaler, model
   
    except:
        print("Import error, check the file!")

def inference(file, label_encoder,protocol_encoder, scaler, model):

    df = pd.read_csv(file)

    df.drop(columns=['Info',
                     'No.',
                     "Source",
                     "Destination"], axis=1, inplace=True)
    
    df['Time'] = pd.to_datetime(df['Time'])

    # Adding a 'Duration' column in seconds
    df['Duration'] = df['Time'].diff().dt.total_seconds()

    df.drop(columns=['Time'],axis=1,inplace=True)

    # Dropping rows with missing values
    df = df.dropna()

    # Encoding categorical features using Label Encoding
    for col in df.columns:
        if df[col].dtype == 'object':
            if col == 'Protocol':
                df[col] = protocol_encoder.transform(df[col])
            else:
                df[col] = label_encoder.transform(df[col])
    
    df[['Length', 'Duration']] = scaler.transform(df[['Length', 'Duration']])

    # Getting the names of the LabelEncoder classes
    class_names = label_encoder.classes_

    # Extracting probabilities for the instances in the test set
    probabilities = model.predict_proba(df)

    # Creating a new DataFrame with the probabilities
    probabilities_df = pd.DataFrame(probabilities, columns=[f'{class_names[i]}' for i in range(len(class_names))])

    # Replacing NaN with 0 in the probability DataFrame
    probabilities_df.fillna(0, inplace=True)

    # Converting floating point values to percentage
    probabilities_df *= 100

    # Converting the predicted classes back to the original categories
    predicted_classes = label_encoder.inverse_transform(model.predict(df))

    probabilities_df = pd.concat([probabilities_df,pd.Series(predicted_classes, name='predicted_class')], axis=1)

    print(probabilities_df)
    probabilities_df.to_csv("./results/inference_class_probability.csv") # save the probabilities

def main():
    while True:
        print()
        print("Choose an option:")
        print('1 - Train and save model')
        print('2 - Load model')
        print('3 - Inference')
        print("4 - Exit the program")

        e = input()

        if e == '1': 
            print()
            print("Model")
            print('1 - Random Forest Classifier')
            print('2 - Mult Layer Perceptron Classifier')
            print('3 - Decision Tree Classifier')
            m = input()
            label_encoder,protocol_encoder, scaler, model = train(m)

        if e == '2': 
            print()
            print("Path to files:")
            p = input ()
            label_encoder,protocol_encoder, scaler, model = load_model(p)

        if e == '3': 
            print()
            print("Path to files:")
            p = input ()
            try:
                inference(p,label_encoder,protocol_encoder, scaler, model)
            except:
                print("Error!")

        if e == '4': 
            print()
            print("Exiting the program")
            exit()


if __name__ == "__main__":

    main()