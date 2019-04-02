import numpy as np
import cv2
import dlib
from app import app
from imutils import face_utils
import argparse


def _apply_affine_transform(src, src_tri, dst_tri, size):
    """
    Apply affine transform calculated using src_tri and dst_tri to src and output an image of size.
    :param src: source image
    :param src_tri: source delanauy triangle
    :param dst_tri: destinator delanauy triangle
    :param size: size of surce image
    :return: output with affine transformation
    """
    # Given a pair of triangles, find the affine transform.
    warp_mat = cv2.getAffineTransform(np.float32(src_tri), np.float32(dst_tri))

    # Apply the Affine Transform just found to the src image
    dst = cv2.warpAffine(src, warp_mat, (size[0], size[1]), None, flags=cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_REFLECT_101)

    return dst


def _in_rectangle(rect, point):
    """
    Check if a point is inside a rectangle
    :param rect: rectangle points
    :param point: point
    :return: True if point in rectangle otherwise False
    """
    if point[0] < rect[0]:
        return False
    elif point[1] < rect[1]:
        return False
    elif point[0] > rect[0] + rect[2]:
        return False
    elif point[1] > rect[1] + rect[3]:
        return False
    return True


#
def _calculate_delaunay_triangles(rect, points):
    """
    Calculate delanauy triangle.
    See: https://www.learnopencv.com/delaunay-triangulation-and-voronoi-diagram-using-opencv-c-python/
    :param rect: rectangle
    :param points: face landamrks
    :return: delaunay triangle
    """
    # create subdiv
    subdiv = cv2.Subdiv2D(rect)

    # Insert points into subdiv
    for p in points:
        subdiv.insert(p)

    triangle_list = subdiv.getTriangleList()

    delaunay_triangles = []

    pt = []

    for t in triangle_list:
        pt.append((t[0], t[1]))
        pt.append((t[2], t[3]))
        pt.append((t[4], t[5]))

        pt1 = (t[0], t[1])
        pt2 = (t[2], t[3])
        pt3 = (t[4], t[5])

        if _in_rectangle(rect, pt1) and _in_rectangle(rect, pt2) and _in_rectangle(rect, pt3):
            ind = []
            # Get face-points (from 68 face detector) by coordinates
            for j in range(3):
                for k in range(len(points)):
                    if abs(pt[j][0] - points[k][0]) < 1.0 and abs(pt[j][1] - points[k][1]) < 1.0:
                        ind.append(k)
                        # Three points form a triangle. Triangle array corresponds to the file tri.txt in FaceMorph
            if len(ind) == 3:
                delaunay_triangles.append((ind[0], ind[1], ind[2]))

        pt = []

    return delaunay_triangles


#
def _warp_triangle(img1, img2, t1, t2):
    """
    Warps and alpha blends triangular regions from img1 and img2 to img
    :param img1: source image
    :param img2: warped image
    :param t1: delaunay triangles for img1
    :param t2: delaunay triangles for img2
    """

    # Find bounding rectangle for each triangle
    r1 = cv2.boundingRect(np.float32([t1]))
    r2 = cv2.boundingRect(np.float32([t2]))

    # Offset points by left top corner of the respective rectangles
    t1_rect = []
    t2_rect = []
    t2_rect_int = []

    for i in range(3):
        t1_rect.append(((t1[i][0] - r1[0]), (t1[i][1] - r1[1])))
        t2_rect.append(((t2[i][0] - r2[0]), (t2[i][1] - r2[1])))
        t2_rect_int.append(((t2[i][0] - r2[0]), (t2[i][1] - r2[1])))

    # Get mask by filling triangle
    mask = np.zeros((r2[3], r2[2], 3), dtype=np.float32)
    cv2.fillConvexPoly(mask, np.int32(t2_rect_int), (1.0, 1.0, 1.0), 16, 0)

    # Apply warpImage to small rectangular patches
    img1_rect = img1[r1[1]:r1[1] + r1[3], r1[0]:r1[0] + r1[2]]
    # img2Rect = np.zeros((r2[3], r2[2]), dtype = img1Rect.dtype)

    size = (r2[2], r2[3])

    img2_rect = _apply_affine_transform(img1_rect, t1_rect, t2_rect, size)

    img2_rect = img2_rect * mask

    # Copy triangular region of the rectangular patch to the output image
    img2[r2[1]:r2[1] + r2[3], r2[0]:r2[0] + r2[2]] = img2[r2[1]:r2[1] + r2[3], r2[0]:r2[0] + r2[2]] * (
            (1.0, 1.0, 1.0) - mask)

    img2[r2[1]:r2[1] + r2[3], r2[0]:r2[0] + r2[2]] = img2[r2[1]:r2[1] + r2[3], r2[0]:r2[0] + r2[2]] + img2_rect


def _extract_landmarks(img, detector, predictor):
    """
    Extract landmarks from given image
    :param img: image
    :param detector: detect if in image there is a face
    :param predictor: detect landmarks ponits
    :return: list of tuples landmarks points
    """

    # Convert frame to gray
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # detect faces in the grayscale frame
    faces = detector(gray, 0)

    if len(faces) != 1:  # make sure if there is only 1 face into webcam
        return None

    # extract landmarks from face
    shape = predictor(gray, faces[0])
    landmarks = face_utils.shape_to_np(shape)

    return list(map(tuple, landmarks))


def face_swap(img1, img2):
    """
    Make face swap between two images
    :param img1: source image
    :param img2: warped image
    :return: faced output
    """
    # Load models
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(app.config["FACE_LANDMARKS_PATH"])

    # Read images
    img1_warped = np.copy(img2)

    # Extract landmarks from given faces
    points1 = _extract_landmarks(img1, detector, predictor)
    points2 = _extract_landmarks(img2, detector, predictor)

    # Find convex hull
    hull1 = []
    hull2 = []

    hull_index = cv2.convexHull(np.array(points2), returnPoints=False)

    for i in range(len(hull_index)):
        hull1.append(points1[int(hull_index[i])])
        hull2.append(points2[int(hull_index[i])])

    # Find delanauy traingulation for convex hull points
    rect = (0, 0, img2.shape[1], img2.shape[0])

    dt = _calculate_delaunay_triangles(rect, hull2)

    if len(dt) == 0:
        quit()

    # Apply affine transformation to Delaunay triangles
    for i in range(len(dt)):
        t1 = []
        t2 = []

        # get points for img1, img2 corresponding to the triangles
        for j in range(3):
            t1.append(hull1[dt[i][j]])
            t2.append(hull2[dt[i][j]])

        _warp_triangle(img1, img1_warped, t1, t2)

    # Calculate Mask
    hull8u = []
    for i in range(len(hull2)):
        hull8u.append((hull2[i][0], hull2[i][1]))

    mask = np.zeros(img2.shape, dtype=img2.dtype)

    cv2.fillConvexPoly(mask, np.int32(hull8u), (255, 255, 255))

    r = cv2.boundingRect(np.float32([hull2]))

    center = (r[0] + int(r[2] / 2), r[1] + int(r[3] / 2))

    # Clone seamlessly.
    output = cv2.seamlessClone(np.uint8(img1_warped), img2, mask, center, cv2.NORMAL_CLONE)

    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Wear eyeglasses')
    parser.add_argument('--source-image', help='Input face path')
    parser.add_argument('--warped-image', help='Input face path')
    args = parser.parse_args()

    output = face_swap(cv2.imread(args.source_image), cv2.imread(args.warped_image))

    cv2.imshow("Face Swapped", output)
    cv2.waitKey(0)

    cv2.destroyAllWindows()
