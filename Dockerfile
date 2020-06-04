FROM continuumio/miniconda3

# Update conda.
RUN conda update -n base -c defaults conda

# Create the environment:
COPY environment.yml .
RUN conda env create -f environment.yml

# Run bash in virtual environment "working". Use conda deactivate to exit.
# Pull the environment name out of the environment.yml
RUN echo "source activate $(head -1 environment.yml | cut -d' ' -f2)" > ~/.bashrc
ENV PATH /opt/conda/envs/$(head -1 environment.yml | cut -d' ' -f2)/bin:$PATH

# Welcome message.
ADD welcome_message.txt /
RUN echo '[ ! -z "$TERM" -a -r /etc/motd ] && cat /etc/motd' \
        >> /etc/bash.bashrc \
        ; cat welcome_message.txt > /etc/motd

# FastAPI uses a PyYaml that conflicts with chatterbot. So it has to be installed last.
SHELL ["conda", "run", "-n", "working", "/bin/bash", "-c"]
RUN conda install -c conda-forge fastapi=0.55.0

WORKDIR /home
CMD ["conda", "run", "-n", "working", "python", "main.py"]