FROM 410585721938.dkr.ecr.us-west-1.amazonaws.com/ml-cache:latest

COPY src/ ./

CMD ["main.handler"]