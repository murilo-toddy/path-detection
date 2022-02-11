#include <opencv2/imgcodecs.hpp>
#include <opencv2/highgui.hpp>
#include <iostream>

#include "imageProcessing.h"
#include "contourHandler.h"

#define SAMPLES 13

using namespace std;
using namespace cv;


int main() {
    for (int i = 0; i < SAMPLES; i++) {
        string imagePath = "../source/4.jpg";
        Mat image = imread(imagePath);
        Mat canny = getImageCanny(image, false);

        vector<vector<Point>> contours = searchContours(canny, false);

        imshow("Original Image", image);
        imshow("Canny Image", canny);

        Mat imageWithConeHighlight = image.clone();
        for (int i = 0; i < contours.size(); i++) {
            drawContours(imageWithConeHighlight, contours, i, Scalar(0, 255, 255), 2);
        }

        imshow("Cones Highlighted", imageWithConeHighlight);
        cout << contours.size() << " cone(s) found" << endl;
        waitKey(0);
    }
    return 0;
}
