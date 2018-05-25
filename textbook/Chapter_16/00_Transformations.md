---
layout: textbook
interact_link: notebooks/Chapter_16/00_Transformations.ipynb
previous:
  url: 
  title: Chapter 16
next:
  url: /textbook/Chapter_16/01_Linear_Transformations
  title: Linear Transformations
sidebar:
  nav: sidebar-textbook
---

# Transformations #

Let $X$ have a continuous distribution and let $Y = g(X)$ be a function of $X$. We know how to find $E(Y)$, assuming the expectation exists. In this chapter we will develop a method for finding the density of $Y$ in terms of $g$ and the density of $X$. 

The method is only valid for "well behaved" functions $g$. We will define what "well behaved" means in this context. It turns out that the class of well behaved functions is rich enough to cover a large set of interesting random variables.

We will start by studying properties of the exponential distribution which was introduced in the previous chapter. We will recognize that all exponential random variables are linear transformations of one of them. This observation will lead us to a general formula for the density of a function of a random variable.
