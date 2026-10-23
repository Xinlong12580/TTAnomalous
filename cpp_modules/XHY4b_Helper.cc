#include "TIMBER/Framework/include/common.h"
float deltaR(float eta0, float phi0, float eta1, float phi1)
{
    float deltaPhi = std::abs(phi0-phi1) < M_PI ? std::abs(phi0 - phi1) : 2*M_PI - std::abs(phi0 - phi1);
    return sqrt((eta0 - eta1) * (eta0 - eta1) + deltaPhi * deltaPhi);

}      

ROOT::VecOps::RVec<bool> deltaRMtching(float eta, float phi, ROOT::VecOps::RVec<float> Etas, ROOT::VecOps::RVec<float> Phis, float threshold)
{
    ROOT::VecOps::RVec<bool> Matched = {};
    for (int i = 0; i < Etas.size(); i++)
        Matched.push_back((deltaR(eta, phi, Etas.at(i), Phis.at(i)) < threshold)); 
    return Matched;
    
}

int genBMatching(ROOT::VecOps::RVec<bool> deltaRMatched)
{
    for( int i = 0; i < deltaRMatched.size(); i++ )
        if(deltaRMatched.at(i) == 1)
            return i;
    return -1;

}
int genBMatching(float eta, float phi, ROOT::VecOps::RVec<float> Etas, ROOT::VecOps::RVec<float> Phis, float threshold)
{
    ROOT::VecOps::RVec<bool> deltaRMatched = deltaRMtching(eta, phi, Etas, Phis, threshold);
    int idx = genBMatching(deltaRMatched);
    return idx;
}


int genBMatching_withPNet(ROOT::VecOps::RVec<bool> deltaRMatched, ROOT::VecOps::RVec<float> BScores, float minBScore, float maxBScore)
{
    for( int i = 0; i < deltaRMatched.size(); i++ )
        if(deltaRMatched.at(i) == 1 && BScores.at(i) > minBScore && BScores.at(i) < maxBScore)
            return i;
    return -1;

}
int genBMatching_withPNet(float eta, float phi, ROOT::VecOps::RVec<float> Etas, ROOT::VecOps::RVec<float> Phis, float threshold, ROOT::VecOps::RVec<float> BScores, float minBScore, float maxBScore)
{
    ROOT::VecOps::RVec<bool> deltaRMatched = deltaRMtching(eta, phi, Etas, Phis, threshold);
    int idx = genBMatching_withPNet(deltaRMatched, BScores, minBScore, maxBScore);
    return idx;
}









int genHiggsMatching(ROOT::VecOps::RVec<bool> deltaRMatched, ROOT::VecOps::RVec<float> Masses, float minMass, float maxMass)
{
    for( int i = 0; i < deltaRMatched.size(); i++ )
        if(deltaRMatched.at(i) == 1 && Masses.at(i) > minMass && Masses.at(i) < maxMass)
            return i;
    return -1;

}

int genHiggsMatching(float eta, float phi, ROOT::VecOps::RVec<float> Etas, ROOT::VecOps::RVec<float> Phis, float threshold, ROOT::VecOps::RVec<float> Masses, float minMass, float maxMass)
{
    ROOT::VecOps::RVec<bool> deltaRMatched = deltaRMtching(eta, phi, Etas, Phis, threshold);
    int idx = genHiggsMatching(deltaRMatched, Masses, minMass, maxMass);
    return idx;
}

int genHiggsMatching_withPNet(ROOT::VecOps::RVec<bool> deltaRMatched, ROOT::VecOps::RVec<float> Masses, float minMass, float maxMass, ROOT::VecOps::RVec<float> BScores, float minBScore, float maxBScore)
{
    for( int i = 0; i < deltaRMatched.size(); i++ )
        if(deltaRMatched.at(i) == 1 && Masses.at(i) > minMass && Masses.at(i) < maxMass && BScores.at(i) > minBScore && BScores.at(i) < maxBScore)
            return i;
    return -1;

}

int genHiggsMatching_withPNet(float eta, float phi, ROOT::VecOps::RVec<float> Etas, ROOT::VecOps::RVec<float> Phis, float threshold, ROOT::VecOps::RVec<float> Masses, float minMass, float maxMass, ROOT::VecOps::RVec<float> BScores, float minBScore, float maxBScore)
{
    ROOT::VecOps::RVec<bool> deltaRMatched = deltaRMtching(eta, phi, Etas, Phis, threshold);
    int idx = genHiggsMatching_withPNet(deltaRMatched, Masses, minMass, maxMass, BScores, minBScore, maxBScore);
    return idx;
}
