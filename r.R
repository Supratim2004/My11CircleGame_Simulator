# Load dataset (Example: iris dataset)
data(iris)
df <- iris[, 1:4]  # Selecting only numeric columns
install.packages("readxl")
library(readxl)
df=read_excel("data.xlsx")
df1=df[,2:9]
# Perform PCA
pca_result <- prcomp(df1,center=TRUE,scale.=TRUE)

# Print summary
summary(pca_result)

# Scree plot to visualize explained variance
screeplot(pca_result, type = "lines", main = "Scree Plot")

# Biplot for visualization
#biplot(pca_result, main = "PCA Biplot")

# Access principal components
pca_result$x  # Scores of principal components
pca_result
r=pca_result$x
l=pca_result$rotation
u=pca_result$sdev
