import ROOT
import json
from hist import Hist
import array
import numpy as np
from TIMBER.Analyzer import Correction, CutGroup, ModuleWorker, analyzer, Node
from TIMBER.Tools.AutoNoiseFilter import AutoNoiseFilter as AutoNF
from TIMBER.Tools.Common import CompileCpp, OpenJSON
import TIMBER.Tools.AutoJME_correctionlib as AutoJME
import TIMBER.Tools.AutoJetID_correctionlib as AutoJetID
import TIMBER.Tools.AutoPU_correctionlib as AutoPU
import TIMBER.Tools.AutoBTagging_correctionlib as AutoBTagging

class TTAnomalous_Analyzer:
    #initiate the analyzer and set up the inputs
    def __init__(self, dataset = None, year = None, n_files = None, i_job = None, nEvents = -1):
        
        #set input variables
        self.dataset = dataset
        self.year = year
        self.n_files = n_files
        self.i_job = i_job
        self.nEvents = nEvents
        
        #loading json files contaning luminosity, Xsection and Trigger info
        with open("raw_nano/Luminosity.json") as f:        
            self.luminosity_json = json.load(f) 
        with open("raw_nano/Xsections_background.json") as f:
            self.Xsection_json = json.load(f)
        with open("raw_nano/Trigger.json") as f:
            self.Trigger_json = json.load(f)
        self.lumi =  self.luminosity_json[self.year]
        
        #Setting up the process, subprocess and Xsection of the job. For Signal the Xsection is set to 1 pb
        if "SignalMC" in self.dataset:
            self.Xsec = 1
            self.process = "SignalMC_XHY4b"
            self.subprocess = "SignalMC_XHY4b"
        elif "Data" in self.dataset:
            self.Xsec = 1
            self.process = "Data"
            self.subprocess = "Data"
        for process in self.Xsection_json:
            if process in self.dataset:
                self.process = process
                for subprocess in self.Xsection_json[process]:
                    if subprocess in self.dataset:
                        self.subprocess = subprocess
                        self.Xsec = self.Xsection_json[process][subprocess]

        #Setting up the year tag used in JME corrections
        self.triggers = {}
        for trigger in self.Trigger_json:
            self.triggers[trigger] = self.Trigger_json[trigger][self.year]
        if self.year == "2022":
            self.corr_year = "2022_Summer22"
        elif self.year == "2022EE":
            self.corr_year = "2022_Summer22EE"
        elif self.year == "2023":
            self.corr_year = "2023_Summer23"
        elif self.year == "2023BPix":
            self.corr_year = "2023_Summer23BPix"
        elif self.year == "2024":
            self.corr_year = "2024_Summer24" 

        self.nanoAOD_ver = 15

        #Setting default if no input args are provided
        if self.dataset == None:
            self.isData = -1
            self.files = None
            self.output = None
            self.analyzer = None
            self.totalWeight = {}
            return

        #Setting isData flag 
        if "Data" in self.dataset or "JetMET" in self.dataset:
            self.isData = 1
        elif "MC" in self.dataset:
            self.isData = 0
        else:
            self.isData = -1
        
        #If the job is data, setting up the era used in JME corrections
        if self.isData == 1:
            eras = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
            for era in eras:
                if (era + "-") in self.dataset:
                    self.data_era = era
        else:
            self.data_era = ""

        #Setting up the default output root file. The Events snapshot, Runs Tree and Cutflow infomation will be stored in this file
        self.output = f"output_{self.n_files}_{self.i_job}.root"
        
        #instantiate a dictionary to store the cutflow infomation. The keys of this dict are the name of the step (cut) and the values are the total weight after the step. "genWeight" is used here.        
        self.totalWeight = {}

        #now that all the info for the job is set up, we start to build the analyzer. Firstly collect the the input files
        if ".root" in self.dataset:
            self.files=[self.dataset]
        
        elif ".txt" in self.dataset:
            with open(self.dataset, "r") as f:
                all_files = f.readlines()
                all_files = [line.strip() for line in all_files]
                N = len(all_files)
                job_files = []
                if (self.i_job * self.n_files) > (N - 1):
                    raise ValueError("i_job * n_files should be less than the total number of files") 
                if ((self.i_job + 1) * self.n_files) <= (N - 1):
                    job_files = all_files[self.i_job * self.n_files : (self.i_job + 1) * self.n_files]
                else:
                    job_files = all_files[self.i_job * self.n_files : N]
            self.files = []
            with open("raw_nano/BAD_ROOT_FILES.txt", "r") as f: #This function is no long in use
                self.bad_files = f.readlines()
                self.bad_files = [_file.strip().split() for _file in self.bad_files]
            for _file in job_files: #remove bad files
                if [self.dataset[(self.dataset.find("raw_nano/") + 9) : ], _file ] not in self.bad_files:
                    self.files.append(_file)
                    print(f"REGISTERING FILE: {self.dataset} {_file}")
                else:
                    print(f"IGNORING BAD FILE: {self.dataset} {_file}")
        else:
            raise ValueError("Input dataset must be a .txt or .root file") 
            

        if len(self.files) == 0:
                raise ValueError("No files are registered successfully") 
        
        #We collected the files and now build the analyzer 
        print(self.files) 
        self.analyzer = analyzer(self.files)
        self.analyzer.isData = self.isData
        if not (self.isData == 1):
            self.sumW = ROOT.RDataFrame("Runs", self.files).Sum("genEventSumw").GetValue()
        else:
            self.sumW = 1 
        if(nEvents > 0): 
            self.analyzer.SetActiveNode(Node("choppedrdf", self.analyzer.GetActiveNode().DataFrame.Range(0, nEvents))) # makes an RDF with only the first nentries considered
        return



 


    #register total weight after a certain step. This will be used to make the cutflow and efficiency plots. weight used is "genWeight"
    def register_weight(self, var, weight = "genWeight"):
        print(var)
        if self.isData == 1:
            self.totalWeight[var] = float(self.analyzer.GetActiveNode().DataFrame.Count().GetValue())
        else:
            #self.totalWeight[var] = float(self.analyzer.GetActiveNode().DataFrame.Count().GetValue())
            self.totalWeight[var] = float(self.analyzer.GetActiveNode().DataFrame.Sum(weight).GetValue())
        print(self.totalWeight[var])
    

    #at the end of the job, we save the cutflow weights to the Cutflow TTree in the output root file
    def save_cutflowInfo(self):    
        print("saving cutflow.................") 
        in_file = ROOT.TFile.Open(self.files[0],"READ")    #Checking if the input files already contain the Cutflow tree. If so, sove it to the output file; if not, create a new Cutflow TTree
        cutflow_tree = in_file.Get("Cutflow")
        new_tree =  (len(self.files) > 1 or (not (cutflow_tree and isinstance(cutflow_tree, ROOT.TTree) and cutflow_tree.GetEntries() == 1))) #flag deciding if creating a new tree
        squashing = cutflow_tree and isinstance(cutflow_tree, ROOT.TTree) #flag if the new tree is should be built from beginning or squashed from existing entries
        in_file.Close()
        if new_tree:
            if squashing:
                print("squashing existing trees.................") 
                rdf_tmp = ROOT.RDataFrame("Cutflow", self.files)
                branches = rdf_tmp.GetColumnNames()
                
                sums = {branch: 0.0 for branch in branches}
                for branch in branches:
                    print("summing " + branch)
                    sums[branch] = rdf_tmp.Sum(branch).GetValue()
                for key in sums:
                    print(key, sums[key])
                #return
                tmp_file = ROOT.TFile.Open("tmp.root","RECREATE")    
                squashed_tree = ROOT.TTree("Cutflow", "Cutflow")
                out_vars = {}
                for branch in branches:
                    print(sums[branch])
                    vec = array.array('d', [sums[branch]])
                    out_vars[branch] = vec
                    
                    squashed_tree.Branch(f"{branch}", vec, f"{branch}/D")    
                    out_vars[branch][0] = sums[branch]
                squashed_tree.Fill()
                squashed_tree.SetDirectory(tmp_file)
                squashed_tree.Write()
                tmp_file.Close()
            else:
                print("creating tree.................") 
                tmp_file = ROOT.TFile.Open("tmp.root","RECREATE")    
                cutflow_tree = ROOT.TTree("Cutflow", "Cutflow")
                n_files = array.array('d', [float(len(self.files))])  
                cutflow_tree.Branch("n_files", n_files, "n_files/D")
                cutflow_tree.Fill()
                cutflow_tree.SetDirectory(tmp_file)
                cutflow_tree.Write()
                tmp_file.Close()
        if new_tree:
            cutflow_rdf = ROOT.RDataFrame("Cutflow", "tmp.root")
        else:
            cutflow_rdf = ROOT.RDataFrame("Cutflow", self.files)
        for w_name in self.totalWeight:
            cutflow_rdf = cutflow_rdf.Define(w_name, f"double({self.totalWeight[w_name]})")
        opts = ROOT.RDF.RSnapshotOptions()
        opts.fMode = "UPDATE"
        cutflow_rdf.Snapshot("Cutflow", self.output, "", opts)
         



        

    #skimming function 
    def skim(self):
        #LOOKS GOOD
        #make skim cut
        self.register_weight("BeforeSkim")
        if self.totalWeight["BeforeSkim"] == 0:
            raise ValueError("file loading failed")
        self.analyzer.Define("SkimFlag","skimmingAK8JetAk4JetLepton(nFatJet,FatJet_pt, nJet,Jet_pt, nMuon, Muon_pt, nElectron, Electron_pt )")
        
        self.analyzer.Cut("SkimFlagCut","SkimFlag>0")
        self.register_weight("Skim")


    def skim_control(self):
        self.register_weight("BeforeSkim")
        if self.totalWeight["BeforeSkim"] == 0:
            raise ValueError("file loading failed")
        self.analyzer.Define("SkimFlag","skimming3AK8Jets(nFatJet,FatJet_pt)")
        
        self.analyzer.Cut("SkimFlagCut","SkimFlag>0")
        self.register_weight("Skim")
    
    #Generating tag to indicate is an event should be masked
    def mask_goldenJson(self):
        if self.isData == 1:
            self.analyzer.Define("goldenJsonMask", f'mask_goldenJson("{self.year}", run, luminosityBlock)')
        else:
            pass
            #raise ValueError("Golden json files can only e applied to data files") 

    #Cut on Golden Json masking
    def cut_goldenJson(self):
        if self.isData == 1:
            self.analyzer.Cut("goldenJsonCut", "goldenJsonMask == 1")
        else:
            pass
            #raise ValueError("Golden json files can only e applied to data files") 
        self.register_weight("GoldenJson")
     
    def selection_muon(self):
        AutoNF(self.analyzer, self.year, self.isData) ###NO JERC correction, but should be fine since the effect is small
        self.register_weight("NoiseFilter")
        AutoJetID.AutoJetID(self.analyzer, self.corr_year, ["Jet","FatJet"])
        if not (self.isData == 1):
            AutoPU.AutoPU(self.analyzer, self.corr_year)
            genW = Correction('genW',"cpp_modules/genW.cc",corrtype='corr')
            evalargs = {
                    "genWeight": "genWeight",
                    "lumi": f"{self.lumi}",
                    "Xsec": f"{self.Xsec}",
                    "sumW": "1"
            }
            self.analyzer.AddCorrection(genW, evalargs)
            self.analyzer.AddCorrection(
                Correction('Pdfweight','TIMBER/Framework/include/PDFweight_uncert.h',[self.analyzer.lhaid],corrtype='uncert')
            )
            self.analyzer.AddCorrection(
                Correction('QCDScaleWeight','cpp_modules/QCDScaleWeight_uncert.cc',[],corrtype='uncert')
            )
            if "TTBar" in self.dataset:
                self.analyzer.AddCorrection(
                    Correction('TopPtWeight','cpp_modules/TopPt_reweighting.cc',[],corrtype='weight')
                )


        ##################TRIGGER##########################################################################
        print(self.triggers) 
        triggers_muon = self.triggers["Muon"]
        triggerCut_muon = self.analyzer.GetTriggerString(triggers_muon)
        self.analyzer.Cut("TriggerCut_muon", triggerCut_muon)
        self.register_weight("TriggerCut")
        

        #################MET################################################################################        
        self.analyzer.Cut("METCUT", "PuppiMET_pt > 70")
        self.register_weight("MET")        


        ################OBJECT SELECTION###################################################################
        self.analyzer.Define("FatJet_goodness", f"goodJet(nFatJet, FatJet_jetId_corr, 2, FatJet_pt, 400,  FatJet_eta, 2.5)") 
        self.analyzer.Define("FatJet_goodness_AFJ", f"goodJet(nFatJet, FatJet_jetId_corr, 2, FatJet_pt, 400,  FatJet_eta, 2.5)") 
        self.analyzer.Define("Jet_goodness", f"goodJet(nJet, Jet_jetId_corr, 2, Jet_pt, 50,  Jet_eta, 2.5)")
        self.analyzer.Define("LowPtMuon_goodness", f"goodLowPtMuon(nMuon, Muon_tightId, Muon_pfIsoId, 4, Muon_pt, 30, 55, Muon_eta, 2.4)") 
        self.analyzer.Define("minRLepJetIdx", "IdxminRLepJet(nMuon, Muon_eta, Muon_phi, nJet, Jet_eta, Jet_phi, Jet_pt, 15)")
        self.analyzer.Define("HighPtMuonIsoID", "goodHighPtLeptonIsoID(nMuon,  minRLepJetIdx, Muon_pt, Muon_eta, Muon_phi, nJet, Jet_eta, Jet_phi , 0.4, 25)")
        self.analyzer.Define("HighPtMuon_goodness", f"goodHighPtMuon(nMuon, Muon_tightId, HighPtMuonIsoID, Muon_highPtId, 2, Muon_pt, 55,  Muon_eta, 2.4 )") 
        self.analyzer.Define("Muon_goodness", f"union_goodness(nMuon, HighPtMuon_goodness, LowPtMuon_goodness)")
 
        self.analyzer.Define("FatJet_TopbWqqVSQCD", f"DefineTagger(nFatJet, FatJet_globalParT3_QCD, FatJet_globalParT3_TopbWqq)")         
        self.analyzer.Define("FatJet_TopVSQCD", f"DefineTagger(nFatJet, FatJet_globalParT3_QCD, FatJet_globalParT3_TopbWqq, FatJet_globalParT3_TopbWq)")         
        self.analyzer.Define("FatJet_XbbVSQCD", f"DefineTagger(nFatJet, FatJet_globalParT3_QCD, FatJet_globalParT3_Xbb)")         
        self.analyzer.Define("FatJet_InverseQCD", f"InvertTagger(nFatJet, FatJet_globalParT3_QCD)")         

        ################EVENT SELECTION################################################################
        self.analyzer.Define("nGoodMuon", "nGood(nMuon, Muon_goodness)")
        self.analyzer.Cut("nGoodMuonCut", "nGoodMuon >= 1")
        self.analyzer.Define("nGoodJet", "nGood(nJet, Jet_goodness)")
        self.analyzer.Cut("nGoodJetCut", "nGoodJet >= 2")
        self.analyzer.Define("nGoodFatJet", "nGood(nFatJet, FatJet_goodness)")
        self.analyzer.Cut("nGoodFatJetCut", "nGoodFatJet >= 1")
        
        #################Identification#####################################################################

        self.analyzer.Define("Idx_Muon", "First_good(nMuon, Muon_goodness)")
        self.analyzer.Define("Pt_muon", "Muon_pt.at(Idx_Muon)")
        self.analyzer.Define("Eta_muon", "Muon_eta.at(Idx_Muon)")
        self.analyzer.Define("Phi_muon", "Muon_phi.at(Idx_Muon)")
        self.analyzer.Define("Mass_muon", "Muon_mass.at(Idx_Muon)")
        self.analyzer.Define("Idx_JT", "FindJT(nFatJet, FatJet_goodness, FatJet_msoftdrop, 105, 210, FatJet_TopVSQCD, 0.9, FatJet_eta, FatJet_phi, Eta_muon, Phi_muon, 0.8 )")
        self.analyzer.Cut("Idx_JT_cut", "Idx_JT >= 0" )
        self.analyzer.Define("Mass_JT", "FatJet_msoftdrop.at(Idx_JT)")
        self.analyzer.Define("Eta_JT", "FatJet_eta.at(Idx_JT)")
        self.analyzer.Define("Phi_JT", "FatJet_phi.at(Idx_JT)")
        self.analyzer.Define("Pt_JT", "FatJet_pt.at(Idx_JT)")
        self.analyzer.Define("Tagger_JT", "FatJet_TopVSQCD.at(Idx_JT)")


        self.analyzer.Define("Idx_JB", "FindJB(nJet, Jet_goodness, Jet_btagUParTAK4B, 0.9, Jet_eta, Jet_phi, Eta_JT, Phi_JT, 1.2 )")
        self.analyzer.Cut("BJet_cut", "Idx_JB >= 0") 
        self.register_weight("BJet")
        self.analyzer.Define("Mass_JB", "Jet_mass.at(Idx_JB)")
        self.analyzer.Define("Eta_JB", "Jet_eta.at(Idx_JB)")
        self.analyzer.Define("Phi_JB", "Jet_phi.at(Idx_JB)")
        self.analyzer.Define("Pt_JB", "Jet_pt.at(Idx_JB)")
        self.analyzer.Define("Tagger_JB", "Jet_btagUParTAK4B.at(Idx_JB)")

        ################Identification##################################################################
       
        self.analyzer.Define("Idx_AFJ", "Find_Anomalous_FatJet(nFatJet, FatJet_goodness, Idx_JT, FatJet_eta, FatJet_phi, Eta_JB, Phi_JB, 1.2 )")
        self.analyzer.Define("Mass_AFJ", "Idx_AFJ < 0? -1.f : FatJet_msoftdrop.at(Idx_AFJ)" )
        self.analyzer.Define("Eta_AFJ", "Idx_AFJ < 0? -100.f : FatJet_eta.at(Idx_AFJ)" )
        self.analyzer.Define("Phi_AFJ", "Idx_AFJ < 0? -100.f : FatJet_phi.at(Idx_AFJ)" )
        self.analyzer.Define("Pt_AFJ", "Idx_AFJ < 0? -1.f : FatJet_pt.at(Idx_AFJ)" )
        self.analyzer.Define("Tagger_AFJ", "Idx_AFJ < 0? -1.f : FatJet_TopVSQCD.at(Idx_AFJ)" )
        userful_scores = ["FatJet_XbbVSQCD", "FatJet_globalParT3_QCD", "FatJet_InverseQCD"] 
        for score in userful_scores:
            self.analyzer.Define(f"Score_{score}_AFJ", f"Idx_AFJ < 0? -1.f : {score}.at(Idx_AFJ)" )
        self.analyzer.MakeWeightCols(name = "All")





    def selection_electron(self):
        AutoNF(self.analyzer, self.year, self.isData) ###NO JERC correction, but should be fine since the effect is small
        self.register_weight("NoiseFilter")
        AutoJetID.AutoJetID(self.analyzer, self.corr_year, ["Jet","FatJet"])
        if not (self.isData == 1):
            AutoPU.AutoPU(self.analyzer, self.corr_year)
            genW = Correction('genW',"cpp_modules/genW.cc",corrtype='corr')
            evalargs = {
                    "genWeight": "genWeight",
                    "lumi": f"{self.lumi}",
                    "Xsec": f"{self.Xsec}",
                    "sumW": "1"
            }
            self.analyzer.AddCorrection(genW, evalargs)
            self.analyzer.AddCorrection(
                Correction('Pdfweight','TIMBER/Framework/include/PDFweight_uncert.h',[self.analyzer.lhaid],corrtype='uncert')
            )
            self.analyzer.AddCorrection(
                Correction('QCDScaleWeight','cpp_modules/QCDScaleWeight_uncert.cc',[],corrtype='uncert')
            )
            if "TTBar" in self.dataset:
                self.analyzer.AddCorrection(
                    Correction('TopPtWeight','cpp_modules/TopPt_reweighting.cc',[],corrtype='weight')
                )


        ##################TRIGGER##########################################################################
        print(self.triggers) 
        triggers = self.triggers["Electron"]
        triggerCut = self.analyzer.GetTriggerString(triggers)
        self.analyzer.Cut("TriggerCut", triggerCut)
        self.register_weight("TriggerCut")
        

        #################MET################################################################################        
        self.analyzer.Cut("METCUT", "PuppiMET_pt > 60")
        self.register_weight("MET")        


        ################OBJECT SELECTION###################################################################
        self.analyzer.Define("FatJet_goodness", f"goodJet(nFatJet, FatJet_jetId_corr, 2, FatJet_pt, 400,  FatJet_eta, 2.5)") 
        self.analyzer.Define("FatJet_goodness_AFJ", f"goodJet(nFatJet, FatJet_jetId_corr, 2, FatJet_pt, 400,  FatJet_eta, 2.5)") 
        self.analyzer.Define("Jet_goodness", f"goodJet(nJet, Jet_jetId_corr, 2, Jet_pt, 50,  Jet_eta, 2.5)")
        self.analyzer.Define("LowPtElectron_goodness", "goodLowPtElectron(nElectron, Electron_mvaIso_WP80, Electron_pt, 35, 120, Electron_superclusterEta, {{0., 1.44}, {1.57, 2.5}})") 
        self.analyzer.Define("minRLepJetIdx", "IdxminRLepJet(nElectron, Electron_eta, Electron_phi, nJet, Jet_eta, Jet_phi, Jet_pt, 15)")
        self.analyzer.Define("HighPtElectronIsoID", "goodHighPtLeptonIsoID(nElectron,  minRLepJetIdx, Electron_pt, Electron_eta, Electron_phi, nJet, Jet_eta, Jet_phi , 0.4, 25)")
        self.analyzer.Define("HighPtElectron_goodness", "goodHighPtElectron(nElectron, Electron_mvaNoIso_WP80, HighPtElectronIsoID, Electron_pt, 120,  Electron_superclusterEta, {{0., 1.44}, {1.57, 2.5}} )") 
        self.analyzer.Define("Electron_goodness", f"union_goodness(nElectron, HighPtElectron_goodness, LowPtElectron_goodness)")
 
        self.analyzer.Define("FatJet_TopbWqqVSQCD", f"DefineTagger(nFatJet, FatJet_globalParT3_QCD, FatJet_globalParT3_TopbWqq)")         
        self.analyzer.Define("FatJet_TopVSQCD", f"DefineTagger(nFatJet, FatJet_globalParT3_QCD, FatJet_globalParT3_TopbWqq, FatJet_globalParT3_TopbWq)")         
        self.analyzer.Define("FatJet_XbbVSQCD", f"DefineTagger(nFatJet, FatJet_globalParT3_QCD, FatJet_globalParT3_Xbb)")         
        self.analyzer.Define("FatJet_InverseQCD", f"InvertTagger(nFatJet, FatJet_globalParT3_QCD)")         

        ################EVENT SELECTION################################################################
        self.analyzer.Define("nGoodElectron", "nGood(nElectron, Electron_goodness)")
        self.analyzer.Cut("nGoodElectronCut", "nGoodElectron >= 1")
        self.analyzer.Define("nGoodJet", "nGood(nJet, Jet_goodness)")
        self.analyzer.Cut("nGoodJetCut", "nGoodJet >= 2")
        self.analyzer.Define("nGoodFatJet", "nGood(nFatJet, FatJet_goodness)")
        self.analyzer.Cut("nGoodFatJetCut", "nGoodFatJet >= 1")
        
        #################Identification#####################################################################

        self.analyzer.Define("Idx_Electron", "First_good(nElectron, Electron_goodness)")
        self.analyzer.Define("Pt_electron", "Electron_pt.at(Idx_Electron)")
        self.analyzer.Define("Eta_electron", "Electron_eta.at(Idx_Electron)")
        self.analyzer.Define("Phi_electron", "Electron_phi.at(Idx_Electron)")
        self.analyzer.Define("Mass_electron", "Electron_mass.at(Idx_Electron)")
        self.analyzer.Define("Idx_JT", "FindJT(nFatJet, FatJet_goodness, FatJet_msoftdrop, 105, 210, FatJet_TopVSQCD, 0.9, FatJet_eta, FatJet_phi, Eta_electron, Phi_electron, 0.8 )")
        self.analyzer.Cut("Idx_JT_cut", "Idx_JT >= 0" )
        self.analyzer.Define("Mass_JT", "FatJet_msoftdrop.at(Idx_JT)")
        self.analyzer.Define("Eta_JT", "FatJet_eta.at(Idx_JT)")
        self.analyzer.Define("Phi_JT", "FatJet_phi.at(Idx_JT)")
        self.analyzer.Define("Pt_JT", "FatJet_pt.at(Idx_JT)")
        self.analyzer.Define("Tagger_JT", "FatJet_TopVSQCD.at(Idx_JT)")


        self.analyzer.Define("Idx_JB", "FindJB(nJet, Jet_goodness, Jet_btagUParTAK4B, 0.9, Jet_eta, Jet_phi, Eta_JT, Phi_JT, 1.2 )")
        self.analyzer.Cut("BJet_cut", "Idx_JB >= 0") 
        self.register_weight("BJet")
        self.analyzer.Define("Mass_JB", "Jet_mass.at(Idx_JB)")
        self.analyzer.Define("Eta_JB", "Jet_eta.at(Idx_JB)")
        self.analyzer.Define("Phi_JB", "Jet_phi.at(Idx_JB)")
        self.analyzer.Define("Pt_JB", "Jet_pt.at(Idx_JB)")
        self.analyzer.Define("Tagger_JB", "Jet_btagUParTAK4B.at(Idx_JB)")

        ################Identification##################################################################
       
        self.analyzer.Define("Idx_AFJ", "Find_Anomalous_FatJet(nFatJet, FatJet_goodness, Idx_JT, FatJet_eta, FatJet_phi, Eta_JB, Phi_JB, 1.2 )")
        self.analyzer.Define("Mass_AFJ", "Idx_AFJ < 0? -1.f : FatJet_msoftdrop.at(Idx_AFJ)" )
        self.analyzer.Define("Eta_AFJ", "Idx_AFJ < 0? -100.f : FatJet_eta.at(Idx_AFJ)" )
        self.analyzer.Define("Phi_AFJ", "Idx_AFJ < 0? -100.f : FatJet_phi.at(Idx_AFJ)" )
        self.analyzer.Define("Pt_AFJ", "Idx_AFJ < 0? -1.f : FatJet_pt.at(Idx_AFJ)" )
        self.analyzer.Define("Tagger_AFJ", "Idx_AFJ < 0? -1.f : FatJet_TopVSQCD.at(Idx_AFJ)" )
        userful_scores = ["FatJet_XbbVSQCD", "FatJet_globalParT3_QCD", "FatJet_InverseQCD"] 
        for score in userful_scores:
            self.analyzer.Define(f"Score_{score}_AFJ", f"Idx_AFJ < 0? -1.f : {score}.at(Idx_AFJ)" )
        self.analyzer.MakeWeightCols(name = "All")












    def selection(self):
        AutoNF(self.analyzer, self.year, self.isData) ###NO JERC correction, but should be fine since the effect is small
        self.register_weight("NoiseFilter")
        AutoJetID.AutoJetID(self.analyzer, self.corr_year, ["Jet","FatJet"])
        if not (self.isData == 1):
            AutoPU.AutoPU(self.analyzer, self.corr_year)
            genW = Correction('genW',"cpp_modules/genW.cc",corrtype='corr')
            evalargs = {
                    "genWeight": "genWeight",
                    "lumi": f"{self.lumi}",
                    "Xsec": f"{self.Xsec}",
                    "sumW": "1"
            }
            self.analyzer.AddCorrection(genW, evalargs)
            self.analyzer.AddCorrection(
                Correction('Pdfweight','TIMBER/Framework/include/PDFweight_uncert.h',[self.analyzer.lhaid],corrtype='uncert')
            )
            self.analyzer.AddCorrection(
                Correction('QCDScaleWeight','cpp_modules/QCDScaleWeight_uncert.cc',[],corrtype='uncert')
            )
            if "TTBar" in self.dataset:
                self.analyzer.AddCorrection(
                    Correction('TopPtWeight','cpp_modules/TopPt_reweighting.cc',[],corrtype='weight')
                )
        print(self.triggers) 
        triggers_muon = self.triggers["Muon"]
        triggerCut_muon = self.analyzer.GetTriggerString(triggers_muon)
        triggers_electron = self.triggers["Electron"]
        triggerCut_electron = self.analyzer.GetTriggerString(triggers_electron)
        if self.isData:
            if "Muon" in self.dataset:
                self.analyzer.Cut("TriggerCut_muon", triggerCut_muon)
            elif "EGamma" in self.dataset:
                self.analyzer.Cut("TriggerCut_electron", triggerCut_electron)
                veto_triggerCut_muon = "!(" + triggerCut_muon + ")"
                self.analyzer.Cut("Veto_TriggerCut_muon", veto_triggerCut_muon) #Remove overlaping events
        else:
            triggerCut_combined = triggerCut_muon + "||"  + triggerCut_electron
            print(triggerCut_combined)
            self.analyzer.Cut("TriggerCut_combined", triggerCut_combined)
        self.register_weight("TriggerCut")
        
        self.analyzer.Cut("METCUT", "PuppiMET_pt > 60")
        self.register_weight("MET")        

        self.analyzer.Define("FatJet_goodness", f"goodJet(nFatJet, FatJet_jetId_corr, 2, FatJet_pt, 300,  FatJet_eta, 2.5)") 
        self.analyzer.Define("Jet_goodness", f"goodJet(nJet, Jet_jetId_corr, 2, Jet_pt, 50,  Jet_eta, 2.5)")
        self.analyzer.Define("Muon_goodness", f"goodMuon(nMuon, Muon_looseId, Muon_pfIsoId, 0, Muon_pt, 40, Muon_eta, 2.4)") 
        self.analyzer.Define("Electron_goodness", f"goodElectron(nElectron, Electron_cutBased, 0, Electron_pt,40, Electron_eta, 2.4)") 
        self.analyzer.Define("FatJet_TopbWqqVSQCD", f"DefineTagger(nFatJet, FatJet_globalParT3_TopbWqq, FatJet_globalParT3_QCD)")         
        self.analyzer.Define("Idx_JT", "FindJT(nFatJet, FatJet_goodness, FatJet_msoftdrop, 150, 200, FatJet_TopbWqqVSQCD, 0.1)")
        self.analyzer.Cut("JT_cut", "Idx_JT >= 0")
        self.register_weight("Idx_JT")
        self.analyzer.Define("Mass_JT", "FatJet_msoftdrop.at(Idx_JT)")
        self.analyzer.Define("Eta_JT", "FatJet_eta.at(Idx_JT)")
        self.analyzer.Define("Phi_JT", "FatJet_phi.at(Idx_JT)")
        self.analyzer.Define("Pt_JT", "FatJet_pt.at(Idx_JT)")
        self.analyzer.Define("Tagger_JT", "FatJet_TopbWqqVSQCD.at(Idx_JT)")

        self.analyzer.Define("Idx_Muon", "FindLepton(nMuon, Muon_goodness, Muon_eta, Muon_phi, Eta_JT, Phi_JT, 2.0 )")
        self.analyzer.Define("Idx_Electron", "FindLepton(nElectron, Electron_goodness, Electron_eta, Electron_phi, Eta_JT, Phi_JT, 2.0)")
        self.analyzer.Cut("Lep_cut", "Idx_Muon >= 0 || Idx_Electron >= 0 ")
        self.register_weight("Idx_Lep")
        self.analyzer.Define("Flavor_Lep", "FindLepFlavor(Idx_Muon, Muon_pt, Idx_Electron, Electron_pt)") #11 for e, 13 for mu
        self.analyzer.Define("Mass_Lep", "Flavor_Lep == 13? Muon_mass.at(Idx_Muon) : Electron_mass.at(Idx_Electron)")
        self.analyzer.Define("Eta_Lep", "Flavor_Lep == 13? Muon_eta.at(Idx_Muon) : Electron_eta.at(Idx_Electron)")
        self.analyzer.Define("Phi_Lep", "Flavor_Lep == 13? Muon_phi.at(Idx_Muon) : Electron_phi.at(Idx_Electron)")
        self.analyzer.Define("Pt_Lep", "Flavor_Lep == 13? Muon_pt.at(Idx_Muon) : Electron_pt.at(Idx_Electron)")


        self.analyzer.Define("Idx_JB", "FindJB(nJet, Jet_goodness, Jet_btagUParTAK4B, 0.5, Jet_eta, Jet_phi, Eta_Lep, Phi_Lep, 1.5 )")
        self.analyzer.Cut("BJet_cut", "Idx_JB >= 0") 
        self.register_weight("BJet")
        self.analyzer.Define("Mass_JB", "Jet_mass.at(Idx_JB)")
        self.analyzer.Define("Eta_JB", "Jet_eta.at(Idx_JB)")
        self.analyzer.Define("Phi_JB", "Jet_phi.at(Idx_JB)")
        self.analyzer.Define("Pt_JB", "Jet_pt.at(Idx_JB)")
        self.analyzer.Define("Tagger_JB", "Jet_btagUParTAK4B.at(Idx_JB)")
        
        self.analyzer.Define("Idx_AFJ", "Find_Anomalous_FatJet(nFatJet, FatJet_goodness, Idx_JT)")
        self.analyzer.Define("Mass_AFJ", "Idx_AFJ < 0? -1.f : FatJet_msoftdrop.at(Idx_AFJ)" )
        self.analyzer.Define("Eta_AFJ", "Idx_AFJ < 0? -100.f : FatJet_eta.at(Idx_AFJ)" )
        self.analyzer.Define("Phi_AFJ", "Idx_AFJ < 0? -100.f : FatJet_phi.at(Idx_AFJ)" )
        self.analyzer.Define("Pt_AFJ", "Idx_AFJ < 0? -1.f : FatJet_pt.at(Idx_AFJ)" )
        self.analyzer.Define("Tagger_AFJ", "Idx_AFJ < 0? -1.f : FatJet_TopbWqqVSQCD.at(Idx_AFJ)" )
        
        self.analyzer.MakeWeightCols(name = "All")





    def selection_control(self):
        AutoNF(self.analyzer, self.year, self.isData) ###NO JERC correction, but should be fine since the effect is small
        self.register_weight("NoiseFilter")
        AutoJetID.AutoJetID(self.analyzer, self.corr_year, ["Jet","FatJet"])
        if not (self.isData == 1):
            AutoPU.AutoPU(self.analyzer, self.corr_year)
            genW = Correction('genW',"cpp_modules/genW.cc",corrtype='corr')
            evalargs = {
                    "genWeight": "genWeight",
                    "lumi": f"{self.lumi}",
                    "Xsec": f"{self.Xsec}",
                    "sumW": "1"
            }
            self.analyzer.AddCorrection(genW, evalargs)
            self.analyzer.AddCorrection(
                Correction('Pdfweight','TIMBER/Framework/include/PDFweight_uncert.h',[self.analyzer.lhaid],corrtype='uncert')
            )
            self.analyzer.AddCorrection(
                Correction('QCDScaleWeight','cpp_modules/QCDScaleWeight_uncert.cc',[],corrtype='uncert')
            )
            if "TTBar" in self.dataset:
                self.analyzer.AddCorrection(
                    Correction('TopPtWeight','cpp_modules/TopPt_reweighting.cc',[],corrtype='weight')
                )
        print(self.triggers) 
        triggers = self.triggers["Hadron"]
        triggerCut = self.analyzer.GetTriggerString(triggers)
        self.analyzer.Cut("TriggerCut", triggerCut)
        self.register_weight("TriggerCut")
        

        self.analyzer.Define("FatJet_goodness", f"goodJet(nFatJet, FatJet_jetId_corr, 2, FatJet_pt, 300,  FatJet_eta, 2.5)") 
        
        #self.analyzer.Define("FatJet_Hadronic", "hadronicJet(nFatJet, FatJet_goodness, FatJet_tagger")
        self.analyzer.Define("Idx_GJ", "FindGluonicJet(nFatJet, FatJet_goodness, FatJet_particleNet_XggVsQCD, 0.8)")

        self.analyzer.Cut("GJCut", "Idx_GJ >= 0")
        self.register_weight("GJ")

        self.analyzer.Define("Mass_GJ", "FatJet_msoftdrop.at(Idx_GJ)")
        self.analyzer.Define("Eta_GJ", "FatJet_eta.at(Idx_GJ)")
        self.analyzer.Define("Phi_GJ", "FatJet_phi.at(Idx_GJ)")
        self.analyzer.Define("Pt_GJ", "FatJet_pt.at(Idx_GJ)")
        self.analyzer.Define("Tagger_GJ", "FatJet_particleNet_XggVsQCD.at(Idx_GJ)")

        
        self.analyzer.MakeWeightCols(name = "All")



    def snapshot(self, columns = None, saveRunChain = False, openOption = "RECREATE"): #saving TTree to the output
        if columns == None:
            with open("raw_nano/columnBlackList.txt","r") as f:
                badColumns = f.read().splitlines()
            with open("raw_nano/columnPrefixBlackList.txt","r") as f:
                badColumnPrefixs = f.read().splitlines()
            with open("raw_nano/columnWhiteList.txt","r") as f:
                goodColumns = f.read().splitlines()
            with open("raw_nano/columnPrefixWhiteList.txt","r") as f:
                goodColumnPrefixs = f.read().splitlines()

            columns = []

            for c in self.analyzer.DataFrame.GetColumnNames(): #defining default saving columns
                passed = 1
                if c in badColumns:
                    passed = 0
                for bad_prefix in badColumnPrefixs:
                    if str(c).startswith(bad_prefix):
                        passed = 0

                if c in goodColumns: #The column list files have the highest prioroty
                    passed = 1
                for good_prefix in goodColumnPrefixs:
                    if str(c).startswith(good_prefix):
                        passed = 1

                if passed == 1:
                    columns.append(c)
        for c in columns:
            print(c)
        print(f"Total number of columns: {len(columns)}")
        self.analyzer.Snapshot(columns, self.output, "Events", saveRunChain = saveRunChain, openOption = openOption)





    def make_TH1(self, bins, weights, f):
        f.cd()
        for column in bins:
            if len(weights) == 0:
                hist = self.analyzer.DataFrame.Histo1D((f"{column}_{self.year}_{self.process}_{self.subprocess}_{self.n_files}_{self.i_job}", f"{column}_{self.year}_{self.process}_{self.subprocess}_{self.n_files}_{self.i_job}", len(bins[column]) - 1, bins[column]), column)
                hist.Write()
            else:
                for weight in weights:
                    hist = self.analyzer.DataFrame.Histo1D((f"{column}_{weight}_{self.year}_{self.process}_{self.subprocess}_{self.n_files}_{self.i_job}", f"{column}_{weight}_{self.year}_{self.process}_{self.subprocess}_{self.n_files}_{self.i_job}", len(bins[column]) - 1, bins[column]), column, weight)
                    hist.Write()




















