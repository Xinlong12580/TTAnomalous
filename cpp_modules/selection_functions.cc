#include "TIMBER/Framework/include/common.h"
#include "cpp_modules/share.h"

//Calculating DeltaR of two points
float DeltaR(RVec<float> Etas, RVec<float> Phies){
    float deltaEta = std::abs(Etas[0] - Etas[1]);
    float deltaPhi = std::abs(Phies[0]-Phies[1]) < M_PI ? std::abs(Phies[0] - Phies[1]) : 2*M_PI - std::abs(Phies[0] - Phies[1]);
    float deltaR=sqrt(deltaEta * deltaEta + deltaPhi * deltaPhi);
    return deltaR;
}

//Calculating DeltaR of each object in a collection with respect to a given point
RVec<float> DeltaR(RVec<float> Etas, RVec<float> Phies, float eta, float phi){
    if (Etas.size() != Phies.size())
        throw std::runtime_error("Eta vector and Phi vector should be of the same size");
    RVec<float> Delta_Rs = {};
    for (int i = 0; i < Etas.size(); i++){
        float deltaR = DeltaR({Etas.at(i), eta}, {Phies.at(i), phi});
        //std::cout<<deltaR<<std::endl;
        Delta_Rs.push_back(deltaR);
    }
    return Delta_Rs;
}



RVec<bool> goodJet(int nJet, RVec<int> Jet_jetId, int jetId_min, RVec<float> Jet_pt, float pt_min, RVec<float> Jet_eta, float absEta_max){
    RVec<bool> IsGood = {};
    for (int i = 0; i < nJet; i ++){
        if (Jet_jetId.at(i) >= jetId_min && Jet_pt.at(i) >= pt_min && std::abs(Jet_eta.at(i)) <= absEta_max )
            IsGood.push_back(true);
        else
             IsGood.push_back(false);
    }
    return IsGood;
}



RVec<bool> goodJet_withMass(int nJet, RVec<int> Jet_jetId, int jetId_min, RVec<float> Jet_pt, float pt_min, RVec<float> Jet_mass0, float mass0_min, RVec<float> Jet_mass1, float mass1_min, RVec<float> Jet_eta, float absEta_max){
    RVec<bool> IsGood = {};
    for (int i = 0; i < nJet; i ++){
        if (Jet_jetId.at(i) >= jetId_min && Jet_pt.at(i) >= pt_min && (Jet_mass0.at(i) >= mass0_min || Jet_mass1.at(i) >= mass1_min) && std::abs(Jet_eta.at(i)) <= absEta_max )
            IsGood.push_back(true);
        else
             IsGood.push_back(false);
    }
    return IsGood;
}

int nGood(int nGoodness, RVec<bool> Goodness){
    int n = 0;
    for(Int_t i=0; i<nGoodness;i++){
        if(Goodness.at(i)) n++;
    }
    return n;
}




RVec<bool> goodMuon(int nMuon, RVec<bool> Muon_id, RVec<char> Muon_pfIsoId, int iso_cut, RVec<float> Muon_pt, float pt_cut, RVec<float>  Muon_eta, float eta_cut ){
    RVec<bool> IsGood = {};
    for(Int_t i=0; i<nMuon;i++){
        if(Muon_id[i] && int(Muon_pfIsoId[i])>iso_cut && Muon_pt[i]>pt_cut && TMath::Abs(Muon_eta[i])<eta_cut){
            IsGood.push_back(true);
        }
        else{
            IsGood.push_back(false);
        }
    }
    return IsGood;
}

RVec<bool> goodLowPtMuon(int nMuon, RVec<bool> Muon_id, RVec<char> Muon_pfIsoId, int iso_cut, RVec<float> Muon_pt, float pt_min, float pt_max, RVec<float>  Muon_eta, float eta_cut ){
    RVec<bool> IsGood = {};
    for(Int_t i=0; i<nMuon;i++){
        if(Muon_id[i] && int(Muon_pfIsoId[i])>=iso_cut && Muon_pt[i]>pt_min &&  Muon_pt[i]<pt_max && TMath::Abs(Muon_eta[i])<eta_cut){
            IsGood.push_back(true);
        }
        else{
            IsGood.push_back(false);
        }
    }
    return IsGood;
}

RVec<bool> goodHighPtMuon(int nMuon, RVec<bool> Muon_id, RVec<bool> goodHighPtMuonIsoID, RVec<char> Muon_highPtId, int highPt_cut, RVec<float> Muon_pt, float pt_min,  RVec<float>  Muon_eta, float eta_cut ){
    RVec<bool> IsGood = {};
    for(Int_t i=0; i<nMuon;i++){
        if(Muon_id[i] && goodHighPtMuonIsoID[i] && int(Muon_highPtId[i])>=highPt_cut && Muon_pt[i]>pt_min && TMath::Abs(Muon_eta[i])<eta_cut){
            IsGood.push_back(true);
        }
        else{
            IsGood.push_back(false);
        }
    }
    return IsGood;
}

RVec<int> IdxminRLepJet(int nLep, RVec<float> Lep_eta, RVec<float>  Lep_phi, int nJet, RVec<float> Jet_eta, RVec<float>  Jet_phi, RVec<float> Jet_pt, float jet_pt_min){
    RVec<int> Indices = {};
    for(Int_t i=0; i<nLep;i++){
        int Idx = -1;
        float R_min = 10000000000000.;
        for(Int_t j=0; j<nJet;j++){
            if (Jet_pt.at(j) < jet_pt_min) continue;
            float R = DeltaR(RVec<float> {Lep_eta.at(i), Jet_eta.at(j)}, RVec<float> {Lep_phi.at(i),  Jet_phi.at(j)}) ;
            if(R < R_min){
                R_min = R;
                Idx = j;
            }
        }
        Indices.push_back(Idx);
    }
    return Indices;
}


float rel_pt(float pt, float eta, float phi,  float eta0, float phi0){
    float _tmp = cosh(eta)*cosh(eta) - (cos(phi - phi0) + sinh(eta)*sinh(eta0)) * (cos(phi - phi0) + sinh(eta)*sinh(eta0)) / cosh(eta0) / cosh(eta0); 
    return pt*sqrt( max(_tmp, 0.0f) );
}

RVec<bool> goodHighPtMuonIsoID(int nMuon,  RVec<int> IdxminRLepJet, RVec<float> Muon_pt, RVec<float> Muon_eta, RVec<float>  Muon_phi, int nJet, RVec<float> Jet_eta, RVec<float>  Jet_phi , float R_min, float pt_rel_min){
    RVec<bool> IsGood = {};
    for(Int_t i=0; i<nMuon;i++){
        int j = IdxminRLepJet.at(i);
        if (j < 0) { IsGood.push_back(true); continue;}
        float R = DeltaR(RVec<float> {Muon_eta.at(i), Jet_eta.at(j)}, RVec<float> {Muon_phi.at(i),  Jet_phi.at(j)});
        if(R > R_min){ IsGood.push_back(true); continue;} 
        float pt_rel = rel_pt(Muon_pt.at(i), Muon_eta.at(i), Muon_phi.at(i), Jet_eta.at(j), Jet_phi.at(j));
        if (pt_rel > pt_rel_min) { IsGood.push_back(true); continue;}
        IsGood.push_back(false); 
    }
    return IsGood;
}



RVec<bool> union_goodness(int nLep, RVec<bool> goodness1, RVec<bool> goodness2){
    RVec<bool> IsGood = {};
    for(Int_t i=0; i<nLep;i++){
        if (goodness1.at(i) || goodness2.at(i))
            IsGood.push_back(true);
        else
            IsGood.push_back(false);
    }
    return IsGood;
}

RVec<bool> goodElectron( int nElectron, RVec<int> Electron_cutBased, int id_cut, RVec<float> Electron_pt, float pt_cut, RVec<float> Electron_eta, float eta_cut){
    RVec<bool> IsGood = {};
    for(Int_t i=0; i<nElectron;i++){
        if(Electron_cutBased[i]>id_cut && Electron_pt[i]>pt_cut && TMath::Abs(Electron_eta[i])<eta_cut)
            IsGood.push_back(true);
        else
            IsGood.push_back(false);
    }
    return IsGood;
}

RVec<float> DefineTagger(int nJet, RVec<float> Tagger_QCD, RVec<float> Tagger_target){
    RVec<float> Tagger = {};
    for(Int_t i=0; i<nJet;i++){
        Tagger.push_back(Tagger_target.at(i) / (Tagger_target.at(i) + Tagger_QCD.at(i)));
    }
    return Tagger;
}

RVec<float> DefineTagger(int nJet, RVec<float> Tagger_QCD, RVec<float> Tagger_target1, RVec<float> Tagger_target2){
    RVec<float> Tagger = {};
    for(Int_t i=0; i<nJet;i++){
        Tagger.push_back((Tagger_target1.at(i) + Tagger_target2.at(i)) / (Tagger_target1.at(i) + Tagger_target2.at(i) + Tagger_QCD.at(i)));
    }
    return Tagger;
}

int FindJT( int nFatJet, RVec<bool> FatJet_goodness, RVec<float> FatJet_msoftdrop, float mass_min, float mass_max, RVec<float> FatJet_TopVSQCD, float tagger_min ){
    int idx_JT = -1;
    for (int i = 0; i<nFatJet; i++){
        if (FatJet_goodness.at(i) && FatJet_msoftdrop.at(i) > mass_min && FatJet_msoftdrop.at(i) < mass_max && FatJet_TopVSQCD.at(i) > tagger_min){
            idx_JT = i;
            break;
        }
    }
    return idx_JT;
}

int FindJT( int nFatJet, RVec<bool> FatJet_goodness, RVec<float> FatJet_msoftdrop, float mass_min, float mass_max, RVec<float> FatJet_TopVSQCD, float tagger_min, RVec<float> FatJet_eta, RVec<float> FatJet_phi, float Eta_muon, float Phi_muon, float deltaR_min ){
    int idx_JT = -1;
    for (int i = 0; i<nFatJet; i++){
        if (FatJet_goodness.at(i) && FatJet_msoftdrop.at(i) > mass_min && FatJet_msoftdrop.at(i) < mass_max && FatJet_TopVSQCD.at(i) > tagger_min){
            float deltaR = DeltaR( {FatJet_eta.at(i), Eta_muon}, {FatJet_phi.at(i), Phi_muon});
            if(deltaR > deltaR_min){
                idx_JT = i;
                break;
            }
        }
    }
    return idx_JT;
}

int FindLepton(int nLep, RVec<bool> Lep_goodness, RVec<float> Lep_eta, RVec<float> Lep_phi, float Eta_JT, float Phi_JT, float R_min ){
    int idx_Lep = -1;
    RVec<float> DeltaRs = DeltaR(Lep_eta, Lep_phi, Eta_JT, Phi_JT);
    for (int i = 0; i < nLep; i++){
        if (Lep_goodness.at(i) && DeltaRs.at(i) > R_min ){
            idx_Lep = i;
            break;
        }
    }
    return idx_Lep;
}

int FindLepFlavor(int Idx_Muon, RVec<int> Muon_pt, int Idx_Electron, RVec<int> Electron_pt){
    if (Idx_Muon < 0) return 11;
    if (Idx_Electron < 0) return 13;
    return ( Muon_pt.at(Idx_Muon) > Electron_pt.at(Idx_Electron)? 13 : 11);
}

int FindJB(int nJet, RVec<bool> Jet_goodness, RVec<float> Jet_tagger, float tagger_min, RVec<float> Jet_eta, RVec<float> Jet_phi, float Eta_JT, float Phi_JT, float R_min ){
    int idx_JB = -1;
    RVec<float> DeltaRs = DeltaR(Jet_eta, Jet_phi, Eta_JT, Phi_JT);
    for (int i = 0; i < nJet; i++){
        if (Jet_goodness.at(i) && DeltaRs.at(i) > R_min && Jet_tagger.at(i) > tagger_min ){
            idx_JB = i;
            break;
        }
    }
    return idx_JB;
}

int Find_Anomalous_FatJet( int nFatJet, RVec<bool> FatJet_goodness, int Idx_JT){
    int Idx_AFJ = -1;
     for (int i = 0; i < nFatJet; i++){
        if (FatJet_goodness.at(i) && Idx_JT != i ){
            Idx_AFJ = i;
            break;
        }
    }
    return Idx_AFJ;
}

int Find_Anomalous_FatJet( int nFatJet, RVec<bool> FatJet_goodness, int Idx_JT, RVec<float> FatJet_eta, RVec<float> FatJet_phi, float Eta_JB, float Phi_JB, float R_min ){
    int Idx_AFJ = -1;
    RVec<float> DeltaRs = DeltaR(FatJet_eta, FatJet_phi, Eta_JB, Phi_JB);
     for (int i = 0; i < nFatJet; i++){
        if (FatJet_goodness.at(i) && Idx_JT != i && DeltaRs.at(i) > R_min ){
            Idx_AFJ = i;
            break;
        }
    }
    return Idx_AFJ;
}

int FindGluonicJet(int nFatJet, RVec<bool> FatJet_goodness, RVec<float> FatJet_particleNet_XggVsQCD, float min_WP){
    int Idx_GJ = -1;
     for (int i = 0; i < nFatJet; i++){
        if (FatJet_goodness.at(i) && FatJet_particleNet_XggVsQCD.at(i) > min_WP ){
            Idx_GJ = i;
            break;
        }
    }
    return Idx_GJ;
}

int First_good(int nPart, RVec<bool> Goodness){
    for (int i = 0; i < nPart; i++){     
        if(Goodness.at(i)) return i;
    }
    return -1;
}

//Calculate Inv mass for a list of variables
Float_t InvMass_PtEtaPhiM(ROOT::VecOps::RVec<Float_t> Pts, ROOT::VecOps::RVec<Float_t> Etas,  ROOT::VecOps::RVec<Float_t> Phis, ROOT::VecOps::RVec<Float_t> Masss)
{
	Float_t inv_mass = SHARE::InvalidF;
	RVec<ROOT::Math::PtEtaPhiMVector> Vectors = {};
	
	for(Int_t i = 0; i < Pts.size(); i++)
	{
		//If one value in the list is invalid, return invalid inv mass
		if(Pts.at(i) < (SHARE::InvalidF + 10) ||  Etas.at(i) < (SHARE::InvalidF + 10) || Phis.at(i) < (SHARE::InvalidF + 10) || Masss.at(i) < (SHARE::InvalidF + 10))
		{
			inv_mass = SHARE::InvalidF;
			return inv_mass;
		}
		
		ROOT::Math::PtEtaPhiMVector vector(Pts.at(i), Etas.at(i), Phis.at(i), Masss.at(i));
		Vectors.push_back(vector);
	}
	inv_mass = hardware::InvariantMass(Vectors);
	return inv_mass;
}

float Rapidity(float pt, float eta, float phi, float mass){
     
    ROOT::Math::PtEtaPhiMVector vector(pt, eta, phi, mass);
    //if ( ! (vector.Rapidity()  > -50) ){
    //    std::cout<<vector.Rapidity()<<" "<<pt<<" "<<eta<<" "<<phi<<" "<<mass<<std::endl;
    //    throw "error";
    //}
    return vector.Rapidity();
}

float DeltaRapidity(float pt_0, float eta_0, float phi_0, float mass_0, float pt_1, float eta_1, float phi_1, float mass_1){
    float Y_0 = Rapidity(pt_0, eta_0, phi_0, mass_0);
    float Y_1 = Rapidity(pt_1, eta_1, phi_1, mass_1);
    return (Y_0 - Y_1);
}

ROOT::VecOps::RVec<Float_t> makeTXbb(int nFatJet, ROOT::VecOps::RVec<Float_t> FatJet_Xbb, ROOT::VecOps::RVec<Float_t> FatJet_QCD){
    ROOT::VecOps::RVec<Float_t> TXbb = {};
    for (int i = 0; i < nFatJet; i ++){
        TXbb.push_back(FatJet_Xbb.at(i) / (FatJet_Xbb.at(i) + FatJet_QCD.at(i)));
    }
    return TXbb;
}
template <class _type>
bool debugger(_type input, std::string extra = ""){
    std::cout<<extra<<" DEBUGGER: "<<input<<std::endl;
    return 0;
}
