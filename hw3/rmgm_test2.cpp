#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cassert>
#include <vector>
#include <algorithm>
#include <time.h>

#define ZERO_PROB 1e-100

using namespace std;

int userclusterN, itemclusterN;
int ratingN;

class Rating
{
public:
	Rating(){
		p = new double* [userclusterN];
		for(int i=0; i<userclusterN; i++)
			p[i] = new double [itemclusterN];
	}
	~Rating(){
		for(int i=0; i<userclusterN; i++)
			delete [] p[i];
		delete [] p;
	}
	int u, v;
	double r;
	//p[userclusterN][itemclusterN] 
	double** p;
};

bool compare_u(Rating* x, Rating* y)
{
	return (x->u < y->u);
}

bool compare_v(Rating* x, Rating* y)
{
	return (x->v < y->v);
}

bool compare_r(Rating* x, Rating* y)
{
	return (x->r < y->r);
}

inline int rating2index(double r)
{
	return int(r * ratingN - 1);
}

inline double index2rating(int i)
{
	return (double(i + 1)) / ratingN;
}

FILE* myopen(char* dir_path, char* filename, char* op)
{
	char path[128];
	strcpy(path, dir_path);
	strcat(path, filename);
	FILE* fp = fopen(path, op);
	assert(fp != NULL);
	return fp;
}

// ./rmgm ${dir} ${userclusterN} ${itemclusterN} $(iteration)
int main(int argc, char const *argv[])
{
	if(argc != 5){
		fprintf(stderr, "usage: ./rmgm ${dir} ${userclusterN} ${itemclusterN} $(iteration)\n");
		exit(1);
	}
	int s_userN = 30000, s_itemN = 3000, t_userN = 20000, t_itemN = 2000;
	int s_ratingN = 0, t_ratingN = 0;
	ratingN = 10;
	userclusterN = atoi(argv[2]); itemclusterN = atoi(argv[3]);

	vector<Rating*> source, train;
	FILE* fp;
	Rating* temp_rating;
	
	char dir_path[128];
	strcpy(dir_path, argv[1]);
	if(dir_path[strlen(dir_path)-1] != '/')
		strcat(dir_path, "/");

	srand(time(NULL));
	double CU[userclusterN], CV[itemclusterN];
	double R_CUCV[userclusterN][itemclusterN][ratingN];

	for(int i=0; i<userclusterN; i++)
		CU[i] = 0;
	for(int i=0; i<itemclusterN; i++)
		CV[i] = 0;
	for(int i=0; i<userclusterN; i++)
		for(int j=0; j<itemclusterN; j++)
			for(int k=0; k<ratingN; k++)
				R_CUCV[i][j][k] = 0;

	//read from source.txt
	fp = myopen(dir_path, "source.txt", "r");
	temp_rating = new Rating;
	while(fscanf(fp, "%d", &(temp_rating->u)) != EOF){
		fscanf(fp, "%d%lf", &(temp_rating->v), &(temp_rating->r));
		source.push_back(temp_rating);
		s_ratingN++;
		int usercluster = rand() % userclusterN;
		int itemcluster = rand() % itemclusterN;
		CU[usercluster]++; CV[itemcluster]++;
		R_CUCV[usercluster][itemcluster][rating2index(temp_rating->r)]++;
		temp_rating = new Rating;
	}
	//printf("%d %d %lf\n", source[0]->u, source[0]->v, source[0]->r);
	fclose(fp);

	//read from train.txt
	fp = myopen(dir_path, "train.txt", "r");
	temp_rating = new Rating;
	while(fscanf(fp, "%d", &(temp_rating->u)) != EOF){
		fscanf(fp, "%d%lf", &(temp_rating->v), &(temp_rating->r));
		train.push_back(temp_rating);
		t_ratingN++;
		int usercluster = rand() % userclusterN;
		int itemcluster = rand() % itemclusterN;
		CU[usercluster]++; CV[itemcluster]++;
		R_CUCV[usercluster][itemcluster][rating2index(temp_rating->r)]++;
		temp_rating = new Rating;
	}
	//printf("%d %d %lf\n", train[0]->u, train[0]->v, train[0]->r);
	fclose(fp);

	printf("Reading done.\n");

	//initialization
	//co-cluster source matrix (for instance, using orthogonal nonnegative matrix tri-factorization)
	//initialize CU, CV, R_CUCV from co-clustering results
	
	double normalization = 0;
	for(int i=0; i<userclusterN; i++)
		normalization += CU[i];
	for(int i=0; i<userclusterN; i++)
		CU[i] /= normalization;

	normalization = 0;
	for(int i=0; i<itemclusterN; i++)
		normalization += CV[i];
	for(int i=0; i<itemclusterN; i++)
		CV[i] /= normalization;

	for(int i=0; i<userclusterN; i++)
		for(int j=0; j<itemclusterN; j++){
			normalization = 0;
			for(int k=0; k<ratingN; k++)
				normalization += R_CUCV[i][j][k];
			for(int k=0; k<ratingN; k++)
				R_CUCV[i][j][k] /= normalization;
		}

	//initialize uniformly
	//double US_CU[userclusterN][s_userN];
	//double UT_CU[userclusterN][t_userN];
	//double VS_CV[itemclusterN][s_itemN];
	//double VT_CV[itemclusterN][t_itemN];
	double** US_CU = new double* [userclusterN];
	for(int i=0; i<userclusterN; i++)
		US_CU[i] = new double [s_userN];

	double** UT_CU = new double* [userclusterN];
	for(int i=0; i<userclusterN; i++)
		UT_CU[i] = new double [t_userN];

	double** VS_CV = new double* [itemclusterN];
	for(int i=0; i<itemclusterN; i++)
		VS_CV[i] = new double [s_userN];

	double** VT_CV = new double* [itemclusterN];
	for(int i=0; i<itemclusterN; i++)
		VT_CV[i] = new double [t_userN];

	double init_value_u = 1.0 / (s_userN + t_userN);
	for(int i=0; i<userclusterN; i++){
		for(int j=0; j<s_userN; j++)
			US_CU[i][j] = init_value_u;
		for(int j=0; j<t_userN; j++)
			UT_CU[i][j] = init_value_u;
	}

	double init_value_v = 1.0 / (s_itemN + t_itemN);
	for(int i=0; i<itemclusterN; i++){
		for(int j=0; j<s_itemN; j++)
			VS_CV[i][j] = init_value_v;
		for(int j=0; j<t_itemN; j++)
			VT_CV[i][j] = init_value_v;
	}

	printf("Initialization done\n");

	int iteration = atoi(argv[4]);
	for(int it=0; it<iteration; it++){
		//printf("Iteration %d : \n", it);
		fprintf(stderr, "Iteration %d : \n", it);
		printf("\tE step\n");
		//E step : compute P(k,l | j^(z))
		//source
		for(int i=0; i<s_ratingN; i++){
			double denominator = 0;
			for(int j=0; j<userclusterN; j++)
				for(int k=0; k<itemclusterN; k++)
					denominator += (
						CU[j] * US_CU[j][source[i]->u] *
						CV[k] * VS_CV[k][source[i]->v] *
						R_CUCV[j][k][rating2index(source[i]->r)]);
			for(int j=0; j<userclusterN; j++)
				for(int k=0; k<itemclusterN; k++){
					if(denominator == 0)
						source[i]->p[j][k] = ZERO_PROB;
					else
						source[i]->p[j][k] = (
							CU[j] * US_CU[j][source[i]->u] *
							CV[k] * VS_CV[k][source[i]->v] *
							R_CUCV[j][k][rating2index(source[i]->r)] /
							denominator);
				}
		}
		//train
		for(int i=0; i<t_ratingN; i++){
			double denominator = 0;
			for(int j=0; j<userclusterN; j++)
				for(int k=0; k<itemclusterN; k++){
					denominator += (
						CU[j] * UT_CU[j][train[i]->u] *
						CV[k] * VT_CV[k][train[i]->v] *
						R_CUCV[j][k][rating2index(train[i]->r)]);
				}
			for(int j=0; j<userclusterN; j++)
				for(int k=0; k<itemclusterN; k++){
					if(denominator == 0)
						train[i]->p[j][k] = ZERO_PROB;
					else
						train[i]->p[j][k] = (
							CU[j] * UT_CU[j][train[i]->u] *
							CV[k] * VT_CV[k][train[i]->v] *
							R_CUCV[j][k][rating2index(train[i]->r)] /
							denominator);
				}
		}
		/*printf("\tsource:\n");
		for(int i=0; i<10; i++)
			for(int j=0; j<userclusterN; j++)
				for(int k=0; k<itemclusterN; k++)
					printf("source[%d]->p[%d][%d] = %lf\n", i, j, k, source[i]->p[j][k]);
		printf("\ttrain:\n");
		for(int i=0; i<10; i++)
			for(int j=0; j<userclusterN; j++)
				for(int k=0; k<itemclusterN; k++)
					printf("train[%d]->p[%d][%d] = %lf\n", i, j, k, train[i]->p[j][k]);*/
		//M step : update model parameters
		printf("\tM step\n");
		//CU
		for(int k=0; k<userclusterN; k++){
			double nominator = 0;
			for(int j=0; j<s_ratingN; j++)
				for(int l=0; l<itemclusterN; l++)
					nominator += source[j]->p[k][l];
			for(int j=0; j<t_ratingN; j++)
				for(int l=0; l<itemclusterN; l++)
					nominator += train[j]->p[k][l];
			CU[k] = nominator / (s_ratingN + t_ratingN);
		}
		/*for(int k=0; k<userclusterN; k++)
			printf("CU[%d] = %lf\n", k, CU[k]);*/
		//CV
		for(int l=0; l<itemclusterN; l++){
			double nominator = 0;
			for(int j=0; j<s_ratingN; j++)
				for(int k=0; k<itemclusterN; k++)
					nominator += source[j]->p[k][l];
			for(int j=0; j<t_ratingN; j++)
				for(int k=0; k<itemclusterN; k++)
					nominator += train[j]->p[k][l];
			CV[l] = nominator / (s_ratingN + t_ratingN);
		}
		/*for(int l=0; l<itemclusterN; l++)
			printf("CV[%d] = %lf\n", l, CV[l]);*/
		//US_CU
		sort(source.begin(), source.end(), compare_u);
		/*printf("\tsource sorted by u\n");
		for(int i=0; i<10; i++)
			printf("i = %d : u = %d, v = %d, r = %lf\n", i, source[i]->u, source[i]->v, source[i]->r);*/
		for(int k=0; k<userclusterN; k++){
			int j = 0;
			for(int i=0; i<s_userN; i++){
				double nominator = ZERO_PROB;
				while(j<s_ratingN && source[j]->u < i)
					j++;
				for(; j<s_ratingN && source[j]->u == i; j++)
					for(int l=0; l<itemclusterN; l++)
						nominator += source[j]->p[k][l];
				if(CU[k] == 0)
					US_CU[k][i] = ZERO_PROB;
				else
					US_CU[k][i] = nominator / CU[k] / (s_ratingN + t_ratingN);
			}
		}
		/*printf("\tUS_CU\n");
		for(int k=0; k<userclusterN; k++)
			for(int i=0; i<5; i++)
				printf("US_CU[%d][%d] = %lf\n", k, i, US_CU[k][i]);*/
		//UT_CU
		sort(train.begin(), train.end(), compare_u);
		for(int k=0; k<userclusterN; k++){
			int j = 0;
			for(int i=0; i<t_userN; i++){
				double nominator = ZERO_PROB;
				while(j<t_ratingN && train[j]->u < i)
					j++;
				for(; j<t_ratingN && train[j]->u == i; j++)
					for(int l=0; l<itemclusterN; l++)
						nominator += train[j]->p[k][l];
				if(CU[k] == 0)
					UT_CU[k][i] = ZERO_PROB;
				else
					UT_CU[k][i] = nominator / CU[k] / (s_ratingN + t_ratingN);
			}
		}
		/*printf("\tUT_CU\n");
		for(int k=0; k<userclusterN; k++)
			for(int i=0; i<5; i++)
				printf("UT_CU[%d][%d] = %lf\n", k, i, UT_CU[k][i]);*/
		//VS_CV
		sort(source.begin(), source.end(), compare_v);
		for(int l=0; l<itemclusterN; l++){
			int j = 0;
			for(int i=0; i<s_itemN; i++){
				double nominator = ZERO_PROB;
				while(j<s_ratingN && source[j]->v < i)
					j++;
				for(; j<s_ratingN && source[j]->v == i; j++)
					for(int k=0; k<userclusterN; k++)
						nominator += source[j]->p[k][l];
				if(CV[l] == 0)
					VS_CV[l][i] = ZERO_PROB;
				else
					VS_CV[l][i] = nominator / CV[l] / (s_ratingN + t_ratingN);
			}
		}
		/*printf("\tVS_CV\n");
		for(int k=0; k<itemclusterN; k++)
			for(int i=0; i<5; i++)
				printf("VS_CV[%d][%d] = %lf\n", k, i, VS_CV[k][i]);*/
		//VT_CV
		sort(train.begin(), train.end(), compare_v);
		for(int l=0; l<itemclusterN; l++){
			int j = 0;
			for(int i=0; i<t_itemN; i++){
				double nominator = ZERO_PROB;
				while(j<t_ratingN && train[j]->v < i)
					j++;
				for(; j<t_ratingN && train[j]->v == i; j++)
					for(int k=0; k<userclusterN; k++)
						nominator += train[j]->p[k][l];
				if(CV[l] == 0)
					VS_CV[l][i] = ZERO_PROB;
				else
					VT_CV[l][i] = nominator / CV[l] / (s_ratingN + t_ratingN);
			}
		}
		/*printf("\tVT_CV\n");
		for(int k=0; k<itemclusterN; k++)
			for(int i=0; i<5; i++)
				printf("VT_CV[%d][%d] = %lf\n", k, i, VT_CV[k][i]);*/
		//R_CUCV
		sort(source.begin(), source.end(), compare_r);
		sort(train.begin(), train.end(), compare_r);
		for(int k=0; k<userclusterN; k++)
			for(int l=0; l<itemclusterN; l++){
				double denominator = 0;
				for(int j=0; j<s_ratingN; j++)
					denominator += source[j]->p[k][l];
				for(int j=0; j<t_ratingN; j++)
					denominator += train[j]->p[k][l];
				if(denominator == 0){
					for(int r=0; r<ratingN; r++)
						R_CUCV[k][l][r] = ZERO_PROB;
				}
				else{
					int js = 0, jt = 0;
					for(int r=0; r<ratingN; r++){
						double nominator = ZERO_PROB;
						while(js<s_ratingN && rating2index(source[js]->r) < r)
							js++;
						for(; js<s_ratingN && rating2index(source[js]->r) == r; js++)
							nominator += source[js]->p[k][l];
						while(jt<t_ratingN && rating2index(train[jt]->r) < r)
							jt++;
						for(; jt<t_ratingN && rating2index(train[jt]->r) == r; jt++)
							nominator += train[jt]->p[k][l];
						R_CUCV[k][l][r] = nominator / denominator;
					}
				}
			}
		/*printf("\tR_CUCV\n");
		for(int k=0; k<userclusterN; k++)
			for(int l=0; l<itemclusterN; l++)
				for(int r=0; r<ratingN; r++)
					printf("R_CUCV[%d][%d][%d] = %lf\n", k, l, r, R_CUCV[k][l][r]);*/	
	}
	printf("\nTraining done\n");

	/*printf("\tUT_CU\n");
	for(int k=0; k<userclusterN; k++)
		for(int i=0; i<t_userN; i++)
			printf("UT_CU[%d][%d] = %g\n", k, i, UT_CU[k][i]);
	printf("\tVT_CV\n");
	for(int k=0; k<itemclusterN; k++)
		for(int i=0; i<t_itemN; i++)
			printf("VT_CV[%d][%d] = %g\n", k, i, VT_CV[k][i]);*/



	//predict
	fp = myopen(dir_path, "test.txt", "r");
	FILE* fp2 = myopen(dir_path, "pred.txt", "w");
	int lines = 0, count = 0;
	char line[128];
	while(fgets(line, 128, fp) != NULL)
		lines++;
	printf("number of lines = %d\nStart prediction\n", lines);
	rewind(fp);	
	while(fgets(line, 128, fp) != NULL){
		count++;
		int u, v;
		sscanf(line, "%d%d", &u, &v);
		double ans = 0;

		double u_denominator = 0, v_denominator = 0;
		for(int k=0; k<userclusterN; k++)
			u_denominator += UT_CU[k][u] * CU[k];
		for(int l=0; l<itemclusterN; l++)
			v_denominator += VT_CV[l][v] * CV[l];
		//printf("u = %d, v = %d\n", u, v);
		//printf("\nu_denominator = %g, v_denominator = %g\n", u_denominator, v_denominator);
		for(int r=0; r<ratingN; r++){
			//printf("r = %d\n", r);
			double prob = ZERO_PROB;
			if(u_denominator < 1e-50 || v_denominator < 1e-50){
				for(int k=0; k<userclusterN; k++)
					for(int l=0; l<itemclusterN; l++)
						prob += R_CUCV[k][l][r] * CU[k] * CV[l];
				//printf("r = %d, prob = %g\n\n", r, prob);
				ans += index2rating(r) * prob;
			}
			else{
				for(int k=0; k<userclusterN; k++)
					for(int l=0; l<itemclusterN; l++){
						/*printf("R_CUCV[%d][%d][%d] = %g\n", k, l, r, R_CUCV[k][l][r]);
						printf("UT_CU[%d][%d] = %g, CU[%d] = %g\n", k, u, UT_CU[k][u], k, CU[k]);
						printf("VT_CV[%d][%d] = %g, CV[%d] = %g\n", l, v, VT_CV[l][v], l, CV[l]);*/
						prob += (
							R_CUCV[k][l][r] *
							(UT_CU[k][u] * CU[k] / u_denominator) *
							(VT_CV[l][v] * CV[l] / v_denominator));
					}
				
				//printf("prob = %g\n", prob);
				ans += index2rating(r) * prob;
			}
		}
		fprintf(fp2, "%d %d %lf\n", u, v, ans);
		if(count % 10000 == 0){
			fprintf(stderr, "%lf%% done.\n", double(count) / lines * 100);
		}	
	}

	return 0;
}