# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.191.1/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version: 3, 3.9, 3.8, 3.7, 3.6
ARG VARIANT="3.9"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# [Choice] Node.js version: none, lts/*, 16, 14, 12, 10
ARG NODE_VERSION="none"
RUN if [ "${NODE_VERSION}" != "none" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

RUN apt-get update \
 && apt-get install --no-install-recommends -y \
      graphviz \
      imagemagick \
      make \
      software-properties-common \
 && apt-add-repository 'deb http://security.debian.org/debian-security stretch/updates main' \ 
 && apt-get update \
 && apt-get install --no-install-recommends -y openjdk-8-jre \
 && apt-get autoremove \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

#PlantUML
ENV PLANTUML_DIR /usr/local/plantuml
ENV PLANTUML_JAR plantuml.jar
ENV PLANTUML $PLANTUML_DIR/$PLANTUML_JAR

RUN \
    echo "#PlantUML" && \
    mkdir $PLANTUML_DIR && \
    wget "https://sourceforge.net/projects/plantuml/files/plantuml.jar" --no-check-certificate && \
    echo "#Check jar file size. refs #9. normal jar file size is maybe > 5mb" && \
    size=$(stat -c %s plantuml.jar) && \
    test $size -gt 5000000 && \
    mv plantuml.jar $PLANTUML_DIR

COPY requirements.txt .

RUN python3 -m pip install --no-cache-dir -U pip
RUN python3 -m pip install --no-cache-dir Pillow
RUN python3 -m pip install -r requirements.txt