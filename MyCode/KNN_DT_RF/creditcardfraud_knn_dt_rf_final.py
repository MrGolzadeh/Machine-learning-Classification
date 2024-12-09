# -*- coding: utf-8 -*-
"""creditcardfraud_knn_dt_rf_final.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Ssacwmrfvr-tVdHSVhv4Tizb3fAiyZkJ

Copyright © [2024] [ Saeed Babagolzadeh & Hamed Jamshidi ]

Feel free to use this content, provided you properly this GitHub repository:
 [MrGolzadeh's GitHub repository](https://github.com/MrGolzadeh/MrGolzadeh). For more details, see the [Creative Commons BY license.](https://creativecommons.org/licenses/by/4.0/)

# Credit Card Fraud Detection

This dataset presents transactions that occurred in two days, where we have 492 frauds out of 284,807 transactions.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.metrics import classification_report
import warnings
warnings.filterwarnings('ignore')

"""# **Download Dataset**"""

import kagglehub

# Download latest version
path = kagglehub.dataset_download("mlg-ulb/creditcardfraud")

print("Path to dataset files:", path)

# load above downloaded file
import pandas as pd

df = pd.read_csv(path + '/creditcard.csv')
df.head()

"""## Exploratory Data Analysis (EDA):


1. Check Summary Statistics for the Dataset
2. Visualize Distribution of Classes
3. Check Correlation Matrix
4. Plot the Distribution of Some Selected Features

.
.
.

"""

# Display summary statistics for the dataset
df.describe()

# Plot the correlation matrix
import seaborn as sns

corr_matrix = df.corr()
plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, annot=False, cmap='coolwarm', linewidths=0.5)
plt.title('Correlation Matrix')
plt.show()
corr_matrix

# Plot the distribution of all columns
for col in df.columns:
    plt.figure(figsize=(8,4))
    plt.title(f'Distribution of {col}')
    sns.set_style("white")
    plt.ylabel('count')
    sns.distplot(x=df[col],kde=True, hist_kws=dict(edgecolor="black"),bins=40)
    plt.show()

# Separate features and target variable
X = df.drop('Class', axis=1)
y = df['Class']
X.shape, y.shape

# Display the class distribution in percentages
class_counts = df['Class'].value_counts(normalize=True) * 100
print(f"Class Distribution:\n{class_counts}")

# Visualize the class distribution
sns.countplot(x='Class', data=df)
plt.title('Class Distribution')
plt.show()

"""1. Two major challenges in the dataset based on your EDA findings:
> 1. Dataset is imbalance
> 2. Features are not in the same scale   
2. Analyze the correlation matrix of the features.
> The correlation matrix illustrates the correlation of each feature with the label and with each other. In this case, the label has the lowest correlation with feature v17. Additionally, normalizing the feature scale could potentially result in a different correlation matrix.

## Data Preprocessing

Based on the challenges we've identified, recommend preprocessing methods to use during training to enhance model performance are:


* Data Cleaning (Handling Missing Values, ...)
* Data Transformation (Standardization, ...)
* Feature Engineering (Feature Selection, ...)
* Handling Imbalanced Data
* ...
"""

df.shape

df.columns

X.columns

df.isnull().sum()

# Standardize the features
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler

def standardize_features(X_train, X_test):
    #scaler = RobustScaler()
    scaler = StandardScaler()
    #scaler = MinMaxScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    return X_train, X_test

# Balance the dataset
def dataset_balancement(X_train, y_train):
    X_train = np.array(X_train)
    y_train = np.array(y_train)

    fraud_indices = np.where(y_train == 1)[0]
    not_fraud_indices = np.where(y_train == 0)[0]
    fraud_records =  len(fraud_indices)

    under_sample_indices = np.random.choice(not_fraud_indices, len(not_fraud_indices), False)
    over_sample_indices = np.random.choice(fraud_indices, len(y_train), replace=True)

    y_train = y_train[np.concatenate([over_sample_indices, under_sample_indices])]
    X_train = X_train[np.concatenate([over_sample_indices, under_sample_indices])]
    print(X_train.shape, y_train.shape)
    return X_train, y_train

"""# **Forward sequential selection**"""

from sklearn.feature_selection import SequentialFeatureSelector
from sklearn.linear_model import RidgeCV

ridge = RidgeCV(alphas=np.logspace(-6, 6, num=5)).fit(X, y)
feature_names = np.array(list(df.columns[:-1]))
sfs_forward = SequentialFeatureSelector(
    ridge, n_features_to_select=5, direction="forward"
).fit(X, y)

print(
    "Features selected by forward sequential selection: "
    f"{feature_names[sfs_forward.get_support()]}")

# Features selected by forward sequential selection: ['V10' 'V12' 'V14' 'V16' 'V17']

selected_features = ['V10', 'V12', 'V14', 'V16', 'V17']
new_df = df[selected_features]

new_df.head(5)

X_new = new_df
y_new = df['Class']
X_new.shape, y_new.shape

"""## Classifying

1. Use KNN model on the preprocessed and unpreprocessed training data.
2. Report followning evaluaiton metrics: Accuracy, Recall, Precision, Confusion Matrix
3. Evaluation the best model using K-Fold Cross Validation
3. Enhance Model's Performance
"""

from sklearn.neighbors import KNeighborsClassifier, NearestCentroid
from sklearn.model_selection import StratifiedKFold, KFold , cross_val_score
from sklearn.metrics import accuracy_score, recall_score, classification_report
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.metrics import roc_auc_score, roc_curve, RocCurveDisplay
from sklearn.model_selection import train_test_split
import seaborn as sns

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, y_train)
pred = knn.predict(X_test)
print("Accuracy Score",accuracy_score(y_test, pred))

print(cross_val_score(knn, X_train, y_train, cv=10))

print("Classification Report:")
print(classification_report(y_test, pred))

"""# Finding the Optimum K"""

accuracy_rate = []
for i in range(1,12):
    knn = KNeighborsClassifier(n_neighbors=i)
    scores = cross_val_score(knn, X_train, y_train, cv=10, scoring='accuracy')
    accuracy_rate.append(scores.mean())

plt.figure(figsize=(8,6))
accuracy_plot = plt.plot(range(1,12), accuracy_rate, color='blue', linestyle='dashed', marker='o',
    markerfacecolor='red', markersize=10)
accuracy_plot = plt.title('Accuracy Rate vs. K Value')
accuracy_plot = plt.xlabel('N_neighbors')
accuracy_plot = plt.ylabel('Accuracy Rate')

"""**Is accuracy a suitable metric for evaluating performance in this problem?**

No, Accuracy is generally not a good metric for evaluating model performance on highly imbalanced datasets. This is because accuracy measures the proportion of correct predictions out of all predictions, and in the case of imbalanced datasets, it can be misleading. If the majority class is much larger than the minority class, a model could achieve high accuracy simply by always predicting the majority class, but it would fail to capture the performance on the minority class.

Achieving high recall is crucial for this problem, Balance the dataset classes is the best way to handle such problems.
"""

knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_train, y_train)
pred = knn.predict(X_test)
print("K = 3  &  Accuracy Score",accuracy_score(y_test, pred))
cm = confusion_matrix(y_test,pred)
plt.subplots(figsize = (10,6))
sns.heatmap(cm ,annot =True , cmap="Blues", fmt = 'g')
plt.xlabel("Predicition")
plt.ylabel("Actual")
plt.title("confusion matrix")
plt.show()
print(roc_auc_score(y_test, pred))
RocCurveDisplay.from_predictions(y_test, pred)
plt.show()

X_train_s, X_test_s = standardize_features(X_train, X_test)
X_train_s_b, y_train_b = dataset_balancement(X_train_s, y_train)

knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_train_s_b, y_train_b)
pred_s_b = knn.predict(X_test_s)
print("K = 3  &  Accuracy Score",accuracy_score(y_test, pred_s_b))
cm = confusion_matrix(y_test,pred_s_b)
plt.subplots(figsize = (10,6))
sns.heatmap(cm ,annot =True , cmap="Blues", fmt = 'g')
plt.xlabel("Predicition")
plt.ylabel("Actual")
plt.title("confusion matrix")
plt.show()
print(roc_auc_score(y_test, pred_s_b))
RocCurveDisplay.from_predictions(y_test, pred_s_b)
plt.show()
print("Classification Report:")
print(classification_report(y_test, pred_s_b))

k_values = range(1, 20)
recall_scores = []

for k in k_values:
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_train_s_b, y_train_b)
    y_preds = knn.predict(X_test_s)
    recall = recall_score(y_test, y_preds)
    recall_scores.append(recall)

# Plotting Recall for different values of k
plt.figure(figsize=(10, 6))
plt.plot(k_values, recall_scores, marker='o', linestyle='-', color='b')
plt.title('kNN Classification Recall for Different k Values')
plt.xlabel('Number of Neighbors (k)')
plt.ylabel('Recall')
plt.xticks(k_values)
plt.grid(True)
plt.show()

knn = KNeighborsClassifier(n_neighbors=7)
knn.fit(X_train_s_b, y_train_b)
pred_s_b = knn.predict(X_test_s)
print("K = 7  &  Accuracy Score",accuracy_score(y_test, pred_s_b))
cm = confusion_matrix(y_test,pred_s_b)
plt.subplots(figsize = (10,6))
sns.heatmap(cm ,annot =True , cmap="Blues", fmt = 'g')
plt.xlabel("Predicition")
plt.ylabel("Actual")
plt.title("confusion matrix")
plt.show()
print(roc_auc_score(y_test, pred_s_b))
RocCurveDisplay.from_predictions(y_test, pred_s_b)
plt.show()
print("Classification Report:")
print(classification_report(y_test, pred_s_b))

knn = KNeighborsClassifier(n_neighbors=11)
knn.fit(X_train_s_b, y_train_b)
pred_s_b = knn.predict(X_test_s)
print("K = 11  &  Accuracy Score",accuracy_score(y_test, pred_s_b))
cm = confusion_matrix(y_test,pred_s_b)
plt.subplots(figsize = (10,6))
sns.heatmap(cm ,annot =True , cmap="Blues", fmt = 'g')
plt.xlabel("Predicition")
plt.ylabel("Actual")
plt.title("confusion matrix")
plt.show()
print(roc_auc_score(y_test, pred_s_b))
RocCurveDisplay.from_predictions(y_test, pred_s_b)
plt.show()
print("Classification Report:")
print(classification_report(y_test, pred_s_b))

X_new_train, X_new_test, y_new_train, y_new_test = train_test_split(X_new, y_new, test_size=0.3, random_state=42, stratify=y)

knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_new_train, y_new_train)
pred_new = knn.predict(X_new_test)
print("K = 3  &  Accuracy Score",accuracy_score(y_new_test, pred_new))
cm = confusion_matrix(y_new_test,pred_new)
plt.subplots(figsize = (10,6))
sns.heatmap(cm ,annot =True , cmap="Blues", fmt = 'g')
plt.xlabel("Predicition")
plt.ylabel("Actual")
plt.title("confusion matrix")
plt.show()
print(roc_auc_score(y_new_test, pred_new))
RocCurveDisplay.from_predictions(y_new_test, pred_new)
plt.show()
print("Classification Report:")
print(classification_report(y_new_test, pred_new))

X_new_train, X_new_test, y_new_train, y_new_test = train_test_split(X_new, y_new, test_size=0.3, random_state=42)

X_new_train_s, X_new_test_s = standardize_features(X_new_train, X_new_test)
X_new_train_s_b, y_new_train_b = dataset_balancement(X_new_train_s, y_new_train)

knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X_new_train_s_b, y_new_train_b)
pred_new_s_b = knn.predict(X_new_test_s)
print("K = 3  &  Accuracy Score",accuracy_score(y_new_test, pred_new_s_b))
cm = confusion_matrix(y_new_test,pred_new_s_b)
plt.subplots(figsize = (10,6))
sns.heatmap(cm ,annot =True , cmap="Blues", fmt = 'g')
plt.xlabel("Predicition")
plt.ylabel("Actual")
plt.title("confusion matrix")
plt.show()
print(roc_auc_score(y_new_test, pred_new_s_b))
RocCurveDisplay.from_predictions(y_new_test, pred_new_s_b)
plt.show()
print("Classification Report:")
print(classification_report(y_new_test, pred_new_s_b))

k_values = range(1, 20)
recall_scores = []

for k in k_values:
    knn = KNeighborsClassifier(n_neighbors=k)
    knn.fit(X_new_train_s_b, y_new_train_b)
    y_pred = knn.predict(X_new_test_s)
    recall = recall_score(y_new_test, y_pred)
    recall_scores.append(recall)

# Plotting Recall for different values of k
plt.figure(figsize=(10, 6))
plt.plot(k_values, recall_scores, marker='o', linestyle='-', color='b')
plt.title('kNN Classification Recall for Different k Values')
plt.xlabel('Number of Neighbors (k)')
plt.ylabel('Recall')
plt.xticks(k_values)
plt.grid(True)
plt.show()

knn = KNeighborsClassifier(n_neighbors=9)
knn.fit(X_new_train_s_b, y_new_train_b)
pred_new_s_b = knn.predict(X_new_test_s)
print("K = 9  &  Accuracy Score",accuracy_score(y_new_test, pred_new_s_b))
cm = confusion_matrix(y_new_test,pred_new_s_b)
plt.subplots(figsize = (10,6))
sns.heatmap(cm ,annot =True , cmap="Blues", fmt = 'g')
plt.xlabel("Predicition")
plt.ylabel("Actual")
plt.title("confusion matrix")
plt.show()
print(roc_auc_score(y_new_test, pred_new_s_b))
RocCurveDisplay.from_predictions(y_new_test, pred_new_s_b)
plt.show()
print("Classification Report:")
print(classification_report(y_new_test, pred_new_s_b))

"""# **Classification with Decision Trees**"""

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn import metrics
from sklearn.tree import export_graphviz
import graphviz
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score, RocCurveDisplay, classification_report

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

clf = DecisionTreeClassifier(criterion='entropy', max_depth=3)
clf.fit(X, y)


dot_data = export_graphviz(
    clf,
    feature_names= X_train.columns,
    class_names=['0', '1'],
    filled=True,
    rounded=True,
    proportion=False
)

graph = graphviz.Source(dot_data)
graph.render(filename="decision_tree", format="png", cleanup=True)
graph.view()
graph

clf = DecisionTreeClassifier(criterion='entropy')
clf.fit(X, y)

dot_data = export_graphviz(
    clf,
    feature_names= X_train.columns,
    class_names=['0', '1'],
    filled=True,
    rounded=True,
    proportion=False
)

graph = graphviz.Source(dot_data)
graph.render(filename="decision_tree", format="png", cleanup=True)
graph.view()
graph

clf_id3 = DecisionTreeClassifier(criterion='entropy')
clf_id3.fit(X_train, y_train)
y_pred_id3 = clf_id3.predict(X_test)

print("Classifire = id3  &  Accuracy Score",accuracy_score(y_test, y_pred_id3))
cm = confusion_matrix(y_test, y_pred_id3)
plt.subplots(figsize = (10,6))
sns.heatmap(cm ,annot =True , cmap="Blues", fmt = 'g')
plt.xlabel("Predicition")
plt.ylabel("Actual")
plt.title("confusion matrix")
plt.show()
print(roc_auc_score(y_test, y_pred_id3))
RocCurveDisplay.from_predictions(y_test, y_pred_id3)
plt.show()
print("Classification Report:")
print(classification_report(y_test, y_pred_id3))

clf_c45 = DecisionTreeClassifier(criterion='gini')
clf_c45.fit(X_train, y_train)
y_pred_c45 = clf_c45.predict(X_test)

print("Classifire = c4.5  &  Accuracy Score",accuracy_score(y_test, y_pred_c45))
cm = confusion_matrix(y_test, y_pred_c45)
plt.subplots(figsize = (10,6))
sns.heatmap(cm ,annot =True , cmap="Blues", fmt = 'g')
plt.xlabel("Predicition")
plt.ylabel("Actual")
plt.title("confusion matrix")
plt.show()
print(roc_auc_score(y_test, y_pred_c45))
RocCurveDisplay.from_predictions(y_test, y_pred_c45)
plt.show()
print("Classification Report:")
print(classification_report(y_test, y_pred_c45))

"""# **Classifying with processed data**"""

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

X_train_s, X_test_s = standardize_features(X_train, X_test)
X_train_s_b, y_train_b = dataset_balancement(X_train_s, y_train)

clf_id3 = DecisionTreeClassifier(criterion='entropy')
clf_id3.fit(X_train_s_b, y_train_b)
y_pred_s_b = clf_id3.predict(X_test_s)

print("Classifire = id3  &  Accuracy Score",accuracy_score(y_test, y_pred_s_b))
cm = confusion_matrix(y_test, y_pred_s_b)
plt.subplots(figsize = (10,6))
sns.heatmap(cm ,annot =True , cmap="Blues", fmt = 'g')
plt.xlabel("Predicition")
plt.ylabel("Actual")
plt.title("confusion matrix")
plt.show()
print(roc_auc_score(y_test, y_pred_s_b))
RocCurveDisplay.from_predictions(y_test, y_pred_s_b)
plt.show()
print("Classification Report:")
print(classification_report(y_test, y_pred_s_b))

clf_c45 = DecisionTreeClassifier(criterion='gini')
clf_c45.fit(X_train_s_b, y_train_b)
y_pred_s_b_c45 = clf_c45.predict(X_test_s)

print("Classifire = c4.5  &  Accuracy Score",accuracy_score(y_test, y_pred_s_b_c45))
cm = confusion_matrix(y_test, y_pred_s_b_c45)
plt.subplots(figsize = (10,6))
sns.heatmap(cm ,annot =True , cmap="Blues", fmt = 'g')
plt.xlabel("Predicition")
plt.ylabel("Actual")
plt.title("confusion matrix")
plt.show()
print(roc_auc_score(y_test, y_pred_s_b_c45))
RocCurveDisplay.from_predictions(y_test, y_pred_s_b_c45)
plt.show()
print("Classification Report:")
print(classification_report(y_test, y_pred_s_b_c45))

"""# **Random Forest**"""

from sklearn.ensemble import RandomForestClassifier

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
rf_classifier.fit(X_train, y_train)
y_pred_rf = rf_classifier.predict(X_test)

print("Classifire = RandomForest  &  Accuracy Score",accuracy_score(y_test, y_pred_rf))
cm = confusion_matrix(y_test, y_pred_rf)
plt.subplots(figsize = (10,6))
sns.heatmap(cm ,annot =True , cmap="Blues", fmt = 'g')
plt.xlabel("Predicition")
plt.ylabel("Actual")
plt.title("confusion matrix")
plt.show()
print(roc_auc_score(y_test, y_pred_rf))
RocCurveDisplay.from_predictions(y_test, y_pred_rf)
plt.show()
print("Classification Report:")
print(classification_report(y_test, y_pred_rf))

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
X_train_s, X_test_s = standardize_features(X_train, X_test)
X_train_s_b, y_train_b = dataset_balancement(X_train_s, y_train)

rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
rf_classifier.fit(X_train_s_b, y_train_b)
y_pred_s_b_rf = rf_classifier.predict(X_test_s)

print("Classifire = RandomForest  &  Accuracy Score",accuracy_score(y_test, y_pred_s_b_rf))
cm = confusion_matrix(y_test, y_pred_s_b_rf)
plt.subplots(figsize = (10,6))
sns.heatmap(cm ,annot =True , cmap="Blues", fmt = 'g')
plt.xlabel("Predicition")
plt.ylabel("Actual")
plt.title("confusion matrix")
plt.show()
print(roc_auc_score(y_test, y_pred_s_b_rf))
RocCurveDisplay.from_predictions(y_test, y_pred_s_b_rf)
plt.show()
print("Classification Report:")
print(classification_report(y_test, y_pred_s_b_rf))

"""# **Classifying with different Depth**"""

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

clf_id3 = DecisionTreeClassifier(criterion='entropy', max_depth=3)
clf_id3.fit(X_train, y_train)
y_pred_id3 = clf_id3.predict(X_test)

print("Classifire = id3  &  Accuracy Score",accuracy_score(y_test, y_pred_id3))
cm = confusion_matrix(y_test, y_pred_id3)
plt.subplots(figsize = (10,6))
sns.heatmap(cm ,annot =True , cmap="Blues", fmt = 'g')
plt.xlabel("Predicition")
plt.ylabel("Actual")
plt.title("confusion matrix")
plt.show()
print(roc_auc_score(y_test, y_pred_id3))
RocCurveDisplay.from_predictions(y_test, y_pred_id3)
plt.show()
print("Classification Report:")
print(classification_report(y_test, y_pred_id3))

clf_c45 = DecisionTreeClassifier(criterion='gini', max_depth=7)
clf_c45.fit(X_train, y_train)
y_pred_c45 = clf_c45.predict(X_test)

print("Classifire = c4.5  &  Accuracy Score",accuracy_score(y_test, y_pred_c45))
cm = confusion_matrix(y_test, y_pred_c45)
plt.subplots(figsize = (10,6))
sns.heatmap(cm ,annot =True , cmap="Blues", fmt = 'g')
plt.xlabel("Predicition")
plt.ylabel("Actual")
plt.title("confusion matrix")
plt.show()
print(roc_auc_score(y_test, y_pred_c45))
RocCurveDisplay.from_predictions(y_test, y_pred_c45)
plt.show()
print("Classification Report:")
print(classification_report(y_test, y_pred_c45))

"""# **Classifying with processed data**"""

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

X_train_s, X_test_s = standardize_features(X_train, X_test)
X_train_s_b, y_train_b = dataset_balancement(X_train_s, y_train)

clf_id3 = DecisionTreeClassifier(criterion='entropy', max_depth=3)
clf_id3.fit(X_train_s_b, y_train_b)
y_pred_s_b = clf_id3.predict(X_test_s)

print("Classifire = id3  &  Accuracy Score",accuracy_score(y_test, y_pred_s_b))
cm = confusion_matrix(y_test, y_pred_s_b)
plt.subplots(figsize = (10,6))
sns.heatmap(cm ,annot =True , cmap="Blues", fmt = 'g')
plt.xlabel("Predicition")
plt.ylabel("Actual")
plt.title("confusion matrix")
plt.show()
print(roc_auc_score(y_test, y_pred_s_b))
RocCurveDisplay.from_predictions(y_test, y_pred_s_b)
plt.show()
print("Classification Report:")
print(classification_report(y_test, y_pred_s_b))

clf_c45 = DecisionTreeClassifier(criterion='gini', max_depth=7)
clf_c45.fit(X_train_s_b, y_train_b)
y_pred_s_b_c45 = clf_c45.predict(X_test_s)

print("Classifire = c4.5  &  Accuracy Score",accuracy_score(y_test, y_pred_s_b_c45))
cm = confusion_matrix(y_test, y_pred_s_b_c45)
plt.subplots(figsize = (10,6))
sns.heatmap(cm ,annot =True , cmap="Blues", fmt = 'g')
plt.xlabel("Predicition")
plt.ylabel("Actual")
plt.title("confusion matrix")
plt.show()
print(roc_auc_score(y_test, y_pred_s_b_c45))
RocCurveDisplay.from_predictions(y_test, y_pred_s_b_c45)
plt.show()
print("Classification Report:")
print(classification_report(y_test, y_pred_s_b_c45))

"""# **Random Forest**"""

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=9)
rf_classifier.fit(X_train, y_train)
y_pred_rf = rf_classifier.predict(X_test)

print("Classifire = RandomForest  &  Accuracy Score",accuracy_score(y_test, y_pred_rf))
cm = confusion_matrix(y_test, y_pred_rf)
plt.subplots(figsize = (10,6))
sns.heatmap(cm ,annot =True , cmap="Blues", fmt = 'g')
plt.xlabel("Predicition")
plt.ylabel("Actual")
plt.title("confusion matrix")
plt.show()
print(roc_auc_score(y_test, y_pred_rf))
RocCurveDisplay.from_predictions(y_test, y_pred_rf)
plt.show()
print("Classification Report:")
print(classification_report(y_test, y_pred_rf))

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
X_train_s, X_test_s = standardize_features(X_train, X_test)
X_train_s_b, y_train_b = dataset_balancement(X_train_s, y_train)

rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=9)
rf_classifier.fit(X_train_s_b, y_train_b)
y_pred_s_b_rf = rf_classifier.predict(X_test_s)

print("Classifire = RandomForest  &  Accuracy Score",accuracy_score(y_test, y_pred_s_b_rf))
cm = confusion_matrix(y_test, y_pred_s_b_rf)
plt.subplots(figsize = (10,6))
sns.heatmap(cm ,annot =True , cmap="Blues", fmt = 'g')
plt.xlabel("Predicition")
plt.ylabel("Actual")
plt.title("confusion matrix")
plt.show()
print(roc_auc_score(y_test, y_pred_s_b_rf))
RocCurveDisplay.from_predictions(y_test, y_pred_s_b_rf)
plt.show()
print("Classification Report:")
print(classification_report(y_test, y_pred_s_b_rf))

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
X_train_s, X_test_s = standardize_features(X_train, X_test)
X_train_s_b, y_train_b = dataset_balancement(X_train_s, y_train)

from sklearn.metrics import precision_score, recall_score

depth = range(1, 30)
precision_scores = []
recall_scores = []

for d in depth:
    clf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=d)
    clf.fit(X_train_s_b, y_train_b)
    y_pred = clf.predict(X_test_s)
    precision = precision_score(y_test, y_pred)
    precision_scores.append(precision)
    recall = recall_score(y_test, y_pred)
    recall_scores.append(recall)

# Plotting Precision
plt.figure(figsize=(10, 6))
plt.plot(depth, precision_scores, marker='o', linestyle='-', color='b')
plt.title('Random Forest Classification Precision for Different depth')
plt.xlabel('Max_Depth (d)')
plt.ylabel('Precision')
plt.xticks(depth)
plt.grid(True)
plt.show()

# Plotting Recall
plt.figure(figsize=(10, 6))
plt.plot(depth, recall_scores, marker='x', linestyle='-', color='r')
plt.title('Random Forest Classification Recall for Different depth')
plt.xlabel('Max_Depth (d)')
plt.ylabel('Recall')
plt.xticks(depth)
plt.grid(True)
plt.show()

plt.figure(figsize=(10, 6))
plt.plot(depth, precision_scores, marker='o', linestyle='-', color='b', label='Precision')
plt.plot(depth, recall_scores, marker='x', linestyle='-', color='r', label='Recall')
plt.title('Precision Vs Recall for Random Forest')
plt.xlabel('Max Depth (d)')
plt.ylabel('Scores')
plt.xticks(depth)
plt.grid(True)
plt.legend()
plt.show()

rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=8)
rf_classifier.fit(X_train_s_b, y_train_b)
y_pred_s_b_rf = rf_classifier.predict(X_test_s)

print("Classifire = RandomForest  &  Accuracy Score",accuracy_score(y_test, y_pred_s_b_rf))
cm = confusion_matrix(y_test, y_pred_s_b_rf)
plt.subplots(figsize = (10,6))
sns.heatmap(cm ,annot =True , cmap="Blues", fmt = 'g')
plt.xlabel("Predicition")
plt.ylabel("Actual")
plt.title("confusion matrix")
plt.show()
print(roc_auc_score(y_test, y_pred_s_b_rf))
RocCurveDisplay.from_predictions(y_test, y_pred_s_b_rf)
plt.show()
print("Classification Report:")
print(classification_report(y_test, y_pred_s_b_rf))

from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline, make_pipeline

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
X_train_s, X_test_s = standardize_features(X_train, X_test)

model = make_pipeline(
    RandomUnderSampler(random_state=42, sampling_strategy='majority'),
    #SMOTE(random_state=42),
    RandomForestClassifier(n_estimators=100, random_state=42, max_depth=8)
)

model.fit(X_train_s, y_train)
pred_s = model.predict(X_test_s)

print("Classifire = RandomForest  &  Accuracy Score",accuracy_score(y_test, pred_s))
cm = confusion_matrix(y_test, pred_s)
plt.subplots(figsize = (10,6))
sns.heatmap(cm ,annot =True , cmap="Blues", fmt = 'g')
plt.xlabel("Predicition")
plt.ylabel("Actual")
plt.title("confusion matrix")
plt.show()
print(roc_auc_score(y_test, pred_s))
RocCurveDisplay.from_predictions(y_test, pred_s)
plt.show()
print("Classification Report:")
print(classification_report(y_test, pred_s))