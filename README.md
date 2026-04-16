# About

This is a small assignment where I classify the types of housing developments based on the Housing Maui dataset and do some basic data analytics on it. The same classification task will also be done on another separate piece of data, which is about SHPD (historical protected areas).

```tree 
.
├── clean-data
│   └── shpd-labelled.csv
├── images
│   ├── economic_impact_summary.png
│   ├── project_impact_summary.pdf
│   └── project_summary.png
├── raw-data
│   ├── labels.csv
│   ├── my_copy_building-permits.xlsx
│   ├── SHPD consolidated.xlsx
│   └── shpd-plumb.csv
├── README.md
└── src
    ├── analysis.ipynb
    ├── binary-logistic.py
    ├── data-gather
    │   ├── shpd-21-24-determinations.pdf
    │   └── shpd-pdf-plumber.py
    ├── multinomial-logistic.py
    ├── prototyping.ipynb
    ├── supervised-shpd.py
    └── unsurpervised-maui.ipynb
```
# Data
We have two XLSX spreadsheets that we're going to work with. 
The first is the Maui Housing data that I will use in order to find the most popular housing developments and possibly map those out?

# Methods
Text classification, vectorization. Perhaps some regression models if I can find corresponding census data with some areal interpolation... that's going to be interesting. 

1. Text classification (unsupervised & supervised)
2. Logistic regressions for probabilities
3. Basic summary statistics (type by year, etc.)

# TODO
1. Priority is to clean data and get some K-means clustering... need to focus on the more "detailed" project names... cannot access on HICRIS.
2. Once K-means clustering is achieved, do a supervised learning algorithm with specific criteria to get what I want. 
3. With the categories from the supervised algorithm, do summary statistics with data that we have (not that much TBH)
4. Find geographical data to match with the TMKs. Use Python as much as possible. 
