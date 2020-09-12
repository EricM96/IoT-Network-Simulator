FROM rust:1.46-buster

WORKDIR /user/src/tcp-echo-client
COPY . .

RUN cargo install --path .

CMD ["tcp-echo-client"]
