from math import pi


class Robot:
    def __init__(self):
        self.reference_positions = []
        self.scan_data = []
        self.pole_indices = []
        self.motor_ticks = []
        self.filtered_positions = []
        self.filtered_stddev = []
        self.landmarks = []
        self.detected_landmarks = []
        self.world_landmarks = []
        self.world_ellipses = []
        self.particles = []
        self.last_ticks = None

    def read(self, filename):
        """Reads log data from file. Calling this multiple times with different
           files will result in a merge of the data, i.e. if one file contains
           M and S data, and the other contains M and P data, then LegoLogfile
           will contain S from the first file and M and P from the second file."""
        # If information is read in repeatedly, replace the lists instead of appending,
        # but only replace those lists that are present in the data.
        first_reference_positions = True
        first_scan_data = True
        first_pole_indices = True
        first_motor_ticks = True
        first_filtered_positions = True
        first_filtered_stddev = True
        first_landmarks = True
        first_detected_landmarks = True
        first_world_landmarks = True
        first_world_ellipses = True
        first_particles = True
        f = open(filename)
        for l in f:
            sp = l.split()
            # P is the reference position.
            # File format: P timestamp[in ms] x[in mm] y[in mm]
            # Stored: A list of tuples [(x, y), ...] in reference_positions.
            if sp[0] == 'P':
                if first_reference_positions:
                    self.reference_positions = []
                    first_reference_positions = False 
                self.reference_positions.append( (int(sp[2]), int(sp[3])) )

            # S is the scan data.
            # File format:
            #  S timestamp[in ms] distances[in mm] ...
            # Or, in previous versions (set s_record_has_count to True):
            #  S timestamp[in ms] count distances[in mm] ...
            # Stored: A list of tuples [ [(scan1_distance,... ), (scan2_distance,...) ]
            #   containing all scans, in scan_data.
            elif sp[0] == 'S':
                if first_scan_data:
                    self.scan_data = []
                    first_scan_data = False
                self.scan_data.append(tuple([float(s) for s in sp[3:]]))

            # I is indices of poles in the scan.
            # The indices are given in scan order (counterclockwise).
            # -1 means that the pole could not be clearly detected.
            # File format: I timestamp[in ms] index ...
            # Stored: A list of tuples of indices (including empty tuples):
            #  [(scan1_pole1, scan1_pole2,...), (scan2_pole1,...)...]
            elif sp[0] == 'I':
                if first_pole_indices:
                    self.pole_indices = []
                    first_pole_indices = False
                self.pole_indices.append(tuple([int(s) for s in sp[2:]]))

            # M is the motor data.
            # File format: M timestamp[in ms] pos[in ticks] tachoCount[in ticks] acceleration[deg/s^2] rotationSpeed[deg/s] ...
            #   (4 values each for: left motor, right motor, and third motor (not used)).
            # Stored: A list of tuples [ (inc-left, inc-right), ... ] with tick increments, in motor_ticks.
            # Note that the file contains absolute ticks, but motor_ticks contains the increments (differences).
            elif sp[0] == 'M':
                ticks = (float(sp[1]), float(sp[2]))
                if first_motor_ticks:
                    self.motor_ticks = []
                    first_motor_ticks = False
                    self.last_ticks = ticks
                self.motor_ticks.append(tuple(ticks))
                self.last_ticks = ticks

            # F is filtered trajectory. No time stamp is used.
            # File format: F x[in mm] y[in mm]
            # OR:          F x[in mm] y[in mm] heading[in radians]
            # Stored: A list of tuples, each tuple is (x y) or (x y heading)
            elif sp[0] == 'F':
                if first_filtered_positions:
                    self.filtered_positions = []
                    first_filtered_positions = False
                self.filtered_positions.append(tuple([float(s) for s in sp[1:]]))

            # E is error of filtered trajectory. No time stamp is used.
            # File format: E (angle of main axis)[in radians] std-dev1 std-dev2
            # OR:          The same format but with std-dev-heading appended.
            # Note: std-dev1 is along the main axis, std-dev2 is along the
            # second axis, which is orthogonal to the main axis.
            # Stored: A list of tuples, each tuple is
            # (angle, std-dev1, std-dev2) or
            # (angle, std-dev1, std-dev2, std-dev-heading).
            elif sp[0] == 'E':
                if first_filtered_stddev:
                    self.filtered_stddev = []
                    first_filtered_stddev = False
                self.filtered_stddev.append(tuple([float(s) for s in sp[1:]]))
                
            # L is landmark. This is actually background information, independent
            # of time.
            # File format: L <type> info...
            # Supported types:
            # landmark: L C x y diameter.
            # Stored: List of (<type> info) tuples.
            elif sp[0] == 'L':
                if first_landmarks:
                    self.landmarks = []
                    first_landmarks = False
                if sp[1] == 'C':
                    self.landmarks.append(tuple(['C'] + [f"{float(land)}" for land in sp[2:]]))
                    
            # D is detected landmarks (in each scan).
            # File format: D <type> info...
            # Supported types:
            # landmark: D C x y x y ...
            #   Stored: List of lists of (x, y) tuples of the landmark positions,
            #   one list per scan.
            elif sp[0] == 'D':
                if sp[1] == 'C':
                    if first_detected_landmarks:
                        self.detected_landmarks = []
                        first_detected_landmarks = False
                    cyl = sp[2:]
                    self.detected_landmarks.append([
                        (float(cyl[2 * i]), float(cyl[2 * i + 1]))
                        for i in range(int(len(cyl) / 2))
                    ])

            # W is information to be plotted in the world (in each scan).
            # File format: W <type> info...
            # Supported types:
            # landmark: W C x y x y ...
            #   Stored: List of lists of (x, y) tuples of the landmark positions,
            #   one list per scan.
            # Error ellipses: W E angle axis1 axis, angle axis1 axis2 ...
            #   where angle is the ellipse's orientations and axis1 and axis2 are the lenghts
            #   of the two half axes.
            #   Stored: List of lists of (angle, axis1, axis2) tuples.
            #   Note the ellipses can be used only in combination with "W C", which will
            #   define the center point of the ellipse.
            elif sp[0] == 'W':
                if sp[1] == 'C':
                    if first_world_landmarks:
                        self.world_landmarks = []
                        first_world_landmarks = False

                    cyl = sp[2:]
                    self.world_landmarks.append([
                        (float(cyl[2 * i]), float(cyl[2 * i + 1]))
                        for i in range(int(len(cyl) / 2))
                    ])
                elif sp[1] == 'E':
                    if first_world_ellipses:
                        self.world_ellipses = []
                        first_world_ellipses = False
                    ell = [float(s) for s in sp[2:]]
                    # ell = map(float, sp[2:])
                    self.world_ellipses.append([(ell[3*i], ell[3*i+1], ell[3*i+2]) for i in range(len(ell)//3)])

            # PA is particles.
            # File format:
            #  PA x0, y0, heading0, x1, y1, heading1, ...
            # Stored: A list of lists of tuples:
            #  [[(x0, y0, heading0), (x1, y1, heading1),...],
            #   [(x0, y0, heading0), (x1, y1, heading1),...], ...] 
            # where each list contains all particles of one time step.
            elif sp[0] == 'PA':
                if first_particles:
                    self.particles = []
                    first_particles = False
                i = 1
                particle_list = []
                while i < len(sp):
                    particle_list.append(tuple([float(s) for s in sp[i:i+3]]))
                    i += 3
                self.particles.append(particle_list)

        f.close()

    def info(self, i):
        """Prints reference pos, number of scan points, and motor ticks."""
        s = ""
        if i < len(self.reference_positions):
            s += " | ref-pos: %4d %4d" % self.reference_positions[i]

        if i < len(self.scan_data):
            s += " | scan-points: %d" % len(self.scan_data[i])

        if i < len(self.pole_indices):
            indices = self.pole_indices[i]
            if indices:
                s += " | pole-indices:"
                for idx in indices:
                    s += " %d" % idx
            else:
                s += " | (no pole indices)"
                    
        if i < len(self.motor_ticks):
            s += " | motor: %d %d" % self.motor_ticks[i]

        if i < len(self.filtered_positions):
            f = self.filtered_positions[i]
            s += " | filtered-pos:"
            for j in (0,1):
                s += " %.1f" % f[j]
            if len(f) > 2:
                s += " %.1f" % (f[2] / pi * 180.)

        if i < len(self.filtered_stddev):
            stddev = self.filtered_stddev[i]
            s += " | stddev:"
            # Print stddev in both axes, and theta, if present.
            # Don't print the orientation angle stddev[0].
            for j in (1,2):
                s += " %.1f" % stddev[j]
            if len(stddev) > 3:
                s += " %.1f" % (stddev[3] / pi * 180.)

        return s

    def size(self):
        """Return the number of entries. Take the max, since some lists may be empty."""
        return max(len(self.reference_positions), len(self.scan_data),
                   len(self.pole_indices), len(self.motor_ticks),
                   len(self.filtered_positions), len(self.filtered_stddev),
                   len(self.detected_landmarks), len(self.world_landmarks),
                   len(self.particles))
