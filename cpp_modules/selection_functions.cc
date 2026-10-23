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

RVec<bool> goodLowPtElectron(int nElectron, RVec<bool> Electron_id, RVec<float> Electron_pt, float pt_min, float pt_max, RVec<float>  Electron_eta,  RVec<std::pair<float, float>> eta_ranges ){
    RVec<bool> IsGood = {};
    for(Int_t i=0; i<nElectron;i++){
        bool inRange = false;
        for (const auto& range : eta_ranges) {
            if (range.first < TMath::Abs(Electron_eta.at(i)) && range.second > TMath::Abs(Electron_eta.at(i)) ) {inRange = true; break;}
        }
        if(inRange && Electron_id[i] && Electron_pt[i]>pt_min &&  Electron_pt[i]<pt_max){
            IsGood.push_back(true);
        }
        else{
            IsGood.push_back(false);
        }
    }
    return IsGood;
}

RVec<bool> goodHighPtElectron(int nElectron, RVec<bool> Electron_id, RVec<bool> goodHighPtElectronIsoID, RVec<float> Electron_pt, float pt_min,  RVec<float>  Electron_eta,  RVec<std::pair<float, float>> eta_ranges ){
    RVec<bool> IsGood = {};
    for(Int_t i=0; i<nElectron;i++){
        bool inRange = false;
        for (const auto& range : eta_ranges) {
            if (range.first < TMath::Abs(Electron_eta.at(i)) && range.second > TMath::Abs(Electron_eta.at(i)) ) {inRange = true; break;}
        }
        if(inRange && Electron_id[i] && goodHighPtElectronIsoID[i] && Electron_pt[i]>pt_min){
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

RVec<bool> goodHighPtLeptonIsoID(int nMuon,  RVec<int> IdxminRLepJet, RVec<float> Muon_pt, RVec<float> Muon_eta, RVec<float>  Muon_phi, int nJet, RVec<float> Jet_eta, RVec<float>  Jet_phi , float R_min, float pt_rel_min){
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

RVec<float> InvertTagger(int nJet, RVec<float> Tagger){
    RVec<float> InverseTagger = {};
    for(Int_t i=0; i<nJet;i++){
        InverseTagger.push_back(1 / std::max(float(Tagger.at(i)), float(1e-6) ) );
    }
    return InverseTagger;
}

RVec<float> OneminusTagger(int nJet, RVec<float> Tagger){
    RVec<float> OneminusTagger = {};
    for(Int_t i=0; i<nJet;i++){
        OneminusTagger.push_back(1. - Tagger.at(i));
    }
    return OneminusTagger;
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

RVec<bool> FindJBCandidates(int nJet, RVec<bool> Jet_goodness, RVec<float> Jet_tagger, float tagger_min, RVec<float> Jet_eta, RVec<float> Jet_phi, float Eta_JT, float Phi_JT, float R_min ){
    RVec<bool> IsGood = {};  
    RVec<float> DeltaRs = DeltaR(Jet_eta, Jet_phi, Eta_JT, Phi_JT);
    for (int i = 0; i < nJet; i++){
        if (Jet_goodness.at(i) && DeltaRs.at(i) > R_min && Jet_tagger.at(i) > tagger_min ) IsGood.push_back(true);
        else IsGood.push_back(false);
    }
    return IsGood;
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

std::pair<int, int> FindJB(int nJet, RVec<bool> BTaggedJet_goodness, RVec<float> Jet_pt, RVec<float> Jet_eta, RVec<float> Jet_phi, RVec<float> Jet_mass, float Pt_Lep, float Eta_Lep, float Phi_Lep, float Mass_Lep, float Pt_Nu, std::pair<float, float> EtaCandidates_Nu, float Phi_Nu, float Mass_Nu = 0., float top_mass = 173. )
{
    float min_mass_diff = 10000000.;
    int best_idx = -1;
    int best_eta_idx = -1;
    for (int i = 0; i < nJet; i++){
        if(! BTaggedJet_goodness.at(i)) continue;
        for (int j = 0; j < 2; j ++){
            float Eta_Nu = (j==0) ? EtaCandidates_Nu.first : EtaCandidates_Nu.second;
            float inv_mass = InvMass_PtEtaPhiM({Jet_pt.at(i), Pt_Lep, Pt_Nu}, {Jet_eta.at(i), Eta_Lep, Eta_Nu}, {Jet_phi.at(i), Phi_Lep, Phi_Nu}, {Jet_mass.at(i), Mass_Lep, Mass_Nu});
            float mass_diff = std::abs(inv_mass - top_mass);
            if (mass_diff < min_mass_diff){
                min_mass_diff = mass_diff;
                best_idx = i;
                best_eta_idx = j;
            }
        }
    }
    std::pair <int, int> Idx_JB_and_Eta_Nu;
    Idx_JB_and_Eta_Nu.first = best_idx;
    Idx_JB_and_Eta_Nu.second = best_eta_idx;
    return Idx_JB_and_Eta_Nu;
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

std::pair<std::complex<float> , std::complex<float> > SolvePz(float invMass, float Pt_1, float Eta_1, float Phi_1, float Mass_1, float Pt_2, float Phi_2, float Mass_2 ){
    std::pair<std::complex<float> , std::complex<float> > PzCandidates;
    float Mt_1 = std::sqrt(Mass_1 * Mass_1 + Pt_1 * Pt_1);
    float Mt_2 = std::sqrt(Mass_2 * Mass_2 + Pt_2 * Pt_2);
    float Pz_1 = Pt_1 * std::sinh(Eta_1);
    float D = ( invMass * invMass - Mass_1 * Mass_1 - Mass_2 * Mass_2 + 2 * Pt_1 * Pt_2 * std::cos(Phi_1 - Phi_2) ) / 2;
    float a = Mt_1 * Mt_1;
    float b = - 2 * D * Pz_1;
    float c = Mt_1 * Mt_1 * Mt_2 * Mt_2 + Pz_1 * Pz_1 * Mt_2 * Mt_2 - D * D;
    std::complex<float>  disc = std::complex<float>  ( b * b - 4 * a * c );
    
    PzCandidates.first = (-b + std::sqrt(disc)) / (2 * a);
    PzCandidates.second = (-b - std::sqrt(disc)) / (2 * a);
    return PzCandidates;

}
std::pair<std::complex<float> , std::complex<float> > SolveEta(float invMass, float Pt_1, float Eta_1, float Phi_1, float Mass_1, float Pt_2, float Phi_2, float Mass_2 ){
    std::pair<std::complex<float> , std::complex<float> > PzCandidates = SolvePz(invMass, Pt_1, Eta_1, Phi_1, Mass_1, Pt_2, Phi_2, Mass_2 );
    std::pair<std::complex<float> , std::complex<float> > EtaCandidates;
    EtaCandidates.first = std::asinh(PzCandidates.first / Pt_2 );
    EtaCandidates.second = std::asinh(PzCandidates.second / Pt_2 );
    return EtaCandidates;
}

template <typename T>
std::pair<T , T > SolveEta(std::pair<T , T > PzCandidates, float Pt ){
    std::pair<T , T > EtaCandidates;
    EtaCandidates.first = std::asinh(PzCandidates.first / Pt );
    EtaCandidates.second = std::asinh(PzCandidates.second / Pt );
    return EtaCandidates;
}



std::pair<float, float> real_part(std::pair<std::complex<float> , std::complex<float> > complex_pair){
    std::pair<float, float> real_pair;
    real_pair.first = complex_pair.first.real();
    real_pair.second = complex_pair.second.real();
    return real_pair;
}
bool isReal(std::complex<float> complex_number ){
    if (std::abs(complex_number.imag() ) < 1e-6) return true;
    return false;
}

bool isReal(std::pair<std::complex<float> , std::complex<float> > complex_pair){
    if (isReal(complex_pair.first) && isReal(complex_pair.second) ) return true;
    return false;
}
