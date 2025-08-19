FROM python:3.9

WORKDIR /usr/src/app
SHELL ["/bin/bash", "-c"]
RUN chmod 777777 /usr/src/app

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Kolkata

RUN apt-get -y update
RUN git clone https://github.com/axiomatic-systems/Bento4.git 
WORKDIR /usr/src/app/Bento4/cmakebuild

RUN cmake -DCMAKE_BUILD_TYPE=Release ..
RUN make
RUN make install

COPY requirements.txt .
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade Pillow
RUN pip3 install --no-cache-dir -r requirements.txt && pip install construct==2.8.8 && rm /usr/local/bin/mp4dump && cp /usr/src/app/Bento4/cmakebuild/mp4dump /usr/local/bin/mp4dump

COPY . .
CMD ["python", "bot.py"]
