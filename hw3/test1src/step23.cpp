#include <iostream>
#include <fstream>
#include <vector>
#include <set>
#include <thread>
#include <chrono>
#include <ctime>

#include <cassert>
#include <cmath>

#include "Kuhn_Munkres.cpp"

#define USER_N (50000)
#define ITEM_N (5000)
#define N_THREAD (5)
#define DIST (10)

using namespace std;

typedef vector<vector<double> > MATRIX;


MATRIX source (ITEM_N, vector<double>(USER_N, 0.0));
MATRIX train  (ITEM_N, vector<double>(USER_N, 0.0));

// Source -> Target.
vector<vector<int> > usermatch (USER_N, vector<int>());
vector<int> itemmatch;

// Loads matrix from file and combines with original values.
void LoadMatrix(MATRIX &matrix, char * mf_file, char * ori_file) {
  double value;
  int user = 0, item = 0;
  ifstream fin(mf_file, ifstream::in);
  while (fin >> value) {
    matrix[item][user] = value;
    ++item;
    if (item == 5000) {
      ++user;
      item = 0;
    }
  }
  assert(item == 5000 && user == 50000);
  fin.close();

  ifstream fori(ori_file, ifstream::in);
  while (fori >> user >> item >> value) {
    matrix[item][user] = value;
  }
  fori.close();
}

// Item bipartite matching by Hungarian in O(n^3)
void FindItemMatching(MATRIX &source, MATRIX &train, vector<int> &match) {
  MATRIX src_dist(ITEM_N, vector<double>(DIST+1, 0)),
         tar_dist(ITEM_N, vector<double>(DIST+1, 0));
  match.resize(ITEM_N, -1);

  cout << "Going to transfer to item distribution." << endl;
  // Transfers to item distribution.
  for (int item = 0; item < ITEM_N; ++item) {
    int s = 0, t = 0, idx;
    for (int user = 0; user < USER_N; ++user) {
      if (source[item][user] > 1e-6) {
        idx = int(floor(source[item][user] / (1.0 / DIST)));
        ++ src_dist[item][ std::min(idx, DIST) ];
        ++ s;
      }
      if (train[item][user] > 1e-6) {
        idx = int(floor(train[item][user] / (1.0 / DIST)));
        ++ tar_dist[item][ std::min(idx, DIST) ];
        ++ t;
      }
    }
    for (int i = 0; i <= DIST; ++i) {
      src_dist[item][i] /= s;
      tar_dist[item][i] /= t;
    }
  }

  cout << "Going to transfer to weight matrix." << endl;
  // Transfer to weight matrix.
  MATRIX weight(ITEM_N, vector<double>(ITEM_N, 0.0));
  double total, dif;
  for (int src = 0; src < ITEM_N; ++src) {
    for (int tar = 0; tar < ITEM_N; ++tar) {
      total = 0.0;
      for (int i = 0; i <= DIST; ++i) {
        dif = src_dist[src][i] - tar_dist[tar][i];
        total += dif * dif;
      }
      weight[src][tar] = (-1) * sqrt(total / (DIST + 1));
    }
  }
  
  cout << "Going to use Kuhn Munkres to find best matching." << endl;
  // Kuhn Munkres finds best matching. 
  struct KM graph;
  graph.init(ITEM_N);
  for (int i = 0; i < ITEM_N; i++) {
    for (int j = 0; j < ITEM_N; j++) {
      graph.add_edge(i, j, weight[i][j]);
    }
  }
  cout << "Maximum weight: " << graph.solve() << endl;
  for (int i1 = 0; i1 < ITEM_N; i1++) {
    match[graph.match[i1]] = i1;
  }
  itemmatch = vector<int>(graph.match, graph.match + ITEM_N);
}

// Rearrange source by item order.
void PermutAndTranspost(MATRIX &source, vector<int> &TwoTo1) {
  MATRIX newmat(USER_N, vector<double>(ITEM_N, 0.0));
  for (int user = 0; user < USER_N; ++user) {
    for (int item = 0; item < ITEM_N; ++item) {
      newmat[user][item] = source[ TwoTo1[item] ][user];
    }
  }
}

// Thread function for finding user matching.
void threadFunc(int start_idx, int end_idx) {
  for (int u2 = start_idx; u2 < end_idx; ++u2) {
    if ((u2 * 100) % USER_N == 0) 
      cout << u2 * 100 / USER_N << "%  ";
    int best = -1;
    int mindif = 1e9;
    double dif;
    for (int u1 = 0; u1 < USER_N; ++u1) {
      dif = 0.0;
      for (int item = 0; item < ITEM_N; ++item) {
        dif = source[u1][item] - train[u2][item];
        dif += dif * dif;
      }
      if (dif < mindif) {
        mindif = dif;
        best = u1;
      }
    }
    usermatch[best].push_back(u2);

  }
}
// Combine the most likely user in source with user vector in train.
void FindUserMatching(MATRIX &source, MATRIX &train) {
  int start = 0;
  int gap = USER_N / N_THREAD;
  vector<thread> thrs;
  for (int i = 0; i < N_THREAD; ++i) {
    int end = start + gap;
    if (i == N_THREAD-1)  // In case of n_user % n_thread != 0
      end = USER_N;
    thrs.push_back(thread(threadFunc, start, end));
    start = end;
  }

  for (auto &th : thrs) {
    th.join();
  }
}

void OutputLibfm(char * src_ori, char * tar_ori, char * output) {
  // Deal with source
  ifstream srcfile(src_ori, ifstream::in);
  ifstream tarfile(tar_ori, ifstream::in);
  ofstream outfile(output, ofstream::out);

  vector< set<int> > used(USER_N, set<int>());

  int user, item;
  double value;
  // Target file 
  while (tarfile >> user >> item >> value) {
    outfile << value << " " << user << ":1 " << item + 50000 << ":1" << endl;
    used[user].insert(item);
  }

  // Source file process after target to avoid duplicate.
  while (srcfile >> user >> item >> value) {
    for (auto u2 : usermatch[user]) {
      if (used[u2].count(itemmatch[item]) > 1) {
        outfile << value << " " 
                << u2 << ":1 " << itemmatch[item] + 50000 << ":1" << endl;
      }
    }
  }

}

void PrintTime() {
  std::chrono::time_point<std::chrono::system_clock> now = 
    std::chrono::system_clock::now();
  std::time_t end_time = std::chrono::system_clock::to_time_t(now);
  std::cout << "finished computation at " << std::ctime(&end_time);
}

int main(int argc, char * argv[]) {
  if (argc != 6) {
    cerr << "Usage: " << argv[0] << " [source] [source original] "
      << "[train] [train original] [output]" << endl;
    exit(1);
  }

  PrintTime();
  // Loads source & train matrix.
  LoadMatrix(source, argv[1], argv[2]);
  LoadMatrix(train, argv[3], argv[4]);

  PrintTime();
  // Reduces to item distribution.
  vector<int> trainTOsource(ITEM_N, -1);

  PrintTime();
  // Finds minimum cost matching.
  FindItemMatching(source, train, trainTOsource);

  PrintTime();
  // Rearranges sequence of item vector for each user in source.
  PermutAndTranspost(source, trainTOsource);

  PrintTime();
  // Combine the most likely user in source with user vector in train.
  FindUserMatching(source, train);

  PrintTime();
  // Output matrix as in LibFM format.
  OutputLibfm(argv[2], argv[4], argv[5]);

  PrintTime();
  return 0;
}


