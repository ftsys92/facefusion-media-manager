FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ARG FACEFUSION_VERSION=2.3.0
ENV GRADIO_SERVER_NAME=0.0.0.0

WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get install python3.10 -y
RUN apt-get install python-is-python3 -y
RUN apt-get install pip -y
RUN apt-get install git -y
RUN apt-get install curl -y
RUN apt-get install ffmpeg -y

RUN apt-get update && \
    apt-get install -y inotify-tools && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/facefusion/facefusion.git --branch ${FACEFUSION_VERSION} --single-branch .
RUN python install.py --torch cuda-11.8 --onnxruntime cuda-11.8 --skip-venv

RUN cd /usr/local/lib/python3.10/dist-packages/torch/lib && ln -s libnvrtc-672ee683.so.11.2 libnvrtc.so

RUN pip install Flask Flask-HTTPAuth Flask-CORS requests rq Flask-RQ2 redis flask_socketio

RUN mkdir -p /usr/src/app/source && mkdir -p /usr/src/app/target && mkdir -p /usr/src/app/output

# Run the script when the container launches
CMD ["/usr/src/app/worker.sh"]
