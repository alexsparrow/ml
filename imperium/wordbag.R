
print("Loading data")
train <- read.csv("wordbag_train.csv", head=TRUE)
train$Response = as.factor(train$Response)

library(e1071)

print("Fitting model")
model.svm <- svm(Response ~ ., data=train, probability=TRUE)
train.p <- predict(model.svm, train, probability=TRUE)

library(caTools)
train.prob <- attr(train.p, "probabilities")[,2]
print(colAUC(train.prob, train$Response))

test <- read.csv("wordbag_test.csv")
test.p <- predict(model.svm, test, probability=TRUE)
test.prob <- attr(test.p, "probabilities")[,2]

df <- read.csv("data/imperium_test.csv", head=TRUE)
df <- data.frame(c(data.frame(Insult=ps.test), df))

write.csv(df, "wordbag_submit.csv", row.names=FALSE) 

libary(randomForest)
model.rf <- randomForest(train$Response ~ ., data=train, importance=TRUE)
train.rf.p <- predict(model.rf, train, type="prob")

print(colAUC(train.rf.p[,2], train$Response))

test.rf.p <- predict(model.rf, test, type="prob")

df$Insult <- test.rf.p[,2]
write.csv(df, "wordbag_rf_submit.csv", row.names=FALSE)
