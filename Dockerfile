## Copy your SSH public key to the Docker build context
#cp ~/.ssh/id_rsa.pub /path/to/docker/build/context/
#
## Build the Docker image and run the container, mounting ${HOME}/temp to /temp and forwarding port 22
#docker build -t your_image_name /path/to/docker/build/context/
#docker run -d -p 22:22 -v ${HOME}/temp:/temp your_image_name
#
## SSH into the running container using your SSH private key
#ssh -i ~/.ssh/id_rsa root@localhost





# Use the continuumio/anaconda3 image as the base
FROM continuumio/anaconda3

# install requirements from requirements.txt
COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt


