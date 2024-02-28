FROM node:17
WORKDIR /app
COPY . .
RUN npm install -g n
RUN npm ci --dev
RUN ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir staticfiles/bundles --public-url="./"