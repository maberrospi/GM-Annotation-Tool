# Description
The repository provides a graph matching annotation tool built using Python [Dash](https://dash.plotly.com/). It offers the ability to create keypoint annotations using pairs of images.

![ToolInterfaceDemonstration](/demo_img/GMTool_Interface.png)

# Install Dependencies
```
# Clone repository
git clone https://github.com/maberrospi/GM-Annotation-Tool.git

# Install the 'enviornment_nobuilds.yml' file
$ conda env create -f environment_nobuilds.yml

# Activate environment
$ conda activate GMAnnotationTool

# Install pip dependencies (If needed)
$ pip install numpy dash dash_bootstrap_components

``` 

# Usage
```
# Activate the environment
$ python GMAnnotationToo.py -dh '127.0.0.1' -p 8050
# Navigate to the link provided with your favorite browser to start using the tool.
```
The `-dh` and `-p` arguments are optional and refer to the `host ip` and the `port` where the app will be deployed.
The annotation output folder will be created the first time you save any annotations and is located in the `Output` directory.

# Annotation Instructions

1. Match points in the images. Always select the first point from the left image.
2. Each match will be annotated with a number corresponding to the clicking order.
3. The matches are saved as JSON files in the following format: `{"matches": [{"x1": px, "y1": px, "x2": px, "y2": px}]}`. The file name concatenates the image filenames likeso `R0009_1_pre_1_3-R0009_1_post_1_3.json`.
4. If no matches are chosen, the annotation will contain `{"matches": null}`