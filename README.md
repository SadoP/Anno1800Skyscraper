# ANNO 1800 Skyscraper Layout Optimizer
This layout optimizer works by taking in a predefined layout and then finds the (near) optimal way to upgrade skyscrapers to different levels in order to maximize population by randomly upgrading and downgrading some skyscrapers, discarding worse and keeping better configurations.  
[Skyscrapers](https://anno1800.fandom.com/wiki/Skyscrapers) in Anno 1800 benefit from Panorame, i.e. if a skyscraper is surrounded by buildings of lower height, this will increase its panorama and total population, being surrounded by higher buildings will decrease its panorama and total population.
A mixture of higher and lower level skyscrapers creates the highest benefits, finding the best layout is however very difficult.
If someone with more math knowledge than me can prove there is no analytical solution, that would be great.  
A solution based around trying all possible solutions [has been tried](https://github.com/Caracus/Anno1800Panorama) but this is infeasible for large amounts of buildings.
Randomly applying mutations to an initial distribution of skyscraper levels will increase or decrease the total population of the layout.
Only keeping the mutations that create an improvement will eventually converge to a solution that is close to the best possible solution.

## Example 
Starting Layout with randomly initialized house levels  
<img src="./layouts/3x3/3x3_in.png" alt="Start Layout" style="max-width: 512px">

Layout after optimizing  
<img src="./layouts/3x3/3x3_out.png" alt="Optimized Layout" style="max-width: 512px">


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
If you have problems installing poetry, follow the installation instructions here:
[https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation)
## Usage
 - Create a folder in "layouts" that contains a file that matches the pattern "*_in.csv", e.g. "mylayout_in.csv".
 - Populate the csv like "./example/example_in.csv". The first two columns contain the x- and y-coordinate of the house, the third column the level to start with (1-3 for engineers, 1-5 for investors or "random" for random seeding), the fourth column contains the type of skyscraper (0 for engineers, 1 for investors)
 - Run the program with the following parameters:
   - dir (d): The directory your csv file is in
   - epochs (e): The number of epochs to run the program for. More houses need a higher number
   - change (c): The amount of houses to flip. Can be int for absolute values or float for relative values. This number varies depending on the size and shape of your layout. There's nothing but trying different values to find the best one, but lower values tend to work better in my experience.
 
   ```bash
    python main.py -d layouts/example -e 10000 -c .05
   ```
