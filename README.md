# Data Analysis

Below are the containers and files we would like to add to our repository:

A virtual environment setup for dependency management. \
A devcontainer configuration for GitHub Codespaces\
A Python Jupyter Notebook.\
GitHub Actions for continuous integration to automate linting and testing.\
Github Copilot for AI-assisted coding.
A docker file to use globally if needed.

[![Python Template for IDS706](https://github.com/glawb45/ids706-data-engineering/actions/workflows/main.yml/badge.svg?branch=data-analysis)](https://github.com/glawb45/ids706-data-engineering/actions/workflows/main.yml)

### Goal

The goal of this project is to perform basic data analysis using a banking dataset. We will start with EDA, including designing visualizations, and make a machine learning model to predict whether a customer will default on their credit or not.

## Create a New GitHub Repository

1. We can simply clone our previous repository from ids706-data-engineering and make a new branch
2. We will not need a script nor test cases for data analysis, so we will only work out of our Notebook.

## Setup Python Environment (if you're not using a Dev Container)

If you're working outside of a dev container, you can manually create and activate a virtual environment. If you do so, for consistency, it's recommended to name the environment the same as your repository.

```bash
python3 -m venv ~/.IDS706_python_template
source ~/.IDS706_python_template/bin/activate
```

## Create a Makefile

```bash
install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

format:
	black *.py

lint:
	flake8 hello.py

test:
	python -m pytest -vv --cov=hello test_hello.py

clean:
    rm -rf __pycache__ .pytest_cache .coverage

all: install format lint test

```

## Create a requirements.txt file

```bash
pylint
flake8
pytest
click
black
pytest-cov
numpy
pandas
seaborn
matplotlib
scikit-learn
```

## Create a docker file
```bash
docker build -t <image_name> .
docker run -d -p --name <container_name> <image_name>
```

This will create a docker file to be used globally and contain both the image and container name.


![Docker file and port created](Docker.png)


## VS Code Dev Containers (Suggested)

Open a sample in a container by pressing shift+command+P, then select Dev Containers: Add Development Container Configuration Files.... Choose the Python 3.11 template, and it will create the necessary files for you.

#### Rebuild or update your container
After you make changes to your container, such as installing a packages, you'll rebuild your container for your changes to take effect. by pressing shift+command+P, then select Dev Containers: Rebuild Container or Codespaces: Rebuild Container command so the modifications are picked up.

## Run the Makefile (required if you do not use Dev Containers)

```bash
make install
```

## Create a Jupyter Notebook + Modifications

### 1. Load the dataset
```bash
bank = pd.read_excel('bank-additional-full.xlsx')
bank.head().T
bank.describe()
bank.info()
```

I think one important point that I can see is missing is the year is not represented — if someone were to sort by month, all the "May" values would be arranged together and the user would then assume all these values were from the same year.

Personally, some important predictors of y, without performing an in-depth data analysis, include job and marital status because those could both determine if and when someone has the funds to invest money (and jointly with spouses). Average yearly balance obviously is probably the biggest predictor, but also if there is a default credit balance and if the person has taken a personal loan.

Other important predictors for y include the number of contacts in this campaign and those that have been performed before and for this particular client.

### 2. Provide basic statistics for the attribute

```bash
bank['marital'].value_counts() # ex. marital status counts
```

Doing a slightly deeper dive — i.e. looking at the most basic summary statistics — we see that the average age for a client was roughly 40 years old. However, here we see an outlier which is probabbly a mistake in the input of data: there is no way anyone is 311 years old, which seems like a human input error because there is only value of this value. The 112 age seems very much an outlier as well, but at least still a possible value.

The average duration of the last call to the client was roughly 4 minutes, 20 seconds long. The number of campaigns performed for a single client during a single campaign on average was a little less than 3 — it doesn't seem plausible, unless it was someone extremely famous that 56 methods of contact would be performed in a single campaign, but this is not really even an outlier given other data. The average number of previous campaigns for a single client was roughly less than 1, meaning more clients were not marketed to than were.

Average number of days that passed between contacts was 962. The employee variation rate was roughly 0.08 — this is good because this means there is low employee turnover.

The consumer indices can go into the negatives, meaning those metrics are bad for business likely — the price index is fine, but the confidence index is much lower than where we want it to be. Considering the max does not eclipse even zero, there is something that we need to do better in marketing or in our product as a whole.

European banks on average will lend each other money at a 3.6% interest rate, and at most 5%. That value relatively should be high considering it's coming from banks.

The number of employed individuals at most was 5,228 but on average stayed in the mid-5,100 range.

In terms of jobs, administrators and blue-collar workers led the way. Most clients were married and had some sort of university degree.

Most people did not have default credit. Most people took housing loans but not personal loans.

It makes sense that most people were contacted by cellphone rather than landline/telephone.

We need to perform more analyses for success rate correlating to day and month, but it seemed most campaigns were marketed on Thursdays or Mondays in May.

Many marketing campaigns didn't have an outcome at all — for a bank, this should be viewed as a failure unless those campaigns are still ongoing. It also makes sense that there were more failures than successes with those campaigns. On the same note, there were about 9x less time deposits than the opposite.

### 3. Visualizations

My approach here was to make a new dataset without the missing values from the original dataset. I then want to make pie charts for marital status, job and education in relation to the clients, and then make another for most "successful" marketing month.

```bash
# Example of one pie plot
sub_bank = bank
sub_bank = sub_bank.dropna()

# Create 2x2 data matrix
fig, axs = plt.subplots(2, 2, figsize=(15, 10))

# Job pie chart

job_cat = sub_bank['job'].unique()
job_val = sub_bank['job'].value_counts()

axs[0,0].pie(job_val, labels=job_cat, autopct='%1.2f%%')
axs[0,0].set_title('Distribution of clients\' jobs')
```

We first cleaned the data slightly so we were able to negate missing data points.

In the first case with jobs, the clients who were mainly contacted were in the services industry, or were housemaids or administrators. It was rare that students and entrepreneurs were contacted.

In terms of clients' marital statuses, over 60% were married, while just under 30% were single and the mostly remaining 11% were previously married.

Most clients contacted had attended a basic four-year college, but only 4% of all had a university degree. Twenty-three percent of those contacted had a high school diploma. Less than 0.05% of clients contacted were illiterate — perhaps those constitute the very young population (there was one 5 year old, but how can we determine who is making up the other part of the percentage?).

Finally, in terms of weekdays, let's say that the bank found out that one day in particular generated the most success and/or we had the most time that day. That most successful and perhaps most time-consuming day would have been Monday, followed by Tuesday. Throughout the week, it is obvious either we were having less success or we were getting decreasingly motivated to fulfill our jobs because the distribution of campaigns lessened as the week went on.

```bash
# Create 2x2 data matrix
fig, axs = plt.subplots(2, 2, figsize=(15, 10))

# Default Credit Bar Chart

sns.countplot(x="default", data=sub_bank, order=["yes", "no", "unknown"], ax=axs[0, 0])
axs[0, 0].set_title("Marketing Strategies: Default Credit")
axs[0, 0].set_xlabel("Does a customer have previous default credit?")
axs[0, 0].set_ylabel("Count")
```

With respect to some of our actual marketing strategies — I apologize because I was unable to put these into pairwise plots like the ones below — it was rare that any customers had a default credit in their bank account. It was also rare that a customer had taken out a personal loan, but was seemed very common that they would take out housing loans.

Most clients were contacted via cell, while others were contacted via telephone.

Altogether, there was a very low number of successful campaigns, while there weren't many more failures (relatively). There was a large number of nonexistent campaigns, however, telling us that either these campaigns were never even started with the customer or they were never finished and are still ongoing.

### 4. Data Quality Issues

For the sake of redundancy, I won't explain the 311 year old in age again, nor some of the blanks which have already been explained earlier.

In the previous sections with my graphs, I dropped all the missing values from the dataset, certainly honing in on values that existed. This allowed me to perform a preliminary EDA with the graphs I was able to produce.

I also explained the discrepancy with the months and why May had the outstanding most data points.

It is difficult to say whether there are any real outliers with the data in duration of campaign because those span from 0 seconds to more than 4000 seconds.

Although the data dictionary says there's no blanks in the marital column, there is 1 — we can likely drop this value since it's not going to skew the data any way. We can do the same with the lone blank in the default credit column, as well as the lone blank in the month and poutcome columns. Finally, we can do the same with the lone blank in the target response column.

As we can see with the code block below, no duplicates exist.

For checking the missing values, there wasn't a whole lot needed to be done besides dropping the missing rows, which I explained above. I used that method to produce the plots above and below as well so that missing values — or "nan's" — would not appear.

You can see below that there weren't that many missing values. If you compare the number of tuples present for the original dataset, which I called "bank," and the one without missing values — "sub_bank" — there are roughly five less rows.

#### Find outliers

```bash
# Create 2x2 data matrix
fig, axs = plt.subplots(2, 2, figsize=(15, 10))

# Boxplot for time duration of the last contact of a client
axs[0,0].boxplot(sub_bank['duration'])
axs[0,0].set_title('Range of Duration')
axs[0,0].set_xlabel('Duration')
axs[0,0].set_ylabel('Time (seconds)')
```

With the plots above, there are clearly many outliers for each data attribute. The range of duration spans from [0, 4918], so this makes sense but it's clear the median is much closer to 100-200. Perhaps approaching an analyses with a weighted mean would be a good way to go. The mean of the data is just under 260 seconds.

Roughly the same comes from the number of contacts for this campaign and client, although clearly less number of outliers. The biggest outlier is 56 contacts, where a client was contacted 56 times, 13 more than any other client.

For the previous number of contacts, there is a small count of discrete data points, which doesn't make a whole lot of sense for a boxplot. The box and whiskers are all centered around zero, while the "outliers" represent just any other data point.

Finally, since the number of days since the client was last contacted skews so much toward the higher data points, the outliers represent the values closer to 0, which is not a lot of the data.

### 5. Relationships Between Attributes

```bash
# Numeric variables
quant_col = sub_bank[['age', 'duration', 'campaign', 'pdays', 'previous', 'nr.employed']]

sns.pairplot(quant_col)

# Show the plot
plt.show()
```

With our most prominent quantitative variables, we can see correlations using numeric values.

Although the one point of the 311 year-old, likely a human error as we previously talked about, is skewing our data heavily for the age graphs, it makes sense for the remaining graphs that there will be a higher duration of campaigns if the person is of a relatively good response age. If they are too young or too old, they will not be able to comprehend what is actually going on. Age and the other variables seem to have relatively the same relationships as well.

With the other variables, there seems to be a general negative (r < 0) or nonexistent correlation (r ~ 0) except for that of number of employed individuals in our bank and the duration of the campaign. This positive relationship exists between the number of employees and the number of contacts performed in that campaign to a particular client. The latter certainly makes sense because if we have a greater number of employees, this gives more leeway to each employee to focus on marketing to a small cohort of individuals.

With our rates and indices, there is a lot more to look at here. In general, there are more overall positive or negative relationships between the variables. The employee turnover rate is directly proportional to the consumer price index but inversely proportional to the confidence index. This means consumers are paying average price for our services but likely not loving it. There is also a fair positive correlation etween the turnover rate and the European bank lending rate.

The consumer price and confidence indices are negatively correlated with each other, which makes sense based on our previous observations.

It is difficult to say whether the European bank lending rate has any real relationship to either of the indices.

Now, I want to see relationships between categorical and quantitative variables using models

### 6. Modeling - KNN

```bash
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
```

As I have learned in the past, K = 10 is usually a good baseline when testing knn, so I start with this value when making the model. I then fit the model using the x and y training sets and project it to the x test set. We find that the model has a 91% accuracy rate when k = 10. This means that the model is very good in predicting when there will be a term deposit subscription

I then use cross-validation to find the optimal number of nearest neighbors.

After using cross validation on the training set for K = [1, 30], I determine that optimal K for yielding the best results accurately is K = 30.

Thus, we can say that K = 13 will give us a ~90.03% accuracy rate in determining which clients said they did want a term deposit subscription.

We can also see that the precision rate is 91% — which tells us that our model is predicting the true positive out of total observed 91% of the time — and the recall rate is 98%, telling us that our model is preidcting the true positives out of total positives is 98%.

KNN has its pros and cons with this data. One certain downside is converting all the string categorical variables into numeric variables — it makes it difficult to determine which factors correspond to the category when you have an abundance of categories. However, we don't have too many overall variables here, so KNN seems to be a fine choice.

On the other hand, the model-making method is generally better for smaller datasets; i.e. not when we have 40,000+ rows of data. We could have chosen another method here which likely could have worked better. Now knowing that K = 13 is optimal, we could also go with Quadratic Discriminant Analysis because, as I said before, as K increases, the decision boundary becomes more linear. If we want a method that keeps the boundaries fluid, we can go with QDA in the future.

## Run code

Run the following chunk to run our code

```bash
python GL_DE_HW2.py
```


## Run test cases

Run test_analysis.py to run all test cases, including cleaning the dataset, drop missing values, calculate summmary statistics and test our modeling pipeline.

```bash
python test_analysis.py
```

![Test cases passed](Test_Cases.png)


## Commit and push your changes via commands or User Interface

```bash
git add .
git commit -m "Initial commit with Python template setup"   
git push origin main
```

## Enable GitHub Actions

1. Go to your repository on GitHub.
2. Click on the "Actions" tab.
3. Click on "New workflow".
4. Select "Set up a workflow yourself".
5. Replace the content with the following YAML configuration:

```bash
name: Python Template for IDS706

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Lint with flake8
      run: flake8 hello.py
    - name: Run tests
      run: pytest --cov=hello
```

6. Commit and push this file to your repository.
7. GitHub Actions will run automatically on every push or pull request!

## Actions
1. Go to the "Actions" tab in your repository.
2. You should see the workflow running.
3. Click on the latest workflow run to see the details.

