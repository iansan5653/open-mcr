import pathlib
import image_utils
import corner_finding
import cv2
import grid_reading
import geometry_utils

sample_img_location = pathlib.Path(
    "C:\\Users\\Ian Sanders\\Git Repositories\\scantron-reading\\examples\\one.png"
)
sample_image = image_utils.get_image(sample_img_location)
points = corner_finding.find_corner_marks(sample_image)
sample_image_bw = image_utils.convert_to_bw(sample_image)

grid = grid_reading.Grid(points, 36, 51)
grid_centers = grid.get_all_centers()
grid_shapes = grid.get_all_shapes()
for center, shape in zip(grid_centers, grid_shapes):
    fill_pct = image_utils.get_fill_percent(sample_image_bw, shape)
    x = int(center.x)
    y = int(center.y)
    print(fill_pct)
    if fill_pct < 0.25:
        continue
    cv2.circle(sample_image, (x, y), 15, (0, int(255 * fill_pct), int(255 * (1 - fill_pct))), -1)

cv2.imshow("", sample_image)
cv2.waitKey()
#cv2.imwrite(str(sample_img_location.parent / "out.png"), sample_image)