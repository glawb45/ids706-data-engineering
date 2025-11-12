# Wines Dataset Manipulation using PySpark

For this assignment, I followed the same outline we were taught in class, so some of the assignment details may be out of order.

## 1. Data Processing Pipeline

For this assignment, I used the Red Wine quality dataset directly through databricks. I accessed it using the following file path:

```bash
path = "dbfs:/databricks-datasets/wine-quality/winequality-red.csv"


start = time.time()

df_spark = spark.read.csv(path, header=True, inferSchema=True, sep=";")
```

I initially ran into some issues reading in the data, as it was reading as a CSV rather than a table, so I had to remember to put the separator as a semicolon to distinguish attributes in the table as well.

I used several data analytical functions, including `.groupBy`, `.filter`, `.withColumn` and used left joins with a small dataset I created on my own.

I also used `.repartition` to partition my queries, which seemingly provided better performance, as can be seen in the notebook.

```bash
# Repartition to different sizes
print("Testing different partition strategies...\n")

# Fewer partitions (4)
df_few = df_large.repartition(2)
start = time.time()
df_few.filter(col('quality') > 5).count()
few_time = time.time() - start
print(f"✓ Fewer partitions (4): {few_time:.2f}s")

```

## 2. Performance Analysis

I used the `.explain` function on a sample query to show the full path I had for this:

```bash

df_exp = df_large.filter(col('chlorides') > 0.1) \
    .groupBy('quality') \
    .count() \
    .orderBy(desc('count')) \
    .limit(10)

df_exp.explain()

```

![Shuffle Path](SS/Path_1.png)
![Shuffle Path 2](SS/Path_2.png)