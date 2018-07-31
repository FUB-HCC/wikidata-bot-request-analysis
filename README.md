# wikidata-requests-for-permissions

## Requirements

To be able to work properly collaboratively with jupyter notebook you should have installed ipython version 6.4.0 and Python version 3.6.0.

## Installing

To install the project run

```
git clone https://github.com/FUB-HCC/wikidata-bot-request-analysis.git
cd wikidata-bot-request-analysis.git
pip install -r requirements.txt
```

## Running

### Whole Data Pipeline

If you want to run the whole data pipeline (e.g. retrieving, processing and storing the data) you should run the following:

First setting an environment variable:
```
PYWIKIBOT2_NO_USER_CONFIG=2
```
Then copying the config file and filling it with your own configuration:
```
cp config.yaml.sample config.yaml
```

Afterwards you can run the script with the following command:
```
python src/main.py
```

### Only Analysis

If you only want to run the analysis, you should execute the following:
```
cd doc/
jupyter notebook
```
Then you can find the file with all analyses in doc/doc.ipython.

