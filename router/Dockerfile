FROM rust:1.46-buster

WORKDIR /user/src/router
COPY . .

RUN chmod +x ./install-packages.sh
RUN ./install-packages.sh

RUN sudo chmod +x ./set_packet_counts.sh
RUN chmod +x ./get_packet_counts.sh

RUN useradd -m docker && echo "docker:docker" | chpasswd && adduser docker sudo

RUN cargo install --path .

CMD ["./set_packet_counts.sh && router"]
