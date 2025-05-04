package main

import (
	"log"
	"math/rand"
	"net/http"
	"os"
	"strings"
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
			log.Println("Method not allowed:", r.Method)
			return
		}

		r.ParseMultipartForm(20 << 20) // 20 MB limit

		var user_request UserRequest
		user_request.From(r)

		var dir UniqueDir
		err := dir.New()
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			log.Println(err.Error())
			return
		}

		defer dir.Clean()

		for _, fileHeader := range user_request.Files {
			err := SaveFile(fileHeader, dir.Path)
			if err != nil {
				http.Error(w, err.Error(), http.StatusInternalServerError)
				log.Println(err.Error())
				return
			}
		}

		var out []byte

		if user_request.Files != nil {
			out, err = ExecFiles(user_request.Prompt, dir.Path)
			if err != nil {
				http.Error(w, "Error: AI could not parse query!", http.StatusInternalServerError)
				log.Println(err.Error())
				return
			}
		} else if user_request.Video != "" {
			out, err = ExecVideo(user_request.Prompt, user_request.Video)
			if err != nil {
				http.Error(w, "Error: AI could not parse query!", http.StatusInternalServerError)
				log.Println( "Error: AI could not parse query!")
				return
			}

			delimiter := "---DONE---"
			input := string(out)

			if idx := strings.Index(input, delimiter); idx != -1 {
				result := input[idx+len(delimiter):]
				out = []byte(result)
			} else {
				http.Error(w, "Error: AI could not parse query!", http.StatusInternalServerError)
				log.Println( "Error: AI could not parse query!")
				return
			}
		}

		w.WriteHeader(http.StatusOK)
		w.Write(out)
		return
	})


	log.Printf("Listening on: localhost%s\n", port)
	log.Fatal(http.ListenAndServe(port, nil))
}
