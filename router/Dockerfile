FROM rust:1.46-buster

WORKDIR /user/src/router
COPY . .

RUN cargo install --path .

CMD ["router"]
