FROM rust:1.46-buster

WORKDIR /user/src/tcp-echo-server
COPY . .

RUN cargo install --path .

CMD ["tcp-echo-server"]
