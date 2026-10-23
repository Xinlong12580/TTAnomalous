#ifndef AK4_CORR
#define AK4_CORR
#include <correction.h>
#include <ROOT/RVec.hxx>
using namespace ROOT::VecOps;
class AK4_btagging_correction{
    public:
    AK4_btagging_correction(std::string SF_file,  std::string SF_key_heavy, std::string SF_key_light, std::string eff_file);
    ~AK4_btagging_correction(){}
    std::vector<float> eval(int nJet, RVec<float> etas, RVec<float> pts, RVec<int> flavors, RVec<int> scores_discrete, bool correlated, bool do_heavy_flavor, bool do_light_flavor, int WP_variation, std::string corrType);
    correction::Correction::Ref ref_sf_heavy;
    correction::Correction::Ref ref_sf_light;
    boost::property_tree::ptree eff_tree;
};


AK4_btagging_correction::AK4_btagging_correction(std::string SF_file,  std::string SF_key_heavy, std::string SF_key_light, std::string eff_file){
    std::unique_ptr<correction::CorrectionSet> SF_set = correction::CorrectionSet::from_file(SF_file.c_str()); 
    ref_sf_heavy = SF_set->at(SF_key_heavy);
    ref_sf_light = SF_set->at(SF_key_light);
    boost::property_tree::read_json(eff_file, eff_tree);
};




std::vector<float> AK4_btagging_correction::eval(int nJet, RVec<float> etas, RVec<float> pts, RVec<int> flavors, RVec<int> scores_discrete, bool correlated, bool do_heavy_flavor, bool do_light_flavor, int WP_variation, std::string corrType){
    if (WP_variation != -1 && ! (WP_variation >=1 && WP_variation <= 5) )
        throw "invalid WP_variation!";
    float nom_event = 1.;
    float up_event = 1.;
    float down_event = 1.;
    std::map<int, std::string> wp_map = {{1, "L"}, {2, "M"}, {3, "T"}, {4, "XT"}, {5, "XXT"} };
    std::map<int, std::string> uncer_map;
    if (correlated)
        uncer_map =  {{0, "central"}, {1, "up_correlated"}, {2, "down_correlated"} };
    else
        uncer_map =  {{0, "central"}, {1, "up_uncorrelated"}, {2, "down_uncorrelated"} };
    //cout<<"test0"<<endl;
    for (int i =0; i < nJet; i++){
        float abseta = std::abs(etas.at(i));
        float pt = pts.at(i);
        int score_discrete =  scores_discrete.at(i);
        int flavor = flavors.at(i);
        if (score_discrete == -1 || abseta >= 2.49)
            continue;
        if ( ( ! do_heavy_flavor ) && ( flavor == 4 || flavor == 5 ) )
            continue;
        if ( ( ! do_light_flavor ) && ( flavor == 0 ) )
            continue;
        //cout<<"test1 "<<score_discrete<<" "<<flavor<<""<<pt<<" "<<abseta<<endl; 
        std::string working_point_L = wp_map[score_discrete];
        std::string working_point_H = wp_map[score_discrete + 1];
        
        std::vector<float> SF_L = {1., 1., 1.};
        std::vector<float> SF_H = {1., 1., 1.};
        float eff_L = 1.;
        float eff_H = 1.;
        //cout<<"test2"<<endl;
        if (score_discrete == 0){
            SF_L = {1., 1., 1.};
            eff_L = 1.;
                //cout<<"test2.00"<<endl;
        }
        else{
                //cout<<"test2.01"<<endl;
            //boost::property_tree::ptree wp_tree = eff_tree.get_child(working_point_L);
            boost::property_tree::ptree wp_tree = eff_tree.get_child(std::to_string(score_discrete));
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
                            eff_L = abseta_range.second.get_value<float>();
                            break;
                        }
                    } 
                    break;
                }
            }
            
            for (int i =0; i < 3; i++){
                std::string systematic = uncer_map[i];
                //std::cout<<"SYS: "<<systematic<<endl;
                std::map<std::string, correction::Variable::Type> map {
                    { 
                    "abseta", abseta},
                    { 
                    "pt", pt},
                    { 
                    "working_point", working_point_L.c_str()},
                    { 
                    "flavor", flavor},
                    {
                    "systematic", systematic.c_str() }
                };
                correction::Correction::Ref ref_sf;
                if (flavor == 4 || flavor == 5)
                    ref_sf = ref_sf_heavy;
                else if (flavor == 0)
                    ref_sf = ref_sf_light;

                //cout<<"test2.1 "<<abseta<<" "<<pt<<" "<<working_point_L<<" "<<flavor<<" "<<systematic<<endl;
                std::vector<correction::Variable::Type> inputs_sf;
                // Loop over inputs for both
                for (const correction::Variable& input: ref_sf->inputs()) {
                    //cout<<"test2.11"<<input.name()<<endl;
                    inputs_sf.push_back(map.at(input.name()));
                }
                SF_L.at(i) = ref_sf->evaluate(inputs_sf);
                //cout<<"test2.2"<<endl;
            }
        }
        //cout<<"test3"<<endl;
        if (score_discrete == 5){
            SF_H = {1., 1., 1.};
            eff_H = 0.;
        }
        else{
            //boost::property_tree::ptree wp_tree = eff_tree.get_child(working_point_H);
            boost::property_tree::ptree wp_tree = eff_tree.get_child(std::to_string(score_discrete + 1));
            boost::property_tree::ptree flavor_tree = wp_tree.get_child(std::to_string(flavor));
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
                            eff_H = abseta_range.second.get_value<float>();
                            break;
                        }
                    } 
                    break;
                }
            }
            for (int i =0; i < 3; i++){
                std::string systematic = uncer_map[i];
                std::map<std::string, correction::Variable::Type> map {
                    { 
                    "abseta", abseta},
                    { 
                    "pt", pt},
                    { 
                    "working_point", working_point_H},
                    { 
                    "flavor", flavor},
                    { 
                    "systematic", systematic }
                };
                correction::Correction::Ref ref_sf;
                if (flavor == 4 || flavor == 5)
                    ref_sf = ref_sf_heavy;
                else if (flavor == 0)
                    ref_sf = ref_sf_light;
                std::vector<correction::Variable::Type> inputs_sf;
                // Loop over inputs for both
                for (const correction::Variable& input: ref_sf->inputs()) {
                    inputs_sf.push_back(map.at(input.name()));
                }
                SF_H.at(i) = ref_sf->evaluate(inputs_sf);
            }
        }
        //cout<<eff_L<< " "<<eff_H<<" "<<SF_L.at(0) <<" "<<SF_L.at(1)<< " "<<SF_L.at(2) <<" "<<SF_H.at(0)<< " "<<SF_H.at(1) <<" "<<SF_H.at(2)<< " "<<endl;
        float nom = 1.;
        float up = 1.;
        float down = 1.;
        if (eff_L != eff_H ){
            if ( WP_variation == score_discrete ){
                nom = (eff_L * SF_L.at(0) - eff_H * SF_H.at(0)) / (eff_L - eff_H ); //IGNORE UNCERTAINTY OF EFFICIENCY
                up = (eff_L * SF_L.at(1) - eff_H * SF_H.at(0)) / (eff_L - eff_H ); //IGNORE UNCERTAINTY OF EFFICIENCY
                down = (eff_L * SF_L.at(2) - eff_H * SF_H.at(0)) / (eff_L - eff_H ); //IGNORE UNCERTAINTY OF EFFICIENCY
            } else if (WP_variation == (score_discrete + 1) ){
                nom = (eff_L * SF_L.at(0) - eff_H * SF_H.at(0)) / (eff_L - eff_H ); //IGNORE UNCERTAINTY OF EFFICIENCY
                up = (eff_L * SF_L.at(0) - eff_H * SF_H.at(1)) / (eff_L - eff_H ); //IGNORE UNCERTAINTY OF EFFICIENCY
                down = (eff_L * SF_L.at(0) - eff_H * SF_H.at(2)) / (eff_L - eff_H ); //IGNORE UNCERTAINTY OF EFFICIENCY
            } else if (WP_variation == -1){
                nom = (eff_L * SF_L.at(0) - eff_H * SF_H.at(0)) / (eff_L - eff_H ); //IGNORE UNCERTAINTY OF EFFICIENCY
                up = (eff_L * SF_L.at(1) - eff_H * SF_H.at(1)) / (eff_L - eff_H ); //IGNORE UNCERTAINTY OF EFFICIENCY
                down = (eff_L * SF_L.at(2) - eff_H * SF_H.at(2)) / (eff_L - eff_H ); //IGNORE UNCERTAINTY OF EFFICIENCY
            } else {
                nom = (eff_L * SF_L.at(0) - eff_H * SF_H.at(0)) / (eff_L - eff_H ); //IGNORE UNCERTAINTY OF EFFICIENCY
                up = (eff_L * SF_L.at(0) - eff_H * SF_H.at(0)) / (eff_L - eff_H ); //IGNORE UNCERTAINTY OF EFFICIENCY
                down = (eff_L * SF_L.at(0) - eff_H * SF_H.at(0)) / (eff_L - eff_H ); //IGNORE UNCERTAINTY OF EFFICIENCY
            }
        }
        nom_event *= std::max(nom,0.0f);    
        up_event *= std::max(up, 0.0f );    
        down_event *= std::max(down, 0.0f);   
        //cout<<"Weight: "<<nom<<" "<<up<< " "<<down<<endl; 
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
