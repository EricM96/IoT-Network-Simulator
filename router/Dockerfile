FROM rust:1.46-buster

RUN rustup default nightly \
        && rustup update

WORKDIR /user/src/router
COPY . .

RUN chmod +x ./install-packages.sh
RUN ./install-packages.sh

RUN sudo chmod +x ./set_packet_counts.sh
RUN chmod +x ./get_packet_counts.sh

RUN cargo install --path .

ENV ROCKET_ENV=production

CMD ["router"]
