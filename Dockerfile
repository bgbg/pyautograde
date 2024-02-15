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

# Install the required Python packages with conda
RUN conda install -y pandas numpy matplotlib jupyter scikit-learn pytest black defopt && \
    conda clean -afy

# Install OpenSSH server
RUN apt-get update && \
    apt-get install -y openssh-server && \
    mkdir /var/run/sshd

# Configure SSH for passwordless access
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && \
    sed -i 's/#ChallengeResponseAuthentication yes/ChallengeResponseAuthentication no/' /etc/ssh/sshd_config

# Setup directory for authorized_keys
RUN mkdir -p /root/.ssh && \
    chmod 700 /root/.ssh

# Ensure you copy your public SSH key into the same directory as the Dockerfile before building
COPY id_rsa.pub /root/.ssh/authorized_keys

RUN chmod 600 /root/.ssh/authorized_keys

# SSH login fix
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

# Expose SSH port
EXPOSE 22


# Start SSH daemon
CMD ["/usr/sbin/sshd", "-D"]


