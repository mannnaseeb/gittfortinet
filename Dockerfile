FROM python:3.8.3-slim
RUN mkdir -p /app
COPY . app/
WORKDIR /app
RUN apt update
RUN apt install vim -y
RUN chmod +x launch.sh
RUN chmod +x generate_certs.sh
RUN pip3 config set global.index-url "http://192.168.80.189:5001/simple"
RUN pip3 config set global.trusted-host "192.168.80.189"
RUN pip3 install -r requirements.txt
RUN ./generate_certs.sh
ENTRYPOINT ["./launch.sh"]
