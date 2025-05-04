package main

import (
	"encoding/base64"
	"encoding/json"
	"io"
	"log"
	"mime/multipart"
	"os"
	"os/exec"
	"path"
	"path/filepath"
	"strings"
)

// SaveFile saves a file into DIRECTORY.
func SaveFile(f *multipart.FileHeader, directory string) error {
	file, err := f.Open()
	if err != nil {
		return err
	}
	defer file.Close()


	dst, err := os.Create(path.Join(directory, f.Filename))
	if err != nil {
		return err
	}
	defer dst.Close()

	_, err = io.Copy(dst, file)
	if err != nil {
		return err
	}

	return nil
}

// ExecFiles runs the python program to extract information on the PROMPT
// based on information in the files in DIRECTORY.
func ExecFiles(prompt, directory string) ([]byte, error) {
	_, err := exec.Command(
		"./lib/venv/bin/python3", 
		"./lib/files/main.py", 
		prompt, 
		directory).Output()

	if err != nil {
		return nil, err
	}

	entries, err := os.ReadDir(directory)
    if err != nil {
		return nil, err
    }

	filesMap := make(map[string]string)
	for _, entry := range entries {
        if entry.IsDir() || !strings.HasPrefix(entry.Name(), "highlight_") {
            continue
        }

        data, err := os.ReadFile(filepath.Join(directory, entry.Name()))
        if err != nil {
            continue
        }

        encoded := base64.StdEncoding.EncodeToString(data)
		log.Println(encoded)
        filesMap[entry.Name()] = encoded
    }

	log.Println(filesMap)

	return json.Marshal(filesMap)
}

// ExecVideo runs the python program to retrieve the timestamp where NEEDLE is mentioned
// from the LINK.
func ExecVideo(needle, link string) ([]byte, error) {
	return exec.Command(
		"./lib/venv/bin/python3", 
		"./lib/video/main.py", 
		needle, 
		link).Output()
}
