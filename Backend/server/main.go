package main

import (
	"log"
	"net/http"
	"os"
)

func main() {
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("Server is not up yet :P"))
	})

	port := os.Getenv("PORT")

	log.Printf("Listening on: localhost%s\n", port)
	log.Fatal(http.ListenAndServe(port, nil))
}
