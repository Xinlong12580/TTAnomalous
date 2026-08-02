#include <TFile.h>
#include <TMath.h>
#include <stdio.h>
#include <vector>
#include <iostream>
#include "ROOT/RVec.hxx"
#include "TIMBER/Framework/include/common.h"

using namespace ROOT::VecOps;

namespace deltaRMatching {
	using rvec_i = RVec<int>;
	using rvec_f = RVec<float>;

	UInt_t getHIdx(rvec_i GenPart_pdgId, Int_t nGenPart);
	UInt_t getYIdx(rvec_i GenPart_pdgId, Int_t nGenPart);
	std::vector<Int_t> getBFromHIdxs(rvec_i GenPart_pdgId,rvec_i GenPart_genPartIdxMother, Int_t nGenPart);
	std::vector<Int_t> getBFromYIdxs(rvec_i GenPart_pdgId,rvec_i GenPart_genPartIdxMother, Int_t nGenPart);
	Float_t deltaR(Float_t eta1, Float_t phi1, Float_t eta2, Float_t phi2);
	RVec<Int_t> doDRMatching(Int_t nFatJet, Int_t nGenPart, rvec_f FatJet_phi, rvec_f FatJet_eta, rvec_f GenPart_phi, rvec_f GenPart_eta, rvec_i GenPart_pdgId, rvec_i GenPart_genPartIdxMother);
	Float_t getGen_Y_pt(Int_t nGenPart,rvec_i GenPart_pdgId,rvec_f GenPart_pt);
	Float_t getGen_H_pt(Int_t nGenPart,rvec_i GenPart_pdgId,rvec_f GenPart_pt);
	Int_t genJetToRecoMatching(Int_t nGenJet, Float_t FatJet_phi, Float_t FatJet_eta, rvec_f vGenJet_phi, rvec_f vGenJet_eta);
	UInt_t getParticleWithStatus(rvec_i GenPart_pdgId, rvec_i GenPart_statusFlags, Int_t nGenPart, Int_t pdgCode);
	bool IsBitSet(int b, int pos);
	float deltaPhi(float phi1,float phi2);


	void deltaRMatching(){
	    return;
	}

	float deltaPhi(float phi1, float phi2) {
		float result = phi1 - phi2;
		while (result > TMath::Pi()) result -= 2*TMath::Pi();
		while (result <= -TMath::Pi()) result += 2*TMath::Pi();
		return result;
	}

	Int_t genJetToRecoMatching(Int_t nGenJet, Float_t FatJet_phi, Float_t FatJet_eta, rvec_f vGenJet_phi, rvec_f vGenJet_eta){
	//Returns GenJet idx closest to coordinates of a reco jet
	//search for closest or first within 0.4?
	    Float_t distance = 0.5;
	    Float_t minDelta = 1.0;
	    Int_t closestIdx = -1;
	    Float_t GenJetEta, GenJetPhi, delta;
	    for(Int_t GenJetIdx=0; GenJetIdx<nGenJet;GenJetIdx++){
	    
		GenJetEta = vGenJet_eta[GenJetIdx];
		GenJetPhi = vGenJet_phi[GenJetIdx];
		delta     = deltaRMatching::deltaR(FatJet_eta,FatJet_phi,GenJetEta,GenJetPhi);

		if(delta<distance && delta<minDelta){
		    closestIdx = GenJetIdx;
		}
	    }

	    //std::cout<<"Couldn't match Gen to Reco";
	    return closestIdx;
	}


	RVec<Int_t> doDRMatching(Int_t nFatJet, Int_t nGenPart, rvec_f FatJet_phi, rvec_f FatJet_eta, rvec_f GenPart_phi, rvec_f GenPart_eta, rvec_i GenPart_pdgId, rvec_i GenPart_genPartIdxMother){
	//Returns FatJet indices in event i matched to H and Y, respectively
	//Example: <1,3> would mean FatJet[1] is matched to H, FatJet[3] to Y
	//Returns -1 if no match for a particular boson
	//Example: <4,-1> would mean FatJet[4] is matched to H, but no FatJets are matched to Y


	    UInt_t HIdx                 = getHIdx(GenPart_pdgId,nGenPart);
	    Float_t HEta                = GenPart_eta[HIdx];
	    Float_t HPhi                = GenPart_phi[HIdx];

	    UInt_t YIdx                 = getYIdx(GenPart_pdgId,nGenPart);
	    Float_t YEta                = GenPart_eta[YIdx];
	    Float_t YPhi                = GenPart_phi[YIdx];

	    vector<Int_t> BfromHIdxs    = getBFromHIdxs(GenPart_pdgId,GenPart_genPartIdxMother,nGenPart);
	    Float_t b1_H_eta            = GenPart_eta[BfromHIdxs[0]];
	    Float_t b2_H_eta            = GenPart_eta[BfromHIdxs[1]];
	    Float_t b1_H_phi            = GenPart_phi[BfromHIdxs[0]];
	    Float_t b2_H_phi            = GenPart_phi[BfromHIdxs[1]];
	 
	    vector<Int_t> BfromYIdxs    = getBFromYIdxs(GenPart_pdgId,GenPart_genPartIdxMother,nGenPart);
	    Float_t b1_Y_eta            = GenPart_eta[BfromYIdxs[0]];
	    Float_t b2_Y_eta            = GenPart_eta[BfromYIdxs[1]];
	    Float_t b1_Y_phi            = GenPart_phi[BfromYIdxs[0]];
	    Float_t b2_Y_phi            = GenPart_phi[BfromYIdxs[1]];

	    Int_t YFatJetMatchIdx       = -1;
	    Int_t HFatJetMatchIdx       = -1;

	    Float_t distance = 0.8;

	    for(Int_t fatJetIdx=0; fatJetIdx<nFatJet;fatJetIdx++){
	    
		Float_t fatJetEta = FatJet_eta[fatJetIdx];
		Float_t fatJetPhi = FatJet_phi[fatJetIdx];

		Float_t deltaJetH   = deltaR(fatJetEta,fatJetPhi,HEta,HPhi);
		Float_t deltaJetHb1 = deltaR(fatJetEta,fatJetPhi,b1_H_eta,b1_H_phi);
		Float_t deltaJetHb2 = deltaR(fatJetEta,fatJetPhi,b2_H_eta,b2_H_phi);

		Float_t deltaJetY   = deltaR(fatJetEta,fatJetPhi,YEta,YPhi);
		Float_t deltaJetYb1 = deltaR(fatJetEta,fatJetPhi,b1_Y_eta,b1_Y_phi);
		Float_t deltaJetYb2 = deltaR(fatJetEta,fatJetPhi,b2_Y_eta,b2_Y_phi);


		if(deltaJetH<distance && deltaJetHb1<distance && deltaJetHb2<distance){
		    HFatJetMatchIdx = fatJetIdx;
		}
		if(deltaJetY<distance && deltaJetYb1<distance && deltaJetYb2<distance){
		    YFatJetMatchIdx = fatJetIdx;
		}

	    }

	    RVec<Int_t>matchedFatJets = {HFatJetMatchIdx,YFatJetMatchIdx};
	    return matchedFatJets;
	}

	Float_t getGen_Y_pt(Int_t nGenPart,rvec_i GenPart_pdgId,rvec_f GenPart_pt){
	    UInt_t  YIdx = getYIdx(GenPart_pdgId,nGenPart);
	    Float_t Ypt  = GenPart_pt[YIdx];
	    return Ypt;
	}

	Float_t getGen_H_pt(Int_t nGenPart,rvec_i GenPart_pdgId,rvec_f GenPart_pt){
	    UInt_t  HIdx = getHIdx(GenPart_pdgId,nGenPart);
	    Float_t Hpt  = GenPart_pt[HIdx];
	    return Hpt;
	}

	Float_t deltaR(Float_t eta1, Float_t phi1, Float_t eta2, Float_t phi2){
	    Float_t deltaEta      = eta2-eta1;
	    Float_t deltaPhi_corr = deltaRMatching::deltaPhi(phi1,phi2);//if |phi1-phi2|>pi, reduce it by pi
	    Float_t deltaR        = TMath::Sqrt(deltaEta*deltaEta+deltaPhi_corr*deltaPhi_corr);
	    return deltaR;
	}


	UInt_t getHIdx(rvec_i GenPart_pdgId, Int_t nGenPart){
	//Returns the idx at which pdgId=25 (H)
	    for(Int_t i=0; i<nGenPart; ++i)
		if(GenPart_pdgId[i]==25)
		    return i;

	    std::cout<<"Warning: Couldn't find H\n";
	    return -1;
	}

	UInt_t getYIdx(rvec_i GenPart_pdgId, Int_t nGenPart){
	//Returns the idx at which pdgId=35 (Y)
	    for(Int_t i=0; i<nGenPart; ++i)
		if(GenPart_pdgId[i]==35)
		    return i;

	    std::cout<<"Warning: Couldn't find Y\n";
	    return -1;
	}


	UInt_t getParticleWithStatus(rvec_i GenPart_pdgId, rvec_i GenPart_statusFlags, Int_t nGenPart, Int_t status , Int_t pdgCode){
	    for(Int_t i=0; i<nGenPart; ++i){
		if(GenPart_pdgId[i]==pdgCode && IsBitSet(GenPart_statusFlags[i],status))
		    return i;
	    }

	    std::cout<<"Warning: Couldn't find particle with pdgId"<< pdgCode << " \n";
	    return -1;
	}


	bool IsBitSet(int num, int pos)
	{
	    std::bitset<16> bits(num);
	    std:bool bitAtPos = bits[pos];
	    return bitAtPos;
	}



	std::vector<Int_t> getBFromHIdxs(rvec_i GenPart_pdgId,rvec_i GenPart_genPartIdxMother, Int_t nGenPart){
	//Returns the indices of 2 b quarks from H decay
	    std::vector<Int_t> bIdxs;

	    for(Int_t i=0; i<nGenPart; ++i){
		if(GenPart_pdgId[i]==5 || GenPart_pdgId[i]==-5){
		    Int_t motherIdx = GenPart_genPartIdxMother[i];
		    //std::cout<<motherIdx<<" "<<GenPart_pdgId[motherIdx]<<"\n";
		    if(GenPart_pdgId[motherIdx]==25){
			bIdxs.push_back(i);
		    }
		}
		if(bIdxs.size()==2){
		    return bIdxs;
		}
	    }

	    std::cout<<"Warning: Couldn't find bb from H\n";
	    bIdxs = {-1,-1};
	    return bIdxs;
	}

	std::vector<Int_t> getBFromYIdxs(rvec_i GenPart_pdgId,rvec_i GenPart_genPartIdxMother, Int_t nGenPart){
	//Returns the indices of 2 b quarks from H decay
	    std::vector<Int_t> bIdxs;

	    for(Int_t i=0; i<nGenPart; ++i){
		if(GenPart_pdgId[i]==5 || GenPart_pdgId[i]==-5){
		    Int_t motherIdx = GenPart_genPartIdxMother[i];
		    //std::cout<<motherIdx<<" "<<GenPart_pdgId[motherIdx]<<"\n";
		    if(GenPart_pdgId[motherIdx]==35){
			bIdxs.push_back(i);
		    }
		}
		if(bIdxs.size()==2){
		    return bIdxs;
		}
	    }

	    std::cout<<"Warning: Couldn't find bb from Y\n";
	    bIdxs = {-1,-1};
	    return bIdxs;
	}
}
