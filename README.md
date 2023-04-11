## Set up the environment
 - Have [Conda](https://docs.conda.io/en/latest/miniconda.html) installed according to the official instructions
 - Set up the conda environment and activate it then install dependencies enforced by poetry:
```bash
    conda env create -f environment.yml
    conda activate Anno1800Skyscraper
    curl -sSL https://install.python-poetry.org | python3 -
    poetry install
    poetry self update
```
