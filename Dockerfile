FROM node:8.11.1

# Create app directory
WORKDIR /src/app/

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)
COPY package*.json /src/app/

RUN npm install

# Bundle app source
COPY . /src/app/

VOLUME [ "/src/app" ]
CMD [ "npm", "start" ]