# Question 1
SELECT *, Count(Distinct(TransactionDate)) as rn
FROM transactions
Group by ProductID
ORDER BY ProductID, TransactionDate ASC
Where rn = 3;

With CTE AS {
    SELECT *, row_number() OVER (PARTITION by "ProductID" ORDER by "TransactionDate") as rn 
    From transactions t 
    }
SELECT *
From cte;

# Question 2 - good
Select Region, sum(TotalValue) AS total_spending_region
From customers C
LEFT JOIN transactions T
ON C.CustomerID = T.CustomerID
Group By Region
Order By total_spending_region DESC
HAVING total_spending_region > 300;

# Question 3 - good
Select ProductName
From products P
Left Join transactions T
On P.ProductId = T.ProductId
Where Quantity IS NULL;

# Question 4
Select Distinct(ProductId)
From products
Group By ProductId
Where AVG(Price) > 
(Select AVG(Price))
From products);