#include <TMath.h>
#include <stdio.h>
#include <iostream>
#include <TRandom.h>

int getRand01(){
    //randomly returns 0 or 1
    static long seed = 1;
    seed++;
    TRandom randGen = TRandom(seed);
    int rand = randGen.Binomial(1,0.5);
    return rand;   
}


Int_t idxCloserToHiggsMass(Float_t m0, Float_t m1);
Int_t higgsMassMatching(Float_t m0, Float_t m1);
Int_t higgsMassMatchingAlternative(Float_t m0, Float_t m1);

Int_t idxCloserToHiggsMass(Float_t m0, Float_t m1){
//returns index of the jet closer in mass to Higgs jet mass (125)
	Float_t diff0 = TMath::Abs(m0-125.0);
	Float_t diff1 = TMath::Abs(m1-125.0);
	if(diff0<=diff1){
		return 0;
	}
	else{
		return 1;
	}
}

Int_t higgsMassMatching(Float_t m0, Float_t m1, float mass_low = 110, float mass_high = 140){
//returns index of the Higgs jet
//criterion is that it falls into 110-140 GeV mass window
//if both are in the window, choose randomly
	int HcandidateFlag0 = 0;
	int HcandidateFlag1 = 0;

	if(m0 > mass_low && m0 < mass_high ){
		HcandidateFlag0 = 1;
	}
	if(m1 > mass_low && m1 < mass_high ){
		HcandidateFlag1 = 1;
	}
	if(HcandidateFlag0==1 && HcandidateFlag1!=1){
		return 0;
	}
	if(HcandidateFlag1==1 && HcandidateFlag0!=1){
		return 1;
	}
	if(HcandidateFlag0==1 && HcandidateFlag1==1){
		int res = getRand01();
		return res;
	}
	return -1;
}


Int_t higgsMassMatchingAlternative(Float_t m0, Float_t m1){
//returns index of the Higgs jet
//criterion is that it falls into 110-140 GeV mass window
//if both are in the window, choose one closer to 125
	int HcandidateFlag0 = 0;
	int HcandidateFlag1 = 0;

	if(m0 > 110 && m0 < 140 ){
		HcandidateFlag0 = 1;
	}
	if(m1 > 110 && m1 < 140 ){
		HcandidateFlag1 = 1;
	}
	if(HcandidateFlag0==1 && HcandidateFlag1!=1){
		return 0;
	}
	if(HcandidateFlag1==1 && HcandidateFlag0!=1){
		return 1;
	}
	if(HcandidateFlag0==1 && HcandidateFlag1==1){
		int res = idxCloserToHiggsMass(m0,m1);
		return res;
	}
	return -1;
}
