source("simulation_utils.R")
library(testthat)

######################################################################

test_distrNormalRange <- function(){
  n = 100
  set.seed(12345)
  
  # Works!
  empiricalRangeDistr <- replicate(100000, {
    tmp <- rnorm(n)
    max(tmp) - min(tmp)
  })
  for(w in seq(3, 6, by = 0.5)){
    emp <- mean(empiricalRangeDistr <= w)
    expect_equal(distrNormalRange(w, n), emp, tolerance = 0.005)
  }
}

test_distrMultinomialRange <- function(){
  reps = 10000
  
  bins = 15
  set.seed(12345)
  
  # Works!
  empiricalRangeDistr <- replicate(100000, {
    tmp <- rmultinom(n = 1, size = reps, prob = rep(1/bins, bins))
    diff(range(tmp))
  })
  for(w in (1:20)*10){
    emp <- mean(empiricalRangeDistr <= w)
    expect_equal(distrMultinomialRange(w, reps, bins), emp, tolerance = 0.015)
  }
}

######################################################################

# Will be silent if there are no errors
test_distrNormalRange()
test_distrMultinomialRange()