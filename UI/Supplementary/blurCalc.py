import cv2
import numpy as np

def calculate_blur(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    lap_var = cv2.Laplacian(gray_image, cv2.CV_64F).var()
    return lap_var

def main():
    image_path = 'hi.jpg' 
    original_image = cv2.imread(image_path)


    height, width = original_image.shape[:2]

    rows = 6
    cols = 11
    region_height = height // rows
    region_width = width // cols

    result_image = original_image.copy()


    for row in range(rows):
        for col in range(cols):
            y1, y2 = row * region_height, (row + 1) * region_height
            x1, x2 = col * region_width, (col + 1) * region_width

            region = original_image[y1:y2, x1:x2]

            
            blur = calculate_blur(region)

           
            cv2.putText(
                result_image,
                f"Blur: {blur:.2f}",
                (x1 + 10, y2 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                1,
                cv2.LINE_AA
            )

            
            cv2.rectangle(result_image, (x1, y1), (x2, y2), (0, 255, 0), 1)

    cv2.imshow("Result", result_image)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()