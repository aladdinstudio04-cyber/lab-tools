package main

import (
    "io"
    "log"
    "net"
)

func main() {
    listener, err := net.Listen("tcp", ":4444")
    if err != nil {
        log.Fatal("Failed to bind:", err)
    }
    log.Println("TCP C2 listening on :4444")
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

    // Here you can either:
    // 1. Send a static message back
    // 2. Or pipe it to a local listener (if you want full interactivity)
    // For simplicity, we just echo back a greeting
    client.Write([]byte("Connected to Render C2!\n"))
}
