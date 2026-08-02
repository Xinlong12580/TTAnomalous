#include<cmath>
class DDT_map{
public:
    std::string method;
    TF2 f;
    int nMass;
    std::vector<int> MXs;
    std::vector<int> MYs;
    std::vector<float> scores;
    DDT_map();
    void set_parametric(std::string para_file, std::string func);
    void set_KNN(std::vector<int> _MXs, std::vector<int> _MYs, std::vector<float> _scores){MXs = _MXs; MYs = _MYs; scores = _scores;}
    void set_KNN(std::string fname);
    ~DDT_map(){};
    bool eval_parametric(float MVA, float MX, float MY);
    float eval_parametric(float MX, float MY);
    bool eval_KNN(float MVA, float MX, float MY, int k, bool do_distance);
    float eval_KNN(float MX, float MY, int k, bool do_distance );
    
};
void DDT_map::set_parametric(std::string para_file, std::string func = "1.99/(1+exp(- [5] /x * ( [0] + [1]*x+[2]*y + [3]*x*x + [4]*y*y ))) - 1"){
    f = TF2("DDT_f", func.c_str(), 0, 4000, 0, 3500);
    std::ifstream infile(para_file);
    std::string line;
    std::vector<float> paras = {};
    while (std::getline(infile, line)) {
        float value = std::stof(line);
        paras.push_back(value);
    }
    std::cout<<"DDT map funcion: "<<func<<std::endl;
    std::cout<<"DDT map parameters: "<<std::endl;
    for(int i = 0; i < paras.size(); i++){
        std::cout<<i<<" "<<paras.at(i)<<std::endl;
        f.SetParameter(i, paras.at(i));
    }
     
};

void DDT_map::set_KNN(std::string fname)
{
    ifstream file(fname);

    if (!file) {
        cerr << "Error opening file " << fname <<std::endl;
    }

    int MX, MY;
    float score;

    while (file >> MX >> MY >> score) {
        MXs.push_back(MX);
        MYs.push_back(MY);
        scores.push_back(score);
    }
    file.close();
}

bool DDT_map::eval_parametric(float MVA, float MX, float MY){
    float threshold = f.Eval(MX, MY);
    //std::cout<<MVA<<" "<<wp<<" "<<MX<<" "<<MY<<std::endl;
    return (MVA > threshold);
}

float DDT_map::eval_parametric(float MX, float MY){
    float threshold = f.Eval(MX, MY);
    //std::cout<<MVA<<" "<<wp<<" "<<MX<<" "<<MY<<std::endl;
    return threshold;
}

bool DDT_map::eval_KNN(float MVA, float MX, float MY, int k, bool do_distance){
    float threshold = eval_KNN(MX,  MY, k, do_distance);
    return (MVA > threshold);
}

float DDT_map::eval_KNN(float MX, float MY, int k, bool do_distance){
    std::vector<float> distances = {};
    for (int i = 0 ; i < MXs.size(); i ++){
        distances.push_back(std::max(float(1e-6) , float(std::sqrt((MX - MXs.at(i) ) * (MX - MXs.at(i) ) + (MY - MYs.at(i) ) * (MY - MYs.at(i) ) ) ) ) ) ;
    }
    std::vector<int> minIndices(distances.size());
    std::iota(minIndices.begin(), minIndices.end(), 0);

    std::partial_sort(minIndices.begin(), minIndices.begin() + std::min(k, (int)minIndices.size()), minIndices.end(), [&distances](int a, int b) { return distances[a] < distances[b]; });

    minIndices.resize(std::min(k, (int)minIndices.size()));
    if (MY > 3500 || MX > 4000)
        return scores.at(minIndices.at(0));
    else{
        float sumW = 0;
        float threshold = 0;
        for (int i = 0; i <  minIndices.size() ; i++){
            if (do_distance){
                sumW += (1 / distances.at(minIndices.at(i)));
                threshold += (scores.at(minIndices.at(i)) / distances.at(minIndices.at(i)));
            }
            else{
                sumW += 1;
                threshold += scores.at(minIndices.at(i)) ;
            }
        }
        threshold = threshold / sumW;
        return threshold;
    }
}

