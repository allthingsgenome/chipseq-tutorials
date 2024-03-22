# Project README

## Description

This is a quick tutorial on how to create a consensus peak file from .narrowPeak or .broadPeak files and generate a intersection matrix that can be used to create UpSet plots.

The script, `create_intersect_matrix.py`, takes a merged peak file from the MACS2 peak caller tool and generates an output file containing additional information about the merged peaks and their presence or absence in each sample. It also creates a separate file that summarizes the unique combinations of samples present in the merged broad peaks, which can be used for further analysis or visualization.

## Prerequisites

Before proceeding, ensure that you have the following software installed:

- Conda (Miniconda or Anaconda Distribution)
- BEDTools (for the `mergebed` command)

## Installation

1. **Install BEDTools**

If you haven't already, install BEDTools by following the instructions for your operating system from the official website: [https://bedtools.readthedocs.io/en/latest/content/installation.html](https://bedtools.readthedocs.io/en/latest/content/installation.html)

2. **Install Micromamba or Microconda**

Micromamba and Microconda are lightweight alternatives to the full Anaconda distribution, designed for environments where disk space is limited or when you need a faster installation process.

To install Micromamba or Microconda, follow the instructions from the respective official repositories:

- Micromamba: [https://github.com/mamba-org/mamba](https://github.com/mamba-org/mamba)
- Microconda: [https://repo.anaconda.com/miniconda/](https://repo.anaconda.com/miniconda/)

3. **Create a Conda Environment**

Once you have Micromamba or Microconda installed, create a new conda environment with Python 3.10 by running the following command:

```
micromamba env create -f environment.yml
```

Replace `micromamba` with `microconda` if you installed Microconda instead.

4. **Activate the Environment**

```
micromamba activate py3
```

Replace `micromamba` with `microconda` if you installed Microconda instead.

5. **Create Consensus Peak File**

Create a merged peak file using bedtools mergeBed.

```
sort -k1,1 -k2,2n *.narrowPeak | mergeBed -c 2,3,4,5,6,7,8,9 -o collapse,collapse,collapse,collapse,collapse,collapse,collapse,collapse > merged.consensus_peaks.txt
```

Replace `.narrowPeak files` with `.broadPeak files` if necessary.

6. **Create Intersection Matrix Files**

Create intersection matrix files using `create_intersection_matrix.py` script.

```
python create_intersect_matrix.py merged.consensus_peaks.txt output.intersection.txt --min_replicates 1
```

## Script Output

The script generates two output files:

1. `<OUTFILE>`: This file contains additional information about the merged peaks and their presence or absence in each sample.

2. `<OUTFILE>.intersect.txt`: This file summarizes the unique combinations of samples present in the merged broad peaks and their frequencies, sorted in descending order. It is compatible with the UpSetR package for visualizing set intersections.

- The script collects all unique sample names from the merged interval file and uses them to create output columns.

## Script Limitations

The script doesn't generalize very well because it splits the sample names based on the first instance of "." which may not be the case for peak files created outside our pipeline.

For example, in the example test case we use the `.narrowPeak` file names were variations of `sample_name._peaks.narrowPeak`.

## Additional Resources

- Conda Documentation: [https://docs.conda.io/en/latest/](https://docs.conda.io/en/latest/)
- BEDTools Documentation: [https://bedtools.readthedocs.io/en/latest/](https://bedtools.readthedocs.io/en/latest/)
- Python Documentation: [https://docs.python.org/3/](https://docs.python.org/3/)