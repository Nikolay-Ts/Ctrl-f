package main

import (
	"io"
	"mime/multipart"
	"os"
	"os/exec"
	"path"
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
	return exec.Command(
		"./lib/venv/bin/python3", 
		"./lib/files/main.py", 
		prompt, 
		directory).Output()
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
