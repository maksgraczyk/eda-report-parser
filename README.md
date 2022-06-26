# eda-report-parser
A Python package for parsing text reports from EDA tools for their easier processing. It also contains a command-line tool for converting one or more text reports into a single and portable HTML file with interactive tables.

## EDA tools currently supported
* Xilinx/AMD Vivado

## How to use?
Firstly, install the package by running the following command:
```
pip install git+https://github.com/maksgraczyk/eda-report-parser.git
```
Alternatively, if you want to change the code, clone this repository manually and run the following command inside:
```
pip install -e .
```
Afterwards, you can start using `eda-report-parser`. The main module is called `edaparser` and the command-line tool is `reporthtml`.

## Example usage of the command-line tool
Converting two report files `report1.txt` and `report2.txt` produced by Vivado for an FPGA "X" into an HTML file `report.html`:
```
reporthtml -d X -t vivado -o report.html report1.txt report2.txt
```
The produced `report.html` file allows opening interactive tables for either `report1.txt` or `report2.txt`.

## License
See LICENSE.
