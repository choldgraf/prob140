---
layout: textbook
interact_link: notebooks/Chapter_21/00_The_Beta_and_the_Binomial.ipynb
previous:
  url: 
  title: Chapter 21
next:
  url: /textbook/Chapter_21/01_Updating_and_Prediction
  title: Updating And Prediction
sidebar:
  nav: sidebar-textbook
---

# The Beta and the Binomial #

Connections between the beta and binomial families have acquired fundamental importance in machine learning. In the previous chapter, you began to see some of these connections. In this chapter we will generalize those observations.

The experiment that we will study has two stages.
- Pick a value of $p$ according to a beta distribution
- Toss a coin that lands heads with the chosen probability $p$

We will see how the posterior distribution of the chance of heads is affected by the prior and by the data. After observing the results of $n$ tosses, we will make predictions about the next toss. We will find the unconditional distribution of the number of heads in $n$ tosses of our random coin and examine the long run behavior of the proportion of heads.

In labs, you will apply this theory to study a model for clustering when the number of possible clusters is not known in advance.
