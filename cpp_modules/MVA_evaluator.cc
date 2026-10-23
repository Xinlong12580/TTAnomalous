#include <cstdlib>
#include <iostream>
#include <map>
#include <string>
 
#include "TChain.h"
#include "TFile.h"
#include "TTree.h"
#include "TString.h"
#include "TObjString.h"
#include "TSystem.h"
#include "TROOT.h"
 
#include "TMVA/Factory.h"
#include "TMVA/DataLoader.h"
#include "TMVA/Tools.h"
#include "TMVA/TMVAGui.h"


class MVA_evaluator{
public:
    float vals[100] = {0.0};
    float specs[100] = {0.0};
    int n_vals = 0;
    int n_specs = 0;
    std::string methodName;
    TMVA::Reader *reader = new TMVA::Reader( "!Color:!Silent" );
    MVA_evaluator(int _n_vals, std::vector<std::string> val_names, std::string xml_file, int _n_specs = 0, std::vector<std::string> spec_names = {}, std::string _methodName = "BDTG");
    ~MVA_evaluator(){};
    float eval(std::vector<float> inputs);
    

};

MVA_evaluator::MVA_evaluator(int _n_vals, std::vector<std::string> val_names, std::string xml_file, int _n_specs = 0, std::vector<std::string> spec_names = {}, std::string _methodName = "BDTG"){
    n_vals = _n_vals;
    n_specs = _n_specs;
    methodName = _methodName;
    for (int i = 0; i < n_vals; i ++) 
        reader->AddVariable( val_names.at(i), &vals[i] ); 
    for (int i = 0; i < n_specs; i ++) 
        reader->AddSpectator( spec_names.at(i), &specs[i] ); 
    reader->BookMVA( methodName, xml_file );
}

float MVA_evaluator::eval(std::vector<float> inputs){
    for(int i = 0; i < n_vals; i ++){
        vals[i] = inputs.at(i);
    
    }
    //std::cout<<"test"<<std::endl;
    //float MVA_score = reader->EvaluateMVA(methodName + " method");
    float MVA_score = reader->EvaluateMVA(methodName);
    return MVA_score;
}

float mass_shift(float mass, float input_down, float input_up, float target_down, float target_up){
    return (target_up - target_down)/(input_up - input_down) * (mass - input_down) + target_down;
}
