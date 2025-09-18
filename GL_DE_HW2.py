#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report


# -----------------------------
# Data Loading & Cleaning
# -----------------------------

def load_dataset(path: str) -> pd.DataFrame:
    """Load the Excel dataset."""
    return pd.read_excel(path)


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Clean common data entry issues."""
    df = df.copy()
    df['contact'] = df['contact'].replace('telephonee', 'telephone')
    df['day_of_week'] = df['day_of_week'].replace('fr', 'fri')
    return df


def drop_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Drop missing values."""
    return df.dropna()


# -----------------------------
# Basic Summaries
# -----------------------------

def summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Return median summary stats by y."""
    return df.groupby("y")[
        ['age', 'duration', 'pdays', 'previous',
         'emp.var.rate', 'cons.price.idx', 'cons.conf.idx',
         'euribor3m', 'nr.employed']
    ].median()


def value_counts(df: pd.DataFrame, col: str) -> pd.Series:
    """Return counts for a categorical column."""
    return df[col].value_counts()


# -----------------------------
# Visualization Functions
# -----------------------------

def plot_pie_charts(df: pd.DataFrame) -> None:
    """Plot pie charts for job, marital, education, and weekday."""
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))

    for ax, col, title in zip(
        axs.ravel(),
        ["job", "marital", "education", "day_of_week"],
        ["Jobs", "Marital Status", "Education", "Weekday Campaigns"]
    ):
        vals = df[col].value_counts()
        axs_dict = ax.pie(vals, labels=vals.index, autopct='%1.2f%%')
        ax.set_title(f"Distribution of {title}")

    plt.tight_layout()
    plt.show()


def plot_bar_charts(df: pd.DataFrame) -> None:
    """Plot bar charts for default, housing, loan, poutcome."""
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    sns.countplot(x="default", data=df, order=["yes", "no", "unknown"], ax=axs[0, 0])
    sns.countplot(x="housing", data=df, order=["yes", "no", "unknown"], ax=axs[1, 0])
    sns.countplot(x="loan", data=df, order=["yes", "no", "unknown"], ax=axs[0, 1])
    sns.countplot(x="poutcome", data=df, order=["success", "failure", "nonexistent"], ax=axs[1, 1])
    plt.tight_layout()
    plt.show()


def plot_boxplots(df: pd.DataFrame) -> None:
    """Plot boxplots for numeric columns."""
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    axs[0, 0].boxplot(df['duration']); axs[0, 0].set_title("Duration")
    axs[1, 0].boxplot(df['campaign']); axs[1, 0].set_title("Campaign Contacts")
    axs[0, 1].boxplot(df['pdays']); axs[0, 1].set_title("Days Since Contact")
    axs[1, 1].boxplot(df['previous']); axs[1, 1].set_title("Previous Contacts")
    plt.tight_layout()
    plt.show()


# -----------------------------
# Modeling Functions
# -----------------------------

def prepare_model_data(df: pd.DataFrame):
    """Prepare X, y for modeling with one-hot encoding."""
    df = df[df['age'] != 311]  # remove outlier
    df_encoded = pd.get_dummies(df, columns=[
        'job', 'marital', 'education', 'default',
        'loan', 'contact', 'month', 'day_of_week', 'poutcome', 'y'
    ])
    X = df_encoded.drop(columns=['y_no', 'y_yes', 'IDX', 'housing'], errors="ignore")
    y = df_encoded['y_yes']
    return train_test_split(X, y, test_size=0.2, random_state=42)


def train_knn(X_train, y_train, k: int = 10) -> KNeighborsClassifier:
    """Train KNN model with given k."""
    model = KNeighborsClassifier(n_neighbors=k)
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test):
    """Evaluate model accuracy and return metrics."""
    X_test = np.ascontiguousarray(X_test)
    y_pred = model.predict(X_test)
    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "confusion_matrix": confusion_matrix(y_test, y_pred),
        "classification_report": classification_report(y_test, y_pred)
    }


def tune_knn(X_train, y_train):
    param_grid = {"n_neighbors": list(range(1, 11))}
    
    # find the smallest class size
    min_class_size = np.min(np.bincount(y_train))
    cv = min(5, len(y_train), min_class_size)
    if cv < 2:
        cv = 2  # fallback so GridSearchCV still runs
    
    grid = GridSearchCV(KNeighborsClassifier(), param_grid, cv=cv)
    grid.fit(X_train, y_train)
    return {"best_k": grid.best_params_["n_neighbors"], "best_score": grid.best_score_}


# -----------------------------
# Main Entry Point
# -----------------------------

def main():
    df = load_dataset("bank-additional-full.xlsx")
    df = clean_dataset(df)
    sub_df = drop_missing(df)

    print("Summary Stats:\n", summary_statistics(df))
    print("\nJob Counts:\n", value_counts(df, "job"))

    # Modeling
    X_train, X_test, y_train, y_test = prepare_model_data(sub_df)
    model = train_knn(X_train, y_train, k=10)
    results = evaluate_model(model, X_test, y_test)
    print("\nKNN Results:\n", results)


if __name__ == "__main__":
    main()
