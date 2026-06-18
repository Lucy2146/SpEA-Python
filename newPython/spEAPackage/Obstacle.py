import math

from .Node import Node
from .ObNode import ObNode


class Obstacle:
    #defines a polygon obstacle in the plane that can be added to the graph
    EPSILON = 1e-10
    NO = 0 #if there is an intersecting point
    YES = 1
    COLINEAR = 2

    def __init__(self, points):
        assert len(points) >= 3, "Not a polygon"
        assert points[0] != points[-1], "Polygon closes automatically"

        self.points = points  #array of corner points
        self.solid = True #whether it is a solid or soft obstacle
        self.crossCost = float("inf") #cost per unit of intersecting line going through the obstacle

        self.setBoundingBox()

        assert not self.selfIntersect(), "Self-intersecting polygon"

    # --------------------------------------------------
    # Bounding box
    # [lowerX, upperX, lowerY, upperY]
    # --------------------------------------------------
    def setBoundingBox(self):
        xs = [p.x for p in self.points]
        ys = [p.y for p in self.points]

        self.boundbox = [
            min(xs), max(xs),
            min(ys), max(ys)
        ]

    def getBoundingBox(self):
        return self.boundbox

    # --------------------------------------------------
    # Obstacle type: changing obstacle type to allow for crossing through
    # distance is always in km
    # --------------------------------------------------
    def makeSoft(self, cross_cost):
        if cross_cost < 1.0:
            raise ValueError("Cross cost too small")

        self.solid = False
        self.crossCost = cross_cost

    def makeSolid(self):
        self.solid = True
        self.crossCost = float("inf")

    def isSolid(self):
        return self.solid

    def getPoints(self):
        return self.points

    def getCrossCosts(self):
        return self.crossCost

    # --------------------------------------------------
    # Containment: returns true if the given node is one of the obstacles corners
    # --------------------------------------------------
    def containsCornerNode(self, node):
        return any(node == p for p in self.points)

    # checks if the given node is inside the obstacle, true if inside
    def containsNode(self, node):
        bx = self.boundbox

        # bounding box check
        if (
            node.x < bx[0] - self.EPSILON or node.x > bx[1] + self.EPSILON or
            node.y < bx[2] - self.EPSILON or node.y > bx[3] + self.EPSILON
        ):
            return False

        # check if point is on the boundary, if yes return false
        for i in range(len(self.points)):
            if self.nodeOnEdge(node, self.points[i], self.points[(i + 1) % len(self.points)]):
                return False

        # ray casting
        ray_start = Node(bx[1] + 0.1, bx[2] + (bx[3] - bx[2]) / 2)
        ray_end = node

        #line segment ray in linear equation in std form: ax + by + c = 0
        a_ray = ray_end.y - ray_start.y
        b_ray = ray_start.x - ray_end.x
        c_ray = ray_end.x * ray_start.y - ray_start.x * ray_end.y

        crosses = 0
        for i in range(len(self.points)):
            #count the intersections with the ray segment only
            crosses += self.intersecting(
                ray_start, ray_end,
                self.points[i],
                self.points[(i + 1) % len(self.points)],
                a_ray, b_ray, c_ray,
                segment_only=True
            )

        return crosses % 2 == 1

    # --------------------------------------------------
    # Geometry helpers
    # --------------------------------------------------
    @staticmethod
    # checks whether given node is on given edge of polygon, including edge points
    def nodeOnEdge(self, node, start, end):
        if (
            node.x > max(start.x, end.x) + self.EPSILON or
            node.x < min(start.x, end.x) - self.EPSILON or
            node.y < min(start.y, end.y) - self.EPSILON or
            node.y > max(start.y, end.y) + self.EPSILON
        ):
            return False

        #line edge in linear equation std form
        a = end.y - start.y
        b = start.x - end.x
        c = end.x * start.y - start.x * end.y

        #every node that solves the eqaution is on the line:
        d = a * node.x + b * node.y + c

        return abs(d) < self.EPSILON # true if the node lies on the infinite line and within EPSILON range of the actual line segment
    


    #checks whether the given ray line intersects  a given polygon edge line
	# If the end point of the ray line touches the boundary, this also returns YES
	# unless the obstacle corner node touches the ray line. In this case there are two possibilities:
	#  1) If the other end node of the obstacle edge is on the right of the ray line: return NO
	#  2) If the other end node of the obstacle edge is on the left of the ray line: return YES
	# Returning NO means there is no intersection point (or see above)
	# Returning YES if there is an intersection (apart from above)
	# Returning COLINEAR if both line segments are co-linear (not necessarily intersecting) 
    def intersecting(self, raystart, rayend, edgestart, edgeend,
                      a_ray, b_ray, c_ray, segment_only):

        #every node that solves the equation is on the lines
        d_ray1 = a_ray * edgestart.x + b_ray * edgestart.y + c_ray
        d_ray2 = a_ray * edgeend.x + b_ray * edgeend.y + c_ray

        #if d_ray1 and d_ray2 have the same sign then the ndoes are on the same side of the infinite ray
        # 0 means the node is on the ray infinite line
        if (d_ray1 >= self.EPSILON and d_ray2 >= self.EPSILON) or \
           (d_ray1 <= -self.EPSILON and d_ray2 <= -self.EPSILON):
            return self.NO

        #if the other point is o the right side
        if abs(d_ray1) < self.EPSILON and d_ray2 >= self.EPSILON:
            return self.NO
        if abs(d_ray2) < self.EPSILON and d_ray1 >= self.EPSILON:
            return self.NO

        #the edge intersected the infinite line above
        a_edge = edgeend.y - edgestart.y
        b_edge = edgestart.x - edgeend.x
        c_edge = edgeend.x * edgestart.y - edgestart.x * edgeend.y

        if segment_only:
            d_edge1 = a_edge * raystart.x + b_edge * raystart.y + c_edge
            d_edge2 = a_edge * rayend.x + b_edge * rayend.y + c_edge

            #if both have the same sign and neither one is 0 then no intersection is possible
            if (d_edge1 >= self.EPSILON and d_edge2 >= self.EPSILON) or \
               (d_edge1 <= -self.EPSILON and d_edge2 <= -self.EPSILON):
                return self.NO

        #now either the line segments are colinear or intersect exactly at one point
        if abs(a_ray * b_edge - a_edge * b_ray) < self.EPSILON:
            return self.COLINEAR

        #if not colinear then they intersect in exactly one spot
        return self.YES

    # --------------------------------------------------
    # Intersections: all intersections between lien segment and obstacle
    # --------------------------------------------------
    def allIntersections(self, line_start, line_end, a_line, b_line, c_line):
        crossings = []

        #call method intersecting for each edge of the obstacle and
		#if there is an intersection calculate the cross point and add to the list
        for i in range(len(self.points)):
            e1 = self.points[i]
            e2 = self.points[(i + 1) % len(self.points)]

            res = self.intersecting(
                line_start, line_end, e1, e2,
                a_line, b_line, c_line,
                segment_only=False
            )

            if res == 1:
                a_edge = e2.y - e1.y
                b_edge = e1.x - e2.x
                c_edge = e2.x * e1.y - e1.x * e2.y

                if abs(b_line) < self.EPSILON: #line is vertical
                    x = line_start.x
                    y = -(c_edge + a_edge * x) / b_edge
                elif abs(b_edge) < self.EPSILON: #edge is vertical
                    x = e1.x
                    y = -(c_line + a_line * x) / b_line
                else:
                    x = (c_edge * b_line - b_edge * c_line) / (a_line * b_edge - a_edge * b_line)
                    y = -(c_line + a_line * x) / b_line

                crossings.append(Node(x, y))

            elif res == 2: #lines are colinear
                #both corner points can be added as they will be outside the obstacle
                crossings.extend([e1, e2])

        return crossings


    #checks whether a given node is within a certain range of the bounding box
    def withinRange(self, node, range_x, range_y):
        # bounding box: [lowerX, upperX, lowerY, upperY]
        if node.x + range_x < self.boundbox[0] or node.x - range_x > self.boundbox[1]:
            return False
        if node.y + range_y < self.boundbox[2] or node.y - range_y > self.boundbox[3]:
            return False

        return True #true iff bounding boxes cross
    

    # --------------------------------------------------
    # Distance through obstacle: calc cost of a line intersecting the obstacle
    # if solid then returns inf
    # --------------------------------------------------
    def calculateLineCrossDist(self, line_start, line_end):
        intersect_dist = 0
        if line_start == line_end:
            return 0.0

        bx = self.boundbox

        if ( #check if the line is actually in reach of the obstacle
            max(line_start.x, line_end.x) < bx[0] - self.EPSILON or
            min(line_start.x, line_end.x) > bx[1] + self.EPSILON or
            max(line_start.y, line_end.y) < bx[2] - self.EPSILON or
            min(line_start.y, line_end.y) > bx[3] + self.EPSILON
        ):
            return 0.0

        #line segment ray in std lienar equation form
        a = line_end.y - line_start.y
        b = line_start.x - line_end.x
        c = line_end.x * line_start.y - line_start.x * line_end.y

        #get all intersections of the line with this obstacle
        crossings = self.allIntersections(line_start, line_end, a, b, c)

        #add the lines start and end points
        crossings.extend([line_start, line_end])

        # reference point outside the line and obstacle (but in line with the line)
        if abs(b) < self.EPSILON: #vertical line
            star = Node(line_start.x, min(line_start.y, line_end.y, bx[2]) - 0.1)
        else:
            if b==0: print("calcLineCrossingDist b = 0!")
            star_x = min(line_start.x, line_end.x, bx[0]) - 0.1
            star_y = (-c - a * star_x) / b
            star = Node(star_x, star_y)

        #sorting by distance to reference point, star node
        crossings.sort(key=lambda n: n.distanceSqrTo(star))
        for n in crossings:
            if math.isinf(n.x) or math.isinf(n.y) or math.isnan(n.x) or math.isnan(n.y):
                print("Bad node detected:", n)

        csize = len(crossings)
        inside = False #starting at star node
        onEdge = False
        sectionStart = star
        seenFirstNode = False
        seenSecondNode = False
        i = 0

        while (i < csize and not seenSecondNode):
            if( isinstance(sectionStart, ObNode)):
                onEdge = not onEdge #checking if we are on an obstacle edge
            sectionEnd = crossings[i]

            if (sectionEnd.__eq__(line_start) or sectionEnd.__eq__(line_end)):
                if (not seenFirstNode):
                    seenFirstNode = True
                    sectionStart = sectionEnd
                    i += 1
                    sectionEnd = crossings[i] #set next node
                    if (sectionEnd.__eq__(line_start) or sectionEnd.__eq__(line_end)):
                        seenSecondNode = True
                else:
                    seenSecondNode = True 


            if (inside and seenFirstNode and not onEdge):
                dist = sectionStart.distanceTo(sectionEnd)
                if (dist > self.EPSILON):
                    if(self.solid): return self.crossCost
                    intersect_dist += dist
            
            inside = not inside

            sectionStart = sectionEnd
            i += 1

        if(intersect_dist < self.EPSILON): return 0
        print('length inside obstacle: ', intersect_dist)
        return intersect_dist

    # --------------------------------------------------
    # Self intersection
    # --------------------------------------------------
    
    def selfIntersect(self):
        for i in range(len(self.points)):
            s1 = self.points[i]
            e1 = self.points[(i + 1) % len(self.points)]

            for j in range(i, len(self.points)):
                s2 = self.points[j]
                e2 = self.points[(j + 1) % len(self.points)]

                if self.twoLinesCross(s1, e1, s2, e2) is not None:
                    return True

        return False


    #check whether two lines cross (not just touch)
    def twoLinesCross(self, s1, e1, s2, e2):
        denom1 = e1.x - s1.x
        denom2 = e2.x - s2.x

        if denom1 == 0 or denom2 == 0:
            if denom1 == denom2: return None
            if denom1 == 0: #line 1 is vertical
                x = s1.x
                m2 = (e2.y - s2.y) / denom2
                b2 = s2.y - m2 * s2.x
                y = m2*x + b2
                if (y < max(s1.y, e1.y) and  y >min( s1.y, e1.y) and x < max(s2.x, e2.x) and x> min(s2.x, e2.x)):
                    return Node(x, y)
                return None
            else: #denom2 == 0, line 2 is vertical
                x = s2.x
                m1 = (e1.y - s1.y) / denom1
                b1 = s1.y - m1 * s1.x
                y = m1*x + b1
                if (y < max(s2.y, e2.y) and  y >min( s2.y, e2.y) and x < max(s1.x, e1.x) and x> min(s1.x, e1.x)):
                    return Node(x, y)
                return None

        m1 = (e1.y - s1.y) / denom1
        b1 = s1.y - m1 * s1.x


        m2 = (e2.y - s2.y) / denom2
        b2 = s2.y - m2 * s2.x

        if abs(m1 - m2) < self.EPSILON:
            return None

        x = (b2 - b1) / (m1 - m2)
        y = m1 * x + b1

        if ( x < max(s1.x, e1.x) - self.EPSILON and
             x > min(s1.x, e1.x) + self.EPSILON and 
             x < max(s2.x, e2.x) - self.EPSILON and
             x > min(s2.x, e2.x) + self.EPSILON):
            return Node(x, y)

        return None