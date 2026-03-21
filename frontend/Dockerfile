FROM node:18-alpine

WORKDIR /app

RUN npm install -g serve

COPY . .

EXPOSE 3000

CMD ["sh", "-c", "serve -s . -l ${PORT:-3000}"]