package main

import (
    "io"
    "log"
    "net/http"
    "os"
    "time"
)

func main() {
    port := os.Getenv("PORT")
    if port == "" {
        port = "8080"
    }

    http.HandleFunc("/", handleRoot)
    http.HandleFunc("/collect", handleCollect)

    log.Println("HTTP C2 listening on :" + port)
    log.Fatal(http.ListenAndServe(":"+port, nil))
}

func handleRoot(w http.ResponseWriter, r *http.Request) {
    w.Write([]byte("C2 Server is Online\n"))
}

func handleCollect(w http.ResponseWriter, r *http.Request) {
    if r.Method != "POST" {
        http.Error(w, "Only POST allowed", 405)
        return
    }

    body, err := io.ReadAll(r.Body)
    if err != nil {
        http.Error(w, "Read error", 400)
        return
    }

    log.Printf("[!] Data Received from %s at %s:\n%s\n", r.RemoteAddr, time.Now().Format(time.RFC3339), string(body))
    w.Write([]byte("Data received"))
}
