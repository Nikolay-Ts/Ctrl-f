package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
)

func main() {
	http.HandleFunc("/submit", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "*")
		w.Header().Set("Access-Control-Allow-Headers", "*")

		r.ParseMultipartForm(20 << 20) // 20 MB limit

		files := r.MultipartForm.File["pdfs"]
		if len(files) == 0 {
			http.Error(w, "No files uploaded", http.StatusBadRequest)
			return
		}

		for _, fileHeader := range files {
			file, err := fileHeader.Open()
			if err != nil {
				http.Error(w, "Error opening file", http.StatusInternalServerError)
				return
			}
			defer file.Close()

			dst, err := os.Create("./uploads/" + fileHeader.Filename)
			if err != nil {
				http.Error(w, "Error creating file", http.StatusInternalServerError)
				return
			}
			defer dst.Close()

			_, err = io.Copy(dst, file)
			if err != nil {
				http.Error(w, "Error saving file", http.StatusInternalServerError)
				return
			}

			fmt.Fprintf(w, "Uploaded: %s\n", fileHeader.Filename)
		}
	})

	port := os.Getenv("PORT")

	log.Printf("Listening on: localhost%s\n", port)
	log.Fatal(http.ListenAndServe(port, nil))
}
