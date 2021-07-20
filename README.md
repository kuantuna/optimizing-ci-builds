# Optimizing CI Builds


## Issues

1. Duplicates in the data.csv file (should figure it out why!)

2. Searching for pom.xml and build.gradle in the root directory (fine for now, can be improved in the future)

3. For the search API first 1000 repositories allowed (cannot get more than 1000 projects)


## Improvements (for now)

1. Figuring a way to filter out non-active projects

2. Do we need atomicity in data.csv?


## Improvements (for the future)

1. May have better data filtering

2. May add more options for coverage and continuous integration tools


## Links to read

1. https://www.freecodecamp.org/news/how-to-generate-code-coverage-report-with-codecov-and-github-actions/

2. https://blog.codecentric.de/en/2021/02/github-actions-pipeline/

3. https://graciano.dev/2020/08/25/use-jacoco-and-github-actions-to-improve-code-coverage/

