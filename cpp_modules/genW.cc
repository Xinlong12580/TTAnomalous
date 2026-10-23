// Requires CMSSW
// Following the example from JME found here:
// https://gitlab.cern.ch/cms-nanoAOD/jsonpog-integration/-/blob/master/examples/jercExample.C

#include <correction.h>
#include <ROOT/RVec.hxx>

using ROOT::VecOps::RVec;

//Lumi * Xsec to gen Weight
class genW {
    public:
        genW(){};
        ~genW(){};
        RVec<float> eval(float genWeight, float lumi, float Xsec, float sumW);
};


RVec<float> genW::eval(float genWeight, float lumi, float Xsec, float SumW) {
    RVec<float> out {1.0, 1.0, 1.0};

        for(int i = 0; i < 3; i++){
            out[i] = genWeight * lumi * Xsec / SumW;
        }

        return out;
};
