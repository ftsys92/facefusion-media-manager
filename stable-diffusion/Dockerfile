FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

WORKDIR /usr/src/app

RUN apt-get update
RUN apt install wget git python3 python3-venv libgl1 libglib2.0-0 -y
RUN apt install --no-install-recommends google-perftools -y

RUN adduser --system --group appuser
RUN chown -R appuser:appuser /usr/src/app
USER appuser

RUN git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui .
RUN chmod +x webui.sh

CMD ["/bin/bash", "/usr/src/app/webui.sh", "--listen", "--api", "--medvram-sdxl", "--xformers", "--cors-allow-origins", "https://my-site.local, https://my-site.local:5000"]