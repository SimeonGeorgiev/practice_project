# Practice projects
This repository includes several practice projects I've worked on while at university:

1. Sloan_digital_sky_survey: Here I train a decision tree on a dataset from Kaggle. The decision tree is then hosted on a socket server which can handle requests asynchronously. The server responds to bytestring messages and can return classifications from requests submitted as byte-encoded JSON strings. I've written a context manager to handle communications with similar servers. I used it compute a confusion matrix from remote classifications on test data. This project uses numpy, pandas and sklearn as well as an async module: https://gist.github.com/dabeaz/fc5c08040effca799759 
The data was taken from: https://www.kaggle.com/lucidlenn/sloan-digital-sky-survey

2. DNA_analysis: This is code from an assignment during semester 1 of my Bioinformatics degree. 
I've created classes and methods for parsing DNA sequences, submitting queries to the NCBI BLAST server and then analysing the results. This project uses Biopython: http://biopython.org.
