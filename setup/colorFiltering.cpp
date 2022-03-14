#include "colorFiltering.h"

int hmin = 0, smin = 0, vmin = 0;
int hmax = 179, smax = 255, vmax = 255;

/**
 * @brief Create a Trackbar to allow HSV parameters changing
 */
void createTrackbar() {
    cv::namedWindow("Trackbar", cv::WINDOW_AUTOSIZE);
    cv::createTrackbar("Hue Min", "Trackbar", &hmin, 179);
    cv::createTrackbar("Hue Max", "Trackbar", &hmax, 179);
    cv::createTrackbar("Sat Min", "Trackbar", &smin, 255);
    cv::createTrackbar("Sat Max", "Trackbar", &smax, 255);
    cv::createTrackbar("Val Min", "Trackbar", &vmin, 255);
    cv::createTrackbar("Val Max", "Trackbar", &vmax, 255);
}

/**
 * @brief Create trackbar for dynamic color filtering using sampled images as input
 */
void findColorSpectrumSampleImage(const std::string &imagePath) {
    createTrackbar();
    cv::Mat image = cv::imread(imagePath), hsv, mask;

    while(true) {
        cvtColor(image, hsv, cv::COLOR_BGR2HSV);
        cv::Scalar lower(hmin, smin, vmin);
        cv::Scalar upper(hmax, smax, vmax);
        inRange(hsv, lower, upper, mask);

        cv::imshow("Original image", image);
        cv::imshow("Masked image", mask);
        cv::waitKey(1);
    }
}

/**
 * @brief Create trackbar for dynamic color filtering using video capture as input
 */
void findColorSpectrumVideo() {
    createTrackbar();
    cv::VideoCapture cap(0);
    cv::Mat image, hsv, mask;

    while(cap.isOpened()) {
        cap >> image;
        cv::cvtColor(image, hsv, cv::COLOR_BGR2HSV);
        cv::Scalar lower(hmin, smin, vmin);
        cv::Scalar upper(hmax, smax, vmax);
        cv::inRange(hsv, lower, upper, mask);
        
        cv::imshow("Original image", image);
        cv::imshow("Masked image", mask);
        cv::waitKey(1);
    }
}
