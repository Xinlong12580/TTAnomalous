
using namespace ROOT::VecOps;

class TopPt_reweighting {

    public:
    RVec<float> eval( int nGenPart, RVec<int> GenPart_pdgId, RVec<float> GenPart_pt, float scale = 2.);
};

TopPt_weight::TopPt_weight(){};


RVec<float> TopPt_reweighting::eval( int nGenPart, RVec<int> GenPart_pdgId, RVec<float> GenPart_pt, float scale = 2.){

    float genTPt = -1.;
    float genTbarPt = -1.;
    for (int i = 0; i < nGenPart; i ++)
        if (GenPart_pdgId.at(i) == 6)
            genTPt = GenPart_pt.at(i);
        else if (GenPart_pdgId.at(i) == -6)
            genTbarPt = GenPart_pt.at(i);
    


    float wTPt = 1.0;
    float wTPt_up = 1.0;
    float wTPt_down = 1.0;
    if (genTPt > 0){ 
        wTPt = exp(0.0615 - 0.0005*genTPt);
        wTPt_up = exp(0.0615 - (1*scale)*0.0005*genTPt);
        wTPt_down = exp(0.0615 - (1/scale)*0.0005*genTPt);
    }

    float wTbarPt = 1.0;
    float wTbarPt_up = 1.0;
    float wTbarPt_down = 1.0;
    if (genTbarPt > 0){
        wTbarPt = exp(0.0615 - 0.0005*genTbarPt);
        wTbarPt_up = exp(0.0615 - (1*scale)*0.0005*genTbarPt);
        wTbarPt_down = exp(0.0615 - (1/scale)*0.0005*genTbarPt);
    }

    return {sqrt(wTPt*wTbarPt),sqrt(wTPt_up*wTbarPt_up),sqrt(wTPt_down*wTbarPt_down)};
}
