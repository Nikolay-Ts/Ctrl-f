package main

import (
	"log"
	"math/rand"
	"net/http"
	"os"
	"time"
)

func main() {
	rand.Seed(time.Now().UnixNano())

	port := os.Getenv("PORT")

	http.HandleFunc("/submit", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "*")
		w.Header().Set("Access-Control-Allow-Headers", "*")

		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}

		if r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		r.ParseMultipartForm(20 << 20) // 20 MB limit

		var user_request UserRequest
		user_request.From(r.MultipartForm)

		var dir UniqueDir
		err := dir.New()
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		defer dir.Clean()

		for _, fileHeader := range user_request.Files {
			err := SaveFile(fileHeader, dir.Path)
			if err != nil {
				http.Error(w, err.Error(), http.StatusInternalServerError)
			}

			w.WriteHeader(http.StatusOK)
			return
		}
	})


	log.Printf("Listening on: localhost%s\n", port)
	log.Fatal(http.ListenAndServe(port, nil))
}
