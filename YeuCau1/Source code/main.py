
def LoadData(fileName):
	f = open(fileName);
	s = f.readline(); # đọc số đỉnh
	n = int(s);
	s = f.readline(); # đọc đỉnh start và đỉnh goal
	temp = s.split(' ');
	start = int(temp[0]);
	goal = int(temp[1]);
	
	matrix = []; # đọc ma trận kề
	for i in range(n):
		s = f.readline();
		temp = s.split(' ');
		matrix.append([]);
		for j in range(n):
			matrix[i].append(int(temp[j]));

	heuristic = []; # đọc các số heuristic của mỗi đỉnh
	s = f.readline();
	temp = s.split(' ');
	for i in range(n):
		heuristic.append(int(temp[i]));
	f.close();
	return matrix, n, start, goal, heuristic;

def WritePath(fileName, visited, path):
	res = "";
	for i in range(len(visited)):
		res += str(visited[i]) + " ";

	res += '\n';
	for i in range(len(path)):
		res += str(path[i]) + " ";
	res += '\n';
	f = open(fileName, "w");
	f.write(res);
	f.close();
	pass

def PrintData(matrix, n , heuristic, start, goal):
	for row in matrix:
		print(row);
	print("n = ",n, ", Start = ", start, ", Goal = ", goal);
	print("Heuristic: ", heuristic);

def GetPath(start, goal, trace):
	res = [];
	u = goal;
	while u != start:
		res.append(u);
		u = trace[u];
	res.append(u);
	return res[::-1];

def DFS(matrix, start, goal, n):
	trace = [-1]*(n+1);		# lưu vết và đánh dấu, trace = -1 nếu chưa thăm
	stack = [start];		# stack chứa các đỉnh chuẩn bị duyệt
	visited = [];			# danh sách lưu các đỉnh đã thăm
	trace[start] = -2;		# gán giá trị khác -1 cho start để đánh dấu đã thăm
	while  stack:
		u = stack.pop();
		visited.append(u);

		# nếu tìm thấy, trả về danh sách các đỉnh đã thăm và đường đi
		if u == goal:
			return visited , GetPath(start, goal, trace);

		# duyệt backward, để lấy phần tử có chỉ mục nhỏ hơn ra khỏi stack trước
		for v in range(n - 1,-1,-1):
			# nếu có cạnh nối và chưa thăm thì bỏ vào stack
			if matrix[u][v] != 0 and trace[v] == -1 :
				stack.append(v);
				trace[v] = u;
	# nếu không tìm thấy goal thì trả về -1
	return visited, -1;

def BFS(matrix, start, goal, n):
	# BFS dùng queue thay cho stack và vòng for chạy forward
	# vai trò các biến còn lại tương tự DFS
	trace = [-1]*(n+1);
	queue = [start];
	visited = [];
	trace[start] = -2;
	while queue:
		u = queue.pop(0);
		visited.append(u);
		if u == goal:
			return visited, GetPath(start, goal, trace);
		for v in range(n):
			if matrix[u][v] != 0 and trace[v] == -1:
				queue.append(v);
				trace[v] = u;
	return visited, -1;

def UCS(matrix, start, goal, n):
	# openset là tập chứa các nút đã mở, gồm 2 phần tử { u, g(u)}
	# visited là tập chứa các nút đã thăm
	openset = {};
	visited = [];
	trace = [-1]*(n+1);
	openset[start] = 0;
	trace[start] = -2;
	while openset:
		# lấy node có g(u) nhỏ nhất từ openset
		u = min(openset, key = openset.get);
		u_cost = openset[u];
		
		openset.pop(u);
		visited.append(u);

		if u == goal:
			return visited, GetPath(start, goal, trace);
		for v in range(n):
			if matrix[u][v] != 0:
				# nếu nút v đã thăm và g(v) mới lớn hơn g(v) cũ thì ta update
				v_cost = u_cost + matrix[u][v];
				if (v in visited) or (v in openset and v_cost > openset[v]):
					continue;
				
				# ngược lại, ta thêm nút v vào openset và lưu vết
				openset[v] = v_cost;
				trace[v] = u;
	return visited, -1;

def GBFS(matrix, start, goal, n, heuristic):
	trace = [-1]*(n+1);
	stack = [start];
	visited = [];
	trace[start] = -2;
	while stack :
		u = stack.pop();
		visited.append(u);
		if u == goal:
			return visited, GetPath(start, goal, trace);
		
		v_heuristic = [];	# danh sách chứa các nút v và heuristic tương ứng
		for v in range(n):
			if matrix[u][v] != 0 and trace[v] == -1:
				v_heuristic.append([heuristic[v], v]);
				trace[v] = u;

		#sắp xếp lại theo thứ tự giảm dần của heuristic để thêm vào stack
		v_heuristic.sort(reverse = True);
		for v in v_heuristic:
			if v[1] not in stack:
				stack.append(v[1]);
	return visited, -1;

def ASS(matrix, start, goal, n, heuristic):
	# mỗi phần tử của openset là một cặp { u, [f(u)] }
	# với f(u) là một cặp [ g(u) , h(u)]
	# g(u) là chi phí đường đi từ start tới u
	# h(u) là heuristic từ u tới goal
	
	openset = {};
	visited = [];
	trace  = [-1]*(n + 1);
	trace[start] = -2;
	openset[start] = [0 , heuristic[start]];
	while openset:
		# lấy node có f(u) = g(u) + h(u) nhỏ nhất từ openset
		# u = min(openset, key = openset.get) 
		u = min(openset.items(), key = lambda x: x[1][0] + x[1][1])[0];
		g_u = openset[u][0];
		h_u = openset[u][1];
		
		# xóa node đang xét khỏi openset, thêm nó vào tập các nút đã thăm
		openset.pop(u);
		visited.append(u);

		if u == goal:
			return visited, GetPath(start, goal, trace);
		
		for v in range(n):
			if matrix[u][v] != 0:
				# nếu nút đó đã thăm thì ta bỏ qua
				if v in visited :
					continue;

				# nếu nút v có trong openset và f(v) mới nhỏ hơn f(v) cũ, ta update f(v)
				# còn nếu nút v chưa có trong openset thì ta thêm vào
				g_v_new = g_u + matrix[u][v];
				if (v in openset and g_v_new < openset[v][0]) or (v not in openset):
					openset[v] = [g_v_new, heuristic[v]];
					trace[v] = u;
	return visited, -1;

def main():

	matrix, n, start, goal, heuristic = LoadData("input.txt");
	# PrintData(matrix,n,heuristic, start, goal);
	
	vis, pth = DFS(matrix, start, goal, n);
	WritePath("dfs.txt", vis, pth);

	vis, pth = BFS(matrix, start, goal, n);
	WritePath("bfs.txt", vis, pth);
	
	vis, pth = UCS(matrix, start, goal, n);
	WritePath("ucs.txt", vis, pth);

	vis, pth = GBFS(matrix, start, goal, n, heuristic);
	WritePath("gbfs.txt", vis, pth);

	vis, pth = ASS(matrix, start, goal, n, heuristic);
	WritePath("astar.txt", vis, pth);

if __name__ == '__main__':
	main()
	