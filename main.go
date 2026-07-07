package main

import (
    "log"
    "net"
    "os"
)

func main() {
    port := os.Getenv("PORT")
    if port == "" {
        port = "4444" // fallback for local testing
    }

    listener, err := net.Listen("tcp", ":"+port)
    if err != nil {
        log.Fatal("Failed to bind:", err)
    }
    log.Println("TCP C2 listening on :" + port)

    for {
        conn, err := listener.Accept()
        if err != nil {
            log.Println("Accept error:", err)
            continue
        }
        go handleConnection(conn)
    }
}

func handleConnection(client net.Conn) {
    defer client.Close()
    log.Println("New connection from:", client.RemoteAddr())
    client.Write([]byte("Connected to Render C2!\n"))
}
