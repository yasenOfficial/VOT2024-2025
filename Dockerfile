FROM golang:1.23.1

# Setva working dir v containera
WORKDIR /app 

# Kopirane na requirements i install
COPY go.mod ./
COPY go.sum ./

RUN go mod download

# Kopirane na source code
COPY . .

# Build na source code
RUN go build -o main .

# specify porta kojato se izpolzva
EXPOSE 8080

# Run na aplikaciqta
CMD ["./main"]