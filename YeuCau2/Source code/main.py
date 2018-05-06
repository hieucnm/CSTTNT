
import time
import math

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection


def Linear_Equation(u,v):
	a = v.y - u.y
	b = u.x - v.x
	c = u.x*(u.y - v.y) + u.y*(v.x - u.x)
	return [a, b, c]

def GetPoints(string):
	# tách các điểm ra bằng kí tự khoảng trắng
	bufs = string.split()
	points = []
	#  với mổi điểm đã tách, lại tách hoành độ và tung độ bằng dấu phẩy
	for buf in bufs:
		temp = buf.split(",")
		points.append(MyPoint(int(temp[0]) , int(temp[1])))
	return points

def LoadData(fileName):
	f = open(fileName);
	s = f.readline(); # đọc số đa giác
	n = int(s);
	if n < 1:
		raise ValueError("Number of polygon must be greater than 0!")
	s = f.readline(); # đọc đỉnh start và đỉnh goal
	start , goal = GetPoints(s);
	
	polygons = [];
	# đọc danh sách đỉnh các đa giác
	for i in range(n):
		s = f.readline();
		vertices = GetPoints(s);
		polygon = MyPolygon(vertices)
		polygons.append(polygon)
		pass
	return polygons, start, goal, n

def PlotData(polygons,start,goal):
	fig, ax = plt.subplots()
	
	# vẽ các đa giác
	pch = []
	for myPolygon in polygons:
		# chuyển đối tượng MyPolygon thành dối tượng Polygon của matplotlib để vẽ hình
		polygon = Polygon([(p.x,p.y) for p in myPolygon.vertices])
		pch.append(polygon)
	p = PatchCollection(pch, alpha = 0.4)
	ax.add_collection(p)

	# vẽ 2 điểm start và goal
	ax.plot(start.x, start.y, '*', color = 'red')
	ax.plot(goal.x, goal.y, '*', color = 'red')
	ax.annotate("S",(start.x, start.y), color = 'red')
	ax.annotate("G",(goal.x, goal.y), color = 'red')
	return fig, ax

class MyPoint:
	""" Mỗi đối tượng MyPoint gồm:
	# x,y    : tọa độ điểm
	# G      : chi phí đi từ điểm start đến điểm đang xét
	# H      : heuristic của điểm đang xét, ở đây em cho là khoảng cách tới goal
	# parent : nút cha, dùng để truy vết
	"""

	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.G = 0
		self.H = 0
		self.parent = None

	# định nghĩa toán tử so sánh bằng ==
	def __eq__ (self, other):
		if self.x == other.x and self.y == other.y:
			return True
		return False

	def index_in (self, pointList):
		n = len(pointList)
		for i in range(n):
			if pointList[i] == self:
				return i
		return None

	# phương thức phát sinh các nút lân cận từ 8 hướng xung quanh
	def movable_nodes(self, polygons):
		x = self.x
		y = self.y
		children = []
		for i in range(-1,2):
			for j in range(-1,2):
				children.append(MyPoint(x+i,y+j))

		children.remove(self)
		movable = []
		for v in children:
			if v.x < 0 or v.y < 0:
				continue
			is_valid = True
			for poly in polygons:
				if poly.contains_point(self,v):
					is_valid = False
					break
			if is_valid == True:
				movable.append(v)
		return movable
	
	# phương thức tính khoảng cách tới nút khác, bằng khoảng cách euclide
	def Distance(self, other):
		return math.sqrt( (self.x - other.x)**2 + (self.y - other.y)**2 )

	def move_cost(self, other):
		return self.Distance(other)

	# phương thức tính Heuristic của nút, dựa vào khoảng cách tới điểm goal
	def Heuristic(self, goal):
		# return self.Distance(goal)
		if abs(goal.y - self.y) <= abs(goal.x - self.x) :
			# tạo điểm T trung gian, sau đó trả về self.Distance(T) + T.Distance(G)
			if self.x <= goal.x:
				x_T = goal.x - abs(goal.y - self.y)
			else:
				x_T = goal.x + abs(goal.y - self.y)
			return abs(self.x - x_T) + abs(goal.y - self.y)*math.sqrt(2)
		else:
			if self.y <= goal.y:
				y_T = goal.y - abs(goal.x - self.x)
			else:
				y_T = goal.y + abs(goal.x - self.x)
			return abs(self.y - y_T) + abs(goal.x - self.x)*math.sqrt(2)

class MyPolygon:
	""" Mỗi đối tượng MyPolygon gồm 3 thuộc tính
	# 	vertices:danh sách tọa độ các đỉnh đa giác
	# 	edges: danh sách hệ số a,b,c của phương trình chứa các cạnh đa giác (có dạng ax + by + c = 0)
	# 	boundingbox: hình CN bao quanh đa giác, gồm tọa độ 2 đỉnh topRight(x_max, y_max) và bottomLeft(x_min, y_min)
	"""

	def __init__(self, vertices):
		self.vertices = vertices 
		self.vertices.append(MyPoint(self.vertices[0].x , self.vertices[0].y)) # thêm đỉnh đầu tiên			
		self.edges = self.getEdges()		
		self.boundingbox = self.calculate_boundingbox()

	# phương thức tính hệ số a,b,c của phương trình các cạnh đa giác
	def getEdges(self):
		edges = []
		num_vertices = len(self.vertices) - 1
		for i in range(num_vertices):
			edges.append(Linear_Equation(self.vertices[i] , self.vertices[i+1]))
		return edges

	# phương thức tính tọa độ đỉnh Trái_dưới (botomLeft) và Phải_trên (topRight) của boundingbox
	def calculate_boundingbox(self):
		x_max = x_min = self.vertices[0].x
		y_max = y_min = self.vertices[0].y
		for v in self.vertices:
			if v.x > x_max:
				x_max = v.x
			if v.x < x_min:
				x_min = v.x
			if v.y > y_max:
				y_max = v.y
			if v.y < y_min:
				y_min = v.y
		return [ MyPoint(x_min, y_min) , MyPoint(x_max, y_max) ]

	# phương thức kiểm tra đỉnh v , là đỉnh lân cận với đỉnh u, có nằm trong đa giác hay ko
	# biết đỉnh u nằm ngoài đa giác
	def contains_point(self, u, v):
		bottomLeft = self.boundingbox[0]
		topRight = self.boundingbox[1]
		# kiểm tra xem đỉnh v có nằm ngoài boundingbox hay ko
		# nếu nằm ngoài boundingbox thì chắc chắn nó nằm ngoài đa giác, nếu nằm trong thì mới duyệt các cạnh
		if v.x < bottomLeft.x or v.y < bottomLeft.y or v.x > topRight.x or v.y > topRight.y:
			return False

		# duyệt các cạnh đa giác, áp dụng giải thuật Ray Tracing
		num_vertices = len(self.vertices) - 1
		for i in range(num_vertices):
			t_u = self.edges[i][0]*u.x + self.edges[i][1]*u.y + self.edges[i][2]
			t_v = self.edges[i][0]*v.x + self.edges[i][1]*v.y + self.edges[i][2]

			# nếu t_v = 0, tức đỉnh v nằm trên 1 cạnh của đa giác
			if t_v == 0:
				return True

			# nếu t_u*t_v > 0, tức u và v nằm cùng phía với cạnh này, ta ko kết luận được gì => continue
			# nếu tất cả các cạnh đều rơi vào trường hợp này, tức u và v nằm cùng phía với tất cả cạnh
			# 	thì v nằm ngoài đa giác, hết vòng for sẽ return False
			if t_u*t_v > 0:
				continue

			# nếu rơi vào trường hợp t_u*t_v < 0, tức u và v nằm khác phía của cạnh này,
			# 	Ta viết phương trình đường thẳng (d) tạo bởi 2 đỉnh u và v
			a ,b ,c = Linear_Equation(u, v)
			t_A = a*self.vertices[i].x + b*self.vertices[i].y + c
			t_B = a*self.vertices[i+1].x + b*self.vertices[i+1].y + c
			
			# 	Nếu 2 đỉnh tạo nên cạnh này nằm khác phía với đường thẳng (d),
			#	thì ta ko thể chọn đi v, vì nếu đi thì đường đi từ u tới v sẽ cắt cạnh của đa giác
			if t_A*t_B <= 0:
				return True
		return False

def Expand_ASS(openset, visited, polygons, u, goal):
	for v in u.movable_nodes(polygons):
		
		if v in visited:
			continue

		index_v = v.index_in(openset)
		if index_v:
			g_v_new = u.G + u.move_cost(v)
			if g_v_new < openset[index_v].G:
				openset[index_v].G = g_v_new
				openset[index_v].parent = u
		else:
			v.G = u.G + u.move_cost(v)
			v.H = v.Heuristic(goal);
			v.parent = u;
			openset.append(v)
	pass

def GBFS(polygons, start, goal):
	
	# openset là tập chứa các đỉnh đã mở
	# visited là tập chứa các đỉnh đã thăm
	# khởi tạo các giá trị:
	openset = [];
	visited = [];
	start.H = start.Heuristic(goal);
	openset.append(start);
	while openset:
		# lấy node có h(u) nhỏ nhất từ openset
		u = min(openset, key = lambda x: x.H);
		# nếu tìm thấy thì trả về đường đi
		if u == goal:
			# trả về path
			path = [];
			while u:
				path.append(u);
				u = u.parent;
			return path[::-1];
			
		# xóa node đang xét khỏi openset, thêm nó vào tập các nút đã thăm
		openset.remove(u);
		visited.append(u);
	
		# trong các nút lân cận với nút đang xét, nút nào không nằm trong các đa giác thì ta mở
		for v in u.movable_nodes(polygons):
			# nếu nút đó đã thăm thì ta bỏ qua
			if v in visited :
				continue;
			
			if v not in openset:
				v.H = v.Heuristic(goal);
				v.parent = u;
				openset.append(v)
	return None;

def ASS(polygons, start, goal):
	
	# openset là tập chứa các đỉnh đã mở
	# visited là tập chứa các đỉnh đã thăm
	# khởi tạo các giá trị:
	openset = [];
	visited = [];
	start.H = start.Heuristic(goal);
	openset.append(start);
	while openset:
		# lấy node có f(u) = g(u) + h(u) nhỏ nhất từ openset
		u = min(openset, key = lambda x: x.G + x.H);
		# nếu tìm thấy thì trả về đường đi
		if u == goal:
			path = [];
			while u:
				path.append(u);
				u = u.parent;
			return path;
			
		# xóa node đang xét khỏi openset, thêm nó vào tập các nút đã thăm
		openset.remove(u);
		visited.append(u);
		Expand_ASS(openset, visited, polygons, u, goal)
	return None;

def GetPath(s_openset, g_openset, u):
	path = []
	v = u
	while v:
		path.append(v)
		v = v.parent
	path.reverse()
	for v in g_openset:
		if v == u:
			v = v.parent
			while v:
				path.append(v)
				v = v.parent
	return path

def bi_ASS(polygons, start, goal):
	s_openset = [];
	g_openset = [];
	s_visited = [];
	g_visited = [];
	start.H = start.Heuristic(goal);
	goal.H = goal.Heuristic(start);
	s_openset.append(start);
	g_openset.append(goal);
	while s_openset and g_openset:
		if s_openset:
			u_s = min(s_openset, key = lambda x: x.G + x.H);
			if u_s == goal or u_s in g_openset:
				return GetPath(s_openset, g_openset, u_s)
			s_openset.remove(u_s)
			s_visited.append(u_s);
			Expand_ASS(s_openset, s_visited, polygons, u_s, goal)
		
		if g_openset:
			u_g = min(g_openset, key = lambda x: x.G + x.H);
			if u_g == start or u_g in s_openset:
				return GetPath(s_openset, g_openset, u_g)
			g_openset.remove(u_g)
			g_visited.append(u_g)
			Expand_ASS(g_openset, g_visited, polygons, u_g, goal)
	return None;

def Count_Length(path):
	length = 0;
	for i in range(len(path) - 1):
		length += path[i].Distance(path[i+1])
	return length

def PlotPath(path, ax):
	xs = [p.x for p in path]
	ys = [p.y for p in path]
	ax.plot(xs,ys,'-o', color='green')

def main():

	polygons , start, goal, n= LoadData("input8.txt")
	fig, ax = PlotData(polygons,start,goal)

	print("Num of polygons: ",n)
	print("Start = (",start.x, start.y,") | Goal = (",goal.x, goal.y,")")

	begin = time.time()
	path = ASS(polygons, start, goal)
	print("Elapsed Time = ",time.time() - begin);
	
	# nếu có đường đi thì tính chiều dài và vẽ đường đi
	if path:
		print("Path found!")
		print("Path Length = ", Count_Length(path))
		PlotPath(path, ax)
	else:
		print("Path not found!")
	
	plt.grid(True)
	plt.show()


if __name__ == '__main__':
	main()
	
