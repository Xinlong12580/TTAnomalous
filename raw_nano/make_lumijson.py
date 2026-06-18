import json
#in pb^-1
lumi_json = {}
lumi_json["2022"] = 7.9804 * 1000
lumi_json["2022EE"] = 26.6717 * 1000
lumi_json["2023"] = 17.650 * 1000
lumi_json["2023BPix"] = 9.451 * 1000

with open("Luminosity.json", "w") as file:
    json.dump(lumi_json, file, indent = 4)

