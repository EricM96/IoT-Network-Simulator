FROM rust:1.46-buster

WORKDIR /app
COPY . .

RUN chmod +x ./install-packages.sh
RUN ./install-packages.sh

RUN cargo install --path .

CMD ["refridgerator"]

