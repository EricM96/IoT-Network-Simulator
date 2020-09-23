FROM rust:1.46-buster

WORKDIR /app
COPY . .

RUN cargo install --path .

CMD ["motion_sensor"]

