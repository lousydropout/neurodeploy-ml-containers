FROM public.ecr.aws/lambda/python:3.10

COPY src/ ./

RUN pip install -r requirements.txt

CMD ["main.handler"]