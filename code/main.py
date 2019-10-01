import pathlib
import image_utils
import corner_finding
import cv2
import grid_reading
import geometry_utils

images = [
    "SMITH", "SANDERS", "KAW", "ABCDEFGHIJ", "UNRELIABLE"
]

folder = pathlib.Path("C:\\Users\\Ian Sanders\\Git Repositories\\scantron-reading\\examples\\")
for image_name in images:
    image_path = folder / (image_name + ".jpg")
    image = image_utils.get_image(image_path)
    try:
        corners = corner_finding.find_corner_marks(image)
    except RuntimeError:
        print(f"{image_name}: Can't find corners.")
        continue
    image_bw = image_utils.convert_to_bw(image)
    grid = grid_reading.Grid(corners, 36, 51, image_bw)
    last_name = grid_reading.make_alphabet_group(grid, 1, 3, 12)
    values = [letter.read_value() for letter in last_name]
    print(f"{image_name}: {values}")




#for point in lmarks:
#    #fill_pct = image_utils.get_fill_percent(sample_image_bw, shape)
#    x = int(point.x)
#    y = int(point.y)
#    #print(fill_pct)
#    #if fill_pct < 0.25:
#    #    continue
#    cv2.circle(sample_image, (x, y), 5, (0, 255, 255), -1)
#
##cv2.imshow("", sample_image)
##cv2.waitKey()
#cv2.imwrite(str(sample_img_location.parent / "out.png"), sample_image)