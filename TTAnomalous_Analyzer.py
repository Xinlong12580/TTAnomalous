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
        self.analyzer.Define("HighPtMuonIsoID", "goodHighPtMuonIsoID(nMuon,  minRLepJetIdx, Muon_pt, Muon_eta, Muon_phi, nJet, Jet_eta, Jet_phi , 0.4, 25)")
        self.analyzer.Define("HighPtMuon_goodness", f"goodHighPtMuon(nMuon, Muon_tightId, HighPtMuonIsoID, Muon_highPtId, 2, Muon_pt, 55,  Muon_eta, 2.4 )") 
        self.analyzer.Define("Muon_goodness", f"union_goodness(nMuon, HighPtMuon_goodness, LowPtMuon_goodness)")
 
        self.analyzer.Define("FatJet_TopbWqqVSQCD", f"DefineTagger(nFatJet, FatJet_globalParT3_QCD, FatJet_globalParT3_TopbWqq)")         
        self.analyzer.Define("FatJet_TopVSQCD", f"DefineTagger(nFatJet, FatJet_globalParT3_QCD, FatJet_globalParT3_TopbWqq, FatJet_globalParT3_TopbWq)")         

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


        self.analyzer.Define("Idx_JB", "FindJB(nJet, Jet_goodness, Jet_btagUParTAK4B, 0.5, Jet_eta, Jet_phi, Eta_JT, Phi_JT, 1.2 )")
        self.analyzer.Cut("BJet_cut", "Idx_JB >= 0") 
        self.register_weight("BJet")
        self.analyzer.Define("Mass_JB", "Jet_mass.at(Idx_JB)")
        self.analyzer.Define("Eta_JB", "Jet_eta.at(Idx_JB)")
        self.analyzer.Define("Phi_JB", "Jet_phi.at(Idx_JB)")
        self.analyzer.Define("Pt_JB", "Jet_pt.at(Idx_JB)")
        self.analyzer.Define("Tagger_JB", "Jet_btagUParTAK4B.at(Idx_JB)")

        ################Identification##################################################################
        
        #self.analyzer.Define("Idx_AFJ", "Find_Anomalous_FatJet(nFatJet, FatJet_goodness, Idx_JT)")
        self.analyzer.Define("Idx_AFJ", "Find_Anomalous_FatJet(nFatJet, FatJet_goodness, Idx_JT, FatJet_eta, FatJet_phi, Eta_JB, Phi_JB, 1.2 )")
        self.analyzer.Define("Mass_AFJ", "Idx_AFJ < 0? -1.f : FatJet_msoftdrop.at(Idx_AFJ)" )
        self.analyzer.Define("Eta_AFJ", "Idx_AFJ < 0? -100.f : FatJet_eta.at(Idx_AFJ)" )
        self.analyzer.Define("Phi_AFJ", "Idx_AFJ < 0? -100.f : FatJet_phi.at(Idx_AFJ)" )
        self.analyzer.Define("Pt_AFJ", "Idx_AFJ < 0? -1.f : FatJet_pt.at(Idx_AFJ)" )
        self.analyzer.Define("Tagger_AFJ", "Idx_AFJ < 0? -1.f : FatJet_TopVSQCD.at(Idx_AFJ)" )
        
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




























    def selection_1p1_BDT(self, JME_syst = "nom", region = "Signal", triggerType = "Hadron", massType = "regressedMass", top_fac = 0., do_tagger_corr = 1):
        #Requiring two FatJets 
        self.analyzer.Cut("SkimCut", "SkimFlag == 1 || SkimFlag == 3") 
        self.register_weight("SkimOf1p1")
        AutoNF(self.analyzer, self.year, self.isData) ###NO JERC correction, but should be fine since the effect is small
        self.register_weight("NoiseFilter")
        #lepton veto
        self.analyzer.Define("nEle", "nElectrons(nElectron, Electron_cutBased, 0, Electron_pt,20, Electron_eta)")
        self.analyzer.Define("nMu", "nMuons(nMuon, Muon_looseId, Muon_pfIsoId, 0, Muon_pt, 20, Muon_eta)")
        self.analyzer.Cut("LeptonVetoCut", "nMu==0 && nEle==0")
        self.register_weight("LeptonVeto")
        

        AutoJetID.AutoJetID(self.analyzer, self.corr_year, ["Jet","FatJet"])
        AutoJME.AutoJME(self.analyzer, ["Jet", "FatJet"], self.corr_year, self.data_era, True, AK8Calib_extras = ["regressedMass"])
        AutoJME.AutoJME_mSD(self.analyzer, self.corr_year, self.data_era)
        self.register_weight("JERCJetVeto")
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
                 

        
        #triggers
        triggers = self.triggers[triggerType]
        print(triggers)
        triggerCut = self.analyzer.GetTriggerString(triggers)
        print(triggerCut)
        self.analyzer.Cut("TriggerCut", triggerCut)
        self.register_weight("TriggerCut")

        self.analyzer.Define("FatJet_goodness", f"goodJet(nFatJet, FatJet_jetId_corr, 2, FatJet_pt_{JME_syst}, 300,  FatJet_eta, 2.5)") 
        
        #Higgs Match
        if region == "Validation":
            self.analyzer.Define("idxH", f"FindIdxJH_random(FatJet_{massType}_{JME_syst}, 60, 100, 2, FatJet_goodness)")
        if region == "AValidation":
            self.analyzer.Define("idxH", f"FindIdxJH_random(FatJet_{massType}_{JME_syst}, 200, 250, 2, FatJet_goodness)")
        elif region == "Signal":
            self.analyzer.Define("idxH", f"FindIdxJH_random(FatJet_{massType}_{JME_syst}, 100, 150, 2, FatJet_goodness)")
        elif region == "Control":
            self.analyzer.Define("idxH_veto", f"FindIdxJH(FatJet_{massType}_{JME_syst}, 100, 150, FatJet_goodness, 125)")
            self.analyzer.Cut("HiggsVeto", "idxH_veto < 0")
            self.register_weight("HiggsVeto")
            self.analyzer.Define("idxH", f"FindIdxJH_random(FatJet_{massType}_{JME_syst}, 150, 200, 2, FatJet_goodness)")

        self.analyzer.Define("idxY", "FindIdxJY(FatJet_goodness, idxH)")
        self.analyzer.Cut("HiggsCut", "idxH >= 0 && idxY >= 0") 
        self.register_weight("HiggsMatch")

        self.analyzer.Define("Delta_Eta", "abs(FatJet_eta.at(idxH) - FatJet_eta.at(idxY))")
        #self.analyzer.Define("Delta_Y", f"abs(DeltaRapidity(FatJet_pt_{JME_syst}.at(idxH),FatJet_eta.at(idxH), FatJet_phi.at(idxH), FatJet_msoftdrop_{JME_syst}.at(idxH), FatJet_pt_{JME_syst}.at(idxY),FatJet_eta.at(idxY), FatJet_phi.at(idxY), FatJet_msoftdrop_{JME_syst}.at(idxY)))")
        self.analyzer.Define("Delta_Y", f"abs(DeltaRapidity(FatJet_pt_{JME_syst}.at(idxH),FatJet_eta.at(idxH), FatJet_phi.at(idxH), FatJet_{massType}_{JME_syst}.at(idxH), FatJet_pt_{JME_syst}.at(idxY),FatJet_eta.at(idxY), FatJet_phi.at(idxY), FatJet_{massType}_{JME_syst}.at(idxY)))")

    
        ROOT.gInterpreter.Declare(f'TaggerDiscretizer AK8_Discretizer = TaggerDiscretizer("FatJet",  "{self.corr_year}", "");')
        #ROOT.gInterpreter.Declare(f'TaggerDiscretizer AK4_Discretizer = TaggerDiscretizer("Jet",  "{self.corr_year}", "UParTAK4_wp_values");')
        #Defining a bunch of variables for later use
        self.analyzer.Define("MassHiggsCandidate",f"FatJet_msoftdrop_{JME_syst}[idxH]")
        self.analyzer.Define("MassHiggsCandidate_regressed",f"FatJet_regressedMass_{JME_syst}[idxH]")
        self.analyzer.Define("PtHiggsCandidate", f"FatJet_pt_{JME_syst}[idxH]")
        self.analyzer.Define("EtaHiggsCandidate", "FatJet_eta[idxH]")
        self.analyzer.Define("PhiHiggsCandidate", "FatJet_phi[idxH]")
        self.analyzer.Define("Tagger_PNetXbb_H", "FatJet_particleNet_XbbVsQCD[idxH]")
        self.analyzer.Define("Tagger_Xbb_H", "FatJet_globalParT3_Xbb[idxH]")
        self.analyzer.Define("Tagger_QCD_H", "FatJet_globalParT3_QCD[idxH]")
        self.analyzer.Define("Tagger_TopbWqq_H", "FatJet_globalParT3_TopbWqq[idxH]")
        self.analyzer.Define("Tagger_TopbWq_H", "FatJet_globalParT3_TopbWq[idxH]")
        self.analyzer.Define("Tagger_H", f"Tagger_Xbb_H / (Tagger_Xbb_H + Tagger_QCD_H + {top_fac} * Tagger_TopbWqq_H)")
        self.analyzer.Define("Tagger_H_discrete", f"AK8_Discretizer.eval(Tagger_H)")
        self.analyzer.Define("Tagger_H_decapitated", f"AK8_Discretizer.decapitate(Tagger_H)")
        if  self.isData != 1 :
            self.analyzer.Define("TFlavor_H", f"classifyProbeJet(PhiHiggsCandidate, EtaHiggsCandidate, nGenPart, GenPart_phi,GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)")
        
        self.analyzer.Define("MassYCandidate", f"FatJet_msoftdrop_{JME_syst}[idxY]")
        self.analyzer.Define("MassYCandidate_regressed",f"FatJet_regressedMass_{JME_syst}[idxY]")
        self.analyzer.Define("PtYCandidate", f"FatJet_pt_{JME_syst}[idxY]")
        self.analyzer.Define("EtaYCandidate", "FatJet_eta[idxY]")
        self.analyzer.Define("PhiYCandidate", "FatJet_phi[idxY]")
        self.analyzer.Define("Tagger_PNetXbb_Y", "FatJet_particleNet_XbbVsQCD[idxY]")
        self.analyzer.Define("Tagger_Xbb_Y", "FatJet_globalParT3_Xbb[idxY]")
        self.analyzer.Define("Tagger_QCD_Y", "FatJet_globalParT3_QCD[idxY]")
        self.analyzer.Define("Tagger_TopbWqq_Y", "FatJet_globalParT3_TopbWqq[idxY]")
        self.analyzer.Define("Tagger_TopbWq_Y", "FatJet_globalParT3_TopbWq[idxY]")
        self.analyzer.Define("Tagger_Y", f"Tagger_Xbb_Y / (Tagger_Xbb_Y + Tagger_QCD_Y + {top_fac} * Tagger_TopbWqq_Y)")
        self.analyzer.Define("Tagger_Y_discrete", f"AK8_Discretizer.eval(Tagger_Y)")
        self.analyzer.Define("Tagger_Y_decapitated", f"AK8_Discretizer.decapitate(Tagger_Y)")
        if  self.isData != 1:
            self.analyzer.Define("TFlavor_Y", f"classifyProbeJet(PhiYCandidate, EtaYCandidate, nGenPart, GenPart_phi,GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)")
        
        #X(JJ) Mass
        self.analyzer.Define(f"MassLeadingTwoFatJets", "InvMass_PtEtaPhiM({PtHiggsCandidate, PtYCandidate}, {EtaHiggsCandidate, EtaYCandidate}, {PhiHiggsCandidate, PhiYCandidate}, {MassHiggsCandidate, MassYCandidate})")
        self.analyzer.Define(f"MassLeadingTwoFatJets_regressed", "InvMass_PtEtaPhiM({PtHiggsCandidate, PtYCandidate}, {EtaHiggsCandidate, EtaYCandidate}, {PhiHiggsCandidate, PhiYCandidate}, {MassHiggsCandidate_regressed, MassYCandidate})")
        self.analyzer.Define(f"MassLeadingTwoFatJets_regressed_regressed", "InvMass_PtEtaPhiM({PtHiggsCandidate, PtYCandidate}, {EtaHiggsCandidate, EtaYCandidate}, {PhiHiggsCandidate, PhiYCandidate}, {MassHiggsCandidate_regressed, MassYCandidate_regressed})")


        self.analyzer.Define("leadingFatJetPt", f"FatJet_pt_{JME_syst}[0]")
        self.analyzer.Define("leadingFatJetPhi", "FatJet_phi[0]")
        self.analyzer.Define("leadingFatJetEta", "FatJet_eta[0]")
        self.analyzer.Define("leadingFatJetMsoftdrop", f"FatJet_msoftdrop_{JME_syst}[0]")
        self.analyzer.Define("MX", "MassLeadingTwoFatJets")
        self.analyzer.Define("MY", "MassYCandidate")
        if massType == "regressedMass":        
            self.analyzer.Define("MH", "MassHiggsCandidate_regressed")
        elif massType == "msoftdrop":
            self.analyzer.Define("MH", "MassHiggsCandidate")
        self.analyzer.Define("reco_mY", "MY") 
        self.analyzer.Define("reco_mX", "MX") 
        self.analyzer.Define("reco_mH", "MH") 

        if (self.isData != 1 and triggerType != "Reference"):
            self.analyzer.AddCorrection(
                Correction('TriggerSF_data','cpp_modules/Trigger_SF.cc',["raw_nano/trigger_1p1_SFs.json", self.year], corrtype='weight'), {"pt":"leadingFatJetPt", "mass":"MX", "uncert":'"data"'}
            ) 
            self.analyzer.AddCorrection(
                Correction('TriggerSF_MC','cpp_modules/Trigger_SF.cc',["raw_nano/trigger_1p1_SFs.json", self.year], corrtype='weight'), {"pt":"leadingFatJetPt", "mass":"MX", "uncert":'"MC"'}
            ) 
        if "Signal" in self.dataset:
            self.genXHY()
            self.check_matching_1p1()
            if do_tagger_corr == 1:
                self.Xbbtagging_corr("1p1", True) 
        #Making weight columns
        uncerts_to_corr = {}
        uncerts_to_corr["AK8_Xbbtagging"] = []
        WPs = ["L", "M", "T"]
        for wp in WPs:
            uncerts_to_corr["AK8_Xbbtagging"].append(f"AK8_Xbbtagging_wp{wp}")
        self.analyzer.MakeWeightCols(name = "All", uncerts_to_corr = uncerts_to_corr)
            








    #main selection function for mode 2p1
    def selection_2p1_BDT(self, JME_syst = "nom", region = "Signal", triggerType = "Hadron", massType = "regressedMass", top_fac = 0., do_tagger_corr = 1):
        #Skimming for 2p1
        self.analyzer.Cut("SkimCut", "SkimFlag == 2 || SkimFlag == 3")
        self.register_weight("SkimOf2p1")
        
        AutoNF(self.analyzer, self.year, self.isData) ###NO JERC correction, but should be fine since the effect is small
        self.register_weight("NoiseFilter")
        
        #Lepton veto
        self.analyzer.Define("nEle", "nElectrons(nElectron, Electron_cutBased, 0, Electron_pt,20, Electron_eta)")
        self.analyzer.Define("nMu", "nMuons(nMuon, Muon_looseId, Muon_pfIsoId, 0, Muon_pt, 20, Muon_eta)")
        self.analyzer.Cut("LeptonVetoCut", "nMu==0 && nEle==0")
        self.register_weight("LeptonVeto")
        
        AutoJetID.AutoJetID(self.analyzer, self.corr_year, ["Jet","FatJet"])
        #AutoJME.AutoJME(self.analyzer, ["Jet", "FatJet"], self.corr_year, self.data_era, True, AK8Calib_extras = ["regressedMass"])
        AutoJME.AutoJME(self.analyzer, ["Jet", "FatJet"], self.corr_year, self.data_era, True)
        self.analyzer.Define(f"FatJet_regressedMass_{JME_syst}", "getRawVal(nFatJet, FatJet_regressedMass, FatJet_rawFactor)")

        
        AutoJME.AutoJME_mSD(self.analyzer, self.corr_year, self.data_era)
        self.register_weight("JERCJetVeto")
        

        if not (self.isData == 1):
            AutoPU.AutoPU(self.analyzer, self.corr_year)
            genW    = Correction('genW',"cpp_modules/genW.cc",corrtype='corr')
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

        if "2024" in self.year:
            AK4_tagger = "Jet_btagUParTAK4B"
            AK4_tagger_corrName = "UParTAK4"
        else:
            AK4_tagger = "Jet_btagPNetB"
            AK4_tagger_corrName = "particleNet"
        ROOT.gInterpreter.Declare(f'TaggerDiscretizer AK4_Discretizer = TaggerDiscretizer("Jet",  "{self.corr_year}", "{AK4_tagger_corrName}_wp_values");') 
        self.analyzer.Define("Jet_tagger_discrete", f"AK4_Discretizer.eval({AK4_tagger})")


        
        
        #Triggers and Flags
        triggers = self.triggers[triggerType]
        print(triggers)
        triggerCut = self.analyzer.GetTriggerString(triggers)
        print(triggerCut)
        self.analyzer.Cut("TriggerCut", triggerCut)
        self.register_weight("TriggerCut")
        ROOT.gInterpreter.Declare(f'TaggerDiscretizer AK8_Discretizer = TaggerDiscretizer("FatJet",  "{self.corr_year}", "");')

        self.analyzer.Define("FatJet_goodness", f"goodJet(nFatJet, FatJet_jetId_corr, 2, FatJet_pt_{JME_syst}, 300,  FatJet_eta, 2.5)")

        
        #Looking for Higgs Jet
        if region == "Signal":
            self.analyzer.Define("idxJH", f"FindIdxJH(FatJet_{massType}_{JME_syst}, 100, 150, FatJet_goodness, 125)")
        elif region == "Validation":
            self.analyzer.Define("idxJH", f"FindIdxJH(FatJet_{massType}_{JME_syst}, 60, 100, FatJet_goodness, 80)")
        elif region == "AValidation":
            self.analyzer.Define("idxJH", f"FindIdxJH(FatJet_{massType}_{JME_syst}, 200, 250, FatJet_goodness, 225)")
        elif region == "Control":
            self.analyzer.Define("idxH_veto", f"FindIdxJH(FatJet_{massType}_{JME_syst}, 100, 150, FatJet_goodness, 125)")
            self.analyzer.Cut("HiggsVeto", "idxH_veto < 0")
            self.register_weight("HiggsVeto")
            self.analyzer.Define("idxJH", f"FindIdxJH(FatJet_{massType}_{JME_syst}, 150, 200, FatJet_goodness, 173)")
        self.analyzer.Cut("HiggsMassCut", f"idxJH >= 0")
        self.register_weight("HiggsMatch")

        
        self.analyzer.Define("MassHiggsCandidate", f"FatJet_msoftdrop_{JME_syst}[idxJH]")
        self.analyzer.Define("MassHiggsCandidate_regressed",f"FatJet_regressedMass_{JME_syst}[idxJH]")
        self.analyzer.Define("PtHiggsCandidate", f"FatJet_pt_{JME_syst}[idxJH]")
        self.analyzer.Define("EtaHiggsCandidate", "FatJet_eta[idxJH]")
        self.analyzer.Define("PhiHiggsCandidate", "FatJet_phi[idxJH]") 
        self.analyzer.Define("Tagger_PNetXbb_H", "FatJet_particleNet_XbbVsQCD[idxJH]")
        self.analyzer.Define("Tagger_Xbb_H", "FatJet_globalParT3_Xbb[idxJH]")
        self.analyzer.Define("Tagger_QCD_H", "FatJet_globalParT3_QCD[idxJH]")
        self.analyzer.Define("Tagger_TopbWqq_H", "FatJet_globalParT3_TopbWqq[idxJH]")
        self.analyzer.Define("Tagger_TopbWq_H", "FatJet_globalParT3_TopbWq[idxJH]")
        self.analyzer.Define("Tagger_H", f"Tagger_Xbb_H / (Tagger_Xbb_H + Tagger_QCD_H + {top_fac} * Tagger_TopbWqq_H)")
        self.analyzer.Define("Tagger_H_discrete", f"AK8_Discretizer.eval(Tagger_H)")
        self.analyzer.Define("Tagger_H_decapitated", f"AK8_Discretizer.decapitate(Tagger_H)")
        if  self.isData != 1 :
            self.analyzer.Define("TFlavor_H", f"classifyProbeJet(PhiHiggsCandidate, EtaHiggsCandidate, nGenPart, GenPart_phi,GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)")
        

        
        #Defining several regions depending on the B tagging score for the Y Jets
        self.analyzer.Define("Jet_goodness", f"goodJet(nJet, Jet_jetId_corr, 2, Jet_pt_{JME_syst}, 50,  Jet_eta, 2.5)")
        #Looking for Y Jets
        self.analyzer.Define("idxJY", f"FindIdxJY(Jet_eta, Jet_phi, FatJet_eta[idxJH], FatJet_phi[idxJH], {AK4_tagger}, 0.8, Jet_goodness)")
        self.analyzer.Cut("IdxJYCut", "idxJY.at(0) >= 0 && idxJY.at(1) >= 0")


        self.register_weight("JYMatch")
        #Defining a bunch of variables for later use
        self.analyzer.Define("idxJY0", "idxJY.at(0)")
        self.analyzer.Define("idxJY1", "idxJY.at(1)") 
        if (self.isData != 1): 
            self.analyzer.Define("hadronFlavorJY0", "Jet_hadronFlavour[idxJY0]")
            self.analyzer.Define("hadronFlavorJY1", "Jet_hadronFlavour[idxJY1]")
        self.analyzer.Define("PtJY0", f"Jet_pt_{JME_syst}[idxJY0]")
        self.analyzer.Define("PtJY1", f"Jet_pt_{JME_syst}[idxJY1]")
        self.analyzer.Define("EtaJY0", "Jet_eta[idxJY0]")
        self.analyzer.Define("EtaJY1", "Jet_eta[idxJY1]")
        self.analyzer.Define("PhiJY0", "Jet_phi[idxJY0]")
        self.analyzer.Define("PhiJY1", "Jet_phi[idxJY1]")
        self.analyzer.Define("MassJY0", f"Jet_mass_{JME_syst}[idxJY0]")
        self.analyzer.Define("MassJY1", f"Jet_mass_{JME_syst}[idxJY1]")
        self.analyzer.Define("Tagger_PNetb_Y0", "Jet_btagPNetB[idxJY0]")
        self.analyzer.Define("Tagger_PNetb_Y1", "Jet_btagPNetB[idxJY1]")
        self.analyzer.Define("Tagger_b_Y0", f"{AK4_tagger}[idxJY0]")
        self.analyzer.Define("Tagger_b_Y1", f"{AK4_tagger}[idxJY1]")
        self.analyzer.Define("Tagger_b_Ymin", "std::min(Tagger_b_Y0, Tagger_b_Y1)")
        self.analyzer.Define("Tagger_b_Ymax", "std::max(Tagger_b_Y0, Tagger_b_Y1)")
        self.analyzer.Define("Tagger_b_Y0_discrete", f"AK4_Discretizer.eval(Tagger_b_Y0)")
        self.analyzer.Define("Tagger_b_Y1_discrete", f"AK4_Discretizer.eval(Tagger_b_Y1)")
        self.analyzer.Define("Tagger_b_Ymin_discrete", f"AK4_Discretizer.eval(Tagger_b_Ymin)")
        self.analyzer.Define("Tagger_b_Ymax_discrete", f"AK4_Discretizer.eval(Tagger_b_Ymax)")
        self.analyzer.Define("Tagger_b_Y0_decapitated", f"AK4_Discretizer.decapitate(Tagger_b_Y0)")
        self.analyzer.Define("Tagger_b_Y1_decapitated", f"AK4_Discretizer.decapitate(Tagger_b_Y1)")
        self.analyzer.Define("Tagger_b_Ymin_decapitated", f"AK4_Discretizer.decapitate(Tagger_b_Ymin)")
        self.analyzer.Define("Tagger_b_Ymax_decapitated", f"AK4_Discretizer.decapitate(Tagger_b_Ymax)")




        #self.analyzer.Cut("YJetIDCut", "Jet_jetId_corr[idxJY0] >= 2 && Jet_jetId_corr[idxJY1] >= 2")
        #self.register_weight("YJetID")
        #self.analyzer.Cut("YPtCut", "PtJY0 >= 50 && PtJY0 >= 50")
        #self.register_weight("YPt")
        #self.analyzer.Cut("YEtaCut", "std::abs(EtaJY0) < 2.5 && std::abs(EtaJY1) < 2.5")
        #self.register_weight("YEta")
        #self.analyzer.Cut("JYPtCut", "PtJY0 > 100 && PtJY1 > 100")
        
        
        self.analyzer.Define("MassYCandidate", "InvMass_PtEtaPhiM({PtJY0, PtJY1}, {EtaJY0, EtaJY1}, {PhiJY0, PhiJY1}, {MassJY0, MassJY1} )" )
        self.analyzer.Define("MassJJH", "InvMass_PtEtaPhiM({PtHiggsCandidate, PtJY0, PtJY1}, {EtaHiggsCandidate, EtaJY0, EtaJY1}, {PhiHiggsCandidate, PhiJY0, PhiJY1}, {MassHiggsCandidate, MassJY0, MassJY1})")
        self.analyzer.Define("MassJJH_regressed", "InvMass_PtEtaPhiM({PtHiggsCandidate, PtJY0, PtJY1}, {EtaHiggsCandidate, EtaJY0, EtaJY1}, {PhiHiggsCandidate, PhiJY0, PhiJY1}, {MassHiggsCandidate_regressed, MassJY0, MassJY1})")

        #defining a few variables
        self.analyzer.Define("MX", "MassJJH")
        self.analyzer.Define("MY", "MassYCandidate")
        if massType == "regressedMass":
            self.analyzer.Define("MH", "MassHiggsCandidate_regressed")
        elif massType == "msoftdrop": 
            self.analyzer.Define("MH", "MassHiggsCandidate")
        self.analyzer.Define("reco_mY", "MY") 
        self.analyzer.Define("reco_mX", "MX") 
        self.analyzer.Define("reco_mH", "MH") 

        self.analyzer.Define("leadingFatJetPt", f"FatJet_pt_{JME_syst}.at(0)")
        self.analyzer.Define("leadingFatJetPhi", "FatJet_phi.at(0)")
        self.analyzer.Define("leadingFatJetEta", "FatJet_eta.at(0)")
        self.analyzer.Define("leadingFatJetMsoftdrop", f"FatJet_msoftdrop_{JME_syst}.at(0)")
        #Making weight columns
        if (self.isData != 1 and triggerType != "Reference"):
            self.analyzer.AddCorrection(
                Correction('TriggerSF_data','cpp_modules/Trigger_SF.cc',["raw_nano/trigger_2p1_SFs.json", self.year], corrtype='weight'), {"pt":"leadingFatJetPt", "mass":"MX", "uncert":'"data"'}
            ) 
            self.analyzer.AddCorrection(
                Correction('TriggerSF_MC','cpp_modules/Trigger_SF.cc',["raw_nano/trigger_2p1_SFs.json", self.year], corrtype='weight'), {"pt":"leadingFatJetPt", "mass":"MX", "uncert":'"MC"'}
            )
        if "Signal" in self.dataset:
            self.genXHY()
            self.check_matching_2p1()
            if do_tagger_corr == 1:
                self.btagging_corr(JME_syst, True) 
                self.Xbbtagging_corr("2p1", True)
        #Making weight columns
        uncerts_to_corr={"AK4_btagging_light_correlated" : ["AK4_btagging_light_uncorrelated"], "AK4_btagging_heavy_correlated" : ["AK4_btagging_heavy_uncorrelated"]}
        WPs = ["L", "M", "T", "XT", "XXT"]
        for wp in WPs:
            uncerts_to_corr["AK4_btagging_light_correlated"].append(f"AK4_btagging_light_correlated_wp{wp}")
            uncerts_to_corr["AK4_btagging_light_correlated"].append(f"AK4_btagging_light_uncorrelated_wp{wp}")
            uncerts_to_corr["AK4_btagging_heavy_correlated"].append(f"AK4_btagging_heavy_correlated_wp{wp}")
            uncerts_to_corr["AK4_btagging_heavy_correlated"].append(f"AK4_btagging_heavy_uncorrelated_wp{wp}")
        WPs = ["L", "M", "T"]
        uncerts_to_corr["AK8_Xbbtagging"] = []
        for wp in WPs:
            uncerts_to_corr["AK8_Xbbtagging"].append(f"AK8_Xbbtagging_wp{wp}")
            
        self.analyzer.MakeWeightCols(name = "All", uncerts_to_corr = uncerts_to_corr)
        
        print(f"DEBUG: { self.analyzer.GetActiveNode().DataFrame.Count().GetValue()}") 



    def selection_combined_BDT(self, JME_syst = "nom", region = "Signal", massType = "regressedMass", triggerType = "Hadron", top_fac = 0.):
        if self.isData: 
            All_JME_systs = ["nom"]
        else:
            All_JME_systs = ["nom", "JES__up", "JES__down", "JER__up", "JER__down"]
        AutoNF(self.analyzer, self.year, self.isData) ###NO JERC correction, but should be fine since the effect is small
        self.register_weight("NoiseFilter")
        
        #Lepton veto
        self.analyzer.Define("nEle", "nElectrons(nElectron, Electron_cutBased, 0, Electron_pt,20, Electron_eta)")
        self.analyzer.Define("nMu", "nMuons(nMuon, Muon_looseId, Muon_pfIsoId, 0, Muon_pt, 20, Muon_eta)")
        self.analyzer.Cut("LeptonVetoCut", "nMu==0 && nEle==0")
        self.register_weight("LeptonVeto")
        
        AutoJetID.AutoJetID(self.analyzer, self.corr_year, ["Jet","FatJet"])
        #AutoJME.AutoJME(self.analyzer, ["Jet", "FatJet"], self.corr_year, self.data_era, True, AK8Calib_extras = ["regressedMass"])
        AutoJME.AutoJME(self.analyzer, ["Jet", "FatJet"], self.corr_year, self.data_era, True)
        for _syst in All_JME_systs:
            self.analyzer.Define(f"FatJet_regressedMass_{_syst}", "getRawVal(nFatJet, FatJet_regressedMass, FatJet_rawFactor)")
        
        AutoJME.AutoJME_mSD(self.analyzer, self.corr_year, self.data_era)
        self.register_weight("JERCJetVeto")
        

        if not (self.isData == 1):
            AutoPU.AutoPU(self.analyzer, self.corr_year)
            genW    = Correction('genW',"cpp_modules/genW.cc",corrtype='corr')
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
 
        #Triggers and Flags
        triggers = self.triggers[triggerType]
        print(triggers)
        triggerCut = self.analyzer.GetTriggerString(triggers)
        print(triggerCut)
        self.analyzer.Cut("TriggerCut", triggerCut)
        self.register_weight("TriggerCut")

        

        if "2024" in self.year:
            AK4_tagger = "Jet_btagUParTAK4B"
            AK4_tagger_corrName = "UParTAK4"
        else:
            AK4_tagger = "Jet_btagPNetB"
            AK4_tagger_corrName = "particleNet"
       
        ROOT.gInterpreter.Declare(f'TaggerDiscretizer AK8_Discretizer = TaggerDiscretizer("FatJet",  "{self.corr_year}", "");')


        ROOT.gInterpreter.Declare(f'TaggerDiscretizer AK4_Discretizer = TaggerDiscretizer("Jet",  "{self.corr_year}", "{AK4_tagger_corrName}_wp_values");') 
        self.analyzer.Define("Jet_tagger_discrete", f"AK4_Discretizer.eval({AK4_tagger})")
        #####################################################################################################################
        #Skimming
        self.analyzer.Define("flag1p1_SkimCut", "SkimFlag == 1 || SkimFlag == 3")
        self.analyzer.Define("flag2p1_SkimCut", "SkimFlag == 2 || SkimFlag == 3")


        self.analyzer.Define("val1p1_FatJet_goodness", f"goodJet(nFatJet, FatJet_jetId_corr, 2, FatJet_pt_{JME_syst}, 450,  FatJet_eta, 2.5)") 
        self.analyzer.Define("val2p1_FatJet_goodness", f"goodJet(nFatJet, FatJet_jetId_corr, 2, FatJet_pt_{JME_syst}, 300,  FatJet_eta, 2.5)") 
        self.analyzer.Define("val2p1_Jet_goodness", f"goodJet(nJet, Jet_jetId_corr, 2, Jet_pt_{JME_syst}, 50,  Jet_eta, 2.5)")
        ##############################################################################################################
        #Higgs Match
        if region == "Signal":
            self.analyzer.Define("val1p1_idxH_try", f"flag1p1_SkimCut == 0? 0 : FindIdxJH_random(FatJet_{massType}_{JME_syst}, 100, 150, 2, val1p1_FatJet_goodness)")
        elif region == "Validation":
            self.analyzer.Define("val1p1_idxH_try", f"flag1p1_SkimCut == 0? 0 : FindIdxJH_random(FatJet_{massType}_{JME_syst}, 60, 100, 2, val1p1_FatJet_goodness)")
        elif region == "AValidation":
            self.analyzer.Define("val1p1_idxH_try", f"flag1p1_SkimCut == 0? 0 : FindIdxJH_random(FatJet_{massType}_{JME_syst}, 200, 250, 2, val1p1_FatJet_goodness)")
        elif region == "Control":
            self.analyzer.Define("val1p1_idxH_veto", f"flag1p1_SkimCut == 0? 0 : FindIdxJH(FatJet_{massType}_{JME_syst}, 100, 150, val1p1_FatJet_goodness, 125)")
            self.analyzer.Define("flag1p1_HiggsVeto", "flag1p1_SkimCut == 0? false : val1p1_idxH_veto < 0")
            self.analyzer.Define("val1p1_idxH_try", f"flag1p1_SkimCut == 0? 0 : FindIdxJH_random(FatJet_{massType}_{JME_syst}, 150, 200, 2, val1p1_FatJet_goodness)")
        self.analyzer.Define("val1p1_idxY_try", "flag1p1_SkimCut == 0? -1 : FindIdxJY(val1p1_FatJet_goodness, val1p1_idxH_try)")
        self.analyzer.Define("flag1p1_IdxJYCut", "flag1p1_SkimCut == 0? false : val1p1_idxY_try >= 0")
        self.analyzer.Define("flag1p1_IdxJHCut", "flag1p1_SkimCut == 0? false : val1p1_idxH_try >= 0")
        #############################################################################################################
        if region == "Signal":
            self.analyzer.Define("val2p1_idxH_try", f"flag2p1_SkimCut == 0? 0 : FindIdxJH(FatJet_{massType}_{JME_syst}, 100, 150, val2p1_FatJet_goodness, 125)")
        elif region == "Validation":
            self.analyzer.Define("val2p1_idxH_try", f"flag2p1_SkimCut == 0? 0 : FindIdxJH(FatJet_{massType}_{JME_syst}, 60, 100, val2p1_FatJet_goodness, 80)")
        elif region == "AValidation":
            self.analyzer.Define("val2p1_idxH_try", f"flag2p1_SkimCut == 0? 0 : FindIdxJH(FatJet_{massType}_{JME_syst}, 200, 250, val2p1_FatJet_goodness, 225)")
        elif region == "Control":
            self.analyzer.Define("val2p1_idxH_veto", f"flag2p1_SkimCut == 0? 0 : FindIdxJH(FatJet_{massType}_{JME_syst}, 100, 150, val2p1_FatJet_goodness, 125)")
            self.analyzer.Define("flag2p1_HiggsVeto", "flag2p1_SkimCut == 0? false : val2p1_idxH_veto < 0")
            self.analyzer.Define("val2p1_idxH_try", f"flag2p1_SkimCut == 0? 0 : FindIdxJH(FatJet_{massType}_{JME_syst}, 150, 200, val2p1_FatJet_goodness, 173)")
        #Looking for Y Jets
        self.analyzer.Define("val2p1_idxY_try", f"flag2p1_SkimCut == 0? RVec<int>{0, 1} : FindIdxJY(Jet_eta, Jet_phi, FatJet_eta[max(0, val2p1_idxH_try)], FatJet_phi[max(0, val2p1_idxH_try)], {AK4_tagger}, 0.8, val2p1_Jet_goodness)")
        self.analyzer.Define("flag2p1_IdxJYCut", "flag2p1_SkimCut == 0? false : val2p1_idxY_try.at(0) >= 0 && val2p1_idxY_try.at(1) >= 0")
        self.analyzer.Define("flag2p1_IdxJHCut", f"flag2p1_SkimCut == 0? false : val2p1_idxH_try >= 0")
        ################################################################################################################
        
        self.analyzer.Cut("YHCut", "(flag2p1_IdxJYCut && flag2p1_IdxJHCut) || (flag1p1_IdxJYCut && flag1p1_IdxJHCut)") 
        self.register_weight("HiggsYMatch")
        self.analyzer.Define("val1p1_idxH", "max(val1p1_idxH_try, 0)")
        self.analyzer.Define("val1p1_idxY", "max(val1p1_idxY_try, 0)")
        self.analyzer.Define("val2p1_idxH", "max(val2p1_idxH_try, 0)")
        self.analyzer.Define("val2p1_idxY", "RVec<int>{max(val2p1_idxY_try.at(0), 0), max(val2p1_idxY_try.at(1), 0)}")
        ########################################################################################################################

        self.analyzer.Define("val1p1_Delta_Eta", "flag1p1_SkimCut == 0? 0.f : abs(FatJet_eta.at(val1p1_idxH) - FatJet_eta.at(val1p1_idxY))")
        self.analyzer.Define("val1p1_Delta_Y", f"flag1p1_SkimCut == 0? 0.f : abs(DeltaRapidity(FatJet_pt_{JME_syst}.at(val1p1_idxH),FatJet_eta.at(val1p1_idxH), FatJet_phi.at(val1p1_idxH), FatJet_{massType}_{JME_syst}.at(val1p1_idxH), FatJet_pt_{JME_syst}.at(val1p1_idxY),FatJet_eta.at(val1p1_idxY), FatJet_phi.at(val1p1_idxY), FatJet_{massType}_{JME_syst}.at(val1p1_idxY)))")
    
        #Defining a bunch of variables for later use
        self.analyzer.Define("val1p1_MassHiggsCandidate",f"flag1p1_SkimCut == 0? 0.f : FatJet_msoftdrop_{JME_syst}[val1p1_idxH]")
        self.analyzer.Define("val1p1_MassHiggsCandidate_regressed",f"flag1p1_SkimCut == 0? 0.f : FatJet_regressedMass_{JME_syst}[val1p1_idxH]")
        self.analyzer.Define("val1p1_PtHiggsCandidate", f"flag1p1_SkimCut == 0? 0.f : FatJet_pt_{JME_syst}[val1p1_idxH]")
        self.analyzer.Define("val1p1_EtaHiggsCandidate", "flag1p1_SkimCut == 0? 0.f : FatJet_eta[val1p1_idxH]")
        self.analyzer.Define("val1p1_PhiHiggsCandidate", "flag1p1_SkimCut == 0? 0.f : FatJet_phi[val1p1_idxH]")
    
        self.analyzer.Define("val1p1_Tagger_PNetXbb_H", "flag1p1_SkimCut == 0? 0.f : FatJet_particleNet_XbbVsQCD[val1p1_idxH]")
        self.analyzer.Define("val1p1_Tagger_Xbb_H", "flag1p1_SkimCut == 0? 0.f : FatJet_globalParT3_Xbb[val1p1_idxH]")
        self.analyzer.Define("val1p1_Tagger_QCD_H", "flag1p1_SkimCut == 0? 0.f : FatJet_globalParT3_QCD[val1p1_idxH]")
        self.analyzer.Define("val1p1_Tagger_TopbWqq_H", "flag1p1_SkimCut == 0? 0.f : FatJet_globalParT3_TopbWqq[val1p1_idxH]")
        self.analyzer.Define("val1p1_Tagger_TopbWq_H", "flag1p1_SkimCut == 0? 0.f : FatJet_globalParT3_TopbWq[val1p1_idxH]")
        self.analyzer.Define("val1p1_Tagger_H", f"flag1p1_SkimCut == 0? 0.f : val1p1_Tagger_Xbb_H / (val1p1_Tagger_Xbb_H + val1p1_Tagger_QCD_H + {top_fac} * val1p1_Tagger_TopbWqq_H)")
        self.analyzer.Define("val1p1_Tagger_H_discrete", f"flag1p1_SkimCut == 0? 0 : AK8_Discretizer.eval(val1p1_Tagger_H)")
        self.analyzer.Define("val1p1_Tagger_H_decapitated", f"flag1p1_SkimCut == 0? 0.f : AK8_Discretizer.decapitate(val1p1_Tagger_H)")
        
        self.analyzer.Define("val1p1_MassYCandidate", f"flag1p1_SkimCut == 0? 0.f : FatJet_msoftdrop_{JME_syst}[val1p1_idxY]")
        self.analyzer.Define("val1p1_MassYCandidate_regressed",f"flag1p1_SkimCut == 0? 0.f : FatJet_regressedMass_{JME_syst}[val1p1_idxY]")
        self.analyzer.Define("val1p1_PtYCandidate", f"flag1p1_SkimCut == 0? 0.f : FatJet_pt_{JME_syst}[val1p1_idxY]")
        self.analyzer.Define("val1p1_EtaYCandidate", "flag1p1_SkimCut == 0? 0.f : FatJet_eta[val1p1_idxY]")
        self.analyzer.Define("val1p1_PhiYCandidate", "flag1p1_SkimCut == 0? 0.f : FatJet_phi[val1p1_idxY]")



        self.analyzer.Define("val1p1_Tagger_PNetXbb_Y", "flag1p1_SkimCut == 0? 0.f : FatJet_particleNet_XbbVsQCD[val1p1_idxY]")
        self.analyzer.Define("val1p1_Tagger_Xbb_Y", "flag1p1_SkimCut == 0? 0.f : FatJet_globalParT3_Xbb[val1p1_idxY]")
        self.analyzer.Define("val1p1_Tagger_QCD_Y", "flag1p1_SkimCut == 0? 0.f : FatJet_globalParT3_QCD[val1p1_idxY]")
        self.analyzer.Define("val1p1_Tagger_TopbWqq_Y", "flag1p1_SkimCut == 0? 0.f : FatJet_globalParT3_TopbWqq[val1p1_idxY]")
        self.analyzer.Define("val1p1_Tagger_TopbWq_Y", "flag1p1_SkimCut == 0? 0.f : FatJet_globalParT3_TopbWq[val1p1_idxY]")
        self.analyzer.Define("val1p1_Tagger_Y", f"flag1p1_SkimCut == 0? 0.f : val1p1_Tagger_Xbb_Y / (val1p1_Tagger_Xbb_Y + val1p1_Tagger_QCD_Y + {top_fac} * val1p1_Tagger_TopbWqq_Y)")
        self.analyzer.Define("val1p1_Tagger_Y_discrete", f"flag1p1_SkimCut == 0? 0 : AK8_Discretizer.eval(val1p1_Tagger_Y)")
        self.analyzer.Define("val1p1_Tagger_Y_decapitated", f"flag1p1_SkimCut == 0? 0.f : AK8_Discretizer.decapitate(val1p1_Tagger_Y)")
        if  self.isData != 1:
            self.analyzer.Define("val1p1_TFlavor_Y", f"flag1p1_SkimCut == 0? 0 : classifyProbeJet(val1p1_PhiYCandidate, val1p1_EtaYCandidate, nGenPart, GenPart_phi,GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)")
            self.analyzer.Define("val1p1_TFlavor_H", f"flag1p1_SkimCut == 0? 0 : classifyProbeJet(val1p1_PhiHiggsCandidate, val1p1_EtaHiggsCandidate, nGenPart, GenPart_phi,GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)")
        
        #X(JJ) Mass
        self.analyzer.Define(f"val1p1_MassLeadingTwoFatJets", "flag1p1_SkimCut == 0? 0.f : InvMass_PtEtaPhiM({val1p1_PtHiggsCandidate, val1p1_PtYCandidate}, {val1p1_EtaHiggsCandidate, val1p1_EtaYCandidate}, {val1p1_PhiHiggsCandidate, val1p1_PhiYCandidate}, {val1p1_MassHiggsCandidate, val1p1_MassYCandidate})")
        self.analyzer.Define(f"val1p1_MassLeadingTwoFatJets_regressed", "flag1p1_SkimCut == 0? 0.f : InvMass_PtEtaPhiM({val1p1_PtHiggsCandidate, val1p1_PtYCandidate}, {val1p1_EtaHiggsCandidate, val1p1_EtaYCandidate}, {val1p1_PhiHiggsCandidate, val1p1_PhiYCandidate}, {val1p1_MassHiggsCandidate_regressed, val1p1_MassYCandidate})")
        self.analyzer.Define(f"val1p1_MassLeadingTwoFatJets_regressed_regressed", "flag1p1_SkimCut == 0? 0.f : InvMass_PtEtaPhiM({val1p1_PtHiggsCandidate, val1p1_PtYCandidate}, {val1p1_EtaHiggsCandidate, val1p1_EtaYCandidate}, {val1p1_PhiHiggsCandidate, val1p1_PhiYCandidate}, {val1p1_MassHiggsCandidate_regressed, val1p1_MassYCandidate_regressed})")

        self.analyzer.Define("val1p1_MX", "flag1p1_SkimCut == 0? 0.f : val1p1_MassLeadingTwoFatJets")
        self.analyzer.Define("val1p1_MY", "flag1p1_SkimCut == 0? 0.f : val1p1_MassYCandidate")
        if massType == "regressedMass": 
            self.analyzer.Define("val1p1_MH", "flag1p1_SkimCut == 0? 0.f : val1p1_MassHiggsCandidate_regressed")
        elif massType == "msoftdrop":
            self.analyzer.Define("val1p1_MH", "flag1p1_SkimCut == 0? 0.f : val1p1_MassHiggsCandidate")
        self.analyzer.Define("val1p1_reco_mY", "flag1p1_SkimCut == 0? 0.f : val1p1_MY") 
        self.analyzer.Define("val1p1_reco_mX", "flag1p1_SkimCut == 0? 0.f : val1p1_MX") 
        self.analyzer.Define("val1p1_reco_mH", "flag1p1_SkimCut == 0? 0.f : val1p1_MH") 
        



        for _syst in All_JME_systs:
            self.analyzer.Define(f"val1p1_MassYCandidate_{_syst}", f"flag1p1_SkimCut == 0? 0.f : FatJet_msoftdrop_{_syst}[val1p1_idxY]")
            self.analyzer.Define(f"val1p1_MassYCandidate_regressed_{_syst}",f"flag1p1_SkimCut == 0? 0.f : FatJet_regressedMass_{_syst}[val1p1_idxY]")
            self.analyzer.Define(f"val1p1_PtYCandidate_{_syst}", f"flag1p1_SkimCut == 0? 0.f : FatJet_pt_{_syst}[val1p1_idxY]")

            self.analyzer.Define(f"val1p1_MassHiggsCandidate_{_syst}",f"flag1p1_SkimCut == 0? 0.f : FatJet_msoftdrop_{_syst}[val1p1_idxH]")
            self.analyzer.Define(f"val1p1_MassHiggsCandidate_regressed_{_syst}",f"flag1p1_SkimCut == 0? 0.f : FatJet_regressedMass_{_syst}[val1p1_idxH]")
            self.analyzer.Define(f"val1p1_PtHiggsCandidate_{_syst}", f"flag1p1_SkimCut == 0? 0.f : FatJet_pt_{_syst}[val1p1_idxH]")
            
            self.analyzer.Define(f"val1p1_MY_{_syst}", f"flag1p1_SkimCut == 0? 0.f : val1p1_MassYCandidate_{_syst}")
            self.analyzer.Define(f"val1p1_MX_{_syst}", f"flag1p1_SkimCut == 0? 0.f : flag1p1_SkimCut == 0? 0.f : InvMass_PtEtaPhiM({{val1p1_PtHiggsCandidate_{_syst}, val1p1_PtYCandidate_{_syst} }}, {{val1p1_EtaHiggsCandidate, val1p1_EtaYCandidate}}, {{val1p1_PhiHiggsCandidate, val1p1_PhiYCandidate}}, {{val1p1_MassHiggsCandidate_{_syst}, val1p1_MassYCandidate_{_syst} }})")





        
    #######################################################################################################################
    ######################### 2p1 ##################################33
    ###########################################################################################
        self.analyzer.Define("val2p1_MassHiggsCandidate", f"flag2p1_SkimCut == 0? 0.f : FatJet_msoftdrop_{JME_syst}[val2p1_idxH]")
        self.analyzer.Define("val2p1_MassHiggsCandidate_regressed",f"flag2p1_SkimCut == 0? 0.f : FatJet_regressedMass_{JME_syst}[val2p1_idxH]")
        self.analyzer.Define("val2p1_PtHiggsCandidate", f"flag2p1_SkimCut == 0? 0.f : FatJet_pt_{JME_syst}[val2p1_idxH]")
        self.analyzer.Define("val2p1_EtaHiggsCandidate", "flag2p1_SkimCut == 0? 0.f : FatJet_eta[val2p1_idxH]")
        self.analyzer.Define("val2p1_PhiHiggsCandidate", "flag2p1_SkimCut == 0? 0.f : FatJet_phi[val2p1_idxH]") 
        self.analyzer.Define("val2p1_Tagger_PNetXbb_H", "flag2p1_SkimCut == 0? 0.f : FatJet_particleNet_XbbVsQCD[val2p1_idxH]")
        self.analyzer.Define("val2p1_Tagger_Xbb_H", "flag2p1_SkimCut == 0? 0.f : FatJet_globalParT3_Xbb[val2p1_idxH]")
        self.analyzer.Define("val2p1_Tagger_QCD_H", "flag2p1_SkimCut == 0? 0.f : FatJet_globalParT3_QCD[val2p1_idxH]")
        self.analyzer.Define("val2p1_Tagger_TopbWqq_H", "flag2p1_SkimCut == 0? 0.f : FatJet_globalParT3_TopbWqq[val2p1_idxH]")
        self.analyzer.Define("val2p1_Tagger_TopbWq_H", "flag2p1_SkimCut == 0? 0.f : FatJet_globalParT3_TopbWq[val2p1_idxH]")
        self.analyzer.Define("val2p1_Tagger_H", f"flag2p1_SkimCut == 0? 0.f : val2p1_Tagger_Xbb_H / (val2p1_Tagger_Xbb_H + val2p1_Tagger_QCD_H + {top_fac} * val2p1_Tagger_TopbWqq_H)")
        self.analyzer.Define("val2p1_Tagger_H_discrete", f"flag2p1_SkimCut == 0? 0 : AK8_Discretizer.eval(val2p1_Tagger_H)")
        self.analyzer.Define("val2p1_Tagger_H_decapitated", f"flag2p1_SkimCut == 0? 0.f : AK8_Discretizer.decapitate(val2p1_Tagger_H)")
        if  self.isData != 1 :
            self.analyzer.Define("val2p1_TFlavor_H", f"flag2p1_SkimCut == 0? 0 : classifyProbeJet(val2p1_PhiHiggsCandidate, val2p1_EtaHiggsCandidate, nGenPart, GenPart_phi,GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)")
        


        #Defining a bunch of variables for later use
        self.analyzer.Define("val2p1_idxY0", "flag2p1_SkimCut == 0? 0 : val2p1_idxY.at(0)")
        self.analyzer.Define("val2p1_idxY1", "flag2p1_SkimCut == 0? 0 : val2p1_idxY.at(1)") 
        if (self.isData != 1): 
            self.analyzer.Define("val2p1_hadronFlavorJY0", "flag2p1_SkimCut == 0? 0 : Jet_hadronFlavour[val2p1_idxY0]")
            self.analyzer.Define("val2p1_hadronFlavorJY1", "flag2p1_SkimCut == 0? 0 : Jet_hadronFlavour[val2p1_idxY1]")
        self.analyzer.Define("val2p1_PtJY0", f"flag2p1_SkimCut == 0? 0.f : Jet_pt_{JME_syst}[val2p1_idxY0]")
        self.analyzer.Define("val2p1_PtJY1", f"flag2p1_SkimCut == 0? 0.f : Jet_pt_{JME_syst}[val2p1_idxY1]")
        self.analyzer.Define("val2p1_EtaJY0", "flag2p1_SkimCut == 0? 0.f : Jet_eta[val2p1_idxY0]")
        self.analyzer.Define("val2p1_EtaJY1", "flag2p1_SkimCut == 0? 0.f : Jet_eta[val2p1_idxY1]")
        self.analyzer.Define("val2p1_PhiJY0", "flag2p1_SkimCut == 0? 0.f : Jet_phi[val2p1_idxY0]")
        self.analyzer.Define("val2p1_PhiJY1", "flag2p1_SkimCut == 0? 0.f : Jet_phi[val2p1_idxY1]")
        self.analyzer.Define("val2p1_MassJY0", f"flag2p1_SkimCut == 0? 0.f : Jet_mass_{JME_syst}[val2p1_idxY0]")
        self.analyzer.Define("val2p1_MassJY1", f"flag2p1_SkimCut == 0? 0.f : Jet_mass_{JME_syst}[val2p1_idxY1]")
        self.analyzer.Define("val2p1_Tagger_PNetb_Y0", "flag2p1_SkimCut == 0? 0.f : Jet_btagPNetB[val2p1_idxY0]")
        self.analyzer.Define("val2p1_Tagger_PNetb_Y1", "flag2p1_SkimCut == 0? 0.f : Jet_btagPNetB[val2p1_idxY1]")
        self.analyzer.Define("val2p1_Tagger_b_Y0", f"flag2p1_SkimCut == 0? 0.f : {AK4_tagger}[val2p1_idxY0]")
        self.analyzer.Define("val2p1_Tagger_b_Y1", f"flag2p1_SkimCut == 0? 0.f : {AK4_tagger}[val2p1_idxY1]")
        self.analyzer.Define("val2p1_Tagger_b_Ymin", "flag2p1_SkimCut == 0? 0.f : std::min(val2p1_Tagger_b_Y0, val2p1_Tagger_b_Y1)")
        self.analyzer.Define("val2p1_Tagger_b_Ymax", "flag2p1_SkimCut == 0? 0.f : std::max(val2p1_Tagger_b_Y0, val2p1_Tagger_b_Y1)")
        self.analyzer.Define("val2p1_Tagger_b_Y0_discrete", f"flag2p1_SkimCut == 0? 0 : AK4_Discretizer.eval(val2p1_Tagger_b_Y0)")
        self.analyzer.Define("val2p1_Tagger_b_Y1_discrete", f"flag2p1_SkimCut == 0? 0 : AK4_Discretizer.eval(val2p1_Tagger_b_Y1)")
        self.analyzer.Define("val2p1_Tagger_b_Ymin_discrete", f"flag2p1_SkimCut == 0? 0 : AK4_Discretizer.eval(val2p1_Tagger_b_Ymin)")
        self.analyzer.Define("val2p1_Tagger_b_Ymax_discrete", f"flag2p1_SkimCut == 0? 0 : AK4_Discretizer.eval(val2p1_Tagger_b_Ymax)")
        self.analyzer.Define("val2p1_Tagger_b_Y0_decapitated", f"flag2p1_SkimCut == 0? 0.f : AK4_Discretizer.decapitate(val2p1_Tagger_b_Y0)")
        self.analyzer.Define("val2p1_Tagger_b_Y1_decapitated", f"flag2p1_SkimCut == 0? 0.f : AK4_Discretizer.decapitate(val2p1_Tagger_b_Y1)")
        self.analyzer.Define("val2p1_Tagger_b_Ymin_decapitated", f"flag2p1_SkimCut == 0? 0.f : AK4_Discretizer.decapitate(val2p1_Tagger_b_Ymin)")
        self.analyzer.Define("val2p1_Tagger_b_Ymax_decapitated", f"flag2p1_SkimCut == 0? 0.f : AK4_Discretizer.decapitate(val2p1_Tagger_b_Ymax)")

        
        self.analyzer.Define("val2p1_MassYCandidate", "flag2p1_SkimCut == 0? 0.f : InvMass_PtEtaPhiM({val2p1_PtJY0, val2p1_PtJY1}, {val2p1_EtaJY0, val2p1_EtaJY1}, {val2p1_PhiJY0, val2p1_PhiJY1}, {val2p1_MassJY0, val2p1_MassJY1} )" )
        self.analyzer.Define("val2p1_MassJJH", "flag2p1_SkimCut == 0? 0.f : InvMass_PtEtaPhiM({val2p1_PtHiggsCandidate, val2p1_PtJY0, val2p1_PtJY1}, {val2p1_EtaHiggsCandidate, val2p1_EtaJY0, val2p1_EtaJY1}, {val2p1_PhiHiggsCandidate, val2p1_PhiJY0, val2p1_PhiJY1}, {val2p1_MassHiggsCandidate, val2p1_MassJY0, val2p1_MassJY1})")
        self.analyzer.Define("val2p1_MassJJH_regressed", "flag2p1_SkimCut == 0? 0.f : InvMass_PtEtaPhiM({val2p1_PtHiggsCandidate, val2p1_PtJY0, val2p1_PtJY1}, {val2p1_EtaHiggsCandidate, val2p1_EtaJY0, val2p1_EtaJY1}, {val2p1_PhiHiggsCandidate, val2p1_PhiJY0, val2p1_PhiJY1}, {val2p1_MassHiggsCandidate_regressed, val2p1_MassJY0, val2p1_MassJY1})")

        #defining a few variables
        self.analyzer.Define("val2p1_MY", "flag2p1_SkimCut == 0? 0.f : val2p1_MassYCandidate")
        self.analyzer.Define("val2p1_MX", "flag2p1_SkimCut == 0? 0.f : val2p1_MassJJH")
        if massType == "regressedMass":
            self.analyzer.Define("val2p1_MH", "flag2p1_SkimCut == 0? 0.f : val2p1_MassHiggsCandidate_regressed")
        elif massType == "msoftdrop": 
            self.analyzer.Define("val2p1_MH", "flag2p1_SkimCut == 0? 0.f : val2p1_MassHiggsCandidate")
        self.analyzer.Define("val2p1_reco_mY", "flag2p1_SkimCut == 0? 0.f : val2p1_MY") 
        self.analyzer.Define("val2p1_reco_mX", "flag2p1_SkimCut == 0? 0.f : val2p1_MX") 
        self.analyzer.Define("val2p1_reco_mH", "flag2p1_SkimCut == 0? 0.f : val2p1_MH") 


        for _syst in All_JME_systs:
            self.analyzer.Define(f"val2p1_PtJY0_{_syst}", f"flag2p1_SkimCut == 0? 0.f : Jet_pt_{_syst}[val2p1_idxY0]")
            self.analyzer.Define(f"val2p1_PtJY1_{_syst}", f"flag2p1_SkimCut == 0? 0.f : Jet_pt_{_syst}[val2p1_idxY1]")
            self.analyzer.Define(f"val2p1_MassJY0_{_syst}", f"flag2p1_SkimCut == 0? 0.f : Jet_mass_{_syst}[val2p1_idxY0]")
            self.analyzer.Define(f"val2p1_MassJY1_{_syst}", f"flag2p1_SkimCut == 0? 0.f : Jet_mass_{_syst}[val2p1_idxY1]")
            self.analyzer.Define(f"val2p1_MassHiggsCandidate_{_syst}", f"flag2p1_SkimCut == 0? 0.f : FatJet_msoftdrop_{_syst}[val2p1_idxH]")
            self.analyzer.Define(f"val2p1_MassHiggsCandidate_regressed_{_syst}",f"flag2p1_SkimCut == 0? 0.f : FatJet_regressedMass_{_syst}[val2p1_idxH]")
            self.analyzer.Define(f"val2p1_PtHiggsCandidate_{_syst}", f"flag2p1_SkimCut == 0? 0.f : FatJet_pt_{_syst}[val2p1_idxH]")
            self.analyzer.Define(f"val2p1_MY_{_syst}", f"flag2p1_SkimCut == 0? 0.f : InvMass_PtEtaPhiM({{val2p1_PtJY0_{_syst}, val2p1_PtJY1_{_syst} }}, {{val2p1_EtaJY0, val2p1_EtaJY1}}, {{val2p1_PhiJY0, val2p1_PhiJY1}}, {{val2p1_MassJY0_{_syst}, val2p1_MassJY1_{_syst} }} )" )
            self.analyzer.Define(f"val2p1_MX_{_syst}", f"flag2p1_SkimCut == 0? 0.f : InvMass_PtEtaPhiM({{val2p1_PtHiggsCandidate_{_syst}, val2p1_PtJY0_{_syst}, val2p1_PtJY1_{_syst} }}, {{val2p1_EtaHiggsCandidate, val2p1_EtaJY0, val2p1_EtaJY1}}, {{val2p1_PhiHiggsCandidate, val2p1_PhiJY0, val2p1_PhiJY1}}, {{val2p1_MassHiggsCandidate_{_syst}, val2p1_MassJY0_{_syst}, val2p1_MassJY1_{_syst} }})")
            
    ##################################################################################################################
   



        self.analyzer.Define("flag1p1_MJJCut", "flag1p1_SkimCut == 0? false : val1p1_MX > 200 ")
        self.analyzer.Define("flag1p1_MJYCut", "flag1p1_SkimCut == 0? false : val1p1_MY > 40")
        self.analyzer.Define("flag1p1_Tagger_H_min", "flag1p1_SkimCut == 0? false : val1p1_Tagger_H >= 0.1")
        self.analyzer.Define("flag1p1_Tagger_Y_min", "flag1p1_SkimCut == 0? false : val1p1_Tagger_Y >= 0.1")

        self.analyzer.Define("flag2p1_MJJCut", "flag2p1_SkimCut == 0? false : val2p1_MX > 200")
        self.analyzer.Define("flag2p1_MJYCut", "flag2p1_SkimCut == 0? false : val2p1_MY > 200")
        self.analyzer.Define("flag2p1_Tagger_H_min", "flag2p1_SkimCut == 0? false : val2p1_Tagger_H >= 0.1")
        self.analyzer.Define("flag2p1_Tagger_b_Ymin", "flag2p1_SkimCut == 0? false : val2p1_Tagger_b_Ymin_discrete >= 1")
        
        flagstring_1p1 = "1 "
        flagstring_2p1 = "1 "
        for c in self.analyzer.DataFrame.GetColumnNames():
            if "flag1p1" in  str(c):
                flagstring_1p1 += f"&& {str(c)} "
            if "flag2p1" in  str(c):
                flagstring_2p1 += f"&& {str(c)} "
        print(flagstring_1p1)
        print(flagstring_2p1)
        self.analyzer.Define("flag1p1", flagstring_1p1)
        self.analyzer.Define("flag2p1", flagstring_2p1)
        self.analyzer.Cut("flag1p1_or_flag2p1", "flag1p1 || flag2p1")
        #self.register_weight("flag1p1_or_flag2p1")




    ######################################################################################################################


        self.analyzer.Define("leadingFatJetPt", f"FatJet_pt_{JME_syst}[0]")
        self.analyzer.Define("leadingFatJetPhi", "FatJet_phi[0]")
        self.analyzer.Define("leadingFatJetEta", "FatJet_eta[0]")
        self.analyzer.Define("leadingFatJetMsoftdrop", f"FatJet_msoftdrop_{JME_syst}[0]")






        if (self.isData != 1 and triggerType != "Reference"):
            self.analyzer.AddCorrection(
                Correction('corr1p1_TriggerSF_data','cpp_modules/Trigger_SF.cc',["raw_nano/trigger_1p1_SFs.json", self.year], corrtype='weight'), {"pt":"leadingFatJetPt", "mass":"val1p1_MX", "uncert":'"data"'}
            ) 
            self.analyzer.AddCorrection(
                Correction('corr1p1_TriggerSF_MC','cpp_modules/Trigger_SF.cc',["raw_nano/trigger_1p1_SFs.json", self.year], corrtype='weight'), {"pt":"leadingFatJetPt", "mass":"val1p1_MX", "uncert":'"MC"'}
            ) 
            self.analyzer.AddCorrection(
                Correction('corr2p1_TriggerSF_data','cpp_modules/Trigger_SF.cc',["raw_nano/trigger_2p1_SFs.json", self.year], corrtype='weight'), {"pt":"leadingFatJetPt", "mass":"val2p1_MX", "uncert":'"data"'}
            ) 
            self.analyzer.AddCorrection(
                Correction('corr2p1_TriggerSF_MC','cpp_modules/Trigger_SF.cc',["raw_nano/trigger_2p1_SFs.json", self.year], corrtype='weight'), {"pt":"leadingFatJetPt", "mass":"val2p1_MX", "uncert":'"MC"'}
            ) 
        if "Signal" in self.dataset:
            self.genXHY()
            self.check_matching_1p1(combineMode = 1)
            self.check_matching_2p1(combineMode = 1)
            self.Xbbtagging_corr("1p1", True, combineMode = 1) 
            self.Xbbtagging_corr("2p1", True, combineMode = 1) 
            self.btagging_corr(JME_syst, True, combineMode = 1) 

        #Making weight columns
        uncerts_to_corr_1p1 = {}
        uncerts_to_corr_1p1["corr1p1_AK8_Xbbtagging"] = []
        WPs = ["L", "M", "T"]
        for wp in WPs:
            uncerts_to_corr_1p1["corr1p1_AK8_Xbbtagging"].append(f"corr1p1_AK8_Xbbtagging_wp{wp}")
            

        
        #Making weight columns
        uncerts_to_corr_2p1={"corr2p1_AK4_btagging_light_correlated" : ["corr2p1_AK4_btagging_light_uncorrelated"], "corr2p1_AK4_btagging_heavy_correlated" : ["corr2p1_AK4_btagging_heavy_uncorrelated"]}
        WPs = ["L", "M", "T", "XT", "XXT"]
        for wp in WPs:
            uncerts_to_corr_2p1["corr2p1_AK4_btagging_light_correlated"].append(f"corr2p1_AK4_btagging_light_correlated_wp{wp}")
            uncerts_to_corr_2p1["corr2p1_AK4_btagging_light_correlated"].append(f"corr2p1_AK4_btagging_light_uncorrelated_wp{wp}")
            uncerts_to_corr_2p1["corr2p1_AK4_btagging_heavy_correlated"].append(f"corr2p1_AK4_btagging_heavy_correlated_wp{wp}")
            uncerts_to_corr_2p1["corr2p1_AK4_btagging_heavy_correlated"].append(f"corr2p1_AK4_btagging_heavy_uncorrelated_wp{wp}")
        WPs = ["L", "M", "T"]
        uncerts_to_corr_2p1["corr2p1_AK8_Xbbtagging"] = []
        for wp in WPs:
            uncerts_to_corr_2p1["corr2p1_AK8_Xbbtagging"].append(f"corr2p1_AK8_Xbbtagging_wp{wp}")
        
        corrs_1p1 = []
        corrs_2p1 = []
        for corr_name in self.analyzer.GetCorrectionNames():
            if "corr1p1" in corr_name:
                corrs_1p1.append(corr_name)
            if "corr2p1" in corr_name:
                corrs_2p1.append(corr_name)
        

        print(corrs_1p1, corrs_2p1)
        self.analyzer.MakeWeightCols(name = "1p1", dropList = corrs_2p1, uncerts_to_corr = uncerts_to_corr_1p1)
        self.analyzer.MakeWeightCols(name = "2p1", dropList = corrs_1p1, uncerts_to_corr = uncerts_to_corr_2p1)

    
        
        print(f"DEBUG: { self.analyzer.GetActiveNode().DataFrame.Count().GetValue()}") 

























    def btagging_corr(self, JME_syst, seperate_WP, combineMode = 0):
        corr_prefix = ""
        val_prefix = ""
        if combineMode == 1:
            corr_prefix = "corr2p1_"

        
        _dataset = self.dataset[self.dataset.find("MX-") : self.dataset.find(".txt")]
        eff_file = f"raw_nano/btagging_effs/{self.year}_{_dataset}_AK4_btagging_eff.txt" 
        if self.year != "2024":
            SF_file = f"/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/BTV/{self.corr_year}/btagging.json.gz"
            SF_key_heavy = f"particleNet_comb" 
            SF_key_light = f"particleNet_light" 
        else:
            SF_file = f"/cvmfs/cms-griddata.cern.ch/cat/metadata/BTV/Run3-24CDEReprocessingFGHIPrompt-Summer24-NanoAODv15/latest/btagging.json.gz" 
            SF_key_heavy = "UParTAK4_comb"
            SF_key_light = "UParTAK4_light"
        print("using config for btagging corr: ", SF_file, SF_key_heavy, SF_key_light, eff_file) 
        
        self.analyzer.AddCorrection(
            Correction(f'{corr_prefix}AK4_btagging_light_correlated','cpp_modules/AK4_btagging_correction.cc',[SF_file, SF_key_heavy, SF_key_light, eff_file], corrtype='weight'), {"nJet":"nJet", "etas":"Jet_eta", "pts": f"Jet_pt_{JME_syst}", "flavors": "Jet_hadronFlavour", "scores_discrete" : "Jet_tagger_discrete", "correlated" : "true", "do_heavy_flavor" : "false", "do_light_flavor" : "true", "WP_variation" : "-1" , "corrType" : '"weight"' }
        ) 
        self.analyzer.AddCorrection(
            Correction(f'{corr_prefix}AK4_btagging_light_uncorrelated','cpp_modules/AK4_btagging_correction.cc',[SF_file, SF_key_heavy, SF_key_light, eff_file], corrtype='uncert'), {"nJet":"nJet", "etas":"Jet_eta", "pts": f"Jet_pt_{JME_syst}", "flavors": "Jet_hadronFlavour", "scores_discrete" : "Jet_tagger_discrete", "correlated" : "false", "do_heavy_flavor" : "false", "do_light_flavor" : "true", "WP_variation" : "-1" , "corrType" : '"uncert"' }
        ) 
        self.analyzer.AddCorrection(
            Correction(f'{corr_prefix}AK4_btagging_heavy_correlated','cpp_modules/AK4_btagging_correction.cc',[SF_file, SF_key_heavy, SF_key_light, eff_file], corrtype='weight'), {"nJet":"nJet", "etas":"Jet_eta", "pts": f"Jet_pt_{JME_syst}", "flavors": "Jet_hadronFlavour", "scores_discrete" : "Jet_tagger_discrete", "correlated" : "true", "do_heavy_flavor" : "true", "do_light_flavor" : "false" , "WP_variation" : "-1" , "corrType" : '"weight"'}
        ) 
        self.analyzer.AddCorrection(
            Correction(f'{corr_prefix}AK4_btagging_heavy_uncorrelated','cpp_modules/AK4_btagging_correction.cc',[SF_file, SF_key_heavy, SF_key_light, eff_file], corrtype='uncert'), {"nJet":"nJet", "etas":"Jet_eta", "pts": f"Jet_pt_{JME_syst}", "flavors": "Jet_hadronFlavour", "scores_discrete" : "Jet_tagger_discrete", "correlated" : "false", "do_heavy_flavor" : "true", "do_light_flavor" : "false" , "WP_variation" : "-1" , "corrType" : '"uncert"'}
        ) 
        if seperate_WP:
            WPs = ["L", "M", "T", "XT", "XXT"]
            for i in range(len(WPs)):
                wp = WPs[i]
                self.analyzer.AddCorrection(
                    Correction(f'{corr_prefix}AK4_btagging_light_correlated_wp{wp}','cpp_modules/AK4_btagging_correction.cc',[SF_file, SF_key_heavy, SF_key_light, eff_file], corrtype='uncert'), {"nJet":"nJet", "etas":"Jet_eta", "pts": f"Jet_pt_{JME_syst}", "flavors": "Jet_hadronFlavour", "scores_discrete" : "Jet_tagger_discrete", "correlated" : "true", "do_heavy_flavor" : "false", "do_light_flavor" : "true", "WP_variation" : f"{i + 1}" , "corrType" : '"uncert"' }
                ) 
                self.analyzer.AddCorrection(
                    Correction(f'{corr_prefix}AK4_btagging_light_uncorrelated_wp{wp}','cpp_modules/AK4_btagging_correction.cc',[SF_file, SF_key_heavy, SF_key_light, eff_file], corrtype='uncert'), {"nJet":"nJet", "etas":"Jet_eta", "pts": f"Jet_pt_{JME_syst}", "flavors": "Jet_hadronFlavour", "scores_discrete" : "Jet_tagger_discrete", "correlated" : "false", "do_heavy_flavor" : "false", "do_light_flavor" : "true", "WP_variation" : f"{i + 1}" , "corrType" : '"uncert"' }
                ) 
                self.analyzer.AddCorrection(
                    Correction(f'{corr_prefix}AK4_btagging_heavy_correlated_wp{wp}','cpp_modules/AK4_btagging_correction.cc',[SF_file, SF_key_heavy, SF_key_light, eff_file], corrtype='uncert'), {"nJet":"nJet", "etas":"Jet_eta", "pts": f"Jet_pt_{JME_syst}", "flavors": "Jet_hadronFlavour", "scores_discrete" : "Jet_tagger_discrete", "correlated" : "true", "do_heavy_flavor" : "true", "do_light_flavor" : "false" , "WP_variation" : f"{i + 1}" , "corrType" : '"uncert"'}
                ) 
                self.analyzer.AddCorrection(
                    Correction(f'{corr_prefix}AK4_btagging_heavy_uncorrelated_wp{wp}','cpp_modules/AK4_btagging_correction.cc',[SF_file, SF_key_heavy, SF_key_light, eff_file], corrtype='uncert'), {"nJet":"nJet", "etas":"Jet_eta", "pts": f"Jet_pt_{JME_syst}", "flavors": "Jet_hadronFlavour", "scores_discrete" : "Jet_tagger_discrete", "correlated" : "false", "do_heavy_flavor" : "true", "do_light_flavor" : "false" , "WP_variation" : f"{i + 1}" , "corrType" : '"uncert"'}
                ) 










    def Xbbtagging_corr(self, mode, seperate_WP, combineMode = 0):
        corr_prefix_1p1 = ""
        corr_prefix_2p1 = ""
        val_prefix_1p1 = ""
        val_prefix_2p1 = ""
        if combineMode == 1:
            corr_prefix_1p1 = "corr1p1_"
            val_prefix_1p1 = "val1p1_"
            corr_prefix_2p1 = "corr2p1_"
            val_prefix_2p1 = "val2p1_"
            
        _dataset = self.dataset[self.dataset.find("MX-") : self.dataset.find(".txt")]
        eff_file = f"raw_nano/Xbbtagging_effs/{mode}_{self.year}_{_dataset}_AK8_Xbbtagging_eff.txt" 
        SF_file = f"raw_nano/Xbbtagging_SFs/{self.year}_AK8_Xbbtagging_SF.txt" 
        print("using config for Xbbtagging corr: ", SF_file, eff_file) 
        
        if mode == "1p1":
            self.analyzer.AddCorrection(
                Correction(f'{corr_prefix_1p1}AK8_Xbbtagging','cpp_modules/AK8_Xbbtagging_correction.cc',[SF_file, eff_file], corrtype='weight'), {"nJet":"2", "etas":f"{{ {val_prefix_1p1}EtaHiggsCandidate, {val_prefix_1p1}EtaYCandidate}}", "pts": f"{{ {val_prefix_1p1}PtHiggsCandidate, {val_prefix_1p1}PtYCandidate}}", "flavors": f"{{ {val_prefix_1p1}Higgs_matched_to_Xbb, {val_prefix_1p1}Y_matched_to_Xbb}}", "scores_discrete" : f"{{ {val_prefix_1p1}Tagger_H_discrete, {val_prefix_1p1}Tagger_Y_discrete }}", "WP_variation" : "-1" , "corrType" : '"weight"'}
            ) 
            if seperate_WP:
                WPs = ["L", "M", "T"]
                for i in range(len(WPs)):
                    wp = WPs[i]
                    self.analyzer.AddCorrection(
                        Correction(f'{corr_prefix_1p1}AK8_Xbbtagging_wp{wp}','cpp_modules/AK8_Xbbtagging_correction.cc',[SF_file, eff_file], corrtype='uncert'), {"nJet":"2", "etas":f"{{ {val_prefix_1p1}EtaHiggsCandidate, {val_prefix_1p1}EtaYCandidate }}", "pts": f"{{ {val_prefix_1p1}PtHiggsCandidate, {val_prefix_1p1}PtYCandidate }}", "flavors": f"{{ {val_prefix_1p1}Higgs_matched_to_Xbb, {val_prefix_1p1}Y_matched_to_Xbb}}", "scores_discrete" : f"{{ {val_prefix_1p1}Tagger_H_discrete, {val_prefix_1p1}Tagger_Y_discrete}}", "WP_variation" : f"{i+1}" , "corrType" : '"uncert"'}
                    )
 
        if mode == "2p1":
            self.analyzer.AddCorrection(
                Correction(f'{corr_prefix_2p1}AK8_Xbbtagging','cpp_modules/AK8_Xbbtagging_correction.cc',[SF_file, eff_file], corrtype='weight'), {"nJet":"1", "etas":f"{{ {val_prefix_2p1}EtaHiggsCandidate}}", "pts": f"{{ {val_prefix_2p1}PtHiggsCandidate}}", "flavors": f"{{ {val_prefix_2p1}Higgs_matched_to_Xbb}}", "scores_discrete" : f"{{ {val_prefix_2p1}Tagger_H_discrete}}" , "WP_variation" : "-1" , "corrType" : '"weight"'}
            )
            if seperate_WP: 
                WPs = ["L", "M", "T"]
                for i in range(len(WPs)):
                    wp = WPs[i]
                    self.analyzer.AddCorrection(
                        Correction(f'{corr_prefix_2p1}AK8_Xbbtagging_wp{wp}','cpp_modules/AK8_Xbbtagging_correction.cc',[SF_file, eff_file], corrtype='uncert'), {"nJet":"1", "etas":f"{{ {val_prefix_2p1}EtaHiggsCandidate}}", "pts": f"{{ {val_prefix_2p1}PtHiggsCandidate}}", "flavors": f"{{ {val_prefix_2p1}Higgs_matched_to_Xbb}}", "scores_discrete" : f"{{ {val_prefix_2p1}Tagger_H_discrete}}" , "WP_variation" : f"{i+1}" , "corrType" : '"uncert"'}
                    ) 

        
        
    def selection_combined_old(self, JME_syst = "nom", region = "Signal"):
        OBSOLETE
        AutoJetID.AutoJetID(self.analyzer, self.corr_year, ["Jet","FatJet"], nanoAOD_ver = self.nanoAOD_ver)
        if self.year != "2024":
            AutoJME.AutoJME(self.analyzer, ["Jet", "FatJet"], self.corr_year, self.data_era, True)
        else:
            AutoJME.AutoJME(self.analyzer, ["Jet"], self.corr_year, self.data_era, True)
            self.analyzer.Define(f"FatJet_pt_{JME_syst}", "FatJet_pt")
            self.analyzer.Define(f"FatJet_msoftdrop_{JME_syst}", "FatJet_msoftdrop")
        if not (self.isData == 1):
            if self.year != "2024":
                AutoPU.AutoPU(self.analyzer, self.corr_year)
            else:
                 AutoPU.AutoPU(self.analyzer, "2023_Summer23BPix")  
            genW    = Correction('genW',"cpp_modules/genW.cc",corrtype='corr')
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

        self.register_weight("JERCJetVeto")

        AutoNF(self.analyzer, self.year, self.isData)
        self.register_weight("NoiseFilterCut")
        
        #Lepton veto
        self.analyzer.Define("nEle", "nElectrons(nElectron, Electron_cutBased, 0, Electron_pt,20, Electron_eta)")
        self.analyzer.Define("nMu", "nMuons(nMuon, Muon_looseId, Muon_pfIsoId, 0, Muon_pt, 20, Muon_eta)")
        self.analyzer.Cut("LeptonVetoCut", "nMu==0 && nEle==0")
        self.register_weight("LeptonVeto")
        
        #Triggers and Flags
        with open("raw_nano/Trigger.json") as f:
            triggers = json.load(f)
        hadron_triggers = triggers["Hadron"][self.year]
        print(hadron_triggers)
        triggerCut = self.analyzer.GetTriggerString(hadron_triggers)
        print(triggerCut)
        self.analyzer.Cut("TriggerCut", triggerCut)
        self.register_weight("TriggerCut")

        self.analyzer.Define("leadingFatJetPt", f"FatJet_pt_{JME_syst}.at(0)")
        self.analyzer.Define("leadingFatJetPhi", "FatJet_phi.at(0)")
        self.analyzer.Define("leadingFatJetEta", "FatJet_eta.at(0)")
        self.analyzer.Define("leadingFatJetMsoftdrop", f"FatJet_msoftdrop_{JME_syst}.at(0)")

        #################################1p1####################################################################
        self.analyzer.Define("flag1p1_SkimCut", "SkimFlag == 1 || SkimFlag == 3") 

        #FatJet quality
        self.analyzer.Define("flag1p1_IDCut","flag1p1_SkimCut == 0 ? false : FatJet_jetId_corr.at(0) >= 2 && FatJet_jetId_corr.at(1) >= 2")
        
        #FatJet Pt
        self.analyzer.Define("flag1p1_PtCut", f"flag1p1_SkimCut == 0 ? false : FatJet_pt_{JME_syst}.at(0) > 450 && FatJet_pt_{JME_syst}.at(1) > 450")

        #FatJet Mass
        self.analyzer.Define("flag1p1_MassCut", f"flag1p1_SkimCut == 0 ? false : FatJet_msoftdrop_{JME_syst}.at(0) > 40 && FatJet_msoftdrop_{JME_syst}.at(1) > 40" )

        #FatJet Delta R
        self.analyzer.Define("flag1p1_DeltaEtaCut", "flag1p1_SkimCut == 0 ? false : abs(FatJet_eta.at(0) - FatJet_eta.at(1)) < 1.3")
        
        #Higgs Match
        if region == "Control":
            self.analyzer.Define("val1p1_idxH_try", f"higgsMassMatching(FatJet_msoftdrop_{JME_syst}[0], FatJet_msoftdrop_{JME_syst}[1], 150, 200)")
        elif region == "Signal":
            self.analyzer.Define("val1p1_idxH_try", f"higgsMassMatching(FatJet_msoftdrop_{JME_syst}[0], FatJet_msoftdrop_{JME_syst}[1], 100, 150)")
        self.analyzer.Define("val1p1_idxY_try", "flag1p1_SkimCut == 0 ? 0 : 1 - val1p1_idxH_try")
        self.analyzer.Define("val1p1_idxH", "flag1p1_SkimCut == 0 ? 0 : std::max(0, val1p1_idxH_try)")
        self.analyzer.Define("val1p1_idxY", "flag1p1_SkimCut == 0 ? 0 : std::min(1, val1p1_idxY_try)")
        self.analyzer.Define("flag1p1_HiggsCut", "flag1p1_SkimCut == 0 ? false : val1p1_idxH_try >= 0") 


    
        #Defining a bunch of variables for later use
        self.analyzer.Define("val1p1_MassHiggsCandidate",f"flag1p1_SkimCut == 0 ? 0.f : FatJet_msoftdrop_{JME_syst}[val1p1_idxH]")
        self.analyzer.Define("val1p1_PtHiggsCandidate", f"flag1p1_SkimCut == 0 ? 0.f : FatJet_pt_{JME_syst}[val1p1_idxH]")
        self.analyzer.Define("val1p1_EtaHiggsCandidate", "flag1p1_SkimCut == 0 ? 0.f : FatJet_eta[val1p1_idxH]")
        self.analyzer.Define("val1p1_PhiHiggsCandidate", "flag1p1_SkimCut == 0 ? 0.f : FatJet_phi[val1p1_idxH]")
        self.analyzer.Define("val1p1_PNet_H", "flag1p1_SkimCut == 0 ? 0.f : FatJet_particleNet_XbbVsQCD[val1p1_idxH]")
        
        self.analyzer.Define("val1p1_MassYCandidate", f"flag1p1_SkimCut == 0 ? 0.f : FatJet_msoftdrop_{JME_syst}[val1p1_idxY]")
        self.analyzer.Define("val1p1_PtYCandidate", f"flag1p1_SkimCut == 0 ? 0.f : FatJet_pt_{JME_syst}[val1p1_idxY]")
        self.analyzer.Define("val1p1_EtaYCandidate", "flag1p1_SkimCut == 0 ? 0.f : FatJet_eta[val1p1_idxY]")
        self.analyzer.Define("val1p1_PhiYCandidate", "flag1p1_SkimCut == 0 ? 0.f : FatJet_phi[val1p1_idxY]")
        self.analyzer.Define("val1p1_PNet_Y", "flag1p1_SkimCut == 0 ? 0.f : FatJet_particleNet_XbbVsQCD[val1p1_idxY]")
        
        #X(JJ) Mass
        self.analyzer.Define(f"val1p1_MassLeadingTwoFatJets", "flag1p1_SkimCut == 0 ? 0.f : InvMass_PtEtaPhiM({val1p1_PtHiggsCandidate, val1p1_PtYCandidate}, {val1p1_EtaHiggsCandidate, val1p1_EtaYCandidate}, {val1p1_PhiHiggsCandidate, val1p1_PhiYCandidate}, {val1p1_MassHiggsCandidate, val1p1_MassYCandidate})")
        self.analyzer.Define("flag1p1_MJJCut", "flag1p1_SkimCut == 0 ? false : val1p1_MassLeadingTwoFatJets > 200")


        
        self.analyzer.Define("val1p1_MJY", "val1p1_MassYCandidate")
        self.analyzer.Define("val1p1_MJJ", "val1p1_MassLeadingTwoFatJets")
        self.analyzer.Define("val1p1_MY", "val1p1_MassYCandidate")
        self.analyzer.Define("val1p1_MX", "val1p1_MassLeadingTwoFatJets")

        #######################################2p1########################################################## 
        #Skimming for 2p1
        self.analyzer.Define("flag2p1_SkimCut", "SkimFlag == 2 || SkimFlag == 3")
        
        #Looking for Higgs Jet
        #self.analyzer.Define("val2p1_idxJH_try", f"flag2p1_SkimCut == 0 ? 0 : FindIdxJH(FatJet_msoftdrop_{JME_syst}, 100, 150, 10000)")
        if region == "Signal":
            self.analyzer.Define("val2p1_idxJH_try", f"FindIdxJH(FatJet_msoftdrop_{JME_syst}, 100, 150, 10000, 125)")
        elif region == "Control":
            self.analyzer.Define("val2p1_idxJH_try", f"FindIdxJH(FatJet_msoftdrop_{JME_syst}, 150, 200, 10000, 175)")
        self.analyzer.Define("val2p1_idxJH", f"flag2p1_SkimCut == 0 ? 0 : std::max(val2p1_idxJH_try, 0)")
        self.analyzer.Define("flag2p1_HiggsMassCut", f"flag2p1_SkimCut == 0 ? false : val2p1_idxJH_try >= 0")

        
        self.analyzer.Define("val2p1_MassHiggsCandidate", f"flag2p1_SkimCut == 0 ? 0.f : FatJet_msoftdrop_{JME_syst}[val2p1_idxJH]")
        self.analyzer.Define("val2p1_PtHiggsCandidate", f"flag2p1_SkimCut == 0 ? 0.f : FatJet_pt_{JME_syst}[val2p1_idxJH]")
        self.analyzer.Define("val2p1_EtaHiggsCandidate", "flag2p1_SkimCut == 0 ? 0.f : FatJet_eta[val2p1_idxJH]")
        self.analyzer.Define("val2p1_PhiHiggsCandidate", "flag2p1_SkimCut == 0 ? 0.f : FatJet_phi[val2p1_idxJH]") 
        self.analyzer.Define("val2p1_PNet_H", "flag2p1_SkimCut == 0 ? 0.f : FatJet_particleNet_XbbVsQCD[val2p1_idxJH]")
        

        #Higgs Jet Quality
        self.analyzer.Define("flag2p1_HiggsEtaCut", "flag2p1_SkimCut == 0 ? false : std::abs(val2p1_EtaHiggsCandidate) < 2.5")

        self.analyzer.Define("flag2p1_FatJetIDCut","flag2p1_SkimCut == 0 ? false : FatJet_jetId_corr[val2p1_idxJH] >= 2 ")


        self.analyzer.Define("flag2p1_PtCut", f"flag2p1_SkimCut == 0 ? false : val2p1_PtHiggsCandidate > 300")
        

        #Defining several regions depending on the B tagging score for the Y Jets
        #self.analyzer.Define("val2p1_DeltaR_HJ", f" DeltaR(Jet_eta, Jet_phi, FatJet_eta[val2p1_idxJH], FatJet_phi[val2p1_idxJH])")

        #Looking for Y Jets
        self.analyzer.Define("val2p1_idxJY_try", f"flag2p1_SkimCut == 0 ? RVec<int>({0, 0}) : FindIdxJY(Jet_eta, Jet_phi, val2p1_EtaHiggsCandidate, val2p1_PhiHiggsCandidate, Jet_btagPNetB, 0.8)")
        self.analyzer.Define("val2p1_idxJY", "flag2p1_SkimCut == 0 ? RVec<int>({0, 0}) : RVec<int>({std::max(val2p1_idxJY_try.at(0), 0), std::max(val2p1_idxJY_try.at(1), 0)})")
        self.analyzer.Define("flag2p1_IdxJYCut", "flag2p1_SkimCut == 0 ? false : val2p1_idxJY_try.at(0) >= 0 && val2p1_idxJY_try.at(1) >= 0")


        #Defining a bunch of variables for later use
        self.analyzer.Define("val2p1_idxJY0", "flag2p1_SkimCut == 0 ? 0 : val2p1_idxJY.at(0)")
        self.analyzer.Define("val2p1_idxJY1", "flag2p1_SkimCut == 0 ? 0 : val2p1_idxJY.at(1)")  
        self.analyzer.Define("val2p1_PtJY0", f"flag2p1_SkimCut == 0 ? 0.f : Jet_pt_{JME_syst}[val2p1_idxJY0]")
        self.analyzer.Define("val2p1_PtJY1", f"flag2p1_SkimCut == 0 ? 0.f : Jet_pt_{JME_syst}[val2p1_idxJY1]")
        self.analyzer.Define("val2p1_EtaJY0", "flag2p1_SkimCut == 0 ? 0.f : Jet_eta[val2p1_idxJY0]")
        self.analyzer.Define("val2p1_EtaJY1", "flag2p1_SkimCut == 0 ? 0.f : Jet_eta[val2p1_idxJY1]")
        self.analyzer.Define("val2p1_PhiJY0", "flag2p1_SkimCut == 0 ? 0.f : Jet_phi[val2p1_idxJY0]")
        self.analyzer.Define("val2p1_PhiJY1", "flag2p1_SkimCut == 0 ? 0.f : Jet_phi[val2p1_idxJY1]")
        self.analyzer.Define("val2p1_MassJY0", f"flag2p1_SkimCut == 0 ? 0.f : Jet_mass_{JME_syst}[val2p1_idxJY0]")
        self.analyzer.Define("val2p1_MassJY1", f"flag2p1_SkimCut == 0 ? 0.f : Jet_mass_{JME_syst}[val2p1_idxJY1]")
        self.analyzer.Define("val2p1_PNet_Y0", "flag2p1_SkimCut == 0 ? 0.f : Jet_btagPNetB[val2p1_idxJY0]")
        self.analyzer.Define("val2p1_PNet_Y1", "flag2p1_SkimCut == 0 ? 0.f : Jet_btagPNetB[val2p1_idxJY1]")
        self.analyzer.Define("val2p1_PNet_Ymin", "flag2p1_SkimCut == 0 ? 0.f : std::min(val2p1_PNet_Y0, val2p1_PNet_Y1)")
        self.analyzer.Define("val2p1_PNet_Y", "flag2p1_SkimCut == 0 ? 0.f : std::max(val2p1_PNet_Y0, val2p1_PNet_Y1)")




        self.analyzer.Define("flag2p1_YJetIDCut", " flag2p1_SkimCut == 0 ? false : Jet_jetId_corr[val2p1_idxJY0] >= 2 && Jet_jetId_corr[val2p1_idxJY1] >= 2")
        self.analyzer.Define("flag2p1_YPtCut", "flag2p1_SkimCut == 0 ? false : val2p1_PtJY0 >= 50 && val2p1_PtJY0 >= 50")
        self.analyzer.Define("flag2p1_YEtaCut", "flag2p1_SkimCut == 0 ? false : std::abs(val2p1_EtaJY0) < 2.5 && std::abs(val2p1_EtaJY1) < 2.5")
        
        
        self.analyzer.Define("val2p1_MassYCandidate", "flag2p1_SkimCut == 0 ? 0.f : InvMass_PtEtaPhiM({val2p1_PtJY0, val2p1_PtJY1}, {val2p1_EtaJY0, val2p1_EtaJY1}, {val2p1_PhiJY0, val2p1_PhiJY1}, {val2p1_MassJY0, val2p1_MassJY1} )" )
        self.analyzer.Define("val2p1_MassJJH", "flag2p1_SkimCut == 0 ? 0.f : InvMass_PtEtaPhiM({val2p1_PtHiggsCandidate, val2p1_PtJY0, val2p1_PtJY1}, {val2p1_EtaHiggsCandidate, val2p1_EtaJY0, val2p1_EtaJY1}, {val2p1_PhiHiggsCandidate, val2p1_PhiJY0, val2p1_PhiJY1}, {val2p1_MassHiggsCandidate, val2p1_MassJY0, val2p1_MassJY1})")
        self.analyzer.Define("flag2p1_MJJCut", "flag2p1_SkimCut == 0 ? 0.f : val2p1_MassJJH > 200")
     
        self.analyzer.Define("flag2p1_PNet_YminCut", "flag2p1_SkimCut == 0 ? false : val2p1_PNet_Ymin > 0.1")
        self.analyzer.Define("flag2p1_MJYCut", "flag2p1_SkimCut == 0 ? false : val2p1_MassYCandidate > 200")


        #defining a few variables
        self.analyzer.Define("val2p1_MJY", "val2p1_MassYCandidate")
        self.analyzer.Define("val2p1_MJJH", "val2p1_MassJJH")
        self.analyzer.Define("val2p1_MY", "val2p1_MassYCandidate")
        self.analyzer.Define("val2p1_MX", "val2p1_MassJJH")

        flagstring_1p1 = "1 "
        flagstring_2p1 = "1 "
        for c in self.analyzer.DataFrame.GetColumnNames():
            if "flag1p1" in  str(c):
                flagstring_1p1 += f"&& {str(c)} "
            if "flag2p1" in  str(c):
                flagstring_2p1 += f"&& {str(c)} "
        print(flagstring_1p1) 
        print(flagstring_2p1) 
        self.analyzer.Define("flag1p1", flagstring_1p1)
        self.analyzer.Define("flag2p1", flagstring_2p1)
        self.analyzer.Cut("flag1p1_or_flag2p1", "flag1p1 || flag2p1")
        self.register_weight("flag1p1_or_flag2p1")
        if not (self.isData == 1): #channel depedent corrections
            self.analyzer.AddCorrection(
                Correction('C1p1_TriggerSF','cpp_modules/Trigger_SF.cc',["raw_nano/trigger_1p1_SFs.json", self.year], corrtype='weight'), {"pt":"leadingFatJetPt", "mass":"val1p1_MX"}
            ) 
            self.analyzer.AddCorrection(
                Correction('C2p1_TriggerSF','cpp_modules/Trigger_SF.cc',["raw_nano/trigger_2p1_SFs.json", self.year], corrtype='weight'), {"pt":"leadingFatJetPt", "mass":"val2p1_MX"}
            ) 
        
        weights_1p1 = ["C1p1_TriggerSF"]
        weights_2p1 = ["C2p1_TriggerSF"]
        print(weights_1p1, weights_2p1)
        self.analyzer.MakeWeightCols(name = "1p1", dropList = weights_2p1)
        self.analyzer.MakeWeightCols(name = "2p1", dropList = weights_1p1)



    def register_weight_after_division_BDT(self):
        base_node = self.analyzer.GetActiveNode()
        self.analyzer.Cut("CutRegion_SR1", f"Region_SR1") 
        self.register_weight("Region_PASS")
        self.analyzer.SetActiveNode(base_node)

    def eff_after_selection_2p1(self):
        wp_H_2p1 = 0.98
        wp_Y_2p1 = 0.9659
        base_node = self.analyzer.GetActiveNode()
        self.analyzer.Cut("Region_SR_2p1", f"PNet_H > {wp_H_2p1} && PNet_Y > {wp_Y_2p1}") 
        self.register_weight("Region_SR_2p1")
        self.analyzer.SetActiveNode(base_node)

    def eff_after_selection_1p1(self):
        wp_H_1p1 = 0.98
        wp_Y_1p1 = 0.98
        base_node = self.analyzer.GetActiveNode()
        self.analyzer.Cut("Region_SR_1p1", f"PNet_H > {wp_H_1p1} && PNet_Y > {wp_Y_1p1}") 
        self.register_weight("Region_SR_1p1")
        self.analyzer.SetActiveNode(base_node)

    def eff_after_selection_compound(self): 
        wp_H_1p1 = 0.98
        wp_Y_1p1 = 0.98
        wp_H_2p1 = 0.98
        wp_Y_2p1 = 0.9659
        self.analyzer.Define("flag1p1_Region_SR_1p1", f"flag1p1 && val1p1_PNet_H > {wp_H_1p1} && val1p1_PNet_Y > {wp_Y_1p1}")
        self.analyzer.Define("flag2p1_Region_SR_2p1", f"flag2p1 && val2p1_PNet_H > {wp_H_2p1} && val2p1_PNet_Y > {wp_Y_2p1}")

        base_node = self.analyzer.GetActiveNode()
        self.analyzer.Cut("Region_SR_1p1", "flag1p1_Region_SR_1p1") 
        self.register_weight("Region_SR_1p1")
        self.analyzer.SetActiveNode(base_node)
        self.analyzer.Cut("Region_SR_2p1", "flag2p1_Region_SR_2p1") 
        self.register_weight("Region_SR_2p1")
        self.analyzer.SetActiveNode(base_node)
        self.analyzer.Cut("Region_SR_1p1_and_not_Region_SR_2p1", "flag1p1_Region_SR_1p1 && !(flag2p1_Region_SR_2p1)") 
        self.register_weight("Region_SR_1p1_and_not_Region_SR_2p1")
        self.analyzer.SetActiveNode(base_node)
        self.analyzer.Cut("Region_SR_2p1_and_not_Region_SR_1p1", "flag2p1_Region_SR_2p1 && !(flag1p1_Region_SR_1p1)") 
        self.register_weight("Region_SR_2p1_and_not_Region_SR_1p1")
        self.analyzer.SetActiveNode(base_node)
        self.analyzer.Cut("Region_SR_2p1_and_Region_SR_1p1", "flag2p1_Region_SR_2p1 && flag1p1_Region_SR_1p1") 
        self.register_weight("Region_SR_1p1_and_Region_SR_2p1")
        self.analyzer.SetActiveNode(base_node)




    def trainer_preprosessing_1p1(self, do_tagger = 1, do_mass = 1):
        if do_mass == 1:
            self.analyzer.Cut("MJJCut", "MX > 200")
            self.register_weight("MXCut")
         
            self.analyzer.Cut("MJYCut", "MY > 40")
            self.register_weight("MYCut")
        if do_tagger == 1: 
            self.analyzer.Cut("Tagger_H_min", "Tagger_H >= 0.1")
            self.register_weight("minTagger_H")
            self.analyzer.Cut("Tagger_Y_min", "Tagger_Y >= 0.1")
            self.register_weight("minTagger_Y")
        

    def trainer_preprosessing_2p1(self, do_tagger = 1, do_mass = 1):
        if do_mass ==  1:
            self.analyzer.Cut("MJJCut", "MX > 200")
            self.register_weight("MXCut")
         
            self.analyzer.Cut("MJYCut", "MY > 200")
            self.register_weight("MYCut")
        if do_tagger == 1: 
            self.analyzer.Cut("Tagger_H_min", "Tagger_H >= 0.1")
            self.register_weight("minTagger_H")
            self.analyzer.Cut("Tagger_b_Ymin", "Tagger_b_Ymin_discrete >= 1")
            self.register_weight("minTagger_Y")
        



    def BDT_tagging_discrete_1p1(self):      
        ###############Remove these lines if already defined
        decapitated_defined = 0
        for c in self.analyzer.DataFrame.GetColumnNames():
            if "decapitated" in str(c):
                decapitated_defined = 1
                break
        if decapitated_defined == 0:
            ROOT.gInterpreter.Declare(f'TaggerDiscretizer AK8_Discretizer = TaggerDiscretizer("FatJet",  "{self.corr_year}", "");')
            self.analyzer.Define("Tagger_H_decapitated", f"AK8_Discretizer.decapitate(Tagger_H)")
            self.analyzer.Define("Tagger_Y_decapitated", f"AK8_Discretizer.decapitate(Tagger_Y)")
        
        ROOT.gInterpreter.Declare('MVA_evaluator evaluator_1p1(4, std::vector<std::string>({ "Delta_Y", "MassHiggsCandidate", "Tagger_H_decapitated", "Tagger_Y_decapitated"}), "raw_nano/BDTs/TMVAClassification_BDTG_1p1_2022_2022EE_2023_2023BPix_2024_merged.weights.xml" );')
        if "RegSig" in self.dataset:
            self.analyzer.Define("BDTG", "evaluator_1p1.eval(std::vector<float>({ Delta_Y, MassHiggsCandidate, float(Tagger_H_decapitated), float(Tagger_Y_decapitated)}))")
        elif "RegCon" in self.dataset:
            self.analyzer.Define("MassHiggsCandidate_shift", "mass_shift(MassHiggsCandidate, 150, 200, 100, 150)")            
            self.analyzer.Define("BDTG", "evaluator_1p1.eval(std::vector<float>({ Delta_Y, MassHiggsCandidate_shift, float(Tagger_H_decapitated), float(Tagger_Y_decapitated)}))")
        elif "RegVal" in self.dataset:
            self.analyzer.Define("MassHiggsCandidate_shift", "mass_shift(MassHiggsCandidate, 60, 100, 100, 150)")            
            self.analyzer.Define("BDTG", "evaluator_1p1.eval(std::vector<float>({ Delta_Y, MassHiggsCandidate_shift, float(Tagger_H_decapitated), float(Tagger_Y_decapitated)}))")
        ROOT.gInterpreter.Declare('DDT_map Dmap_1p1;')
        #ROOT.gInterpreter.ProcessLine('Dmap_1p1.set_KNN("raw_nano/BDTs/BDT_threshold_discrete_MX1600_MY300_1p1_2022_2022EE_2023_2023BPix_2024_merged.txt");')
        #self.analyzer.Define("BDTG_threshold", f'Dmap_1p1.eval_KNN(MX, MY, 1, false)')
        #ROOT.gInterpreter.ProcessLine('Dmap_1p1.set_parametric("raw_nano/Dummy.txt", "   (-5.9954e-04 * exp (0.0014*x) +  0.9907) - 0.01");')
        #ROOT.gInterpreter.ProcessLine('Dmap_1p1.set_parametric("raw_nano/Dummy.txt", "0.98");')
        #ROOT.gInterpreter.ProcessLine('Dmap_1p1.set_parametric("raw_nano/Dummy.txt", "0.97 - 2e-6 * x");')
        ROOT.gInterpreter.ProcessLine('Dmap_1p1.set_parametric("raw_nano/Dummy.txt", "0.967");')
        self.analyzer.Define("BDTG_threshold", f'Dmap_1p1.eval_parametric(MX, MY)')
        self.analyzer.Define("Region_SR1", f'BDTG > BDTG_threshold')
        self.analyzer.Define("Region_SB1", f"! Region_SR1")
        self.register_weight_after_division_BDT()
 


    def BDT_tagging_discrete_2p1(self):      
        if self.year != "2024":
            ROOT.gInterpreter.Declare('MVA_evaluator evaluator_2p1(4, std::vector<std::string>({"MassHiggsCandidate", "Tagger_H_decapitated", "Tagger_b_Y0_decapitated", "Tagger_b_Y1_decapitated"}), "raw_nano/BDTs/TMVAClassification_BDTG_2p1_2022_2022EE_2023_2023BPix_merged.weights.xml" );')
            if "RegSig" in self.dataset:
                self.analyzer.Define("BDTG", "evaluator_2p1.eval(std::vector<float>({ MassHiggsCandidate, float(Tagger_H_decapitated), float(Tagger_b_Y0_decapitated), float(Tagger_b_Y1_decapitated)}))")
            elif "RegCon" in self.dataset:
                self.analyzer.Define("MassHiggsCandidate_shift", "mass_shift(MassHiggsCandidate, 150, 200, 100, 150)")            
                self.analyzer.Define("BDTG", "evaluator_2p1.eval(std::vector<float>({ MassHiggsCandidate_shift, float(Tagger_H_decapitated), float(Tagger_b_Y0_decapitated), float(Tagger_b_Y1_decapitated)}))")
            elif "RegVal" in self.dataset:
                self.analyzer.Define("MassHiggsCandidate_shift", "mass_shift(MassHiggsCandidate, 60, 100, 100, 150)")            
                self.analyzer.Define("BDTG", "evaluator_2p1.eval(std::vector<float>({ MassHiggsCandidate_shift, float(Tagger_H_decapitated), float(Tagger_b_Y0_decapitated), float(Tagger_b_Y1_decapitated)}))")

            ROOT.gInterpreter.Declare('DDT_map Dmap_2p1;')
            #ROOT.gInterpreter.ProcessLine('Dmap_2p1.set_KNN("raw_nano/BDTs/BDT_threshold_discrete_MX1600_MY500_2p1_2022_2022EE_2023_2023BPix_merged.txt");')
            #self.analyzer.Define("BDTG_threshold", f'Dmap_2p1.eval_KNN(MX, MY, 1, false)')
            #ROOT.gInterpreter.ProcessLine('Dmap_2p1.set_parametric("raw_nano/Dummy.txt", "(-1.3226e-04 * exp( 9.1526e-04* (x+y)) + 0.9951) - 0.009 ");')
            #ROOT.gInterpreter.ProcessLine('Dmap_2p1.set_parametric("raw_nano/Dummy.txt", "0.986 ");')
            #ROOT.gInterpreter.ProcessLine('Dmap_2p1.set_parametric("raw_nano/Dummy.txt", "( 0.987 * (1  - 2e-6 * x) * (1 - 2e-6 * y) )");')
            ROOT.gInterpreter.ProcessLine('Dmap_2p1.set_parametric("raw_nano/Dummy.txt", "( 0.981 )");')
            self.analyzer.Define("BDTG_threshold", f'Dmap_2p1.eval_parametric(MX, MY)')
            self.analyzer.Define("Region_SR1", f'BDTG > BDTG_threshold')
            self.analyzer.Define("Region_SB1", f"! Region_SR1")
            self.register_weight_after_division_BDT()

        elif self.year == "2024":
            ROOT.gInterpreter.Declare('MVA_evaluator evaluator_2p1(4, std::vector<std::string>({"MassHiggsCandidate", "Tagger_H_decapitated", "Tagger_b_Y0_decapitated", "Tagger_b_Y1_decapitated"}), "raw_nano/BDTs/TMVAClassification_BDTG_2p1_2024.weights.xml" );')
            if "RegSig" in self.dataset:
                self.analyzer.Define("BDTG", "evaluator_2p1.eval(std::vector<float>({ MassHiggsCandidate, float(Tagger_H_decapitated), float(Tagger_b_Y0_decapitated), float(Tagger_b_Y1_decapitated)}))")
            elif "RegCon" in self.dataset:
                self.analyzer.Define("MassHiggsCandidate_shift", "mass_shift(MassHiggsCandidate, 150, 200, 100, 150)")            
                self.analyzer.Define("BDTG", "evaluator_2p1.eval(std::vector<float>({ MassHiggsCandidate_shift, float(Tagger_H_decapitated), float(Tagger_b_Y0_decapitated), float(Tagger_b_Y1_decapitated)}))")
            elif "RegVal" in self.dataset:
                self.analyzer.Define("MassHiggsCandidate_shift", "mass_shift(MassHiggsCandidate, 60, 100, 100, 150)")            
                self.analyzer.Define("BDTG", "evaluator_2p1.eval(std::vector<float>({ MassHiggsCandidate_shift, float(Tagger_H_decapitated), float(Tagger_b_Y0_decapitated), float(Tagger_b_Y1_decapitated)}))")
            ROOT.gInterpreter.Declare('DDT_map Dmap_2p1;')
            #ROOT.gInterpreter.ProcessLine('Dmap_2p1.set_KNN("raw_nano/BDTs/BDT_threshold_discrete_MX1600_MY500_2p1_2024.txt");')
            #self.analyzer.Define("BDTG_threshold", f'Dmap_2p1.eval_KNN(MX, MY, 1, false)')
            #ROOT.gInterpreter.ProcessLine('Dmap_2p1.set_parametric("raw_nano/Dummy.txt", "(-1.3226e-04 * exp( 9.1526e-04* (x + y)) + 0.9951) - 0.005 ");')
            #ROOT.gInterpreter.ProcessLine('Dmap_2p1.set_parametric("raw_nano/Dummy.txt", "0.989 ");')
            #ROOT.gInterpreter.ProcessLine('Dmap_2p1.set_parametric("raw_nano/Dummy.txt", "( 0.99 * (1  - 2e-6 * x) * (1 - 2e-6 * y) ) ");')
            ROOT.gInterpreter.ProcessLine('Dmap_2p1.set_parametric("raw_nano/Dummy.txt", "( 0.984 )");')
            self.analyzer.Define("BDTG_threshold", f'Dmap_2p1.eval_parametric(MX, MY)')
            self.analyzer.Define("Region_SR1", f'BDTG > BDTG_threshold')
            self.analyzer.Define("Region_SB1", f"! Region_SR1")
            self.register_weight_after_division_BDT()



    def BDT_tagging_1p1(self):     
        OBSOLETE  
        ROOT.gInterpreter.Declare('MVA_evaluator evaluator(4, std::vector<std::string>({ "DeltaY", "MassHiggsCandidate", "PNet_H", "PNet_Y"}), "raw_nano/TMVAClassification_BDTG.weights_1p1.xml", 3, std::vector<std::string>({"BDT_weight", "minPNet", "sample_ID"}) );')
        self.analyzer.Define("BDTG", "evaluator.eval(std::vector<float>({ DeltaY, MassHiggsCandidate, PNet_H, PNet_Y}))")
        ROOT.gInterpreter.Declare('DDT_map Dmap("raw_nano/DDT_map_para_1p1.txt", "1.99/(1+exp(- [5] /x * ( [0] + [1]*x+[2]*y + [3]*x*x + [4]*y*y ))) - 1");')
        #ROOT.gInterpreter.Declare('DDT_map Dmap("raw_nano/DDT_map_para_1p1.txt", "0.8 + 0 * x * [5]");')
        self.analyzer.Define("BDTG_threshold", f'Dmap.eval(MX, MY)')
        self.analyzer.Define("Region_SR1", f'BDTG > BDTG_threshold')
        self.analyzer.Define("Region_SB1", f"! Region_SR1")
    
    def BDT_tagging_2p1(self):        
        OBSOLETE  
        ROOT.gInterpreter.Declare('MVA_evaluator evaluator(4, std::vector<std::string>({ "MassHiggsCandidate", "PNet_H", "PNet_Y", "PNet_Ymin"}), "raw_nano/TMVAClassification_BDTG.weights_2p1.xml", 6, std::vector<std::string>({"BDT_weight", "PNet_Y0", "PNet_Y1", "minPNet", "minPNet_higherY", "sample_ID"}) );')
        self.analyzer.Define("BDTG", "evaluator.eval(std::vector<float>({ MassHiggsCandidate, PNet_H, PNet_Y, PNet_Ymin}))")
        #ROOT.gInterpreter.Declare('DDT_map Dmap("raw_nano/DDT_map_para_2p1.txt", "0.14/(1+exp(- [5]  * ( [0] + [1]*x+[2]*y + [3]*x*x + [4]*y*y ))) + 0.78");')
        ROOT.gInterpreter.Declare('DDT_map Dmap("raw_nano/DDT_map_para_2p1.txt", "1.8/(1+exp( [4] * (sqrt( (x - [0]) * (x - [0]) / [1] / [1]  + (y - [2]) * (y - [2]) / [3] / [3]) - [5] ) ) ) - 1");')
        #ROOT.gInterpreter.Declare('DDT_map Dmap("raw_nano/DDT_map_para_2p1.txt", "0.16/(1+exp(- [5]  * ( [0] + [1]*x+[2]*y + [3]*x*x + [4]*y*y ))) + 0.8");')
        #ROOT.gInterpreter.Declare('DDT_map Dmap("raw_nano/DDT_map_para_2p1.txt", "0.8 + 0 * x * [5]");')
        self.analyzer.Define("BDTG_threshold", f'Dmap.eval(MX, MY)')
        self.analyzer.Define("Region_SR1", f'BDTG > BDTG_threshold')
        self.analyzer.Define("Region_SB1", f"! Region_SR1")



    #Defining Regions for mode 1p1
    def b_tagging_1p1(self):
        OBSOLETE  
        T_score_H = 0.95
        L_score_H = 0.8
        Aux_score1_H = 0.55
        Aux_score2_H = 0.3
        T_score_Y = 0.95
        L_score_Y = 0.8
        Aux_score1_Y = 0.3
        Aux_score2_Y = 0.2
        self.analyzer.Define("Region_SR1", f"PNet_H >= {T_score_H} && PNet_Y >= {T_score_Y}")
        self.analyzer.Define("Region_SR2", f"PNet_H >= {L_score_H} && PNet_Y >= {L_score_Y}")
        self.analyzer.Define("Region_SB1", f"PNet_H >= {T_score_H} && PNet_Y < {L_score_Y} && PNet_Y > {Aux_score1_Y}")
        self.analyzer.Define("Region_SB2", f"PNet_H >= {L_score_H} && PNet_Y < {L_score_Y} && PNet_Y > {Aux_score1_Y}")
        self.analyzer.Define("Region_VS1", f"PNet_H >= {Aux_score1_H} && PNet_H < {L_score_H} && PNet_Y >= {T_score_Y}")
        self.analyzer.Define("Region_VS2", f"PNet_H >= {Aux_score1_H} && PNet_H < {L_score_H} && PNet_Y >= {L_score_Y}")
        self.analyzer.Define("Region_VB1", f"PNet_H >= {Aux_score1_H} && PNet_H < {L_score_H} && PNet_Y < {L_score_Y} && PNet_Y > {Aux_score1_Y}")
        self.analyzer.Define("Region_VS3", f"PNet_H >= {Aux_score2_H} && PNet_H < {Aux_score1_H} && PNet_Y >= {T_score_Y}")
        self.analyzer.Define("Region_VS4", f"PNet_H >= {Aux_score2_H} && PNet_H < {Aux_score1_H} && PNet_Y >= {L_score_Y}")
        self.analyzer.Define("Region_VB2", f"PNet_H >= {Aux_score2_H} && PNet_H < {Aux_score1_H} && PNet_Y < {L_score_Y} && PNet_Y > {Aux_score1_Y}")
    
    def b_tagging_1p1_unbounded(self):
        OBSOLETE  
        T_score_H = 0.95
        L_score_H = 0.8
        Aux_score1_H = 0.55
        Aux_score2_H = 0.3
        T_score_Y = 0.95
        L_score_Y = 0.8
        Aux_score1_Y = 0.3
        Aux_score2_Y = 0.2
        self.analyzer.Define("Region_SR1", f"PNet_H >= {T_score_H} && PNet_Y >= {T_score_Y}")
        self.analyzer.Define("Region_SR2", f"PNet_H >= {L_score_H} && PNet_Y >= {L_score_Y}")
        self.analyzer.Define("Region_SB1", f"PNet_H >= {T_score_H} && PNet_Y < {L_score_Y}")
        self.analyzer.Define("Region_SB2", f"PNet_H >= {L_score_H} && PNet_Y < {L_score_Y}")
        self.analyzer.Define("Region_VS1", f"PNet_H >= {Aux_score1_H} && PNet_H < {L_score_H} && PNet_Y >= {T_score_Y}")
        self.analyzer.Define("Region_VS2", f"PNet_H >= {Aux_score1_H} && PNet_H < {L_score_H} && PNet_Y >= {L_score_Y}")
        self.analyzer.Define("Region_VB1", f"PNet_H >= {Aux_score1_H} && PNet_H < {L_score_H} && PNet_Y < {L_score_Y}")
        self.analyzer.Define("Region_VS3", f"PNet_H >= {Aux_score2_H} && PNet_H < {Aux_score1_H} && PNet_Y >= {T_score_Y}")
        self.analyzer.Define("Region_VS4", f"PNet_H >= {Aux_score2_H} && PNet_H < {Aux_score1_H} && PNet_Y >= {L_score_Y}")
        self.analyzer.Define("Region_VB2", f"PNet_H >= {Aux_score2_H} && PNet_H < {Aux_score1_H} && PNet_Y < {L_score_Y}")
    #defining Control and Validation regions in a different way
    def b_tagging_1p1_v1(self):
        T_score_H = 0.98
        L_score_H = 0.8
        Aux_score1_H = 0
        #Aux_score2_H = 0.3
        T_score_Y = 0.98
        L_score_Y = 0.8
        Aux_score1_Y = 0.55
        Aux_score2_Y = 0.3
        self.analyzer.Define("Region_SR1", f"PNet_Y >= {T_score_Y} && PNet_H >= {T_score_H}")
        self.analyzer.Define("Region_SR2", f"PNet_Y >= {L_score_Y} && PNet_H >= {L_score_H}")
        self.analyzer.Define("Region_SB1", f"PNet_Y >= {T_score_Y} && PNet_H < {L_score_H}")
        self.analyzer.Define("Region_SB2", f"PNet_Y >= {L_score_Y} && PNet_H < {L_score_H}")
        self.analyzer.Define("Region_VS1", f"PNet_Y >= {Aux_score1_Y} && PNet_Y < {L_score_Y} && PNet_H >= {T_score_H}")
        self.analyzer.Define("Region_VS2", f"PNet_Y >= {Aux_score1_Y} && PNet_Y < {L_score_Y} && PNet_H >= {L_score_H}")
        self.analyzer.Define("Region_VB1", f"PNet_Y >= {Aux_score1_Y} && PNet_Y < {L_score_Y} && PNet_H < {L_score_H}")
        self.analyzer.Define("Region_VS3", f"PNet_Y >= {Aux_score2_Y} && PNet_Y < {Aux_score1_Y} && PNet_H >= {T_score_H}")
        self.analyzer.Define("Region_VS4", f"PNet_Y >= {Aux_score2_Y} && PNet_Y < {Aux_score1_Y} && PNet_H >= {L_score_H}")
        self.analyzer.Define("Region_VB2", f"PNet_Y >= {Aux_score2_Y} && PNet_Y < {Aux_score1_Y} && PNet_H < {L_score_H}")
    
    #defining different regions for the 2p1 mode. Out-dated, should only use SR1, SR2, SB1 and SB2
    def b_tagging_2p1(self):
        OBSOLETE  
        T_score_H = 0.98
        L_score_H = 0.95
        Aux_score1_H = 0.5
        T_score_Y = 0.9659
        L_score_Y = 0.7515
        Aux_score1_Y = 0.5
        Aux_score2_Y = 0.3
        self.analyzer.Define("Region_SR1", f"PNet_Y >= {T_score_Y} && PNet_H >= {T_score_H}")
        self.analyzer.Define("Region_SR2", f"PNet_Y >= {L_score_Y} && PNet_H >= {L_score_H}")
        self.analyzer.Define("Region_SB1", f"PNet_Y >= {T_score_Y} && PNet_H < {L_score_H} && PNet_H > {Aux_score1_H}")
        self.analyzer.Define("Region_SB2", f"PNet_Y >= {L_score_Y} && PNet_H < {L_score_H} && PNet_H > {Aux_score1_H}")

        self.analyzer.Define("Region_VS1", f"PNet_Y >= {Aux_score1_Y} && PNet_Y < {L_score_Y} && PNet_H >= {T_score_H}")
        self.analyzer.Define("Region_VS2", f"PNet_Y >= {Aux_score1_Y} && PNet_Y < {L_score_Y} && PNet_H >= {L_score_H}")
        self.analyzer.Define("Region_VB1", f"PNet_Y >= {Aux_score1_Y} && PNet_Y < {L_score_Y} && PNet_H < {L_score_H} && PNet_H > {Aux_score1_H}")
        self.analyzer.Define("Region_VS3", f"PNet_Y >= {Aux_score2_Y} && PNet_Y < {Aux_score1_Y} && PNet_H >= {T_score_H}")
        self.analyzer.Define("Region_VS4", f"PNet_Y >= {Aux_score2_Y} && PNet_Y < {Aux_score1_Y} && PNet_H >= {L_score_H}")
        self.analyzer.Define("Region_VB2", f"PNet_Y >= {Aux_score2_Y} && PNet_Y < {Aux_score1_Y} && PNet_H < {L_score_H} && PNet_H > {Aux_score1_H}")
    
    #Make cuts on a region
    def divide(self, region):
        self.analyzer.Cut(f"RegionCut_{region}","Region_" + region)
        self.register_weight("Region_"+region)
    



    #Saving 2D Hist MX vs MY for 1p1 mode. MY is saved as the x axis and MX the Y axis
    def dumpTemplates_1p1(self, region, f, JME_syst, weight = "weight_All__nominal"):
        f.cd()
        MJY_bins = array.array("d", np.linspace(0, 5000, 501) )
        MJJ_bins = array.array("d", np.linspace(0, 5000, 501) )
        if JME_syst == "nom":
            templates = self.analyzer.MakeTemplateHistos(
                ROOT.TH2D(f"MXvsMY_{region}", f"MX vs MY in {region}", len(MJY_bins) - 1, MJY_bins, len(MJJ_bins) - 1, MJJ_bins), 
                ['MY','MX']
        )
            templates.Do('Write')
        else:
            hist = self.analyzer.DataFrame.Histo2D((f"MXvsMY_{region}__{weight}_{JME_syst}", f"MX vs MY in {region}", len(MJY_bins) - 1, MJY_bins, len(MJJ_bins) - 1, MJJ_bins), "MY", "MX", weight)
            hist.Write()

    #Saving 2D Hist MX vs MY for 2p1 mode. MY is saved as the x axis and MX the Y axis
    def dumpTemplates_2p1(self, region, f, JME_syst, weight = "weight_All__nominal"):
        f.cd()
        MJY_bins = array.array("d", np.linspace(0, 5000, 501) )
        MJJ_bins = array.array("d", np.linspace(0, 5000, 501) )
        if JME_syst == "nom":
            templates = self.analyzer.MakeTemplateHistos(
                ROOT.TH2D(f"MXvsMY_{region}", f"MX vs MY in {region}", len(MJY_bins) - 1, MJY_bins, len(MJJ_bins) - 1, MJJ_bins), 
                ['MY','MX']
        )
            templates.Do('Write')
        else:
            hist = self.analyzer.DataFrame.Histo2D((f"MXvsMY_{region}__{weight}_{JME_syst}", f"MX vs MY in {region}", len(MJY_bins) - 1, MJY_bins, len(MJJ_bins) - 1, MJJ_bins), "MY", "MX", weight)
            hist.Write()

    def dumpTemplates_normalized(self, region, f, JME_syst, weight_tag = "All"):
        f.cd()
        MY_bins = array.array("d", np.linspace(0, 5000, 501) )
        MX_bins = array.array("d", np.linspace(0, 5000, 501) )
        if JME_syst != "nom":
            self.analyzer.Define(f"weight_{weight_tag}__nominal_normalized", f"weight_{weight_tag}__nominal/ {self.sumW}")
            hist = self.analyzer.DataFrame.Histo2D((f"MXvsMY_{region}__weight_{weight_tag}__nominal_{JME_syst}", f"MX vs MY in {region}", len(MY_bins) - 1, MY_bins, len(MX_bins) - 1, MX_bins), "MY", "MX", f"weight_{weight_tag}__nominal_normalized")
            hist.Write()
        else:
            for c in self.analyzer.DataFrame.GetColumnNames():
                if str(c).startswith("weight_") and weight_tag in str(c):
                    weight = str(c)
                    self.analyzer.Define(f"{weight}_normalized", f"{weight}/ {self.sumW}")
                    hist = self.analyzer.DataFrame.Histo2D((f"MXvsMY_{region}__{weight}", f"MX vs MY in {region}", len(MY_bins) - 1, MY_bins, len(MX_bins) - 1, MX_bins), "MY", "MX", f"{weight}_normalized")
                    hist.Write()
          


    def dumpTemplates_compound(self, region, f, JME_syst, mode = "1p1", MX = "MX", MY = "MY", bin_scale = 1):
        f.cd()
        MY_bins = array.array("d", np.linspace(0, 5000 * bin_scale , 501) )
        MX_bins = array.array("d", np.linspace(0, 5000 * bin_scale, 501) )
        if JME_syst != "nom":
            self.analyzer.Define(f"weight_{mode}__nominal_normalized_{JME_syst}", f"weight_{mode}__nominal/ {self.sumW}")
            hist = self.analyzer.DataFrame.Histo2D((f"MXvsMY_{region}__weight_{mode}__nominal_{JME_syst}", f"MX vs MY in {region}", len(MY_bins) - 1, MY_bins, len(MX_bins) - 1, MX_bins), MY, MX, f"weight_{mode}__nominal_normalized_{JME_syst}")
            hist.Write()
        else:
            for c in self.analyzer.DataFrame.GetColumnNames():
                if str(c).startswith("weight_")  and mode in str(c):
                    weight = str(c)
                    self.analyzer.Define(f"{weight}_normalized", f"{weight}/ {self.sumW}")
                    hist = self.analyzer.DataFrame.Histo2D((f"MXvsMY_{region}__{weight}", f"MX vs MY in {region}", len(MY_bins) - 1, MY_bins, len(MX_bins) - 1, MX_bins), MY, MX, f"{weight}_normalized")
                    hist.Write()
          

    #Saving a bunch of Hists where the column name and bins are specified in the "bins" dictionary, and weight given in the "weights" list
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


    def make_TH2(self, bins, weights, f, name = ""):
        f.cd()
        for graph in bins:
            it = iter(graph)
            x_name = next(it)
            y_name = next(it)
            x_bins = graph[x_name]
            y_bins = graph[y_name]
            if len(weights) == 0:
                hist = self.analyzer.DataFrame.Histo2D((f"{x_name}_vs_{y_name}_{self.year}_{self.process}_{self.subprocess}_{self.n_files}_{self.i_job}_{name}", f"{x_name}_vs_{y_name}_{self.year}_{self.process}_{self.subprocess}_{self.n_files}_{self.i_job}_{name}", len(x_bins) - 1, x_bins, len(y_bins) - 1, y_bins ), x_name, y_name)
                hist.Write()
            else:
                for weight in weights:
                    hist = self.analyzer.DataFrame.Histo2D((f"{x_name}_vs_{y_name}_{self.year}_{self.process}_{self.subprocess}_{self.n_files}_{self.i_job}_{name}", f"{x_name}_vs_{y_name}_{self.year}_{self.process}_{self.subprocess}_{self.n_files}_{self.i_job}_{name}", len(x_bins) - 1, x_bins, len(y_bins) - 1, y_bins ), x_name, y_name, weight)
                    hist.Write()

##############################################################################################################################
#For testing
#############################################################################################################################

    def selection_without_trigger_1p1(self, JME_syst = "nom"):
        OBSOLETE
        #performing all the corrections
        AutoJME.AutoJME(self.analyzer, ["Jet", "FatJet"], self.corr_year, self.data_era, True)
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

        self.register_weight("JERCJetVeto")
        #Doing the skimming for 1p1
        
        AutoNF(self.analyzer, self.year, self.isData)
        self.register_weight("NoiseFilterCut")

        
        #lepton veto
        self.analyzer.Define("nEle", "nElectrons(nElectron, Electron_cutBased, 0, Electron_pt,20, Electron_eta)")
        self.analyzer.Define("nMu", "nMuons(nMuon, Muon_looseId, Muon_pfIsoId, 0, Muon_pt, 20, Muon_eta)")
        self.analyzer.Cut("LeptonVetoCut", "nMu==0 && nEle==0")
        self.register_weight("LeptonVeto")
        
        pre_trigger = ["HLT_PFJet260"]
        pretriggerCut = self.analyzer.GetTriggerString(pre_trigger)
        print(pretriggerCut)
        self.analyzer.Cut("PreTriggerCut", pretriggerCut)
        self.register_weight("PreTriggerCut")


        #Requiring two FatJets 
        self.analyzer.Cut("SkimCut", "SkimFlag == 1 || SkimFlag == 3") 
        self.register_weight("SkimOf1p1_2FatJets")


        #FatJet quality
        self.analyzer.Cut("IDCut","FatJet_jetId_corr.at(0) >= 2 && FatJet_jetId_corr.at(1) >= 2")
        self.register_weight("FatJetID")
        
        #FatJet Pt
        self.analyzer.Cut("PtCut", f"FatJet_pt_{JME_syst}.at(0) > 450 && FatJet_pt_{JME_syst}.at(1) > 450")
        self.register_weight("FatJetPt")

        #FatJet Mass
        self.analyzer.Cut("MassCut", f"FatJet_msoftdrop_{JME_syst}.at(0) > 40 && FatJet_msoftdrop_{JME_syst}.at(1) > 40" )
        self.register_weight("FatJetMass")

        #FatJet Delta R
        self.analyzer.Cut("DeltaEtaCut", "abs(FatJet_eta.at(0) - FatJet_eta.at(1)) < 1.3")
        self.register_weight("DeltaEta")
        
        #Higgs Match
        self.analyzer.Define("idxH", f"higgsMassMatching(FatJet_msoftdrop_{JME_syst}.at(0), FatJet_msoftdrop_{JME_syst}.at(1))")
        self.analyzer.Define("idxY", "1 - idxH")
        self.analyzer.Cut("HiggsCut", "idxH >= 0") 
        self.register_weight("HiggsMatch")


    

        #Defining a bunch of variables for later use
        self.analyzer.Define("MassHiggsCandidate",f"FatJet_msoftdrop_{JME_syst}[idxH]")
        self.analyzer.Define("PtHiggsCandidate", f"FatJet_pt_{JME_syst}[idxH]")
        self.analyzer.Define("EtaHiggsCandidate", "FatJet_eta[idxH]")
        self.analyzer.Define("PhiHiggsCandidate", "FatJet_phi[idxH]")
        self.analyzer.Define("PNet_H", "FatJet_particleNet_XbbVsQCD[idxH]")
        
        self.analyzer.Define("MassYCandidate", f"FatJet_msoftdrop_{JME_syst}[idxY]")
        self.analyzer.Define("PtYCandidate", f"FatJet_pt_{JME_syst}[idxY]")
        self.analyzer.Define("EtaYCandidate", "FatJet_eta[idxY]")
        self.analyzer.Define("PhiYCandidate", "FatJet_phi[idxY]")
        self.analyzer.Define("PNet_Y", "FatJet_particleNet_XbbVsQCD[idxY]")
        
        #X(JJ) Mass
        self.analyzer.Define(f"MassLeadingTwoFatJets", "InvMass_PtEtaPhiM({PtHiggsCandidate, PtYCandidate}, {EtaHiggsCandidate, EtaYCandidate}, {PhiHiggsCandidate, PhiYCandidate}, {MassHiggsCandidate, MassYCandidate})")
        self.analyzer.Cut("MJJCut", "MassLeadingTwoFatJets > 200")
        self.register_weight("MassJJ")


        self.analyzer.Define("leadingFatJetPt", f"FatJet_pt_{JME_syst}.at(0)")
        self.analyzer.Define("leadingFatJetPhi", "FatJet_phi.at(0)")
        self.analyzer.Define("leadingFatJetEta", "FatJet_eta.at(0)")
        self.analyzer.Define("leadingFatJetMsoftdrop", f"FatJet_msoftdrop_{JME_syst}.at(0)")
        
        self.analyzer.Define("MJY", "MassYCandidate")
        self.analyzer.Define("MJJ", "MassLeadingTwoFatJets")
        self.analyzer.Define("MY", "MassYCandidate")
        self.analyzer.Define("MX", "MassLeadingTwoFatJets")

        #Making weight columns
        self.analyzer.MakeWeightCols(name = "All")
        
        print(f"DEBUG: { self.analyzer.GetActiveNode().DataFrame.Count().GetValue()}") 


    
    def add_trigger(self, triggerType = "Hadron"):
        triggers = self.triggers[triggerType]
        print(triggers)
        triggerCut = self.analyzer.GetTriggerString(triggers)
        print(triggerCut)
        self.analyzer.Cut("TriggerCut", triggerCut)

        


    def selection_without_trigger_2p1(self, JME_syst = "nom"):
        OBSOLETE
        #Performing all corrections
        AutoJME.AutoJME(self.analyzer, ["Jet", "FatJet"], self.corr_year, self.data_era, True)
        if not (self.isData == 1):
            AutoPU.AutoPU(self.analyzer, self.corr_year)
            genW    = Correction('genW',"cpp_modules/genW.cc",corrtype='corr')
            evalargs = {
                    "genWeight": "genWeight",
                    "lumi": f"{self.lumi}",
                    "Xsec": f"{self.Xsec}",
                    "sumW": "1"
            }
            self.analyzer.AddCorrection(genW, evalargs)

        self.register_weight("JERCJetVeto")

        AutoNF(self.analyzer, self.year, self.isData)
        self.register_weight("NoiseFilterCut")
        
        #Lepton veto
        self.analyzer.Define("nEle", "nElectrons(nElectron, Electron_cutBased, 0, Electron_pt,20, Electron_eta)")
        self.analyzer.Define("nMu", "nMuons(nMuon, Muon_looseId, Muon_pfIsoId, 0, Muon_pt, 20, Muon_eta)")
        self.analyzer.Cut("LeptonVetoCut", "nMu==0 && nEle==0")
        self.register_weight("LeptonVeto")
        
        #Triggers and Flags
        pre_trigger = ["HLT_PFJet260"]
        pretriggerCut = self.analyzer.GetTriggerString(pre_trigger)
        print(pretriggerCut)
        self.analyzer.Cut("PreTriggerCut", pretriggerCut)
        self.register_weight("PreTriggerCut")

        #Skimming for 2p1
        self.analyzer.Cut("SkimCut", "SkimFlag == 2 || SkimFlag == 3")
        self.register_weight("SkimOf2p1")


        
        #Looking for Higgs Jet
        self.analyzer.Define("idxJH", f"FindIdxJH(FatJet_msoftdrop_{JME_syst}, 100, 150, 10000)")
        self.analyzer.Cut("HiggsMassCut", f"idxJH >= 0")
        self.register_weight("HiggsMatch")

        
        self.analyzer.Define("MassHiggsCandidate", f"FatJet_msoftdrop_{JME_syst}[idxJH]")
        self.analyzer.Define("PtHiggsCandidate", f"FatJet_pt_{JME_syst}[idxJH]")
        self.analyzer.Define("EtaHiggsCandidate", "FatJet_eta[idxJH]")
        self.analyzer.Define("PhiHiggsCandidate", "FatJet_phi[idxJH]") 
        self.analyzer.Define("PNet_H", "FatJet_particleNet_XbbVsQCD[idxJH]")
        

        #Higgs Jet Quality
        self.analyzer.Cut("HiggsEtaCut", "std::abs(EtaHiggsCandidate) < 2.5")
        self.register_weight("HiggsEta")

        self.analyzer.Cut("FatJetIDCut","FatJet_jetId_corr[idxJH] >= 2 ")
        self.register_weight("FatJetID")


        self.analyzer.Cut("PtCut", f"PtHiggsCandidate > 300")
        self.register_weight(f"FatJetPt")
        

        #Defining several regions depending on the B tagging score for the Y Jets

        #Looking for Y Jets
        self.analyzer.Define("idxJY", f"FindIdxJY(Jet_eta, Jet_phi, FatJet_eta[idxJH], FatJet_phi[idxJH], Jet_btagPNetB, 0.8)")
        self.analyzer.Cut("IdxJYCut", "idxJY.at(0) >= 0 && idxJY.at(1) >= 0")


        self.register_weight("JYMatch")
        #Defining a bunch of variables for later use
        self.analyzer.Define("idxJY0", "idxJY.at(0)")
        self.analyzer.Define("idxJY1", "idxJY.at(1)")  
        self.analyzer.Define("PtJY0", f"Jet_pt_{JME_syst}[idxJY0]")
        self.analyzer.Define("PtJY1", f"Jet_pt_{JME_syst}[idxJY1]")
        self.analyzer.Define("EtaJY0", "Jet_eta[idxJY0]")
        self.analyzer.Define("EtaJY1", "Jet_eta[idxJY1]")
        self.analyzer.Define("PhiJY0", "Jet_phi[idxJY0]")
        self.analyzer.Define("PhiJY1", "Jet_phi[idxJY1]")
        self.analyzer.Define("MassJY0", f"Jet_mass_{JME_syst}[idxJY0]")
        self.analyzer.Define("MassJY1", f"Jet_mass_{JME_syst}[idxJY1]")
        self.analyzer.Define("PNet_Y0", "Jet_btagPNetB[idxJY0]")
        self.analyzer.Define("PNet_Y1", "Jet_btagPNetB[idxJY1]")
        self.analyzer.Define("PNet_Ymin", "std::min(PNet_Y0, PNet_Y1)")
        self.analyzer.Define("PNet_Y", "std::max(PNet_Y0, PNet_Y1)")




        self.analyzer.Cut("YJetIDCut", "Jet_jetId_corr[idxJY0] >= 2 && Jet_jetId_corr[idxJY1] >= 2")
        self.register_weight("YJetID")
        self.analyzer.Cut("YPtCut", "PtJY0 >= 50 && PtJY0 >= 50")
        self.register_weight("YPt")
        self.analyzer.Cut("YEtaCut", "std::abs(EtaJY0) < 2.5 && std::abs(EtaJY1) < 2.5")
        self.register_weight("YEta")
        #self.analyzer.Cut("JYPtCut", "PtJY0 > 100 && PtJY1 > 100")

        
        
        self.analyzer.Define("MassYCandidate", "InvMass_PtEtaPhiM({PtJY0, PtJY1}, {EtaJY0, EtaJY1}, {PhiJY0, PhiJY1}, {MassJY0, MassJY1} )" )
        self.analyzer.Define("MassJJH", "InvMass_PtEtaPhiM({PtHiggsCandidate, PtJY0, PtJY1}, {EtaHiggsCandidate, EtaJY0, EtaJY1}, {PhiHiggsCandidate, PhiJY0, PhiJY1}, {MassHiggsCandidate, MassJY0, MassJY1})")
        self.analyzer.Cut("MJJCut", "MassJJH > 200")
        self.register_weight("MXCut")
     
        self.analyzer.Cut("PNet_YminCut", "PNet_Ymin > 0.1")
        self.register_weight("PNet_Ymin")
        self.analyzer.Cut("MJYCut", "MassYCandidate > 200")
        self.register_weight("MJYCut")


        #defining a few variables
        self.analyzer.Define("MJY", "MassYCandidate")
        self.analyzer.Define("MJJH", "MassJJH")
        self.analyzer.Define("MY", "MassYCandidate")
        self.analyzer.Define("MX", "MassJJH")

        self.analyzer.Define("leadingFatJetPt", f"FatJet_pt_{JME_syst}.at(0)")
        self.analyzer.Define("leadingFatJetPhi", "FatJet_phi.at(0)")
        self.analyzer.Define("leadingFatJetEta", "FatJet_eta.at(0)")
        self.analyzer.Define("leadingFatJetMsoftdrop", f"FatJet_msoftdrop_{JME_syst}.at(0)")
        #Making weight columns
        self.analyzer.MakeWeightCols(name = "All")
        
        print(f"DEBUG: { self.analyzer.GetActiveNode().DataFrame.Count().GetValue()}") 






    #Making N-1 plots for the 1p1 mode
    def Nminus1_1p1(self, JME_syst, MC_weight, f): 
        OBSOLETE
        f.cd()
        AutoJME.AutoJME(self.analyzer, ["Jet", "FatJet"], self.corr_year, self.data_era, True)
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

        self.register_weight("JERCJetVeto")
        #Doing the skimming for 1p1
        
        AutoNF(self.analyzer, self.year, self.isData)
        self.register_weight("NoiseFilterCut")

        
        #lepton veto
        self.analyzer.Define("nEle", "nElectrons(nElectron, Electron_cutBased, 0, Electron_pt,20, Electron_eta)")
        self.analyzer.Define("nMu", "nMuons(nMuon, Muon_looseId, Muon_pfIsoId, 0, Muon_pt, 20, Muon_eta)")
        self.analyzer.Cut("LeptonVetoCut", "nMu==0 && nEle==0")
        self.register_weight("LeptonVeto")
        

        
        #triggers and flags
        hadron_triggers = self.triggers
        print(hadron_triggers)
        triggerCut = self.analyzer.GetTriggerString(hadron_triggers)
        print(triggerCut)
        self.analyzer.Cut("TriggerCut", triggerCut)
        self.register_weight("TriggerCut")

        #Requiring two FatJets 
        self.analyzer.Cut("SkimCut", "SkimFlag == 1 || SkimFlag == 3") 
        self.register_weight("SkimOf1p1_2FatJets")


        #FatJet quality
        self.analyzer.Cut("IDCut","FatJet_jetId_corr.at(0) >= 2 && FatJet_jetId_corr.at(1) >= 2")
        self.register_weight("FatJetID")
        

        #FatJet Mass
        self.analyzer.Cut("MassCut", f"FatJet_msoftdrop_{JME_syst}.at(0) > 40 && FatJet_msoftdrop_{JME_syst}.at(1) > 40" )
        self.register_weight("FatJetMass")

        #Higgs Match
        self.analyzer.Define("idxH", f"higgsMassMatching(FatJet_msoftdrop_{JME_syst}.at(0), FatJet_msoftdrop_{JME_syst}.at(1))")
        self.analyzer.Define("idxY", "1 - idxH")
        self.analyzer.Cut("HiggsCut", "idxH >= 0") 
        self.register_weight("HiggsMatch")


    

        #Defining a bunch of variables for later use
        self.analyzer.Define("MassHiggsCandidate",f"FatJet_msoftdrop_{JME_syst}[idxH]")
        self.analyzer.Define("PtHiggsCandidate", f"FatJet_pt_{JME_syst}[idxH]")
        self.analyzer.Define("EtaHiggsCandidate", "FatJet_eta[idxH]")
        self.analyzer.Define("PhiHiggsCandidate", "FatJet_phi[idxH]")
        self.analyzer.Define("PNet_H", "FatJet_particleNet_XbbVsQCD[idxH]")
        
        self.analyzer.Define("MassYCandidate", f"FatJet_msoftdrop_{JME_syst}[idxY]")
        self.analyzer.Define("PtYCandidate", f"FatJet_pt_{JME_syst}[idxY]")
        self.analyzer.Define("EtaYCandidate", "FatJet_eta[idxY]")
        self.analyzer.Define("PhiYCandidate", "FatJet_phi[idxY]")
        self.analyzer.Define("PNet_Y", "FatJet_particleNet_XbbVsQCD[idxY]")
        
        #X(JJ) Mass
        self.analyzer.Define(f"MassLeadingTwoFatJets", "InvMass_PtEtaPhiM({PtHiggsCandidate, PtYCandidate}, {EtaHiggsCandidate, EtaYCandidate}, {PhiHiggsCandidate, PhiYCandidate}, {MassHiggsCandidate, MassYCandidate})")
        self.analyzer.Cut("MJJCut", "MassLeadingTwoFatJets > 200")
        self.register_weight("MassJJ")


        self.analyzer.Define("leadingFatJetPt", f"FatJet_pt_{JME_syst}.at(0)")
        self.analyzer.Define("leadingFatJetPhi", "FatJet_phi.at(0)")
        self.analyzer.Define("leadingFatJetEta", "FatJet_eta.at(0)")
        self.analyzer.Define("leadingFatJetMsoftdrop", f"FatJet_msoftdrop_{JME_syst}.at(0)")
        
        self.analyzer.Define("MJY", "MassYCandidate")
        self.analyzer.Define("MJJ", "MassLeadingTwoFatJets")
        self.analyzer.Define("MY", "MassYCandidate")
        self.analyzer.Define("MX", "MassLeadingTwoFatJets")

        self.analyzer.Define("FatJet_pt_0", f"FatJet_pt_{JME_syst}.at(0)")
        self.analyzer.Define("FatJet_pt_1", f"FatJet_pt_{JME_syst}.at(1)")
        self.analyzer.Define("deltaEta", "abs(FatJet_eta.at(0) - FatJet_eta.at(1))")
        self.analyzer.MakeWeightCols(name = "All")
        NCuts = CutGroup("Nminus1_1p1")
        Vars = {}

        NCuts.Add("PtHCut", f"FatJet_pt_0 > 450 && FatJet_pt_1 > 450")
        Vars["PtHCut"] = {f"FatJet_pt_0":array.array("d", np.linspace(0, 3000, 301)), f"FatJet_pt_1":array.array("d", np.linspace(0, 3000, 301))}

        NCuts.Add("DeltaEtaCut", "deltaEta < 1.3")
        Vars["DeltaEtaCut"] = {"deltaEta": array.array("d", np.linspace(0, 5, 101))}


        wp = 0.98
        NCuts.Add("BTaggingHCut", f"PNet_H >= {wp} && PNet_H >= {wp}") 
        Vars["BTaggingHCut"] = {f"PNet_H":array.array("d", np.linspace(0, 1, 101)), f"PNet_Y":array.array("d", np.linspace(0, 1, 101))}
        

        nodes = self.analyzer.Nminus1(NCuts)
        for key in nodes.keys():
            if key == "full":
                continue
            for var in Vars[key]:
                hist = nodes[key].DataFrame.Histo1D(( f"{key}__{var}__{self.year}__{self.process}__{self.subprocess}__{MC_weight}", f"{key}__{var}__{self.year}__{self.process}__{self.subprocess}__{MC_weight}", len(Vars[key][var]) - 1, Vars[key][var]), var, MC_weight )        
                hist.Write()





    def Nminus1_2p1(self, JME_syst, MC_weight, f): #making N-1 plots for the 2p1 mode. Pretty out-dated, needs update beforing using
        OBSOLETE
        AutoJME.AutoJME(self.analyzer, ["Jet", "FatJet"], self.corr_year, self.data_era, True)
        if not (self.isData == 1):
            AutoPU.AutoPU(self.analyzer, self.corr_year)
            genW    = Correction('genW',"cpp_modules/genW.cc",corrtype='corr')
            evalargs = {
                    "genWeight": "genWeight",
                    "lumi": f"{self.lumi}",
                    "Xsec": f"{self.Xsec}",
                    "sumW": "1"
            }
            self.analyzer.AddCorrection(genW, evalargs)

        self.register_weight("JERCJetVeto")

        AutoNF(self.analyzer, self.year, self.isData)
        self.register_weight("NoiseFilterCut")
        
        #Lepton veto
        self.analyzer.Define("nEle", "nElectrons(nElectron, Electron_cutBased, 0, Electron_pt,20, Electron_eta)")
        self.analyzer.Define("nMu", "nMuons(nMuon, Muon_looseId, Muon_pfIsoId, 0, Muon_pt, 20, Muon_eta)")
        self.analyzer.Cut("LeptonVetoCut", "nMu==0 && nEle==0")
        self.register_weight("LeptonVeto")
        
        #Triggers and Flags
        with open("raw_nano/Trigger.json") as f:
            triggers = json.load(f)
        hadron_triggers = triggers["Hadron"][self.year]
        print(hadron_triggers)
        triggerCut = self.analyzer.GetTriggerString(hadron_triggers)
        print(triggerCut)
        self.analyzer.Cut("TriggerCut", triggerCut)
        self.register_weight("TriggerCut")


        #Skimming for 2p1
        self.analyzer.Cut("SkimCut", "SkimFlag == 2 || SkimFlag == 3")
        self.register_weight("SkimOf2p1")


        
        #Looking for Higgs Jet
        self.analyzer.Define("idxJH", f"FindIdxJH(FatJet_msoftdrop_{JME_syst}, 100, 150, 10000)")
        self.analyzer.Cut("HiggsMassCut", f"idxJH >= 0")
        self.register_weight("HiggsMatch")

        
        self.analyzer.Define("MassHiggsCandidate", f"FatJet_msoftdrop_{JME_syst}[idxJH]")
        self.analyzer.Define("PtHiggsCandidate", f"FatJet_pt_{JME_syst}[idxJH]")
        self.analyzer.Define("EtaHiggsCandidate", "FatJet_eta[idxJH]")
        self.analyzer.Define("PhiHiggsCandidate", "FatJet_phi[idxJH]") 
        self.analyzer.Define("PNet_H", "FatJet_particleNet_XbbVsQCD[idxJH]")
        

        #Higgs Jet Quality
        self.analyzer.Cut("HiggsEtaCut", "std::abs(EtaHiggsCandidate) < 2.5")
        self.register_weight("HiggsEta")

        self.analyzer.Cut("FatJetIDCut","FatJet_jetId_corr[idxJH] >= 2 ")
        self.register_weight("FatJetID")


        

        #Defining several regions depending on the B tagging score for the Y Jets

        #Looking for Y Jets
        self.analyzer.Define("idxJY", f"FindIdxJY(Jet_eta, Jet_phi, FatJet_eta[idxJH], FatJet_phi[idxJH], Jet_btagPNetB, 0.8)")
        self.analyzer.Cut("IdxJYCut", "idxJY.at(0) >= 0 && idxJY.at(1) >= 0")


        self.register_weight("JYMatch")
        #Defining a bunch of variables for later use
        self.analyzer.Define("idxJY0", "idxJY.at(0)")
        self.analyzer.Define("idxJY1", "idxJY.at(1)")  
        self.analyzer.Define("PtJY0", f"Jet_pt_{JME_syst}[idxJY0]")
        self.analyzer.Define("PtJY1", f"Jet_pt_{JME_syst}[idxJY1]")
        self.analyzer.Define("EtaJY0", "Jet_eta[idxJY0]")
        self.analyzer.Define("EtaJY1", "Jet_eta[idxJY1]")
        self.analyzer.Define("PhiJY0", "Jet_phi[idxJY0]")
        self.analyzer.Define("PhiJY1", "Jet_phi[idxJY1]")
        self.analyzer.Define("MassJY0", f"Jet_mass_{JME_syst}[idxJY0]")
        self.analyzer.Define("MassJY1", f"Jet_mass_{JME_syst}[idxJY1]")
        self.analyzer.Define("PNet_Y0", "Jet_btagPNetB[idxJY0]")
        self.analyzer.Define("PNet_Y1", "Jet_btagPNetB[idxJY1]")
        self.analyzer.Define("PNet_Ymin", "std::min(PNet_Y0, PNet_Y1)")
        self.analyzer.Define("PNet_Y", "std::max(PNet_Y0, PNet_Y1)")




        self.analyzer.Cut("YJetIDCut", "Jet_jetId_corr[idxJY0] >= 2 && Jet_jetId_corr[idxJY1] >= 2")
        self.register_weight("YJetID")
        self.analyzer.Cut("YEtaCut", "std::abs(EtaJY0) < 2.5 && std::abs(EtaJY1) < 2.5")
        self.register_weight("YEta")
        #self.analyzer.Cut("JYPtCut", "PtJY0 > 100 && PtJY1 > 100")

        
        
        self.analyzer.Define("MassYCandidate", "InvMass_PtEtaPhiM({PtJY0, PtJY1}, {EtaJY0, EtaJY1}, {PhiJY0, PhiJY1}, {MassJY0, MassJY1} )" )
        self.analyzer.Define("MassJJH", "InvMass_PtEtaPhiM({PtHiggsCandidate, PtJY0, PtJY1}, {EtaHiggsCandidate, EtaJY0, EtaJY1}, {PhiHiggsCandidate, PhiJY0, PhiJY1}, {MassHiggsCandidate, MassJY0, MassJY1})")
        self.analyzer.Cut("MJJCut", "MassJJH > 200")
        self.register_weight("MXCut")
     
        self.analyzer.Cut("PNet_YminCut", "PNet_Ymin > 0.1")
        self.register_weight("PNet_Ymin")
        self.analyzer.Cut("MJYCut", "MassYCandidate > 200")
        self.register_weight("MJYCut")


        #defining a few variables
        self.analyzer.Define("MJY", "MassYCandidate")
        self.analyzer.Define("MJJH", "MassJJH")
        self.analyzer.Define("MY", "MassYCandidate")
        self.analyzer.Define("MX", "MassJJH")

        self.analyzer.Define("leadingFatJetPt", f"FatJet_pt_{JME_syst}.at(0)")
        self.analyzer.Define("leadingFatJetPhi", "FatJet_phi.at(0)")
        self.analyzer.Define("leadingFatJetEta", "FatJet_eta.at(0)")
        self.analyzer.Define("leadingFatJetMsoftdrop", f"FatJet_msoftdrop_{JME_syst}.at(0)")
        #Making weight columns
        self.analyzer.MakeWeightCols(name = "All")
        
        print(f"DEBUG: { self.analyzer.GetActiveNode().DataFrame.Count().GetValue()}") 


        NCuts = CutGroup("Nminus1_2p1")
        Vars = {}

        NCuts.Add("PtHCut", f"PtHiggsCandidate > 300")
        Vars["PtHCut"] = {f"PtHiggsCandidate":array.array("d", np.linspace(0, 3000, 301))}

        NCuts.Add("PtJYCut", f"PtJY0 >= 50 && PtJY1 >= 50")
        Vars["PtJYCut"] = {f"PtJY0":array.array("d", np.linspace(0, 3000, 301)), f"PtJY1":array.array("d", np.linspace(0, 3000, 301))}
        wp_f = 0.98
        NCuts.Add("BTaggingHCut", f"PNet_H >= {wp_f}") 
        Vars["BTaggingHCut"] = {f"PNet_H":array.array("d", np.linspace(0, 1, 101))}
        wp_s = 0.9659
        NCuts.Add("BTaggingYCut", f"PNet_Y >= {wp_s}") 
        Vars["BTaggingYCut"] = {f"PNet_Y":array.array("d", np.linspace(0, 1, 101))}
        
        nodes = self.analyzer.Nminus1(NCuts)
        for key in nodes.keys():
            if key == "full":
                continue
            for var in Vars[key]:
                hist = nodes[key].DataFrame.Histo1D(( f"{key}__{var}__{self.year}__{self.process}__{self.subprocess}__{MC_weight}", f"{key}__{var}__{self.year}__{self.process}__{self.subprocess}__{MC_weight}", len(Vars[key][var]) - 1, Vars[key][var]), var, MC_weight )        
                hist.Write()
        
        
    

    
        
        
        
        




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
    

    def genXHY(self):
        self.analyzer.Define("gen_Y_idx", "find_part(GenPart_pdgId, 35)")
        self.analyzer.Define("gen_higgs_idx", "find_part(GenPart_pdgId, 25)")
        self.analyzer.Define("gen_bY_idxes", "find_b(GenPart_pdgId, GenPart_genPartIdxMother, 35)")
        self.analyzer.Define("gen_bHiggs_idxes", "find_b(GenPart_pdgId, GenPart_genPartIdxMother, 25)")
        #rdf = rdf.Filter("gen_Y_idx >= 0 && gen_higgs_idx >= 0 && gen_bY_idxes[0] >= 0 && gen_bY_idxes[1] >= 0 && gen_bHiggs_idxes[0] >= 0 && gen_bHiggs_idxes[1] >= 0")

        self.analyzer.Define("gen_higgs_pt", "GenPart_pt[gen_higgs_idx]")
        self.analyzer.Define("gen_higgs_eta", "GenPart_eta[gen_higgs_idx]")
        self.analyzer.Define("gen_higgs_phi", "GenPart_phi[gen_higgs_idx]")
        self.analyzer.Define("gen_higgs_mass", "GenPart_mass[gen_higgs_idx]")
        self.analyzer.Define("gen_Y_pt", "GenPart_pt[gen_Y_idx]")
        self.analyzer.Define("gen_Y_eta", "GenPart_eta[gen_Y_idx]")
        self.analyzer.Define("gen_Y_phi", "GenPart_phi[gen_Y_idx]")
        self.analyzer.Define("gen_Y_mass", "GenPart_mass[gen_Y_idx]")

        self.analyzer.Define("gen_bY_etas", "ROOT::VecOps::RVec<float>({GenPart_eta[gen_bY_idxes[0]], GenPart_eta[gen_bY_idxes[1]]})")
        self.analyzer.Define("gen_bY_phis", "ROOT::VecOps::RVec<float>({GenPart_phi[gen_bY_idxes[0]], GenPart_phi[gen_bY_idxes[1]]})")
        self.analyzer.Define("gen_bY_pts", "ROOT::VecOps::RVec<float>({GenPart_pt[gen_bY_idxes[0]], GenPart_pt[gen_bY_idxes[1]]})")
        self.analyzer.Define("gen_bY_ms", "ROOT::VecOps::RVec<float>({GenPart_mass[gen_bY_idxes[0]], GenPart_mass[gen_bY_idxes[1]]})")
        self.analyzer.Define("gen_mbbY", "InvMass_PtEtaPhiM(gen_bY_pts, gen_bY_etas, gen_bY_phis, gen_bY_ms)")

        self.analyzer.Define("gen_bH_etas", "ROOT::VecOps::RVec<float>({GenPart_eta[gen_bHiggs_idxes[0]], GenPart_eta[gen_bHiggs_idxes[1]]})")
        self.analyzer.Define("gen_bH_phis", "ROOT::VecOps::RVec<float>({GenPart_phi[gen_bHiggs_idxes[0]], GenPart_phi[gen_bHiggs_idxes[1]]})")
        self.analyzer.Define("gen_bH_pts", "ROOT::VecOps::RVec<float>({GenPart_pt[gen_bHiggs_idxes[0]], GenPart_pt[gen_bHiggs_idxes[1]]})")
        self.analyzer.Define("gen_bH_ms", "ROOT::VecOps::RVec<float>({GenPart_mass[gen_bHiggs_idxes[0]], GenPart_mass[gen_bHiggs_idxes[1]]})")
        self.analyzer.Define("gen_mbbH", "InvMass_PtEtaPhiM(gen_bH_pts, gen_bH_etas, gen_bH_phis, gen_bH_ms)")


    def check_matching_1p1(self, combineMode = 0):
        val_prefix = ""
        if combineMode == 1:
            val_prefix = "val1p1_"
        self.analyzer.Define(f"{val_prefix}Higgs_matched", f"deltaRMatching::deltaR({val_prefix}EtaHiggsCandidate, {val_prefix}PhiHiggsCandidate, gen_higgs_eta, gen_higgs_phi) < 0.8")
        self.analyzer.Define(f"{val_prefix}Y_matched", f"deltaRMatching::deltaR({val_prefix}EtaYCandidate, {val_prefix}PhiYCandidate, gen_Y_eta, gen_Y_phi) < 0.8")
        self.analyzer.Define(f"{val_prefix}Higgs_matched_to_Y", f"deltaRMatching::deltaR({val_prefix}EtaHiggsCandidate, {val_prefix}PhiHiggsCandidate, gen_Y_eta, gen_Y_phi) < 0.8")
        self.analyzer.Define(f"{val_prefix}Y_matched_to_Higgs", f"deltaRMatching::deltaR({val_prefix}EtaYCandidate, {val_prefix}PhiYCandidate, gen_higgs_eta, gen_higgs_phi) < 0.8")
        self.analyzer.Define(f"{val_prefix}Higgs_matched_to_Xbb", f"{val_prefix}Higgs_matched || {val_prefix}Higgs_matched_to_Y")
        self.analyzer.Define(f"{val_prefix}Y_matched_to_Xbb", f"{val_prefix}Y_matched || {val_prefix}Y_matched_to_Higgs")
        self.analyzer.Define(f"{val_prefix}both_matched", f"({val_prefix}Higgs_matched && {val_prefix}Y_matched) || ({val_prefix}Higgs_matched_to_Y && {val_prefix}Y_matched_to_Higgs)")
    def check_matching_2p1(self, combineMode = 0):
        val_prefix = ""
        if combineMode == 1:
            val_prefix = "val2p1_"
        self.analyzer.Define(f"{val_prefix}Higgs_matched", f"deltaRMatching::deltaR({val_prefix}EtaHiggsCandidate, {val_prefix}PhiHiggsCandidate, gen_higgs_eta, gen_higgs_phi) < 0.8")
        self.analyzer.Define(f"{val_prefix}Higgs_matched_to_Y", f"deltaRMatching::deltaR({val_prefix}EtaHiggsCandidate, {val_prefix}PhiHiggsCandidate, gen_Y_eta, gen_Y_phi) < 0.8")
        self.analyzer.Define(f"{val_prefix}Higgs_matched_to_Xbb", f"{val_prefix}Higgs_matched || {val_prefix}Higgs_matched_to_Y")
        self.analyzer.Define(f"{val_prefix}Y_matched", f"(deltaRMatching::deltaR({val_prefix}EtaJY0, {val_prefix}PhiJY0, gen_bY_etas.at(0), gen_bY_phis.at(0)) < 0.4 && deltaRMatching::deltaR({val_prefix}EtaJY1, {val_prefix}PhiJY1, gen_bY_etas.at(1), gen_bY_phis.at(1)) < 0.4) || (deltaRMatching::deltaR({val_prefix}EtaJY0, {val_prefix}PhiJY0, gen_bY_etas.at(1), gen_bY_phis.at(1)) < 0.4 && deltaRMatching::deltaR({val_prefix}EtaJY1, {val_prefix}PhiJY1, gen_bY_etas.at(0), gen_bY_phis.at(0)) < 0.4) ")
        self.analyzer.Define(f"{val_prefix}both_matched", f"{val_prefix}Higgs_matched && {val_prefix}Y_matched")
        
        
        
        














    
    







































####################################################################################################################
#-----------------------TESTING , DEBUGGING, AND DEPRECATED FUNCTIONS------------------------------------------------------------
####################################################################################################################


    def save_fileInfo(self): #This function already exists in TIMBER
        run_rdf = ROOT.RDataFrame("Runs", self.files)
        opts = ROOT.RDF.RSnapshotOptions()
        opts.fMode = "UPDATE"
        run_rdf.Snapshot("Runs", self.output, "", opts)
    
        
    def optimize_b_wp(self, wp_min, wp_max, wp_step):
        for i in range(int(np.ceil((wp_max - wp_min) / wp_step)) + 1):
            wp = wp_min + i * wp_step
            self.analyzer.Cut(f"SRCut_wp_{wp:.4f}".replace(".", "p"), f"PNet_H >= {wp} && PNet_Y >= {wp}")
            self.register_weight(f"SRCut_wp_{wp:.4f}".replace(".", "p"))



    def lumiXsecWeight(self): #Other weighting schemes are used
        if self.isData == 0:
            luminosity = -1
            for year in self.luminosity_json:
                if (year + "__") in self.dataset:
                    luminosity = self.luminosity_json[year]
                    break
            if luminosity < 0:
                raise ValueError("Loading luminosity failed") 
                
            Xsection = -1
            for process in self.Xsection_json:
                if (process + "__") in self.dataset:
                    for subprocess in self.Xsection_json[process]:
                        print(subprocess)
                        if ((subprocess) in self.dataset):
                            Xsection = self.Xsection_json[process][subprocess]
                            break
                if Xsection >= 0:
                    break
            if Xsection < 0:
                raise ValueError("Loading Xsection failed")
              
            weightSum = ROOT.RDataFrame("Runs", self.files).Sum("genEventSumw").GetValue()
             
            print(f"reweightng MC samples {self.dataset} with luminosity {luminosity} and Xsection {Xsection}")
            self.analyzer.Define("lumiXsecWeight", f"lumiXsecWeight({luminosity}, {Xsection}, {weightSum}, genWeight)")
        else:
            raise ValueError("Weight can only e applied to MC files") 
        


        
         





    def make_analyzer(self):
        self.analyzer = analyzer(self.files)

    def selection_1p1_BDT_debug(self, JME_syst = "nom", region = "Signal", triggerType = "Hadron", massType = "regressedMass", top_fac = 0.):
        #Requiring two FatJets 
        self.analyzer.Cut("SkimCut", "SkimFlag == 1 || SkimFlag == 3") 
        self.register_weight("SkimOf1p1")
        AutoNF(self.analyzer, self.year, self.isData) ###NO JERC correction, but should be fine since the effect is small
        self.register_weight("NoiseFilter")
        #lepton veto
        self.analyzer.Define("nEle", "nElectrons(nElectron, Electron_cutBased, 0, Electron_pt,20, Electron_eta)")
        self.analyzer.Define("nMu", "nMuons(nMuon, Muon_looseId, Muon_pfIsoId, 0, Muon_pt, 20, Muon_eta)")
        self.analyzer.Cut("LeptonVetoCut", "nMu==0 && nEle==0")
        self.register_weight("LeptonVeto")
        

        AutoJetID.AutoJetID(self.analyzer, self.corr_year, ["Jet","FatJet"])
        #AutoJME.AutoJME(self.analyzer, ["Jet", "FatJet"], self.corr_year, self.data_era, True, AK8Calib_extras = ["regressedMass"])
        AutoJME.AutoJME(self.analyzer, ["Jet", "FatJet"], self.corr_year, self.data_era, True)
        self.analyzer.Define(f"FatJet_regressedMass_{JME_syst}", "getRawVal(nFatJet, FatJet_regressedMass, FatJet_rawFactor)")
        AutoJME.AutoJME_mSD(self.analyzer, self.corr_year, self.data_era)
        self.register_weight("JERCJetVeto")
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
        
        #triggers
        triggers = self.triggers[triggerType]
        print(triggers)
        triggerCut = self.analyzer.GetTriggerString(triggers)
        print(triggerCut)
        self.analyzer.Cut("TriggerCut", triggerCut)
        self.register_weight("TriggerCut")

        self.analyzer.Define("FatJet_goodness", f"goodJet(nFatJet, FatJet_jetId_corr, 2, FatJet_pt_{JME_syst}, 450,  FatJet_eta, 2.5)") 
        
        #Higgs Match
        if region == "Signal":
            self.analyzer.Define("idxH", f"FindIdxJH(FatJet_{massType}_{JME_syst}, 0, 10000, FatJet_goodness, 125)")

        self.analyzer.Define("idxY", "FindIdxJY(FatJet_goodness, idxH)")
        self.analyzer.Cut("HiggsCut", "idxH >= 0 && idxY >= 0") 
        self.register_weight("HiggsMatch")

        self.analyzer.Define("Delta_Eta", "abs(FatJet_eta.at(idxH) - FatJet_eta.at(idxY))")

    
        ROOT.gInterpreter.Declare(f'TaggerDiscretizer AK8_Discretizer = TaggerDiscretizer("FatJet",  "{self.corr_year}", "");')
        #ROOT.gInterpreter.Declare(f'TaggerDiscretizer AK4_Discretizer = TaggerDiscretizer("Jet",  "{self.corr_year}", "UParTAK4_wp_values");')
        #Defining a bunch of variables for later use
        self.analyzer.Define("MassHiggsCandidate",f"FatJet_msoftdrop_{JME_syst}[idxH]")
        self.analyzer.Define("MassHiggsCandidate_regressed",f"FatJet_regressedMass_{JME_syst}[idxH]")
        self.analyzer.Define("MassHiggsCandidate_raw",f"FatJet_mass_{JME_syst}[idxH]")
        self.analyzer.Define("PtHiggsCandidate", f"FatJet_pt_{JME_syst}[idxH]")
        self.analyzer.Define("EtaHiggsCandidate", "FatJet_eta[idxH]")
        self.analyzer.Define("PhiHiggsCandidate", "FatJet_phi[idxH]")
        self.analyzer.Define("Tagger_PNetXbb_H", "FatJet_particleNet_XbbVsQCD[idxH]")
        self.analyzer.Define("Tagger_Xbb_H", "FatJet_globalParT3_Xbb[idxH]")
        self.analyzer.Define("Tagger_QCD_H", "FatJet_globalParT3_QCD[idxH]")
        self.analyzer.Define("Tagger_TopbWqq_H", "FatJet_globalParT3_TopbWqq[idxH]")
        self.analyzer.Define("Tagger_TopbWq_H", "FatJet_globalParT3_TopbWq[idxH]")
        self.analyzer.Define("Tagger_H", f"Tagger_Xbb_H / (Tagger_Xbb_H + Tagger_QCD_H + {top_fac} * Tagger_TopbWqq_H)")
        self.analyzer.Define("Tagger_H_discrete", f"AK8_Discretizer.eval(Tagger_H)")
        self.analyzer.Define("Tagger_H_decapitated", f"AK8_Discretizer.decapitate(Tagger_H)")
        
        self.analyzer.Define("MassYCandidate", f"FatJet_msoftdrop_{JME_syst}[idxY]")
        self.analyzer.Define("MassYCandidate_raw", f"FatJet_mass_{JME_syst}[idxY]")
        self.analyzer.Define("MassYCandidate_regressed",f"FatJet_regressedMass_{JME_syst}[idxY]")
        self.analyzer.Define("PtYCandidate", f"FatJet_pt_{JME_syst}[idxY]")
        self.analyzer.Define("EtaYCandidate", "FatJet_eta[idxY]")
        self.analyzer.Define("PhiYCandidate", "FatJet_phi[idxY]")
        self.analyzer.Define("Tagger_PNetXbb_Y", "FatJet_particleNet_XbbVsQCD[idxY]")
        self.analyzer.Define("Tagger_Xbb_Y", "FatJet_globalParT3_Xbb[idxY]")
        self.analyzer.Define("Tagger_QCD_Y", "FatJet_globalParT3_QCD[idxY]")
        self.analyzer.Define("Tagger_TopbWqq_Y", "FatJet_globalParT3_TopbWqq[idxY]")
        self.analyzer.Define("Tagger_TopbWq_Y", "FatJet_globalParT3_TopbWq[idxY]")
        self.analyzer.Define("Tagger_Y", f"Tagger_Xbb_Y / (Tagger_Xbb_Y + Tagger_QCD_Y + {top_fac} * Tagger_TopbWqq_Y)")
        self.analyzer.Define("Tagger_Y_discrete", f"AK8_Discretizer.eval(Tagger_Y)")
        self.analyzer.Define("Tagger_Y_decapitated", f"AK8_Discretizer.decapitate(Tagger_Y)")
        if  self.isData != 1:
            self.analyzer.Define("TFlavor_Y", f"classifyProbeJet(PhiYCandidate, EtaYCandidate, nGenPart, GenPart_phi,GenPart_eta, GenPart_pdgId, GenPart_genPartIdxMother)")
        
        #X(JJ) Mass
        self.analyzer.Define(f"MassLeadingTwoFatJets", "InvMass_PtEtaPhiM({PtHiggsCandidate, PtYCandidate}, {EtaHiggsCandidate, EtaYCandidate}, {PhiHiggsCandidate, PhiYCandidate}, {MassHiggsCandidate, MassYCandidate})")
        self.analyzer.Define(f"MassLeadingTwoFatJets_regressed", "InvMass_PtEtaPhiM({PtHiggsCandidate, PtYCandidate}, {EtaHiggsCandidate, EtaYCandidate}, {PhiHiggsCandidate, PhiYCandidate}, {MassHiggsCandidate_regressed, MassYCandidate})")
        self.analyzer.Define(f"MassLeadingTwoFatJets_regressed_regressed", "InvMass_PtEtaPhiM({PtHiggsCandidate, PtYCandidate}, {EtaHiggsCandidate, EtaYCandidate}, {PhiHiggsCandidate, PhiYCandidate}, {MassHiggsCandidate_regressed, MassYCandidate_regressed})")


        self.analyzer.Define("leadingFatJetPt", f"FatJet_pt_{JME_syst}[0]")
        self.analyzer.Define("leadingFatJetPhi", "FatJet_phi[0]")
        self.analyzer.Define("leadingFatJetEta", "FatJet_eta[0]")
        self.analyzer.Define("leadingFatJetMsoftdrop", f"FatJet_msoftdrop_{JME_syst}[0]")
        
        self.analyzer.Define("MY", "MassYCandidate_regressed")
        self.analyzer.Define("MX", "MassLeadingTwoFatJets_regressed_regressed")
        self.analyzer.Define("MH", "MassHiggsCandidate_regressed")
        self.analyzer.Define("reco_mY", "MY") 
        self.analyzer.Define("reco_mX", "MX") 
        self.analyzer.Define("reco_mH", "MH") 

        #Making weight columns
        #self.analyzer.MakeWeightCols(name = "All", uncerts_to_corr = uncerts_to_corr)
        self.analyzer.MakeWeightCols(name = "All")
         






