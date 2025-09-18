import unittest
import pandas as pd
import numpy as np
from GL_DE_HW2 import (
    clean_dataset, drop_missing, summary_statistics,
    prepare_model_data, train_knn, evaluate_model, tune_knn
)


class TestDataEngineering(unittest.TestCase):

    def test_clean_dataset(self):
        df = pd.DataFrame({"contact": ["telephonee", "cell"], "day_of_week": ["fr", "mon"]})
        cleaned = clean_dataset(df)
        self.assertNotIn("telephonee", cleaned["contact"].values)
        self.assertNotIn("fr", cleaned["day_of_week"].values)

    def test_drop_missing(self):
        df = pd.DataFrame({"a": [1, np.nan, 2]})
        dropped = drop_missing(df)
        self.assertEqual(dropped.shape[0], 2)

    def test_summary_statistics(self):
        df = pd.DataFrame({
            "y": ["yes", "no", "yes"],
            "age": [30, 40, 50],
            "duration": [100, 200, 300],
            "pdays": [1, 2, 3],
            "previous": [0, 1, 2],
            "emp.var.rate": [0.1, 0.2, 0.3],
            "cons.price.idx": [93, 94, 95],
            "cons.conf.idx": [-40, -42, -41],
            "euribor3m": [4.5, 4.2, 4.3],
            "nr.employed": [5000, 5100, 5200]
        })
        summary = summary_statistics(df)
        self.assertIn("age", summary.columns)

    def test_modeling_pipeline(self):
        df = pd.DataFrame({
            "age": [30, 40, 50, 60],
            "duration": [100, 200, 150, 120],
            "campaign": [1, 2, 1, 3],
            "pdays": [10, 20, 30, 40],
            "previous": [0, 1, 0, 1],
            "nr.employed": [5000, 5100, 5200, 5300],
            "emp.var.rate": [0.1, 0.2, 0.3, 0.4],
            "cons.price.idx": [93, 94, 95, 96],
            "cons.conf.idx": [-40, -42, -41, -39],
            "euribor3m": [4.5, 4.2, 4.3, 4.4],
            "job": ["admin.", "blue-collar", "student", "admin."],
            "marital": ["married", "single", "divorced", "married"],
            "education": ["basic.4y", "high.school", "university.degree", "illiterate"],
            "default": ["no", "unknown", "no", "yes"],
            "loan": ["no", "yes", "no", "no"],
            "contact": ["cellular", "telephone", "cellular", "cellular"],
            "month": ["may", "jun", "jul", "aug"],
            "day_of_week": ["mon", "tue", "wed", "thu"],
            "poutcome": ["failure", "nonexistent", "success", "failure"],
            "y": ["yes", "no", "yes", "no"]
        })

        X_train, X_test, y_train, y_test = prepare_model_data(df)
        model = train_knn(X_train, y_train, k=2)
        results = evaluate_model(model, X_test, y_test)
        self.assertIn("accuracy", results)
        self.assertIsInstance(results["accuracy"], float)

        tuning = tune_knn(X_train, y_train)
        self.assertIn("best_k", tuning)


if __name__ == "__main__":
    unittest.main()