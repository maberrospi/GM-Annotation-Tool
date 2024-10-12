# Specify parent image
FROM condaforge/mambaforge:23.11.0-0 AS conda
# Specify working directory of image
WORKDIR /annotation_tool
# Copy file to workdir
COPY environment.yml .
# Install dependencies
RUN conda env create -f environment.yml
# Pull the environment name out of the environment.yml
# RUN echo "source activate $(head -1 /tmp/environment.yml | cut -d' ' -f2)" > ~/.bashrc
RUN echo "source activate GMAnnotationTool" > ~/.bashrc
ENV PATH=/opt/conda/envs/GMAnnotationTool/bin:$PATH
# Install additional dependencies with pip
RUN pip install numpy dash dash_bootstrap_components
# Copy rest of files
COPY . .
# Exposed port for the container
EXPOSE 4000
# Specify command when container is run
CMD [ "python", "GMAnnotationTool.py", "--host", "0.0.0.0", "--port", "4000" ]