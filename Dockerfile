FROM arm32v7/python:slim
#FROM haproxy
RUN apt update && apt dist-upgrade -y &&apt -y install git
WORKDIR /app
RUN git clone https://github.com/efip-farmasalud/farmasaludapi . 
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
