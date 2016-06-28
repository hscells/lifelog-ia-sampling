package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/ioutil"
	"math"
	"os"
	"sort"
	"strconv"
	"strings"
)

// Cosine is an implementation of cosine similarity
// https://github.com/gaspiman/cosine_similarity
func Cosine(a []float64, b []float64) (cosine float64, err error) {
	count := 0
	lenA := len(a)
	lenB := len(b)
	if lenA > lenB {
		count = lenA
	} else {
		count = lenB
	}
	sumA := 0.0
	s1 := 0.0
	s2 := 0.0
	for k := 0; k < count; k++ {
		if k >= lenA {
			s2 += math.Pow(b[k], 2)
			continue
		}
		if k >= lenB {
			s1 += math.Pow(a[k], 2)
			continue
		}
		sumA += a[k] * b[k]
		s1 += math.Pow(a[k], 2)
		s2 += math.Pow(b[k], 2)
	}
	if s1 == 0 || s2 == 0 {
		return 0.0, errors.New("Vectors should not be null (all zeros)")
	}
	return sumA / (math.Sqrt(s1) * math.Sqrt(s2)), nil
}

// CopyFile copies a file from src to dst. If src and dst files exist, and are
// the same, then return success. Otherise, attempt to create a hard link
// between the two files. If that fail, copy the file contents from src to dst.
func CopyFile(src, dst string) (err error) {
	sfi, err := os.Stat(src)
	if err != nil {
		return
	}
	if !sfi.Mode().IsRegular() {
		// cannot copy non-regular files (e.g., directories,
		// symlinks, devices, etc.)
		return fmt.Errorf("CopyFile: non-regular source file %s (%q)", sfi.Name(), sfi.Mode().String())
	}
	dfi, err := os.Stat(dst)
	if err != nil {
		if !os.IsNotExist(err) {
			return
		}
	} else {
		if !(dfi.Mode().IsRegular()) {
			return fmt.Errorf("CopyFile: non-regular destination file %s (%q)", dfi.Name(), dfi.Mode().String())
		}
		if os.SameFile(sfi, dfi) {
			return
		}
	}
	if err = os.Link(src, dst); err == nil {
		return
	}
	err = copyFileContents(src, dst)
	return
}

// copyFileContents copies the contents of the file named src to the file named
// by dst. The file will be created if it does not already exist. If the
// destination file exists, all it's contents will be replaced by the contents
// of the source file.
func copyFileContents(src, dst string) (err error) {
	in, err := os.Open(src)
	if err != nil {
		return
	}
	defer in.Close()
	out, err := os.Create(dst)
	if err != nil {
		return
	}
	defer func() {
		cerr := out.Close()
		if err == nil {
			err = cerr
		}
	}()
	if _, err = io.Copy(out, in); err != nil {
		return
	}
	err = out.Sync()
	return
}

// Image is a tuple containing a filename and a histogram vector
type Image struct {
	FileName  string
	Path      string
	Histogram []float64
}

// AvgerageVec takes
func AvgerageVec(img []Image) (avgVec []float64) {
	avgVec = img[0].Histogram
	for i := 1; i < len(img); i++ {
		for j := 0; j < len(img[i].Histogram); j++ {
			avgVec[j] += img[i].Histogram[j]
		}
	}
	for i := 0; i < len(avgVec); i++ {
		avgVec[i] = avgVec[i] / float64(len(img))
	}
	return
}

// Contains checks to see if a number is already in a slice
func Contains(s []int, e int) bool {
	for _, a := range s {
		if a == e {
			return true
		}
	}
	return false
}

func main() {

	args := os.Args[1:]

	if len(args) > 0 {
		// load the data from a JSON file
		data, err := ioutil.ReadFile(args[0])
		images := make(map[string][]float64)
		json.Unmarshal(data, &images)
		if err != nil {
			panic(err)
		}

		var clusterName string
		if len(args) == 2 {
			clusterName = args[2]
		} else {
			clusterName = "cluster"
		}

		// make absolutely sure that the images being sorted are in order
		keys := make([]string, 0, len(images))
		for key := range images {
			keys = append(keys, key)
		}
		sort.Strings(keys)

		clusterID := 0
		similarityThreashold := 0.86

		clusters := make(map[int][]Image)
		totalImages := 0

		// Temporal clustering is a two stage process to clustering sequential or time-sensitive images. The first stage
		// involves iterating through the list of images in order comparing the cosine similarity of the current image to
		// the next image in the list. If the images pass under a threashold, it is added to a new cluster and all images
		// along with all images after it. After this step, clusters are merged by taking the average feature vectors of the
		// cluster and comparing it against all other clusters which haven't been merged yet using cosine similarity.

		// iterate over the keys to ensure images are looked at sequentially
		for i := 0; i < len(keys)-1; i++ {

			// calculate the similarity for the image currently being looked at, and the next image
			similarity, err := Cosine(images[keys[i]], images[keys[i+1]])
			if err != nil {
				panic(err)
			}

			// create the new path to copy the image into
			filePath := strings.Split(keys[i], "/")
			fileName := filePath[len(filePath)-1]

			// ignore the stupid dotfiles
			if len(fileName) > 0 && fileName[0] != '.' {
				image := Image{}
				image.FileName = fileName
				image.Path = strings.Join(filePath[0:len(filePath)-1], "/")
				image.Histogram = images[keys[i]]
				// move the image into the current cluster
				clusters[clusterID] = append(clusters[clusterID], image)

				// if the similarity is below some threashold, need to create a new cluster
				if similarity < similarityThreashold {
					clusterID++
				}
				totalImages++
			}
		}

		// merge the clusters into similar groupings
		mergedClusters := make(map[int][]Image)
		merged := []int{}
		clusterID = 0

		for i := 0; i < len(clusters); i++ {
			// i may have been merged already within the inner loop
			if !Contains(merged, i) {
				for j := i; j < len(clusters); j++ {
					// j may already be merged in this loop
					if !Contains(merged, j) {
						// calculate the similarity between the average of the current cluster and all other clusters not yet merged
						similarity, err := Cosine(AvgerageVec(clusters[i]), AvgerageVec(clusters[j]))
						if err != nil {
							panic(err)
						}

						// if that similarity passes above a threashold, merge it with the current cluster and don't allow it to be
						// merged again
						if similarity >= 0.95 {
							mergedClusters[clusterID] = append(mergedClusters[clusterID], clusters[j]...)
							merged = append(merged, j)
						}
					}
				}

				// the value of i cannot be used to keep track of the current cluster, as most of the time there will be less
				// merged clusters than clusters made in the previous step
				clusterID++
			}
		}

		fmt.Println(totalImages)
		totalMergedImages := 0
		for i := 0; i < len(mergedClusters); i++ {
			for j := 0; j < len(mergedClusters[i]); j++ {
				totalMergedImages++
			}
		}
		fmt.Println(totalMergedImages)

		// copy all the files
		for i := 0; i < len(mergedClusters); i++ {
			for j := 0; j < len(mergedClusters[i]); j++ {

				dir, err := os.Getwd()
				if err != nil {
					panic(err)
				}

				filename := mergedClusters[i][j].FileName
				path := mergedClusters[i][j].Path
				dir += "/" + clusterName + "/" + strconv.Itoa(i)
				err = os.MkdirAll(dir, 0777)
				if err != nil {
					panic(err)
				}
				fmt.Printf("src: %v\ndest: %v \n", path+"/"+filename, dir+"/"+filename)
				err = copyFileContents(path+"/"+filename, dir+"/"+filename)
				if err != nil {
					panic(err)
				}
			}
		}

		fmt.Print("Initial clusters: ")
		fmt.Println(len(clusters))

		fmt.Print("Clusters after merge: ")
		fmt.Println(len(mergedClusters))

	} else {
		panic("Not enough command line arguments")
	}

}
