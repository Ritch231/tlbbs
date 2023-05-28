FROM python:3.10.11-slim-buster

RUN pip3 install requests
RUN mkdir -p /workfolder
COPY ./src/tlbbs.py /workfolder/

CMD [ "python", "/workfolder/tlbbs.py" ]