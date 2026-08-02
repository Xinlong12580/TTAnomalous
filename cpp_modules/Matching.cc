#include "TIMBER/Framework/include/common.h"
namespace HGG 
{
	Float_t InvalidF=-999999.;
}

//Matching the Valuess to the Idxs
RVec<Float_t> FQuantityMatching (RVec<Int_t> Idxs, RVec<Float_t> Vals)
{
	RVec<Float_t> Matched_vals = {};
	for (int i = 0; i< Idxs.size(); i++)
	{
		if (Idxs.at(i) < 0) 
			Matched_vals.push_back(HGG::InvalidF);
		else 
			Matched_vals.push_back(Vals.at(Idxs.at(i)));
	}
	return Matched_vals;
}

RVec<Int_t> FMaxIdxFinding(RVec<Float_t> Vals, Int_t nRequired)
{
       	RVec<Int_t> MaxIdxs(nRequired, -1);
	if (Vals.size() < nRequired)
		return MaxIdxs;
                //throw std::runtime_error("Vector size should be larger than the required number");
       std::priority_queue<Float_t, RVec<Float_t>, std::greater<Float_t>> Maxs; //use a priority_queque tostrip the smallest variables
       for (auto val : Vals)
       {
	       Maxs.push(val);
	       if(Maxs.size() > nRequired)
		       Maxs.pop();
       }
       MaxIdxs.clear();
       while(! Maxs.empty())
       {
	       MaxIdxs.push_back(std::distance(Vals.begin(), std::find(Vals.begin(), Vals.end(), Maxs.top())));
	       Maxs.pop();
       }
       return MaxIdxs;
}

RVec<Int_t> LeptonPairIdxFinding(RVec<Float_t> Vals, RVec<Int_t> Signs)
{
	if(Vals.size() != Signs.size())
                throw std::runtime_error("Value vector and sign vector should be of the same size");
	RVec<Int_t> Pos_idxs = {};
	RVec<Float_t> Pos_vals = {};
	RVec<Int_t> Neg_idxs = {};
	RVec<Float_t> Neg_vals = {};
	for( Int_t i = 0; i < Vals.size(); i++)
	{
		if (Signs.at(i) == 1)
		{
			Pos_idxs.push_back(i);
			Pos_vals.push_back(Vals.at(i));
		}
		else if (Signs.at(i) == -1)
		{
			Neg_idxs.push_back(i);
			Neg_vals.push_back(Vals.at(i));
		}
	}
	Int_t pos_idx = FMaxIdxFinding(Pos_vals, 1).at(0);
	Int_t neg_idx = FMaxIdxFinding(Neg_vals, 1).at(0);
	Int_t pos_idx_oriVec = pos_idx >= 0 ? Pos_idxs.at(pos_idx) : -1;
	Int_t neg_idx_oriVec = neg_idx >= 0 ? Neg_idxs.at(neg_idx) : -1;
	RVec<Int_t> Idxs = {pos_idx_oriVec, neg_idx_oriVec};
	return Idxs;
		
}

RVec<Int_t> GenRelevantPartMatching_HGGWLNu(Int_t nGenPart,RVec<Int_t> GenPart_pdgId, RVec<Int_t> GenPart_genPartIdxMother) 
{ 
        ROOT::VecOps::RVec<Int_t> Idxs={-1 , -1 , -1 , -1 , -1 , -1 , -1}; // Mother W, Higgs, Gluon, Gluon, Daughter W, Lepton, Neutrino 
        //Looking for two gluons from Higgs
	Int_t count=0; 
        for (Int_t i = 0 ; i < nGenPart ; i++)
	{ 
            if (GenPart_pdgId[i] == 21 && GenPart_genPartIdxMother[i] >= 0 && GenPart_pdgId[GenPart_genPartIdxMother[i]] == 25)
	    { 
                Idxs.at(count+2) = i;
                count++; 
                if(count == 2) 
			break;
            } 
        }
	//If two gluons share the same mother, then register the mother
	if(Idxs.at(2) > 0 && Idxs.at(3) > 0 && GenPart_genPartIdxMother[Idxs.at(2)] == GenPart_genPartIdxMother[Idxs.at(3)])
		Idxs.at(1)=GenPart_genPartIdxMother[Idxs.at(2)];	
       	
	//Looking for the mother W
	
	if( Idxs.at(1) > 0)
	{
		Idxs.at(0) = GenPart_genPartIdxMother[Idxs.at(1)];
		//The mother of a Higgs could be another Higgs due to generator features. so we trace back until finding the real mother
		while( GenPart_pdgId[Idxs.at(0)] == 25 )
		{
			Idxs.at(0) = GenPart_genPartIdxMother[Idxs.at(0)];
		}
	}

        //We can't find the mother W from the gen info, so we directly look for the lepton and the neutrino from a W
	for (Int_t i = 0 ; i < nGenPart ; i++)
	{ 
            if (GenPart_pdgId[GenPart_genPartIdxMother[i]] == -24 || GenPart_pdgId[GenPart_genPartIdxMother[i]] == 24)
	    {
			if(GenPart_pdgId[i] == 11 || GenPart_pdgId[i] == 13 || GenPart_pdgId[i] == 15 || GenPart_pdgId[i] == -11 || GenPart_pdgId[i] == -13 || GenPart_pdgId[i] == -15)//Lepton
                		Idxs.at(5) = i;
			else if(GenPart_pdgId[i] == -12 || GenPart_pdgId[i] == -14 || GenPart_pdgId[i] == -16 || GenPart_pdgId[i] == 12 || GenPart_pdgId[i] == 14 || GenPart_pdgId[i] == 16)
                		Idxs.at(6) = i;
	    }

        }
	//If the lepton and the neotrino are from the same W, then register the W as the daughter W
	if(Idxs.at(5) > 0 && Idxs.at(6) > 0 && GenPart_genPartIdxMother[Idxs.at(5)] == GenPart_genPartIdxMother[Idxs.at(6)])
		Idxs.at(4) = GenPart_genPartIdxMother[Idxs.at(5)];
	
	//to-do: Should add another check that the daughter W and the Higgs are from the same mother
	
        return Idxs; 
} 


RVec<Int_t> GenRelevantPartMatching_HGGZLL(Int_t nGenPart,RVec<Int_t> GenPart_pdgId, RVec<Int_t> GenPart_genPartIdxMother) 
{ 
        ROOT::VecOps::RVec<Int_t> Idxs={-1 , -1 , -1 , -1 , -1 , -1 , -1}; // Mother W, Higgs, Gluon, Gluon, Daughter W, Lepton, Antilepton 
        //Looking for two gluons from Higgs
	Int_t count=0; 
        for (Int_t i = 0 ; i < nGenPart ; i++)
	{ 
            if (GenPart_pdgId[i] == 21 && GenPart_genPartIdxMother[i] >= 0 && GenPart_pdgId[GenPart_genPartIdxMother[i]] == 25)
	    { 
                Idxs.at(count+2) = i;
                count++; 
                if(count == 2) 
			break;
            } 
        }
	//If two gluons share the same mother, then register the mother
	if(Idxs.at(2) > 0 && Idxs.at(3) > 0 && GenPart_genPartIdxMother[Idxs.at(2)] == GenPart_genPartIdxMother[Idxs.at(3)])
		Idxs.at(1)=GenPart_genPartIdxMother[Idxs.at(2)];	
       	
	//Looking for the mother W
	
	if( Idxs.at(1) > 0)
	{
		Idxs.at(0) = GenPart_genPartIdxMother[Idxs.at(1)];
		//The mother of a Higgs could be another Higgs due to generator features. so we trace back until finding the real mother
		while( GenPart_pdgId[Idxs.at(0)] == 25 )
		{
			Idxs.at(0) = GenPart_genPartIdxMother[Idxs.at(0)];
		}
	}

        //We can't find the mother W from the gen info, so we directly look for the lepton and the neutrino from a W
	
	for (Int_t i = 0 ; i < nGenPart ; i++)
	{ 
            if (GenPart_pdgId[GenPart_genPartIdxMother[i]] == 23)
	    {
			if(GenPart_pdgId[i] == 11 || GenPart_pdgId[i] == 13 || GenPart_pdgId[i] == 15)//Lepton
                		Idxs.at(5) = i;
			else if(GenPart_pdgId[i] == -11 || GenPart_pdgId[i] == -13 || GenPart_pdgId[i] == -15)//Lepton
                		Idxs.at(6) = i;
	    }
        }

	//to-do: Should check if the lepton pair is of the same flavor

	//If the lepton and the neotrino are from the same W, then register the W as the daughter W
	if(Idxs.at(5) > 0 && Idxs.at(6) > 0 && GenPart_genPartIdxMother[Idxs.at(5)] == GenPart_genPartIdxMother[Idxs.at(6)])
		Idxs.at(4) = GenPart_genPartIdxMother[Idxs.at(5)];
	
	//to-do: Should add another check that the daughter W and the Higgs are from the same mother
	
        return Idxs; 
}


//Function for matching Reco particles to a GenPart with delta R method                             
Int_t RecoPartMatching_deltaR(Float_t gen_eta, Float_t gen_phi, RVec<Float_t> Reco_etas, RVec<Float_t> Reco_phis, Float_t deltaR_thrhd=0.4) {
        Int_t idx = -1;
        if(Reco_phis.size() != Reco_etas.size())
                throw std::runtime_error("Eta vector and Phi vector should be of the same size");
        Float_t best_deltaR = 10000000.;
        //Loop over all etas and phis to find the best match
        for (Int_t i = 0; i < Reco_etas.size(); i++)
	{
                Float_t reco_eta = Reco_etas[i];
                Float_t reco_phi = Reco_phis[i];
		Float_t deltaEta = std::abs(gen_eta-reco_eta);
                Float_t deltaPhi = std::abs(gen_phi-reco_phi) < M_PI ? std::abs(gen_phi - reco_phi) : 2*M_PI - std::abs(gen_phi - reco_phi);
                Float_t deltaR=sqrt(deltaEta * deltaEta + deltaPhi * deltaPhi);
                if(deltaR < best_deltaR)
		{
                        idx = i;
                        best_deltaR = deltaR;
                }
        }
        //Check if the best match satisfies the criteria
        if(best_deltaR > deltaR_thrhd)
                idx = -1;
        return idx;
}


//Overloading function to Reco matching for a vector of GnParts
RVec<Int_t> RecoPartMatching_deltaR(RVec<Float_t> Gen_etas, RVec<Float_t> Gen_phis, RVec<Float_t> Reco_etas, RVec<Float_t> Reco_phis, Float_t deltaR_thrhd=0.4) 
{
        if(Reco_phis.size() != Reco_etas.size() || Gen_phis.size() != Gen_etas.size())
                throw std::runtime_error("Eta vector and Phi vector should be of the same size");
	RVec<Int_t> Idxs(Gen_etas.size(), -1);
	for(Int_t i = 0; i < Gen_etas.size(); i++)
		Idxs.at(i) = RecoPartMatching_deltaR(Gen_etas.at(i), Gen_phis.at(i), Reco_etas, Reco_phis, deltaR_thrhd);
	return Idxs;
}

//Overloading function to take the Idxs of GenParts as input
RVec<Int_t> RecoPartMatching_deltaR(RVec<Int_t> Gen_Idxs, RVec<Float_t> Gen_etas, RVec<Float_t> Gen_phis, RVec<Float_t> Reco_etas, RVec<Float_t> Reco_phis, Float_t deltaR_thrhd=0.4) 
{
	RVec<Float_t> Relevant_gen_etas = FQuantityMatching(Gen_Idxs, Gen_etas);	
	RVec<Float_t> Relevant_gen_phis = FQuantityMatching(Gen_Idxs, Gen_phis);	
	RVec<Int_t> Idxs = RecoPartMatching_deltaR(Relevant_gen_etas, Relevant_gen_phis, Reco_etas, Reco_phis, deltaR_thrhd);
	return Idxs;
}

//Matching FatJets to 2 GenParts
Int_t FatJetMatching_deltaR(RVec<Float_t> Gen_etas, RVec<Float_t> Gen_phis, RVec<Float_t> FatJet_etas, RVec<Float_t> FatJet_phis, Float_t deltaR_thrhd=0.8) 
{ 
	if(Gen_etas.size() != 2 || Gen_phis.size() != 2)
                throw std::runtime_error("Gen Vector should be of size 2");
	Int_t idx = -1;
	Int_t idx0 = RecoPartMatching_deltaR(Gen_etas.at(0), Gen_phis.at(0), FatJet_etas, FatJet_phis, deltaR_thrhd);
	Int_t idx1 = RecoPartMatching_deltaR(Gen_etas.at(1), Gen_phis.at(1), FatJet_etas, FatJet_phis, deltaR_thrhd);
	if (idx0 == idx1) 
		idx=idx0;
	return idx;
}

//Overloading function take the gen idxs as input
	
Int_t FatJetMatching_deltaR(RVec<Int_t> Gen_idxs, RVec<Float_t> Gen_etas, RVec<Float_t> Gen_phis, RVec<Float_t> FatJet_etas, RVec<Float_t> FatJet_phis, Float_t deltaR_thrhd=0.8) 
{ 
	RVec<Float_t> Relevant_gen_etas = FQuantityMatching(Gen_idxs, Gen_etas);
	RVec<Float_t> Relevant_gen_phis = FQuantityMatching(Gen_idxs, Gen_phis);
	Int_t idx = FatJetMatching_deltaR(Relevant_gen_etas,  Relevant_gen_phis, FatJet_etas, FatJet_phis, deltaR_thrhd);
	return idx;
}

//Calculate Inv mass for a list of variables
Float_t InvMass_PtEtaPhiM(ROOT::VecOps::RVec<Float_t> Pts, ROOT::VecOps::RVec<Float_t> Etas,  ROOT::VecOps::RVec<Float_t> Phis, ROOT::VecOps::RVec<Float_t> Masss)
{
	Float_t inv_mass = HGG::InvalidF;
	RVec<ROOT::Math::PtEtaPhiMVector> Vectors = {};
	
	for(Int_t i = 0; i < Pts.size(); i++)
	{
		//If one value in the list is invalid, return invalid inv mass
		if(Pts.at(i) < (HGG::InvalidF + 10) ||  Etas.at(i) < (HGG::InvalidF + 10) || Phis.at(i) < (HGG::InvalidF + 10) || Masss.at(i) < (HGG::InvalidF + 10))
		{
			inv_mass = HGG::InvalidF;
			return inv_mass;
		}
		
		ROOT::Math::PtEtaPhiMVector vector(Pts.at(i), Etas.at(i), Phis.at(i), Masss.at(i));
		Vectors.push_back(vector);
	}
	inv_mass = hardware::InvariantMass(Vectors);
	return inv_mass;
}
