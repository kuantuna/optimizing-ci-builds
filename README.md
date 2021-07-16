# Optimizing CI Builds

## Steps

**1. Finding Java Maven repositories that uses Jacoco in Github.**

A python script is used to find the most forked 420 public java repositories in Github. Subsequently, these projects were filtered according to whether or not they had a pom.xml file in their root directory. In the remaining projects, the pom.xml file was searched for the keyword **"org.jacoco"**. Finally, the results were saved in the data.csv file.

## Issues

**1. Duplicates in the data.csv file**

I don't know why, but there are projects written more than once in the data.csv file.

**2. pom.xml in root directory**

The written python script only searches for pom.xml files in the root directory. Maybe there are pom.xml files in other directories as well.
