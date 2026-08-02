using namespace ROOT::VecOps;

int skimmingAK8JetAk4JetLepton(int nFatJet, RVec<float> FatJet_pt, int nJet, RVec<float> Jet_pt, int nMuon, RVec<float> Muon_pt, int nElectron, RVec<float> Electron_pt){
    if(nFatJet < 1 || nJet < 1 || (nMuon < 1 && nElectron < 1) ){
        return 0;
    }
    if (FatJet_pt.at(0) < 250 || Jet_pt.at(0) < 30 ){
        return 0;
    }
    if ( (nMuon > 0 && Muon_pt.at(0) > 20) || (nElectron > 0 && Electron_pt.at(0) > 20) ){
        return 1;
    }
    return 0;
}

int skimming3AK8Jets(int nFatJet, RVec<float> FatJet_pt){
    int n_required_jets = 1;
    if(nFatJet < n_required_jets ){
        return 0;
    }
    if (FatJet_pt.at(n_required_jets - 1) < 250 ){
        return 0;
    }
    return 1;
}

