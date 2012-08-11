# Import training data
print("Loading data")
train <- read.csv("wordbag_train.csv", head=TRUE)
train$Response <- as.factor(train$Response)

# Fill in missing NA values
# Not sure how valid this or if it should actually be done separately per response
train$Hour[is.na(train$Hour)] <- mean(train$Hour, na.rm = TRUE)
train$Weekday[is.na(train$Weekday)] <- median(train$Weekday, na.rm = TRUE)
train$Weekday <- as.factor(train$Weekday)

test <- read.csv("wordbag_test.csv")
test$Hour[is.na(test$Hour)] <- mean(test$Hour, na.rm = TRUE)
test$Weekday[is.na(test$Weekday)] <- median(test$Weekday, na.rm = TRUE)
test$Weekday <- as.factor(test$Weekday)
df <- read.csv("data/imperium_test.csv", head=TRUE)

# Fit an svm
library(e1071)
#print("Fitting model")
#model.svm <- svm(Response ~ ., data=train, probability=TRUE)
#train.p <- predict(model.svm, train, probability=TRUE)

# Calculate AUC (Area Under ROC curve) metric
library(caTools)
#train.prob <- attr(train.p, "probabilities")[,2]
#print(colAUC(train.prob, train$Response))

# Read test dataset and run the model on it
#test.p <- predict(model.svm, test, probability=TRUE)
#test.prob <- attr(test.p, "probabilities")[,2]

# Write the output
#df <- data.frame(c(data.frame(Insult=test.p), df))
#write.csv(df, "wordbag_svm_submit.csv", row.names=FALSE) 

# Fit random forest to data
print("Training random forest")
library(randomForest)
model.rf <- randomForest(train$Response ~ ., data=train, importance=TRUE)
train.rf.p <- predict(model.rf, train, type="prob")

print("AUC from training set")
print(colAUC(train.rf.p[,2], train$Response))

# Predict and write out
print("Writing out RF predictions")
test.rf.p <- predict(model.rf, test, type="prob")
df$Insult <- test.rf.p[,2]
write.csv(df, "wordbag_rf_submit.csv", row.names=FALSE)

library(ggplot2)
# Output some plots
print("Plotting")
pdf("plots.pdf", width=7, height=14)
colAUC(train.rf.p[,2], train$Response, alg="ROC", plotROC=TRUE)
lines( par()$usr[1:2], par()$usr[3:4] )

library(gridExtra)
q1 <- qplot(train$Weekday) + geom_histogram(aes(fill=train$Response))
q2 <- qplot(train$Hour) + geom_histogram(aes(fill=train$Response))
grid.arrange(q1, q2)

# Produce some variable importance plots
rf.importance <- data.frame(name = rownames(model.rf$importance[,0]), 
                            MeanDecreaseAccuracy = as.vector(model.rf$importance[,3]), 
                            MeanDecreaseGini = as.vector(model.rf$importance[,4]))
# MeanDecreaseGini sorted bar chart
rf.importance <- rf.importance[order(rf.importance$MeanDecreaseGini),]
rf.importance$name  <- factor(rf.importance$name, as.character(rf.importance$name))
g3 <- qplot(rf.importance$name, rf.importance$MeanDecreaseGini, geom="bar",
      main="MeanDecreaseGini from Random Forest", ylab="MeanDecreaseGini", xlab="Features") + coord_flip()

grid.arrange(g3)

# MeanDecreaseAccuracy sorted bar chart
rf.importance <- rf.importance[order(rf.importance$MeanDecreaseAccuracy),]
rf.importance$name  <- factor(rf.importance$name, as.character(rf.importance$name))
g4 <- qplot(rf.importance$name, rf.importance$MeanDecreaseAccuracy, geom="bar",
      main="MeanDecreaseAccuracy from Random Forest", ylab="MeanDecreaseAccuracy", xlab="Features") + coord_flip()
grid.arrange(g4)

dev.off()
print("Done")
