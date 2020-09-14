FROM rust:1.46-buster

WORKDIR /user/src/router
COPY . .

RUN chmod +x ./install-packages.sh
RUN ./install-packages.sh

RUN cargo install --path .

CMD ["router"]
