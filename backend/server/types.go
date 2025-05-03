package main

import (
	"fmt"
	"math/rand"
	"mime/multipart"
	"os"
	"path"
	"time"
)

type UserRequest struct {
	Prompt 	string
	Files	[]*multipart.FileHeader
	Video	string
}

// UserRequest.From populates the struct with the form data.
func (u *UserRequest) From(f *multipart.Form) {
	u.Prompt = f.Value["prompt"][0]
	
	if (len(f.File) <= 0) {
		u.Files = nil
	} else {
		u.Files = f.File["pdfs"]
	}

	if (len(f.Value["video"]) <= 0) {
		u.Video = ""
	} else {
		u.Video = f.Value["video"][0]
	}
}

type UniqueDir struct {
	Path 	string
}

// UniqueDir.New creates a uniquely named directory.
func (dir *UniqueDir) New() error {
	uuid := fmt.Sprintf("%d-%d", time.Now().UnixNano(), rand.Int())
	dir.Path = path.Join("data", uuid)

	err := os.Mkdir(dir.Path, 0770)
	if err != nil {
		return err
	}

	return nil
}

// UniqueDir.Clean deletes directory.
func (dir *UniqueDir) Clean() error {
	return os.RemoveAll(dir.Path)
}

