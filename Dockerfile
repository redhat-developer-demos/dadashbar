# Dockerfile sourced from: 
# https://catalog.redhat.com/software/containers/rhel8/python-39/6065b20a0376735023221b11?container-tabs=get-the-source

FROM registry.fedoraproject.org/f35/python3

# Add application sources to a directory that the assemble script expects them
# and set permissions so that the container runs without root access
USER 0
ADD . /tmp/src
RUN /usr/bin/fix-permissions /tmp/src
USER 1001

# Install the dependencies
RUN /usr/libexec/s2i/assemble

# Set the default command for the resulting image
CMD /usr/libexec/s2i/run
