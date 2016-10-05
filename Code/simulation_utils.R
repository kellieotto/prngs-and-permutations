library(dplyr)


getEmpiricalDistrRaw <- function(n, k, reps=1e7){
  # Just generates the samples and leaves them in matrix form,
  # one per row, unsorted.
  samReplicates <- t(replicate(reps, sort(sample(n, k))))
  return(samReplicates)
}        


getEmpiricalDistr <- function(samReplicates){
  # Takes input from getEmpiricalDistrRaw
  samReplicates <-  samReplicates %>% as.data.frame() %>% mutate("uniqueid" = apply(samReplicates, 1, paste0, collapse = "."))
  uniqueSampleDF <- samReplicates %>% group_by(uniqueid) %>% summarise(n())
  uniqueSamples <- vector("list", nrow(uniqueSampleDF))
  for(i in seq_len(nrow(uniqueSampleDF))){
    uniqueSamples[[i]]$sample <- as.numeric(unlist(strsplit(as.character(uniqueSampleDF[i, "uniqueid"]), split="\\.")))
    uniqueSamples[[i]]$freq <- unlist(uniqueSampleDF[i, "n()"])
  }
  return(uniqueSamples)
}


getEmpiricalDistr_slow <- function(samReplicates){
  # Takes input from getEmpiricalDistrRaw
  uniqueSampleVec <- unique(samReplicates)
  uniqueSamples <- vector("list", nrow(uniqueSampleVec))
  for(i in seq_along(uniqueSamples)){
    sam <- uniqueSampleVec[i, ]
    uniqueSamples[[i]]$sample <- sam
    uniqueSamples[[i]]$freq <- sum(apply(samReplicates, 1, function(row) all(row==sam)))
  }
  return(uniqueSamples)
}


getItemCounts <- function(samReplicates){
  # Takes input from getEmpiricalDistrRaw
  itemCounts <- data.frame(table(samReplicates))
  colnames(itemCounts) <- c("Item", "Count")
  return(itemCounts)
}                                         


getEmpiricalDistr_old <- function(n, k, reps=1e7){
  samReplicates <- t(replicate(reps, sort(sample(n, k))))
  uniqueSampleVec <- unique(samReplicates)
  uniqueSamples <- vector("list", nrow(uniqueSampleVec))
  for(i in seq_along(uniqueSamples)){
    sam <- uniqueSampleVec[i, ]
    uniqueSamples[[i]]$sample <- sam
    uniqueSamples[[i]]$freq <- sum(apply(samReplicates, 1, function(row) all(row==sam)))
  }
  return(uniqueSamples)
}


getItemCounts_old <- function(n, k, reps = 10^7){
  samReplicates <- t(replicate(reps, sort(sample(n, k))))
  itemCounts <- data.frame(table(samReplicates))
  colnames(itemCounts) <- c("Item", "Count")
  return(itemCounts)
}


getItemFreq <- function(itemCounts, reps = 10^7){
  itemCounts$Probability <- itemCounts$Count/reps
  return(itemCounts)
}


computeMaxProbRatio <- function(probs){
  return(max(probs) / min(probs))
}


conductChisqTest <- function(counts){
  res <- chisq.test(counts)
  return(list(
    "Statistic" = res$statistic,
    "DF" = res$parameter,
    "Pvalue" = res$p.value
  ))
}


distrNormalRange <- function(w, k){
  # CDF of the range of k IID standard normals, evaluated at w
  tmp <- integrate(function(x) k*dnorm(x)*(pnorm(x+w)-pnorm(x))^(k-1), lower = -Inf, upper = Inf)
}


distrMultinomialRange <- function(w, n, k){
  # CDF of the range of multinomial variables evaluated at w
  # n draws, k categories each having probability 1/k
  cutoff <- (w - 1/(2*n))*sqrt(k/n)
  return(distrNormalRange(cutoff, k))
}

findFreqItems <- function(samReplicates, m){
  # Return indices of the m most frequently occurring items
  countSorted <- sort(table(samReplicates), decreasing = TRUE)
  return(as.numeric(names(countSorted)[1:m]))
}

findInfrequentSamples <- function(samReplicates){
  # Return indices of the most infrequently occurring sample
  # input samReplicates is the list output of getEmpiricalDistr
  sample_freq <- sapply(samReplicates, function(x) x$freq)
  indices <- samReplicates[[which.min(sample_freq)]]
  return(indices)
}


getPopMean <- function(x){
  return(mean(x))
}


getSampleMean <- function(x, samReplicates){
  # Takes input:
  # x = population
  # samReplicates = samples. output from getEmpiricalDistrRaw, not getEmpiricalDistr
  sampMeans <- apply(samReplicates, 1, function(sam) mean(x[sam]))
  return(mean(sampMeans))
}
