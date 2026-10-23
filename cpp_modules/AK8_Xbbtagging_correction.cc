#ifndef AK8_CORR
#define AK8_CORR
#include <correction.h>
#include <ROOT/RVec.hxx>
using namespace ROOT::VecOps;
class AK8_Xbbtagging_correction{
    public:
    AK8_Xbbtagging_correction(std::string SF_file, std::string eff_file);
    ~AK8_Xbbtagging_correction(){}
    std::vector<float> eval(int nJet, RVec<float> etas, RVec<float> pts, RVec<int> flavors, RVec<int> scores_discrete, int WP_variation, std::string corrType);
    boost::property_tree::ptree eff_tree;
    boost::property_tree::ptree SF_tree;
};


AK8_Xbbtagging_correction::AK8_Xbbtagging_correction(std::string SF_file, std::string eff_file){
    boost::property_tree::read_json(eff_file, eff_tree);
    boost::property_tree::read_json(SF_file, SF_tree);
};




std::vector<float> AK8_Xbbtagging_correction::eval(int nJet, RVec<float> etas, RVec<float> pts, RVec<int> flavors, RVec<int> scores_discrete, int WP_variation, std::string corrType){
    if (WP_variation != -1 && WP_variation != 1 && WP_variation != 2 && WP_variation != 3)
        throw "invalid WP_variation!";
    float nom_event = 1.;
    float up_event = 1.;
    float down_event = 1.;
    //cout<<"test0"<<endl;
    for (int i =0; i < nJet; i++){
        float abseta = std::abs(etas.at(i));
        float pt = pts.at(i);
        int score_discrete =  scores_discrete.at(i);
        int flavor = flavors.at(i);
        if (flavor != 1 || abseta >= 2.49 || score_discrete == -1)
            continue;
        //cout<<"test1 "<<score_discrete<<" "<<flavor<<" "<<pt<<" "<<abseta<<endl; 
        
        std::vector<float> SF = {1., 1., 1.};
        if (score_discrete == 0){
            std::vector<int> WPs = {1,2,3};
            std::vector<float> effs = {1., 1.,1.};
            std::vector<float> SF_noms = {1., 1.,1.};
            std::vector<float> SF_ups = {1., 1.,1.};
            std::vector<float> SF_downs = {1., 1.,1.};
            for (const int wp : WPs){
                boost::property_tree::ptree wp_tree = eff_tree.get_child(std::to_string(wp));
                boost::property_tree::ptree flavor_tree = wp_tree.get_child(std::to_string(flavor));
                for(const auto & pt_range : flavor_tree){
                    std::string pt_key = pt_range.first;
                    size_t pt_pos = pt_key.find('_');
                    std::string pt_part1 = pt_key.substr(0, pt_pos);
                    std::string pt_part2 = pt_key.substr(pt_pos + 1);
                    float pt_low = std::stof(pt_part1);
                    float pt_high = std::stof(pt_part2);
                    if (pt_low <= pt && pt < pt_high){
                            //cout<<"test2.02 "<<pt_low<<" "<<pt_high<<endl;
                        boost::property_tree::ptree pt_tree = pt_range.second;
                        for(const auto & abseta_range : pt_tree){
                            std::string abseta_key = abseta_range.first;
                            size_t abseta_pos = abseta_key.find('_');
                            std::string abseta_part1 = abseta_key.substr(0, abseta_pos);
                            std::string abseta_part2 = abseta_key.substr(abseta_pos + 1);
                            float abseta_low = std::stof(abseta_part1);
                            float abseta_high = std::stof(abseta_part2);
                            if (abseta_low <= abseta && abseta < abseta_high){
                                //cout<<"test2.03 "<<abseta_low<<" "<<abseta_high<<endl;
                                effs[wp - 1] = abseta_range.second.get_value<float>();
                                break;
                            }
                        } 
                        break;
                    }
                }
                wp_tree = SF_tree.get_child(std::to_string(wp));
                flavor_tree = wp_tree.get_child(std::to_string(flavor));
                for(const auto & pt_range : flavor_tree){
                    std::string pt_key = pt_range.first;
                    size_t pt_pos = pt_key.find('_');
                    std::string pt_part1 = pt_key.substr(0, pt_pos);
                    std::string pt_part2 = pt_key.substr(pt_pos + 1);
                    float pt_low = std::stof(pt_part1);
                    float pt_high = std::stof(pt_part2);
                    if (pt_low <= pt && pt < pt_high){
                        boost::property_tree::ptree pt_tree = pt_range.second;
                        for(const auto & abseta_range : pt_tree){
                            std::string abseta_key = abseta_range.first;
                            size_t abseta_pos = abseta_key.find('_');
                            std::string abseta_part1 = abseta_key.substr(0, abseta_pos);
                            std::string abseta_part2 = abseta_key.substr(abseta_pos + 1);
                            float abseta_low = std::stof(abseta_part1);
                            float abseta_high = std::stof(abseta_part2);
                            if (abseta_low <= abseta && abseta < abseta_high){
                                SF_noms[wp - 1] = abseta_range.second.get<float>("nom");
                                if (wp == WP_variation || WP_variation == -1) {
                                    SF_ups[wp - 1] = SF_noms[wp - 1] + abseta_range.second.get<float>("up_uncert");
                                    SF_downs[wp - 1] = SF_noms[wp - 1] - abseta_range.second.get<float>("down_uncert");
                                }
                                else
                                {
                                    SF_ups[wp - 1] = SF_noms[wp - 1];
                                    SF_downs[wp - 1] = SF_noms[wp - 1];
                                }
                                break;
                            }
                        } 
                        break;
                    }
                }

            }
            if (1 - effs[0] - effs[1] - effs[2] > 0){
                SF[0] = (1 - SF_noms[0] * effs[0] - SF_noms[1] * effs[1] - SF_noms[2] * effs[2]) / (1 - effs[0] - effs[1] - effs[2]);
                SF[1] = (1 - SF_ups[0] * effs[0] - SF_ups[1] * effs[1] - SF_ups[2] * effs[2]) / (1 - effs[0] - effs[1] - effs[2]);
                SF[2] = (1 - SF_downs[0] * effs[0] - SF_downs[1] * effs[1] - SF_downs[2] * effs[2]) / (1 - effs[0] - effs[1] - effs[2]);
             }

        }

        else{
            boost::property_tree::ptree wp_tree = SF_tree.get_child(std::to_string(score_discrete));
            boost::property_tree::ptree flavor_tree = wp_tree.get_child(std::to_string(flavor));
            for(const auto & pt_range : flavor_tree){
                std::string pt_key = pt_range.first;
                size_t pt_pos = pt_key.find('_');
                std::string pt_part1 = pt_key.substr(0, pt_pos);
                std::string pt_part2 = pt_key.substr(pt_pos + 1);
                float pt_low = std::stof(pt_part1);
                float pt_high = std::stof(pt_part2);
                if (pt_low <= pt && pt < pt_high){
                        //cout<<"test2.02 "<<pt_low<<" "<<pt_high<<endl;
                    boost::property_tree::ptree pt_tree = pt_range.second;
                    for(const auto & abseta_range : pt_tree){
                        std::string abseta_key = abseta_range.first;
                        size_t abseta_pos = abseta_key.find('_');
                        std::string abseta_part1 = abseta_key.substr(0, abseta_pos);
                        std::string abseta_part2 = abseta_key.substr(abseta_pos + 1);
                        float abseta_low = std::stof(abseta_part1);
                        float abseta_high = std::stof(abseta_part2);
                        if (abseta_low <= abseta && abseta < abseta_high){
                            //cout<<"test2.03 "<<abseta_low<<" "<<abseta_high<<endl;
                            SF[0] = abseta_range.second.get<float>("nom");
                            if (score_discrete == WP_variation || WP_variation == -1 ){
                                SF[1] = SF[0] + abseta_range.second.get<float>("up_uncert");
                                SF[2] = SF[0] - abseta_range.second.get<float>("down_uncert");
                            }
                            else
                            {
                                SF[1] = SF[0];
                                SF[2] = SF[0];
                            }
                            break;
                        }
                    } 
                    break;
                }
            }
        }
        //cout<<"Weight: "<<SF[0]<<" "<<SF[1]<< " "<<SF[2]<<endl; 
        nom_event *= std::max(SF[0],0.0f);    
        up_event *= std::max(SF[1], 0.0f );    
        down_event *= std::max(SF[2], 0.0f);   
    }
        //cout<<"Event Weight: "<<nom_event<<" "<<up_event<< " "<<down_event<<endl; 
    std::vector<float> weights;
    if (corrType == "weight")
        weights = {nom_event, up_event, down_event};
    if (corrType == "uncert")
        weights = {up_event, down_event};
    return weights;
}
#endif
