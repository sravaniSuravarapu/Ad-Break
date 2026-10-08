FROM python:3.12-slim

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir . && sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh

EXPOSE 8000

CMD ["./entrypoint.sh"]
