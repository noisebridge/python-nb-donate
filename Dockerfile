FROM python:3.6
COPY . /app
WORKDIR /app
RUN mkdir /var/log/donate && \
    pip install -r requirements.txt
ENV FLASK_APP autoapp.py
ENTRYPOINT ["flask"]
CMD ["run", "--host=0.0.0.0"]
