#!/bin/bash

update-ca-certificates

npm install
npm run build

node server.js