package main

import (
	"fmt"
	"math/rand"
	"mime/multipart"
	"net/http"
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
func (u *UserRequest) From(r *http.Request) {
	u.Prompt = r.FormValue("prompt")
	
	if (len(r.MultipartForm.File) <= 0) {
		u.Files = nil
	} else {
		u.Files = r.MultipartForm.File["pdfs"]
	}

	u.Video = r.FormValue("video")
}

type UniqueDir struct {
	Path 	string
}

// UniqueDir.New creates a uniquely named directory.
func (dir *UniqueDir) New() error {
	err := os.Mkdir("data", 0770)
	if err != nil {
		return err
	}

	uuid := fmt.Sprintf("%d-%d", time.Now().UnixNano(), rand.Int())
	dir.Path = path.Join("data", uuid)

	err = os.Mkdir(dir.Path, 0770)
	if err != nil {
		return err
	}

	return nil
}

// UniqueDir.Clean deletes directory.
func (dir *UniqueDir) Clean() error {
	return os.RemoveAll(dir.Path)
}

