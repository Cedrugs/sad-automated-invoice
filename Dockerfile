FROM python
WORKDIR /
COPY . /
RUN pip install -r requirements.txt
CMD ["python3", "main.py"]