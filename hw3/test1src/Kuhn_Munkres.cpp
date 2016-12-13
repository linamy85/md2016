#include <algorithm>
using std::min;
using std::fill;
using std::max;

#define INF (1e9)

struct KM{
// Maximum Bipartite Weighted Matching (Perfect Match)
	static const int MXN = 5010;
	int n,match[MXN],vx[MXN],vy[MXN];
	double edge[MXN][MXN],lx[MXN],ly[MXN],slack[MXN];
	// ^^^^ long long
	void init(int _n){
		n = _n;
		for (int i=0; i<n; i++)
			for (int j=0; j<n; j++)
				edge[i][j] = 0;
	}
	void add_edge(int x, int y, double w){ // long long
		edge[x][y] = w;
	}
	bool DFS(int x){
		vx[x] = 1;
		for (int y=0; y<n; y++){
			if (vy[y]) continue;
			if (lx[x]+ly[y] > edge[x][y]){
				slack[y] = min(slack[y], lx[x]+ly[y]-edge[x][y]);
			} else {
				vy[y] = 1;
				if (match[y] == -1 || DFS(match[y])){
					match[y] = x;
					return true;
				}
			}
		}
		return false;
	}
	double solve(){
		fill(match,match+n,-1);
		fill(lx,lx+n,-INF);
		fill(ly,ly+n,0);
		for (int i=0; i<n; i++)
			for (int j=0; j<n; j++)
				lx[i] = max(lx[i], edge[i][j]);
		for (int i=0; i<n; i++){
			fill(slack,slack+n,INF);
			while (true){
				fill(vx,vx+n,0);
				fill(vy,vy+n,0);
				if ( DFS(i) ) break;
				double d = INF; // long long
				for (int j=0; j<n; j++)
					if (!vy[j]) d = min(d, slack[j]);
				for (int j=0; j<n; j++){
					if (vx[j]) lx[j] -= d;
					if (vy[j]) ly[j] += d;
					else slack[j] -= d;
				}
			}
		}
		double res=0;
		for (int i=0; i<n; i++)
			res += edge[match[i]][i];
		return res;
	}
};
