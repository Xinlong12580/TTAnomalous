
int find_part(ROOT::VecOps::RVec<int> pdgIds, int pdgId = 25){
    int idx = -1;
    for (int i = 0; i < pdgIds.size(); i++){
        if(pdgIds.at(i) == pdgId)
            idx = i;   
    }
    return idx;
}

ROOT::VecOps::RVec<int> find_b(ROOT::VecOps::RVec<int> pdgIds, ROOT::VecOps::RVec<int> motherIdxes, int pdgId = 35){
    ROOT::VecOps::RVec<int> idxes = {-1, -1};
    //std::cout<<"TEST0"<<std::endl;
    for (int i = 0; i < pdgIds.size(); i++){
        if(pdgIds.at(i) == 5 && motherIdxes.at(i) < pdgIds.size() && pdgIds.at(motherIdxes.at(i)) == pdgId){
            idxes.at(0) = i;
            break;
        }
    }
    //std::cout<<"TEST1"<<std::endl;
    for (int i = 0; i < pdgIds.size(); i++){
        if(pdgIds.at(i) == -5 && motherIdxes.at(i) < pdgIds.size() && pdgIds.at(motherIdxes.at(i)) == pdgId){
            idxes.at(1) = i;
            break;
        }
    }
    return idxes;
}

TLorentzVector vec(float pt, float eta, float phi, float mass){
    TLorentzVector v;
    v.SetPtEtaPhiM(pt, eta, phi, mass);
    return v;
}
