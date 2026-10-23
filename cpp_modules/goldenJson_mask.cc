#include <nlohmann/json.hpp>
using json = nlohmann::json;

bool mask_goldenJson(string year, int run, int luminosityBlock)
{
    //Looking for the correct goldenJson file to use
    string json_file;
    if( year == "2022" || year == "2022EE" )
        json_file = "raw_nano/json/Cert_Collisions2022_355100_362760_Golden.json";
    else if ( year == "2023" || year == "2023BPix" )
        json_file = "raw_nano/json/Cert_Collisions2023_366442_370790_Golden.json";
    else if ( year == "2024" )
        json_file = "raw_nano/json/Cert_Collisions2024_378981_386951_Golden.json";
    else 
        throw "year must be 2022, 2022EE, 2023, 2023BPix, 2024";
    
    // Checking if the run and the block is included in the goldenJson file. if found, return 1; else, 0
    std::ifstream file(json_file);
    std::stringstream buffer;
    buffer << file.rdbuf();
    json goodRuns = json::parse(buffer.str());
    if (! goodRuns.contains(std::to_string(run)))
        return 0;
    
    json goodBlockRanges = goodRuns[std::to_string(run)];
    for (json range : goodBlockRanges)
    {
        if(luminosityBlock >= range[0] && luminosityBlock <= range[1])
            return 1;
    }
        
    return 0;
}

