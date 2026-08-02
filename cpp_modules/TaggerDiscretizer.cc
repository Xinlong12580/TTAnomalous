#include <cmath>
#include <algorithm>
#include <correction.h>
#include <ROOT/RVec.hxx>
using namespace ROOT::VecOps;


using ROOT::VecOps::RVec;
class TaggerDiscretizer{
public:
    std::vector<float> WPs;

    TaggerDiscretizer(std::string jetType,  std::string year, std::string taggerType = "UParTAK4_wp_values", std::vector<float> _WPs = {}){
        if (_WPs.size() > 0)
            WPs = _WPs;
        else
            if (jetType == "FatJet" || jetType == "AK8"){
                //WPs = {0, 0.9172, 0.9734, 0.9880, 1};
                //WPs = {0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.9172, 0.9734, 0.9880, 1};
                //WPs = {0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.975, 0.99, 1}; // TEMPERARY SOLUTION!
                WPs = {0, 0.95, 0.975, 0.99, 1}; // TEMPERARY SOLUTION!
            }
            else if (jetType == "Jet" || jetType == "AK4"){
               std::string f_name = "/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/BTV/"; 
                if (year == "2024_Summer24")
                    f_name = f_name + year + "/btagging_preliminary.json.gz"; // AD HOC SOLUTION!
                else
                    f_name = f_name + year + "/btagging.json.gz";
                std::unique_ptr<correction::CorrectionSet> _cset = correction::CorrectionSet::from_file(f_name.c_str());
                std::cout<<"Using File: " << f_name<<" with key: " <<taggerType<<std::endl;
                //correction::Correction::Ref         ref = _cset->at(taggerType.c_str());
                correction::Correction::Ref         ref = _cset->at(taggerType);
                WPs = {0.};
                std::vector<std::string> s_wps = {"L", "M", "T", "XT", "XXT"};
                    
                for (auto s_wp : s_wps){
                    std::map<std::string, correction::Variable::Type> map {{ "working_point" , s_wp.c_str()}};
                    std::vector<correction::Variable::Type> inputs;
                    for (const correction::Variable& input: ref->inputs()) {
                        std::cout<<input.name()<<std::endl;
                        inputs.push_back(map.at(input.name()));
                    }
                    float wp = ref->evaluate(inputs);
                    std::cout<<s_wp<<": "<<wp<<std::endl;
                    WPs.push_back(wp);
                }
                WPs.push_back(1.);
            } 
            else
                throw "Supported jetType: Jet, FatJet";
        std::cout<<"Using Working Points: ";
        for (auto wp : WPs)
                std::cout<<wp<<" ";
        std:;cout<<std::endl;
    }

    ~TaggerDiscretizer(){}

    int eval(float score){
        //cout<<"TH"<<score<<endl;
        int score_discrete = -1; 
        for (int i = 0; i < WPs.size() - 1; i ++)
            if (score >= WPs.at(i) && score < WPs.at(i+1)){
                score_discrete = i;
                break;
            }
        
        return score_discrete; 
    }

    RVec<int> eval(RVec<float> scores){
        RVec<int> scores_discrete = {};
        for (const float score : scores)
            scores_discrete.push_back(eval(score));
        return scores_discrete; 
    }

    float decapitate(float score){
        float WP_tightest = WPs.at(WPs.size() - 2);
        if(score < WP_tightest){
            return score;
        }
        else{
            return WP_tightest;
        }
    }
    RVec<float> decapitate(RVec<float> scores){
        RVec<float> scores_decapitated = {};
        for (const float score : scores)
            scores_decapitated.push_back(decapitate(score));
        return scores_decapitated; 
    }

};




/*
float discretizeTaggers(float score, std::string jetType, std::string year){
    std::vector<float> WPs;
    //particleNet Tagger
    if (jetType == "AK4"){
        if (year == "2022")
            WPs = {0, 0.047, 0.245, 0.6734, 0.7862, 0.961, 1};
        if (year == "2022EE")
            WPs = {0, 0.0499, 0.2605, 0.6915, 0.8033, 0.9664, 1};
        if (year == "2023")
            WPs = {0, 0.0358, 0.1917, 0.6172, 0.7515, 0.9659, 1};
        if (year == "2023BPix")
            WPs = {0, 0.0359, 0.1919, 0.6133, 0.7544, 0.9688, 1};
        if (year == "2024")//No WP, using 2023BPix for the moment
            WPs = {0, 0.0359, 0.1919, 0.6133, 0.7544, 0.9688, 1};
    }
    else if (jetType == "AK8"){
        WPs = {0, 0.9172, 0.9734, 0.9880, 1};
        //WPs = {0, 0.2, 0.4, 0.6, 0.8, 0.9172, 0.9734, 0.9880, 1};
    }
    float score_discrete = -1.; //Defined as float to avoid data type mismatch later
    for (int i = 0; i < WPs.size() - 1; i ++)
        if (score >= WPs.at(i) && score < WPs.at(i+1)){
            score_discrete = i;
            break;
        }
    return score_discrete; 
};
*/
