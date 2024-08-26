# this docker file builds image, that will serve as a prefect-orion-server, prefect-agent and prefect-worker
# all dependencies and libs that flow execution requires has to be installed here 

FROM prefecthq/prefect:2.11.3-python3.9

# Update and install packages
RUN apt update && \
    /usr/local/bin/python -m pip install --upgrade pip && \
    apt-get install libpq-dev -y

# Set the working directory
WORKDIR /app

# Copy and install requirements
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

