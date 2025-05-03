package main

import (
	"io"
	"mime/multipart"
	"os"
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
