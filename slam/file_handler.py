from math import atan2, sqrt, sin, cos
import numpy as np

# Write a list of landmarks to file
def write_landmarks(file_desc, line_header: str, cylinder_list: list) -> None:
    file_desc.write(f"{line_header}")
    for c in cylinder_list:
        c = (float(c[0]), float(c[1]))
        file_desc.write("%f %f " % c)
    file_desc.write("\n")


# Write error ellipses to file
def write_error_ellipses(file_desc, line_header: str, covariance_matrix_list: list) -> None:
    file_desc.write(f"{line_header} ")
    for m in covariance_matrix_list:
        eigenvals, eigenvects = np.linalg.eig(m)
        angle = atan2(eigenvects[1,0], eigenvects[0,0])
        file_desc.write("%f %f %f " % (angle, sqrt(eigenvals[0]), sqrt(eigenvals[1])))
    file_desc.write("\n")


# Write robot variance to file
def write_robot_variance(file_desc, line_header: str, error: list) -> None:
    file_desc.write(f"{line_header} ")
    file_desc.write("%f %f %f %f\n" % error)


# Write particle pose to file
def write_particle_pose(file_desc, line_header: str, mean: list, scanner_displacement: float) -> None:
    file_desc.write(f"{line_header} ")
    file_desc.write("%f %f %f\n" % \
        (mean[0] + cos(mean[2]) * scanner_displacement,
         mean[1] + sin(mean[2]) * scanner_displacement,
         mean[2]))

def write_particles(file_desc, line_header, particles):
    # Note this function would more likely be a part of FastSLAM or a base class
    # of FastSLAM. It has been moved here for the purpose of keeping the
    # FastSLAM class short in this tutorial.
    """Prints particles to given file_desc output."""
    if not particles:
        return
    file_desc.write(f"{line_header} ")
    for p in particles:
        file_desc.write("%f %f %f " % tuple(p.pose))
    file_desc.write("\n")