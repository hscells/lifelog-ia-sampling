#include <iostream>

#include <fstream>
#include "opencv2/core/core.hpp"
#include "opencv2/features2d/features2d.hpp"
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/nonfree/nonfree.hpp"
#include <list>

using namespace std;
using namespace cv;

const char* ofile;

Mat load_image(string* image) {
    Mat img = imread(image->c_str(), 1);
    return img;
}

vector<Mat> load_images(string* image_list_file) {
    vector<Mat> images;

    ifstream infile;
    string line;
    infile.open(image_list_file->c_str());

    while (infile >> line) {
        Mat img = load_image(new string(line));
        if( !img.empty() ) {
            images.push_back(img);
        }
    }
    infile.close();

    return images;
}

map<char,Mat>* calculate_histogram(string* image_name) {
    Mat image = imread( image_name->c_str(), 1 );
    vector<Mat> bgr_planes;
    split( image, bgr_planes );

    /// Establish the number of bins
    int histSize = 256;

    /// Set the ranges ( for B,G,R) )
    float range[] = { 0, 256 } ;
    const float* histRange = { range };

    bool uniform = true; bool accumulate = false;

    Mat b_hist, g_hist, r_hist;

    /// Compute the histograms:
    calcHist( &bgr_planes[0], 1, 0, Mat(), b_hist, 1, &histSize, &histRange, uniform, accumulate );
    calcHist( &bgr_planes[1], 1, 0, Mat(), g_hist, 1, &histSize, &histRange, uniform, accumulate );
    calcHist( &bgr_planes[2], 1, 0, Mat(), r_hist, 1, &histSize, &histRange, uniform, accumulate );

    map<char,Mat>* cols = new map<char, Mat>();
    cols->insert(pair<char,Mat>('b',b_hist));
    cols->insert(pair<char,Mat>('g',g_hist));
    cols->insert(pair<char,Mat>('r',r_hist));
    return cols;
}

map<string*, map<char, Mat>*>* calculate_histograms(string* image_file_list) {

  map<string*, map<char, Mat>*>* vectors = new map<string*, map<char, Mat>*>();

  ifstream infile;
  string line;
  infile.open(image_file_list->c_str());


  while (infile >> line) {
    /**
     * real	0m28.179s
     * user	0m25.227s
     * sys	0m1.152s
     */
    /**
     * real	0m32.443s
     * user	0m26.826s
     * sys	0m2.110s
     */
    cout << "reading: " << line << endl;
    map<char, Mat>* cols = calculate_histogram(new string(line));
    vectors->insert(pair<string*, map<char, Mat>*>(new string(line), cols));
  }
  infile.close();
  return vectors;
}

void write_vectors(map<string*, map<char, Mat>*>*  vectors) {
  map<string*, map<char, Mat>*>::iterator it = vectors->begin();
  ofstream output;
  output.open(ofile);
  while (it != vectors->end()) {
    string* name = it->first;
    map<char, Mat>* cols = it->second;

    Mat b_hist, g_hist, r_hist;

    b_hist = cols->at('b');
    g_hist = cols->at('g');
    r_hist = cols->at('r');

    vector<Mat> matrices;
    matrices.push_back(b_hist);
    matrices.push_back(g_hist);
    matrices.push_back(r_hist);
    Mat combined;
    hconcat(matrices, combined);

    string fqn = name->substr(1, strlen(name->c_str()));
    output << '"' << *name << '"' << ":" << combined;
    cout << *name << endl;
    ++it;
  }
  output.close();

}

void draw_histogram(map<char, Mat>* cols) {
  int histSize = 256;
  Mat b_hist, g_hist, r_hist;
  b_hist = cols->at('b');
  g_hist = cols->at('g');
  r_hist = cols->at('r');
  // Draw the histograms for B, G and R
  int hist_w = 512; int hist_h = 400;
  int bin_w = cvRound( (double) hist_w/histSize );

  Mat histImage( hist_h, hist_w, CV_8UC3, Scalar( 0,0,0) );

  /// Normalize the result to [ 0, histImage.rows ]
  normalize(b_hist, b_hist, 0, histImage.rows, NORM_MINMAX, -1, Mat() );
  normalize(g_hist, g_hist, 0, histImage.rows, NORM_MINMAX, -1, Mat() );
  normalize(r_hist, r_hist, 0, histImage.rows, NORM_MINMAX, -1, Mat() );

  /// Draw for each channel
  for( int i = 1; i < histSize; i++ )
  {
      line( histImage, Point( bin_w*(i-1), hist_h - cvRound(b_hist.at<float>(i-1)) ) ,
                       Point( bin_w*(i), hist_h - cvRound(b_hist.at<float>(i)) ),
                       Scalar( 255, 0, 0), 2, 8, 0  );
      line( histImage, Point( bin_w*(i-1), hist_h - cvRound(g_hist.at<float>(i-1)) ) ,
                       Point( bin_w*(i), hist_h - cvRound(g_hist.at<float>(i)) ),
                       Scalar( 0, 255, 0), 2, 8, 0  );
      line( histImage, Point( bin_w*(i-1), hist_h - cvRound(r_hist.at<float>(i-1)) ) ,
                       Point( bin_w*(i), hist_h - cvRound(r_hist.at<float>(i)) ),
                       Scalar( 0, 0, 255), 2, 8, 0  );
  }

  /// Display
  namedWindow("calcHist Demo", CV_WINDOW_AUTOSIZE );
  imshow("calcHist Demo", histImage );
}

int main(int argc, char const *argv[]) {
    const char* ifile;
    if (argc == 3) {
      ifile = argv[1];
      ofile = argv[2];
    } else {
      cout << "extractfeatures <in file> <out file>" << endl;
      exit(1);
    }
    map<string*, map<char, Mat>*>* vectors = calculate_histograms(new string(ifile));
    write_vectors(vectors);
    return 0;
}
