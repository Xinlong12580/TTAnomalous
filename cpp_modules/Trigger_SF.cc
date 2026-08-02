#ifndef TRIGGER_CORR
#define TRIGGER_CORR
#include <cmath>
#include <algorithm>
#include <correction.h>
#include <ROOT/RVec.hxx>
using namespace ROOT::VecOps;

/** @class Trigger_weight
 *  @brief C++ class. Specializes in the construction of trigger efficiency weights stored as histograms.
 * Uncertainties are calculated as one half of the trigger inefficiency (ie. (1-eff)/2).
 * 
 * Uncertainties are capped to never be greater than 1 or less
 * than 0. Additionally, a plateau value can be provided which
 * assumes 100% efficiency (and zero uncertainty) beyond the provided
 * threshold. 
 * 
 * Finally, if a bin is 0 and the surrounding bins are non-zero 
 * (this could happen in the case of poor statistics),
 * a value for the 0 bin will be linearly interpolated from the two
 * neighboring bins.
 * 
 */
class Trigger_SF
{
    public:
        boost::property_tree::ptree ptree;
        boost::property_tree::ptree year_tree;
        Trigger_SF(std::string json_name, std::string year){
            boost::property_tree::read_json(json_name, ptree);
            year_tree = ptree.get_child(year);
        };
        RVec<float> eval(float pt, float mass, std::string uncert);
        ~Trigger_SF(){};
};

RVec<float> Trigger_SF::eval(float pt, float mass, std::string uncert) {
    float nom = 1.;
    float up = 1.;
    float down = 1.;
    //cout<<"TEST"<<uncert<<corr_type<<std::endl;
    for(const auto & pt_range : year_tree){
        std::string pt_key = pt_range.first;
        size_t pt_pos = pt_key.find('_');
        std::string pt_part1 = pt_key.substr(0, pt_pos);
        std::string pt_part2 = pt_key.substr(pt_pos + 1);
        float pt_low = std::stof(pt_part1);
        float pt_high = std::stof(pt_part2);
        if (pt_low <= pt && pt < pt_high){
            boost::property_tree::ptree pt_tree = pt_range.second;
            for(const auto & mass_range : pt_tree){
                std::string mass_key = mass_range.first;
                size_t mass_pos = mass_key.find('_');
                std::string mass_part1 = mass_key.substr(0, mass_pos);
                std::string mass_part2 = mass_key.substr(mass_pos + 1);
                float mass_low = std::stof(mass_part1);
                float mass_high = std::stof(mass_part2);
                if (mass_low <= mass && mass < mass_high){
                    boost::property_tree::ptree mass_tree = mass_range.second;
                    if (uncert == "data"){
                        nom = mass_tree.get<float>("data_nom");
                        up = mass_tree.get<float>("data_up");
                        down = mass_tree.get<float>("data_down");
                    }
                    else if (uncert == "MC"){
                        nom = mass_tree.get<float>("MC_nom");
                        up = mass_tree.get<float>("MC_up");
                        down = mass_tree.get<float>("MC_down");
                    }
                    else if (uncert == "total"){
                        nom = mass_tree.get<float>("nom");
                        up = mass_tree.get<float>("up");
                        down = mass_tree.get<float>("down");
                    }
                    else
                        throw "BAD UNCERTAINTY TYPE!";
                    break;
                }
            } 
            break;
        }
    }
    RVec<float> out({nom, up, down});
    return out;
};
#endif
