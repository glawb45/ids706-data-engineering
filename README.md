# Wines Dataset Manipulation using PySpark

## 1. Data Processing Pipeline

For this assignment, I used the Red Wine quality dataset directly through databricks. I accessed it using the following file path:

```bash
path = "dbfs:/databricks-datasets/wine-quality/winequality-red.csv"


start = time.time()

df_spark = spark.read.csv(path, header=True, inferSchema=True, sep=";")
```

I initially ran into some issues reading in the data, as it was reading as a CSV rather than a table, so I had to remember to put the separator as a semicolon to distinguish attributes in the table as well.