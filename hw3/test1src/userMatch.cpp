#include <iostream>
#include <fstream>
#include <stdio.h>
#include <vector>
#include <thread>


using namespace std;

#define N_USER (50000)
#define N_ITEM (5000)
#define N_THREAD (5)

double r1 [N_USER][N_ITEM];
int bestmatch[N_USER];


void threadFunc(vector<vector< pair<int, double> > > &r2,
                int start_idx, int end_idx);
  
void match(vector<vector< pair<int, double> > > &r2) {
  int start = 0;
  int gap = N_USER / N_THREAD;
  vector<thread> thrs;
  for (int i = 0; i < N_THREAD; ++i) {
    int end = start + gap;
    if (i == N_THREAD-1)  // In case of n_user % n_thread != 0
      end = N_USER;
    thrs.push_back(thread(threadFunc, ref(r2), start, end));
    start = end;
  }

  for (auto &th : thrs) {
    th.join();
  }
}

void threadFunc(vector<vector< pair<int, double> > > &r2,
                int start_idx, int end_idx) {
  for (int u2 = start_idx; u2 < end_idx; ++u2) {
    if ((u2 * 100) % N_USER == 0) 
      cout << u2 * 100 / N_USER << "%  ";
    int best = -1;
    int maxdot = -1;
    for (int u1 = 0; u1 < N_USER; ++u1) {
      double dot = 0.0;
      for (auto &p : r2[u2]) {
        dot += p.second * r1[u1][p.first];
      }
      if (dot > maxdot) {
        maxdot = dot;
        best = u1;
      }
    }
    bestmatch[u2] = best;
  }
}

int main(int argc, char * argv[]) {
  vector< vector< pair<int, double> > > r2(
      N_USER, vector< pair<int,double> >());

  ifstream tran_file(argv[1], ifstream::in);
  ifstream train_file(argv[2], ifstream::in);

  cout << "Start loading files in c++" << endl;
  double value;
  for (int user = 0; user < N_USER; ++user) {
    for (int item = 0; item < N_ITEM; ++item) {
      tran_file >> value;
      r1[user][item] = value;
    }
  }
  tran_file.close();

  int user, item;
  while (train_file >> user >> item >> value) {
    r2[user].push_back(make_pair(item, value));
  }
  train_file.close();

  cout << "Load file done" << endl;
  match(r2);
  cout << "Match done" << endl;

  ofstream dump_file(argv[3], ifstream::out);
  for (int user = 0; user < N_USER; ++user) {
    int match_u1 = bestmatch[user];
    for (auto p : r2[user]) {
      r1[match_u1][p.first] = p.second;
    }
    for (int item = 0; item < N_ITEM; ++item) {
      dump_file << r1[match_u1][item] << " ";
    }
    dump_file << endl;
  }
  
}
