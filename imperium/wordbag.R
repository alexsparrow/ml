# Import training data
print("Loading data")
train <- read.csv("wordbag_train.csv", head=TRUE)
train$Response = as.factor(train$Response)

# Fit an svm
library(e1071)
print("Fitting model")
model.svm <- svm(Response ~ ., data=train, probability=TRUE)
train.p <- predict(model.svm, train, probability=TRUE)

# Calculate AUC (Area Under ROC curve) metric
library(caTools)
train.prob <- attr(train.p, "probabilities")[,2]
print(colAUC(train.prob, train$Response))

# Read test dataset and run the model on it
test <- read.csv("wordbag_test.csv")
test.p <- predict(model.svm, test, probability=TRUE)
test.prob <- attr(test.p, "probabilities")[,2]

# Write the output
df <- read.csv("data/imperium_test.csv", head=TRUE)
df <- data.frame(c(data.frame(Insult=test.p), df))
write.csv(df, "wordbag_submit.csv", row.names=FALSE) 

# Fit random forest to data
library(randomForest)
model.rf <- randomForest(train$Response ~ ., data=train, importance=TRUE)
train.rf.p <- predict(model.rf, train, type="prob")

print(colAUC(train.rf.p[,2], train$Response))

# Predict and write out
test.rf.p <- predict(model.rf, test, type="prob")
df$Insult <- test.rf.p[,2]
write.csv(df, "wordbag_rf_submit.csv", row.names=FALSE)

pdf("roc.pdf")
colAUC(train.rf.p[,2], train$Response, alg="ROC", plotROC=TRUE)
