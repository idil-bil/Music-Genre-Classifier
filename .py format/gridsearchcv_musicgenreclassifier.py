# -*- coding: utf-8 -*-
"""GridSearchCV - MusicGenreClassifier

# **CPEN 355 Project - Music Genre Classifier**

*   Idil Bil 
*   Mehmet Berke Karadayi
*   Peter Na

## Initializations
"""

# Import necessary libraries for numerical operations, array handling, data manipulation, and visualization
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Import machine learning components from scikit-learn
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, ConfusionMatrixDisplay

# Import preprocessing and pipeline tools
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# Import table formatting library for better output display
from tabulate import tabulate

# Import GridSearch to find optimal hyperparameters
from sklearn.model_selection import GridSearchCV

"""## Data Processing"""

# Read the .CSV data
music_data_raw = pd.read_csv("sample_data/music_genre.csv")

# Drop the irrelevant columns to the classification and rows with missing cells in any column
music_data_filter = (
    music_data_raw
    .replace('?', np.nan)                                                               # Replace cells with '?' with NaN(blank)
    .dropna()                                                                           # Drop rows with any blank values
    .drop(columns=['instance_id','artist_name', 'track_name', 'obtained_date'])
)

# Use one-hot encoding for categorical/string variables
music_data = pd.get_dummies(music_data_filter, columns=['key', 'mode'], drop_first=True, dtype=int)

print('DATASET AFTER CLEANING')
print(tabulate(music_data.head(10), headers='keys', tablefmt='grid'))

"""## Data Visualization"""

# Count the occurrences of each music genre
genre_counts = music_data['music_genre'].value_counts()

# Create a bar plot to visualize the balance of the dataset
plt.figure(figsize=(10, 6))
genre_counts.plot(kind='bar', color='darkgreen')
plt.title('Distribution of Music Genres', fontweight='bold')
plt.xlabel('Music Genre', fontweight='bold')
plt.ylabel('Number of Occurrences', fontweight='bold')
plt.xticks(rotation=0)                                          # Rotate the x-axis labels for readibility
plt.ylim(4300, 4600)                                            # Limit the y-axis min and max values to see the counts clearly
plt.grid(axis='y', linestyle='-', alpha=0.2)
plt.show()

"""# Model 1 - Random Forest

## Training
"""

# Separate the features and target variable from the dataset
X = music_data.drop(columns=['music_genre'])                  # X contains all features except the target ('music_genre')
y = music_data['music_genre']                                 # y contains only the target variable ('music_genre')

# Split the data: 70% training, 20% validation, 10% testing
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)        # 70% training, 30% temp
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=1/3, random_state=42)  # 20% validation, 10% testing

# Define the parameter grid for the RandomForestClassifier
param_grid_RFC = {
    'classifier__n_estimators': [500, 700],               # Varying number of trees in the forest
    'classifier__max_depth': [10, 20],                    # Max depth of each decision tree
    'classifier__min_samples_split': [10, 20],            # Minimum samples required to split an internal node
    'classifier__min_samples_leaf': [5, 10],              # Minimum samples required at each leaf node
    'classifier__max_features': ['sqrt']                  # Number of features to consider at each split
}

# Create the RFC pipeline with StandardScaler and RandomForestClassifier
rfc = Pipeline([
    ('scaler', StandardScaler()),                             # Standardize features
    ('classifier', RandomForestClassifier(random_state=42))   # Random Forest model with base hyperparameters
])

# Set up GridSearchCV with cross-validation
grid_search_RFC = GridSearchCV(
    estimator=rfc,                            # Use the pipeline as the estimator
    param_grid=param_grid_RFC,                # Parameter grid to search
    cv=5,                                     # 5-fold cross-validation
    scoring='accuracy',                       # Use accuracy as the evaluation metric
    n_jobs=-1,                                # Use all available cores to speed up computation
    verbose=2                                 # Print progress to monitor the search process
)

# Fit GridSearchCV to the training data
grid_search_RFC.fit(X_train, y_train)

# Print the best parameters and best score found by GridSearchCV
print("Best parameters found: ", grid_search_RFC.best_params_)
print("Best cross-validation accuracy: ", grid_search_RFC.best_score_)

# Print the split of the datasets and the end of training
print(f'Training set: {X_train.shape}, Validation set: {X_val.shape}, Test set: {X_test.shape}')
print("Random Forest classifier has been trained.")

"""## Validation"""

# Perform cross-validation on the validation data to evaluate the model's performance
cv_results = cross_validate(grid_search_RFC.best_estimator_, X_val, y_val, cv=5, return_train_score=True)

# Convert the cross-validation results into a DataFrame for easier visualization and analysis
cv_results_df = pd.DataFrame(cv_results)

# Print the DataFrame to display the cross-validation scores for each fold
print(cv_results_df)

"""## Testing"""

# Use the trained RF classifier to predict labels for the test data
y_pred = grid_search_RFC.best_estimator_.predict(X_test)

"""## Results"""

# Print the overall performance report
print("Overall Report - Random Forest Classifier")
print("-------------------------------")
accuracy_rf = accuracy_score(y_test, y_pred)                                                    # Calculate the accuracy score
print(f'Accuracy: {accuracy_rf}')                                                               # Print the calculated accuracy
print("-------------------------------")
class_report_rf = classification_report(y_test, y_pred)                                         # Generate the classification report
print(class_report_rf)                                                                          # Print the classification report (includes: precision, recall, and F1-score for each class)

# Plot the confusion matrix for the RF model
conf_matrix_rf = confusion_matrix(y_test, y_pred)                                               # Generate the confusion matrix
disp_rf = ConfusionMatrixDisplay(confusion_matrix=conf_matrix_rf, display_labels=grid_search_RFC.classes_)
disp_rf.plot(cmap=plt.cm.Blues)                                                                 # Display the confusion matrix
plt.xticks(rotation=45)
plt.title('Confusion Matrix', fontweight='bold')
plt.show()

"""# Model 2 - Support Vector

##Training
"""

# Define a parameter grid to search for optimal hyperparameters
param_grid_SVC = {
    'classifier__C': [1, 5],                                  # Regularization parameter
    'classifier__kernel': ['rbf'],                            # Kernel types for decision boundary shape
    'classifier__gamma': ['scale', 0.1],                      # Gamma controls influence of data points for 'rbf' kernel
    'classifier__max_iter': [500, -1]                         # Max iterations (-1 for unlimited)
}

# Create the SVC pipeline with StandardScaler and Support Vector Classifier
svc = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', SVC(random_state=42))         # SVC initialized without specifying parameters
])

# Set up GridSearchCV with cross-validation
grid_search_SVC = GridSearchCV(
    estimator=svc,                               # Use the pipeline as the estimator
    param_grid=param_grid_SVC,                   # Parameter grid to search
    cv=5,                                        # 5-fold cross-validation
    scoring='accuracy',                          # Optimize for accuracy score
    n_jobs=-1,                                   # Use all available cores
    verbose=2                                    # Output progress to the console
)

# Run grid search on the training data
grid_search_SVC.fit(X_train, y_train)

# Print the results of the grid search
print("Best parameters found: ", grid_search_SVC.best_params_)
print("Best cross-validation accuracy: ", grid_search_SVC.best_score_)

# Print the split of the datasets and the end of training
print(f'Training set: {X_train.shape}, Validation set: {X_val.shape}, Test set: {X_test.shape}')
print("Random Forest classifier has been trained.")

"""##Validation"""

# Perform cross-validation on the validation data to evaluate the model's performance
cv_results = cross_validate(grid_search_SVC.best_estimator_, X_val, y_val, cv=5, return_train_score=True)

# Convert the cross-validation results into a DataFrame for easier visualization and analysis
cv_results_df = pd.DataFrame(cv_results)

# Print the DataFrame to display the cross-validation scores for each fold
print(cv_results_df)

"""##Testing"""

# Use the trained SV classifier to predict labels for the test data
y_pred = grid_search_SVC.best_estimator_.predict(X_test)

"""##Results"""

# Print the overall performance report
print("Overall Report - Support Vector Classifier")
print("-------------------------------")
accuracy_sv = accuracy_score(y_test, y_pred)                                                    # Calculate the accuracy score
print(f'Accuracy: {accuracy_sv}')                                                               # Print the calculated accuracy
print("-------------------------------")
class_report_sv = classification_report(y_test, y_pred)                                         # Generate the classification report
print(class_report_sv)                                                                          # Print the classification report (includes: precision, recall, and F1-score for each class)

# Plot the confusion matrix for the SV model
conf_matrix_sv = confusion_matrix(y_test, y_pred)                                               # Generate the confusion matrix
disp_sv = ConfusionMatrixDisplay(confusion_matrix=conf_matrix_sv, display_labels=grid_search_SVC.classes_)
disp_sv.plot(cmap=plt.cm.Blues)                                                                 # Display the confusion matrix
plt.xticks(rotation=45)
plt.title('Confusion Matrix', fontweight='bold')
plt.show()
