
library(randomForest)
library(e1071)
library(caTools)
library(gbm)
library(nnet)
library(ggplot2)
library(gridExtra)

# Import training data
print("Loading data")
train.data <- read.csv("process/wordbag2_train.csv", head=TRUE)
test.data <- read.csv("process/wordbag2_test.csv")
input.csv <- read.csv("data/imperium_test.csv", head=TRUE)

# Adapted from www.stat.columbia.edu/~gelman/arm/missing.pdf
random.impute.stratified <- function(col, cat){
    imputed <- col
    stopifnot(is.factor(cat))
    for(lev in levels(cat)){
        missing <- is.na(col) & lev == cat
        n.missing <- sum(missing)
        col.obs <- col[(!is.na(col)) & lev==cat]
        imputed[missing] <- sample(col.obs, n.missing, replace=TRUE)
    }
    return(imputed)
}

random.impute <- function(col){
    imputed <- col
    missing <- is.na(col)
    n.missing <- sum(missing)
    col.obs <- col[!missing]
    imputed[missing] <- sample(col.obs, n.missing, replace = TRUE)
    return(imputed)
}

clean.data <- function(data, test=FALSE){
    data$Weekday <- factor(data$Weekday, levels = 0:6)
    data$Hour <- factor(data$Hour, levels= 0:23)
    # Note this is necessary since I plugged dummy values into the training set
    # Although randomForest doesn't care how many levels this factor has, it does
    # check
    data$Response <- factor(data$Response, levels=0:1)
#    if(!test){
#        data$Hour <- random.impute.stratified(data$Hour, data$Response)
#        data$Weekday <- random.impute.stratified(data$Weekday, data$Response)
#    }
#    else{
        data$Hour <- random.impute(data$Hour)
        data$Weekday <- random.impute(data$Weekday)
#    }
    return(data)
}

save.pred <- function (name, pred) {
    #cat('Estimated RMSE: ', rmse(ratings, pred$cv), '\n');

    filename <- paste('predictions/', name, '.csv', sep='');

    write.csv(pred$test, filename, row.names=F, quote=F);
    write.csv(pred$cv, paste(filename, '.cross', sep=''), row.names=F, quote=F);
}

svm.pred <- function(train, test, response){
    # I took this example from https://github.com/mewo2/musichackathon/blob/master/predict.R
    # but just couldn't get it to work so reverted to previous way of doing things (below).
    # n <- nrow(train)
    # dall <- rbind(train, test)
    # model.mat <- model.matrix(~., data=dall)
    # model <- svm(model.mat[1:n], response, probability=TRUE)
    # test.pred <- predict(model, model.mat[-(1:n)], probability=TRUE)
    # print(test.pred)
    # stopifnot(length(test.pred) == nrow(test))
    # test.pred <- predict(svm, test, probability=TRUE)
    df <- data.frame(Response=response, train)
    model.svm <- svm(Response ~ ., data=df, probability=TRUE)
    train.pred <- predict(model.svm, df, probability=TRUE)
    test.pred <- predict(model.svm, test, probability=TRUE)
    return(list(train=attr(train.pred, "probabilities")[,2], 
                test = attr(test.pred, "probabilities")[,2]))
}

rf.pred <- function(train, test, response){
    model <- randomForest(train, response, importance=TRUE)
    cat.new <- sapply(test, function(x) if (is.factor(x) && 
                                                      !is.ordered(x)) 
                length(levels(x))
                        else 1)
    train.pred <- predict(model, train, type="prob")
    test.pred <- predict(model, test, type="prob")
    cv <- train.pred[,2]
    return(list(train=train.pred[,2], test=test.pred[,2], cv=cv, rf=model))
}

gbm.pred <- function(train, test, response){
    # Factors in the dependent variable aren't allowed so convert to numeric
    gb <- gbm.fit(train, as.numeric(as.character(response)), distribution='bernoulli', 
                  shrinkage=0.08,interaction.depth=4, n.trees= 250);
    train.pred <- predict(gb, train, n.trees=250, type="response")
    test.pred <- predict(gb, test, n.trees=250, type="response")
    return(list(train=train.pred, test=test.pred))
}

glm.pred <- function(train, test, response){
    df <- data.frame(Response=response, train)
    gl <- glm(Response~., data=df,  family="binomial")
    train.pred <- predict(gl, df, type="response")
    test.pred <- predict(gl, test, type="response")
    return(list(train=train.pred, test=test.pred))
}

cross.val <- function (predictor, folds, train, test, response, ...) {
    cat('Running primary predictor\n');
    pred <- predictor(train, test, response, ...);
    items <- sample(folds, nrow(train), T);
    cv <- numeric(nrow(train));
    for (i in 1:folds) {
        samp <- which(items == i);
        cat('Running CV fold', i, '\n');
        cpred <- predictor(train[-samp,], train[samp,], response[-samp], ...);
        print(cpred)
        print(length(cpred$test))
        cat('Estimated AUC for fold:', colAUC(cpred$test, response[samp]), '\n');
        cv[samp] <- cpred$test;
    }
    pred$cv <- cv;
    return(pred);
}
    
run.predictions <- function(){
    train <- clean.data(train.data)
    test <- clean.data(test.data, test=TRUE)
    response <- train$Response
    train$Response <- NULL
    test$Response <- NULL
    for(nm in colnames(train)){
        idx <- which(colnames(train) == nm)
        stopifnot(nm %in% colnames(test))
        stopifnot(class(test[,idx]) == class(train[,idx]))
    }
  #  save.pred("glm", cross.val(glm.pred, 10, train, test, response))
  #  save.pred("svm", cross.val(svm.pred, 10, train,test, response))
    #save.pred("gbm", cross.val(gbm.pred, 10, train,test, response))
    save.pred("rf", rf.pred(train, test, response))
}

blend <- function(){
    train <- clean.data(train.data)
    test <- clean.data(test.data, test=TRUE)
    preds <- c( "svm", "rf")
    trains <- sapply(preds, function (name) read.csv(paste('predictions/', name, '.csv.cross', sep=''))$x);
    tests <- sapply(preds, function (name) read.csv(paste('predictions/', name, '.csv', sep=''))$x);
    df <- data.frame(Response = train$Response, trains)
    mix <- nnet(Response~., data=df,  size=5, decay=0.1, maxit=500,  reltol=0, abstol=0, skip=T)
    print(summary(mix))
    cat('Estimated AUC for mix:', colAUC(predict(mix), train$Response), '\n');
    df <- read.csv("data/imperium_test.csv")
    df <- data.frame(Insult=predict(mix,tests), df)
    blendname <- do.call(paste, as.list(c(preds, sep='-')));
    write.csv(df, paste('blends/', blendname, '.csv', sep=''), row.names=F)
    return(mix)
}

importance.plots <- function(fname, model.rf){
    pdf(fname, width=7, height=40)
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
          main="MeanDecreaseAccuracy from Random Forest", ylab="MeanDecreaseAccuracy", 
          xlab="Features") + coord_flip()
    grid.arrange(g4)

    dev.off()
}

make.plots <- function(){
    # Output some plots
    print("Plotting")
    colAUC(train.rf.p[,2], train$Response, alg="ROC", plotROC=TRUE)
    lines( par()$usr[1:2], par()$usr[3:4] )

    q1 <- qplot(train$Weekday) + geom_histogram(aes(fill=train$Response))
    q2 <- qplot(train$Hour) + geom_histogram(aes(fill=train$Response))
    grid.arrange(q1, q2)

}
    print("Done")
