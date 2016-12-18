#include <iostream>
//#include <fstream>
#include <vector>
#include <set>
#include <thread>
#include <chrono>
#include <ctime>
#include <cstdio>

#include <mutex>

#include <cassert>
#include <cmath>

//#include "Kuhn_Munkres.cpp"
#include "bipartite-mincost.cpp"

#define USER_N (50000)
#define ITEM_N (5000)
#define N_THREAD (20)
#define DIST (5)
#define INF (1e6)

using namespace std;

typedef vector<vector<double> > MATRIX;

mutex match_mutex;

//double source[ ITEM_N ][ USER_N ];
//double train[ ITEM_N ][ USER_N ];
MATRIX source (ITEM_N, vector<double>(USER_N, 0.0));
MATRIX train  (ITEM_N, vector<double>(USER_N, 0.0));

// Source -> Target.
vector<vector<int> > usermatch (USER_N, vector<int>());
vector<int> itemmatch;

// Loads matrix from file and combines with original values.
void LoadMatrix(MATRIX& matrix, char * mf_file, char * ori_file) {
  double value;
  int user = 0, item = 0;
  //ifstream fin(mf_file, ifstream::in);
  FILE * fin = fopen(mf_file, "r");

  while (fscanf(fin, "%lf", &value) == 1) {
    matrix[item][user] = value;
    ++item;
    if (item == 5000) {
      ++user;
      item = 0;
    }
  }
  assert(item == 0 && user == 50000);
  //fin.close();
  fclose(fin);

  //ifstream fori(ori_file, ifstream::in);
  FILE * fori = fopen(ori_file, "r");

  while (fscanf(fori, "%d%d%lf", &user, &item, &value) == 3) {
    assert( 0 <= user && user < USER_N );
    assert( 0 <= item && item < ITEM_N );
    matrix[item][user] = value;
  }
  //fori.close();
  fclose(fori);
}

// Item bipartite matching by Hungarian in O(n^3)
void FindItemMatching(vector<int> &Rmate) {
  cerr << "Going to transfer to item distribution." << endl;
  cerr << "Fuck you" << endl;
  MATRIX src_dist(ITEM_N, vector<double>(DIST+1, 0.0));
  MATRIX tar_dist(ITEM_N, vector<double>(DIST+1, 0.0));

  fflush(stdout);
  // Transfers to item distribution.
  for (int item = 0; item < ITEM_N; ++item) {
    int s = 0, t = 0, idx;
    for (int user = 0; user < USER_N; ++user) {
      if (source[item][user] > 1e-6) {
        idx = int(floor(source[item][user] * DIST));
        src_dist[item][ min(idx, DIST) ] += 1;
        ++ s;
      }
      if (train[item][user] > 1e-6) {
        idx = int(floor(train[item][user] * DIST));
        tar_dist[item][ min(idx, DIST) ] += 1;
        ++ t;
      }
    }
    for (int i = 0; i <= DIST; ++i) {
      src_dist[item][i] /= s;
      tar_dist[item][i] /= t;
    }
  }

  cerr << "Going to transfer to weight matrix." << endl;
  // Transfer to weight matrix.
  MATRIX weight(ITEM_N, vector<double>(ITEM_N, 0.0));
  double val;
  for (int src = 0; src < ITEM_N; ++src) {
    for (int tar = 0; tar < ITEM_N; ++tar) {
      for (int i = 0; i <= DIST; ++i) {
        // KL divergence.
        val = src_dist[src][i] * log(src_dist[src][i] / tar_dist[tar][i]);
        if (std::isnan(val))
          val = src_dist[src][i] * -INF;
        if (std::isinf(val))
          val = src_dist[src][i] * INF;
        else
          weight[src][tar] += val;
      }
      //weight[src][tar] = (-1) * sqrt(total / (DIST + 1));
      //weight[src][tar] = sqrt(total / (DIST + 1));
    }
  }
  
  cerr << "Going to use Kuhn Munkres to find best matching." << endl;
  
  cerr << "Min cost: " << MinCostMatching(weight, itemmatch, Rmate) << endl;

}

// Rearrange source by item order.
void PermutAndTranspost(vector<int> &TwoTo1) {
  MATRIX newmat(USER_N, vector<double>(ITEM_N, 0.0));
  MATRIX newtrain(USER_N, vector<double>(ITEM_N, 0.0));

  for (int user = 0; user < USER_N; ++user) {
    for (int item = 0; item < ITEM_N; ++item) {
      newmat[user][item] = source[ TwoTo1[item] ][user];
      newtrain[user][item] = train[item][user];
    }
  }
  source.swap( newmat );
  train.swap(newtrain);
}

// Thread function for finding user matching.
void threadFunc(int start_idx, int end_idx) {
  for (int u2 = start_idx; u2 < end_idx; ++u2) {
    int best = -1;
    double mindif = 1e9;
    double dif, totaldif;
    for (int u1 = 0; u1 < USER_N; ++u1) {
      totaldif = 0.0;
      for (int item = 0; item < ITEM_N; ++item) {
        dif = source[u1][item] - train[u2][item];
        totaldif += dif * dif;
      }
      if (totaldif < mindif) {
        mindif = totaldif;
        best = u1;
      }
    }
    {
      match_mutex.lock();
      usermatch[best].push_back(u2);
      match_mutex.unlock();
    }
    if ((u2 * 100) % USER_N == 0) 
      fprintf(stderr, "%d%% %d - %d (%lf)\n", (u2 * 100) / USER_N, best, u2, mindif);
  }
}
// Combine the most likely user in source with user vector in train.
void FindUserMatching() {
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

  // Shows the distribution for user matching.
  vector<int> count (USER_N);
  for (auto &v : usermatch) {
    ++ count[ v.size() ];
  }
  for (int i = 0; i < USER_N; i ++) {
    if (count[i] > 0)
      cerr << i << ":" << count[i] << " ";
  }
  cerr << endl;

}

void OutputLibfm(char * src_ori, char * tar_ori, char * output) {
  // Deal with source
  //ifstream srcfile(src_ori, ifstream::in);
  //ifstream tarfile(tar_ori, ifstream::in);
  //ofstream outfile(output, ofstream::out);
  FILE * srcfile = fopen(src_ori, "r");
  FILE * tarfile = fopen(tar_ori, "r");
  FILE * outfile = fopen(output, "w");

  vector< set<int> > used(USER_N, set<int>());

  int user, item;
  double value;
  // Target file 
  while (fscanf(tarfile, "%d%d%lf", &user, &item, &value) == 3) {
    //outfile << value << " " << user << ":1 " << item + 50000 << ":1" << endl;
    fprintf(outfile, "%lf %d:1 %d:1\n", value, user, item + USER_N);
    used[user].insert(item);
  }

  // Source file process after target to avoid duplicate.
  while (fscanf(srcfile, "%d%d%lf", &user, &item, &value) == 3) {
    for (auto u2 : usermatch[user]) {
      if (used[u2].count(itemmatch[item]) == 0) {
        //outfile << value << " " 
                //<< u2 << ":1 " << itemmatch[item] + 50000 << ":1" << endl;
        fprintf(outfile, "%lf %d:1 %d:1\n", value, u2, itemmatch[item] + USER_N);
      }
    }
  }

}

void PrintTime(const char *str) {
  std::chrono::time_point<std::chrono::system_clock> now = 
    std::chrono::system_clock::now();
  std::time_t end_time = std::chrono::system_clock::to_time_t(now);
  std::cerr << str << "at " << std::ctime(&end_time);
}

int main(int argc, char * argv[]) {
  cerr << "HAHAHA\n";
  if (argc != 6) {
    cerr << "Usage: " << argv[0] << " [source] [source original] "
      << "[train] [train original] [output]" << endl;
    exit(1);
  }

  cerr << "HAHAHA\n";
  PrintTime("Start ");
  // Loads source & train matrix.
  LoadMatrix(source, argv[1], argv[2]);
  PrintTime("Loads source matrix done ");
  LoadMatrix(train, argv[3], argv[4]);

  PrintTime("Loads train matrix done ");
  // Reduces to item distribution.
  // Finds minimum cost matching.
  vector<int> trainTOsource(ITEM_N, -1);
  cerr << trainTOsource.size() << endl;
  FindItemMatching(trainTOsource);

  PrintTime("Find best item matching done ");
  // Rearranges sequence of item vector for each user in source.
  PermutAndTranspost(trainTOsource);

  PrintTime("Rearrange item vectors done ");
  // Combine the most likely user in source with user vector in train.
  FindUserMatching();

  PrintTime("Find user matching done ");
  // Output matrix as in LibFM format.
  OutputLibfm(argv[2], argv[4], argv[5]);

  PrintTime("Output matrix done ");
  return 0;
}


