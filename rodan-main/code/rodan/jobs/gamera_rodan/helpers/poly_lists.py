from gamera.gameracore import Point


def create_polygon_outer_points_json_dict(poly_list):
    '''
        The following function is used to retrieve polygon points data of the first
        and last staff lines of a particular polygon that is drawn over a staff.
        Note that we iterate through the points of the last staff line in reverse (i.e starting
        from the last point on the last staff line going to the first) - We do this to simplify
        recreating the polygon on the front-end
    '''
    poly_json_list = []

    for poly in poly_list:
        if len(poly):
            last_index = len(poly) - 1
            point_list_one = [(vert.x, vert.y) for vert in poly[0].vertices]
            point_list_last = [(vert.x, vert.y) for vert in poly[last_index].vertices]
            point_list_last.reverse()
            point_list_one.extend(point_list_last)
            poly_json_list.append(point_list_one)

    return poly_json_list


def fix_poly_point_list(poly_list, staffspace_height):

    for poly in poly_list:
        # Check if there are the same number of points on all staff lines
        lengths = [len(line.vertices) for line in poly]
        if len(set(lengths)) == 1:
            continue
        else:
            # Loop over all the staff lines
            for j, line in enumerate(poly):
                # Loop over all the points of the staff
                for k, vert in enumerate(line.vertices):
                    # Loop over all the staff lines again
                    for l, innerline in enumerate(poly):
                        if l == j:
                            # Prevent looping through the same line as outer
                            continue

                        if k < len(innerline.vertices):
                            # Make sure k is in range first
                            y_pix_diff = vert.x - innerline.vertices[k].x
                        else:
                            # It's not in range - we're missing a point
                            # Set this to an arbitrary value to force an insert
                            y_pix_diff = -10000

                        if -3 < y_pix_diff < 3:
                            # If the y-coordinate pixel difference is small enough
                            continue
                        else:
                            # Missing a point on that staff
                            # The multiplier represents the # of lines apart
                            staffspace_multiplier = l - j
                            new_y = vert.y + (staffspace_multiplier * staffspace_height)
                            innerline.vertices.insert(k, Point(vert.x, new_y))

    return poly_list
