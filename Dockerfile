FROM python:3.11.5
COPY ./app /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 9040
ENTRYPOINT ["python"]
CMD ["app.py"]